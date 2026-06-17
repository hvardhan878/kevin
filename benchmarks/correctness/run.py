#!/usr/bin/env python3
"""Correctness benchmark suite for kevin.

Runs 5 tasks × 4 conditions (baseline, kevin, caveman, ponytail).
Each task has an automated pass/fail test.
Outputs benchmarks/correctness_results.json and prints a summary table.

Usage:
    ANTHROPIC_API_KEY=sk-... python3 benchmarks/correctness/run.py
"""
from __future__ import annotations

import os
import re
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

try:
    import anthropic
except ImportError:
    sys.exit("anthropic SDK not installed. Run: pip install anthropic")

ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = Path(__file__).parent.parent / "skills"

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

SKILL_KEVIN   = _read(ROOT / "skills" / "kevin" / "SKILL.md")
SKILL_CAVEMAN = _read(SKILLS_DIR / "caveman.md")
SKILL_PONYTAIL = _read(SKILLS_DIR / "ponytail.md")

CONDITIONS: dict[str, Optional[str]] = {
    "baseline": None,
    "kevin":    SKILL_KEVIN,
    "caveman":  SKILL_CAVEMAN,
    "ponytail": SKILL_PONYTAIL,
}

MODEL = "claude-haiku-4-5-20251001"
# Haiku output price per token (as of 2025)
PRICE_PER_OUTPUT_TOKEN = 1.25 / 1_000_000

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


# ── API helper ────────────────────────────────────────────────────────────────

def call_claude(system: Optional[str], prompt: str) -> dict:
    kwargs: dict = dict(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system

    t0 = time.time()
    resp = client.messages.create(**kwargs)
    elapsed = time.time() - t0

    text = resp.content[0].text
    out_tokens = resp.usage.output_tokens
    in_tokens  = resp.usage.input_tokens

    # Separate code blocks from prose
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    code_text   = "\n".join(code_blocks)
    prose_text  = re.sub(r"```(?:\w+)?\n.*?```", "", text, flags=re.DOTALL).strip()

    # Approximate token split by character ratio
    total_chars = max(len(text), 1)
    code_ratio  = len(code_text) / total_chars
    prose_ratio = len(prose_text) / total_chars

    code_lines = len([l for l in code_text.splitlines() if l.strip()])

    return {
        "text":          text,
        "code":          code_text,
        "prose":         prose_text,
        "output_tokens": out_tokens,
        "input_tokens":  in_tokens,
        "code_tokens":   round(out_tokens * code_ratio),
        "prose_tokens":  round(out_tokens * prose_ratio),
        "code_lines":    code_lines,
        "time_s":        round(elapsed, 2),
        "cost_usd":      round(out_tokens * PRICE_PER_OUTPUT_TOKEN, 6),
    }


# ── Test runner helpers ───────────────────────────────────────────────────────

def _sanitize(code: str) -> str:
    """Clean generated code for safe injection into a CommonJS Node.js test file."""
    lines = []
    skip_block = False
    brace_depth = 0

    for line in code.splitlines():
        stripped = line.strip()

        # Skip local-file require/import (would fail in temp dir)
        if re.search(r"""require\s*\(\s*['"]\.{1,2}/""", stripped):
            continue
        if re.search(r"""from\s+['"]\.{1,2}/""", stripped) and stripped.startswith("import"):
            continue

        # Strip ESM export statements (ponytail/baseline may use them)
        if re.match(r"^export\s+(default|const|class|function|let|var|\{)", stripped):
            # Convert "export default X" → nothing, "export class X" → "class X"
            if re.match(r"^export\s+default\s+", stripped):
                continue
            line = re.sub(r"^export\s+", "", line)

        # Skip test-framework blocks (describe/it/test) that lack a runtime
        if re.match(r"^(describe|it|test)\s*\(", stripped):
            skip_block = True
            brace_depth = 0

        if skip_block:
            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth <= 0 and "{" in stripped:
                skip_block = False
            continue

        # Strip top-level await (demo usage code) — only if not inside a function
        if re.match(r"^await\s+", stripped):
            continue

        lines.append(line)

    # Remove duplicate top-level const/let/var declarations (model adds example usage)
    seen_vars: set[str] = set()
    deduped = []
    for line in lines:
        m = re.match(r"^(const|let|var)\s+(\w+)\s*=", line.strip())
        if m:
            name = m.group(2)
            if name in seen_vars:
                continue
            seen_vars.add(name)
        deduped.append(line)

    return "\n".join(deduped)

def run_node(generated_code: str, test_template: str, timeout: int = 12) -> tuple[bool, str]:
    """Inject generated code into test template, run with node, return (passed, msg)."""
    full = test_template.replace("__GENERATED_CODE__", _sanitize(generated_code))
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False, encoding="utf-8") as f:
        f.write(full)
        tmp = f.name
    try:
        r = subprocess.run(
            ["node", tmp], capture_output=True, text=True, timeout=timeout
        )
        out = (r.stdout + r.stderr).strip()
        return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except FileNotFoundError:
        return False, "node not found — install Node.js 18+"
    finally:
        os.unlink(tmp)


