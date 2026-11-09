#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec 9>results/suite/run.lock
flock 9
test -f results/FOLLOWUPS_COMPLETE.txt
python -u scripts/curvature_diagnostic.py --seeds 10 > results/curvature.log 2>&1
python scripts/aggregate_results.py --strict > results/aggregation.log 2>&1
python scripts/audit_records.py > results/record-audit.log 2>&1
python scripts/verify_checkpoints.py > results/checkpoint-verification.log 2>&1
python scripts/plot_results.py > results/plotting.log 2>&1
python scripts/plot_table20.py >> results/plotting.log 2>&1
python scripts/audit_manuscript_numbers.py > results/manuscript-audit.log 2>&1
python scripts/train_forecast.py --model DLinear --dataset ETTh2 --horizon 96 --initializer results/suite/initializer.json --steps 20 --output results/cli_smoke.json > results/cli-smoke.log 2>&1
printf 'All result audits and figures completed.\n' > results/POSTCHECKS_COMPLETE.txt
