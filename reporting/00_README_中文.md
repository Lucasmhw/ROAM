# ROAM 修订论文与回复配套材料

本包包含已完成的补充实验汇总、对应图件、四位审稿人的逐项英文回复，以及图表生成代码。论文正文为 ICLR 2027 官方单栏格式，共 10 页；参考文献和附录另计。黄色仅标记实质新增或明显变化的内容。

- `01_ROAM_OpenReview_Rebuttal.md`：15 个独立回复块，包含 1 个总回复，以及 p4jQ 4 条、BKGG 3 条、esdH 4 条、gg28 3 条；致谢并入首条。
- `reviewer_files/`：按审稿人拆分的相同回复。
- `02_Experimental_Results_and_Protocols.md`：数值、实验范围和预算口径。
- `03_Chinese_Summary_and_Coverage.md`：审稿意见与修订位置的对应。
- `04_Character_Counts.md`：实际 Comment 字符校验。
- `05_Figure_Captions_and_Placement.md`：论文中的图号和位置。
- `06_Reply_Reading_View.html`：按回复切换的阅读预览，可复制实际 Title 和 Comment 字段；数学排版库需联网加载。
- `figures/figure_data.json`：图件使用的数值汇总。
- `figures/generate_figures.py`：以同一数据源重绘 PDF、PNG、SVG。

图 R2–R6 对应已完成的补充实验。迁移、描述量与 factorial 图采用原稿表格的已报告数值重算。误差条为 seed 标准差；汇总数据不用于推算未报告的配对显著性。

匿名代码与实验协议：<https://anonymous.4open.science/r/ROAM-D935/>。
实验日志、拟合系数和 checkpoints 与本包的报告汇总分别管理；仓库命令可生成相应运行产物。
