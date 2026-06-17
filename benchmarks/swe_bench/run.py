#!/usr/bin/env python3
"""SWE-bench Lite runner for kevin benchmark suite.

Runs N tasks from SWE-bench Lite across 4 conditions:
    baseline | kevin | caveman | ponytail

Each task is a real GitHub issue. Claude produces a patch in one shot.
The patch is evaluated using the official SWE-bench harness (Docker).

Prerequisites:
    pip install swebench datasets anthropic
    Docker running (docker info should succeed)

Usage:
    ANTHROPIC_API_KEY=sk-... python3 benchmarks/swe_bench/run.py [--tasks 50] [--dry-run]
"""
from __future__ import annotations

import os
import sys
import json
import time
import random
import argparse
from pathlib import Path
from typing import Optional
from collections import defaultdict

try:
    import anthropic
except ImportError:
    sys.exit("Run: pip install anthropic")

try:
    import docker as docker_lib
except ImportError:
    sys.exit("Run: pip install docker")

try:
    from datasets import load_dataset
except ImportError:
    sys.exit("Run: pip install datasets")

try:
    from swebench.harness.test_spec.test_spec import make_test_spec
    from swebench.harness.run_evaluation import run_instance
    from swebench.harness.constants import KEY_MODEL
except ImportError:
    sys.exit("Run: pip install swebench")

ROOT       = Path(__file__).parent.parent.parent
SKILLS_DIR = Path(__file__).parent.parent / "skills"

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

CONDITIONS: dict[str, Optional[str]] = {
    "baseline": None,
    "kevin":    _read(ROOT / "skills" / "kevin" / "SKILL.md"),
    "caveman":  _read(SKILLS_DIR / "caveman.md"),
    "ponytail": _read(SKILLS_DIR / "ponytail.md"),
}

MODEL        = "claude-sonnet-4-6"
PRICE_OUTPUT = 15.0 / 1_000_000   # Sonnet output per token
PRICE_INPUT  = 3.0  / 1_000_000   # Sonnet input per token
RUN_ID       = "kevin-benchmark"


# ── Dataset ───────────────────────────────────────────────────────────────────

def load_tasks(n: int) -> list[dict]:
    ds = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    tasks = list(ds)
    random.seed(42)
    random.shuffle(tasks)
    return tasks[:n]


# ── Patch generation ──────────────────────────────────────────────────────────

def make_prompt(task: dict) -> str:
    hints = task.get("hints_text", "").strip()
    return (
        f"Repository: {task['repo']}\n\n"
        f"Issue:\n{task['problem_statement']}\n\n"
        + (f"Hints:\n{hints}\n\n" if hints else "")
        + "Produce a minimal unified diff (git patch) that fixes this issue. "
        "Output only the patch — no explanation, no markdown fences."
    )

