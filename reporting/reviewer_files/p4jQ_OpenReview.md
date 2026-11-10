# ROAM — OpenReview 英文回复总稿

以下为与修订论文对应的 21 个回复块。分别复制 Title 和 Comment 代码块；外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。

---

## p4jQ_00 | p4jQ

Title 字段（33 characters）：

```text
Thank you letter to Reviewer p4jQ
```

Comment 字段（564 characters，LF；CRLF 为 571）：

```markdown
Dear Reviewer p4jQ,

Thank you for recognizing the value of task-aware optimization and for identifying the implementation and attribution details needed to assess it. We have addressed your four concerns in the revised manuscript: the initializer fit and descriptor–geometry connection, direct metric search under defined budgets, the stored curvature representation and solve, and an explicit temporal-classification extension.

The responses below give the measured outcomes, comparison budgets, and corresponding manuscript sections.

Best regards,
The Authors
```

**END p4jQ_00 — 下一条请新建独立回复**

---

## p4jQ_01 | p4jQ

Title 字段（106 characters）：

```text
Response to Weakness 1 and the corresponding Question: initializer fitting and the role of task statistics
```

Comment 字段（2554 characters，LF；CRLF 为 2570）：

```markdown
Thank you for identifying the missing distinction between choosing metric controls and estimating curvature. Sections 3.1–3.2 and Appendix D.3 now specify both stages.

**What the descriptor determines.** For block $b$,
$$
G_b=\\alpha_b[(\\lambda_b+\\delta)I+\\omega_b\\widehat F_b+(1-\\omega_b)D_b].
$$
The descriptor initializes block scales, damping, curvature mixtures, phase thresholds, and exploration settings. The current model, parameterization, loss, and batch enter through $\\widehat F_b$ and $D_b$. Identical data descriptors therefore do not imply identical parameter-space metrics for different models. Initial gradient disagreement is itself model-dependent.

**How the initializer is fitted.** The supplementary DLinear calibration uses eight source tasks: ETTh1 and ETTm1 at horizons 96, 192, 336, and 720. Each evaluates 16 candidates for 1,000 updates, with source validation every 200 updates. Let $z_k$ be the selected controls in latent coordinates and $\\widetilde c_k$ the source-standardized descriptors. The fit is
$$
\\min_{W,b}\\sum_k\\|W\\widetilde c_k+b-z_k\\|_2^2+\\|W\\|_F^2.
$$
The ridge coefficient is one and the intercept is unpenalized. Domain transforms and safety bounds yield feasible controls. Coefficients and feature normalization are frozen for held-out ETTh2/ETTm2; the target population adapts controls, not $W,b$. The initializer dimension follows the model partition. This objective predicts source-validation-selected controls, rather than minimizing the theorem's alignment bound.

**Why the statistics can help.** For a centered linear lag predictor under squared loss, $K=2\\mathbb E[xx^\\top]$. Under stationarity, lag covariance is determined by autocovariances and their spectral representation. Spectral concentration and seasonality can therefore be informative without identifying the full spectrum. Correlation density summarizes cross-variable dependence, while the SNR proxy and gradient disagreement concern update reliability. Section 3.2 also gives the explicit sensitivity of a positive control to a descriptor through the fitted affine coefficients.

**Empirical assessment.** The original descriptor comparison reports .312 mean MSE with the six descriptors and .328 with random descriptors. The new source-mean/direct-search controls in Section 5.4 and same-state curvature diagnostic in Figure 4 test more specific links in the mechanism. Proposition 1 remains a conditional implication from alignment to conditioning; it does not assert that the affine map always achieves alignment.
```

**END p4jQ_01 — 下一条请新建独立回复**

---

## p4jQ_02 | p4jQ

Title 字段（97 characters）：

```text
Response to Weakness 2 and the corresponding Question: direct metric search under matched budgets
```

Comment 字段（2538 characters，LF；CRLF 为 2562）：

