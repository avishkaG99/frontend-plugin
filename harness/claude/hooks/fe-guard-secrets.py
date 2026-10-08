#!/usr/bin/env python3
"""PreToolUse hook: keep agents out of the test-account credentials and saved sessions.

The accounts file (~/.config/frontend-flow/<profile>/test-accounts.env) and Playwright
storage states (.auth/*.json) are read only by the scripts that need them —
scripts/login.py and the browser run. No tool call may open, print, search, copy or edit
them. Running login.py is fine: it never puts a secret in its output.

This is a guardrail, not a sandbox: it matches paths and command text, so it stops the
ordinary ways of reading the file, which is what an honest agent would do by mistake.
Denies with a reason; never crashes a tool call on its own error.
"""
import json
import re
import sys

PROTECTED = [
    re.compile(r"\.config/frontend-flow\b"),
    re.compile(r"test-accounts\.env"),
    re.compile(r"(^|[/\s'\"])\.auth/[^\s'\"]*\.json"),
    re.compile(r"FE_FLOW_ACCOUNTS"),
]
REASON = ("Blocked by fe-guard-secrets: test-account credentials and saved sessions are read "
          "only by frontend-plugin/scripts/login.py and the browser run. Use `login.py --list` "
          "to see which roles are ready; ask the person to edit the file themselves.")


# The fields that open, search or execute something. File *contents* being written are not
# checked: a run script may name a storage-state path, which the browser then loads.
CHECKED_FIELDS = ("file_path", "path", "notebook_path", "pattern", "glob", "command")


def checked_strings(tool_input):
    for field in CHECKED_FIELDS:
        value = tool_input.get(field)
        if isinstance(value, str):
            yield value


def main():
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input") or {}
    for text in checked_strings(tool_input):
        if any(p.search(text) for p in PROTECTED):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            }}))
            return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
