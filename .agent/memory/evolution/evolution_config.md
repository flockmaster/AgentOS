# Evolution Config

进化引擎可调参数及变更历史。

## 当前参数

| Parameter | Value | Description | Last Updated |
|-----------|-------|-------------|-------------|
| decay_rate | -0.1 | 标准衰减速率 (每 30 天) | 2026-02-14 |
| fast_decay_rate | -0.15 | 加速衰减 (因果评分低) | 2026-02-14 |
| slow_decay_rate | -0.05 | 减缓衰减 (因果评分高) | 2026-02-14 |
| harvest_threshold | 0.7 | 收割初始置信度 | 2026-02-14 |
| injection_top_k | 5 | 知识注入条目数上限 | 2026-02-14 |
| injection_max_chars | 200 | 每条知识注入最大字数 | 2026-02-14 |
| archive_days | 90 | 决策图节点归档天数 | 2026-02-14 |
| deprecation_threshold | 0.5 | 知识废弃置信度阈值 | 2026-02-14 |
| causal_min_samples | 5 | 因果评分最小样本数 | 2026-02-14 |
| meta_evolve_interval | 5 | 每 N 次 evolve 触发 meta-evolve | 2026-02-14 |
| max_scan_files | 1000 | 项目扫描文件数上限 | 2026-02-14 |

## 变更历史

| Date | Parameter | Old Value | New Value | Reason | Approved By |
|------|-----------|-----------|-----------|--------|-------------|
| 2026-02-14 | - | - | - | 初始化 v2.0 参数 | system |
