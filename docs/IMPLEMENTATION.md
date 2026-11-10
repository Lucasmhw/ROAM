# Numerical specification

This repository implements the ordinary-parameter ROAM mechanism and supplies the supplementary experiments used in the revised manuscript and responses. The choices below specify source-task fitting, descriptor normalization, diagonal curvature storage, metric solves, and population budgets. Completed numerical summaries and figure-generation inputs are released in `reporting/`; the original benchmark aggregates have their separately stated experimental scope.

## Six task descriptors

`roam/descriptors.py` implements the definitions in Appendix B in the order `[snr, sent, seas, H/T, dens, gns]`. SNR uses a width-25 moving average with endpoint extension. Spectral entropy uses the normalized non-DC periodogram. The seasonal set consists of the three largest non-DC bins per channel. Density counts absolute training correlations exceeding 0.5. Gradient disagreement uses two independently sampled training batches at the shared initial weights. Feature normalization is across source tasks, not across the entries of one vector. A constant source feature receives scale one.

## Explicit initializer fit

For each of eight source forecasting tasks (ETTh1 and ETTm1, horizons 96/192/336/720), run 16 declared control candidates for 1,000 updates, with validation every 200 updates. Select the control with the best validation checkpoint. Let its inverse-domain-transform be `z_k` and let `c_k` be the training descriptor. Fit

$$
\min_{W,b}\sum_k\|W\widetilde c_k+b-z_k\|_2^2+\|W\|_F^2.
$$

The intercept is unpenalized. `roam/controls.py` stores the resulting W, b, means, scales, block count, and source-task provenance in JSON. Test targets never select the candidate or fit the map. ETTh2 and ETTm2 are excluded from source calibration. The ridge coefficient is fixed at one.

Positive control coordinates use softplus; mixture coordinates use sigmoid. A final safety projection bounds alpha to [0.01,100], damping to [1e-8,10], disagreement threshold to [0.05,20], curvature threshold to [1e-6,1], and perturbation scale to [0.01,1]. Source candidate ranges appear in `scripts/run_suite.py`. All selected and unsuccessful candidates are logged.

## Curvature approximation and solve

For squared error averaged over all `m` output scalars, define the normalized prediction Jacobian `J = sqrt(2/m) d f_theta / d theta`. Two independent Rademacher output probes give a nonnegative diagonal estimate

$$
\widehat f=\frac12\sum_{r=1}^2 (J^T v_r)\odot(J^T v_r),\qquad E[v_rv_r^T]=I.
$$

Its expectation is `diag(J^T J)` for fixed parameters and data. Each vector-Jacobian product uses reverse-mode autodiff; neither J nor a dense Gram matrix is materialized. For classification, the corresponding sketch uses sampled softmax labels and independent signs across examples, yielding a diagonal cross-entropy Fisher estimate in expectation. This is not the squared training gradient, which is tracked separately as D.

For block b, the realized diagonal metric is

$$
G_{b,j}=\alpha_b\{\lambda_b+10^{-6}+\omega_b\widehat f_{b,j}+(1-\omega_b)D_{b,j}\}.
$$

The solve is elementwise division. Metric storage/solve work is O(n), excluding network differentiation; a refresh costs two reverse-mode probes plus a forward pass. D accumulates with decay 0.999. Refreshes occur initially and every 100 updates. Between refreshes the *applied* metric is frozen while D continues to accumulate. Every refresh or control change clears curvature memory and restarts Phase I, requiring a fresh sequence of successful checks. This is a concrete consistency policy under Appendix C.4.

## Inner updates and switching

Phase I follows Eq. (15), including its scalar second moment per block, beta1=0.9, beta2=0.999, and epsilon=1e-8. Identity vector transport and additive retraction apply to ordinary weights.

Diagnostics occur every 10 updates of each member’s own optimizer. A curvature pair uses gradients before and after the same parameter step on the same batch and frozen metric. Two fresh independently sampled batches supply the disagreement diagnostic at the destination iterate. Entry requires three successful checks; exit requires three failures. The accepted-pair threshold is `<s,y>_G >= 1e-4 ||s||_G^2 > 0`. L-BFGS stores ten pairs, uses the current metric inner product, and starts with positive `(<s,y>_G/<y,y>_G) I` scaling. Armijo uses coefficient 1e-4, initial step one, halving, and at most ten trials. A non-descent direction falls back to the metric gradient; a failed line search leaves the weights unchanged and is logged.

The continuous control uses

$$
a_t=\frac{1}{1+\chi_t/\tau_\chi}\frac{\max(\rho_t,0)}{\max(\rho_t,0)+\tau_\rho},\quad p_t=(1-a_t)p_t^{I}+a_tp_t^{II}.
$$

