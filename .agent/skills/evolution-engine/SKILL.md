---
name: evolution-engine
description: Agent 自进化引擎 (v2.2)。整合知识收割、工作流优化、模式检测、反思引擎、门禁偏离检测五大模块，赋予 Agent 自我学习和持续改进能力。
---

# Evolution Engine (自进化引擎)

本技能是 Agent 的"大脑升级系统"，负责从经验中学习、积累知识、识别模式、持续优化。

---

## 0. Core Philosophy (核心理念)

> "每一次任务都是学习机会，每一个错误都是改进素材。"

- **Continuous Learning**: 持续从对话和代码中提取知识
- **Pattern Recognition**: 识别可复用的代码和工作模式
- **Self-Reflection**: 定期反思，总结经验教训
- **Metric-Driven**: 用数据驱动优化决策

---

## 1. Modules (模块清单)

| Module | File | Trigger | Description |
|--------|------|---------|-------------|
| Knowledge Harvester | `evolution/knowledge_base.md` | 任务完成后 | 从对话中提取可复用知识 |
| Workflow Optimizer | `evolution/workflow_metrics.md` | 工作流完成后 | 追踪效能并提出优化建议 |
| Pattern Detector | `evolution/pattern_library.md` | 代码提交后 | 识别代码中的可复用模式 |
| Reflection Engine | `evolution/reflection_log.md` | 状态 → ARCHIVING | 自动反思并总结经验 |
| Learning Queue | `evolution/learning_queue.md` | 随时入队 | 管理待处理的学习素材 |

---

## 2. Commands (命令入口)

### 2.1 /evolve - 手动触发进化
**Trigger**: 用户输入 `/evolve` 或 "进化" / "学习"

**Action**:
1. 处理 `learning_queue.md` 中所有待处理素材
2. 更新 `knowledge_base.md` 和 `pattern_library.md`
3. 分析 `workflow_metrics.md` 生成优化建议
4. 输出进化报告

### 2.2 /reflect - 触发反思
**Trigger**: 用户输入 `/reflect` 或 "反思"

**Action**:
1. 读取当前会话的任务完成情况
2. 生成反思报告并追加到 `reflection_log.md`
3. 提取 Action Items

### 2.3 /knowledge - 查询知识库
**Trigger**: 用户输入 `/knowledge [query]` 或 "知识 [query]"

**Action**:
1. 搜索 `knowledge_base.md` 索引
2. 读取匹配的知识条目
3. 返回相关知识摘要

### 2.4 /patterns - 查询模式库
**Trigger**: 用户输入 `/patterns [query]` 或 "模式 [query]"

**Action**:
1. 搜索 `pattern_library.md`
2. 返回匹配的代码模式和模板

---

## 3. Automatic Behaviors (自动行为)

### 3.1 任务完成后入队
**Trigger**: 任何任务 (T-xxx) 标记为完成

**Action**:
```yaml
learning_queue.add:
  source_type: code_change
  source_id: T-xxx
  priority: P2
  metadata:
    files_changed: [...]
    description: "..."
```

### 3.2 错误修复后入队
**Trigger**: Auto-Fix 成功修复错误

**Action**:
```yaml
learning_queue.add:
  source_type: error_fix
  source_id: error-timestamp
  priority: P1
  metadata:
    error_type: "..."
    root_cause: "..."
    solution: "..."
```

### 3.3 工作流完成后记录指标
**Trigger**: 工作流执行完成（成功或失败）

**Action**:
1. 计算工作流耗时
2. 记录成功/失败状态
3. 追加到 `workflow_metrics.md`

### 3.4 IDLE 状态处理队列
**Trigger**: 状态变为 IDLE 且 `learning_queue` 不为空

**Action**:
1. 处理队列中 P0/P1 优先级素材
2. 更新知识库和模式库

---

## 4. Knowledge Harvester (知识收割机)

### 4.1 知识提取规则

从以下来源提取知识：

