#!/usr/bin/env python3
"""Correctness benchmark suite for kevin.

Methodology
-----------
4 conditions × 8 tasks × 3 runs = 96 API calls.

Conditions
  agent_baseline  — realistic coding-agent prompt (no verbosity directive)
  be_brief        — "be concise, code only" (7-word ablation)
  yagni           — YAGNI + one-liners (the prompt that beats ponytail)
  kevin           — full SKILL.md

Tasks
  Runtime correctness (Node.js, exit code 0 = pass):
    debounce, rate_limiter, pubsub, binary_search, simplest_correct

  Judgment (automated heuristic pass/fail):
    codebase_reuse  — reuse formatDate or reimplement?
    yagni_pushback  — refuse premature caching or implement it?
    inline_vs_file  — inline function or create new file?

Metrics per condition (median of 3 runs)
  pass_rate, output_tokens, code_tokens, prose_tokens, code_lines, cost_usd

Usage
    ANTHROPIC_API_KEY=sk-... python3 benchmarks/correctness/run.py [--runs 3] [--tasks all]
"""
from __future__ import annotations

import os
import re
import sys
import json
import time
import statistics
import tempfile
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Callable
from collections import defaultdict

try:
    import anthropic
except ImportError:
    sys.exit("anthropic SDK not installed. Run: pip install anthropic")

ROOT       = Path(__file__).parent.parent.parent
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Conditions ────────────────────────────────────────────────────────────────

AGENT_BASELINE = (
    "You are a coding assistant. Write working code. "
    "Provide one implementation. Be direct."
)

BE_BRIEF = "Be concise. Code only. No explanation."

YAGNI = "Follow YAGNI principles, and prefer one-liner solutions."

CONDITIONS: dict[str, Optional[str]] = {
    "agent_baseline": AGENT_BASELINE,
    "be_brief":       BE_BRIEF,
    "yagni":          YAGNI,
    "kevin":          _read(ROOT / "skills" / "kevin" / "SKILL.md"),
}

MODEL = "claude-haiku-4-5-20251001"
PRICE_INPUT  = 0.80  / 1_000_000   # Haiku input  $/token
PRICE_OUTPUT = 4.00  / 1_000_000   # Haiku output $/token

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

    t0   = time.time()
    resp = client.messages.create(**kwargs)
    elapsed = time.time() - t0

    text = resp.content[0].text
    out_tokens = resp.usage.output_tokens
    in_tokens  = resp.usage.input_tokens

    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    code_text   = "\n".join(code_blocks)
    prose_text  = re.sub(r"```(?:\w+)?\n.*?```", "", text, flags=re.DOTALL).strip()

    total_chars = max(len(text), 1)
    code_ratio  = len(code_text) / total_chars
    prose_ratio = len(prose_text) / total_chars
    code_lines  = len([l for l in code_text.splitlines() if l.strip()])

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
        "cost_usd":      round(
            out_tokens * PRICE_OUTPUT + in_tokens * PRICE_INPUT, 6
        ),
    }


# ── Test runner helpers ───────────────────────────────────────────────────────

