无法直接写文件（当前工具执行被策略拦截）。以下为可直接保存到 `docs/reviews/memory-watchdog-lite-signal-flag-mode/review_tech.md` 的内容：

```markdown
# Tech Feasibility Review: Memory Watchdog Lite (Signal Flag Mode)

## 1. Architecture Impact
- Schema Changes: No
- API Changes: No（仅新增本地文件契约：`.agent/.status`）
- 备注：会引入「会话 `.pb` 路径发现 + 状态文件写入」的运行时依赖。

## 2. Risk Assessment
- Complexity Score (1-10): 4
- POC Required: Yes（仅针对“每次回复后自动触发”能力）
- 主要风险：
  - 自动触发点不稳定：不同 Agent 运行模式不一定保证 Post-Response Hook。
  - `.pb` 文件定位不确定：多会话/多目录下可能误判。
  - 并发写风险：并行会话可能覆盖 `.agent/.status`。
  - 平台耦合：PowerShell 方案默认偏 Windows，跨平台需补 shell 适配。

## 3. Implementation Plan (Rough)
- Backend:
  - 新增 `Check-Memory.ps1`：读取目标 `.pb` 大小、比较 `$ThresholdMB`、原子写 `.agent/.status`。
  - 状态格式固定：`STATUS=NORMAL` 或 `STATUS=WARNING|SIZE=...|THRESHOLD=...`。
  - 错误仅在异常时输出；正常路径完全静默。
- Frontend:
  - Agent 在每轮工具链末尾调用检测（或统一封装命令）。
  - 下轮开始读取 `.agent/.status`；`WARNING` 时强制追加确认提示（Yes/No）。
  - Yes 分支接 `/suspend1` 工作流；No 分支继续但保留风险提示。

## Conclusion
- POC Required
- Estimated Effort: 1-2 天（含 POC、异常处理、并发保护、最小回归验证）
```

建议先做 0.5 天 POC 验证两点：`自动触发可达性`、`多会话下 .pb 定位正确性`。通过后再进主干实现。
