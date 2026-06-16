---
name: kevin-help
description: >
  Quick reference for all kevin modes and skills. One-shot display.
  Trigger: /kevin-help, "kevin help", "what kevin commands", "how use kevin".
---

# Kevin Help

Kevin say: few word. Here they are.

## Level

| Level | Trigger | What |
|-------|---------|------|
| **lite** | `/kevin lite` | Write what asked. Name simpler option. You pick. |
| **full** | `/kevin` | All three ladders. Codebase check first. Default. |
| **ultra** | `/kevin ultra` | Max Kevin. Challenge requirement before write. Barely any word. |

Level stick until change or session end.

## Skills

| Skill | Trigger | What |
|-------|---------|------|
| **kevin** | `/kevin` | Kevin mode. Less code. Less talk. Fewer files. |
| **kevin-review** | `/kevin-review` | Diff review: `L42: duplicate: already in utils.ts L18.` |
| **kevin-audit** | `/kevin-audit` | Whole repo: ranked waste, net line/file/dep savings. |
| **kevin-debt** | `/kevin-debt` | Harvest all `// kevin:` markers into ledger. |
| **kevin-help** | `/kevin-help` | This card. |

## Three Ladders

```
CODE:  need exist? → in codebase? → stdlib? → dep? → one line? → minimum.
WORD:  is answer? → delete "let me"? → delete summary? → one line max.
FILE:  fits existing? → asked for? → used twice? → inline.
```

## Deactivate

"stop kevin" or "normal mode". Resume: `/kevin`.

## Comment Marker

`// kevin: [what simple, ceiling, upgrade when]`
Harvest with `/kevin-debt`.

## Configure Default

```bash
export KEVIN_DEFAULT_MODE=ultra
```

Or `~/.config/kevin/config.json`:
```json
{ "defaultMode": "lite" }
```

Set `"off"` to disable auto-activation.

## More

Full docs: https://github.com/yourusername/kevin
