# 实验结果、协议与汇总口径

R2–R6 使用已完成的实验结果。Table 13 的设置为 ETTh1-192/iTransformer、ETTm1-336/PatchTST、Weather-192/TimeMixer。以下保留不同实验的独立定义；相同数值在不同协议中不代表同一条运行记录。

## 同预算初始化器比较

DLinear，context/horizon=96/96，四成员，20 秒 target cap，20 次 model-level validation，10 seeds。

| Initial controls | ETTh2 MSE ± SD | ETTm2 MSE ± SD |
|---|---|---|
| Conditioned | 0.312 ± 0.010 | 0.174 ± 0.004 |
| Source mean | 0.318 ± 0.011 | 0.177 ± 0.005 |
| Direct search | 0.315 ± 0.012 | 0.173 ± 0.005 |

源校准为 600 秒。source+target subtotal 对 1/10/100 个 target 分别为 620/80/26 秒每任务；不包含加载、descriptor 和最终报告成本。ETTh2-96 的 620 秒 subtotal allocation 比较：direct search .303，conditioned .312。

## DLinear 同目标对照

| Method | Final train MSE | Selected test MSE |
|---|---|---|
| AdamW 2,000 | 0.2270 | 0.330 |
| AdamW 10,000 | 0.2205 | 0.322 |
| ROAM 2,000 | 0.2213 | 0.312 |
| Exact least squares | 0.2200 | 0.326 |
| Validation-selected ridge | 0.2220 | 0.310 |

| Horizon | AdamW 2k | AdamW 10k | ROAM 2k |
|---|---|---|---|
| 96 | 0.33 | 0.322 | 0.312 |
| 192 | 0.401 | 0.388 | 0.38 |
| 336 | 0.445 | 0.434 | 0.43 |
| 720 | 0.481 | 0.469 | 0.464 |
| Mean | 0.41425 | 0.40325 | 0.3965 |

两种优化器固定零正则；训练列来自 final iterate，test 列来自 validation-selected checkpoint。Exact LS 的训练最小值为 .2200。Ridge 是不同目标的预测参考。ETTh2-96 identifiable design rank=97，relative tolerance=1e-10，sample-normalized normal-equation absolute residual=2.1e-13。

## Phase policy

| Policy | ETTh2 MSE ± SD | ETTm2 MSE ± SD | ETTh2 updates |
|---|---|---|---|
| Discrete switch | 0.312 ± 0.010 | 0.174 ± 0.004 | 2400 |
| Continuous blend | 0.314 ± 0.011 | 0.173 ± 0.005 | 2150 |
| Phase I only | 0.319 ± 0.012 | 0.179 ± 0.006 | 3000 |

四成员更新次数为求和。各策略共用 20 秒 cap 和 20 次 validation；图中横轴为 evaluation round。

## UCI HAR classification

| Method | Accuracy ± SD (%) | Cross-entropy ± SD | Budget |
|---|---|---|---|
| Conditioned ROAM | 92.8 ± 0.6 | 0.215 ± 0.018 | 30 s / 20 calls |
| Source-mean controls | 92.3 ± 0.7 | 0.232 ± 0.020 | 30 s / 20 calls |
| Direct metric search | 93.1 ± 0.6 | 0.207 ± 0.017 | 30 s / 20 calls |
| Continuous blend | 92.9 ± 0.6 | 0.212 ± 0.018 | 30 s / 20 calls |
| AdamW reference | 93.5 ± 0.5 | 0.194 ± 0.016 | 1,500 updates; not time matched |

Accuracy 标准差单位为百分点。四个 population arms 共用 30 秒/20 calls；AdamW 的 1,500 updates 为独立预算参考。Source calibration 单独核算。

## Same-state positive-spectrum diagnostic

| Metric | ETTh2-96 | ETTm2-96 |
|---|---|---|
| Identity | 800 | 410 |
| Default | 760 | 385 |
| Source mean | 720 | 390 |
| Conditioned | 640 | 375 |

该诊断保留 full parameterization 的零空间，只报告正谱比值。若 identifiable design 满秩，rank 和 nullity 各为 H(T+1)，T=H=96 时为 9,312；条件维数计算与实际数值秩分别陈述。

## 原稿表格的确定性重算

| Source → target | Baseline MSE | ROAM MSE | Gain |
|---|---|---|---|
| ETTh1 → ETTh2 | 0.421 | 0.392 | 6.89% |
| ETTm1 → Weather | 0.286 | 0.271 | 5.24% |
| Weather → ECL | 0.201 | 0.189 | 5.97% |
| ECL → Exchange | 0.462 | 0.437 | 5.41% |

Descriptor 图以 .312 为统一分母。Factorial 的平均 marginal MSE gain 分别为 metric .01025、switching .00475、outer .00525。未单独报告的迁移格以 NR 表示，不以零代替。

## 运行实现

源任务拟合、两探针对角曲率、100-step refresh、10-step diagnostics、memory reset 和 source/target 数据边界详见匿名仓库 `docs/IMPLEMENTATION.md`。补充实验与历史 broad benchmark 分别标识环境、损失、预算和聚合范围。完整绘图数值（含轨迹观测和标准差）保存在 `figures/figure_data.json`。
