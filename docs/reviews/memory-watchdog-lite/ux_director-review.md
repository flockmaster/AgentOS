# UX Review: Memory Watchdog Lite (Signal Flag Mode)

## 1. Flow Analysis
- [回复后检测 -> 下一轮才提示]: 建议改为“同轮轻提示 + 下轮强确认”，降低预警滞后。
- [WARNING 决策分支]: 仅 `[Yes]/[No]` 过硬，建议加 `[Later] 10轮后再提醒`，减少打断感。
- [Yes 执行路径]: 增加“正在执行 / 成功 / 失败”反馈，避免误触后无感切换。
- [阈值设计]: 建议从单阈值 2MB 改为两级阈值（80% 预警，100% 强警告）。

## 2. UI/Visual Feedback
- [预警文案]: 统一结构为“风险级别 + 当前值/阈值 + 推荐动作”。
- [按钮语义]: `[No] 继续当前对话` 建议改为 `[继续并承担风险]`，语义更清晰。
- [状态一致性]: `.agent/.status` 建议补 `UNKNOWN`（读取失败/缺失）以避免静默失效。
- [交互闭环]: `/suspend1` 后需明确下一步提示（如“已保存，可安全继续/结束”）。

## 3. Usability Score (1-10)
- Reasoning: **7/10**。方向正确且轻量，但提醒时机、分支设计和异常态反馈仍有明显优化空间。

## Conclusion
- **Optimizable**
- Top 3 Changes Needed: [两级阈值策略, WARNING 三分支交互（Yes/Later/Continue with risk）, `/suspend1` 与 `UNKNOWN` 状态反馈闭环]

无法直接写入 `docs/reviews/memory-watchdog-lite/review_ux.md`（当前环境写入受限）；以上内容可直接落盘。
