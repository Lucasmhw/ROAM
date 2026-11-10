# ROAM — OpenReview 英文回复总稿

以下为与修订论文对应的 21 个回复块。分别复制 Title 和 Comment 代码块；外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。

---

## 00_general | All reviewers

Title 字段（52 characters）：

```text
Thank you letter to the Area Chair and all reviewers
```

Comment 字段（1991 characters，LF；CRLF 为 2004）：

```markdown
Dear Area Chair and Reviewers,

Thank you for your careful evaluation of ROAM. We have revised the manuscript to make the task-conditioned mechanism explicit and to connect each empirical claim to the comparison that supports it. Substantive changes are selectively highlighted in yellow; the main text is ten pages in the official ICLR 2027 format.

The revision now specifies source-task fitting of the affine initializer, the diagonal curvature estimator and metric solve, and the active configurations of the complete factorial. It also attributes the classical optimization ingredients and states the conditional scope of the local analysis consistently in the main text and appendix.

The added experiments address the principal attribution questions. Conditioned initialization improves on source-mean controls on both forecasting targets, while direct search is competitive and stronger under the first-task calibration-inclusive allocation. An unchanged-objective DLinear study separates finite-budget training and checkpoint effects from the exact least-squares optimum. Same-state curvature diagnostics, a continuous-blending control, and a subject-disjoint classification extension further test the mechanism and its scope.

We have corrected the transfer visualization from its four documented table entries, regenerated the descriptor plot on a common aggregation basis, and supplied numerical reporting inputs and figure-generation code. The anonymous implementation and reporting package are available at [ROAM](https://anonymous.4open.science/r/ROAM-D935/).

The broad forecasting results remain strong: lower MSE in all 35 dataset–backbone aggregates, with 4.8%–7.3% lower macro MSE by backbone. The revised presentation distinguishes those observations from the stronger optimizer comparisons, the targeted controls, and the conditional mathematical analysis. We hope these concrete changes make the contribution and its limits easier to assess.

Best regards,
The Authors
```

**END 00_general — 下一条请新建独立回复**

---

## p4jQ_00 | p4jQ

Title 字段（33 characters）：

```text
Thank you letter to Reviewer p4jQ
```

Comment 字段（697 characters，LF；CRLF 为 704）：

```markdown
Dear Reviewer p4jQ,

Thank you for recognizing the value of task-aware optimization and for identifying the implementation and attribution details needed to assess it. We have addressed your four concerns in the revised manuscript: the initializer fit and descriptor–geometry connection, direct metric search under defined budgets, the stored curvature representation and solve, and an explicit temporal-classification extension.

The responses below give the results and point to the corresponding sections. We have retained the distinction between improved mean performance in a particular comparison and a universal advantage over alternative optimization strategies.

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

Comment 字段（2485 characters，LF；CRLF 为 2509）：

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
Under an equal 620-second subtotal allocation on ETTh2-96, direct search obtains .303 versus .312 for conditioning. We report this outcome explicitly: direct search is stronger in that cold-start comparison, while source calibration can be shared across repeated deployments.

The revision distinguishes a matched target-adaptation budget from a first-task efficiency claim. Source mean is also informative because it retains calibration investment while removing task-specific initialization. Neither a scalar-learning-rate search nor identity plus PBT would isolate these questions as directly.
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

Comment 字段（2411 characters，LF；CRLF 为 2431）：

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

Conditioning improves over source mean in both metrics, while direct search and blending have higher mean accuracy. The separately budgeted AdamW reference is also stronger. The extension demonstrates that the loss interface and descriptor convention are usable for temporal classification; it does not establish the best classification optimizer or universal cross-domain transfer. The source tasks here are internal subject splits, not an external meta-training corpus.
```

**END p4jQ_04 — 下一条请新建独立回复**

---

## BKGG_00 | BKGG

Title 字段（33 characters）：

```text
Thank you letter to Reviewer BKGG
```

Comment 字段（591 characters，LF；CRLF 为 598）：

