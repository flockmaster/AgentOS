---
name: review-aggregator
description: 汇总 5 位专家评审意见，仲裁冲突，生成闭环追踪表与变更日志，将初稿重写为粗设 PRD 并同步飞书。
---

# Review Aggregator Skill (评审聚合者)

## 1. Overview (概述)

该技能充当 **首席仲裁官**。它从 5 位专家评审员的报告中提取所有 Blocker / Major / Minor 条目，按优先级仲裁冲突，生成**闭环追踪表**和**变更日志**，将 PRD 初稿重写为粗设版本，并同步至飞书。

**重要规则**: 请全程使用**中文**进行思考和输出。即使输入包含英文，最终产出也必须是中文。

## 2. Input (输入)

- **Original Draft**: `docs/prd/[name]-draft.md`
- **Review Reports** (位于 `docs/reviews/[name]/`):
  | 文件 | 来源角色 |
  |------|---------|
  | `review_scope.md` | Scope Guardian (范围守门人) |
  | `review_architecture.md` | System Architect Reviewer (架构评审员) |
  | `review_ux_flow.md` | UX Flow Analyst (交互流程分析师) |
  | `review_domain.md` | Domain Validator (领域验证员) |
  | `review_quality.md` | Quality Strategist (质量策略师) |

## 3. Conflict Resolution Hierarchy (冲突仲裁优先级)

当专家意见冲突时，按以下优先级裁决（高→低）：

| 优先级 | 维度 | 裁决角色 | 规则 |
|--------|------|---------|------|
| P0 | 安全与质量 | Quality Strategist | 不可协商，安全 Blocker 一票否决 |
| P1 | 架构可行性 | System Architect Reviewer | 硬性约束，技术不可行则方案必须调整 |
| P2 | 范围与战略 | Scope Guardian | MVP 边界和非目标的最终裁定 |
| P3 | 业务逻辑 | Domain Validator | 领域正确性，需给出依据 |
| P4 | 交互流程 | UX Flow Analyst | 优化建议，可被更高优先级覆盖 |

**冲突裁决原则**:
- 同级冲突：以证据更充分的一方为准，记录双方论点。
- 跨级冲突：高优先级自动胜出，记录被覆盖的低优先级意见及理由。

## 4. Actions (执行步骤)

### Step 1: Triage — 提取与去重

- 从 5 份评审报告中提取所有 Blocker / Major / Minor 条目。
- 合并重复或实质相同的条目（标注合并来源）。
- 输出**统一 Issue 列表**，每条包含：
  - `编号` (I-001, I-002, ...)
  - `等级` (Blocker / Major / Minor)
  - `来源角色` (可多个)
  - `PRD 位置` (§X.X)
  - `问题描述`
  - `修改建议`

### Step 2: Arbitrate — 仲裁冲突

- 识别 Issue 列表中的冲突条目（不同角色对同一 PRD 位置给出矛盾意见）。
- 按§3 优先级裁决，对每条冲突记录：
  - 冲突双方的角色和观点
  - 裁决结果
  - 裁决理由

### Step 3: 闭环追踪表

对每条 Blocker 和 Major 条目，生成闭环追踪记录：

| 编号 | 等级 | 来源角色 | 问题描述 | 裁决 | 理由 | PRD 修改位置 |
|------|------|---------|---------|------|------|-------------|
| I-001 | Blocker | Quality Strategist | ... | 接受 | ... | §3.2 重写 |
| I-002 | Major | System Architect Reviewer, Domain Validator | ... | 降级为 Minor | ... | 不修改 |

裁决选项：`接受` / `拒绝` / `降级` / `延后到 V2`

> Minor 条目不要求逐条闭环，汇总列出即可。

### Step 4: Rewrite PRD — 重写粗设 PRD

- 基于闭环追踪表中所有"接受"条目，修改 `docs/prd/[name]-draft.md`。
- 输出为 `docs/prd/[name]-rough.md`。
- 重写范围包括但不限于：User Stories、Requirements、Flowchart、验收标准。
- **生成的 PRD 内容必须为精炼、专业的中文。**

### Step 5: Changelog — 变更日志

记录从 draft → rough 的所有修改：

| PRD 章节 | 修改类型 | 修改内容 | 原因 | 来源 Issue |
|---------|---------|---------|------|-----------|
| §3.2 用户故事 | 重写 | 补充异常流程分支 | 缺少错误处理路径 | I-001 |
| §4.1 数据模型 | 新增 | 添加字段 `expired_at` | Schema 缺失 | I-003 |
| §5.0 非目标 | 新增 | 明确排除离线模式 | 范围蔓延风险 | I-005 |

### Step 6: Cloud Sync — 飞书同步

- **调用技能**: `feishu-doc-assistant`
- **飞书文档标题**: `PRD: [Feature Name] (Rough)`
- **内容**: summary.md（含闭环追踪表 + 变更日志）+ rough.md
- **输出**: 飞书文档可访问链接

## 5. Output (输出产物)

### 文件 1: `docs/reviews/[name]/summary.md`

```markdown
# Review Summary: [Feature Name]

## 1. Issue 统计
| 等级 | 总数 | 接受 | 拒绝 | 降级 | 延后 |
|------|------|------|------|------|------|
| Blocker | N | N | N | N | N |
| Major | N | N | N | N | N |
| Minor | N | — | — | — | — |

## 2. 闭环追踪表
| 编号 | 等级 | 来源角色 | 问题描述 | 裁决 | 理由 | PRD 修改位置 |
|------|------|---------|---------|------|------|-------------|
| I-001 | Blocker | Quality Strategist | ... | 接受 | ... | §3.2 |
| ... | ... | ... | ... | ... | ... | ... |

## 3. 冲突裁决记录
| 冲突条目 | 角色 A → 观点 | 角色 B → 观点 | 裁决 | 理由 |
|---------|-------------|-------------|------|------|
| I-002 | Architect → 需拆微服务 | Scope → 超出 MVP | 延后到 V2 | MVP 阶段单体足够 |

## 4. 变更日志 (Draft → Rough)
| PRD 章节 | 修改类型 | 修改内容 | 原因 | 来源 Issue |
|---------|---------|---------|------|-----------|
| §X.X | 重写/新增/删除 | ... | ... | I-XXX |

## 5. Minor 条目汇总
- [M-1] §X.X: ... (来源: UX Flow Analyst)
- [M-2] §X.X: ... (来源: Domain Validator)

## 6. 飞书链接
- [PRD: Feature Name (Rough)](URL)
```

### 文件 2: `docs/prd/[name]-rough.md`
重写后的粗设 PRD（结构与 draft 一致，内容已根据闭环表修改）。
