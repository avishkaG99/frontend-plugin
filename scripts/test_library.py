#!/usr/bin/env python3
"""Check, select and map the test-case library (see frontend-flow references/test-library.md).

    test_library.py --app APP --library LIB check              validate every area file
    test_library.py --app APP --library LIB select --all       Active cases, everywhere
    test_library.py --app APP --library LIB select --area surveys
    test_library.py --app APP --library LIB select TC-SUR-004 UC-SUR-02
    test_library.py --app APP --library LIB impacted           cases the current branch touches

APP is the app repo (paths in areas.json are relative to it); LIB is the library folder,
relative to APP or absolute. LIB/areas.json names the areas, their ID prefixes, the code
each one owns, the roles, and the base branch. `select` and `impacted` print the chosen
cases as a table, or as JSON with --json, so an agent and a person get the same answer.

check exits 1 on any error. Warnings (a test file that does not mention its case ID, an
unused use case) never fail it.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

COLUMNS = ["ID", "UC", "Title", "Type", "Role", "Steps", "Expected", "Automated",
           "Status", "Added in"]
TYPES = {"Smoke", "Happy", "Negative", "Edge", "Permission", "Regression"}
STATUSES = {"Active", "Draft", "Retired"}
TC_ID = re.compile(r"^TC-([A-Z]{2,5})-(\d{3,})$")
UC_ID = re.compile(r"^UC-([A-Z]{2,5})-(\d{2,})$")
UC_HEADING = re.compile(r"^###\s+(UC-[A-Z]{2,5}-\d{2,})\b")
ANY_ID = re.compile(r"\b(?:TC|UC)-[A-Z]{2,5}-\d{2,}\b")


# ---------- reading ----------

def split_row(line):
    """Cells of a markdown table row; `\\|` stays inside a cell."""
    cells = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip().replace("\\|", "|") for c in cells[1:-1]]


def glob_to_regex(pattern):
    """`**` spans directories, `*` stays inside one, everything else is literal."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + "$")


def matches(path, patterns):
    return any(glob_to_regex(p).match(path) for p in patterns)


