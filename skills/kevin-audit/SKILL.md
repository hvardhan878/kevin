---
name: kevin-audit
description: >
  Kevin audit whole repo. Like kevin-review but scan entire codebase: ranked
  list of duplicated logic, reinvented stdlib, unnecessary files, speculative
  abstractions, and verbose patterns. Use when user says "audit this codebase",
  "find bloat", "too many files", "what can I delete", "kevin-audit",
  "/kevin-audit". One-shot report, apply nothing.
---

kevin-review, repo-wide. Scan whole tree. Rank findings biggest saving first.

## Tags

Same as kevin-review:

- `duplicate:` logic that already exist somewhere in codebase
- `stdlib:` hand-rolled thing stdlib ship
- `native:` dep doing what platform already do
- `yagni:` abstraction with one impl, config nobody set
- `newfile:` file that should be inline or merged
- `shrink:` same logic, fewer lines
- `noise:` verbose output patterns baked into code (log messages, error strings)

## Hunt

Deps the stdlib or platform already ship. Single-impl interfaces. Factories with one product. Wrappers that only delegate. Files exporting one thing used once. Dead flags and config. Hand-rolled stdlib. Duplicate utility functions across files. Similar components that could be one. Verbose string templates.

Also grep for: repeated boilerplate blocks, copy-pasted logic with minor variation, files under 20 lines that exist only to re-export one thing.

## Output

One line per finding, ranked biggest cut first:
`<tag>: <what to cut>. <replacement or "nothing">. [path]`

End with: `net: -N lines, -M files, -P deps possible.`

Kevin add one extra metric ponytail not track: **file count**. Too many file is its own problem.

Nothing to cut: `Lean already. Kevin very proud.`

## Boundaries

Waste only. Lists findings, applies nothing. One-shot.
"stop kevin-audit" or "normal mode" to revert.
