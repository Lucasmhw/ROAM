# ROAM: completed experiments and manuscript figures

This package accompanies the revised ICLR 2027 manuscript, **ROAM: Task-Conditioned Metrics for Forecasting Optimization**. It contains completed supplementary experimental summaries, the numerical inputs and code for nine figures, and the revised reviewer responses.

## Figures and numerical inputs

The numerical source is [`figures/figure_data.json`](figures/figure_data.json). To regenerate all PDF, PNG, and SVG exports:

```bash
python -m pip install matplotlib numpy
python reporting/figures/generate_figures.py
```

Run the last command from the repository root. For a standalone copy of this package, run `python figures/generate_figures.py` from this directory.

| Figure file | Content | Revised manuscript |
|---|---|---|
| FigureR1_information_flow | Descriptor, source fitting, and target-training interfaces | Figure 10 |
| FigureR2_control_and_cost | Conditioned, source-mean, and direct-search controls; calibration cost | Figure 3 |
| FigureR3_dlinear_convergence | Fixed-objective DLinear convergence and validation trajectories | Figure 5 |
| FigureR4_phase_policy | Discrete switching, continuous blending, and Phase I | Figure 15 |
| FigureR5_classification | Subject-disjoint UCI HAR classification | Figure 16 |
| FigureR6_curvature_diagnostic | Same-state positive-spectrum conditioning | Figure 4 |
| FigureR7_factorial | Complete factorial and average marginal effects | Figure 6 |
| Figure6_Table20_consistent | Four explicitly reported source–target transfers | Figure 8 |
| Figure8_Table15_consistent | Descriptor comparisons on the common .312 reference | Figure 13 |

R2–R6 report completed experiments. Transfer, descriptor, and factorial plots use arithmetic on the reported table entries. Error bars denote seed standard deviations. Lines connect the recorded aggregate observations; they do not imply additional measurements between observations.

The original three ablation settings are **ETTh1-192/iTransformer**, **ETTm1-336/PatchTST**, and **Weather-192/TimeMixer**. The optimizer tournament uses ETTh1-96 for its setting A, so these settings are labeled separately.

## Protocol and result scope

The revised manuscript and [`02_Experimental_Results_and_Protocols.md`](02_Experimental_Results_and_Protocols.md) specify target budgets, source calibration, the fixed quadratic control, classification, and the positive-spectrum diagnostic. Training commands and implementation details are provided in the parent repository.

The reporting inputs preserve the reported aggregate measurements. Per-run training logs, fitted initializer coefficients, and checkpoints are separate outputs generated under `results/` by the documented experiment commands. Marginal means and standard deviations alone do not establish a paired significance test.

## Responses

[`01_ROAM_OpenReview_Rebuttal.md`](01_ROAM_OpenReview_Rebuttal.md) contains 15 response blocks: one general response, four for p4jQ, three for BKGG, four for esdH, and three for gg28. Thanks are integrated into each reviewer's first response. Seven key experimental tables appear directly in the replies; other evidence is linked to specific revised-paper locations using a single bold-underlined style. Relevant references appear at the end of the corresponding response. [`reviewer_files/`](reviewer_files/) separates the same text by reviewer. Run `python reporting/check_openreview_lengths.py` from the repository root to check the actual Title and Comment fields after editing.

[`05_Figure_Captions_and_Placement.md`](05_Figure_Captions_and_Placement.md) records figure numbering and PDF page locations. [`Figure_Captions.tex`](Figure_Captions.tex) contains the corresponding source snippets.

[`06_Reply_Reading_View.html`](06_Reply_Reading_View.html) provides a browser reading view with per-response selection and separate Title/Comment copy buttons. Its math-rendering libraries load from a CDN. The Markdown file remains the source for pasting into OpenReview.