class Library:
    def __init__(self, app, lib):
        self.app = app
        self.lib = lib
        config_path = lib / "areas.json"
        if not config_path.exists():
            sys.exit(f"no areas.json in {lib}")
        self.config = json.loads(config_path.read_text())
        self.areas = self.config["areas"]
        self.errors, self.warnings = [], []
        self.cases, self.use_cases = [], {}
        for area in self.areas:
            self._read_area(area)

    def _err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def _warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def _read_area(self, area):
        path = self.lib / area["file"]
        if not path.exists():
            self._err(area["file"], "missing — areas.json lists it")
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        for n, line in enumerate(lines, 1):
            m = UC_HEADING.match(line)
            if m:
                self.use_cases.setdefault(m.group(1), []).append((area, n))
        try:
            start = next(i for i, l in enumerate(lines) if l.strip() == "## Test cases")
        except StopIteration:
            self._err(area["file"], "no '## Test cases' section")
            return
        header_at = next((i for i in range(start + 1, len(lines))
                          if lines[i].lstrip().startswith("|")), None)
        if header_at is None:
            self._err(area["file"], "no test-case table under '## Test cases'")
            return
        header = split_row(lines[header_at])
        if header != COLUMNS:
            self._err(f"{area['file']}:{header_at + 1}",
                      f"columns are {header}, expected {COLUMNS}")
            return
        for i in range(header_at + 2, len(lines)):
            line = lines[i]
            if line.startswith("## "):
                break
            if not line.lstrip().startswith("|"):
                continue
            cells = split_row(line)
            where = f"{area['file']}:{i + 1}"
            if len(cells) != len(COLUMNS):
                self._err(where, f"{len(cells)} cells, expected {len(COLUMNS)}")
                continue
            case = dict(zip(COLUMNS, cells))
            case["area"], case["where"] = area["file"][:-3], where
            self.cases.append(case)

    # ---------- check ----------

    def check(self):
        roles = set(self.config.get("roles", []))
        prefixes = {a["prefix"]: a["file"] for a in self.areas}
        seen = {}
        used_ucs = set()
        for uc, places in self.use_cases.items():
            area, n = places[0]
            if len(places) > 1:
                self._err(f"{area['file']}:{n}", f"{uc} defined {len(places)} times")
            m = UC_ID.match(uc)
            if m and m.group(1) != area["prefix"]:
                self._err(f"{area['file']}:{n}", f"{uc} uses prefix {m.group(1)}, "
                          f"this file is {area['prefix']}")
        for case in self.cases:
            where, cid = case["where"], case["ID"]
            m = TC_ID.match(cid)
            if not m:
                self._err(where, f"ID {cid!r} is not TC-<PREFIX>-NNN")
            elif prefixes.get(m.group(1)) != case["area"] + ".md":
                self._err(where, f"{cid} has prefix {m.group(1)}, this file is "
                          f"{next(a['prefix'] for a in self.areas if a['file'] == case['area'] + '.md')}")
            if cid in seen:
                self._err(where, f"{cid} already used at {seen[cid]} — IDs are never reused")
            seen[cid] = where
            if case["UC"] not in self.use_cases:
                self._err(where, f"{cid}: use case {case['UC']!r} has no '### {case['UC']}' heading")
            used_ucs.add(case["UC"])
            for col, allowed in (("Type", TYPES), ("Status", STATUSES)):
                if case[col] not in allowed:
                    self._err(where, f"{cid}: {col} {case[col]!r} not one of {sorted(allowed)}")
            if roles and case["Role"] not in roles:
                self._err(where, f"{cid}: Role {case['Role']!r} not one of {sorted(roles)}")
            for col in ("Title", "Steps", "Expected", "Added in"):
                if not case[col]:
                    self._err(where, f"{cid}: {col} is empty")
            self._check_automated(case)
        for uc, places in self.use_cases.items():
            if uc not in used_ucs:
                area, n = places[0]
                self._warn(f"{area['file']}:{n}", f"{uc} has no test cases yet")
        return not self.errors

    def _check_automated(self, case):
        value, where, cid = case["Automated"], case["where"], case["ID"]
        if value == "browser" or value.startswith("manual"):
            return
        paths = re.findall(r"`([^`]+)`", value)
        if not paths:
            self._err(where, f"{cid}: Automated must be `file`, browser or manual — got {value!r}")
            return
        for rel in paths:
            found = self._resolve_test_file(rel)
            if found is None:
                self._err(where, f"{cid}: test file `{rel}` not found under {self.app.name}")
            elif found == "ambiguous":
                self._err(where, f"{cid}: `{rel}` matches several files — give the path from the app root")
            elif case["Status"] == "Active" and cid not in found.read_text(errors="replace"):
                self._warn(where, f"{cid}: `{rel}` never mentions {cid} — put the ID in the "
                           f"test name so `vitest -t {cid}` finds it")

    def _resolve_test_file(self, rel):
        direct = self.app / rel
        if direct.is_file():
            return direct
        if "/" in rel:
            return None
        hits = [p for p in (self.app / "src").rglob(rel) if "node_modules" not in p.parts]
        return hits[0] if len(hits) == 1 else ("ambiguous" if hits else None)

    # ---------- selecting ----------

    def active(self):
        return [c for c in self.cases if c["Status"] == "Active"]

    def select(self, all_=False, area=None, ids=()):
        cases = self.active()
        if all_:
            return cases
        if area:
            area = area.removesuffix(".md")
            if not any(a["file"] == area + ".md" for a in self.areas):
                sys.exit(f"no area {area!r} (have: {', '.join(a['file'][:-3] for a in self.areas)})")
            return [c for c in cases if c["area"] == area]
        wanted = set(ids)
        unknown = wanted - {c["ID"] for c in self.cases} - set(self.use_cases)
        if unknown:
            sys.exit(f"unknown IDs: {', '.join(sorted(unknown))}")
        return [c for c in cases if c["ID"] in wanted or c["UC"] in wanted]

    # ---------- impact ----------

    def git(self, *args, check=True):
        r = subprocess.run(["git", "-C", str(self.app), *args], capture_output=True, text=True)
        if r.returncode and check:
            sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
        return [l for l in r.stdout.splitlines() if l] if not r.returncode else None

    def resolve_base(self, base):
        """The remote copy of the base when there is one: a local base branch is often stale."""
        for ref in (f"origin/{base}", base):
            if self.git("rev-parse", "--verify", "--quiet", ref, check=False) is not None:
                return ref
        sys.exit(f"no branch {base!r} or origin/{base} in {self.app.name}")

    def changed_files(self, ref):
        """Committed since the merge base, plus staged, unstaged and untracked changes."""
        merge_base = self.git("merge-base", ref, "HEAD")[0]
        files = set(self.git("diff", "--name-only", merge_base))
        files |= set(self.git("ls-files", "--others", "--exclude-standard"))
        return merge_base, sorted(files)

    def area_of(self, path):
        hits = [a for a in self.areas
                if matches(path, a["owns"]) and not matches(path, a.get("except", []))]
        return [a["file"][:-3] for a in hits]

    def import_index(self):
        """`@/…` specifier -> areas whose owned files import it. Built once, in one pass."""
        if getattr(self, "_imports", None) is None:
            self._imports = {}
            spec = re.compile(r"""from\s+['"](@/[^'"]+)['"]""")
            for f in (self.app / "src").rglob("*.ts*"):
                if "node_modules" in f.parts:
                    continue
                owners = self.area_of(f.relative_to(self.app).as_posix())
                if not owners:
                    continue
                for s in set(spec.findall(f.read_text(errors="replace"))):
                    self._imports.setdefault(s, set()).update(owners)
        return self._imports

    def importers(self, path):
        """Areas whose owned files import a shared module, by its @/ alias."""
        stem = re.sub(r"\.(tsx?|jsx?)$", "", path)
        alias = "@/" + stem.removeprefix("src/")
        index = self.import_index()
        areas = set(index.get(alias, ()))
        if alias.endswith("/index"):
            areas |= index.get(alias[: -len("/index")], set())
        return areas

    def impacted(self, base):
        ignore = self.config.get("ignore", [])
        shared = self.config.get("shared", [])
        ref = self.resolve_base(base)
        merge_base, files = self.changed_files(ref)
        report = {"base": ref, "merge_base": merge_base[:10], "changed": [], "areas": {},
                  "unmapped": []}
        for path in files:
            if matches(path, ignore):
                continue
            report["changed"].append(path)
            owners = self.area_of(path)
            if owners:
                for a in owners:
                    report["areas"].setdefault(a, set()).add(f"owns {path}")
            elif matches(path, shared):
                users = self.importers(path)
                for a in users:
                    report["areas"].setdefault(a, set()).add(f"imports {path}")
                if not users:
                    report["unmapped"].append(f"{path} (shared, no area imports it)")
            else:
                report["unmapped"].append(path)
        names = set(report["areas"])
        cases = [c for c in self.active() if c["area"] in names]
        report["areas"] = {k: sorted(v) for k, v in sorted(report["areas"].items())}
        return report, cases


