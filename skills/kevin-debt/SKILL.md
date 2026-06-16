---
name: kevin-debt
description: >
  Harvest every `// kevin:` comment in the codebase into a debt ledger. Kevin
  leave intentional shortcuts marked — this collect them so they don't rot into
  "later means never". Use when user says "kevin debt", "/kevin-debt", "what did
  kevin defer", "list shortcuts", "kevin ledger". One-shot report, change nothing.
---

Every kevin shortcut marked with `// kevin:` comment naming ceiling and upgrade trigger. This collect them. Deferral not become permanent.

## Scan

Grep repo for kevin markers, skip `node_modules`, `.git`, build output:

`grep -rnE '(#|//) ?kevin:' .`

Each hit is one ledger row.

## Output

One row per marker, grouped by file:

`<file>:<line> — <what simplified>. ceiling: <limit>. upgrade: <trigger>.`

Flag rot risk: any `// kevin:` with no upgrade trigger get `no-trigger` tag. Those the ones that silently become permanent.

End with: `N markers, M with no trigger.`

Nothing found: `No kevin: debt. Clean ledger. Kevin pleased.`

## Boundaries

Read and report only. Change nothing. To persist: ask and kevin write ledger to `KEVIN-DEBT.md`. One-shot.