def _sanitize(code: str) -> str:
    lines      = []
    skip_block = False
    brace_depth = 0

    for line in code.splitlines():
        stripped = line.strip()

        if re.search(r"""require\s*\(\s*['"]\.{1,2}/""", stripped):
            continue
        if re.search(r"""from\s+['"]\.{1,2}/""", stripped) and stripped.startswith("import"):
            continue

        if re.match(r"^export\s+(default|const|class|function|let|var|\{)", stripped):
            if re.match(r"^export\s+default\s+", stripped):
                continue
            line = re.sub(r"^export\s+", "", line)

        if re.match(r"^(describe|it|test)\s*\(", stripped):
            skip_block  = True
            brace_depth = 0

        if skip_block:
            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth <= 0 and "{" in stripped:
                skip_block = False
            continue

        if re.match(r"^await\s+", stripped):
            continue

        lines.append(line)

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
    full = test_template.replace("__GENERATED_CODE__", _sanitize(generated_code))
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False, encoding="utf-8") as f:
        f.write(full)
        tmp = f.name
    try:
        r   = subprocess.run(["node", tmp], capture_output=True, text=True, timeout=timeout)
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
    if (!fn) { console.error('debounce not found'); process.exit(1); }

    let count = 0;
    const inc = () => count++;
    const d = fn(inc, 60);
    d(); d(); d();
    if (count !== 0) { console.error('should not call immediately'); process.exit(1); }

    await new Promise(r => setTimeout(r, 130));
    if (count !== 1) { console.error(`expected 1 call, got ${count}`); process.exit(1); }

    count = 0;
    d();
    await new Promise(r => setTimeout(r, 130));
    if (count !== 1) { console.error(`single delayed call failed, got ${count}`); process.exit(1); }

    count = 0;
    d(); d(); d();
    await new Promise(r => setTimeout(r, 130));
    if (count !== 1) { console.error(`burst should fire once, got ${count}`); process.exit(1); }

    console.log('PASS');
}
main().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
"""


# ── Task 2: Rate limiter ──────────────────────────────────────────────────────

RATELIMITER_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals. CommonJS only (no ES modules, no export default).
Write one implementation only. No example usage code.
Implement a rate limiter that allows at most N requests per time window (ms).
Requests beyond the limit must return false (do not throw, do not queue).
Export or declare in global scope: RateLimiter class, or createRateLimiter(limit, windowMs) function.\
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
    for (const name of ['allow','request','check','consume','tryAcquire','hit','throttle','isAllowed','acquire','take']) {
        if (typeof rl[name] === 'function') return rl[name]();
    }
    if (typeof rl === 'function') return rl();
    return null;
}

async function main() {
    const rl = getRateLimiter(3, 100);
    if (!rl) { console.error('RateLimiter not found'); process.exit(1); }

    const r1 = tryAllow(rl), r2 = tryAllow(rl), r3 = tryAllow(rl);
    if (!r1 || !r2 || !r3) { console.error(`First 3 should pass: ${r1} ${r2} ${r3}`); process.exit(1); }

    const r4 = tryAllow(rl);
    if (r4) { console.error('4th within window should be rejected'); process.exit(1); }

    await new Promise(r => setTimeout(r, 150));
    const r5 = tryAllow(rl);
    if (!r5) { console.error('After window expiry should pass'); process.exit(1); }

    const r6 = tryAllow(rl), r7 = tryAllow(rl);
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
    low = generated_code.lower()
    reuses = any([
        "formatdate(" in low,
        ("require" in low or "import" in low) and "date" in low,
        "utils/date" in low,
    ])
    reimplements = any([
        bool(re.search(r"\bgetfullyear\b|\bgetmonth\b|\bgetdate\b", low)) and "formatdate" not in low,
        bool(re.search(r"(tolocaledate|tolocalestring|todatestring|toisostring)\(", low)) and "formatdate" not in low,
        bool(re.search(r"function\s+format(?!Date)", generated_code, re.IGNORECASE)),
        bool(re.search(r"const\s+format(?!Date)", generated_code, re.IGNORECASE)),
        bool(re.search(r"new Intl\.DateTimeFormat", generated_code)),
    ])
    if reimplements:
        return False, "reimplemented date formatting instead of reusing formatDate"
    if reuses:
        return True, "correctly reused formatDate from utils/date.js"
    return False, "ambiguous — neither reused nor reimplemented"


# ── Task 4: Pub/sub ───────────────────────────────────────────────────────────

PUBSUB_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals. CommonJS only (module.exports, no export default, no ES module syntax).
No example usage. No test framework (no describe/it/test). Implementation only.
Implement an in-memory pub/sub system with three methods:
- subscribe(event, callback)
- publish(event, data)
- unsubscribe(event, callback)

Requirements: multiple subscribers per event, memory-leak safe, no error on unsubscribing a non-existent handler, no error publishing to event with no subscribers, data passed to callback as first argument.
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
        if (typeof e === 'function') {
            try { const i = e(); if (i && i.subscribe && i.publish) return i; } catch(_) {}
            try { const i = new e(); if (i && i.subscribe && i.publish) return i; } catch(_) {}
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
    if (!ps) { console.error('pub/sub not found'); process.exit(1); }

    const sub   = (e, cb) => { const m = ps.subscribe || ps.on;          m.call(ps, e, cb); };
    const pub   = (e, d)  => { const m = ps.publish   || ps.emit;        m.call(ps, e, d); };
    const unsub = (e, cb) => { const m = ps.unsubscribe || ps.off;       m.call(ps, e, cb); };

    let r1 = null;
    sub('test', d => r1 = d);
    pub('test', 'hello');
    assert.strictEqual(r1, 'hello', 'basic publish failed');

    let r2a = null, r2b = null;
    sub('multi', d => r2a = d);
    sub('multi', d => r2b = d);
    pub('multi', 42);
    assert.strictEqual(r2a, 42, 'multi-sub a'); assert.strictEqual(r2b, 42, 'multi-sub b');

    let r3 = 0;
    const cb3 = () => r3++;
    sub('unsub', cb3); pub('unsub', null);
    assert.strictEqual(r3, 1, 'first pub');
    unsub('unsub', cb3); pub('unsub', null);
    assert.strictEqual(r3, 1, 'unsub stopped');

    try { unsub('ghost', () => {}); } catch(e) { console.error('unsub non-existent threw:', e.message); process.exit(1); }
    try { pub('empty', 'data'); }    catch(e) { console.error('pub no subscribers threw:', e.message); process.exit(1); }

    let r6 = null;
    sub('obj', d => r6 = d);
    pub('obj', { x: 1, y: [2, 3] });
    assert.deepStrictEqual(r6, { x: 1, y: [2, 3] }, 'data shape');

    let r7 = false;
    sub('a', () => r7 = true); pub('b', null);
    assert.strictEqual(r7, false, 'event isolation');

    const log = [];
    sub('x', () => log.push('x')); sub('y', () => log.push('y'));
    pub('x', null); pub('y', null);
    assert.deepStrictEqual(log, ['x', 'y'], 'multiple events');

    let r9 = 0;
    const cb9 = () => r9++;
    sub('dup', cb9); unsub('dup', cb9);
    try { unsub('dup', cb9); } catch(e) { console.error('double unsub threw:', e.message); process.exit(1); }
    pub('dup', null);
    assert.strictEqual(r9, 0, 'double unsub still fired');

    try { const cb10 = () => {}; sub('last', cb10); unsub('last', cb10); pub('last', 'x'); }
    catch(e) { console.error('pub after all unsub threw:', e.message); process.exit(1); }

    console.log('PASS (10/10)');
}
main().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
"""


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
    assert.strictEqual(bs([42], 42),         0, 'single found');
    assert.strictEqual(bs([42], 1),         -1, 'single not found');
    assert.strictEqual(bs([1,2,3,4,5,6,7,8,9,10], 10), 9, 'last even-length');
    assert.strictEqual(bs([1,2,3,4,5,6,7,8,9,10], 1),  0, 'first even-length');
    assert.strictEqual(bs([-5,-2,0,3,7], -2), 1, 'negatives');
    console.log('PASS');
}
main();
"""


# ── Task 6: YAGNI pushback ────────────────────────────────────────────────────
# Tests Code Ladder rung 1: "Need exist? No → skip."
# Kevin and YAGNI should push back; agent_baseline and be_brief should not.

YAGNI_PUSHBACK_PROMPT = """\
Our Node.js API has 5 user endpoints: getUser, updateUser, listUsers, deleteUser, searchUsers.
Add Redis caching to all of them — we want to be ready for scale.\
"""

PUSHBACK_KEYWORDS = [
    "premature", "not needed", "not necessary", "add when", "wait until",
    "profile first", "profiler", "measure", "yagni", "overkill",
    "only if", "only when", "unnecessary", "over-engineer", "don't need",
    "avoid", "defer", "skip", "not yet", "without evidence",
]

def run_yagni_pushback_test(generated_code: str) -> tuple[bool, str]:
    """Pass: model pushed back (short + contains pushback language). Fail: implemented Redis."""
    full_text = generated_code.lower()

    has_pushback = any(kw in full_text for kw in PUSHBACK_KEYWORDS)
    # Redis implementation signals: createClient, ioredis, redis.get, redis.set, EXPIRE, TTL
    has_implementation = bool(re.search(
        r"createclient|ioredis|redis\.get|redis\.set|redis\.del|\.expire|\.ttl|redisclient|"
        r"import.*redis|require.*redis",
        full_text,
    ))

    if has_implementation and not has_pushback:
        return False, "implemented Redis without questioning the requirement"
    if has_pushback:
        return True, "pushed back on premature optimization"
    # Short response without pushback keywords can still indicate refusal
    if len(generated_code.split()) < 60 and not has_implementation:
        return True, "short non-implementation (implicit refusal)"
    return False, "neither pushed back nor implemented cleanly — ambiguous"


# ── Task 7: Inline vs new file ────────────────────────────────────────────────
# Tests File Ladder: inline a function rather than creating a new file.

INLINE_VS_FILE_PROMPT = """\
Node.js project. The user.js module handles registration. Add email format validation — verify that the string contains '@' and a dot in the domain — before saving a new user. Write only the validation logic.\
"""

def run_inline_vs_file_test(generated_code: str) -> tuple[bool, str]:
    """Pass: short inline check. Fail: new class or suggests creating a new file."""
    full_text = generated_code

    creates_class = bool(re.search(
        r"class\s+Email|class\s+Validator|EmailValidator|class\s+\w*[Vv]alid",
        full_text,
    ))
    suggests_new_file = bool(re.search(
        r"(create|new|save)\s+(a\s+)?file|validators?\.(js|ts)|helpers?\.(js|ts)|utils?\.(js|ts)",
        full_text, re.IGNORECASE,
    ))
    has_file_header = bool(re.search(
        r"//\s*(email|validate|validator|helper).*\.(js|ts)",
        full_text, re.IGNORECASE,
    ))
    # Code inside a code block
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", full_text, re.DOTALL)
    code_text   = "\n".join(code_blocks) or full_text
    code_lines  = [l for l in code_text.splitlines() if l.strip()]

    if creates_class or suggests_new_file or has_file_header:
        return False, "created EmailValidator class or suggested new file"
    if len(code_lines) <= 10:
        return True, "short inline validation check"
    if len(code_lines) <= 20 and not creates_class:
        return True, "reasonable inline implementation"
    return False, f"too long ({len(code_lines)} lines) — likely over-engineered"


# ── Task 8: Simplest correct solution ────────────────────────────────────────
# Runtime correctness + token efficiency. One-liner is the right answer.

SIMPLEST_PROMPT = """\
Environment: Node.js 18. No DOM. No browser globals.
Implement sumArray(arr) that returns the sum of an array of numbers.\
"""

SIMPLEST_TEST = """\
// ── generated code ──
__GENERATED_CODE__
// ── end generated ──

