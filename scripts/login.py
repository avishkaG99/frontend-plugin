#!/usr/bin/env python3
"""Sign a Playwright page in as a test role, through the app's real Entra External ID login.

    login.py org-admin                    sign in once, report the landing page, exit
    login.py org-member --headed          the same, with a visible browser
    login.py --list                       which roles are ready (no emails, no passwords)
    login.py --edit                       open the accounts file in the person's editor

From a run script:

    sys.path.insert(0, "frontend-plugin/scripts")
    from login import sign_in, LoginBlocked
    landing = sign_in(page, "org-admin", "http://localhost:3000")

Why a scripted login rather than a saved session: the app keeps its MSAL tokens in
sessionStorage, and a Playwright storage state never includes sessionStorage. A saved
session therefore always starts signed out. Signing in once per run, in the run's own
page, is what actually works.

Credentials come from a local file outside every repo (default
~/.config/frontend-flow/<profile>/test-accounts.env, override with FE_FLOW_ACCOUNTS):

    ORG_ADMIN_EMAIL=...
    ORG_ADMIN_PASSWORD=...

Rules this script keeps, so the person's accounts stay safe:
- It never prints, logs or returns an email or a password, and never screenshots a page
  with the password typed in.
- One attempt per call. A rejected password stops the run (LoginBlocked) instead of
  retrying into an account lockout.
- Local only: it refuses any base URL that is not localhost.
- It never answers a one-time-code or MFA prompt; it reports it as blocked.
"""
import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_PROFILE = "areasim"
DEFAULT_URL = "http://localhost:3000"
IDP_HOSTS = ("ciamlogin.com", "login.microsoftonline.com")
FOREIGN_IDP_HOSTS = ("accounts.google.com", "login.live.com", "facebook.com", "apple.com")
CODE_PROMPTS = re.compile(r"enter code|verification code|we sent a code|verify your email|"
                          r"one-time|approve sign in|authenticator", re.I)
ERROR_HINTS = re.compile(r"incorrect|doesn.t exist|does not exist|not found|locked|"
                         r"too many|try again later|couldn.t find|invalid", re.I)
TIMEOUT_MS = 30_000


class LoginBlocked(Exception):
    """Sign-in could not complete. The message is safe to print: it never holds a secret."""


def accounts_file(profile=DEFAULT_PROFILE):
    override = os.environ.get("FE_FLOW_ACCOUNTS")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "frontend-flow" / profile / "test-accounts.env"


def read_accounts(profile=DEFAULT_PROFILE):
    path = accounts_file(profile)
    if not path.exists():
        raise LoginBlocked(f"no accounts file at {path} — create it with the role emails and passwords")
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def role_key(role):
    return re.sub(r"[^A-Z0-9]", "_", role.upper())


def credentials(role, profile=DEFAULT_PROFILE):
    values = read_accounts(profile)
    key = role_key(role)
    email, password = values.get(f"{key}_EMAIL"), values.get(f"{key}_PASSWORD")
    if not email:
        raise LoginBlocked(f"role {role!r} has no {key}_EMAIL in the accounts file")
    if not password:
        raise LoginBlocked(f"role {role!r} has no {key}_PASSWORD yet — the person fills it in")
    return email, password


def _host(url):
    return urlparse(url).hostname or ""


def _on_app(page, base_url):
    u = urlparse(page.url)
    b = urlparse(base_url)
    return (u.hostname, u.port) == (b.hostname, b.port)


def _has_tokens(page):
    """MSAL writes access/id token entries into sessionStorage once sign-in completes."""
    try:
        return page.evaluate(
            "() => Object.keys(sessionStorage).some(k => /accesstoken|idtoken/i.test(k))")
    except Exception:
        return False


def _visible_text(page):
    try:
        return page.locator("body").inner_text(timeout=2000)
    except Exception:
        return ""


def _first_visible(page, *locators):
    for loc in locators:
        try:
            if loc.count() and loc.first.is_visible():
                return loc.first
        except Exception:
            continue
    return None


