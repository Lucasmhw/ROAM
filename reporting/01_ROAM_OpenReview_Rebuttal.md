# ROAM — OpenReview 英文回复总稿

本文件含 15 个独立回复块。完整总稿为总回复 1 条、p4jQ 4 条、BKGG 3 条、esdH 4 条、gg28 3 条；各审稿人的致谢已并入第一条。分别复制 Title 和 Comment 代码块，外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。重点结论使用普通 Markdown 加粗，论文位置使用单层加粗下划线，不叠加外层加粗或标题字号。

---

## 00_general | Area Chair and all Reviewers

Title 字段（38 characters）：

```text
Summary of the completed ROAM revision
```

Comment 字段（2230 characters，LF；CRLF 为 2241）：

```markdown
Dear Area Chair and Reviewers,

Thank you for your careful evaluation of ROAM. We have revised the manuscript to connect the task-conditioned mechanism, its mathematical scope, and the experiments that test it. Substantive changes are selectively highlighted in yellow; the main text remains ten pages in the official ICLR 2027 format.

**Forecasting performance and an inspectable mechanism.** ROAM has lower MSE in all 35 dataset–backbone aggregates, with 4.8%–7.3% lower macro MSE by backbone. The revised $\\underline{\\boldsymbol{\\mathsf{Sections\\ 3.1–3.2}}}$ specify how six interpretable statistics initialize metric controls, how source tasks fit this map, and how current model derivatives realize the metric. $\\underline{\\boldsymbol{\\mathsf{Figure\\ 1}}}$ presents the system overview; $\\underline{\\boldsymbol{\\mathsf{Figure\\ 10}}}$ details the source/target information flow.

**Controlled evidence.** $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ compares conditioned initialization, source-mean controls, and direct metric search under stated target and calibration-inclusive allocations. $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.5}}}$ measures geometry at a common initial model state, and $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.6}}}$ separates finite-budget DLinear behavior from its exact training optimum. The continuous-blending and classification studies appear in $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.4}}}$ and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.5}}}$. Together, they identify both the benefits and the scope of task conditioning.

**Numerical consistency and reproducibility.** We corrected the transfer visualization from its four documented entries, regenerated the descriptor plot on a common aggregation basis, and supplied the corresponding reporting inputs and figure-generation code. $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.6}}}$ links each experiment to its configuration and artifacts in the [anonymous release](https://anonymous.4open.science/r/ROAM-D935/). $\\underline{\\boldsymbol{\\mathsf{Section\\ 4}}}$ now states the classical attribution and the assumptions of the local analysis alongside the results.

Best regards,
The Authors
```

**END 00_general — 下一条请新建独立回复**

---

## p4jQ_01 | p4jQ

Title 字段（73 characters）：

```text
Response to p4jQ (1/4): Descriptor-to-metric mechanism and source fitting
```

Comment 字段（2955 characters，LF；CRLF 为 2975）：