def call_claude(system: Optional[str], prompt: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    kwargs: dict = dict(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system

    t0 = time.time()
    r  = client.messages.create(**kwargs)
    text = r.content[0].text
    return {
        "text":          text,
        "output_tokens": r.usage.output_tokens,
        "input_tokens":  r.usage.input_tokens,
        "time_s":        round(time.time() - t0, 2),
        "cost_usd":      round(
            r.usage.output_tokens * PRICE_OUTPUT +
            r.usage.input_tokens  * PRICE_INPUT, 6
        ),
    }


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_patch(docker_client, task: dict, patch: str, cond: str) -> Optional[bool]:
    try:
        test_spec = make_test_spec(task)
        pred = {
            "instance_id":        task["instance_id"],
            "model_patch":        patch,
            "model_name_or_path": f"kevin-benchmark-{cond}",
        }
        result = run_instance(
            test_spec=test_spec,
            pred=pred,
            rm_image=False,
            force_rebuild=False,
            client=docker_client,
            run_id=RUN_ID,
            timeout=300,
        )
        # result is a dict; resolved means all tests pass
        return result.get("resolved", False)
    except Exception as e:
        print(f"\n  [eval error] {type(e).__name__}: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks",   type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY") and not args.dry_run:
        sys.exit("Set ANTHROPIC_API_KEY before running.")

    # Connect to Docker
    try:
        docker_client = docker_lib.from_env()
        docker_client.ping()
    except Exception as e:
        sys.exit(f"Docker not available: {e}")

    print(f"Loading {args.tasks} tasks from SWE-bench Lite (seed 42)...")
    tasks = load_tasks(args.tasks)
    print(f"Loaded {len(tasks)} tasks. {len(CONDITIONS)} conditions. "
          f"{len(tasks) * len(CONDITIONS)} total evaluations.\n")

    # Cost estimate
    approx_tokens_per_call = 2000
    est_cost = len(tasks) * len(CONDITIONS) * approx_tokens_per_call * PRICE_OUTPUT
    print(f"Estimated API cost: ~${est_cost:.2f} (Sonnet output only, ~{approx_tokens_per_call} tok/call)")
    print(f"Estimated time: {len(tasks) * len(CONDITIONS) * 3 // 60}–{len(tasks) * len(CONDITIONS) * 5 // 60} min (Docker eval ~3–5 min/task)\n")

    results = []
    total = len(tasks) * len(CONDITIONS)
    done  = 0

    for task in tasks:
        tid = task["instance_id"]
        for cond, system in CONDITIONS.items():
            done += 1
            print(f"[{done:>3}/{total}] {tid[:45]:<45} {cond:<10}", end=" ", flush=True)

            if args.dry_run:
                print("(dry run)")
                results.append({
                    "instance_id": tid, "condition": cond,
                    "resolved": None, "output_tokens": 0,
                    "input_tokens": 0, "cost_usd": 0.0, "time_s": 0.0,
                    "dry_run": True,
                })
                continue

            # Generate patch
            prompt = make_prompt(task)
            try:
                api = call_claude(system, prompt)
            except Exception as e:
                print(f"API error: {e}")
                results.append({
                    "instance_id": tid, "condition": cond,
                    "resolved": None, "output_tokens": 0,
                    "input_tokens": 0, "cost_usd": 0.0, "time_s": 0.0,
                    "error": str(e),
                })
                continue

            patch = api["text"]
            resolved = evaluate_patch(docker_client, task, patch, cond)

            icon = "✓" if resolved else ("✗" if resolved is False else "?")
            print(f"{icon}  {api['output_tokens']:>5} tok  ${api['cost_usd']:.4f}  {api['time_s']:.1f}s")

            results.append({
                "instance_id":   tid,
                "condition":     cond,
                "resolved":      resolved,
                "model_patch":   patch,
                "output_tokens": api["output_tokens"],
                "input_tokens":  api["input_tokens"],
                "cost_usd":      api["cost_usd"],
                "time_s":        api["time_s"],
            })

            # Save incrementally
            out = ROOT / "benchmarks" / "swe_bench_results.json"
            out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Final save
    out = ROOT / "benchmarks" / "swe_bench_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults saved to {out}")

    # Write per-condition predictions files for swebench CLI evaluation
    preds_dir = ROOT / "benchmarks" / "swe_bench"
    for cond in CONDITIONS:
        preds = [
            {
                "instance_id":        r["instance_id"],
                "model_patch":        r.get("model_patch", ""),
                "model_name_or_path": f"kevin-{cond}",
            }
            for r in results if r["condition"] == cond and not r.get("dry_run")
        ]
        if preds:
            p = preds_dir / f"predictions_{cond}.json"
            p.write_text(json.dumps(preds, indent=2), encoding="utf-8")
            print(f"Predictions written to {p}")

    print("\nTo evaluate with swebench CLI:")
    for cond in CONDITIONS:
        print(f"  python3.11 -m swebench.harness.run_evaluation \\")
        print(f"    --predictions_path benchmarks/swe_bench/predictions_{cond}.json \\")
        print(f"    --run_id kevin-{cond} --cache_level env")

    if any(not r.get("dry_run") for r in results):
        stats: dict = defaultdict(lambda: {"res": 0, "total": 0, "tokens": 0, "cost": 0.0})
        for r in results:
            if r.get("dry_run") or r.get("error"):
                continue
            s = stats[r["condition"]]
            s["total"]  += 1
            s["res"]    += int(r["resolved"] or 0)
            s["tokens"] += r["output_tokens"]
            s["cost"]   += r["cost_usd"]

        print(f"\n{'Condition':<12} {'Resolved':>10} {'Rate':>7} {'Tokens':>8} {'Cost':>9}")
        print("-" * 52)
        for cond in CONDITIONS:
            s = stats[cond]
            rate = f"{s['res'] / s['total'] * 100:.1f}%" if s["total"] else "—"
            print(f"{cond:<12} {s['res']:>5}/{s['total']:<4} {rate:>6} "
                  f"{s['tokens']:>8} ${s['cost']:>8.4f}")


if __name__ == "__main__":
    main()
