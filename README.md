<h1 align="center">kevin</h1>

<p align="center">
  <em>"Why waste time say lot word when few word do trick?"</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/hvardhan878/kevin?style=flat-square&color=111111&label=stars">
  <img src="https://img.shields.io/github/v/release/hvardhan878/kevin?style=flat-square&color=111111&label=release">
  <img src="https://img.shields.io/badge/works%20with-Claude%20Code-111111?style=flat-square">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square">
</p>

<p align="center">
  <strong>−90% output tokens &nbsp;·&nbsp; −93% lines of code &nbsp;·&nbsp; works on Haiku, Sonnet, Opus</strong><br>
  <sub>3 runs × 5 tasks × 2 models. Reproduce: <a href="benchmarks/">benchmarks/</a></sub>
</p>

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

### Output token (code + narration + all the "let me" and "I have completed")

| | Baseline | **kevin** | reduction |
|--|----------|-----------|-----------|
| Haiku | 7,825 | **797** | **−90%** |
| Sonnet | 7,413 | **631** | **−91%** |

### Per task — Haiku

| Task | Baseline | **kevin** | reduction |
|------|----------|-----------|-----------|
| Email validator | 1,631 | **109** | −93% |
| Debounce | 1,159 | **80** | −93% |
| CSV sum | 1,309 | **91** | −93% |
| Countdown timer | 2,048 | **241** | −88% |
| Rate limiter | 1,678 | **276** | −84% |

Why so much? Most skill only cut the code. Kevin cut the code AND all the word around the code. Two thing cheaper than one thing. Kevin know math.

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
