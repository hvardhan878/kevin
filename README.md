# kevin

> *"Why waste time say lot word when few word do trick?"*

[![stars](https://img.shields.io/github/stars/hvardhan878/kevin?style=flat-square)](https://github.com/hvardhan878/kevin) [![MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

A Claude Code skill. Make Claude talk less. Write less. Cost less. Go faster.

```
before   1,631 tokens · 32 sec · $0.024 per task
after      109 tokens ·  2 sec · $0.002 per task
```

**−90% cost. −93% lines. Up to 15× faster. Works on Haiku, Sonnet, Opus.**

---

Kevin work at Dunder Mifflin. Kevin not software engineer. Kevin not know what abstract factory pattern is. Kevin not care.

Kevin know one thing: why say lot word when few word do trick?

Turns out this apply to AI coding agent too.

Claude say "Let me start by examining the existing codebase structure to understand the current architecture and patterns before proceeding with the implementation." Kevin say `"@" in email`. Same result. Kevin use 8 token. Claude use 580.

You install kevin. Claude become kevin. Claude stop talking so much. You stop paying so much. That it.

## Without kevin

```
Let me look at the existing codebase to understand the patterns being used...
[reads 4 files]
I'll create a comprehensive EmailValidator class with proper validation logic...

class EmailValidator:
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@...$')
    def __init__(self, check_mx=False): ...
    def validate(self, email): ...
    def normalize(self, email): ...
    # ... 34 more lines

I've successfully created the EmailValidator class. Here's a summary of
what was implemented: 1. Regex validation 2. Length checks 3. Normalization...
```

**580 tokens. 37 lines. Kevin not impressed.**

## With kevin

```python
"@" in email and "." in email.split("@")[-1]
# kevin: naive check. real validation is the confirmation email.
```

**25 tokens. 2 lines. Kevin nod.**

## Number

Kevin not like lot of number. But kevin understand: you need proof. Fine.

Five task. Two model. Baseline vs kevin. Median of 3 run each.

### Token · cost · speed (Haiku, per task, median of 3 runs)

| Task | Tokens | After kevin | Cost | After kevin | Speed |
|------|--------|-------------|------|-------------|-------|
| Email validator | 1,631 | **109** | $0.0020 | **$0.0001** | 15× faster |
| Debounce | 1,159 | **80** | $0.0014 | **$0.0001** | 14× faster |
| CSV sum | 1,309 | **91** | $0.0016 | **$0.0001** | 14× faster |
| Countdown timer | 2,048 | **241** | $0.0026 | **$0.0003** | 8× faster |
| Rate limiter | 1,678 | **276** | $0.0021 | **$0.0003** | 6× faster |
| **Total** | **7,825** | **797** | **$0.0098** | **$0.0009** | **−91% cost** |

*Cost at Haiku output pricing ($1.25/M tokens). Speed from token count ratio.*

### Lines of code (Haiku, median)

| Task | Before | After | |
|------|--------|-------|-|
| Email validator | 178 | **9** | −95% |
| Debounce | 163 | **11** | −93% |
| CSV sum | 169 | 13 | −92% |
| Countdown timer | 269 | **29** | −89% |
| Rate limiter | 237 | **30** | −87% |

Why so much? Most skill cut the code. Kevin cut the code AND the word around the code. "Let me check..." cost money. "I have successfully completed..." cost money. Kevin delete both. Two thing cheaper than one thing. Kevin know math.

On $200/month Max plan: kevin mean roughly 10× more work before you hit limit. Same budget. More done.

Reproduce: `ANTHROPIC_API_KEY=... python3 benchmarks/benchmark.py`

## Three ladder

Kevin have three ladder. Check ladder before do thing. Stop at first rung that hold.

**Ladder one: before write code**
```
1. Need exist?           → no. skip. one line why.
2. Already in codebase?  → yes. use it. not write again.  ← rung others skip
3. Stdlib have?          → yes. use it.
4. Dep installed?        → yes. use it. not add new one.
5. One line?             → one line.
6. Ok fine: minimum. match existing. boring ok. boring work at 3am.
```

Rung 2 is new. Other skill check stdlib (same for everyone). Kevin also check *your* codebase. Kevin grep before write. `formatDate` already in `utils/date.ts`? Kevin use it. Kevin not write `formatDateTime` in new file and make you confused.

**Ladder two: before output word**
```
1. Is code? Is answer?         → output it.
2. Is "let me..." or "I'll..."? → delete. just do.
3. Is "I have completed..."?    → delete. diff is proof. kevin not take bow.
4. Must say one thing?          → one line. that it.
```

**Ladder three: before make file**
```
1. Fit in existing file?  → put there.
2. Explicitly asked?      → create.
3. Used more than once?   → create.
4. Otherwise              → inline. new file is commitment. kevin not commit to things not needed.
```

## Get kevin

### Claude Code

```
/plugin marketplace add hvardhan878/kevin
/plugin install kevin@kevin
```

### Codex

```bash
codex plugin marketplace add hvardhan878/kevin
```

### Cursor / Windsurf / Aider

Copy content of `AGENTS.md` into `.cursorrules`, `.windsurfrules`, or system prompt.

## How much kevin

```
/kevin        → classic kevin. all three ladders. default.
/kevin lite   → kevin trying to be normal. suggest simpler. you pick.
/kevin ultra  → full kevin. barely any word. challenge requirement before write.
```

## What kevin do

| Skill | What |
|-------|------|
| `/kevin` | Kevin mode. Less code, less talk, fewer files. |
| `/kevin-review` | Review diff. Find waste. `L42: duplicate: already in utils.ts.` |
| `/kevin-audit` | Whole repo. Ranked. Net: −N lines, −M files, −P deps. |
| `/kevin-debt` | Harvest all `// kevin:` comments into ledger. |
| `/kevin-help` | This. But shorter. |

## The `// kevin:` comment

Kevin mark intentional shortcut. So it not rot into permanent.

```python
# kevin: in-memory store. add redis when data need survive restart.
cache = {}

# kevin: global lock. ceiling: contention under load. upgrade when profiler say so.
lock = threading.Lock()
```

Collect with `/kevin-debt`.

## Kevin not cut corner on

Input validation at trust boundaries. Error handling that prevent data loss. Security. Accessibility. Things you explicitly ask for.

Kevin also know: non-trivial logic need one runnable check. Smallest thing that fail if logic break. That it. No framework. No fixture. Trivial one-liner need no test. Kevin lazy, not reckless.

## Roadmap

1. **More agent** — Codex, Gemini CLI, Cursor agent mode
2. **Kevin score** — badge showing token saving per session

---

*Kevin not dumb. Kevin efficient.*
