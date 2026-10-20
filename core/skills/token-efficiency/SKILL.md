---
name: token-efficiency
description: >-
  Reduce token waste when reading or searching files, querying structured data,
  inspecting diffs, handling verbose tool output, or running long agent sessions
  with subagents (fe-build, fe-e2e). Use when exploring a codebase, reviewing
  git diffs, spawning frontend-flow agents, or when the user asks to save tokens
  or work more efficiently.
---

# Token-Efficient Computer Use

Optimize total cost and time to a verified result. Smaller outputs help when they preserve the evidence needed to finish correctly; extra searches, retries, and coordination can erase the savings.

Before a tool call, ask whether current evidence already answers the question and what information the next decision actually needs.

## Session and subagent habits (highest leverage)

Long chats, large context, and heavy subagents often dominate cost. Fix those before micro-optimising searches.

- One concern per chat (plan approval, or one build step + gates). Avoid leaving Agent / loop sessions open for hours.
- `/compact` mid-task; `/clear` when switching tickets or finishing a batch.
- Resume from the feature spec’s Flow status, not from pasting chat history.
- One plan step per `fe-build`, then stop. Do not chain unsupervised `/fe:run` for hours.
- Run lint / typecheck / focused tests locally for small changes instead of spawning `fe-verify` every time.
- Run browser e2e only for visible UI steps or handoff; prefer impacted or named cases over `--all`.
- Prefer conclusions with path:line refs over pasting large dumps into the reply.
- A smaller parent context does not imply lower total cost: count child-agent usage.

Do not weaken project gates (spec/plan approval, governing standards) to save tokens.

## Output, MCP, models, and first-pass (compound savings)

These cut cost in different parts of the bill. Stack them with the habits above.

### Terse replies (output tokens)

Output is often billed higher than input. Default to dense answers: no filler openers, no unsolicited walkthroughs, no restating the question. Lead with the result; add detail only when asked or when a gate/approval needs it. If the user asks for explanation, tone, or a draft for humans (spec prose, Jira comment), drop terseness for that turn.

### MCP only when needed

Each connected MCP server can load large tool schemas into context every turn. Call MCP only when the task needs that system (e.g. Jira). Prefer one targeted operation over discovering or listing every tool. Do not enable or probe unused MCP servers “just in case.”

### Model choice (Cursor / Claude)

In Cursor, `fe-*` agents use `model: inherit` — they follow the parent chat. Pick **Auto** or a cheaper model in the picker when cost matters; use a stronger model for spec/plan/build. Do not invent model names or change agent defs without the person asking.

### First-pass accuracy beats short replies

One re-prompt on a large context re-reads tens of thousands of tokens. Read the governing standard once and match it; ask ambiguous product questions before writing code. Prefer preventing a wrong build over compressing a correct one.

## Read selectively and expand when needed

- Use available filtered reads and searches that fit the task and the harness's tool guidance. Use shell pipelines for data transformations and queries the native tools do not cover.
- Locate files or symbols with filenames, counts, or bounded matches, then read relevant spans and dependencies. Expand when the result is ambiguous. A capped or truncated search does not establish that other matches are absent.
- Use AST search for structural code patterns and text search for literals, configuration, or logs. Do not install a new search tool unless repeated use justifies the setup.
- `rg` recurses by default. Its `-r` flag means `--replace`, not recursion. Its `-m` match limit applies per file, not across the entire search.
- For broad Git changes, start with `git diff --stat` or `--name-only`, then inspect relevant files. Read a small, targeted diff directly.

## Query and generate at the source

- Project JSON with `jq`; use format-aware tools for YAML, TOML, and XML. Check which `yq` implementation is installed before relying on its options.
- Use `cut` or `awk` for simple delimited text; use a CSV-aware parser for quoted fields or embedded newlines. Choose a compact format that preserves the data's structure.
- Generate repetitive content, conversions, and mechanical edits with a short script when that is simpler and more reliable than emitting the result manually. Choose the language for correctness, not a blanket preference for shell or Python.

## Reduce noise without losing evidence

- Use quiet flags and disable color where supported, while retaining failure diagnostics.
- Save unpredictable or verbose output to a file and inspect relevant sections. Reuse output the harness already persisted instead of rerunning the command solely to recover it.
- Preserve the original command's exit status when capturing or piping output; a successful formatter does not prove the command succeeded.
- Retain exact errors, relevant constraints, failed approaches, and paths or URLs needed to recover details. Recheck evidence when the underlying state changes.

## Account for execution overhead

- Run independent calls in parallel when supported and permitted. Chain dependent commands with `&&` when useful, keeping approval boundaries clear.
- Prefer completion notifications to polling. If polling is necessary, use metadata or hashes when they answer the question more cheaply than rereading the content.
- Delegate substantial, separable work when isolation or parallelism justifies setup and coordination. Request conclusions with references to supporting evidence.

## Preserve useful context and cache reuse

Keep prompt prefixes stable where practical and avoid unnecessary changes to prompt-affecting configuration. Cache behavior and pricing depend on the provider and model.

Use the harness's compaction or context-management mechanisms when needed. Preserve the task's constraints, verified findings, failed attempts, next steps, and references to recoverable details. Judge context reduction by subsequent correctness, retries, total cost, and latency.

<!-- profile -->