```markdown
Dear Reviewer p4jQ, thank you for your thoughtful assessment of task-aware optimization. We address your four concerns below.

**W1: How do descriptors determine the metric, and how is the initializer fitted?**

The revised $\\underline{\\boldsymbol{\\mathsf{Sections\\ 3.1–3.2}}}$ distinguish control selection from model-dependent curvature estimation; $\\underline{\\boldsymbol{\\mathsf{Appendix\\ D.3}}}$ gives the calibration protocol.

**What the descriptor determines.** For block $b$,
$$
G_b=\\alpha_b[(\\lambda_b+\\delta)I+\\omega_b\\widehat F_b+(1-\\omega_b)D_b].
$$
The descriptor initializes block scales, damping, curvature mixtures, phase thresholds, and exploration settings. The current model, parameterization, loss, and batch enter through $\\widehat F_b$ and $D_b$. **The same data descriptors can yield different parameter-space metrics for different models.** Initial gradient disagreement is itself model-dependent.

**How the initializer is fitted.** The supplementary DLinear calibration uses eight source tasks: ETTh1 and ETTm1 at horizons 96, 192, 336, and 720. Each evaluates 16 candidates for 1,000 updates, with source validation every 200 updates. Let $z_k$ be the selected controls in latent coordinates and $\\widetilde c_k$ the source-standardized descriptors. The fit is
$$
\\min_{W,b}\\sum_k\\|W\\widetilde c_k+b-z_k\\|_2^2+\\|W\\|_F^2.
$$
The ridge coefficient is one and the intercept is unpenalized. Domain transforms and safety bounds yield feasible controls. Coefficients and feature normalization are frozen for held-out ETTh2/ETTm2; the target population adapts controls, not $W,b$. The initializer dimension follows the model partition. This objective predicts source-validation-selected controls, rather than minimizing the theorem's alignment bound.

**Why the statistics can help.** For a centered linear lag predictor under squared loss, $K=2\\mathbb E[xx^\\top]$. Under stationarity, lag covariance is determined by autocovariances and their spectral representation. Spectral concentration and seasonality can therefore be informative without identifying the full spectrum. Correlation density summarizes cross-variable dependence, while the SNR proxy and gradient disagreement concern update reliability. $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.2}}}$ also gives the explicit sensitivity of a positive control to a descriptor through the fitted affine coefficients.

**Empirical assessment.** $\\underline{\\boldsymbol{\\mathsf{Table\\ 14}}}$ reports .312 mean MSE with the six descriptors and .328 with random descriptors. The new source-mean/direct-search controls in $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ and same-state curvature diagnostic in $\\underline{\\boldsymbol{\\mathsf{Figure\\ 4}}}$ test more specific links in the mechanism. Proposition 1 remains a conditional implication from alignment to conditioning; it does not assert that the affine map always achieves alignment.
```

**END p4jQ_01 — 下一条请新建独立回复**

---

## p4jQ_02 | p4jQ

Title 字段（65 characters）：

```text
Response to p4jQ (2/4): Direct metric search and calibration cost
```

Comment 字段（2696 characters，LF；CRLF 为 2722）：

```markdown
**W2: What does task conditioning add over direct metric search?**

We have added same-family controls in the revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ and $\\underline{\\boldsymbol{\\mathsf{Figure\\ 3}}}$, with the full protocol in $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.1}}}$.

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

**Conditioning improves on source mean on both targets.** Direct search is slightly stronger on ETTm2, so the result supports a task-dependent initialization benefit rather than universal superiority to metric search. The marginal deviations alone do not establish paired significance.

**Calibration-inclusive comparison.** Source calibration costs 600 seconds. With target adaptation of 20 seconds, the source-plus-target subtotal is 620 seconds for the first task, 80 seconds per task over ten targets, and 26 over 100. Loading, descriptor construction, and final reporting are outside these subtotals. More generally,
$$
\\overline C(N)=C_{\\mathrm{source}}/N+C_{\\mathrm{descriptor}}+C_{\\mathrm{target}}.
$$
Under an equal 620-second subtotal allocation on ETTh2-96, direct search obtains .303 versus .312 for conditioning, averaged over the three matched seeds 0–2. These are separate from the ten-seed target comparison above. **Direct search is stronger for the first task**; source calibration can be shared across repeated deployments.

Source mean retains calibration investment while removing task-specific initialization; direct search tests the same metric family under either the target cap or the calibration-inclusive allocation. These controls separate the value of task information from the compute invested in selecting controls.
```

**END p4jQ_02 — 下一条请新建独立回复**

---

## p4jQ_03 | p4jQ

Title 字段（80 characters）：

```text
Response to p4jQ (3/4): Curvature representation, solve, and implementation cost
```

Comment 字段（2720 characters，LF；CRLF 为 2742）：