```markdown
Thank you for proposing direct search over the metric parameters. We have added this comparison in Section 5.4, Figure 3, and Appendix L.1.

**Matched target comparison.** All arms use ordinary DLinear, context/horizon 96/96, the same metric family and approximation, initialization-seed pool, switching rule, four-member population, data split, and validation-only checkpoint selection. Only initial controls differ:

- Conditioned: evaluate the frozen source-fitted affine map on the target descriptor.
- Source mean: retain the source-fitted latent intercept and remove the descriptor-dependent term.
- Direct search: initialize four candidates from the same feasible metric-control domains, without the descriptor map.

All three retain the same target population adaptation. Each population receives a 20-second training/validation cap, five evaluation rounds, and 20 model-level validation calls. Entries are mean +/- seed standard deviation over ten seeds.

| Initial controls | ETTh2-96 MSE | ETTm2-96 MSE |
|---|---:|---:|
| Conditioned | .312 +/- .010 | .174 +/- .004 |
| Source mean | .318 +/- .011 | .177 +/- .005 |
| Direct search | .315 +/- .012 | .173 +/- .005 |

Conditioning improves on source mean on both targets. Direct search is slightly stronger on ETTm2, so the result supports a task-dependent initialization benefit rather than universal superiority to metric search. The marginal deviations alone do not establish paired significance.

**Calibration-inclusive comparison.** Source calibration costs 600 seconds. With target adaptation of 20 seconds, the source-plus-target subtotal is 620 seconds for the first task, 80 seconds per task over ten targets, and 26 over 100. Loading, descriptor construction, and final reporting are outside these subtotals. More generally,
$$
\\overline C(N)=C_{\\mathrm{source}}/N+C_{\\mathrm{descriptor}}+C_{\\mathrm{target}}.
$$
Under an equal 620-second subtotal allocation on ETTh2-96, direct search obtains .303 versus .312 for conditioning, averaged over the three matched seeds 0–2. These are separate from the ten-seed target comparison above. Direct search is stronger in this first-task comparison, while source calibration can be shared across repeated deployments.

Source mean retains calibration investment while removing task-specific initialization; direct search tests the same metric family under either the target cap or the calibration-inclusive allocation. These controls separate the value of task information from the compute invested in selecting controls.
```

**END p4jQ_02 — 下一条请新建独立回复**

---

## p4jQ_03 | p4jQ

Title 字段（115 characters）：

```text
Response to Weakness 3 and the corresponding Question: diagonal curvature estimation, solves, and state consistency
```

Comment 字段（2525 characters，LF；CRLF 为 2545）：

```markdown
Thank you for requesting the actual stored representation and solve. Section 3.1 and Appendix D now specify the supplementary implementation concretely.

**Diagonal prediction-Jacobian estimator.** For MSE averaged over $m$ output scalars, set $J=\\sqrt{2/m}\\,\\partial f_\\theta/\\partial\\theta$. Two independent Rademacher output probes give
$$
\\widehat f=\\tfrac12\\sum_{r=1}^{2}(J^\\top v_r)\\odot(J^\\top v_r),\\qquad \\widehat F_b=\\operatorname{diag}(\\widehat f_b).
$$
At fixed parameters and batch, $\\mathbb E[\\widehat f]=\\operatorname{diag}(J^\\top J)$. Reverse-mode vector–Jacobian products avoid materializing the Jacobian or a dense Gram matrix. The stored approximation is diagonal; two probes do not make it a rank-two metric.

The separate term is $D_j=\\operatorname{EMA}(h_j^2)$ with decay .999 and ordinary loss gradient $h$. It is not the same estimator as the prediction-Jacobian construction.

**Explicit solve and cost.**
$$
g_{b,j}=\\frac{h_{b,j}}{\\alpha_b[\\lambda_b+10^{-6}+\\omega_b\\widehat f_{b,j}+(1-\\omega_b)D_{b,j}]}.
$$
The damped denominator is strictly positive. Metric storage and application are $O(n)$, excluding network differentiation. Each refresh adds a forward computation and two reverse-mode probes. L-BFGS separately requires $O(Mn)$ storage and recursion work with $M=10$; the population has four model/optimizer states.

**Refreshes and consistent memory.** The applied metric is refreshed initially and every 100 updates, and frozen between refreshes while $D$ accumulates. A metric or control change clears curvature memory and restarts Phase I. Curvature pairs use the same batch before and after a step under the same frozen metric. Diagnostics use two additional independent batches every ten updates, with three successful checks for entry and three failures for exit.

The supplementary forecasting runs use ordinary weights, additive retraction, and identity coordinate transport. They activate no Stiefel or SPD parameter constraints. Appendix C separately describes the restricted tangent-space solve needed for constrained configurations.

The added implementation specification is identified with the supplementary experiments. The original benchmark cost table and the supplementary population cap retain separate scopes; a per-epoch measurement or plateau time is not substituted for population-wide compute. Code is available in `roam/optimizer.py` and `docs/IMPLEMENTATION.md` in the [anonymous repository](https://anonymous.4open.science/r/ROAM-D935/).
```

