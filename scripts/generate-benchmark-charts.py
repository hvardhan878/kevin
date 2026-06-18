#!/usr/bin/env python3
"""Generate benchmark charts from benchmarks/full_comparison_results.json."""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "full_comparison_results.json"
OUT_SUMMARY = ROOT / "assets" / "benchmark-summary.png"
OUT_TASKS = ROOT / "assets" / "benchmark-tasks.png"

CONDITIONS = ["agent_baseline", "caveman", "ponytail", "kevin"]
LABELS = {
    "agent_baseline": "agent baseline",
    "caveman": "caveman",
    "ponytail": "ponytail",
    "kevin": "kevin",
}
COLORS = {
    "agent_baseline": "#89b4fa",
    "caveman": "#a6adc8",
    "ponytail": "#cba6f7",
    "kevin": "#fab387",
}
TASK_LABELS = {
    "debounce": "debounce",
    "rate_limiter": "rate limiter",
    "pubsub": "pub/sub",
    "binary_search": "binary search",
    "simplest_correct": "simplest correct",
    "codebase_reuse": "codebase reuse ★",
    "yagni_pushback": "YAGNI pushback ★",
    "inline_vs_file": "inline vs file ★",
}


def load_stats() -> tuple[dict, dict]:
    rows = [r for r in json.loads(DATA.read_text()) if r["condition"] in CONDITIONS]
    grouped: dict[tuple[str, str], list] = defaultdict(list)
    for r in rows:
        grouped[(r["condition"], r["task"])].append(r)

    cond = {
        c: {
            "pass": 0,
            "total": 0,
            "output_tokens": [],
            "prose_tokens": [],
            "cost": 0.0,
        }
        for c in CONDITIONS
    }
    tasks: dict[str, dict[str, tuple[int, int]]] = defaultdict(dict)

    for (c, task), runs in grouped.items():
        p = sum(1 for r in runs if r["passed"])
        cond[c]["pass"] += p
        cond[c]["total"] += len(runs)
        for r in runs:
            cond[c]["output_tokens"].append(r["output_tokens"])
            cond[c]["prose_tokens"].append(r["prose_tokens"])
            cond[c]["cost"] += r["cost_usd"]
        tasks[task][c] = (p, len(runs))

    for c in CONDITIONS:
        cond[c]["median_output"] = int(statistics.median(cond[c]["output_tokens"]))
        cond[c]["median_prose"] = int(statistics.median(cond[c]["prose_tokens"]))

    return cond, dict(tasks)


def chart_summary(cond: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), facecolor="#1e1e2e")
    for ax in axes:
        ax.set_facecolor("#1e1e2e")
        ax.tick_params(colors="#cdd6f4", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#45475a")

    x = np.arange(len(CONDITIONS))
    bar_colors = [COLORS[c] for c in CONDITIONS]

    # Pass rate
    passes = [cond[c]["pass"] for c in CONDITIONS]
    ax0 = axes[0]
    bars = ax0.bar(x, passes, color=bar_colors, width=0.62, edgecolor="#11111b", linewidth=0.8)
    ax0.axhline(15, color="#585b70", linestyle="--", linewidth=0.8, alpha=0.7)
    ax0.set_xticks(x)
    ax0.set_xticklabels([LABELS[c] for c in CONDITIONS], rotation=20, ha="right")
    ax0.set_ylim(0, 24)
    ax0.set_ylabel("passes (of 24)", color="#cdd6f4", fontsize=9)
    ax0.set_title("correctness", color="#cdd6f4", fontsize=11, pad=8)
    for bar, n in zip(bars, passes):
        ax0.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4, str(n),
                 ha="center", va="bottom", color="#cdd6f4", fontsize=9, fontweight="bold")

    # Output tokens (lower = better)
    tokens = [cond[c]["median_output"] for c in CONDITIONS]
    ax1 = axes[1]
    bars = ax1.bar(x, tokens, color=bar_colors, width=0.62, edgecolor="#11111b", linewidth=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels([LABELS[c] for c in CONDITIONS], rotation=20, ha="right")
    ax1.set_ylabel("median output tokens / call", color="#cdd6f4", fontsize=9)
    ax1.set_title("verbosity", color="#cdd6f4", fontsize=11, pad=8)
    for bar, n in zip(bars, tokens):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3, str(n),
                 ha="center", va="bottom", color="#cdd6f4", fontsize=9)

    # Total cost
    costs = [cond[c]["cost"] for c in CONDITIONS]
    ax2 = axes[2]
    bars = ax2.bar(x, costs, color=bar_colors, width=0.62, edgecolor="#11111b", linewidth=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([LABELS[c] for c in CONDITIONS], rotation=20, ha="right")
    ax2.set_ylabel("total cost (8 tasks × 3 runs)", color="#cdd6f4", fontsize=9)
    ax2.set_title("cost (Haiku)", color="#cdd6f4", fontsize=11, pad=8)
    for bar, n in zip(bars, costs):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0008, f"${n:.3f}",
                 ha="center", va="bottom", color="#cdd6f4", fontsize=8)

    fig.suptitle("kevin benchmark · claude-haiku · 8 tasks · 3 runs each",
                 color="#cdd6f4", fontsize=12, y=1.02)
    fig.tight_layout()
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_SUMMARY, dpi=160, bbox_inches="tight", facecolor="#1e1e2e")
    plt.close(fig)


