# Agent OS v4.2 架构重构计划 (Manifest 驱动)

> **状态**: 起草中
> **愿景**: 关注点彻底分离 (技能 vs 工作流) | 100% 对齐 PRD 文档
> **作者**: Antigravity

---

## 0. 核心摘要 (Executive Summary)

我们将重建 Agent OS 架构，严格遵循 `docs/00` ~ `docs/03` 定义的 **Manifest 驱动** 流水线。
当前的遗留文件混合了逻辑债。本计划提出一个彻底的清理方案。

**核心哲学**:
1.  **技能即纯函数 (Skills are Pure Functions)**: 输入 -> 处理 -> 输出。无流程控制，无门禁。
2.  **工作流即控制器 (Workflows are Controllers)**: 处理用户交互、门禁、分支和技能编排。
3.  **产物即契约 (Artifacts are Contracts)**: 每个阶段向下一阶段交付特定的产物 (`*-draft.md`, `*-rough.md`, `manifest.md`)。

---

## 1. 目录结构 (目标形态)

```
.agent/
├── adapters/               # 系统适配器 (Gemini, Claude, Antigravity 等) - [已完成]
├── memory/                 # 运行时上下文
├── prompts/                # 角色定义 & 模板提示词
│   ├── roles/              # 原子化角色提示词 (UX, Tech, Critic...)
│   └── templates/          # 任务提示词
├── rules/                  # 路由 & 约束
├── skills/                 # 无状态工作单元 (Workers)
│   ├── drafting/           # product-design-expert (Phase 1)
│   ├── reviewing/          # (移除，被 prompts/roles/ 取代)
│   ├── refining/           # PM Agent (Phase 1.5 Fix)
│   ├── decomposing/        # task-decomposition-expert (Phase 2)
│   └── coding/             # codex-cli (Phase 3)
└── workflows/              # 编排逻辑
    ├── 1-drafting.md       # /draft (Phase 1: 初稿)
    ├── 2-reviewing.md      # /review (Phase 1.5: 评审)
    ├── 3-decomposing.md    # /decompose (Phase 2: 拆解)
    └── 4-implementing.md   # /implement (Phase 3: 开发)
```

---

## 2. 第一阶段：需求澄清与初稿 (Phase 1: Clarification & Drafting)

**目标**: 将模糊的用户需求转化为清晰度 > 90% 的需求上下文，并生成结构化的 **PRD 初稿 (Rough Spec)**。

### 2.1 技能：`requirement-analyst` (纯函数)
*   **角色**: 需求分析师 (Gatekeeper)。
*   **输入**: 用户需求 (String) + 项目背景。
*   **动作**:
    1.  **可行性检查 (Feasibility)**: 拒绝离谱/违规需求。
    2.  **清晰度检查 (Clarity)**: 评分 (0-100%)。
    3.  **追问 (Clarify)**: 如果清晰度 < 90%，生成引导性问题列表。
*   **输出**:
    *   状态: `PASS` / `REJECT` / `CLARIFY`.
    *   产物: 结构化需求描述 (Context) 或 问题列表。

### 2.2 技能：`product-design-expert` (纯函数)
*   **角色**: 产品设计师 (Product Designer)。
*   **输入**: 清晰度 > 90% 的结构化需求上下文。
*   **动作**:
    1.  提取核心价值。
    2.  定义 MVP 范围。
    3.  **绘制业务流程图 (Mermaid)**。
*   **输出**: `docs/prd/[name]-draft.md`。

### 2.3 工作流：`1-drafting.md` (控制器)
*   **触发**: 用户说 "做个新功能"。
*   **步骤**:
    1.  **循环 (Loop)**: 调用 `requirement-analyst`。
        *   若状态 == `REJECT`: 终止流程，反馈原因。
        *   若状态 == `CLARIFY`: 向用户提问 -> 用户回答 -> **回到步骤 1**。
    2.  **跳出 (Break)**: 当清晰度 >= 90% (即状态 == `PASS`)。
    3.  调用 `product-design-expert` -> 生成 Draft。
    4.  向用户展示 Draft。
    5.  **门禁**: "是否进入评审?" -> 是: 触发 `2-reviewing.md`。

---

## 3. 第 1.5 阶段：专家评审 (Phase 1.5: Reviewing)

**目标**: 通过并行专家输入验证 PRD 初稿。

### 3.1 角色提示词 (原子单元)
不再使用单体 "Skill"，而是使用 `.agent/prompts/roles/` 中的专用提示词：
*   `ux_director.md`: 关注 流程/UI。
*   `product_director.md`: 关注 战略/路线图/OKR 对齐。
*   `domain_expert.md`: 关注 业务价值。
*   `tech_lead.md`: 关注 可行性/成本。
*   `critic.md`: 关注 边缘情况。

### 3.2 技能：`review-aggregator` (纯函数)
*   **角色**: 高级 PM (Review Aggregator)。
*   **输入**: 5份评审报告 (UX/Product/Domain/Tech/Critic) + 原始 Draft。
*   **动作**: 
    1.  解决冲突，定优先级 (P0/P1)，重写 Draft。
    2.  **云端同步**: 调用 `feishu-doc-assistant` 将 `summary.md` 和 `rough.md` 自动创建为飞书文档 (返回可访问链接)。
