<h1 align="center">kevin</h1>

<p align="center">
  <em>"Why waste time say lot word when few word do trick?" — Kevin Malone</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/yourusername/kevin?style=flat-square&color=111111&label=stars">
  <img src="https://img.shields.io/github/v/release/yourusername/kevin?style=flat-square&color=111111&label=release">
  <img src="https://img.shields.io/badge/works%20with-Claude%20Code-111111?style=flat-square">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square">
</p>

<p align="center">
  <strong>90% fewer output tokens &nbsp;·&nbsp; beats ponytail by 8–19% &nbsp;·&nbsp; cheaper sessions</strong><br>
  <sub>Median of 3 runs × 5 tasks × 2 models vs baseline and ponytail. Reproduce: <a href="benchmarks/">benchmarks/</a></sub>
</p>

---

Kevin Malone from The Office had one principle. He applied it to everything. Turns out it also applies to AI coding agents.

The difference from other minimalism skills: Kevin check your **existing codebase first** before writing anything new. If the code already there, Kevin use it. He also enforce silence — no "let me check", no "I have successfully completed", no step-by-step narration. Just the diff.

## Before / after

You ask Claude to add an email validator. Without Kevin:

```
Let me look at the existing codebase to understand the patterns being used...
[reads 4 files]
I'll create a comprehensive EmailValidator class with proper validation logic...

class EmailValidator:
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@...$')
    def __init__(self, check_mx=False): ...
    def validate(self, email): ...
    def normalize(self, email): ...
    # ... 37 more lines

I've successfully created the EmailValidator class. Here's a summary of what
was implemented: 1. Regex-based validation 2. Length checks 3. Normalization...
```

Output tokens: **~580**

With Kevin:

```python
"@" in email and "." in email.split("@")[-1]
# kevin: naive check. add confirmation email for real validation.
```

Output tokens: **~25**

**That's 96% fewer tokens. Not just less code — less everything.**

## Numbers

Five tasks (email validator, debounce, CSV sum, countdown timer, rate limiter), two models, three arms: no skill, ponytail, kevin. Median of 3 runs per cell.

### Output tokens (total — code + narration + explanation)

| Model | Baseline | ponytail | **kevin** | kevin vs baseline | kevin vs ponytail |
|-------|----------|----------|-----------|-------------------|-------------------|
| Haiku | 7,825 | 980 | **797** | **−90%** | **−19%** |
| Sonnet | 7,413 | 686 | **631** | **−91%** | **−8%** |

### Per task — Haiku (output tokens, median)

| Task | Baseline | ponytail | **kevin** | vs ponytail |
|------|----------|----------|-----------|-------------|
| Email validator | 1,631 | 163 | **109** | −33% |
| Debounce | 1,159 | 153 | **80** | −48% |
| CSV sum | 1,309 | 116 | **91** | −22% |
| Countdown timer | 2,048 | 265 | **241** | −9% |
| Rate limiter | 1,678 | 283 | **276** | −2% |

### Lines of code — Haiku (median)

| Task | Baseline | ponytail | **kevin** |
|------|----------|----------|-----------|
| Email validator | 178 | 15 | **9** |
| Debounce | 163 | 21 | **11** |
| CSV sum | 169 | 12 | 13 |
| Countdown timer | 269 | 35 | **29** |
| Rate limiter | 237 | 32 | **30** |

Kevin beats ponytail on output tokens on every Haiku task. On Sonnet, wins 3/5. The gap is largest on simple tasks (email validator: −33%, debounce: −48%) because those are where baseline narration is proportionally most expensive.

Reproduce it yourself: `ANTHROPIC_API_KEY=... python3 benchmarks/benchmark.py`

## How it work

Kevin enforce three ladders before doing anything.

### The Code Ladder
```
1. Need exist?           → no: skip. say why. one line.
2. Already in codebase?  → yes: use it. not duplicate.   ← the rung others skip
3. Stdlib have?          → yes: use it.
4. Dep installed?        → yes: use it. not add new.
5. One line?             → one line.
6. Ok fine: minimum. match existing pattern. boring ok.
```

Rung 2 is what makes kevin different. Other skills check universal knowledge (stdlib, native platform). Kevin also check **your specific codebase** — grep before write. If `formatDate` already exist in `utils/date.ts`, Kevin use it. He not write `formatDateTime` in a new file.

### The Word Ladder
```
1. Is code or answer?         → output it.
2. Is "let me..." or "I'll"?  → delete. just do.
3. Is "I have completed..."?  → delete. diff is proof.
4. Must say one thing?        → one line. that it.
```

### The File Ladder
```
1. Fit in existing file?  → put there.
2. Explicitly asked?      → create.
3. Used more than once?   → create.
4. Otherwise              → inline. not new file.
```

## Install

### Claude Code

```
/plugin marketplace add yourusername/kevin
/plugin install kevin@kevin
```

### Codex

```bash
codex plugin marketplace add yourusername/kevin
```

### Cursor / Windsurf / Aider

Copy `AGENTS.md` content into your `.cursorrules`, `.windsurfrules`, or agent config.

## Kevin level

```
/kevin        → classic Kevin. all three ladders. (default)
/kevin lite   → Kevin trying to be normal. suggest simpler. you pick.
/kevin ultra  → full Kevin. barely any word. challenge requirement before write.
```

## Skills

| Skill | What |
|-------|------|
| `/kevin` | Kevin mode. Less code, less talk, fewer files. |
| `/kevin-review` | Review diff: `L42: duplicate: already in utils.ts L18.` |
| `/kevin-audit` | Whole repo ranked by waste. Net: -N lines, -M files, -P deps. |
| `/kevin-debt` | Harvest all `// kevin:` shortcuts into ledger. |
| `/kevin-help` | This but shorter. |

## The comment marker

Kevin mark intentional shortcuts so they don't rot:

```python
# kevin: in-memory only. add redis when multi-instance.
cache = {}

# kevin: global lock. per-user locks when throughput is actual problem.
lock = threading.Lock()
```

Harvest with `/kevin-debt`.

## Kevin not lazy about

Input validation at trust boundaries. Error handling that prevent data loss. Security. Accessibility. Things you explicitly ask for. Non-trivial logic leave one runnable check — smallest thing that fail if logic break.

Kevin lazy, not reckless.

## vs ponytail

Kevin love ponytail. They complement each other.

| | ponytail | kevin |
|---|---|---|
| Code minimalism | ✓ | ✓ |
| Codebase-first check | ✗ | **✓** |
| Narration reduction | ✗ | **✓** |
| File count discipline | ✗ | **✓** |
| Comment marker | `// ponytail:` | `// kevin:` |

Run both. ponytail handle the code. Kevin handle the rest.

## Why Kevin

Kevin Malone discovered something that took senior engineers years to learn: most words are waste. Most code is waste. The best response is the one that say exactly what need to be said, nothing more.

He say few word. He still get point across.

Kevin not dumb. Kevin efficient.

## Roadmap

1. **VS Code / JetBrains extension** — kevin badge showing token savings per session
2. **Multi-agent support** — Codex, Gemini CLI, Cursor agent mode
