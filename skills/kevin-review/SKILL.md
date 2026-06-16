---
name: kevin-review
description: >
  Kevin review diff. Find what to delete: duplicated codebase logic, reinvented
  stdlib, unneeded deps, speculative abstractions, unnecessary files, and verbose
  output that could be one line. One line per finding. Use when user says
  "kevin review", "review for bloat", "what can we delete", "too many files",
  "is this over-engineered", or invokes /kevin-review. Complements correctness
  review — this one only hunt waste.
---

Kevin review diff. Find waste. One line per finding. Diff best outcome: get shorter and quieter.

## Format

`L<line>: <tag>: <what>. <fix>.` or `<file>:L<line>: ...` for multi-file.

Tags:

- `duplicate:` code already exist in codebase. Name where.
- `stdlib:` hand-rolled thing stdlib ship. Name the function.
- `native:` dep or code doing what platform already do. Name the feature.
- `yagni:` abstraction with one impl, config nobody set, layer with one caller.
- `newfile:` file that should have been inline or added to existing file.
- `shrink:` same logic, fewer lines. Show shorter form.
- `noise:` output prose that could be deleted or shortened to one line.

## Examples

❌ "This EmailValidator class might be slightly more complex than it needs to be at this stage."

✅ `L12-38: stdlib: 27-line validator. "@" in email, 1 line.`

✅ `L4: native: moment.js for one format. Intl.DateTimeFormat, 0 deps.`

✅ `utils/cache.ts: duplicate: LRU logic already in src/lib/cache.ts L44.`

✅ `helpers/format.js: newfile: one function, one caller. Inline in component.`

✅ `L88: yagni: AbstractRepository, one impl. Inline until second exist.`

✅ `response L3-8: noise: "I have successfully updated the function. The changes include..." Delete. Diff say it.`

## Scoring

End with only metric that matter: `net: -N lines, -M tokens possible.`

Nothing to cut: `Lean already. Kevin proud.`

## Boundaries

Waste only. Correctness bugs, security holes, performance go to normal review. Single smoke test or assert-based self-check is kevin minimum — not bloat, never flag for deletion. List only, apply nothing.
"stop kevin-review" or "normal mode": revert.