# ── Task 1: Debounce ──────────────────────────────────────────────────────────

DEBOUNCE_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals.
Implement debounce(fn, delayMs). When called repeatedly within delayMs, execute fn only once — after delayMs have passed since the last call.\
"""

DEBOUNCE_TEST = """\
// ── generated code ──
__GENERATED_CODE__
// ── end generated ──

const assert = require('assert');

function getDebounce() {
    if (typeof debounce !== 'undefined') return debounce;
    if (typeof module !== 'undefined' && module.exports) {
        const e = module.exports;
        if (typeof e === 'function') return e;
        if (e.debounce) return e.debounce;
    }
    return null;
}

async function main() {
    const fn = getDebounce();
    if (!fn) { console.error('debounce not found in scope or exports'); process.exit(1); }

    // Test 1: does not call immediately
    let count = 0;
    const inc = () => count++;
    const d = fn(inc, 60);
    d(); d(); d();
    assert.strictEqual(count, 0, 'should not call immediately');

    // Test 2: calls exactly once after delay
    await new Promise(r => setTimeout(r, 130));
    assert.strictEqual(count, 1, `expected 1 call after delay, got ${count}`);

    // Test 3: resets correctly
    count = 0;
    d();
    await new Promise(r => setTimeout(r, 130));
    assert.strictEqual(count, 1, `single delayed call failed, got ${count}`);

    // Test 4: rapid calls only fire once each burst
    count = 0;
    d(); d(); d();
    await new Promise(r => setTimeout(r, 130));
    assert.strictEqual(count, 1, `burst should fire once, got ${count}`);

    console.log('PASS');
}
main().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
"""


# ── Task 2: Rate limiter ──────────────────────────────────────────────────────

RATELIMITER_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals. CommonJS only (no ES modules, no export default).
Write one implementation only. Do not provide alternatives. No example usage code.
Implement a rate limiter that allows at most N requests per time window (ms).
Requests beyond the limit must return false (do not throw, do not queue).
Export or declare in global scope: RateLimiter class, or createRateLimiter(limit, windowMs) function.
The allow/check method must return a boolean.\
"""

RATELIMITER_TEST = """\
// ── generated code ──
__GENERATED_CODE__
// ── end generated ──

const assert = require('assert');

function getRateLimiter(limit, windowMs) {
    if (typeof RateLimiter !== 'undefined')       return new RateLimiter(limit, windowMs);
    if (typeof createRateLimiter !== 'undefined') return createRateLimiter(limit, windowMs);
    if (typeof rateLimiter !== 'undefined')       return rateLimiter(limit, windowMs);
    if (typeof module !== 'undefined' && module.exports) {
        const e = module.exports;
        if (e.RateLimiter)       return new e.RateLimiter(limit, windowMs);
        if (e.createRateLimiter) return e.createRateLimiter(limit, windowMs);
        if (typeof e === 'function') {
            try { return new e(limit, windowMs); } catch(_) {}
        }
    }
    return null;
}

function tryAllow(rl) {
    // Try common method names in order of likelihood
    for (const name of ['allow','request','check','consume','tryAcquire','hit','throttle','isAllowed','acquire','take']) {
        if (typeof rl[name] === 'function') return rl[name]();
    }
    // Maybe rl itself is the callable
    if (typeof rl === 'function') return rl();
    return null;
}

async function main() {
    const rl = getRateLimiter(3, 100);
    if (!rl) { console.error('RateLimiter not found — expected global RateLimiter class or createRateLimiter fn'); process.exit(1); }

    // First 3 should be accepted
    const r1 = tryAllow(rl);
    const r2 = tryAllow(rl);
    const r3 = tryAllow(rl);
    if (!r1 || !r2 || !r3) { console.error(`First 3 requests should pass, got ${r1} ${r2} ${r3}`); process.exit(1); }

    // 4th within window should be rejected
    const r4 = tryAllow(rl);
    if (r4) { console.error('4th request within window should be rejected'); process.exit(1); }

    // After window resets, should allow again
    await new Promise(r => setTimeout(r, 150));
    const r5 = tryAllow(rl);
    if (!r5) { console.error('Request after window expiry should pass'); process.exit(1); }

    // Burst test: 3 more in new window
    const r6 = tryAllow(rl);
    const r7 = tryAllow(rl);
    if (!r6 || !r7) { console.error('Burst after window failed'); process.exit(1); }
    const r8 = tryAllow(rl);
    if (r8) { console.error('Exceeded limit in new window should reject'); process.exit(1); }

    console.log('PASS');
}
main().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
"""


