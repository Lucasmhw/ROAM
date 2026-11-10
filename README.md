# ROAM: task-conditioned metrics for forecasting optimization

This repository contains an executable implementation of the ordinary-parameter ROAM operator family and scripts for the supplementary experiments accompanying the author response. The scripts fit the task initializer, record calibration candidates and per-seed measurements, and generate tables and figures.

Completed experimental summaries, the revised responses, and all nine supplementary figure exports are available in [reporting/](reporting/README.md). The numerical plotting inputs are in [figure_data.json](reporting/figures/figure_data.json). Experiment commands create per-run logs, fitted coefficients, and checkpoints under the Git-ignored `results/` directory.

The numerical choices are specified in [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md). The reporting package identifies the supplementary experiments, original benchmark aggregates, and table-derived figures separately. Four additional forecasting adapters provide integration checks for the corresponding backbone interfaces.

## Installation

Python 3.10 or newer and a PyTorch installation appropriate for your CUDA environment are required. The measured GPU experiments used one RTX 4090. The main suite records its runtime environment in `results/suite/environment.json` when executed.

Start from a fresh checkout or downloaded source archive and run commands from its root directory. The recorded Python/CUDA and package versions are listed in [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md). The full experiment commands below default to a CUDA device.

```bash
python -m pip install -e .
python -m pip install pytest
python -m pytest -q
```

For optional upstream backbone checks:

```bash
python -m pip install einops reformer-pytorch
python scripts/fetch_backbones.py
python scripts/smoke_backbones.py --model iTransformer
python scripts/smoke_backbones.py --model PatchTST
python scripts/smoke_backbones.py --model TimeMixer
python scripts/smoke_backbones.py --model ModernTCN
```

Upstream archives are pinned to commits and retain their own licenses. They are downloaded into `vendor/`, which is excluded from this repository. Attribution and source links appear in [THIRD_PARTY.md](THIRD_PARTY.md).

## Reproduce the evidence

Run the commands below in order from the repository root. No existing `results/` folder or pretrained weights are required: source calibration first creates the initializer; subsequent experiments create their records and selected checkpoints; verification and plotting consume those newly generated files. Dataset downloaders obtain ETT and UCI HAR automatically when missing.

Scripts resume completed JSON records, so use a new output directory for a different configuration. Do not mix records from different protocols in one directory. No test metric is used to select a configuration or checkpoint.

```bash
# 8 source tasks, 16 candidates each; then 120 target-population runs
# and 150 finite/extended-training comparisons.
python scripts/run_suite.py --stage all --seeds 10 --candidates 16 --calibration-steps 1000 --target-seconds 20

# Exact affine-predictor solutions and validation-selected ridge controls.
python scripts/exact_dlinear.py

# Same unregularized quadratic: zero-decay AdamW control.
python scripts/convex_zero_decay.py --seeds 10

# Charge source calibration to the first task, 3 matched seeds per target.
python scripts/coldstart_compare.py --seeds 3 --seconds 20

# Subject-disjoint classification extension, with its own initializer.
python scripts/classification_suite.py --seeds 10 --seconds 30

# Training-only, exact positive-spectrum diagnostic at initialization.
python scripts/curvature_diagnostic.py --seeds 10

# Refuse incomplete runs; generate every response table from raw JSON.
python scripts/aggregate_results.py --strict
python scripts/audit_records.py
python scripts/verify_checkpoints.py

# Optional figures from the same run ledger.
python -m pip install matplotlib
python scripts/plot_results.py
python scripts/plot_table20.py

# Verify arithmetic in the supplied manuscript independently of raw runs.
python scripts/audit_manuscript_numbers.py
```

Official ETT and UCI HAR downloads are automatic. Dataset URLs and SHA-256 checksums are saved in the records. Data archives are not redistributed here. The ETT training/validation/test borders are the conventional 12/4/4 months; context is 96 and all seven channels are used. HAR retains the official test subjects and creates validation subjects only from the official training set.

The commands above are the fresh-checkout entry points. The optional `scripts/run_followups.sh` is a Linux server-workflow helper: it expects the forecasting suite, optional upstream backbones, and `data/har.zip` to be present before it runs its checks. It is not the first command to run in an empty checkout.

After source calibration has generated `results/suite/initializer.json`, a single conditioned DLinear run can use those coefficients:

```bash
python scripts/train_forecast.py --model DLinear --dataset ETTh2 --horizon 96 --initializer results/suite/initializer.json --steps 2000 --output results/manual.json
```

## What is compared

| Experiment | Fixed elements | Varying element | Recorded budget |
|---|---|---|---|
| Initialization | DLinear, metric family, population controller, data, seed | Conditioned / source mean / direct search | 4 members, 20 seconds, 20 validation calls |
| Switching | Conditioned initialization and metric | Discrete / explicit blend / Phase I | Same target budget |
| Metric | Population and initialization protocol | Diagonal metric / identity | Same target budget |
| First-task cost | Target task and control search family | Source fit plus transfer / target-only control search | Source calibration cost explicitly charged |
| Convex control | Shared affine DLinear family, data | AdamW 2k/10k updates / ROAM 2k / exact LS | Update-controlled, costs reported |
| Classification | Fixed temporal CNN and subject splits | Initializer and mixing rule | 4 members, 30 seconds, 20 validation calls |

Source calibration is outside the target adaptation cap and is reported separately. Elapsed time includes training, metric probes, diagnostics, line searches, and validation for every population member. It excludes loading, descriptor extraction, and final reporting evaluations. The cap is checked after complete updates; the final validation round can cause a small measured overrun. Peak CUDA memory is the whole-run allocated-memory peak, including data and final reporting evaluations. The AdamW classification reference uses 1,500 updates and is not a time-matched population comparator.

## Outputs and audit trail

The following paths are generated by the experiment and verification scripts; they are not included in the GitHub checkout.

- `results/suite/initializer.json`: actual W, b, feature means/scales, and calibration provenance.
- `results/suite/calibration_*.json`: all source candidates and validation histories.
- `results/suite/target_*.json`: ten seeds per target and arm, with all population members counted.
- `results/suite/checkpoints/`: validation-selected population predictors.
- `results/convex_zero/`: zero-decay selection and convergence controls; identical existing runs are referenced instead of recomputed.
- `results/exact/`: normal-equation residuals, ranks, and least-squares/ridge metrics.
- `results/coldstart/`: all target-only search trials and their cost.
- `results/classification/`: source splits, initializer, candidates, and ten-seed target records.
- `results/summary/RESULTS.md`: generated tables; `summary.json` contains fuller statistics.
- `results/record_audit.json`: validation selection, initial populations, source fits, budgets, and subject-split checks.
- `results/checkpoint_verification.json`: re-evaluation of the 176 generated selected predictors.
- `results/tests.log` and `results/backbone-smoke.log`: numerical and integration verification.

Means and sample standard deviations are computed over the declared reporting seeds. Supplementary paired confidence intervals in `summary.json` are exploratory and unadjusted for multiple comparisons. Generated reports include unsuccessful candidates and outcomes unfavorable to conditioning. Wall-clock caps produce hardware-dependent update counts; fixed seeds do not imply bitwise-identical elapsed-time runs. The checkpoint verification script checks reported metrics against the generated selected weights.

Optimizer forward/backward counters cover training, curvature probes, diagnostics, and line search. Validation requests are recorded separately; their batchwise inference forwards are included in elapsed time but not in the optimizer forward counter.

For direct-search populations, `initial_control_candidates` overrides the base `initial_controls` argument. The first four history entries identify the four actual initial candidates; the record audit checks that correspondence. The base argument is not used to condition a direct-search member.

## Implementation boundaries

The inner optimizer supports ordinary, unconstrained parameter blocks; additive retraction and identity transport apply. Positive-definite optimizer metrics do not impose Stiefel or SPD constraints on predictor weights. The optional constrained-manifold variants discussed in the manuscript are not activated by these experiments.

The released DLinear map uses two shared affine layers and a fixed width-25 moving average. The exact control solves the same identifiable predictor family in float64. The five backbone entry points are available through `scripts/train_forecast.py`; without `--initializer`, that command uses explicitly labeled task-independent controls. Architecture-specific task conditioning requires fitting a compatible block-dimensional initializer. The measured source initializer has two DLinear blocks and must not be silently reused for a different block partition; the CLI checks that count.

The supplied settings define the supplementary experiment protocols; the original benchmark tables retain their separately stated settings and aggregation. The local conditioning analysis assumes positive definiteness and concerns a frozen metric, while the experiments evaluate the adaptive algorithm.