| Source | Extract If | Category |
|--------|------------|----------|
| 错误修复 | 新的错误类型或解决方案 | debugging |
| 架构决策 | 重大技术选型 | architecture |
| 代码模式 | 重复出现 3+ 次 | pattern |
| 工作流优化 | 显著效率提升 | workflow |
| 工具使用 | 新工具或新技巧 | tooling |

### 4.2 知识条目模板

```markdown
---
id: k-xxx
title: [Title]
category: [architecture|debugging|pattern|workflow|tooling]
tags: [tag1, tag2]
created: YYYY-MM-DD
confidence: 0.7
references: [source-id]
---

## Summary
[一句话总结]

## Details
[详细说明]

## Code Example (if applicable)
\`\`\`dart
// code
\`\`\`

## Related Knowledge
- k-yyy: [Related Title]
```

### 4.3 Confidence 更新规则

| Event | Confidence Change |
|-------|-------------------|
| 知识被再次验证 | +0.1 |
| 知识被引用使用 | +0.05 |
| 知识导致错误 | -0.2 |
| 30 天未使用 | -0.1 |

---

## 5. Pattern Detector (模式检测器)

### 5.1 模式识别触发

代码提交后，扫描 Git diff：
1. 检查是否与已知模式匹配
2. 检查是否出现新的重复结构

### 5.2 模式提升规则

```
IF pattern.occurrences >= 3 AND pattern.confidence >= 0.7
THEN promote to pattern_library as ACTIVE
```

### 5.3 复用提示

开发新功能时：
1. 读取功能描述
2. 搜索 `pattern_library.md`
3. 若有匹配模式，提示复用

---

## 6. Workflow Optimizer (工作流优化器)

### 6.1 指标收集点

| Workflow | Collect At |
|----------|-----------|
| feature-flow | 开始、PRD完成、每个任务完成、结束 |
| analyze-error | 开始、诊断完成、修复完成、结束 |
| start | 开始、上下文恢复完成、结束 |

### 6.2 优化建议触发

```
IF workflow.avg_duration > threshold * 1.5
OR workflow.success_rate < 0.8
THEN generate_optimization_suggestion()
```

### 6.3 建议模板

```markdown
## Optimization Suggestion: [Workflow Name]

**Issue**: [问题描述]
**Data**: 
- 平均耗时: X min (阈值: Y min)
- 成功率: X% (目标: 80%+)
- 最常见瓶颈: [Phase Name]

**Suggestion**: [优化建议]
**Expected Impact**: [预期效果]
```

---

## 7. Reflection Engine (反思引擎)

### 7.1 触发时机

- **自动**: 状态从 EXECUTING 变为 ARCHIVING
- **手动**: 用户输入 `/reflect`

### 7.2 反思流程

```
1. 读取 active_context.md 任务完成情况
2. 分析本次会话特点：
   - 任务完成率
   - 自动修复次数
   - 回滚次数
   - 耗时分布
3. 生成反思报告 (What Went Well / What Could Improve)
4. 提取 Learnings (转化为知识条目)
5. 提取 Action Items (转化为待办事项)
6. 追加到 reflection_log.md
```

### 7.3 Action Item 跟踪

Action Items 追加到 `active_context.md` 的任务队列中，标记为 `[REFLECTION]`：

```markdown
- [ ] [REFLECTION] 将 Loading Pattern 标准化为代码模板
```

---

## 8. Evolution Report (进化报告)

执行 `/evolve` 后，输出进化报告：

```markdown
# 🧬 Evolution Report - YYYY-MM-DD

## 📚 Knowledge Updated
- **New**: X items
- **Updated**: X items
- **Deprecated**: X items

## 🔄 Patterns Detected
- **New**: X patterns
- **Promoted**: X patterns

## 📊 Workflow Insights
- **Most Used**: [Workflow Name]
- **Bottleneck**: [Phase Name]
- **Optimization Suggestions**: X

## 💭 Reflections Processed
- **Sessions**: X
- **Action Items Completed**: X/Y

## 🎯 Recommended Next Steps
1. [Action 1]
2. [Action 2]
```

