#!/usr/bin/env python3.11
"""
kevin benchmark — baseline vs kevin vs ponytail
Measures: output tokens, lines of code, total response length
"""
import os, json, time, statistics
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY)

SKILL_PATH = os.path.join(os.path.dirname(__file__), "..", "skills", "kevin", "SKILL.md")
with open(SKILL_PATH) as f:
    KEVIN_SKILL = f.read()

PONYTAIL_SKILL = """You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written.

Before writing any code, stop at the first rung that holds:
1. Does this need to be built at all? (YAGNI)
2. Does the standard library already do this? Use it.
3. Does a native platform feature cover it? Use it.
4. Does an already-installed dependency solve it? Use it.
5. Can this be one line? Make it one line.
6. Only then: write the minimum code that works.

Rules:
- No abstractions that weren't explicitly requested.
- No new dependency if it can be avoided.
- No boilerplate nobody asked for.
- Deletion over addition. Boring over clever. Fewest files possible.
- Code first. Then at most three short lines: what was skipped, when to add it back."""

TASKS = [
    "Write an email validator function in Python.",
    "Write a debounce function in JavaScript.",
    "Write a function that reads a CSV file and sums a numeric column in Python.",
    "Write a countdown timer component in React.",
    "Write a simple rate limiter in Python.",
]

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
]

RUNS = 3  # increase to 10 for publication-quality results

def call(model, system, prompt):
    kwargs = dict(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    r = client.messages.create(**kwargs)
    text = r.content[0].text
    return {
        "output_tokens": r.usage.output_tokens,
        "input_tokens": r.usage.input_tokens,
        "lines": text.count("\n") + 1,
        "chars": len(text),
        "text": text,
    }

def benchmark():
    results = {}

    arms = [
        ("baseline", None),
        ("ponytail", PONYTAIL_SKILL),
        ("kevin",    KEVIN_SKILL),
    ]

    for model in MODELS:
        results[model] = {}
        for arm_name, system in arms:
            results[model][arm_name] = []
            print(f"\n{model} / {arm_name}")
            for task in TASKS:
                run_results = []
                for run in range(RUNS):
                    print(f"  task {TASKS.index(task)+1}/{len(TASKS)} run {run+1}/{RUNS}...", end="", flush=True)
                    try:
                        r = call(model, system, task)
                        run_results.append(r)
                        print(f" {r['output_tokens']} tokens, {r['lines']} lines")
                    except Exception as e:
                        print(f" ERROR: {e}")
                    time.sleep(0.5)

                if run_results:
                    results[model][arm_name].append({
                        "task": task,
                        "median_output_tokens": statistics.median(r["output_tokens"] for r in run_results),
                        "median_lines": statistics.median(r["lines"] for r in run_results),
                        "median_chars": statistics.median(r["chars"] for r in run_results),
                        "runs": len(run_results),
                        "samples": [{"tokens": r["output_tokens"], "lines": r["lines"], "text": r["text"][:300]} for r in run_results],
                    })

    return results

def summarize(results):
    print("\n\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)

    for model in results:
        print(f"\n{model}")
        print(f"{'Task':<35} {'Baseline':>10} {'Ponytail':>10} {'Kevin':>10} {'Kevin vs Base':>14} {'Kevin vs PT':>12}")
        print("-"*90)

        baseline_data = results[model].get("baseline", [])
        ponytail_data = results[model].get("ponytail", [])
        kevin_data    = results[model].get("kevin", [])

        total_base_tok = total_pt_tok = total_kev_tok = 0
        total_base_lines = total_pt_lines = total_kev_lines = 0

        for i, task in enumerate(TASKS):
            short = task[:33] + ".." if len(task) > 35 else task
            b = baseline_data[i]["median_output_tokens"] if i < len(baseline_data) else None
            p = ponytail_data[i]["median_output_tokens"] if i < len(ponytail_data) else None
            k = kevin_data[i]["median_output_tokens"]    if i < len(kevin_data)    else None

            kv_base = f"{((k/b)-1)*100:+.0f}%" if b and k else "n/a"
            kv_pt   = f"{((k/p)-1)*100:+.0f}%" if p and k else "n/a"

            print(f"{short:<35} {str(b or 'n/a'):>10} {str(p or 'n/a'):>10} {str(k or 'n/a'):>10} {kv_base:>14} {kv_pt:>12}")

            if b: total_base_tok += b
            if p: total_pt_tok   += p
            if k: total_kev_tok  += k

        print("-"*90)
        kv_base_total = f"{((total_kev_tok/total_base_tok)-1)*100:+.0f}%" if total_base_tok else "n/a"
        kv_pt_total   = f"{((total_kev_tok/total_pt_tok)-1)*100:+.0f}%"   if total_pt_tok   else "n/a"
        print(f"{'TOTAL (output tokens)':<35} {total_base_tok:>10} {total_pt_tok:>10} {total_kev_tok:>10} {kv_base_total:>14} {kv_pt_total:>12}")

        # Lines
        print(f"\n  Lines of code:")
        for i, task in enumerate(TASKS):
            short = task[:33] + ".." if len(task) > 35 else task
            b = baseline_data[i]["median_lines"] if i < len(baseline_data) else None
            p = ponytail_data[i]["median_lines"]  if i < len(ponytail_data) else None
            k = kevin_data[i]["median_lines"]     if i < len(kevin_data)    else None
            kv_base = f"{((k/b)-1)*100:+.0f}%" if b and k else "n/a"
            kv_pt   = f"{((k/p)-1)*100:+.0f}%" if p and k else "n/a"
            print(f"  {short:<33} {str(b or 'n/a'):>10} {str(p or 'n/a'):>10} {str(k or 'n/a'):>10} {kv_base:>14} {kv_pt:>12}")

    return results

if __name__ == "__main__":
    print(f"kevin benchmark — {RUNS} runs × {len(TASKS)} tasks × {len(MODELS)} models × 3 arms")
    print(f"Total API calls: {RUNS * len(TASKS) * len(MODELS) * 3}")
    results = benchmark()
    summarize(results)
    out = os.path.join(os.path.dirname(__file__), "results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to {out}")