```markdown
Dear Reviewer BKGG,

Thank you for identifying the presentation details needed to follow the method. We have made the descriptor-to-control relationship explicit, added the source-fitting objective and numerical curvature estimator, and expanded the factorial into an eight-row configuration table with named task–backbone settings.

Figure 1 now traces source calibration, target descriptors, online model derivatives, and validation adaptation separately. The responses below address each of your three concerns and point to the revised definitions and evidence.

Best regards,
The Authors
```

**END BKGG_00 — 下一条请新建独立回复**

---

## BKGG_01 | BKGG

Title 字段（105 characters）：

```text
Response to Weakness 1 and the corresponding Question: why temporal statistics can inform metric controls
```

Comment 字段（2225 characters，LF；CRLF 为 2241）：

```markdown
Thank you for asking why data-level descriptors can be relevant to parameter-space optimization. Sections 3.1–3.2 now separate the motivation for conditioning from the model-dependent curvature construction.

For a centered linear lag predictor with squared loss,
$$
K=2\\mathbb E[xx^\\top].
$$
Under stationarity, entries of this lag covariance are autocovariances, which have a spectral representation. Spectral entropy and seasonal concentration can therefore summarize information related to conditioning. Cross-variable correlation density summarizes another part of the input covariance structure. The SNR proxy and initial gradient disagreement instead concern the reliability of stochastic updates, and $H/T$ describes the prediction task.

These are informative summaries, not sufficient statistics for a general Hessian. ROAM uses them to select block scales, damping, curvature mixtures, and phase controls. The actual metric also contains online prediction derivatives and gradient second moments from the instantiated model. Thus model architecture, parameterization, and loss remain part of the geometry even when the data descriptors are unchanged.

The revised initializer fit predicts source-validation-selected controls. Its affine form makes descriptor influence inspectable: before safety clipping, a positive control $\\alpha_b=\\operatorname{softplus}(z_b)$ satisfies
$$
\\frac{\\partial\\alpha_b}{\\partial c_i}=\\operatorname{sigmoid}(z_b)\\frac{W_{bi}}{s_i},
$$
where $s_i$ is the source-feature scale. This expresses the direction and local sensitivity of a control to each descriptor; it is not a theorem that the resulting metric must align with curvature.

The empirical evidence tests separate links. Random descriptors give .328 mean MSE versus .312 for the six descriptors; removing individual descriptors gives .315–.319. The new source-mean/direct-search experiment in Section 5.4 isolates task-specific initialization within the same metric family. Figure 4 then compares the realized positive-spectrum conditioning at the same initial model state. This connects interpretable inputs, model-dependent operators, and observed behavior without assuming that six scalars reconstruct a Hessian.
```

**END BKGG_01 — 下一条请新建独立回复**

---

## BKGG_02 | BKGG

Title 字段（111 characters）：

```text
Response to Weakness 2 and the corresponding Question: explicit computation of the proxy and affine initializer
```

Comment 字段（2025 characters，LF；CRLF 为 2044）：

```markdown
Thank you for pointing out the missing numerical definitions. We have added both the fitting objective and the concrete curvature realization in Section 3 and Appendix D.

**Initializer.** The supplementary DLinear source set is ETTh1/ETTm1 at horizons 96/192/336/720. Each of eight sources compares 16 control candidates trained for 1,000 updates, with validation every 200 updates. The selected latent controls $z_k$ are fitted from featurewise standardized source descriptors by
$$
\\min_{W,b}\\sum_k\\|W\\widetilde c_k+b-z_k\\|_2^2+\\|W\\|_F^2.
$$
The ridge coefficient is one; the intercept is unpenalized. Coefficients and source normalization are frozen for held-out ETTh2/ETTm2. The initializer export records coefficients, scales, source identities, and block count. The target population updates controls, not this fitted map.

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

Title 字段（100 characters）：

```text
Response to Weakness 3 and the corresponding Question: an explicit reading of the complete factorial
```

Comment 字段（2509 characters，LF；CRLF 为 2535）：

```markdown
Thank you for requesting a readable definition of the complete factorial. We have expanded Table 3 and Appendix F to state the active configuration in every row and to name the task–backbone settings.

