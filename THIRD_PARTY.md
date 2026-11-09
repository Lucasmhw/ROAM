# Sources and attribution

The implementation in `roam/` is provided with explicit references to the manuscript equations. The repository downloads the following independent projects and data; their licenses and terms continue to apply.

| Resource | Source | Pin / usage |
|---|---|---|
| Time-Series-Library | https://github.com/thuml/Time-Series-Library | Commit `4e938a1767106324dd753b2a44832bf870a0252e`; iTransformer, PatchTST, TimeMixer adapters |
| ModernTCN | https://github.com/luodhhh/ModernTCN | Commit `56a9a2c018385cd5acef015378cae7f084d1b11c`; ModernTCN adapter |
| LTSF-Linear | https://github.com/cure-lab/LTSF-Linear | DLinear architecture reference; the small shared-map implementation is supplied in `roam/models.py` |
| ETT | https://github.com/zhouhaoyi/ETDataset | Official CSV files; actual download hashes saved in each data manifest |
| UCI HAR | https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones | Official subject split and inertial windows; CC BY 4.0 dataset |

Related optimization references discussed in the response:

- McCandlish et al., *An Empirical Model of Large-Batch Training*, 2018. https://arxiv.org/abs/1812.06162
- Bollapragada et al., *A Progressive Batching L-BFGS Method for Machine Learning*, ICML 2018. https://proceedings.mlr.press/v80/bollapragada18a.html
- Gao, Peng, and Yuan, *Optimization on Product Manifolds under a Preconditioned Metric*, SIAM Journal on Matrix Analysis and Applications 46(3):1816–1845, 2025. https://doi.org/10.1137/24M1643773 (open preprint: https://arxiv.org/abs/2306.08873)
- Gao et al., *Learning to Optimize on Riemannian Manifolds*, TPAMI 45(5):5935–5952, 2023. https://doi.org/10.1109/TPAMI.2022.3215702

The upstream source archives are not included in the upload bundle. `scripts/fetch_backbones.py` retrieves the pinned revisions and preserves their license files.
