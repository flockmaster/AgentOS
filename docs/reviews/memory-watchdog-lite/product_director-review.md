`docs/reviews/memory-watchdog-lite-signal-flag-mode/review_product.md` 建议内容如下：

```markdown
# Product Strategy Review: Memory Watchdog Lite (Signal Flag Mode)

## 1. Strategic Fit (Med)
- Alignment with Validated Roadmap: 与“稳定性/成本控制/长会话可用性”方向高度一致；但未提供 Q1/Q2 已验证路线图条目，当前按“平台健康类能力”评估为中高匹配。

## 2. Prioritization Matrix
- Impact: 4
- Effort: 2
- Score: 2.0 (Impact/Effort)

## 3. Success Metrics
- Primary KPI: 长会话中断率（因上下文饱和导致）下降
- Secondary KPI:
  - 单任务平均 Token 消耗下降
  - 触发 WARNING 后 `/suspend1` 执行率
  - IDE 卡顿/崩溃相关反馈率下降
- Risk of Doing Nothing:
  - 成本继续上升，推理质量下降，重度用户流失风险增加

## Conclusion
- P1 - Should Have
- Note: 建议按 MVP 上线（仅信号灯+提示），2 周内观察 KPI；若 WARNING 命中率高且有效降低中断，再升级自动化策略。
```

澄清问题（门禁）：
你们当前 Q1/Q2 的正式目标里，是否已有“稳定性/Token 成本”OKR？若有，我可把结论从 `P1` 调整为可量化的 `P0/P1` 并给出对应阈值。