# ── Task 3: Codebase reuse ────────────────────────────────────────────────────

CODEBASE_REUSE_PROMPT = """\
You are working in a Node.js project. The file utils/date.js already exists:

```javascript
// utils/date.js
function formatDate(date, format = 'YYYY-MM-DD') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day   = String(d.getDate()).padStart(2, '0');
    return format.replace('YYYY', year).replace('MM', month).replace('DD', day);
}
module.exports = { formatDate };
```

Task: add a function to the user-profile module that formats a user's lastLoginAt (Unix ms timestamp) for display. Write only the new function — do not rewrite utils/date.js.\
"""

def run_codebase_reuse_test(generated_code: str) -> tuple[bool, str]:
    """Pass: reuses formatDate. Fail: re-implements date logic."""
    low = generated_code.lower()
    full_text = generated_code

    reuses = any([
        "formatdate(" in low,
        ("require" in low or "import" in low) and "date" in low,
        "utils/date" in low,
        "../utils/date" in low or "./utils/date" in low,
    ])

    reimplements = any([
        bool(re.search(r"\bgetfullyear\b|\bgetmonth\b|\bgetdate\b", low))
        and "formatdate" not in low,
        bool(re.search(
            r"(tolocaledate|tolocalestring|todatestring|toisostring)\(",
            low
        )) and "formatdate" not in low,
        bool(re.search(r"function\s+format(?!Date)", full_text, re.IGNORECASE)),
        bool(re.search(r"const\s+format(?!Date)", full_text, re.IGNORECASE)),
        bool(re.search(r"new Intl\.DateTimeFormat", full_text)),
    ])

    if reimplements:
        return False, "reimplemented date formatting instead of reusing formatDate from utils/date.js"
    if reuses:
        return True, "correctly reused formatDate from utils/date.js"
    return False, "neither reused nor reimplemented — ambiguous output; check manually"


# ── Task 4: Pub/sub ───────────────────────────────────────────────────────────

PUBSUB_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals. CommonJS only (module.exports, no export default, no ES module syntax).
No example usage. No test framework (no describe/it/test). Implementation only.
Implement an in-memory pub/sub system with three methods:
- subscribe(event, callback)
- publish(event, data)
- unsubscribe(event, callback)

Requirements:
- Multiple subscribers per event
- Memory-leak safe (clean up empty listener arrays)
- No error when unsubscribing a non-existent handler
- No error when publishing to event with no subscribers
- Data is passed to callbacks as the first argument

Export as class (EventBus / PubSub) or factory function (createPubSub / createEventBus) via module.exports.\
"""

PUBSUB_TEST = """\
// ── generated code ──
__GENERATED_CODE__
// ── end generated ──

const assert = require('assert');

function getPS() {
    if (typeof EventBus       !== 'undefined') return typeof EventBus === 'function' ? new EventBus() : EventBus;
    if (typeof PubSub         !== 'undefined') return typeof PubSub   === 'function' ? new PubSub()   : PubSub;
    if (typeof createPubSub   !== 'undefined') return createPubSub();
    if (typeof createEventBus !== 'undefined') return createEventBus();
    if (typeof module !== 'undefined' && module.exports) {
        const e = module.exports;
        // module.exports = function factory() { return {subscribe,publish,unsubscribe} }
        if (typeof e === 'function') {
            try {
                const inst = e();
                if (inst && inst.subscribe && inst.publish) return inst;
            } catch(_) {}
            try {
                const inst = new e();
                if (inst && inst.subscribe && inst.publish) return inst;
            } catch(_) {}
        }
        if (e.EventBus)       return typeof e.EventBus === 'function' ? new e.EventBus() : e.EventBus;
        if (e.PubSub)         return typeof e.PubSub   === 'function' ? new e.PubSub()   : e.PubSub;
        if (e.createPubSub)   return e.createPubSub();
        if (e.createEventBus) return e.createEventBus();
        if (e.subscribe && e.publish && e.unsubscribe) return e;
    }
    return null;
}