```markdown
**W3: What is stored, how is the metric solved, and what does it cost?**

The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.1}}}$ defines the estimator and coordinate-wise solve; $\\underline{\\boldsymbol{\\mathsf{Appendix\\ D}}}$ specifies the supplementary implementation and refresh policy.

**Diagonal prediction-Jacobian estimator.** For MSE averaged over $m$ output scalars, set $J=\\sqrt{2/m}\\,\\partial f_\\theta/\\partial\\theta$. Two independent Rademacher output probes give
$$
\\widehat f=\\tfrac12\\sum_{r=1}^{2}(J^\\top v_r)\\odot(J^\\top v_r),\\qquad \\widehat F_b=\\operatorname{diag}(\\widehat f_b).
$$
At fixed parameters and batch, $\\mathbb E[\\widehat f]=\\operatorname{diag}(J^\\top J)$. Reverse-mode vector–Jacobian products avoid materializing the Jacobian or a dense Gram matrix. **The stored approximation is diagonal**; two probes do not make it a rank-two metric.

The separate term is $D_j=\\operatorname{EMA}(h_j^2)$ with decay .999 and ordinary loss gradient $h$. It is not the same estimator as the prediction-Jacobian construction.

**Explicit solve and cost.**
$$
g_{b,j}=\\frac{h_{b,j}}{\\alpha_b[\\lambda_b+10^{-6}+\\omega_b\\widehat f_{b,j}+(1-\\omega_b)D_{b,j}]}.
$$
The damped denominator is strictly positive. Metric storage and application are $O(n)$, excluding network differentiation. Each refresh adds a forward computation and two reverse-mode probes. L-BFGS separately requires $O(Mn)$ storage and recursion work with $M=10$; the population has four model/optimizer states.

**Refreshes and consistent memory.** The applied metric is refreshed initially and every 100 updates, and frozen between refreshes while $D$ accumulates. A metric or control change clears curvature memory and restarts Phase I. Curvature pairs use the same batch before and after a step under the same frozen metric. Diagnostics use two additional independent batches every ten updates, with three successful checks for entry and three failures for exit.

The supplementary forecasting runs use ordinary weights, additive retraction, and identity coordinate transport. They activate no Stiefel or SPD parameter constraints. $\\underline{\\boldsymbol{\\mathsf{Appendix\\ C}}}$ separately describes the restricted tangent-space solve needed for constrained configurations.

The added implementation specification is identified with the supplementary experiments. The original benchmark cost table and the supplementary population cap retain separate scopes; a per-epoch measurement or plateau time is not substituted for population-wide compute. Code is available in `roam/optimizer.py` and `docs/IMPLEMENTATION.md` in the [anonymous repository](https://anonymous.4open.science/r/ROAM-D935/).
```

**END p4jQ_03 — 下一条请新建独立回复**

---

## p4jQ_04 | p4jQ

Title 字段（64 characters）：

```text
Response to p4jQ (4/4): Subject-disjoint temporal classification
```

Comment 字段（2744 characters，LF；CRLF 为 2770）：

```markdown
**W4: Does the framework extend beyond regression?**

We have added a subject-disjoint UCI HAR classification study [1], summarized in the revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.7}}}$. $\\underline{\\boldsymbol{\\mathsf{Appendix\\ L.5}}}$ specifies the loss interface and splits, with results in $\\underline{\\boldsymbol{\\mathsf{Table\\ 26}}}$ and $\\underline{\\boldsymbol{\\mathsf{Figure\\ 16}}}$.

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

**Conditioning improves over source mean in both metrics**; direct search and blending have higher mean accuracy. The separately budgeted AdamW reference is also stronger. The extension demonstrates the loss interface and descriptor convention on temporal classification, using internal subject splits for calibration. Its scope is this dataset and classifier; the table identifies the stronger reference outcomes and their budgets.

References

[1] Reyes-Ortiz et al. (2013). [Human Activity Recognition Using Smartphones](https://doi.org/10.24432/C54S4K). UCI Machine Learning Repository.
```

**END p4jQ_04 — 下一条请新建独立回复**

---

## BKGG_01 | BKGG

Title 字段（72 characters）：

```text
Response to BKGG (1/3): Descriptor information and optimization geometry
```

Comment 字段（2648 characters，LF；CRLF 为 2668）：

