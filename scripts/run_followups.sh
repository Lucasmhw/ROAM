#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec 9>results/suite/run.lock
flock 9
python - <<'PY'
from pathlib import Path
p=Path('results/suite')
assert len(list(p.glob('target_*.json')))==120, 'Target suite is incomplete'
assert len(list(p.glob('convex_*.json')))==150, 'Convergence suite is incomplete'
PY
python -m pytest -q > results/tests.log 2>&1
for model in DLinear iTransformer PatchTST TimeMixer ModernTCN; do
  python scripts/smoke_backbones.py --model "$model"
done > results/backbone-smoke.log 2>&1
python -u scripts/convex_zero_decay.py > results/convex-zero.log 2>&1
python -u scripts/coldstart_compare.py > results/coldstart.log 2>&1
# The input archive is checked before any classification experiment starts.
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
p=Path('data/har.zip')
assert p.stat().st_size==61005872, 'HAR archive upload is incomplete'
with ZipFile(p) as z: assert z.testzip() is None
PY
python -u scripts/classification_suite.py > results/classification.log 2>&1
printf 'All follow-up experiments completed.\n' > results/FOLLOWUPS_COMPLETE.txt
