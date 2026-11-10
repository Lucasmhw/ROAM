# Reference environment

These are the software versions recorded for the supplementary training runs. Completed experimental summaries and exported figures are provided in `reporting/`; per-run outputs and model weights are generated under `results/`.

| Component | Recorded version |
|---|---|
| Python | 3.12.3 |
| PyTorch | 2.8.0+cu128 |
| CUDA runtime reported by PyTorch | 12.8 |
| NumPy | 2.3.2 |
| SciPy | 1.18.1 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| pytest | 9.2.0 |
| Matplotlib on the training server | 3.10.5 |
| einops, for optional backbone adapters | 0.8.2 |
| reformer-pytorch, for optional backbone adapters | 1.4.4 |

Training used Ubuntu 22.04 and one NVIDIA RTX 4090. Install a PyTorch build compatible with your GPU environment, then install this repository with `python -m pip install -e .`. Optional plotting and backbone dependencies are listed in the README.

The released manuscript figure exports were generated with Matplotlib 3.11.2 and NumPy 2.5.4. `reporting/figures/generate_figures.py` consumes the completed numerical summaries in the adjacent `figure_data.json`. The separate run-analysis scripts consume experiment records under `results/`.

Population experiments use wall-clock caps. Hardware and software differences can change the number of updates completed within a cap, even with the same seeds. The scripts record actual elapsed time, validation calls, selected checkpoints, and evaluation metrics so that a reproduced run can be checked on its own recorded budget.
