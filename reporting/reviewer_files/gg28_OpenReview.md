# ROAM — OpenReview 英文回复总稿

本文件含 3 个独立回复块。完整总稿为总回复 1 条、p4jQ 4 条、BKGG 3 条、esdH 4 条、gg28 3 条；各审稿人的致谢已并入第一条。分别复制 Title 和 Comment 代码块，外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。重点结论使用普通 Markdown 加粗，论文位置使用单层加粗下划线，不叠加外层加粗或标题字号。

---

## gg28_01 | gg28

Title 字段（80 characters）：

```text
Response to gg28 (1/3): Task statistics, model dependence, and measured geometry
```

Comment 字段（3297 characters，LF；CRLF 为 3318）：

```markdown
Dear Reviewer gg28, thank you for recognizing the breadth of the forecasting evaluation and for asking for a clearer mechanism. We address your concerns in three responses.

**W1/Q1: How do task statistics connect to realized geometry?**

The revised $\\underline{\\boldsymbol{\\mathsf{Sections\\ 3–4}}}$ distinguish metric construction from the conditional alignment result. $\\underline{\\boldsymbol{\\mathsf{Figure\\ 10}}}$ makes the information flow explicit.

**Information path.** The descriptor initializes control coordinates. **The metric also uses model-dependent operators** $\\widehat F_b(\\theta)$ and $D_b(\\theta)$ computed from the instantiated model and training loss. For general losses, Gauss–Newton curvature contains both the model Jacobian and output-loss curvature. Initial gradient disagreement is already model-dependent, and the block partition and initializer dimensions follow the backbone. Six scalars are not intended to replace these dependencies.

For a centered linear lag predictor, $K=2\\mathbb E[xx^\\top]$ gives a precise connection between lag covariance and curvature; stationarity connects that covariance to the full spectrum. Spectral summaries can be useful without identifying extreme eigenvalues or eigendirections. $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.2}}}$ gives the source-fitting objective and the explicit derivative of positive controls with respect to descriptor coordinates.

**What is measured.** $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ compares conditioned, source-mean, and direct-search initialization within the same model, metric family, and target budget. For each of ten seeds, the same-state diagnostic uses common initial weights and a shared batch of 64 training windows to estimate the initial metric, with the second-moment term initially zero. It then evaluates each metric against the exact full-training Hessian, before training trajectories diverge. The entries below are means of per-seed positive-spectrum ratios.

| Initial metric | ETTh2-96 positive-spectrum ratio | ETTm2-96 positive-spectrum ratio |
|---|---:|---:|
| Identity | 800 | 410 |
| Default controls | 760 | 385 |
| Source mean | 720 | 390 |
| Conditioned | 640 | 375 |

$\\underline{\\boldsymbol{\\mathsf{Figure\\ 4}}}$ and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.3}}}$ report this diagnostic without treating the redundant DLinear Hessian as positive definite. With a full-rank identifiable design, the two-map model's positive rank and nullity are each $H(T+1)$, or 9,312 for $T=H=96$. This is a conditional dimension calculation; the ETTh2 design-rank measurement (97 at tolerance $10^{-10}$) is stated separately in the exact-solve experiment.

**The lower positive-spectrum ratios support improved geometry on observable directions in these settings.** They do not prove the spectral sandwich in Proposition 1 or explain the entire test-error gain. The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 4}}}$ attributes the classical result and makes its positive-definiteness/coupling assumptions explicit; it makes no convergence claim for the complete switched, stochastic, population-adapted algorithm. Together, the controls and diagnostics connect the task-conditioned mechanism to measured geometry and prediction.
```

**END gg28_01 — 下一条请新建独立回复**

---

## gg28_02 | gg28

Title 字段（71 characters）：

```text
Response to gg28 (2/3): Relationship to existing and learned optimizers
```

Comment 字段（3128 characters，LF；CRLF 为 3150）：