```markdown
Dear Reviewer BKGG, thank you for identifying the details needed to follow the method. We address your three concerns below.

**W1: Why are data-level descriptors relevant to parameter-space geometry?**

The revised $\\underline{\\boldsymbol{\\mathsf{Sections\\ 3.1–3.2}}}$ explain the descriptor-to-control connection. $\\underline{\\boldsymbol{\\mathsf{Figure\\ 1}}}$ gives the system overview, and $\\underline{\\boldsymbol{\\mathsf{Figure\\ 10}}}$ separates source fitting, target descriptors, model derivatives, and validation adaptation.

For a centered linear lag predictor with squared loss,
$$
K=2\\mathbb E[xx^\\top].
$$
Under stationarity, entries of this lag covariance are autocovariances, which have a spectral representation. Spectral entropy and seasonal concentration can therefore summarize information related to conditioning. Cross-variable correlation density summarizes another part of the input covariance structure. The SNR proxy and initial gradient disagreement instead concern the reliability of stochastic updates, and $H/T$ describes the prediction task.

These are informative summaries, not sufficient statistics for a general Hessian. ROAM uses them to select block scales, damping, curvature mixtures, and phase controls. **The actual metric also contains online prediction derivatives and gradient second moments from the instantiated model.** Thus model architecture, parameterization, and loss remain part of the geometry even when the data descriptors are unchanged.

The revised initializer fit predicts source-validation-selected controls. Its affine form makes descriptor influence inspectable: before safety clipping, a positive control $\\alpha_b=\\operatorname{softplus}(z_b)$ satisfies
$$
\\frac{\\partial\\alpha_b}{\\partial c_i}=\\operatorname{sigmoid}(z_b)\\frac{W_{bi}}{s_i},
$$
where $s_i$ is the source-feature scale. This expresses the direction and local sensitivity of a control to each descriptor; it is not a theorem that the resulting metric must align with curvature.

The empirical evidence tests separate links. $\\underline{\\boldsymbol{\\mathsf{Table\\ 14}}}$ reports .328 mean MSE for random descriptors versus .312 for the six descriptors; individual removals give .315–.319. The new source-mean/direct-search experiment in $\\underline{\\boldsymbol{\\mathsf{Section\\ 5.4}}}$ isolates task-specific initialization within the same metric family. $\\underline{\\boldsymbol{\\mathsf{Figure\\ 4}}}$ then compares the realized positive-spectrum conditioning at the same initial model state. This connects interpretable inputs, model-dependent operators, and observed optimization behavior.
```

**END BKGG_01 — 下一条请新建独立回复**

---

## BKGG_02 | BKGG

Title 字段（64 characters）：

```text
Response to BKGG (2/3): Numerical definitions and source fitting
```

Comment 字段（2281 characters，LF；CRLF 为 2302）：

```markdown
**W2: How are the initializer and curvature estimate computed numerically?**

The revised $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.2}}}$ gives the source-fitting objective, and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ D.3}}}$ gives its full protocol. $\\underline{\\boldsymbol{\\mathsf{Section\\ 3.1}}}$ and $\\underline{\\boldsymbol{\\mathsf{Appendix\\ D}}}$ specify the curvature realization and metric solve.

**Initializer.** The supplementary DLinear source set is ETTh1/ETTm1 at horizons 96/192/336/720. Each of eight sources compares 16 control candidates trained for 1,000 updates, with validation every 200 updates. The selected latent controls $z_k$ are fitted from featurewise standardized source descriptors by
$$
\\min_{W,b}\\sum_k\\|W\\widetilde c_k+b-z_k\\|_2^2+\\|W\\|_F^2.
$$
The ridge coefficient is one; the intercept is unpenalized. **Coefficients and source normalization are frozen for held-out ETTh2/ETTm2.** The initializer export records coefficients, scales, source identities, and block count. The target population updates controls, not this fitted map.

**Curvature and solve.** For MSE over $m$ output scalars, $J=\\sqrt{2/m}\\,\\partial f_\\theta/\\partial\\theta$. Two Rademacher probes yield
$$
\\widehat f=\\tfrac12\\sum_{r=1}^2(J^\\top v_r)\\odot(J^\\top v_r),\\quad
\\mathbb E[\\widehat f]=\\operatorname{diag}(J^\\top J).
$$
The stored proxy is diagonal and computed by reverse-mode products. The metric solve divides each ordinary gradient coordinate by
$$
\\alpha_b[\\lambda_b+10^{-6}+\\omega_b\\widehat f_{b,j}+(1-\\omega_b)D_{b,j}],
$$
with $D=\\operatorname{EMA}(h^2)$ and decay .999. This needs $O(n)$ metric storage/application, plus the differentiation cost of the probes.

The applied metric refreshes initially and every 100 updates; metric/control changes reset curvature memory and restart Phase I. Same-batch pairs and two fresh diagnostic batches keep curvature and disagreement measurements distinct. The appendix specifies these choices for the supplementary realization, including its hardware/software environment and data access. `roam/controls.py`, `roam/optimizer.py`, and `docs/IMPLEMENTATION.md` in the [anonymous release](https://anonymous.4open.science/r/ROAM-D935/) provide the corresponding implementation.
```