**END p4jQ_03 — 下一条请新建独立回复**

---

## p4jQ_04 | p4jQ

Title 字段（89 characters）：

```text
Response to Weakness 4 and the corresponding Question: a defined classification extension
```

Comment 字段（2374 characters，LF；CRLF 为 2394）：

```markdown
Thank you for suggesting evaluation beyond regression. We have added a subject-disjoint UCI HAR classification extension in Appendix L.5, Table 26, and Figure 16, with a main-text summary in Section 5.7.

**Loss and descriptor changes.** For softmax cross-entropy, logit curvature is $\\operatorname{diag}(p)-pp^\\top$, giving
$$
F=J^\\top[\\operatorname{diag}(p)-pp^\\top]J.
$$
The implementation estimates its nonnegative diagonal using sampled softmax labels and independent signs across examples. SNR, spectral entropy, seasonal concentration, and correlation density are averaged over training windows; gradient disagreement uses the classification loss. There is no forecast horizon, so $H/T$ is set to zero and a separate initializer is fitted.

**Subject separation and model.** We use the official held-out test subjects and a fixed CNN with two 32-channel convolutional layers, GELU, temporal averaging, and a six-class head. Twenty percent of official training subjects form target validation. Six internal source splits, each comparing eight candidates for 500 updates, use only the remaining training subjects. Neither target validation nor test subjects enter source calibration. The model has three optimizer blocks and ordinary weights.

**Results.** Four population arms share a 30-second target cap, five rounds, 20 model-level validation calls, batch size 64, and ten reporting seeds. Source calibration is separate. AdamW uses a distinct 1,500-update allocation. Accuracy deviations are percentage points.

| Method | Accuracy (%) | Cross-entropy | Budget |
|---|---:|---:|---|
| Conditioned ROAM | 92.8 +/- .6 | .215 +/- .018 | 30 s / 20 calls |
| Source mean | 92.3 +/- .7 | .232 +/- .020 | 30 s / 20 calls |
| Direct metric search | 93.1 +/- .6 | .207 +/- .017 | 30 s / 20 calls |
| Continuous blend | 92.9 +/- .6 | .212 +/- .018 | 30 s / 20 calls |
| AdamW reference | 93.5 +/- .5 | .194 +/- .016 | 1,500 updates |

Conditioning improves over source mean in both metrics, while direct search and blending have higher mean accuracy. The separately budgeted AdamW reference is also stronger. The extension demonstrates the loss interface and descriptor convention on temporal classification, using internal subject splits for calibration. Its scope is this dataset and classifier; the table identifies the stronger reference outcomes and their budgets.
```

**END p4jQ_04 — 下一条请新建独立回复**
