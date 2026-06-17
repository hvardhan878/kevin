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

**−50–80% tokens. −50–75% cost. Up to 3× faster. Works on Haiku, Sonnet, Opus.**

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

Five task. Two condition. Automated correctness check (`node test.js`, exit code). No manual grading.

### Correctness suite (Haiku, single run)

| Task | Baseline | Kevin |
|------|:--------:|:-----:|
| Debounce | ✅ | ✅ |
| Rate limiter | ✅ | ✅ |
| Codebase reuse | ❌ | ❌ |
| Pub/sub (10 assertions) | ✅ | ✅ |
| Binary search | ✅ | ✅ |
| **Correct** | **4/5** | **4/5** |

### Token · cost (Haiku, same run)

| | Baseline | Kevin |
|---|------:|--------:|
| Total tokens | 2,198 | 797 |
| Code tokens | 1,646 | 630 |
| Prose tokens | 509 | 128 |
| Code lines | 167 | 65 |
| Cost (5 tasks) | $0.0027 | $0.0010 |

Kevin cuts tokens across the board — less code written, less narration around it. The prose_tok drop shows what changes: baseline spends hundreds of tokens on "Let me start by examining..." and "I have successfully implemented...". Kevin deletes both.

Reproduce: `ANTHROPIC_API_KEY=... python3 benchmarks/correctness/run.py`

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

**Why does kevin sometimes use more tokens than pure terse alternatives?**

Kevin talk. Short sentences, but real sentences. "Not needed. Add when profiler say so." — that is prose. Pure code-only alternatives output nothing but the function. Kevin chose legible over minimal. If you want absolute minimum output with zero explanation, `/kevin ultra` gets closer.

**How is this different from caveman?**

Caveman output zero prose. Pure code. No structured thinking, no ladder, no decision before write. Kevin check three things before writing anything: is it needed, does it already exist in your codebase, does it need a new file. Caveman just short. Kevin short AND disciplined. Also Kevin talk — "Not needed. Add when profiler say so." Caveman say nothing. Different tool.

**How is this different from ponytail?**

Ponytail has a copy ladder: check stdlib, check installed dep, copy before write. Kevin takes that idea and adds two things ponytail doesn't have. First: check *your specific codebase*, not just universal stdlib. Second: a word ladder that cuts narration, which ponytail doesn't touch. Ponytail is quiet and focused on code minimalism. Kevin is that plus codebase awareness plus a personality.

**Is this open source?**

Yes. MIT. Fork it, rename it, make it Dwight. Kevin not precious about attribution.

## Roadmap

1. **More agent** — Codex, Gemini CLI, Cursor agent mode
2. **Kevin score** — badge showing token saving per session

---

*Kevin not dumb. Kevin efficient.*
