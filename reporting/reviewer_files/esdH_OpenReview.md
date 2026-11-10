# ROAM — OpenReview 英文回复总稿

本文件含 4 个独立回复块。完整总稿为总回复 1 条、p4jQ 4 条、BKGG 3 条、esdH 4 条、gg28 3 条；各审稿人的致谢已并入第一条。分别复制 Title 和 Comment 代码块，外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。重点结论使用普通 Markdown 加粗，论文位置使用单层加粗下划线，不叠加外层加粗或标题字号。

---

## esdH_01 | esdH

Title 字段（65 characters）：

```text
Response to esdH (1/4): Numerical consistency and reproducibility
```

Comment 字段（3621 characters，LF；CRLF 为 3642）：

```markdown
Dear Reviewer esdH, thank you for your detailed checks of the numerical presentation and mathematical assumptions. We address these points in four responses.

**W1: Numerical consistency and reproducibility.**

You are correct that different aggregation scopes cannot explain conflicting values for the same named transfer pair. **We have corrected the transfer figure using the four individually reported pairs.** In the revised paper, $\\underline{\\boldsymbol{\\mathsf{Figure\\ 8}}}$ and $\\underline{\\boldsymbol{\\mathsf{Table\\ 19}}}$ now share these keyed entries:

| Source to target | Standard MSE | ROAM MSE | Recomputed reduction |
|---|---:|---:|---:|
| ETTh1 to ETTh2 | .421 | .392 | 6.89% |
| ETTm1 to Weather | .286 | .271 | 5.24% |
| Weather to ECL | .201 | .189 | 5.97% |
| ECL to Exchange | .462 | .437 | 5.41% |

Each reduction is $100(1-\\mathrm{MSE}_R/\\mathrm{MSE}_B)$. Other cells are marked NR. The separate 12-transfer aggregate, .342/.322, does not determine the eight unreported individual pairs. $\\underline{\\boldsymbol{\\mathsf{Figure\\ 13}}}$ has likewise been regenerated from $\\underline{\\boldsymbol{\\mathsf{Table\\ 14}}}$ using the common .312 reference.

**Aggregation and setting labels.** The Weather-192/TimeMixer .232 in $\\underline{\\boldsymbol{\\mathsf{Table\\ 2}}}$ is horizon-specific; the .232 in $\\underline{\\boldsymbol{\\mathsf{Table\\ 9}}}$ is a four-horizon average. The revision states these scopes and the macro-aggregation formula in $\\underline{\\boldsymbol{\\mathsf{Appendix\\ E}}}$. Lion .243 and the standard-recipe .245 are also distinct optimizer summaries. $\\underline{\\boldsymbol{\\mathsf{Table\\ 12}}}$ now names ETTh1-192/iTransformer, ETTm1-336/PatchTST, and Weather-192/TimeMixer; tournament setting A instead uses ETTh1-96. The reporting inputs preserve these scopes without reconstructing individual horizons from a mean. The broad comparison covers 35 dataset–backbone aggregates; the four optimizer-comparison settings are separately identified.

**Implementation and reporting artifacts.** The revised Reproducibility Statement and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.6}}}$ link the [anonymous release](https://anonymous.4open.science/r/ROAM-D935/). Its evidence map connects each result to its configuration, budget, aggregation rule, and implementation. The release includes `roam/controls.py` and `roam/optimizer.py`, plus entry points for source fitting, direct search, exact DLinear, classification, and same-state curvature. `aggregate_results.py`, `audit_records.py`, and `verify_checkpoints.py` check generated run records. Optional forecasting-backbone adapters provide integration entry points; their smoke tests check those interfaces.

The supplied `reporting/figures/figure_data.json` and figure generator reproduce the added numerical plots and corrected table-derived percentages. **Reporting summaries and per-run training artifacts are distinguished:** documented training commands generate logs, fitted coefficients, and checkpoints under `results/`. The aggregate inputs support the reported mean comparisons.

$\\underline{\\boldsymbol{\\mathsf{Appendix\\ D.3}}}$ states the supplementary environment, model blocks, source/target split, loss normalization, refresh/reset policy, and checkpoint selection. The target cap counts all members, probes, diagnostics, line searches, and validation; source fitting and other excluded costs are accounted for separately. The original benchmark and supplementary protocols retain their respective scopes, and plateau times are not used as population-wide compute ledgers.
```

**END esdH_01 — 下一条请新建独立回复**

---

## esdH_02 | esdH

Title 字段（71 characters）：

```text
Response to esdH (2/4): Convex DLinear and the exact training reference
```

Comment 字段（3200 characters，LF；CRLF 为 3225）：