**Switch definitions.** $M=1$ enables the task metric; $M=0$ uses identity. $S=1$ enables state-triggered Phase I/L-BFGS transitions; $S=0$ retains Phase I. $O=1$ enables validation-driven population replacement and perturbation of active controls; $O=0$ freezes initialized controls. Removing online adaptation does not itself remove descriptor-based initialization.

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
The switching and outer effects are .00475 and .00525. They average four on/off contrasts; they are neither percentages nor additive pieces that must sum to the .021 full-versus-base reduction. Figure 6 visualizes these descriptive effects without inferring uncertainty from rounded means.

**Named settings and scope.** The settings are ETTh1-192/iTransformer, ETTm1-336/PatchTST, and Weather-192/TimeMixer. The first horizon is 192, whereas tournament setting A in Table 2 uses 96. Both captions now make this explicit.

The separate fixed-identity-plus-PBT control rounds to .326 and is not substituted for the .327 O-only cell. Table 6 separately reports ordinary-weight, Stiefel, and SPD-eligible interventions; changing parameter constraints is a distinct structural intervention, not an implicit consequence of changing the optimizer metric. These distinctions keep the factorial interpretation specific to its declared components and populations.
```

**END BKGG_03 — 下一条请新建独立回复**

---

## esdH_00 | esdH

Title 字段（33 characters）：

```text
Thank you letter to Reviewer esdH
```

Comment 字段（734 characters，LF；CRLF 为 741）：

```markdown
Dear Reviewer esdH,

Thank you for checking the numerical presentation and mathematical assumptions so carefully. Your review identified substantive issues that have directly shaped the revision. We have corrected the transfer plot, clarified aggregation and setting labels, linked the implementation and numerical reporting package, and added an unchanged-objective DLinear comparison with exact least-squares and ridge references.

We have also made the classical attribution and singular-Hessian limitation explicit in the main text, and added the missing optimization references. The replies below distinguish these completed manuscript changes from the particular experimental conclusions they support.

Best regards,
The Authors
```

**END esdH_00 — 下一条请新建独立回复**

---

## esdH_01 | esdH

Title 字段（84 characters）：

```text
Response to Weakness 1, part 1: transfer-cell consistency and aggregation provenance
```

Comment 字段（2117 characters，LF；CRLF 为 2134）：

```markdown
Thank you for identifying the cell-wise inconsistency. You are correct: the distinction between a 12-transfer mean and displayed cells cannot explain different values for the same named source–target pair.

**The transfer plot has been corrected.** Figure 8 now uses the four individually reported pairs in Table 19, with explicit source and target keys:

| Source to target | Standard MSE | ROAM MSE | Recomputed reduction |
|---|---:|---:|---:|
| ETTh1 to ETTh2 | .421 | .392 | 6.89% |
| ETTm1 to Weather | .286 | .271 | 5.24% |
| Weather to ECL | .201 | .189 | 5.97% |
| ECL to Exchange | .462 | .437 | 5.41% |

Each percentage is $100(1-\\mathrm{MSE}_R/\\mathrm{MSE}_B)$. The other cells are marked NR, not zero. The 12-transfer aggregate remains separate; its .342/.322 pair does not determine the eight unreported individual pairs. The correction reconciles the displayed figure with the table without inventing those observations or assigning a speculative internal cause to the old plot.

**Aggregation is now explicit.** The Weather-192/TimeMixer value .232 in Table 2 is horizon-specific, whereas .232 in Table 9 averages four horizons. Equality after three-decimal rounding is possible, but the scopes must remain distinct. The revision labels them separately and gives the macro-aggregation formula in Appendix E. The supplied reporting inputs preserve each scope rather than reconstructing individual horizons from a mean. Lion .243 and the standard-recipe .245 also refer to different optimizer summaries.

**Backbone labels are complete.** Table 12 now names ETTh1-192/iTransformer, ETTm1-336/PatchTST, and Weather-192/TimeMixer. The 192-versus-96 difference between its setting A and tournament setting A is explicit.