---

## 9. Integration Points (集成点)

### 9.1 与 context-manager 集成
- 反思结果写入 `active_context.md`
- 进化状态更新 frontmatter

### 9.2 与 feature-flow 集成
- 任务完成后触发知识入队
- 工作流完成后记录指标

### 9.3 与 analyze-error 集成
- 错误修复后触发知识入队
- 更新 `project_decisions.md` 的 Known Issues

### 9.4 与 GEMINI.md (全局配置) 集成
- 注册 `/evolve`, `/reflect`, `/knowledge`, `/patterns` 命令
- 添加自动行为触发器

---

## 10. Data Retention (数据保留)

| Data | Retention | Archive Policy |
|------|-----------|----------------|
| Knowledge Items | 永久 (Confidence > 0.5) | Confidence < 0.5 → deprecated → 7天后删除 |
| Workflow Metrics | 90 天详情，永久统计 | 90 天前详情归档 |
| Pattern Library | 永久 (Occurrences >= 3) | Occurrences < 3 → pending |
| Reflection Log | 永久摘要，30 天详情 | 30 天前详情归档 |
| Learning Queue | 处理后 7 天 | 7 天后删除 |
| Decision Log | 永久 | 90 天无因果链节点自动归档 |
| Outcome Tracker | 永久 | - |
| Injection Log | 90 天 | 90 天前归档 |

---

## 11. 闭环反馈 (Closed-Loop Feedback) — v2.0

### 11.1 知识注入协议

工作流每个阶段开始前自动注入相关知识:

```
1. 提取当前任务关键词
2. 调用 KnowledgeInjector.retrieve_relevant(phase, keywords)
3. 返回 top-5 知识条目 (按 causal_score * confidence 排序)
4. 格式化为 Prompt 注入块 (每条 ≤200 字)
5. 记录注入事件到 injection_log.md
```

**阶段-类别关联**:
| Phase | 优先类别 |
|-------|---------|
| drafting | architecture, workflow, reference-project |
| reviewing | debugging, anti-pattern, architecture |
| decomposing | pattern, architecture, workflow |
| implementing | pattern, debugging, tooling, reference-project |

### 11.2 决策回放

查找与当前上下文相似的历史决策:

```
1. 提取当前决策上下文
2. 调用 DecisionReplay.recommend(context)
3. 返回推荐选项 + 避免选项 + 相关知识引用
4. 格式化为 Prompt 注入块
```

### 11.3 模式脚手架

从模式库生成代码脚手架:

```
1. 提取功能描述
2. 调用 PatternScaffolder.suggest_and_scaffold(description)
3. 返回匹配模式 + 代码模板
4. 格式化为 Prompt 注入块
```

### 11.4 因果追踪

追踪知识应用的实际结果:

```
1. 记录知识应用 (record_outcome)
2. 计算因果评分 (causal_score)
3. 识别反知识 (anti-knowledge)
4. 自适应衰减 (adaptive_decay)
```

**因果评分公式**:
```
causal_score = success_rate * 0.5 + time_saved_norm * 0.3 - bugs_penalty * 0.2
```

---

## 12. 工作流自进化 (Workflow Self-Evolution) — v2.0

### 12.1 瓶颈检测

自动分析工作流历史指标，检测:
- 耗时过长 (> 30 min)
- 成功率过低 (< 80%)
- 返工率过高
- 常见瓶颈阶段

### 12.2 门禁调优

基于历史数据分析门禁表现:
- 首次通过率过低 → 建议放宽
- 从未拦截 → 建议收紧或移除

### 12.3 模板改进

生成工作流模板改进建议:
- 并行执行优化
- 前置验证增强

---

## 13. 跨会话推理 (Cross-Session Reasoning) — v2.0

### 13.1 决策图