```markdown
**W2: DLinear has a convex objective—what can an optimizer improve?**

We agree. With fixed moving-average decomposition $S$ and ordinary affine maps,
$$
\\widehat y=W_{\\rm tr}Sx+W_{\\rm se}(I-S)x+b_{\\rm tr}+b_{\\rm se}
=W_{\\rm eff}x+b_{\\rm eff}.
$$
Unregularized MSE is a convex quadratic with redundant parameters. **An invertible SPD metric preserves its stationary set and attainable training minimum.** The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.6}}}$ states this and examines finite-budget trajectories and validation-selected stopping separately from the exact optimum.

**Same-objective experiment.** $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.2}}}$ fixes ordinary DLinear, context 96, all seven ETT channels, decomposition, chronological splits, training-only normalization, and zero regularization for both optimizers. Both select a learning rate from $\\{10^{-4},3\\times10^{-4},10^{-3},3\\times10^{-3},10^{-2}\\}$ on validation seed 2027, then use ten reporting seeds. ROAM receives 2,000 updates; AdamW receives 2,000 or 10,000. These are update allocations, not equal wall-clock budgets.

$\\underline{\\boldsymbol{\\mathsf{Table\\ 22}}}$ reports ETTh2-96 below. Training losses use the final iterate; test losses use validation-selected checkpoints.

| Method | Final training MSE | Validation-selected test MSE |
|---|---:|---:|
| AdamW, 2,000 updates | .2270 +/- .0015 | .330 +/- .012 |
| AdamW, 10,000 updates | .2205 +/- .0003 | .322 +/- .010 |
| ROAM, 2,000 updates | .2213 +/- .0006 | .312 +/- .010 |
| Exact least squares | .2200 | .326 |
| Validation-selected ridge | .2220 | .310 |

Iterative deviations are seed standard deviations. Exact/ridge solutions are deterministic for the fixed split and solver. The exact float64 solve pools windows and channels for the equivalent identifiable shared affine predictor, including an intercept. Its design rank is 97 at relative tolerance $10^{-10}$; $\\|(A^\\top A/n)U-A^\\top Y/n\\|_F=2.1\\times10^{-13}$ is an absolute residual of sample-normalized equations. Ridge changes the objective and serves as a separate predictive reference.

**The results separate training convergence from prediction.** At 2,000 updates, ROAM is closer to the exact training minimum than AdamW. Extended AdamW reduces that gap further, while ROAM retains lower selected test MSE; ridge is stronger still on ETTh2-96. Across horizons 96/192/336/720, the test-MSE means are .41425 for AdamW 2k, .40325 for AdamW 10k, and .39650 for ROAM 2k. The individual horizon results are in $\\underline{\\boldsymbol{\\mathsf{Table\\ 23}}}$, and $\\underline{\\boldsymbol{\\mathsf{Figure\\ 5}}}$ separates full-training gaps from validation trajectories.

This evidence supports a finite-time trajectory/checkpoint interpretation, including the possible roles of stochastic noise and stopping, without claiming a better convex optimum or optimal test risk. The supplementary zero-decay protocol is distinct from the original $\\underline{\\boldsymbol{\\mathsf{Table\\ 11}}}$ benchmark and its .469/.421 values. The original 7.3% macro improvement is therefore not attributed to changing the predictor or attaining a lower quadratic minimum.
```

**END esdH_02 — 下一条请新建独立回复**

---

## esdH_03 | esdH

Title 字段（77 characters）：

```text
Response to esdH (3/4): Classical analysis and singular-Hessian applicability
```

Comment 字段（2680 characters，LF；CRLF 为 2702）：

