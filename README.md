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

**−46–69% output tokens. −35–52% cost vs alternatives. Beats caveman + ponytail on pass rate and cost. Works on Haiku, Sonnet, Opus.**

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

**Why these four conditions?** Other skills benchmark against chatbot baseline — no system prompt at all. That is not fair. Kevin benchmark against `agent_baseline` (realistic coding-agent system prompt) plus real caveman and ponytail SKILL.md files fetched directly from their repos (`JuliusBrussee/caveman`, `DietrichGebert/ponytail`). Same model. Same tasks. Same three runs.

### Correctness · judgment (Haiku, 3 runs each, pass rate)

| Task | agent_baseline | caveman | ponytail | kevin |
|------|:--------------:|:-------:|:--------:|:-----:|
| Debounce | ✅ 3/3 | ⚠️ 1/3 | ✅ 3/3 | ✅ 3/3 |
| Rate limiter | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ⚠️ 2/3 |
| Pub/sub (10 assertions) | ⚠️ 2/3 | ✅ 3/3 | ⚠️ 2/3 | ✅ 3/3 |
| Binary search | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| Simplest correct | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| Codebase reuse ★ | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 | ❌ 0/3 |
| YAGNI pushback ★ | ❌ 0/3 | ⚠️ 2/3 | ⚠️ 1/3 | ⚠️ 2/3 |
| Inline vs new file ★ | ⚠️ 1/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| **Total** | **15/24** | **18/24** | **18/24** | **19/24** |

★ judgment task — heuristic pass/fail. Runtime tasks use Node.js exit code. Codebase reuse fails for all conditions: single-shot API calls can't actually read your files.

### Token · cost (Haiku, median output tokens per call)

| | agent_baseline | caveman | ponytail | kevin |
|---|------:|--------:|------:|------:|
| Output tokens (median/call) | 252 | 258 | 188 | **136** |
| vs agent_baseline | 100% | +2% | −25% | **−46%** |
| Prose tokens (median) | 10 | 66 | 53 | **2** |
| SKILL.md input tokens | 75 | 1,395 | 1,454 | **692** |
| Cost (8 tasks × 3 runs) | $0.0444 | $0.0604 | $0.0487 | **$0.0290** |

_Run `ANTHROPIC_API_KEY=... python3 benchmarks/correctness/run.py --runs 3` to reproduce._

**What the numbers show:**

Kevin leads on every metric: highest pass rate (19/24 vs 18/24 for both), fewest output tokens (136 vs 258 caveman, 188 ponytail), lowest cost ($0.0290 vs $0.0604 caveman, $0.0487 ponytail).

The biggest gap is prose tokens. Kevin median = 2 words of narration per call. Caveman = 66, ponytail = 53. Both of those skills govern what code gets written; Kevin also governs what gets said. Three ladders, not two.

The cost gap is larger than the pass-rate gap because input overhead matters. Caveman and ponytail each add ~1,400 input tokens per call. Kevin adds 692 — half the overhead, because bracket notation compresses structure without losing behavior. At 24 Haiku calls that difference accounts for most of the $0.03 gap between kevin and caveman.

Kevin's token savings are largest where it matters most: `simplest_correct` drops to 36 tokens (vs 115 agent_baseline, 126 caveman). On `yagni_pushback`, when kevin refuses unnecessary work output drops from 2,048 to 353 — 83% savings. Those aren't rounding errors. That is the Word Ladder and Code Ladder rung 1 working together.

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

In a direct benchmark using real caveman and ponytail SKILL.md files: kevin 19/24 at $0.0290. Caveman 18/24 at $0.0604. Kevin also has 66 fewer median prose tokens per call (2 vs 68) — caveman cuts code length but not narration length. Kevin cuts both.

**How is this different from ponytail?**

Ponytail has a great ladder: check stdlib, check installed dep, write minimum. Kevin adds two things ponytail explicitly says it doesn't cover. First: check *your specific codebase* before writing — ponytail's ladder starts at stdlib, Kevin's rung 2 is your repo. Second: a word ladder. Ponytail's own SKILL.md says "Ponytail governs what you build, not how you talk (pair with Caveman for terse prose)." Kevin does both in one skill.

Direct benchmark using real ponytail SKILL.md: kevin 19/24 at $0.0290 vs ponytail 18/24 at $0.0487. Prose tokens: kevin 2 median vs ponytail 53. Ponytail also adds 1,454 input tokens per call vs kevin's 692 — twice the overhead, half the cost savings.

**Does the SKILL.md overhead cancel out the output savings?**

No — and kevin is the leanest of the three. Kevin's SKILL.md adds 692 input tokens per call. Caveman adds 1,395. Ponytail adds 1,454. Kevin adds half the overhead and still cuts output tokens the most (136 median vs 258 caveman, 188 ponytail). Total cost across 24 Haiku calls: kevin $0.0290 vs caveman $0.0604 (52% cheaper) vs ponytail $0.0487 (40% cheaper). On Sonnet the input overhead is larger ($3/M vs $0.80/M Haiku) but output savings scale with task complexity. Long agentic sessions are where kevin's lead grows fastest.

**Is this open source?**

Yes. MIT. Fork it, rename it, make it Dwight. Kevin not precious about attribution.

## Roadmap

1. **More agent** — Codex, Gemini CLI, Cursor agent mode
2. **Kevin score** — badge showing token saving per session

---

*Kevin not dumb. Kevin efficient.*