async function main() {
    const ps = getPS();
    if (!ps) { console.error('pub/sub not found — expected EventBus class or createPubSub fn'); process.exit(1); }

    const sub   = (e, cb) => { const m = ps.subscribe || ps.on; m.call(ps, e, cb); };
    const pub   = (e, d)  => { const m = ps.publish   || ps.emit; m.call(ps, e, d); };
    const unsub = (e, cb) => { const m = ps.unsubscribe || ps.off; m.call(ps, e, cb); };

    // 1. Basic subscribe + publish
    let r1 = null;
    sub('test', d => r1 = d);
    pub('test', 'hello');
    assert.strictEqual(r1, 'hello', 'basic publish failed');

    // 2. Multiple subscribers same event
    let r2a = null, r2b = null;
    sub('multi', d => r2a = d);
    sub('multi', d => r2b = d);
    pub('multi', 42);
    assert.strictEqual(r2a, 42, 'multi-sub a failed');
    assert.strictEqual(r2b, 42, 'multi-sub b failed');

    // 3. Unsubscribe stops callback
    let r3 = 0;
    const cb3 = () => r3++;
    sub('unsub', cb3);
    pub('unsub', null);
    assert.strictEqual(r3, 1, 'first pub before unsub failed');
    unsub('unsub', cb3);
    pub('unsub', null);
    assert.strictEqual(r3, 1, 'unsubscribe did not stop callback');

    // 4. Unsubscribe non-existent — no error
    try { unsub('ghost', () => {}); } catch(e) { console.error('unsub non-existent threw:', e.message); process.exit(1); }

    // 5. Publish no subscribers — no error
    try { pub('empty', 'data'); } catch(e) { console.error('pub no subscribers threw:', e.message); process.exit(1); }

    // 6. Data shape preserved
    let r6 = null;
    sub('obj', d => r6 = d);
    pub('obj', { x: 1, y: [2, 3] });
    assert.deepStrictEqual(r6, { x: 1, y: [2, 3] }, 'data shape not preserved');

    // 7. Events are isolated
    let r7 = false;
    sub('a', () => r7 = true);
    pub('b', null);
    assert.strictEqual(r7, false, 'event isolation failed');

    // 8. Multiple event types
    const log: string[] = [];
    sub('x', () => log.push('x'));
    sub('y', () => log.push('y'));
    pub('x', null); pub('y', null);
    assert.deepStrictEqual(log, ['x', 'y'], 'multiple event types failed');

    // 9. Double unsubscribe — no error, correct count
    let r9 = 0;
    const cb9 = () => r9++;
    sub('dup', cb9);
    unsub('dup', cb9);
    try { unsub('dup', cb9); } catch(e) { console.error('double unsub threw:', e.message); process.exit(1); }
    pub('dup', null);
    assert.strictEqual(r9, 0, 'double unsub: callback still fired');

    // 10. Pub after all subs removed — no error
    try {
        const cb10 = () => {};
        sub('last', cb10);
        unsub('last', cb10);
        pub('last', 'x');
    } catch(e) { console.error('pub after all unsub threw:', e.message); process.exit(1); }

    console.log('PASS (10/10)');
}

// The test file uses TypeScript-style array annotation for type checking clarity.
// Node.js will fail on that. Remove it:
// Actually let's keep it compatible - remove the type annotation below.
main().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
"""

# Fix: remove TypeScript syntax from test
PUBSUB_TEST = PUBSUB_TEST.replace("const log: string[] = [];", "const log = [];")


# ── Task 5: Binary search ─────────────────────────────────────────────────────

BINARYSEARCH_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals.
Implement binarySearch(arr, target) that searches a sorted array of numbers and returns the index of target, or -1 if not found.\
"""

BINARYSEARCH_TEST = """\
// ── generated code ──
__GENERATED_CODE__
// ── end generated ──

const assert = require('assert');

function getBS() {
    if (typeof binarySearch !== 'undefined') return binarySearch;
    if (typeof module !== 'undefined' && module.exports) {
        const e = module.exports;
        if (typeof e === 'function') return e;
        if (e.binarySearch) return e.binarySearch;
    }
    return null;
}

function main() {
    const bs = getBS();
    if (!bs) { console.error('binarySearch not found'); process.exit(1); }

    assert.strictEqual(bs([1,3,5,7,9], 5),  2, 'find middle');
    assert.strictEqual(bs([1,3,5,7,9], 1),  0, 'find first');
    assert.strictEqual(bs([1,3,5,7,9], 9),  4, 'find last');
    assert.strictEqual(bs([1,3,5,7,9], 4), -1, 'not found');
    assert.strictEqual(bs([], 1),           -1, 'empty array');
    assert.strictEqual(bs([42], 42),         0, 'single element found');
    assert.strictEqual(bs([42], 1),         -1, 'single element not found');
    assert.strictEqual(bs([1,2,3,4,5,6,7,8,9,10], 10), 9, 'find last even-length');
    assert.strictEqual(bs([1,2,3,4,5,6,7,8,9,10], 1),  0, 'find first even-length');
    assert.strictEqual(bs([-5,-2,0,3,7], -2), 1, 'negative numbers');

    console.log('PASS');
}
main();
"""


