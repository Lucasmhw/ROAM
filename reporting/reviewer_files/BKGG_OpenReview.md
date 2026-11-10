# ROAM — OpenReview 英文回复总稿

本文件含 3 个独立回复块。完整总稿为总回复 1 条、p4jQ 4 条、BKGG 3 条、esdH 4 条、gg28 3 条；各审稿人的致谢已并入第一条。分别复制 Title 和 Comment 代码块，外部编号、中文标签及字符统计不属于实际回复。正文中的数学反斜杠已按 OpenReview Markdown 转义。重点结论使用普通 Markdown 加粗，论文位置使用单层加粗下划线，不叠加外层加粗或标题字号。

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