```markdown
**W2: What distinguishes ROAM from existing and learned optimizers?**

The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 2}}}$ attributes the established ingredients and states the contribution at the level of task-conditioned control.

Gauss–Newton/Fisher preconditioning, second-moment estimation, momentum, L-BFGS, manifold operations, and PBT are not new individually. The revised text cites preconditioned product-manifold metrics by Gao, Peng, and Yuan [1], gradient-noise-scale work by McCandlish et al. [2], and stochastic quasi-Newton safeguards by Bollapragada et al. [3].

*Learning to Optimize on Riemannian Manifolds* [4] parameterizes a Riemannian optimizer with a recurrent network and trains it through meta-optimization, including an implicit-differentiation scheme. ROAM instead retains a prescribed metric/update family and fits a compact affine map from explicit task statistics to its control coordinates, followed by derivative-free population adaptation. Source fitting is itself a learned stage, with its calibration cost explicitly included in the first-task comparison and amortized analysis.

**The practical distinction is inspectability.** Descriptor inputs have stated data dependencies; control coordinates have meanings such as block scale, damping, curvature mixture, and phase threshold; the realized metric also uses current model derivatives. $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.2}}}$ now gives the fit and descriptor-to-control sensitivity. Individual descriptor removal, removal of the descriptor term while retaining the source intercept, and direct search over the same family are explicit interventions on this interface.

$\\underline{\\boldsymbol{\\mathsf{Table\\ 3}}}$ reports the largest mean marginal effect for the metric (.01025 versus .00475 for switching and .00525 for outer adaptation). The source-mean/direct-search results in $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ further delimit the role of task information: conditioning improves on source mean on both forecasting targets, but direct search can match or exceed it and is stronger in the first-task cost comparison.

Thus our contribution is a transparent task-conditioning mechanism for forecasting optimization, supported by competitive prediction results and controlled attribution tests. The comparison with recurrent learned optimizers concerns the parameterized interface and learning procedure; empirical performance comparisons are restricted to the optimizers actually evaluated.

References

[1] Gao, Peng, and Yuan (2025). [Optimization on Product Manifolds under a Preconditioned Metric](https://arxiv.org/abs/2306.08873). SIAM J. Matrix Anal. Appl.

[2] McCandlish et al. (2018). [An Empirical Model of Large-Batch Training](https://arxiv.org/abs/1812.06162).

[3] Bollapragada et al. (2018). [A Progressive Batching L-BFGS Method for Machine Learning](https://proceedings.mlr.press/v80/bollapragada18a.html). ICML.

[4] Gao et al. (2023). [Learning to Optimize on Riemannian Manifolds](https://wu-yuwei-bit.github.io/paper/TPAMI2023_Gao_Learning_to_Optimize.pdf). IEEE TPAMI.
```

**END gg28_02 — 下一条请新建独立回复**

---

## gg28_03 | gg28

Title 字段（76 characters）：

```text
Response to gg28 (3/3): Discrete switching and a continuous-blending control
```

Comment 字段（2693 characters，LF；CRLF 为 2717）：

```markdown
**Q2: Why use discrete switching rather than continuous blending?**

We have added a safeguarded continuous comparator, summarized in the revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.7}}}$. $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.4}}}$ defines it, and $\\underline{\\boldsymbol{\\mathsf{Table\\ 25}}}$ and $\\underline{\\boldsymbol{\\mathsf{Figure\\ 15}}}$ report the comparison.

**Why use a gate?** The default rule waits for low relative gradient disagreement and acceptable directional curvature for three checks before using L-BFGS. A metric refresh clears memory and requires renewed eligibility. This gives an interpretable decision about when the available quasi-Newton state is usable and can avoid its direction/line-search work during Phase I. Hysteresis is a persistence rule, not a statistical certificate.

**Continuous alternative.** Using the same metric and accepted pairs, we evaluate
$$
a_t=\\frac{1}{1+\\chi_t/\\tau_\\chi}
\\frac{\\max(\\rho_t,0)}{\\max(\\rho_t,0)+\\tau_\\rho},\\qquad
p_t=(1-a_t)p_t^I+a_tp_t^{II}.
$$
The first-order direction includes its prescribed scaling. Missing valid memory disables the quasi-Newton contribution. The combined direction is checked for descent and uses the same Armijo safeguard; a non-descent direction falls back to the metric gradient. Refresh and pair-acceptance policies are shared.

Conditioned initialization, ordinary DLinear, data, population, metric estimator, and validation selection are fixed. Each population has the same 20-second target cap and 20 validation calls over ten seeds; source calibration is shared and separately accounted for.

| Policy | ETTh2-96 MSE | ETTm2-96 MSE | ETTh2 total updates |
|---|---:|---:|---:|
| Discrete switch | .312 +/- .010 | .174 +/- .004 | 2,400 |
| Continuous blend | .314 +/- .011 | .173 +/- .005 | 2,150 |
| Phase I only | .319 +/- .012 | .179 +/- .006 | 3,000 |

Update counts sum across the four members; deviations are seed standard deviations. **Switching is slightly stronger on ETTh2, blending on ETTm2.** These small differences are not paired significance claims. The figure plots validation progress by evaluation round, without relabeling rounds as elapsed time.

If two directions descend for the same objective at the same point, their convex combination also descends. We therefore do not claim blending is intrinsically unstable. Momentum and stochastic estimates need not satisfy that premise, so both policies need safeguards. The result supports a work–accuracy trade-off for this specified blend, not universal superiority of switching. The revised text presents the discrete policy as a practical default with an explicit eligibility rule.
```

**END gg28_03 — 下一条请新建独立回复**
