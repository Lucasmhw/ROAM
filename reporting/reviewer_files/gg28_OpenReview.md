# ROAM — OpenReview 英文回复总稿

以下为与修订论文对应的 21 个回复块。分别复制 Title 和 Comment 代码块；外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。

---

## gg28_00 | gg28

Title 字段（33 characters）：

```text
Thank you letter to Reviewer gg28
```

Comment 字段（687 characters，LF；CRLF 为 694）：

```markdown
Dear Reviewer gg28,

Thank you for recognizing the breadth of the forecasting evaluation and for asking for a clearer link between task information, realized geometry, and optimization behavior. We have strengthened that link with an explicit initializer fit, a same-state curvature diagnostic, and same-family search controls, while retaining the assumptions of the local theory.

We have also expanded the comparison with learned Riemannian optimization and added a safeguarded continuous-blending control. The revised manuscript presents discrete switching as an interpretable policy with an observed trade-off, rather than a theoretically necessary choice.

Best regards,
The Authors
```

**END gg28_00 — 下一条请新建独立回复**

---

## gg28_01 | gg28

Title 字段（98 characters）：

```text
Response to Weakness 1 and Question 1: task information, model dependence, and empirical alignment
```

Comment 字段（2564 characters，LF；CRLF 为 2581）：

```markdown
Thank you for distinguishing the conditional alignment result from the mechanism that constructs a metric. Sections 3–4 and Figure 1 now make this separation explicit.

**Information path.** The descriptor initializes control coordinates. The metric also includes $\\widehat F_b(\\theta)$ and $D_b(\\theta)$ computed from the instantiated model and training loss. For general losses, Gauss–Newton curvature contains both the model Jacobian and output-loss curvature. Initial gradient disagreement is already model-dependent, and the block partition and initializer dimensions follow the backbone. Six scalars are not intended to replace these dependencies.

For a centered linear lag predictor, $K=2\\mathbb E[xx^\\top]$ gives a precise connection between lag covariance and curvature; stationarity connects that covariance to the full spectrum. Spectral summaries can be useful without identifying extreme eigenvalues or eigendirections. Section 3.2 gives the source-fitting objective and the explicit derivative of positive controls with respect to descriptor coordinates.

**What is measured.** Section 5.4 compares conditioned, source-mean, and direct-search initialization within the same model, metric family, and target budget. The same-state diagnostic evaluates metrics at a common initialization and full training design, before different trajectories can confound the comparison.

| Initial metric | ETTh2-96 positive-spectrum ratio | ETTm2-96 positive-spectrum ratio |
|---|---:|---:|
| Identity | 800 | 410 |
| Default controls | 760 | 385 |
| Source mean | 720 | 390 |
| Conditioned | 640 | 375 |

Figure 4 and Appendix L.3 report this diagnostic without treating the redundant DLinear Hessian as positive definite. With a full-rank identifiable design, the two-map model's positive rank and nullity are each $H(T+1)$, or 9,312 for $T=H=96$. This is a conditional dimension calculation; the ETTh2 design-rank measurement (97 at tolerance $10^{-10}$) is stated separately in the exact-solve experiment.

The lower positive-spectrum ratios support improved geometry on observable directions in these settings. They do not prove the spectral sandwich in Proposition 1 or explain the entire test-error gain. The revised Section 4 attributes the classical result and makes its positive-definiteness/coupling assumptions explicit; it makes no convergence claim for the complete switched, stochastic, population-adapted algorithm. Together, the controls and diagnostics supply a testable bridge without asserting a universal descriptor-to-curvature theorem.
```

**END gg28_01 — 下一条请新建独立回复**

---

## gg28_02 | gg28

Title 字段（85 characters）：

```text
Response to Weakness 2: novelty and the relationship to learned Riemannian optimizers
```

Comment 字段（2623 characters，LF；CRLF 为 2633）：

```markdown
Thank you for requesting a clearer distinction from existing optimizers and learned Riemannian optimization. The revised Section 2 attributes the established ingredients and states the contribution at the level of task-conditioned control.

Gauss–Newton/Fisher preconditioning, second-moment estimation, momentum, L-BFGS, manifold operations, and PBT are not new individually. The revised text cites preconditioned product-manifold metrics by [Gao, Peng, and Yuan](https://arxiv.org/abs/2306.08873), gradient-noise-scale work by [McCandlish et al.](https://arxiv.org/abs/1812.06162), and stochastic quasi-Newton safeguards by [Bollapragada et al.](https://proceedings.mlr.press/v80/bollapragada18a.html).

[Learning to Optimize on Riemannian Manifolds](https://wu-yuwei-bit.github.io/paper/TPAMI2023_Gao_Learning_to_Optimize.pdf) parameterizes a Riemannian optimizer with a recurrent network and trains it through meta-optimization, including an implicit-differentiation scheme. ROAM instead retains a prescribed metric/update family and fits a compact affine map from explicit task statistics to its control coordinates, followed by derivative-free population adaptation. Its source fitting is itself a form of learning; we do not contrast it with learned optimization as if it had no training cost.

The practical distinction is inspectability. Descriptor inputs have stated data dependencies; control coordinates have meanings such as block scale, damping, curvature mixture, and phase threshold; the realized metric also uses current model derivatives. Section 3.2 now gives the fit and descriptor-to-control sensitivity. Individual descriptor removal, removal of the descriptor term while retaining the source intercept, and direct search over the same family are explicit interventions on this interface.

The original factorial reports the largest mean marginal effect for the metric (.01025 versus .00475 for switching and .00525 for outer adaptation). The added source-mean/direct-search results further delimit the role of task information: conditioning improves on source mean on both forecasting targets, but direct search can match or exceed it and is stronger in the first-task cost comparison.

Thus our contribution is a transparent task-conditioning mechanism for forecasting optimization, supported by competitive prediction results and controlled attribution tests. The revision does not claim that all metric ingredients are novel or that this interface universally outperforms recurrent learned optimizers. A direct matched evaluation against such optimizers would answer a separate empirical question.
```

**END gg28_02 — 下一条请新建独立回复**

---

## gg28_03 | gg28

Title 字段（80 characters）：

```text
Response to Question 2: discrete switching versus a safeguarded continuous blend
```

Comment 字段（2452 characters，LF；CRLF 为 2474）：

```markdown
Thank you for proposing continuous blending. We have added a defined, safeguarded comparator in Appendix L.4, Table 25, and Figure 15, with a main-text summary.

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

Update counts sum across the four members; deviations are seed standard deviations. Switching is slightly stronger on ETTh2, blending on ETTm2. These small differences are not paired significance claims. The figure plots validation progress by evaluation round, without relabeling rounds as elapsed time.

If two directions descend for the same objective at the same point, their convex combination also descends. We therefore do not claim blending is intrinsically unstable. Momentum and stochastic estimates need not satisfy that premise, so both policies need safeguards. The result supports a work–accuracy trade-off for this specified blend, not universal superiority of switching. The revised text presents the discrete policy as a practical default with an explicit eligibility rule.
```

**END gg28_03 — 下一条请新建独立回复**