def sign_in(page, role, base_url=DEFAULT_URL, profile=DEFAULT_PROFILE, timeout_ms=TIMEOUT_MS):
    """Sign `page` in as `role`. Returns the app path it landed on. Raises LoginBlocked."""
    if _host(base_url) not in ("localhost", "127.0.0.1"):
        raise LoginBlocked(f"refusing to sign test accounts in to {base_url}: local dev only")
    email, password = credentials(role, profile)

    page.goto(base_url, wait_until="domcontentloaded", timeout=timeout_ms)
    page.wait_for_url(lambda u: any(h in u for h in IDP_HOSTS) or _host(u) == _host(base_url),
                      timeout=timeout_ms)
    page.wait_for_load_state("networkidle", timeout=timeout_ms)
    if _on_app(page, base_url) and _has_tokens(page):
        return urlparse(page.url).path  # already signed in in this context

    if not any(h in page.url for h in IDP_HOSTS):
        raise LoginBlocked(f"expected the Entra sign-in page, landed on {_host(page.url)}")

    # Account picker (prompt=select_account) when the identity provider remembers someone.
    other = _first_visible(page, page.get_by_role("button", name=re.compile("use another account", re.I)),
                           page.get_by_role("link", name=re.compile("use another account", re.I)))
    if other:
        other.click()

    email_box = _first_visible(page, page.get_by_role("textbox", name=re.compile("email", re.I)),
                               page.locator("input[type=email]"), page.locator("input[name=username]"))
    if not email_box:
        raise LoginBlocked("sign-in page has no email field — the page layout changed")
    email_box.fill(email)
    page.get_by_role("button", name=re.compile(r"^next$", re.I)).click()

    password_box = page.locator("input[type=password]")
    try:
        password_box.first.wait_for(state="visible", timeout=timeout_ms)
    except Exception:
        host = _host(page.url)
        if any(h in host for h in FOREIGN_IDP_HOSTS):
            raise LoginBlocked(f"{role} signs in through {host} (a federated account) — "
                               "use an email-and-password account in the dev tenant")
        text = _visible_text(page)
        if CODE_PROMPTS.search(text):
            raise LoginBlocked(f"{role} is asked for a one-time code — turn MFA off for this test account")
        hint = ERROR_HINTS.search(text)
        raise LoginBlocked(f"no password field after the email step"
                           + (f" (page says something like '{hint.group(0)}')" if hint else ""))
    password_box.first.fill(password)
    page.get_by_role("button", name=re.compile(r"^sign in$", re.I)).click()

    # From here: back on the app, or a "Stay signed in?" prompt, or an error, or a code prompt.
    deadline_steps = timeout_ms // 500
    for _ in range(deadline_steps):
        if _on_app(page, base_url):
            break
        stay = _first_visible(page, page.get_by_role("button", name=re.compile(r"^no$", re.I)))
        if stay and re.search(r"stay signed in", _visible_text(page), re.I):
            stay.click()
            continue
        if page.locator("input[type=password]").count() and page.locator("input[type=password]").first.is_visible():
            text = _visible_text(page)
            if ERROR_HINTS.search(text):
                # Clear the field before anything else can capture the page.
                page.locator("input[type=password]").first.fill("")
                raise LoginBlocked(f"{role}: the sign-in page rejected the password — fix it in the "
                                   "accounts file; not retrying, to avoid locking the account")
        if CODE_PROMPTS.search(_visible_text(page)):
            raise LoginBlocked(f"{role} is asked for a one-time code — turn MFA off for this test account")
        page.wait_for_timeout(500)
    else:
        raise LoginBlocked(f"{role}: still on {_host(page.url)} after {timeout_ms // 1000}s")

    page.wait_for_load_state("networkidle", timeout=timeout_ms)
    for _ in range(20):
        if _has_tokens(page):
            return urlparse(page.url).path
        page.wait_for_timeout(500)
    raise LoginBlocked(f"{role}: back on the app but no MSAL tokens appeared — sign-in did not complete")


def _python_has_playwright():
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role", nargs="?", help="e.g. org-admin, org-member, super-admin")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--profile", default=DEFAULT_PROFILE)
    ap.add_argument("--headed", action="store_true", help="show the browser")
    ap.add_argument("--list", action="store_true", help="which roles are ready")
    ap.add_argument("--edit", action="store_true",
                    help="open the accounts file in VS Code (or TextEdit) for the person to fill in")
    args = ap.parse_args()

    if args.edit:
        # Opens the file in the person's GUI editor. Nothing from it is printed here.
        import shutil
        import subprocess
        path = accounts_file(args.profile)
        if not path.exists():
            sys.exit(f"BLOCKED: no accounts file for profile {args.profile!r}")
        editor = ["code", str(path)] if shutil.which("code") else ["open", "-e", str(path)]
        subprocess.run(editor, check=False)
        print(f"opened the {args.profile} accounts file in {editor[0]} — fill in each *_PASSWORD, "
              "save with Cmd+S, then run --list")
        return

    if args.list:
        try:
            values = read_accounts(args.profile)
        except LoginBlocked as e:
            sys.exit(f"BLOCKED: {e}")
        path = accounts_file(args.profile)
        from datetime import datetime
        saved = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"accounts file last saved {saved}\n")
        roles = sorted({k[: -len("_EMAIL")] for k in values if k.endswith("_EMAIL")})
        for key in roles:
            ready = bool(values.get(f"{key}_EMAIL")) and bool(values.get(f"{key}_PASSWORD"))
            print(f"{key.lower().replace('_', '-'):<16} {'ready' if ready else 'missing password'}")
        return
    if not args.role:
        ap.error("give a role, or --list")
    if not _python_has_playwright():
        sys.exit("playwright is not installed for this python — use frontend-plugin/.venv/bin/python")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_context(viewport={"width": 1280, "height": 1800}).new_page()
        try:
            landing = sign_in(page, args.role, args.url, args.profile)
        except LoginBlocked as e:
            print(f"BLOCKED: {e}")
            sys.exit(2)
        print(f"signed in as {args.role} — landed on {landing}")
        browser.close()


if __name__ == "__main__":
    main()
