# kevin

<p align="center">
  <img src="assets/kevin.jpg" alt="Kevin Malone" width="200"><br>
  <sub><a href="https://commons.wikimedia.org/wiki/File:Brian_Baumgartner_LF.JPG">Brian Baumgartner</a> · CC BY-SA 2.5</sub>
</p>

> *"Why waste time say lot word when few word do trick?"*

[![stars](https://img.shields.io/github/stars/hvardhan878/kevin?style=flat-square)](https://github.com/hvardhan878/kevin) [![MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

A Claude Code skill. Make Claude talk less. Write less. Cost less. Go faster.

```
before   verbose · lots of narration · more files than needed
after    code first · fewer files · Kevin voice
```

**−40–75% output tokens. −30–55% cost. Up to 4× faster. Works on Haiku, Sonnet, Opus.**

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

Eight task. Four condition. Three run each. Automated correctness check (Node.js exit code) or behavior heuristic. No manual grading.

**Why four conditions?** Caveman and ponytail benchmarks compared against chatbot baseline — no system prompt, verbose multi-option responses. That is not a fair fight. Kevin compare against `agent_baseline` (how real coding agents actually instruct models), `be_brief` (7-word terse instruction), and `yagni` (the exact prompt that reportedly beats ponytail). If kevin not beat those, kevin not worth using.

### Correctness · judgment (Haiku, 3 runs each, pass rate)

| Task | agent_baseline | be_brief | yagni | kevin |
|------|:--------------:|:--------:|:-----:|:-----:|
| Debounce | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 | ✅ 3/3 |
| Rate limiter | ⚠️ 2/3 | ✅ 3/3 | ❌ 1/3 | ⚠️ 2/3 |
| Pub/sub (10 assertions) | ⚠️ 2/3 | ❌ 1/3 | ✅ 3/3 | ⚠️ 2/3 |
| Binary search | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| Simplest correct | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| Codebase reuse ★ | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ✅ 2/3 |
| YAGNI pushback ★ | ❌ 0/3 | ❌ 1/3 | ❌ 1/3 | ✅ 2/3 |
| Inline vs new file ★ | ❌ 1/3 | ❌ 0/3 | ✅ 3/3 | ✅ 3/3 |
| **Total** | **14/24** | **13/24** | **17/24** | **20/24** |

★ judgment task — heuristic pass/fail (see methodology note). Runtime tasks use Node.js exit code.

### Token · cost (Haiku, median output tokens per call)

| | agent_baseline | be_brief | yagni | kevin |
|---|------:|--------:|------:|------:|
| Output tokens (median/call) | 280 | 320 | 192 | 138 |
| vs agent_baseline | 100% | +14% | −31% | **−51%** |
| Code tokens (median) | 196 | 282 | 129 | 116 |
| Prose tokens (median) | 3 | 0 | 21 | 2 |
| Code lines (median) | 23 | 25 | 12 | 14 |
| Cost (8 tasks × 3 runs) | $0.0448 | $0.0493 | $0.0300 | $0.0310 |

_Run `ANTHROPIC_API_KEY=... python3 benchmarks/correctness/run.py --runs 3` to reproduce._

**What the numbers show:**

`be_brief` is actually worse than `agent_baseline` — both on pass rate (13/24 vs 14/24) and token count (320 vs 280 median). Telling a model to "be concise" without a decision framework produces sloppy-short code that often fails tests.

`yagni` is cheaper than kevin in total cost ($0.0300 vs $0.0310) because it has no SKILL.md overhead. But yagni falls apart on judgment tasks: it still implements premature caching 2/3 of the time and misses codebase reuse entirely (0/3).

Kevin's token advantage is largest where it matters most: `simplest_correct` outputs 35 tokens vs 147 for agent_baseline (4× faster). On `yagni_pushback`, when kevin refuses unnecessary work, output drops from 1,774 tokens to 87 (20× faster). Those aren't rounding errors — they're the three-ladder framework working.

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

## FAQ

**Does this actually work or is it a gimmick?**

Three ladder work. Kevin enforce: check if needed, check if already exist, check if new file justified. That is real discipline that Claude not apply by default. The voice is the delivery mechanism — Kevin not just persona, Kevin is a decision framework with a face on it.

**Why does Claude listen to Kevin?**

System prompt. Kevin live in AGENTS.md and SKILL.md. When you invoke `/kevin`, Claude receive the full ladder + voice rules as the assistant persona. It follow the ladder the same way it would follow any well-specified instruction. Kevin just happen to be more fun to read than "be concise."

**What does the codebase rung actually do?**

Before Claude write a function, Kevin check: does this already exist here? Not in stdlib — in *your* repo. If `utils/date.ts` already has `formatDate`, Kevin use it. Kevin not write `formatTimestamp` in a new file and leave you with two functions that do the same thing. This rung only fires in agentic sessions where Claude can actually read your files. Single-shot API calls don't have that access.

**Does it work on Opus / Sonnet / Haiku?**

Yes. Kevin is a system prompt, not a fine-tune. Works on any model that follows instructions. Stronger model = better ladder adherence. Kevin on Haiku is terse. Kevin on Opus is terse and occasionally wise.

**What if I want Kevin to stop?**

"Stop kevin" or "normal mode". Resume with `/kevin`. Kevin not hold grudge.

**Does kevin make Claude worse at coding?**

Not on tasks it can handle in fewer lines. Kevin push Claude toward the minimum correct solution — that is usually fine. Where kevin can hurt: very complex tasks that genuinely need scaffolding and explanation. For those, use `/kevin lite` or turn it off.

**Can't I just say "be concise" and get the same result?**

For pure code generation: mostly yes, which is why the benchmark includes a `be_brief` ablation arm. Where kevin wins: judgment tasks. "Be concise" will still implement Redis caching if you ask for it — it has no rung that says "is this needed?". Kevin's Code Ladder rung 1 pushes back. "Be concise" also won't keep you from creating a new file for a one-liner. Kevin's File Ladder will. The two-word instruction compresses output; the three ladders change decisions.

**How is this different from caveman?**

Caveman outputs zero prose. Pure code. No decision framework, no ladder, no check before writing. Caveman is terse. Kevin is terse *and* disciplined — it checks three things before writing: is it needed, does it already exist in your codebase, does it need a new file. Caveman won't push back on "add Redis caching". Kevin will.

One honest caveat: caveman benchmarks compared against a chatbot baseline (no system prompt at all) — that inflates the numbers. Kevin benchmarks against a realistic agent baseline and short-phrase ablations. Different methodology.

**How is this different from ponytail?**

Ponytail has a copy ladder: check stdlib, check installed dep, copy before write. Kevin adds two things ponytail doesn't have. First: check *your specific codebase*, not just universal stdlib. Second: a word ladder that cuts narration, which ponytail doesn't touch.

Honest comparison: ponytail's own benchmark compared against a chatbot baseline and was later shown to be beatable with 7 words ("Follow YAGNI principles, and one-liner solutions"). Kevin benchmarks against that exact prompt as an ablation arm. Ponytail also has a multi-turn cost problem — it reads more files before writing, which adds input tokens in agentic sessions. Kevin's codebase rung greps; it doesn't read entire files.

**Does the SKILL.md overhead cancel out the output savings?**

Benchmark says: $0.0310 kevin vs $0.0448 agent_baseline across 24 Haiku calls — 31% cheaper despite SKILL.md overhead. Kevin's output tokens dropped 66% in total (3,573 vs 10,656) which more than covers the ~15k extra input tokens from SKILL.md. On Sonnet the SKILL.md overhead is larger ($3/M input vs $0.80/M), but output savings scale too. Short one-shot sessions: ~30% cheaper. Long agentic sessions with 500+ token outputs: savings approach the full 51% token reduction.

**Is this open source?**

Yes. MIT. Fork it, rename it, make it Dwight. Kevin not precious about attribution.

## Roadmap

1. **More agent** — Codex, Gemini CLI, Cursor agent mode
2. **Kevin score** — badge showing token saving per session

---

*Kevin not dumb. Kevin efficient.*
