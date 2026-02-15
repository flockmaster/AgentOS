---
description: Phase 1: 需求分析、方案探索与 PRD 初稿生成工作流
---

# 工作流：PRD 起草 (Phase 1)

本工作流将用户的原始诉求转化为经过根因分析、方案探索后的结构化 PRD 初稿。

## 执行步骤

0.  **知识注入 (Knowledge Injection)** — *v2.0*
    // turbo
    - **动作**: 调用 `KnowledgeInjector.retrieve_relevant(phase="drafting", keywords=[从用户需求提取])`。
    - **注入类别**: `architecture`, `workflow`, `reference-project`。
    - **输出**: 将 top-5 知识条目（按 `causal_score * confidence` 排序，每条 ≤200 字）注入当前上下文。
    - **记录**: 追加注入事件到 `.agent/memory/evolution/injection_log.md`。

1.  **复杂度分流 (Complexity Triage)**
    - **动作**: 对用户输入运行 `requirement-analyst` 技能的 Step 0。
    - **路径**:
        - **快速通道**: 小改动（改文案、修 Bug 等）→ 直接输出任务描述，跳转 Phase 3 实施。
        - **标准流程**: 新功能/流程变更 → 进入步骤 2。

2.  **需求澄清循环 (Clarification Loop)**
    - **动作**: 运行 `requirement-analyst` 技能的 Step 1。
    - **检查**:
        - 若结果为 `CLARIFY`: 向用户询问缺失信息。等待回复。重复步骤 2。
        - 若信息充足: 进入步骤 3。

3.  **根因分析 (Root Cause Analysis)**
    - **动作**: 运行 `requirement-analyst` 技能的 Step 2。
    - **输出**: 表层需求 → 底层问题 → 问题重定义。
    - **展示**: 向用户呈现根因分析结果，确认问题定义是否准确。

4.  **方案探索与选择 (Solution Discovery & Selection)**
    - **动作**: 运行 `requirement-analyst` 技能的 Step 3 + Step 4。
    - **过程**:
        - 搜索开源项目/库，读取 README 评估匹配度。
        - 结合大模型知识提出创新方案。
        - 生成方案矩阵（2-5 个方案，含用户原始方案）。
    - **交互**: 展示方案矩阵，等待用户选择。
    - **路径**:
        - 用户选定方案 → 进入步骤 5。
        - 用户提出新想法 → 重新进入步骤 4。
    - **输出**: `PASS` 状态 + 选定方案的结构化描述。

5.  **生成 PRD 初稿 (Generate Draft)**
    - **动作**: 使用选定方案上下文，运行 `product-design-expert` 技能。
    - **输入**: requirement-analyst 的 `PASS` 输出 + `project_decisions.md`。
    - **输出**: 新文件生成于 `docs/prd/[name]-draft.md`（覆盖全部 10 个章节）。

6.  **草稿迭代门禁 (Draft Review Gate)**
    - **动作**: 向用户展示 PRD 初稿的路径和内容概要。
    - **询问**: "PRD 初稿已生成，包含 10 个章节。请查阅后选择："
    - **路径**:
        - **满意，进入专家评审**: 触发工作流 `.agent/workflows/2-reviewing.md`。
        - **需要修改**: 用户提出修改意见 → 更新初稿 → 重复步骤 6。
        - **推翻重来**: 回到步骤 4 重新选择方案。
        - **停止**: 在此停止。
    - **偏离处理 (Deviation Handling)** — *v2.2*:
        - 若用户回复不匹配以上任何路径:
          1. 先满足用户的即时请求。
          2. 调用 `GateDeviationDetector.record_deviation(gate_id="1-drafting:step6", workflow_file=".agent/workflows/1-drafting.md", expected_paths=["满意", "修改", "推翻", "停止"], ...)` 记录。
          3. 主动询问: "这个操作目前不在工作流中。需要我把它作为永久步骤添加到流程里吗？"
          4. 用户同意 → 触发 `.agent/workflows/handle-deviation.md` Step 3+。
          5. 无论是否同意修改，偏离均已记录，用于进化分析。
