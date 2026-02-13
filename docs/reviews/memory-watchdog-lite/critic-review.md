`docs/reviews/memory-watchdog-lite/review_critic.md`（当前环境写入被策略拦截，以下为审查内容）

```markdown
# Critic Review: Memory Watchdog Lite (Signal Flag Mode)

## 1. Security Audit (Fail)
- [P0]: `.agent/.status` 可被同目录其他进程篡改，若 Agent 直接信任会被诱导触发 `/suspend1`（信号注入）。
- [P0]: 未定义状态文件访问控制（谁可读写），缺少最小权限模型。
- [P0]: 未约束符号链接/重解析点，可能写入非预期路径（路径穿透/覆写风险）。
- [P1]: `.pb` 大小与阈值属于行为元数据，未定义保留周期与脱敏策略。
- [P1]: 错误输出若包含路径/会话标识，存在信息泄露面。
- [P2]: 未定义 GDPR/CCPA 对应的数据删除、审计与保留策略。

## 2. Edge Case Analysis
- [Case]: `.pb` 不存在/被占用/写入中，可能误判 NORMAL/WARNING。
- [Case]: 多终端并发写 `.agent/.status`，状态抖动与覆盖竞态。
- [Case]: `size == threshold` 规则不一致（文中同时有 `>` 与 `>=`）。
- [Case]: MB/MiB 未定义，触发阈值漂移。
- [Case]: `.status` 空/损坏/非法格式，解析失败回退策略缺失。
- [Case]: 用户连续触发导致 post-hook 重入，重复检测与重复提示。
- [Case]: 断连/超时后 `.status` 过期，下一轮被旧状态误导。
- [Case]: 超大文件或磁盘配额异常，错误路径未定义。
- [Case]: Windows/Linux 权限与路径语义差异，跨平台不一致。

## 3. Logical Consistency
- [Conflict]: “静默检测”与“WARNING 必须确认弹窗”冲突。
- [Conflict]: “回复后执行不了代码”与“tool_use 结束前顺手查”冲突。
- [Conflict]: “非侵入式”与“必须追加确认交互”冲突。
- [Conflict]: “Yes 立即执行 /suspend1”未定义幂等与防重入。
- [Conflict]: 目标是控制 context window，但实现只看文件大小，指标语义不闭环。

## Conclusion
- [Reject]
- Major Blockers: [状态文件完整性/权限防护缺失, 并发竞态无治理, 阈值与单位边界未定, 时序与交互规则自相矛盾]
```
