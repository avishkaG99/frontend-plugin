#!/usr/bin/env python3
"""Capture a Playwright storage state for one role, by letting you sign in yourself.

    scripts/capture_auth.py tenant-admin
    scripts/capture_auth.py external-architect --url http://localhost:3000
    scripts/capture_auth.py --list

A browser window opens. Sign in as that role, get to a signed-in page, then close the
window: the cookies and local storage are written to <app>/.auth/<role>.json.

The file is a live session — as sensitive as the password. It is gitignored here, must
never be committed, and its contents are never printed by this script or by any agent.
Refresh it by running this again when a run reports BLOCKED — session expired.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_APP = "areasim-webapp"
DEFAULT_URL = "http://localhost:3000"
GITIGNORE_LINE = ".auth/"


def python_cmd():
    """Windows ships `python`, macOS and Linux `python3`."""
    for candidate in ("python3", "python"):
        if subprocess.run(["command", "-v", candidate], shell=False,
                          capture_output=True).returncode == 0:
            return candidate
    return sys.executable


def ensure_chromium(py):
    """Install Chromium only when it is missing — the first run costs a minute, later ones nothing."""
    probe = subprocess.run(
        [py, "-c", "from playwright.sync_api import sync_playwright;"
                   "p=sync_playwright().start();print(p.chromium.executable_path);p.stop()"],
        capture_output=True, text=True)
    if probe.returncode == 0 and Path(probe.stdout.strip()).exists():
        return
    print("installing chromium (first run only)…")
    subprocess.run([py, "-m", "playwright", "install", "chromium"], check=True)


def ensure_gitignored(auth_dir):
    gitignore = auth_dir.parent / ".gitignore"
    existing = gitignore.read_text() if gitignore.exists() else ""
    if GITIGNORE_LINE in existing:
        return
    with gitignore.open("a") as handle:
        handle.write(("" if existing.endswith("\n") or not existing else "\n")
                     + f"\n# Playwright storage states — live sessions, never commit\n{GITIGNORE_LINE}\n")
    print(f"added {GITIGNORE_LINE} to {gitignore}")


def summarise(path):
    """Report shape only. Never cookie values: this file is a credential."""
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return "unreadable — sign-in may not have completed"
    cookies = len(data.get("cookies", []))
    origins = len(data.get("origins", []))
    if cookies == 0 and origins == 0:
        return "empty — no session was captured; sign in fully before closing the window"
    return f"{cookies} cookies, {origins} origins"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role", nargs="?", help="a name for this session, e.g. tenant-admin")
    ap.add_argument("--app", default=DEFAULT_APP, help=f"app directory (default: {DEFAULT_APP})")
    ap.add_argument("--url", default=DEFAULT_URL, help=f"URL to open (default: {DEFAULT_URL})")
    ap.add_argument("--list", action="store_true", help="list captured sessions and their age")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent.parent
    auth_dir = root / args.app / ".auth"

    if args.list:
        if not auth_dir.is_dir() or not any(auth_dir.glob("*.json")):
            sys.exit(f"no sessions in {auth_dir}")
        now = datetime.now(timezone.utc)
        for state in sorted(auth_dir.glob("*.json")):
            age = now - datetime.fromtimestamp(state.stat().st_mtime, timezone.utc)
            hours = int(age.total_seconds() // 3600)
            print(f"{state.stem:<24} {hours}h old   {summarise(state)}")
        return

    if not args.role:
        ap.error("a role name is required (or --list)")

    auth_dir.mkdir(parents=True, exist_ok=True)
    ensure_gitignored(auth_dir)
    target = auth_dir / f"{args.role}.json"

    py = python_cmd()
    ensure_chromium(py)

    print(f"\nOpening {args.url}. Sign in as '{args.role}', reach a signed-in page, then close\n"
          f"the window. Nothing is captured until you close it.\n")
    subprocess.run([py, "-m", "playwright", "open",
                    f"--save-storage={target}", args.url], check=True)

    if not target.exists():
        sys.exit("no session file written — the window was closed before sign-in completed")
    print(f"\nsaved {target}  ({summarise(target)})")
    print("This file is a live session: gitignored, never commit it, never paste its contents.")


if __name__ == "__main__":
    main()