**END BKGG_02 — 下一条请新建独立回复**

---

## BKGG_03 | BKGG

Title 字段（68 characters）：

```text
Response to BKGG (3/3): Complete factorial and active configurations
```

Comment 字段（2777 characters，LF；CRLF 为 2805）：

```markdown
**W3: What does each factorial configuration activate?**

The revised $\\underline{\\boldsymbol{\\mathsf{Table\\ 3}}}$ states the active configuration in all eight rows; $\\underline{\\boldsymbol{\\mathsf{Appendix\\ F}}}$ names the task–backbone settings and distinguishes the structural controls.

**Switch definitions.** $M=1$ enables the task metric; $M=0$ uses identity. $S=1$ enables state-triggered Phase I/L-BFGS transitions; $S=0$ retains Phase I. $O=1$ enables validation-driven population replacement and perturbation of active controls; $O=0$ freezes initialized controls. **Freezing online adaptation retains descriptor-based initialization.**

| M | S | O | Active configuration | Mean MSE |
|---:|---:|---:|---|---:|
| 0 | 0 | 0 | Identity; Phase I; fixed controls | .333 |
| 1 | 0 | 0 | Task metric; Phase I; fixed controls | .323 |
| 0 | 1 | 0 | Identity; switching; fixed controls | .329 |
| 0 | 0 | 1 | Identity; Phase I; population selection | .327 |
| 1 | 1 | 0 | Task metric; switching; fixed controls | .318 |
| 1 | 0 | 1 | Task metric; Phase I; outer adaptation | .319 |
| 0 | 1 | 1 | Identity; switching; outer adaptation | .324 |
| 1 | 1 | 1 | Task metric; switching; outer adaptation | .312 |

When $M=0$, metric coordinates are inactive; when $S=0$, switching thresholds are inactive. The O-only row denotes population selection, not learning-rate schedule evolution. A population search over unused metric coordinates is not counted as a metric intervention.

**Marginal effects.** For reported cell mean $f(m,s,o)$,
$$
\\Delta_M=\\tfrac14\\sum_{s,o}[f(0,s,o)-f(1,s,o)]
=\\tfrac14(.010+.011+.008+.012)=.01025.
$$
The switching and outer effects are .00475 and .00525, so **the metric has the largest average marginal effect**. They average four on/off contrasts; they are neither percentages nor additive pieces that must sum to the .021 full-versus-base reduction. $\\underline{\\boldsymbol{\\mathsf{Figure\\ 6}}}$ visualizes these descriptive effects without inferring uncertainty from rounded means.

**Named settings and scope.** The settings are ETTh1-192/iTransformer, ETTm1-336/PatchTST, and Weather-192/TimeMixer. The first horizon is 192, whereas tournament setting A in $\\underline{\\boldsymbol{\\mathsf{Table\\ 2}}}$ uses 96. Both captions now make this explicit.

The separate fixed-identity-plus-PBT control rounds to .326 and is not substituted for the .327 O-only cell. $\\underline{\\boldsymbol{\\mathsf{Table\\ 6}}}$ separately reports ordinary-weight, Stiefel, and SPD-eligible interventions; changing parameter constraints is a distinct structural intervention, not an implicit consequence of changing the optimizer metric. These distinctions keep the factorial interpretation specific to its declared components and populations.
```

**END BKGG_03 — 下一条请新建独立回复**

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