# ---------- output ----------

def print_cases(cases):
    if not cases:
        print("no Active cases selected")
        return
    for c in cases:
        auto = c["Automated"] if c["Automated"] in ("browser",) or c["Automated"].startswith("manual") \
            else "vitest " + " ".join(re.findall(r"`([^`]+)`", c["Automated"]))
        print(f"{c['ID']:<12} {c['UC']:<10} {c['Role']:<18} {auto:<40} {c['Title']}")
    by = {}
    for c in cases:
        kind = "browser" if c["Automated"] == "browser" else (
            "manual" if c["Automated"].startswith("manual") else "vitest")
        by[kind] = by.get(kind, 0) + 1
    print(f"\n{len(cases)} cases — " + ", ".join(f"{n} {k}" for k, n in sorted(by.items())))


def public(case):
    return {k: v for k, v in case.items() if k != "where"} | {"source": case["where"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app", required=True, help="the app repo")
    ap.add_argument("--library", required=True, help="the library folder, relative to --app or absolute")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="validate the library")
    sel = sub.add_parser("select", help="list Active cases for a scope")
    sel.add_argument("--all", action="store_true")
    sel.add_argument("--area")
    sel.add_argument("--type", help="only cases of this Type, e.g. Smoke or Permission")
    sel.add_argument("ids", nargs="*", help="TC-… and/or UC-… IDs")
    imp = sub.add_parser("impacted", help="Active cases in the areas the branch changes")
    imp.add_argument("--base", help="base branch (default: areas.json baseBranch)")
    args = ap.parse_args()

    app = Path(args.app).expanduser().resolve()
    lib = Path(args.library)
    lib = lib if lib.is_absolute() else app / lib
    library = Library(app, lib)

    if args.cmd == "check":
        ok = library.check()
        if args.json:
            print(json.dumps({"ok": ok, "errors": library.errors, "warnings": library.warnings,
                              "cases": len(library.cases), "active": len(library.active()),
                              "use_cases": len(library.use_cases)}, indent=2))
        else:
            for e in library.errors:
                print(f"error   {e}")
            for w in library.warnings:
                print(f"warning {w}")
            print(f"{'ok' if ok else 'FAILED'} — {len(library.cases)} cases "
                  f"({len(library.active())} Active), {len(library.use_cases)} use cases, "
                  f"{len(library.errors)} errors, {len(library.warnings)} warnings")
        sys.exit(0 if ok else 1)

    if library.errors:
        print("library has errors — run `check` first:", file=sys.stderr)
        for e in library.errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    if args.cmd == "select":
        if not (args.all or args.area or args.ids or args.type):
            sys.exit("select needs --all, --area <area>, --type <type>, or IDs")
        cases = library.select(args.all or not (args.area or args.ids), args.area, args.ids)
        if args.type:
            cases = [c for c in cases if c["Type"].lower() == args.type.lower()]
        print(json.dumps([public(c) for c in cases], indent=2) if args.json else "", end="")
        if not args.json:
            print_cases(cases)
        return

    report, cases = library.impacted(args.base or library.config.get("baseBranch", "main"))
    if args.json:
        print(json.dumps(report | {"cases": [public(c) for c in cases]}, indent=2))
        return
    print(f"against {report['base']} (merge base {report['merge_base']}): "
          f"{len(report['changed'])} changed files that can affect users")
    for area, why in report["areas"].items():
        print(f"  {area}: " + "; ".join(why[:3]) + (f"; +{len(why) - 3} more" if len(why) > 3 else ""))
    unmapped = report["unmapped"]
    for path in unmapped[:10]:
        print(f"  unmapped: {path}")
    if len(unmapped) > 10:
        print(f"  unmapped: +{len(unmapped) - 10} more (--json lists all)")
    print()
    print_cases(cases)


if __name__ == "__main__":
    main()
