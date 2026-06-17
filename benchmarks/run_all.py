#!/usr/bin/env python3
"""Run all kevin benchmarks and generate RESULTS.md.

Usage:
    ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_all.py [--skip-swe]

Flags:
    --skip-swe   skip SWE-bench Lite (fast, runs correctness suite only)
    --dry-run    skip all API calls (structure check only)
"""
from __future__ import annotations

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent


def run(script: Path, extra_args: list[str] = []) -> bool:
    """Run a python script, stream output, return True on success."""
    cmd = [sys.executable, str(script)] + extra_args
    result = subprocess.run(cmd, env={**os.environ})
    return result.returncode == 0


def load_json(path: Path) -> list | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def generate_results_md(
    correctness: list | None,
    swe_bench: list | None,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Kevin Benchmark Results",
        "",
        f"Generated: {now}  ",
        f"Model: `claude-haiku-4-5-20251001` (correctness) · `claude-sonnet-4-6` (SWE-bench)",
        "",
        "---",
        "",
    ]

    # ── Correctness suite ──
    lines.append("## Part 1 — Correctness Suite")
    lines.append("")
    lines.append(
        "Five tasks. Four conditions. Automated pass/fail via `node test.js`. "
        "Code lines = lines inside ` ``` ` blocks only."
    )
    lines.append("")

    if correctness:
        from collections import defaultdict

        # Per-task table
        tasks = sorted({r["task"] for r in correctness})
        conds = ["baseline", "kevin", "caveman", "ponytail"]

        for task in tasks:
            rows = {r["condition"]: r for r in correctness if r["task"] == task}
            lines.append(f"### {task.replace('_', ' ').title()}")
            lines.append("")
            lines.append(
                f"| Condition | Pass | Tokens | Code tok | Prose tok | Lines | Cost |"
            )
            lines.append("|-----------|------|-------:|---------:|----------:|------:|-----:|")
            for cond in conds:
                r = rows.get(cond)
                if not r:
                    continue
                status = "✅" if r["passed"] else "❌"
                lines.append(
                    f"| {cond} | {status} | {r['output_tokens']} | "
                    f"{r['code_tokens']} | {r['prose_tokens']} | "
                    f"{r['code_lines']} | ${r['cost_usd']:.4f} |"
                )
            if any(not rows.get(c, {}).get("passed") for c in conds if c in rows):
                for cond in conds:
                    r = rows.get(cond)
                    if r and not r["passed"]:
                        lines.append(f"> **{cond} failed:** {r.get('fail_reason', '')}")
            lines.append("")

        # Summary
        stats: dict = defaultdict(lambda: {"pass": 0, "fail": 0, "tokens": 0, "cost": 0.0,
                                            "code_tokens": 0, "prose_tokens": 0, "lines": 0})
        for r in correctness:
            s = stats[r["condition"]]
            s["pass" if r["passed"] else "fail"] += 1
            s["tokens"]       += r["output_tokens"]
            s["cost"]         += r["cost_usd"]
            s["code_tokens"]  += r["code_tokens"]
            s["prose_tokens"] += r["prose_tokens"]
            s["lines"]        += r["code_lines"]

        base_tok = stats["baseline"]["tokens"] or 1
        n_tasks  = len(tasks)

        lines.append("### Summary (all tasks)")
        lines.append("")
        lines.append(
            "| Condition | Correct | Tokens | vs baseline | Code tok | Prose tok | Lines | Total cost |"
        )
        lines.append("|-----------|--------:|-------:|------------:|---------:|----------:|------:|-----------:|")
        for cond in conds:
            s = stats[cond]
            correct = f"{s['pass']}/{n_tasks}"
            pct     = f"{s['tokens'] / base_tok * 100:.0f}%"
            lines.append(
                f"| {cond} | {correct} | {s['tokens']} | {pct} | "
                f"{s['code_tokens']} | {s['prose_tokens']} | {s['lines']} | ${s['cost']:.4f} |"
            )
        lines.append("")
    else:
        lines.append("_No correctness results found. Run `python3 benchmarks/correctness/run.py`._")
        lines.append("")

    # ── SWE-bench ──
    lines.append("---")
    lines.append("")
    lines.append("## Part 2 — SWE-bench Lite")
    lines.append("")
    lines.append(
        "50 tasks from [princeton-nlp/SWE-bench_Lite](https://github.com/princeton-nlp/SWE-bench). "
        "Real GitHub issues. Evaluated with official harness. Seed 42."
    )
    lines.append("")

    if swe_bench:
        from collections import defaultdict
        conds = ["baseline", "kevin", "caveman", "ponytail"]
        stats2: dict = defaultdict(lambda: {"res": 0, "total": 0, "tokens": 0, "cost": 0.0})
        for r in swe_bench:
            if r.get("dry_run"):
                continue
            s = stats2[r["condition"]]
            s["total"]   += 1
            s["res"]     += int(r["resolved"] or 0)
            s["tokens"]  += r["output_tokens"]
            s["cost"]    += r["cost_usd"]

        lines.append("| Condition | Resolved | Rate | Tokens | Cost |")
        lines.append("|-----------|--------:|-----:|-------:|-----:|")
        for cond in conds:
            s = stats2[cond]
            rate = f"{s['res'] / s['total'] * 100:.1f}%" if s["total"] else "—"
            lines.append(
                f"| {cond} | {s['res']}/{s['total']} | {rate} | {s['tokens']} | ${s['cost']:.2f} |"
            )
        lines.append("")
    else:
        lines.append(
            "_No SWE-bench results found. Run `python3 benchmarks/swe_bench/run.py`._"
        )
        lines.append("")

    # ── Why trust these numbers ──
    lines += [
        "---",
        "",
        "## Why Trust These Numbers?",
        "",
        "**Correctness suite is automated.** Each task runs `node test.js` and checks exit code. "
        "Pass means the code works. Fail means it doesn't. No manual grading.",
        "",
        "**Code lines ≠ prose lines.** Token and line counts measure only what's inside "
        "` ``` ` code blocks. Narration tokens are tracked separately (`prose_tokens`). "
        "This lets you see whether a condition cut *code* or just cut *explanation*.",
        "",
        "**Codebase-reuse task is kevin-unique.** Baseline, caveman, and ponytail don't "
        "know `formatDate` exists in `utils/date.js`. Kevin's ladder step 2 says to grep "
        "first. This task specifically measures that behavior.",
        "",
        "**SWE-bench uses real issues.** Not synthetic tasks. Real GitHub bugs with real "
        "test suites. The official harness (Docker) runs the repo's own tests. We cannot "
        "cheat a pass.",
        "",
        "**Reproduce it:**",
        "```bash",
        "ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_all.py",
        "# or just the fast suite:",
        "ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_all.py --skip-swe",
        "```",
        "",
        "All raw results are in `benchmarks/correctness_results.json` and "
        "`benchmarks/swe_bench_results.json`.",
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-swe", action="store_true", help="skip SWE-bench Lite")
    parser.add_argument("--dry-run",  action="store_true", help="skip API calls")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY") and not args.dry_run:
        sys.exit("Set ANTHROPIC_API_KEY before running.")

    print("=" * 60)
    print("Kevin benchmark suite")
    print("=" * 60)

    # Correctness suite
    print("\n[1/2] Correctness suite")
    print("-" * 40)
    correctness_script = ROOT / "benchmarks" / "correctness" / "run.py"
    if args.dry_run:
        print("  (dry run — skipping API calls)")
        ok1 = True
    else:
        ok1 = run(correctness_script)

    # SWE-bench
    swe_ok = None
    if not args.skip_swe:
        print("\n[2/2] SWE-bench Lite")
        print("-" * 40)
        swe_script = ROOT / "benchmarks" / "swe_bench" / "run.py"
        extra = ["--dry-run"] if args.dry_run else []
        swe_ok = run(swe_script, extra)
    else:
        print("\n[2/2] SWE-bench Lite — skipped (--skip-swe)")

    # Generate RESULTS.md
    print("\nGenerating RESULTS.md ...")
    correctness_data = load_json(ROOT / "benchmarks" / "correctness_results.json")
    swe_data         = load_json(ROOT / "benchmarks" / "swe_bench_results.json")

    md = generate_results_md(correctness_data, swe_data)
    results_path = ROOT / "benchmarks" / "RESULTS.md"
    results_path.write_text(md, encoding="utf-8")
    print(f"  Saved to {results_path}")

    print("\n" + "=" * 60)
    ok = ok1 and (swe_ok is not False)
    print("Done." if ok else "Finished with errors — see output above.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
