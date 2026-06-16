#!/bin/bash
# Run kevin benchmarks. Needs: ANTHROPIC_API_KEY and node/npx.
# Results go to benchmarks/results.json

set -e

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Set ANTHROPIC_API_KEY first."
  exit 1
fi

echo "Installing promptfoo..."
npx promptfoo@latest eval -c benchmarks/promptfooconfig.yaml --output benchmarks/results.json

echo "Done. Results in benchmarks/results.json"
