# ROAM — OpenReview 英文回复总稿

以下为与修订论文对应的 21 个回复块。分别复制 Title 和 Comment 代码块；外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。

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