It uses the same accepted-pair memory and Armijo safeguards. Missing valid memory sets the quasi-Newton contribution to zero. This is one specified continuous alternative, not a claim to optimize over all mixtures.

## Population and budget

Four resident members run serially on one GPU. Initial weights and per-step training batches match across members. The best member supplies a replacement for the worst member at each outer round; the other two continue. A replacement copies model weights and resets optimizer state under perturbed controls. This reset policy avoids copying incompatible curvature memory. Positive controls receive multiplicative log-normal perturbations; mixture weights receive a projected additive perturbation. Target comparisons keep the evaluation interval schedule fixed to ensure matching validation-query opportunities.

In direct-search records, `initial_control_candidates` contains the four actual initial controls and overrides the base `initial_controls` argument. Those candidates are also visible in the first four history entries before replacement. The conditioned base argument is unused for these members. Other arms use their declared base plus three perturbations. `scripts/audit_records.py` verifies the recorded initial populations.

The main target test uses a 20-second population training/validation budget with five rounds (20 model-level validation calls), identical batch size 64, and ten matched seeds. The cap is checked at a completed inner update; the final validation round can cause a small measured overrun. Recorded elapsed time and optimizer forward/backward and line-search calls include all four members. Dataset loading, descriptor extraction, initializer fitting, and final reporting evaluations are outside this target cap. Peak CUDA memory is read after those final evaluations: it is a whole-run allocated-memory peak including data and reporting, not incremental optimizer storage or a training-only peak. Validation requests are counted separately from optimizer forward calls. Source calibration is an additional amortizable training/validation cost, not free compute.

The common resource-utility coefficients are zero in the controlled accuracy experiments. Thus all population members rank by the same validation objective. This isolates performance under a fixed resource cap; it is not an evaluation of nonzero resource-penalty tuning.

## Scope

All reported supplementary forecasting runs use ordinary DLinear weights, context 96, all seven channels, training-only normalization, official 12/4/4-month ETT splits, and normalized MSE/MAE. No Stiefel/SPD parameter constraint or additional forecasting layer is enabled. The exact DLinear comparison solves the equivalent identifiable shared affine predictor in float64 and reports its normal-equation residual. Ridge coefficients are selected on validation only.

For the exact reference, the logged residual is the absolute Frobenius norm of `(A.T @ A / n) @ U - A.T @ Y / n`, where rows pool training windows and channels, the design includes an intercept, and `U` is the identifiable predictor. This states the normalization of the normal equations explicitly.

The DLinear modules use the recorded PyTorch version's default `nn.Linear` initialization under the declared seed, rather than initializing every lag coefficient to the same value. Both maps are shared across channels, have biases, and form separate optimizer blocks. All competing arms use that same initialization convention.

The zero-decay convergence control holds the unregularized objective fixed. Both optimizers select their learning rate from [0.0001,0.0003,0.001,0.003,0.01] using seed 2027, then report seeds 0--9. AdamW receives 2,000 and 10,000 updates; ROAM receives 2,000. The separate practical AdamW grid also considers weight decay [0,0.0001,0.001]. AdamW decay is decoupled; the optional ROAM decay argument adds an L2 term to its loss. The same-objective comparison therefore fixes both to zero. Source metric calibration remains fixed throughout. All source, tuning, and reporting records are retained; a repeated configuration can reuse its identical existing run, with that provenance recorded explicitly.

The exact curvature diagnostic reports only the positive spectrum of the full-training Hessian after metric whitening. It does not remove the redundant model's flat directions by asserting that the Hessian is positive definite. The reduced computation is checked against the full per-output matrix and never used to select controls.

Pinned adapters are supplied for iTransformer, PatchTST, TimeMixer, and ModernTCN. Their small smoke-test configurations verify that optimization executes; they are not replications of the manuscript's complete 35-cell benchmark. The supplementary classification experiment is an explicitly specified extension: UCI HAR subject-disjoint splits, cross-entropy, per-window descriptors averaged over training windows, H/T=0, and a separately fitted three-block initializer. It does not establish universal applicability.

The classification predictor uses two temporal convolutions (9 to 32 channels with kernel 7, then 32 to 32 with kernel 5), GELU activations, temporal averaging, and a six-class linear head. There is no batch normalization. Validation uses a 20% subject split of the official training subjects with split seed 2026. Six further 30% subject splits within those remaining training subjects define the source tasks (split seed 42); each split has disjoint training/validation subjects, while different source splits may overlap. Each source task compares eight candidates for 500 updates, evaluating every 100 updates. Its normalization is refitted using only that source task's training subjects. The four target population arms use ten seeds, batch size 64, and five rounds within 30 seconds. AdamW selects its learning rate from [0.0001,0.0003,0.001,0.003] at seed 2027 and receives 1,500 updates, evaluating every 300. Its update budget is separate from the population time budget.
