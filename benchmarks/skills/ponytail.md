---
# Ponytail — approximate reconstruction of DietrichGebert/ponytail skill
# Used in benchmarks as a "copy ladder" condition.
# Original: https://github.com/DietrichGebert/ponytail
---

Before writing any code, run through the Copy Ladder. Stop at the first step that applies.

## Copy Ladder

1. **Is it already in the codebase?** → Copy it. Reference where it came from.
2. **Is it in the standard library?** → Use it. No new code.
3. **Is it in an already-installed dependency?** → Use it. No new dependency.
4. **Can it be a one-liner?** → Write one line.
5. **Ok, write the minimum.** Match existing style. No abstractions. No patterns.

## Rules

- Copy before write.
- Standard library before third-party.
- Existing dep before new dep.
- One-liner before function.
- Minimum before complete.
- No boilerplate. No setup. No teardown unless asked.
- No comments unless the logic is non-obvious.
- No types unless the file already uses types.

## Output

Show only the code that changes. No before/after. No explanation unless asked.
If explanation needed: one sentence, inline.
