# PRD: Evolution Engine (自进化引擎)

> **Version**: 1.0  
> **Created**: 2026-02-08  
> **Status**: DRAFT - 待确认

---

## 1. Context & Goals

### 1.1 目标
构建一个 **Self-Evolution Engine (自进化引擎)**，使 Agent 具备：
- 从历史对话中自动学习最佳实践
- 自动优化工作流效率
- 积累项目特定知识
- 持续反思并自我改进

### 1.2 价值主张
| 能力 | Before | After |
|-----|--------|-------|
| 错误修复 | 每次从零开始排查 | 自动匹配历史解决方案 |
| 工作流 | 固定流程 | 根据效果自动调优 |
| 知识 | 每次对话独立 | 知识持续积累 |
| 代码模式 | 人工总结 | 自动识别复用模式 |

### 1.3 Architecture Compliance
- 继承现有 `.agent/` 目录结构
- 扩展 `memory/` 模块，新增进化相关数据
- 使用 Markdown 作为知识存储格式（与现有系统一致）
- 不引入外部数据库，保持轻量

---

## 2. Technical Specs

### 2.1 System Architecture

```
.agent/
├── memory/
│   ├── active_context.md       # [现有] 短期记忆
│   ├── project_decisions.md    # [现有] 架构决策
│   ├── user_preferences.md     # [现有] 用户偏好
│   ├── state_machine.md        # [现有] 状态机定义
│   │
│   ├── evolution/              # [新增] 进化引擎数据
│   │   ├── knowledge_base.md       # 知识图谱索引
│   │   ├── workflow_metrics.md     # 工作流效能统计
│   │   ├── pattern_library.md      # 代码模式库
│   │   ├── reflection_log.md       # 反思日志
│   │   └── learning_queue.md       # 待学习队列
│   │
│   └── knowledge/              # [新增] 知识条目
│       ├── k-001-flutter-state-management.md
│       ├── k-002-stacked-viewmodel-pattern.md
│       └── ...
│
├── skills/
│   ├── context-manager/        # [现有]
│   ├── prd-crafter-lite/       # [现有]
│   │
│   └── evolution-engine/       # [新增] 进化引擎技能
│       └── SKILL.md
│
└── workflows/
    ├── start.md                # [现有]
    ├── feature-flow.md         # [现有]
    ├── analyze-error.md        # [现有]
    │
    ├── evolve.md               # [新增] 手动触发进化
    └── reflect.md              # [新增] 反思工作流
```

### 2.2 Core Modules

#### Module A: Knowledge Harvester (知识收割机)
- **职责**: 从对话中提取可复用知识
- **触发时机**: 每次任务完成后自动执行
- **输入**: 当前对话记录、代码变更
- **输出**: 知识条目 (`memory/knowledge/k-xxx.md`)

**知识条目格式**:
```markdown
---
id: k-001
title: Flutter 状态管理最佳实践
category: architecture
tags: [flutter, state, stacked]
created: 2026-02-08
confidence: 0.85
references: [conversation-id-xxx]
---

## Summary
使用 Stacked 框架时，ViewModel 不应直接持有 BuildContext...

## Code Pattern
\`\`\`dart
// Good
class MyViewModel extends BaseViewModel { ... }

// Bad
class MyViewModel { BuildContext context; }
\`\`\`

## Related Knowledge
- k-002: Stacked ViewModel 生命周期
```

#### Module B: Workflow Optimizer (工作流优化器)
- **职责**: 追踪工作流效能并提出改进建议
- **数据存储**: `memory/evolution/workflow_metrics.md`

**指标格式**:
```markdown
# Workflow Metrics

## feature-flow
| Date | Duration | Success | Rollbacks | Auto-Fix | Notes |
|------|----------|---------|-----------|----------|-------|
| 2026-02-08 | 15min | ✓ | 0 | 1 | PRD 阶段耗时过长 |
| 2026-02-07 | 8min | ✓ | 0 | 0 | - |

### Insights
- 平均耗时: 11.5 min
- 成功率: 100%
- 瓶颈: PRD 生成阶段 (占比 60%)
- 建议: 考虑缓存常用模板
```

#### Module C: Pattern Detector (模式检测器)
- **职责**: 识别代码中的可复用模式
- **触发时机**: 代码提交后
- **输入**: Git diff
- **输出**: 模式库条目 (`memory/evolution/pattern_library.md`)

**模式库格式**:
```markdown
# Pattern Library

## P-001: Repository + Cache Pattern
- **Occurrences**: 5 times
- **Files**: `word_repository.dart`, `user_repository.dart`, ...
- **Template**:
\`\`\`dart
class XxxRepository {
  final _cache = <String, dynamic>{};
  
  Future<T> getWithCache<T>(String key, Future<T> Function() fetch) async {
    if (_cache.containsKey(key)) return _cache[key] as T;
    final result = await fetch();
    _cache[key] = result;
    return result;
  }
}
\`\`\`
```

#### Module D: Reflection Engine (反思引擎)
- **职责**: 任务完成后自动评估并总结经验
- **触发时机**: 状态转换 `EXECUTING → ARCHIVING`
- **数据存储**: `memory/evolution/reflection_log.md`

