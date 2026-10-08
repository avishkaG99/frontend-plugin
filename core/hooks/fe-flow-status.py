#!/usr/bin/env python3
"""SessionStart hook: tell a new session which features are mid-flight.

Finds feature specs carrying a `## Flow status` block (see the frontend-flow skill's
references/conductor.md) whose stage is not `done`, and prints one line per feature. Claude
Code adds the output to the session's context, so the first reply already knows where
things stand. Prints nothing when no feature is in progress.

Advisory only: it never blocks, and any error exits 0 silently. A broken hook must not
stand between the person and their session.
"""
import os
import sys
import time
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", "bin", "obj", ".next",
    "coverage", ".claude", ".cursor", "harness", "__pycache__", ".turbo", ".cache",
}
HEADING = "## Flow status"
BUDGET_SECONDS = 3.0
MAX_SHOWN = 5


def find_specs(root, deadline):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if time.monotonic() > deadline:
            return
        for name in filenames:
            if name.endswith(".md"):
                yield Path(dirpath) / name


def section_lines(text):
    """Lines of the real Flow status section, ignoring examples inside code fences."""
    in_fence, inside, lines = False, False, []
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            if inside:
                break
            inside = line.strip() == HEADING
            continue
        if inside:
            lines.append(line)
    return lines if inside or lines else None


def read_block(path):
    """The Flow status fields as a dict, or None when the file has no block."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    body = section_lines(text)
    if body is None:
        return None
    fields = {}
    for line in body:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] and not set(cells[0]) <= {"-", ":"}:
            fields[cells[0].lower()] = cells[1]
    return fields


def main():
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    deadline = time.monotonic() + BUDGET_SECONDS
    active = []
    for path in find_specs(root, deadline):
        fields = read_block(path)
        if not fields:
            continue
        stage = fields.get("stage", "").strip().lower()
        if not stage or stage in {"done", "field"}:
            continue
        active.append((path.stat().st_mtime, path, fields))
    if not active:
        return

    active.sort(reverse=True)
    lines = ["Frontend features in progress (from their specs' Flow status blocks):"]
    for _, path, f in active[:MAX_SHOWN]:
        rel = path.relative_to(root)
        parts = [f"stage {f.get('stage', '?')}"]
        if f.get("next") and f["next"] != "—":
            parts.append(f"next: {f['next']}")
        if f.get("waiting on") and f["waiting on"] not in {"—", "-", ""}:
            parts.append(f"waiting on: {f['waiting on']}")
        ticket = f.get("ticket")
        label = f"{ticket} · {rel}" if ticket and ticket != "—" else str(rel)
        lines.append(f"- {label} — " + "; ".join(parts))
    if len(active) > MAX_SHOWN:
        lines.append(f"- …and {len(active) - MAX_SHOWN} more")
    lines.append("Resume one with /fe:run <ticket or slug>; /fe:run --status shows where it stands.")
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
