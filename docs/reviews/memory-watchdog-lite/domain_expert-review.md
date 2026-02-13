```markdown
# Domain Expert Review: Memory Watchdog Lite (Signal Flag Mode)

## 1. Logic Validation
- 会话文件识别规则（多会话/多目录下“当前 .pb”定位）: **Adjustment Needed**
- 阈值定义（`MB` 采用 1000^2 还是 1024^2、边界 `>=`）: **Adjustment Needed**
- 状态生命周期（`WARNING` 何时失效、是否需要时间戳）: **Adjustment Needed**
- 状态写入一致性（并发会话写 `.agent/.status`）: **Adjustment Needed**
- 用户确认闭环（Yes 后 `/suspend1` 执行失败重试与回执）: **Adjustment Needed**
- 异常处理（找不到 `.pb`、权限不足、损坏文件）: **Adjustment Needed**
- 最小字段完整性（建议补充 `TS`、`SESSION_ID`）: **Adjustment Needed**

## 2. Industry Standard Check
- 监控告警分级（Normal/Warning）: **基本合规**，但建议预留 `CRITICAL`
- 事件可审计性（时间戳、会话标识、最近一次检测结果）: **不合规，需补充**
- 术语一致性（Context Window/Token Budget/Threshold）: **合规**
- 静默运行（正常无输出，异常可观测）: **合规**
- 人机交互可执行性（终端“[Yes]/[No]”应映射可输入命令）: **需修正为命令式交互**

## 3. Value Proposition
- 开发者（长会话重度用户）: 能提前止损 Token 与性能退化，价值明显
- 普通用户（短会话）: 感知弱，需避免过度打扰
- 采纳风险: 若误报/频繁提醒，会降低信任与执行率
- 建议指标: `WARNING->/suspend1` 转化率、触发后崩溃率、平均会话 Token 降幅

## Conclusion
- **Modification Required**
- Critical Domain Gaps:
  - 缺少“当前会话 `.pb`”确定性规则
  - 缺少状态 TTL/时间戳，存在陈旧告警风险
  - 缺少并发写保护与原子更新约束
  - 缺少告警后动作失败的业务补偿流程
  - 交互文案是按钮形态，未定义终端可执行输入协议
```

当前环境只读，无法直接写入 `docs/reviews/[prd-name]/review_domain.md`。