**反思日志格式**:
```markdown
# Reflection Log

## 2026-02-08 Session

### What Went Well (做得好)
- [x] PRD 一次通过用户确认
- [x] 自动修复成功解决编译错误

### What Could Improve (待改进)
- [ ] UI 组件测试覆盖不足
- [ ] 应该先检查是否有现成组件

### Learnings (学到的)
- 新知识: k-005 (Flutter Widget 测试技巧)
- 新模式: P-003 (Loading State Pattern)

### Action Items (后续行动)
- [ ] 将 Loading Pattern 标准化为代码模板
- [ ] 更新 project_decisions.md 添加测试要求
```

#### Module E: Evolution Orchestrator (进化协调器)
- **职责**: 整合以上模块，管理进化周期
- **入口**: `skills/evolution-engine/SKILL.md`

---

## 3. Atomic Task List (任务队列)

### Phase 1: 基础设施 (Foundation)

- [ ] **T-001**: [P0] 创建进化引擎目录结构
    - 创建 `memory/evolution/` 目录
    - 创建 `memory/knowledge/` 目录
    - 初始化所有 .md 文件模板
    - **Verify**: 目录结构存在且包含初始内容

- [ ] **T-002**: [P0] 创建 `evolution-engine` 技能
    - 创建 `skills/evolution-engine/SKILL.md`
    - 定义技能接口：harvest, optimize, detect, reflect, evolve
    - **Verify**: 技能文件存在且格式正确

### Phase 2: 知识模块 (Knowledge Harvester)

- [ ] **T-003**: [P1] 实现知识收割逻辑
    - 在 SKILL.md 中定义知识提取规则
    - 定义知识条目模板
    - 实现知识分类和标签规则
    - **Verify**: 能够手动触发并生成示例知识条目

- [ ] **T-004**: [P1] 创建知识索引系统
    - 实现 `knowledge_base.md` 索引格式
    - 支持按类别、标签、日期检索
    - **Verify**: 索引文件可被解析并查询

### Phase 3: 工作流优化 (Workflow Optimizer)

- [ ] **T-005**: [P1] 实现工作流指标追踪
    - 定义指标收集点（开始时间、结束时间、状态）
    - 更新 `workflow_metrics.md` 格式
    - **Verify**: 执行一次 feature-flow 后，指标被记录

- [ ] **T-006**: [P2] 实现优化建议生成
    - 分析指标数据，识别瓶颈
    - 生成优化建议
    - **Verify**: 指标达到阈值后，生成建议

### Phase 4: 模式检测 (Pattern Detector)

- [ ] **T-007**: [P2] 实现代码模式识别
    - 定义常见模式模板
    - 分析 Git diff 识别重复模式
    - **Verify**: 提交代码后，能检测到匹配模式

- [ ] **T-008**: [P2] 模式复用建议
    - 开发新功能时，检查模式库
    - 自动建议复用现有模式
    - **Verify**: 开发类似功能时收到复用提示

### Phase 5: 反思引擎 (Reflection Engine)

- [ ] **T-009**: [P1] 实现自动反思工作流
    - 创建 `workflows/reflect.md`
    - 任务完成后自动触发
    - 生成反思报告
    - **Verify**: 任务完成后反思日志被更新

- [ ] **T-010**: [P2] 反思结果落地
    - 将反思中的"Action Items"转化为任务
    - 更新相关文档
    - **Verify**: Action Items 能被追踪执行

### Phase 6: 进化协调 (Evolution Orchestrator)

- [ ] **T-011**: [P1] 创建手动进化入口
    - 创建 `workflows/evolve.md`
    - 支持 `/evolve` 命令
    - 整合所有模块一次性执行
    - **Verify**: `/evolve` 命令可执行

- [ ] **T-012**: [P2] 更新全局配置
    - 更新 `GEMINI.md` 添加进化相关命令
    - 更新 `router.rule` 添加路由规则
    - **Verify**: 所有命令可被正确路由

---

## 4. Risks & Mitigations

| 风险 | 影响 | 缓解措施 |
|-----|-----|---------|
| 知识爆炸 | 知识条目过多难以管理 | 引入 `confidence` 分数，低分知识定期清理 |
| 模式误识别 | 错误提取非通用模式 | 设置最小出现次数阈值 (≥3) |
| 反思质量低 | 反思流于形式 | 定义结构化模板，强制填写关键字段 |
| 性能影响 | 进化任务阻塞主流程 | 进化任务异步执行，不阻塞开发 |

---

## 5. Success Metrics

| 指标 | 基线 | 目标 |
|-----|-----|-----|
| 知识条目数 | 0 | 20+ (首月) |
| 代码模式复用率 | 0% | 30%+ |
| 平均任务完成时间 | - | 逐月下降 10% |
| 错误重复发生率 | 100% | <20% |

---

## 6. Implementation Notes

### 6.1 优先级说明
- **P0**: 核心基础设施，必须首先完成
- **P1**: 主要功能，提供核心价值
- **P2**: 增强功能，可迭代改进

### 6.2 技术约束
- 所有数据存储为 Markdown 文件（不引入数据库）
- 使用 YAML Frontmatter 存储元数据（与现有系统一致）
- 技能定义使用标准 SKILL.md 格式

---

> **⚠️ 确认门禁**  
> PRD 已生成，请确认是否开始执行？(Yes/No)
