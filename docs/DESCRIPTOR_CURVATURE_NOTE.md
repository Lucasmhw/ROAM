# A conditional illustration of the data-to-curvature connection

This calculation motivates spectral descriptors in an identifiable linear lag predictor. It is not a theorem that the descriptor map aligns the metric of a nonlinear forecasting network, and it does not make a redundant DLinear Hessian positive definite.

Let the centered lag vector be $x_t=(s_t,s_{t-1},\ldots,s_{t-T+1})$ from a weakly stationary scalar process, with autocovariance $r(\ell)$. For the population squared loss $L(w)=\mathbb E[(y_t-w^T x_t)^2]$, the Hessian is

$$
K=2\mathbb E[x_t x_t^T],\qquad K_{ij}=2r(i-j).
$$

Suppose the covariance admits a spectral density $S$ with convention

$$
r(\ell)=\frac{1}{2\pi}\int_{-\pi}^{\pi}S(\omega)e^{\mathrm i\omega\ell}\,d\omega.
$$

For any real vector $u$, substituting this representation into $u^TKu$ gives

$$
u^TKu=\frac{1}{\pi}\int_{-\pi}^{\pi}S(\omega)
\left|\sum_{j=0}^{T-1}u_j e^{\mathrm i j\omega}\right|^2d\omega.
$$

If $0<S_{\min}\le S(\omega)\le S_{\max}<\infty$ almost everywhere, orthogonality of the complex exponentials yields

$$
2S_{\min}\|u\|^2\le u^TKu\le2S_{\max}\|u\|^2,
\qquad \kappa(K)\le S_{\max}/S_{\min}.
$$

This is an explicit conditional link between the full temporal spectrum and loss curvature. Spectral entropy and seasonal concentration summarize the spectrum but do not specify either of its extrema, so the bound cannot be inferred from those two scalars alone. Likewise, a correlation-density scalar does not reconstruct a multivariate covariance matrix. Initial gradient disagreement also depends on labels, the model, and initialization; it should not be treated as a pure input-spectrum statistic.

For DLinear, the fixed moving-average and residual maps transform the lag design. Its two-map parameterization is redundant, so its full Hessian contains flat directions even when the identifiable input-design covariance is positive definite. `scripts/curvature_diagnostic.py` therefore reports a positive-spectrum diagnostic and explicitly preserves that distinction.

For a nonlinear predictor, the Gauss-Newton/Fisher proxy additionally contains the model Jacobian and loss curvature. The descriptor map chooses scalar controls of that family; the proxy supplies parameter-dependent information. Whether the compact controls improve a training regime remains an empirical question evaluated by the source-mean and direct-search comparisons.