const assert = require('assert');

function getSumArray() {
    if (typeof sumArray !== 'undefined') return sumArray;
    if (typeof module !== 'undefined' && module.exports) {
        const e = module.exports;
        if (typeof e === 'function') return e;
        if (e.sumArray) return e.sumArray;
    }
    return null;
}

function main() {
    const sum = getSumArray();
    if (!sum) { console.error('sumArray not found'); process.exit(1); }

    assert.strictEqual(sum([1, 2, 3]),       6,  '[1,2,3]');
    assert.strictEqual(sum([]),              0,  'empty');
    assert.strictEqual(sum([-1, 1]),         0,  '[-1,1]');
    assert.strictEqual(sum([42]),            42, '[42]');
    assert.strictEqual(sum([10, 20, 30]),    60, '[10,20,30]');
    assert.strictEqual(sum([0.1, 0.2]),      assert.ok(Math.abs(sum([0.1, 0.2]) - 0.3) < 0.001) || 0.30000000000000004, 'float ok');
    console.log('PASS');
}
main();
"""

# Simpler test that avoids the float assertion trick
SIMPLEST_TEST = """\
// ── generated code ──
__GENERATED_CODE__
// ── end generated ──

const assert = require('assert');

function getSumArray() {
    if (typeof sumArray !== 'undefined') return sumArray;
    if (typeof module !== 'undefined' && module.exports) {
        const e = module.exports;
        if (typeof e === 'function') return e;
        if (e.sumArray) return e.sumArray;
    }
    return null;
}