构建决策因果链图谱:
- 节点: 每个决策 (上下文、选择、结果)
- 边: 因果关系 (cause → effect)
- 评分: outcome_score (-1.0 ~ 1.0)

### 13.2 路径查找

查找相似决策路径:
```
1. 提取当前上下文关键词
2. 在决策图中查找相似节点
3. 追踪因果路径
4. 计算路径平均评分
```

### 13.3 后悔分析

```
/regret-review
```
- 找出 outcome_score < -0.3 的决策
- 分析因果影响链
- 生成纠正建议
- 标记反知识

### 13.4 自动归档

90 天无因果链的孤立节点自动归档。

---

## 14. 元学习引擎 (Meta-Learning Engine) — v2.0

### 14.1 知识价值分析

分析各类别知识的因果评分分布:
- 最有价值 / 最无价值的知识 top-5
- 从未被应用的知识比例
- 类别价值不均衡检测

### 14.2 收割策略优化

基于历史数据优化收割策略:
- 高价值类别 → 提高收割优先级
- 低应用率 → 提高收割门槛
- 高衰减率 → 降低衰减速率

### 14.3 知识盲区检测

检测知识库中的覆盖不足:
- 必要类别知识不足
- 参考项目知识缺失
- 反知识未记录

### 14.4 进化规则调优

```
/meta-evolve
```
- 自动触发: 每 5 次 `/evolve`
- 手动触发: `/meta-evolve`
- 所有参数变更需用户确认
- 保留变更历史支持回滚

### 14.5 可调参数

| Parameter | Default | Description |
|-----------|---------|-------------|
| decay_rate | -0.1 | 标准衰减速率 |
| fast_decay_rate | -0.15 | 加速衰减 (低因果) |
| slow_decay_rate | -0.05 | 减缓衰减 (高因果) |
| harvest_threshold | 0.7 | 收割初始置信度 |
| injection_top_k | 5 | 注入条目数上限 |
| archive_days | 90 | 归档天数 |
| meta_evolve_interval | 5 | 元学习触发间隔 |

---

## 15. 门禁偏离检测 (Gate Deviation Detection) — v2.2

当用户在工作流门禁处输入不匹配预期路径时，系统自动检测偏离并提议工作流自进化。

### 15.1 偏离检测

门禁处的预期路径定义在各工作流的 `**路径**:` 块中。当用户输入不匹配任何路径时:

1. **即时响应**: 先满足用户的即时请求
2. **记录偏离**: 调用 `GateDeviationDetector.record_deviation()` 持久化到 `gate_deviation_log.md`
3. **主动提议**: 询问用户是否将此操作永久化到工作流

### 15.2 工作流自进化

用户确认后触发 `/handle-deviation` 工作流:

1. 生成修改提案 (unified diff 预览)
2. 用户确认 diff
3. 安全应用: **备份** → **修改** → **结构验证** → **依赖影响分析**
4. 记录到决策日志

**修改类型**:
- `add_gate_path` — 在门禁路径中添加新选项（最常见）
- `add_step_before_gate` — 在门禁前插入新步骤
- `add_step_after_gate` — 在门禁后插入新步骤

### 15.3 回滚

运行 `/handle-deviation rollback GD-xxx` 可从备份恢复工作流文件。

### 15.4 覆盖门禁

| 门禁 | 工作流 | 预期路径 |
|------|--------|---------|
| `1-drafting:step6` | 1-drafting.md | 满意, 修改, 推翻, 停止 |
| `2-reviewing:step3` | 2-reviewing.md | 是, 修改, 否 |
| `3-decomposing:step5` | 3-decomposing.md | 是, 否 |

### 15.5 关联模块

- `GateDeviationDetector` — 核心检测模块 (`evolution/gate_deviation_detector.py`)
- `WorkflowOptimizer` — 偏离驱动的门禁调优 (`suggest_deviation_based_tuning`)
- `MetaLearner` — 偏离模式分析纳入元学习报告
- `DependencyAnalyzer` — 修改后影响分析

---

_Last Updated: 2026-02-16_