```markdown
**W3: What does the analysis establish, particularly with singular Hessians?**

The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 4}}}$ states the classical attribution and conditional scope alongside the main-text results; $\\underline{\\boldsymbol{\\mathsf{Appendix\\ A}}}$ gives the proofs.

**Classical ingredients.** Proposition 1 applies spectral equivalence, the optimal constant-step quadratic contraction factor, and a local expansion. Nocedal and Wright [1] and Absil et al. [2] are now cited at the start of the main-text analysis as well as in the proofs. These ingredients explain the metric mechanism; they are not claimed as new optimization theorems.

**The singular-Hessian limitation.** The relevant operator is the symmetric $G^{-1/2}KG^{-1/2}$. If $K$ is singular and $D\\succ0$, then
$$
D^{-1/2}KD^{-1/2}=I+E
$$
is singular, so $E$ has eigenvalue $-1$ and $\\nu=\\|E\\|_2\\ge1$. If $D$ is singular, the inverse square root in that expression is not defined. Thus the coupled-block result cannot be applied directly to redundant DLinear or a singular neural-network Hessian.

The main text now interprets the bound under its stated positive-definiteness and coupling assumptions: it separates within-block alignment from neglected cross-block coupling. The singular-case argument follows immediately, so applicability is stated alongside the result.

**Damping and positive-spectrum diagnostics.** **Damping makes the metric $G$ invertible; the loss Hessian $K$ can remain singular.** $\\underline{\\boldsymbol{\\mathsf{Figure\\ 4}}}$ and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.3}}}$ report a positive-spectrum ratio while retaining flat directions in the full parameterization. It is labeled as a diagnostic, not as verification of the nondegenerate-minimum theorem. A regularized operator or a subspace convergence theorem would require its own assumptions.

**Purpose of the analysis.** It identifies alignment, cross-block coupling, and noise amplification as distinct mechanisms, and states what a positive-curvature pair guarantees in a common metric space. It does not prove convergence of NAdam, stochastic L-BFGS, the metric estimator, or the population controller. The direct-search and same-objective controls test empirical questions separately from those conditional implications. The analysis thus explains the mechanisms under explicit assumptions, while the controlled experiments assess the implemented adaptive procedure.

References

[1] Nocedal and Wright (2006). *Numerical Optimization*, 2nd ed. Springer.

[2] Absil, Mahony, and Sepulchre (2008). *Optimization Algorithms on Matrix Manifolds*. Princeton University Press.
```

**END esdH_03 — 下一条请新建独立回复**

---

## esdH_04 | esdH

Title 字段（74 characters）：

```text
Response to esdH (4/4): Attribution and the task-conditioning contribution
```

Comment 字段（3328 characters，LF；CRLF 为 3354）：

```markdown
**W4: Attribution and the distinctive contribution.**

Thank you for identifying the missing references. The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 2}}}$ attributes the established ingredients, and $\\underline{\\boldsymbol{\\mathsf{Section\\ 4}}}$ cites the classical foundations of the analysis.

- **Gradient-noise information.** McCandlish et al. [1] motivate the gradient-disagreement quantities. The initial descriptor uses ordinary gradients; the online diagnostic is evaluated under the current metric.
- **Stochastic quasi-Newton updates.** Bollapragada et al. [2] develop reliable stochastic curvature estimates with progressive batching. ROAM's supplementary controller uses fixed-batch diagnostics to gate momentum/quasi-Newton phases, with safeguarded curvature pairs.
- **Preconditioned manifold metrics.** Gao, Peng, and Yuan [3] establish preconditioned product-manifold metrics, including Gauss–Newton constructions. Nocedal and Wright [4] and Absil et al. [5] supply the spectral-equivalence, local-contraction, and manifold foundations.

**ROAM's contribution is the explicit forecasting-task-to-control interface and its controlled evaluation.** Six interpretable inputs initialize relative block scales, damping, curvature mixtures, and phase controls; online model derivatives realize the metric; validation-based population adaptation updates the controls. This specifies a task-conditioning hypothesis that can be tested by removing descriptor information or replacing it with direct search.

The source-fitting objective now appears in $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.2}}}$ and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ D.3}}}$. Ridge affine regression fits source-validation-selected latent controls with coefficient one and an unpenalized intercept; the fitted map and normalization are frozen on target tasks. $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ compares this initialization with the source intercept and direct search in the same metric family and target budget, with source calibration separately charged.

We also discuss Gao et al.'s *Learning to Optimize on Riemannian Manifolds* [6]. Their recurrent meta-optimizer learns optimization behavior on manifolds; ROAM predicts controls of a prescribed family from explicit statistics. Source fitting remains a learned stage with a measured calibration cost. The comparison distinguishes the interfaces and learning procedures; empirical superiority claims are restricted to the methods actually evaluated.

References

[1] McCandlish et al. (2018). [An Empirical Model of Large-Batch Training](https://arxiv.org/abs/1812.06162).

[2] Bollapragada et al. (2018). [A Progressive Batching L-BFGS Method for Machine Learning](https://proceedings.mlr.press/v80/bollapragada18a.html). ICML.

[3] Gao, Peng, and Yuan (2025). [Optimization on Product Manifolds under a Preconditioned Metric](https://arxiv.org/abs/2306.08873). SIAM J. Matrix Anal. Appl.

[4] Nocedal and Wright (2006). *Numerical Optimization*, 2nd ed. Springer.

[5] Absil, Mahony, and Sepulchre (2008). *Optimization Algorithms on Matrix Manifolds*. Princeton University Press.

[6] Gao et al. (2023). [Learning to Optimize on Riemannian Manifolds](https://wu-yuwei-bit.github.io/paper/TPAMI2023_Gao_Learning_to_Optimize.pdf). IEEE TPAMI.
```

**END esdH_04 — 下一条请新建独立回复**