def chart_tasks(tasks: dict) -> None:
    task_order = [
        "debounce", "rate_limiter", "pubsub", "binary_search", "simplest_correct",
        "codebase_reuse", "yagni_pushback", "inline_vs_file",
    ]
    fig, ax = plt.subplots(figsize=(8.5, 4.2), facecolor="#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    cell_w, cell_h = 1.0, 1.0

    for ri, task in enumerate(task_order):
        for ci, cond in enumerate(CONDITIONS):
            p, t = tasks[task].get(cond, (0, 3))
            color = "#a6e3a1" if p == t else "#f9e2af" if p > 0 else "#f38ba8"
            if p == 0 and task in ("codebase_reuse", "yagni_pushback", "inline_vs_file"):
                color = "#f38ba8" if p == 0 else color
            rect = mpatches.FancyBboxPatch(
                (ci * cell_w + 0.05, (len(task_order) - ri - 1) * cell_h + 0.05),
                cell_w - 0.1, cell_h - 0.1,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=color, edgecolor="#11111b", linewidth=0.6, alpha=0.85,
            )
            ax.add_patch(rect)
            label = f"{p}/{t}"
            ax.text(ci * cell_w + 0.5, (len(task_order) - ri - 1) * cell_h + 0.5, label,
                    ha="center", va="center", fontsize=9, color="#11111b", fontweight="bold")

    ax.set_xlim(0, len(CONDITIONS))
    ax.set_ylim(0, len(task_order))
    ax.set_xticks([i + 0.5 for i in range(len(CONDITIONS))])
    ax.set_xticklabels([LABELS[c] for c in CONDITIONS], color="#cdd6f4", fontsize=9)
    ax.set_yticks([i + 0.5 for i in range(len(task_order))])
    ax.set_yticklabels([TASK_LABELS[t] for t in reversed(task_order)], color="#cdd6f4", fontsize=9)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("pass rate by task (★ = judgment heuristic)", color="#cdd6f4", fontsize=11, pad=10)
    fig.tight_layout()
    fig.savefig(OUT_TASKS, dpi=160, bbox_inches="tight", facecolor="#1e1e2e")
    plt.close(fig)


def main() -> None:
    cond, tasks = load_stats()
    chart_summary(cond)
    chart_tasks(tasks)
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_TASKS}")
    for c in CONDITIONS:
        s = cond[c]
        print(f"  {c}: {s['pass']}/{s['total']} pass, {s['median_output']} tok, ${s['cost']:.4f}")


if __name__ == "__main__":
    main()
