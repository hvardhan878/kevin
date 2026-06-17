# Kevin Benchmark Results

Generated: 2026-06-17 18:35 UTC  
Model: `claude-haiku-4-5-20251001` (correctness) · `claude-sonnet-4-6` (SWE-bench)

---

## Part 1 — Correctness Suite

Five tasks. Four conditions. Automated pass/fail via `node test.js`. Code lines = lines inside ` ``` ` blocks only.

### Binary Search

| Condition | Pass | Tokens | Code tok | Prose tok | Lines | Cost |
|-----------|------|-------:|---------:|----------:|------:|-----:|
| baseline | ✅ | 591 | 337 | 248 | 26 | $0.0007 |
| kevin | ✅ | 238 | 207 | 16 | 14 | $0.0003 |
| caveman | ✅ | 123 | 117 | 0 | 12 | $0.0002 |
| ponytail | ✅ | 116 | 110 | 0 | 10 | $0.0001 |

### Codebase Reuse

| Condition | Pass | Tokens | Code tok | Prose tok | Lines | Cost |
|-----------|------|-------:|---------:|----------:|------:|-----:|
| baseline | ❌ | 305 | 179 | 116 | 14 | $0.0004 |
| kevin | ❌ | 66 | 48 | 12 | 5 | $0.0001 |
| caveman | ✅ | 76 | 71 | 0 | 6 | $0.0001 |
| ponytail | ❌ | 53 | 48 | 0 | 5 | $0.0001 |
> **baseline failed:** reimplemented date formatting instead of reusing formatDate from utils/date.js
> **kevin failed:** reimplemented date formatting instead of reusing formatDate from utils/date.js
> **ponytail failed:** reimplemented date formatting instead of reusing formatDate from utils/date.js

### Debounce

| Condition | Pass | Tokens | Code tok | Prose tok | Lines | Cost |
|-----------|------|-------:|---------:|----------:|------:|-----:|
| baseline | ✅ | 799 | 637 | 145 | 66 | $0.0010 |
| kevin | ✅ | 96 | 57 | 33 | 7 | $0.0001 |
| caveman | ✅ | 75 | 69 | 0 | 8 | $0.0001 |
| ponytail | ✅ | 66 | 60 | 0 | 7 | $0.0001 |

### Pubsub

| Condition | Pass | Tokens | Code tok | Prose tok | Lines | Cost |
|-----------|------|-------:|---------:|----------:|------:|-----:|
| baseline | ✅ | 350 | 345 | 0 | 43 | $0.0004 |
| kevin | ✅ | 217 | 188 | 23 | 22 | $0.0003 |
| caveman | ✅ | 205 | 199 | 0 | 23 | $0.0003 |
| ponytail | ✅ | 202 | 196 | 0 | 23 | $0.0003 |

### Rate Limiter

| Condition | Pass | Tokens | Code tok | Prose tok | Lines | Cost |
|-----------|------|-------:|---------:|----------:|------:|-----:|
| baseline | ✅ | 153 | 148 | 0 | 18 | $0.0002 |
| kevin | ✅ | 180 | 130 | 44 | 17 | $0.0002 |
| caveman | ✅ | 148 | 142 | 0 | 17 | $0.0002 |
| ponytail | ✅ | 176 | 170 | 0 | 19 | $0.0002 |

### Summary (all tasks)

| Condition | Correct | Tokens | vs baseline | Code tok | Prose tok | Lines | Total cost |
|-----------|--------:|-------:|------------:|---------:|----------:|------:|-----------:|
| baseline | 4/5 | 2198 | 100% | 1646 | 509 | 167 | $0.0027 |
| kevin | 4/5 | 797 | 36% | 630 | 128 | 65 | $0.0010 |
| caveman | 5/5 | 627 | 29% | 598 | 0 | 66 | $0.0008 |
| ponytail | 4/5 | 613 | 28% | 584 | 0 | 64 | $0.0008 |

---

## Part 2 — SWE-bench Lite

50 tasks from [princeton-nlp/SWE-bench_Lite](https://github.com/princeton-nlp/SWE-bench). Real GitHub issues. Evaluated with official harness. Seed 42.

_No SWE-bench results found. Run `python3 benchmarks/swe_bench/run.py`._

---

## Why Trust These Numbers?

**Correctness suite is automated.** Each task runs `node test.js` and checks exit code. Pass means the code works. Fail means it doesn't. No manual grading.

**Code lines ≠ prose lines.** Token and line counts measure only what's inside ` ``` ` code blocks. Narration tokens are tracked separately (`prose_tokens`). This lets you see whether a condition cut *code* or just cut *explanation*.

**Codebase-reuse task is kevin-unique.** Baseline, caveman, and ponytail don't know `formatDate` exists in `utils/date.js`. Kevin's ladder step 2 says to grep first. This task specifically measures that behavior.

**SWE-bench uses real issues.** Not synthetic tasks. Real GitHub bugs with real test suites. The official harness (Docker) runs the repo's own tests. We cannot cheat a pass.

**Reproduce it:**
```bash
ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_all.py
# or just the fast suite:
ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_all.py --skip-swe
```

All raw results are in `benchmarks/correctness_results.json` and `benchmarks/swe_bench_results.json`.