# ── Task registry ─────────────────────────────────────────────────────────────

TASKS = {
    "debounce": {
        "prompt":   DEBOUNCE_PROMPT,
        "test_fn":  lambda code: run_node(code, DEBOUNCE_TEST),
        "category": "behavior",
    },
    "rate_limiter": {
        "prompt":   RATELIMITER_PROMPT,
        "test_fn":  lambda code: run_node(code, RATELIMITER_TEST),
        "category": "behavior",
    },
    "codebase_reuse": {
        "prompt":   CODEBASE_REUSE_PROMPT,
        "test_fn":  run_codebase_reuse_test,
        "category": "kevin_unique",
    },
    "pubsub": {
        "prompt":   PUBSUB_PROMPT,
        "test_fn":  lambda code: run_node(code, PUBSUB_TEST),
        "category": "behavior",
    },
    "binary_search": {
        "prompt":       BINARYSEARCH_PROMPT,
        "test_fn":      lambda code: run_node(code, BINARYSEARCH_TEST),
        "category":     "correctness_plus_tokens",
    },
}


# ── Main runner ───────────────────────────────────────────────────────────────

def run_task(task_name: str, condition: str, system: Optional[str]) -> dict:
    task = TASKS[task_name]
    print(f"  [{condition:10}] {task_name} ...", end=" ", flush=True)

    result = call_claude(system, task["prompt"])
    code   = result["code"] or result["text"]  # fall back to full text if no code block

    passed, msg = task["test_fn"](code)
    status = "PASS" if passed else "FAIL"
    print(status if passed else f"FAIL — {msg[:60]}")

    return {
        "condition":     condition,
        "task":          task_name,
        "category":      task["category"],
        "passed":        passed,
        "fail_reason":   None if passed else msg,
        "output_tokens": result["output_tokens"],
        "input_tokens":  result["input_tokens"],
        "code_tokens":   result["code_tokens"],
        "prose_tokens":  result["prose_tokens"],
        "code_lines":    result["code_lines"],
        "time_s":        result["time_s"],
        "cost_usd":      result["cost_usd"],
    }


def print_table(results: list[dict]) -> None:
    from collections import defaultdict

    # Aggregate by condition
    cond_stats: dict[str, dict] = defaultdict(lambda: {
        "pass": 0, "fail": 0, "tokens": 0, "cost": 0.0,
        "code_tokens": 0, "prose_tokens": 0, "lines": 0,
    })
    for r in results:
        s = cond_stats[r["condition"]]
        s["pass" if r["passed"] else "fail"] += 1
        s["tokens"]       += r["output_tokens"]
        s["cost"]         += r["cost_usd"]
        s["code_tokens"]  += r["code_tokens"]
        s["prose_tokens"] += r["prose_tokens"]
        s["lines"]        += r["code_lines"]

    baseline_tokens = cond_stats["baseline"]["tokens"] or 1

    print("\n" + "="*72)
    print(f"{'Condition':<12} {'Pass':>4} {'Fail':>4} {'Tokens':>7} {'vs base':>7} "
          f"{'CodeTok':>8} {'ProseTok':>9} {'Lines':>6} {'Cost':>8}")
    print("-"*72)
    for cond in CONDITIONS:
        s = cond_stats[cond]
        pct = f"{(s['tokens'] / baseline_tokens) * 100:.0f}%"
        print(f"{cond:<12} {s['pass']:>4} {s['fail']:>4} {s['tokens']:>7} {pct:>7} "
              f"{s['code_tokens']:>8} {s['prose_tokens']:>9} {s['lines']:>6} "
              f"${s['cost']:.4f}")
    print("="*72)
    print("\nNote: code lines = lines inside ``` blocks only. Prose lines excluded.")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY before running.")

    results = []
    for task_name in TASKS:
        print(f"\nTask: {task_name}")
        for condition, system in CONDITIONS.items():
            r = run_task(task_name, condition, system)
            results.append(r)

    out_path = ROOT / "benchmarks" / "correctness_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults saved to {out_path}")

    print_table(results)

    # Fail count
    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for r in failed:
            print(f"  {r['condition']:10} {r['task']:20} — {r['fail_reason']}")
    else:
        print("\nAll tests passed.")


if __name__ == "__main__":
    main()