We also regenerated Figure 13 from Table 14 using the common reference .312. The reporting package includes the numerical inputs and plotting code, and Appendix L.6 maps experiments to artifacts. These are deterministic consistency corrections; the main forecasting claim continues to rest on the 35 dataset–backbone benchmark cells and the separately identified optimizer controls.
```

**END esdH_01 — 下一条请新建独立回复**

---

## esdH_02 | esdH

Title 字段（80 characters）：

```text
Response to Weakness 1, part 2: anonymous code and a reproducible evidence trail
```

Comment 字段（2505 characters，LF；CRLF 为 2525）：

```markdown
Thank you for emphasizing reproducibility. The revised Reproducibility Statement and Appendix L.6 now link the [anonymous ROAM repository](https://anonymous.4open.science/r/ROAM-D935/) and map the implementation to the results.

The release contains the ordinary-parameter optimizer, descriptor construction, source-calibrated initializer, diagonal metric estimator, phase safeguards, and supplementary experiment entry points:

| Question | Implementation / entry point |
|---|---|
| Initializer fit | `roam/controls.py`; `scripts/run_suite.py` |
| Metric representation and solve | `roam/optimizer.py`; `docs/IMPLEMENTATION.md` |
| Direct metric search and cost | `run_suite.py`; `coldstart_compare.py` |
| Fixed convex objective | `convex_zero_decay.py`; `exact_dlinear.py` |
| Classification | `classification_suite.py` |
| Same-state curvature | `curvature_diagnostic.py` |
| Run-record checks | `aggregate_results.py`; `audit_records.py`; `verify_checkpoints.py` |

The reporting package additionally provides the completed experimental summaries, `reporting/figures/figure_data.json`, the figure generator, and the revised responses. The added numerical plots are generated from that common reporting data. The four transfer gains and descriptor percentages are recomputed directly from the stated rounded table entries.

The release distinguishes reporting summaries from generated training artifacts. Running the documented experiment commands produces per-run records, fitted coefficients, checkpoints, and logs under `results/`; these are different artifacts from the supplied aggregate tables. The optional adapters for four additional forecasting backbones are integration entry points, not a claim that their smoke tests reproduce the full benchmark.

Appendix D.3 specifies the supplementary environment, model blocks, source/target split, loss normalization, refresh/reset policy, population accounting, and checkpoint selection. The target cap counts all members, probes, diagnostics, line searches, and validation, while source fitting and other excluded costs have separate scopes. A plateau-time figure is not used as a population-wide compute ledger.

These additions make the implementation and the arithmetic behind the displayed results inspectable. We have not inferred per-seed records or paired significance from marginal summary statistics, and the revised manuscript does not use the presence of source code as a substitute for identifying which result each protocol produces.
```

**END esdH_02 — 下一条请新建独立回复**

---

## esdH_03 | esdH

Title 字段（102 characters）：

```text
Response to Weakness 2, part 1: convexity, finite-budget geometry, and the meaning of the DLinear gain
```

Comment 字段（1759 characters，LF；CRLF 为 1770）：

```markdown
We agree with the central convexity point. With fixed moving-average decomposition $S$ and ordinary affine maps,
$$
\\widehat y=W_{\\rm tr}Sx+W_{\\rm se}(I-S)x+b_{\\rm tr}+b_{\\rm se}
=W_{\\rm eff}x+b_{\\rm eff}.
$$
Unregularized MSE is a convex quadratic in the weights, with redundancy in the two-map parameterization. An invertible SPD metric does not change the stationary set or the attainable training minimum of this fixed objective.

The revised Section 5.6 states this explicitly. The benefit under a finite training allocation can instead concern the trajectory, stochastic noise amplification, and validation-selected stopping point. These are affected by geometry even though the limiting training optimum is unchanged. Better test performance is also not equivalent to a smaller training optimum.

To distinguish these possibilities, we have added the same-objective experiment in Appendix L.2. It fixes ordinary DLinear, decomposition, normalization, data split, and zero regularization for both optimizers; tunes learning rates on a separate validation seed; and compares 2,000-update ROAM with 2,000- and 10,000-update AdamW. Exact least squares supplies the training reference, while validation-selected ridge supplies a separate predictive reference.

The results are consistent with this interpretation. At 2,000 updates, ROAM has a smaller training gap than AdamW; extended AdamW gets closer to the exact minimum, yet ROAM's validation-selected checkpoint has lower test MSE. Ridge has lower ETTh2-96 test MSE still. We therefore do not attribute the original 7.3% macro improvement to finding a better convex optimum or to changing the predictor. The numerical details follow in the next response and are now in Tables 22–23 and Figure 5.
```

**END esdH_03 — 下一条请新建独立回复**

---

## esdH_04 | esdH

Title 字段（95 characters）：

```text
Response to Weakness 2, part 2: matched DLinear retraining and an exact least-squares reference
```

Comment 字段（2428 characters，LF；CRLF 为 2454）：

```markdown
We have completed and incorporated an unchanged-objective DLinear comparison in Section 5.6 and Appendix L.2.

**Protocol.** Ordinary DLinear, context 96, all seven ETT channels, fixed decomposition, identical chronological splits and training-only normalization, and zero regularization are shared. Both optimizers select a learning rate from $\\{10^{-4},3\\times10^{-4},10^{-3},3\\times10^{-3},10^{-2}\\}$ using validation seed 2027, followed by ten reporting seeds. ROAM receives 2,000 updates; AdamW receives 2,000 and 10,000. These allocations do not imply equal wall-clock cost.

**Exact reference.** We solve the equivalent identifiable shared affine predictor in float64, pooling windows and channels and including an intercept. On ETTh2-96 the design has rank 97 at relative tolerance $10^{-10}$. The residual $\\|(A^\\top A/n)U-A^\\top Y/n\\|_F$ is $2.1\\times10^{-13}$; this is an absolute residual of sample-normalized equations.

| Method | Final training MSE | Validation-selected test MSE |
|---|---:|---:|
| AdamW, 2,000 updates | .2270 +/- .0015 | .330 +/- .012 |
| AdamW, 10,000 updates | .2205 +/- .0003 | .322 +/- .010 |
| ROAM, 2,000 updates | .2213 +/- .0006 | .312 +/- .010 |
| Exact least squares | .2200 | .326 |
| Validation-selected ridge | .2220 | .310 |

Iterative deviations are seed standard deviations. Exact/ridge solutions are deterministic for the fixed split and solver. Ridge changes the objective and is not included in a claim about the unregularized training minimum. Final training losses and validation-selected test losses use their stated, different checkpoint rules.

| Horizon | AdamW 2k | AdamW 10k | ROAM 2k |
|---:|---:|---:|---:|
| 96 | .330 | .322 | .312 |
| 192 | .401 | .388 | .380 |
| 336 | .445 | .434 | .430 |
| 720 | .481 | .469 | .464 |
| Mean | .41425 | .40325 | .39650 |

Extended AdamW improves its four-horizon test average, narrowing the gap. On ETTh2-96 it is closer to the exact training minimum, but ROAM has lower selected test MSE. The results separate convergence from prediction and support a finite-time trajectory/checkpoint interpretation. They do not show a lower convex optimum or optimal test risk.

These supplementary zero-decay results retain a distinct protocol from the original Table 11 benchmark; they are not presented as a reconstruction of its .469/.421 values. Figure 5 now displays full-training gaps and validation trajectories separately.
```

**END esdH_04 — 下一条请新建独立回复**

---

## esdH_05 | esdH

Title 字段（79 characters）：

```text
Response to Weakness 3: the conditional scope and purpose of the local analysis
```

Comment 字段（2278 characters，LF；CRLF 为 2292）：

```markdown
Thank you for distinguishing valid algebra from applicability. We have revised Section 4 to make the classical attribution and conditional scope as explicit as in Appendix A.

**Classical ingredients.** Proposition 1 applies spectral equivalence, the optimal constant-step quadratic contraction factor, and a local expansion. Nocedal and Wright and Absil et al. are now cited at the start of the main-text analysis as well as in the proofs. These ingredients explain the metric mechanism; they are not claimed as new optimization theorems.

**The singular-Hessian limitation.** The relevant operator is the symmetric $G^{-1/2}KG^{-1/2}$. If $K$ is singular and $D\\succ0$, then
$$
D^{-1/2}KD^{-1/2}=I+E
$$
is singular, so $E$ has eigenvalue $-1$ and $\\nu=\\|E\\|_2\\ge1$. If $D$ is singular, the inverse square root in that expression is not defined. Thus the coupled-block result cannot be applied directly to redundant DLinear or a singular neural-network Hessian.

The sentence you highlighted has been replaced with a conditional interpretation: under the stated positive-definiteness and coupling assumptions, the bound separates within-block alignment from neglected coupling; it does not certify the benchmark partitions. The singular-case argument appears immediately after it in the main text.

**Damping and positive-spectrum diagnostics.** Damping makes the metric $G$ invertible, not the loss Hessian $K$. The new same-state DLinear diagnostic reports a positive-spectrum ratio while retaining flat directions in the full parameterization. It is labeled as a diagnostic, not as verification of the nondegenerate-minimum theorem. A regularized operator or a subspace convergence theorem would require its own assumptions.

**Purpose of the analysis.** It identifies alignment, cross-block coupling, and noise amplification as distinct mechanisms, and states what a positive-curvature pair guarantees in a common metric space. It does not prove convergence of NAdam, stochastic L-BFGS, the metric estimator, or the population controller. The direct-search and same-objective controls test empirical questions separately from those conditional implications. This preserves the derivations you checked while removing the overstatement in their main-text interpretation.
```

**END esdH_05 — 下一条请新建独立回复**

---

## esdH_06 | esdH

Title 字段（104 characters）：

```text
Response to Weakness 4: prior-work attribution and the specific contribution of task-conditioned control
```

Comment 字段（2491 characters，LF；CRLF 为 2502）：

```markdown
Thank you for identifying the missing references and sharpening the novelty question. We have added the cited work and revised the related-work and method discussions to attribute the components explicitly.

- [McCandlish et al. (2018)](https://arxiv.org/abs/1812.06162): our gradient-disagreement quantities follow gradient-noise-scale reasoning. The initial descriptor uses ordinary gradients, while the online diagnostic is evaluated under the current metric.
- [Bollapragada et al. (2018)](https://proceedings.mlr.press/v80/bollapragada18a.html): reliable stochastic curvature pairs and safeguarded L-BFGS are established ingredients. Their method progressively increases batch size; our supplementary controller uses fixed-batch diagnostics to gate momentum/quasi-Newton phases.
- [Gao, Peng, and Yuan (2025)](https://arxiv.org/abs/2306.08873): preconditioned product-manifold metrics, including Gauss–Newton constructions, precede ROAM. We do not claim to originate that metric family principle.
- Nocedal and Wright (2006) and Absil et al. (2008): spectral-equivalence, local contraction, and manifold operations provide the foundations of Section 4.

The revised contribution is the explicit forecasting-task-to-control interface and its controlled evaluation. Six interpretable inputs initialize relative block scales, damping, curvature mixtures, and phase controls; online model derivatives realize the metric; validation-based population adaptation updates controls. This is a specified combination with a testable task-conditioning hypothesis, rather than novelty assigned to each ingredient.

The previously missing fitting objective is now in Section 3.2 and Appendix D.3. Source-validation-selected latent controls are fitted by ridge affine regression with coefficient one and an unpenalized intercept, and the fitted map/normalization are frozen on target tasks. Section 5.4 compares this initialization against both the source intercept and direct metric search within the same operator family and target budget, with calibration cost separately charged.

We also discuss [Gao et al., Learning to Optimize on Riemannian Manifolds](https://wu-yuwei-bit.github.io/paper/TPAMI2023_Gao_Learning_to_Optimize.pdf). Their recurrent meta-optimizer learns optimization behavior on manifolds; ROAM predicts controls of a prescribed family from explicit statistics. We do not claim a universal performance or efficiency advantage over learned optimizers without a matched comparison.
```

**END esdH_06 — 下一条请新建独立回复**

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