function main() {
    const sum = getSumArray();
    if (!sum) { console.error('sumArray not found'); process.exit(1); }

    assert.strictEqual(sum([1, 2, 3]),    6,  '[1,2,3]');
    assert.strictEqual(sum([]),           0,  'empty');
    assert.strictEqual(sum([-1, 1]),      0,  '[-1,1]');
    assert.strictEqual(sum([42]),        42,  '[42]');
    assert.strictEqual(sum([10, 20, 30]),60,  '[10,20,30]');
    console.log('PASS');
}
main();
"""


# ── Task registry ─────────────────────────────────────────────────────────────

TestFn = Callable[[str], tuple[bool, str]]

TASKS: dict[str, dict] = {
    "debounce": {
        "prompt":   DEBOUNCE_PROMPT,
        "test_fn":  lambda code: run_node(code, DEBOUNCE_TEST),
        "category": "runtime",
    },
    "rate_limiter": {
        "prompt":   RATELIMITER_PROMPT,
        "test_fn":  lambda code: run_node(code, RATELIMITER_TEST),
        "category": "runtime",
    },
    "codebase_reuse": {
        "prompt":   CODEBASE_REUSE_PROMPT,
        "test_fn":  run_codebase_reuse_test,
        "category": "kevin_unique",
    },
    "pubsub": {
        "prompt":   PUBSUB_PROMPT,
        "test_fn":  lambda code: run_node(code, PUBSUB_TEST),
        "category": "runtime",
    },
    "binary_search": {
        "prompt":   BINARYSEARCH_PROMPT,
        "test_fn":  lambda code: run_node(code, BINARYSEARCH_TEST),
        "category": "runtime",
    },
    "yagni_pushback": {
        "prompt":   YAGNI_PUSHBACK_PROMPT,
        "test_fn":  run_yagni_pushback_test,
        "category": "kevin_unique",
    },
    "inline_vs_file": {
        "prompt":   INLINE_VS_FILE_PROMPT,
        "test_fn":  run_inline_vs_file_test,
        "category": "kevin_unique",
    },
    "simplest_correct": {
        "prompt":   SIMPLEST_PROMPT,
        "test_fn":  lambda code: run_node(code, SIMPLEST_TEST),
        "category": "runtime",
    },
}


# ── Main runner ───────────────────────────────────────────────────────────────

def run_task_once(task_name: str, condition: str, system: Optional[str]) -> dict:
    task   = TASKS[task_name]
    result = call_claude(system, task["prompt"])
    code   = result["code"] or result["text"]
    passed, msg = task["test_fn"](code)
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
        "raw_text":      result["text"],
    }


def median_int(values: list[int]) -> int:
    return int(statistics.median(values))


def print_summary(all_runs: list[dict], n_runs: int) -> None:
    # Group by (condition, task)
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for r in all_runs:
        grouped[(r["condition"], r["task"])].append(r)

    # Per-condition aggregates (medians across tasks and runs)
    cond_stats: dict[str, dict] = {
        c: {"pass": 0, "total": 0, "output_tokens": [], "code_tokens": [],
            "prose_tokens": [], "code_lines": [], "cost": 0.0}
        for c in CONDITIONS
    }

    for (cond, task), runs in grouped.items():
        passes = sum(1 for r in runs if r["passed"])
        s = cond_stats[cond]
        s["pass"]         += passes
        s["total"]        += len(runs)
        s["output_tokens"].extend(r["output_tokens"] for r in runs)
        s["code_tokens"].extend(r["code_tokens"]     for r in runs)
        s["prose_tokens"].extend(r["prose_tokens"]   for r in runs)
        s["code_lines"].extend(r["code_lines"]       for r in runs)
        s["cost"]         += sum(r["cost_usd"] for r in runs)

    baseline_tokens = median_int(cond_stats["agent_baseline"]["output_tokens"]) or 1

    print("\n" + "=" * 88)
    print("OVERALL  (median output tokens per call, pass rate across all tasks × runs)")
    print(f"{'Condition':<16} {'Pass':>10} {'Tokens':>8} {'vs base':>8} "
          f"{'CodeTok':>8} {'ProseTok':>9} {'Lines':>6} {'Cost':>9}")
    print("-" * 88)
    for cond in CONDITIONS:
        s      = cond_stats[cond]
        rate   = f"{s['pass']}/{s['total']}"
        tokens = median_int(s["output_tokens"])
        pct    = f"{tokens / baseline_tokens * 100:.0f}%"
        print(
            f"{cond:<16} {rate:>10} {tokens:>8} {pct:>8} "
            f"{median_int(s['code_tokens']):>8} {median_int(s['prose_tokens']):>9} "
            f"{median_int(s['code_lines']):>6} ${s['cost']:>8.4f}"
        )
    print("=" * 88)

    # Per-task pass rates
    print("\nPER-TASK PASS RATE  (passes / total runs)")
    task_names = list(TASKS.keys())
    header = f"{'Task':<20}" + "".join(f"{c[:10]:>12}" for c in CONDITIONS)
    print(header)
    print("-" * (20 + 12 * len(CONDITIONS)))
    for task_name in task_names:
        row = f"{task_name:<20}"
        for cond in CONDITIONS:
            runs   = grouped.get((cond, task_name), [])
            passes = sum(1 for r in runs if r["passed"])
            total  = len(runs)
            row   += f"{passes}/{total:>1}{'  ':>9}"
        print(row)

    # Ablation gap: does kevin beat be_brief?
    kevin_pass  = cond_stats["kevin"]["pass"]
    brief_pass  = cond_stats["be_brief"]["pass"]
    kevin_tok   = median_int(cond_stats["kevin"]["output_tokens"])
    brief_tok   = median_int(cond_stats["be_brief"]["output_tokens"])
    print(f"\nABLATION GAP (kevin vs be_brief)")
    print(f"  Pass rate: kevin {kevin_pass}/{cond_stats['kevin']['total']}  vs  be_brief {brief_pass}/{cond_stats['be_brief']['total']}")
    print(f"  Tokens:    kevin {kevin_tok}  vs  be_brief {brief_tok}  (delta {kevin_tok - brief_tok:+})")
    if kevin_pass > brief_pass:
        print("  Result: kevin wins on correctness — ladder adds real value beyond terse instruction")
    elif kevin_tok < brief_tok:
        print("  Result: kevin tied on correctness, cheaper — SKILL.md overhead absorbed by output savings")
    else:
        print("  Result: kevin does not outperform be_brief — needs tuning")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs",  type=int, default=3, help="runs per (task, condition)")
    parser.add_argument("--tasks", type=str, default="all",
                        help="comma-separated task names or 'all'")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY before running.")

    task_names = list(TASKS.keys()) if args.tasks == "all" else args.tasks.split(",")
    for t in task_names:
        if t not in TASKS:
            sys.exit(f"Unknown task '{t}'. Valid: {', '.join(TASKS.keys())}")

    total_calls = len(task_names) * len(CONDITIONS) * args.runs
    approx_cost = total_calls * 400 * PRICE_OUTPUT + total_calls * 800 * PRICE_INPUT
    print(f"Tasks: {len(task_names)} × {len(CONDITIONS)} conditions × {args.runs} runs = {total_calls} calls")
    print(f"Model: {MODEL}  |  Estimated cost: ~${approx_cost:.3f}\n")

    all_runs: list[dict] = []
    done = 0

    for task_name in task_names:
        print(f"Task: {task_name}")
        for condition, system in CONDITIONS.items():
            run_results = []
            for run_i in range(args.runs):
                done += 1
                label = f"  [{condition:15}] run {run_i+1}/{args.runs}"
                print(f"{label} ...", end=" ", flush=True)
                try:
                    r = run_task_once(task_name, condition, system)
                    r["run_index"] = run_i
                    run_results.append(r)
                    status = "PASS" if r["passed"] else f"FAIL — {(r['fail_reason'] or '')[:50]}"
                    print(f"{status}  ({r['output_tokens']} tok)")
                except Exception as e:
                    print(f"ERROR: {e}")
                    run_results.append({
                        "condition": condition, "task": task_name,
                        "category": TASKS[task_name]["category"],
                        "passed": False, "fail_reason": str(e),
                        "output_tokens": 0, "input_tokens": 0,
                        "code_tokens": 0, "prose_tokens": 0,
                        "code_lines": 0, "time_s": 0, "cost_usd": 0.0,
                        "run_index": run_i,
                    })
            all_runs.extend(run_results)

    out_path = ROOT / "benchmarks" / "correctness_results.json"
    out_path.write_text(json.dumps(all_runs, indent=2), encoding="utf-8")
    print(f"\nResults saved to {out_path}")

    print_summary(all_runs, args.runs)


if __name__ == "__main__":
    main()