*   **输出**: 
    - 本地文件 (含中文名): 
        - `docs/reviews/[name]/summary.md` (评审总结)
        - `docs/prd/[name]-rough.md` (PRD 粗设终稿)
    - 交付物: 飞书文档链接 (Feishu Doc Link)。

### 3.3 工作流：`2-reviewing.md` (控制器)
*   **触发**: 来自 `1-drafting.md` 或手动 `/review`。
*   **步骤**:
    1.  并行启动: `codex exec` x 5 (使用角色提示词：UX, Product, Domain, Tech, Critic)。
    2.  等待所有完成。
    3.  调用 `review-aggregator`。
    4.  **门禁**: "PRD 粗设已确认?" -> 是: 触发 `3-decomposing.md`。

---

## 4. 第二阶段：任务拆解 (Phase 2: Decomposition)

**目标**: 将粗设 PRD (>1 天工作量) 拆解为原子任务，并并行生成详细的 Sub-PRDs。

### 4.1 技能：`system-architect` (纯函数)
*   **角色**: 系统架构师 (System Architect)。
*   **输入**: `docs/prd/[name]-rough.md`。
*   **动作**:
    1.  设计全局架构 (Business Panorama)。
    2.  设计任务拓扑 (DAG)。
    3.  **生成任务清单**。
*   **输出**: `docs/tasks/[ID]/manifest.md` (仅包含任务结构，不含 Sub-PRD 内容)。

### 4.2 角色提示词：`sub_prd_writer.md` (原子单元)
*   **角色**: 高级技术写手 (Tech Writer)。
*   **输入**: 
    1.  `rough.md` (父文档 - Context)。
    2.  `manifest.md` (全景图 - Alignment)。
    3.  `Task Detail` (当前任务的定义)。
*   **要求**: 必须包含 接口定义(I/O)、数据结构、验收标准(Gherkin)。
*   **输出**: `docs/tasks/[ID]/sub_prds/[task_name].md`。

### 4.3 工作流：`3-decomposing.md` (控制器)
*   **触发**: 来自 `2-reviewing.md` 或手动 `/decompose`。
*   **步骤**:
    1.  **工期门禁**: 检查是否 > 1 天。 (否: 快速通道)。
    2.  调用 `system-architect` -> 生成 `manifest.md`。
    3.  **串行生成 (Sequential Generation)**: 
        *   为了确保 Sub-PRD 之间的一致性（如：A/B 任务的登录窗口设计统一），**放弃并行**。
        *   Agent 逐个调用 `sub_prd_writer`，并将前序已生成的 Sub-PRD 摘要作为 Context 传递给下一个任务。
    4.  **一致性评审 (PM Audit)**: 
        *   PM 读取所有 Sub-PRD。
        *   **检查 1 (Alignment)**: 是否偏离 `rough.md` (定稿 PRD)？
        *   **检查 2 (Self-Consistency)**: 任务之间是否存在逻辑矛盾或 UI 冲突？
        *   若冲突 -> 触发 **自动修订 (Auto-Fix)**。
    5.  **门禁**: "任务列表与文档已确认?" -> 是: 触发 `4-implementing.md`。

---

## 5. 第三阶段：开发交付 (Phase 3: Implementation)

**目标**: 基于 Manifest 执行任务。

### 5.1 技能：`codex-worker` (已在 CODEX.md 定义)
*   **角色**: 全栈开发。
*   **输入**: `Sub-PRD` + `Manifest`。
*   **动作**: 编码 + 测试。

### 5.2 工作流：`4-implementing.md` (控制器)
*   **触发**: 来自 `3-decomposing.md` 或 `/feature-flow`。
*   **步骤**:
    1.  读取 Manifest。
    2.  拓扑排序 (DAG)。
    3.  **并行分发** (最大 3)。
    4.  循环直到所有任务对应的 checkbox 为 `[x]`。
    5.  **编译门禁 (Compilation Gate)**:
        *   执行全量构建 (e.g., `flutter build apk --debug`)。
        *   **成功**: 
            *   生成 **研发交付报告** (`docs/reports/rd_report_[date].md`)。
            *   **云端同步**: 调用 `feishu-doc-assistant` 将报告同步至飞书。
            *   通知用户验收并提供文档链接。
        *   **失败/异常**: 触发 `analyze-error` 工作流进行自动修复 -> 回到步骤 5。

---

## 6. 迁移步骤

1.  **清理**: 删除/归档旧的单体技能 (`prd-crafter-pro`, `ai-expert-review-board`)。
2.  **创建原子技能**: 创建 `product-design-expert` (绘图), `review-aggregator`, `task-decomposition-expert`。
3.  **创建角色提示词**: 在 `.agent/prompts/roles/` 中创建文件。
4.  **创建工作流**: 创建 4 个编号的工作流文件。
5.  **更新路由**: 指向新的工作流。

**需要批准**: 此计划是否符合您"从头开始"和"不妥协"的愿景？
