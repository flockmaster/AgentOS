---
description: Phase 2: 复杂 PRD 任务拆解与子文档生成工作流
---

# 工作流：任务拆解 (Phase 2)

本工作流将"粗设" PRD 拆解为 Manifest 任务清单和详细的 Sub-PRD 文档。

## 前置条件
- 最终版粗设 PRD 存在于 `docs/prd/[name]-rough.md`。
- 评审汇总文件存在于 `docs/reviews/[name]/summary.md`（含闭环追踪表 + 变更日志）。

## 执行步骤

0.  **知识注入 + 模式脚手架 (Knowledge Injection + Pattern Scaffolding)** — *v2.0*
    // turbo
    - **知识注入**: 调用 `KnowledgeInjector.retrieve_relevant(phase="decomposing", keywords=[从 rough PRD 提取])`。
    - **注入类别**: `pattern`, `architecture`, `workflow`。
    - **模式匹配**: 调用 `PatternScaffolder.suggest_and_scaffold(description)` 建议可复用模式。
    - **输出**: 将 top-5 知识条目 + 匹配模式注入拆解上下文。
    - **记录**: 追加注入事件到 `.agent/memory/evolution/injection_log.md`。

1.  **工作量评估门禁 (Workload Gate)**
    - **动作**: 评估任务工期是否 > 1 天。
    - **路径**:
        - **小任务 (< 1 天)**: 生成**简化版 Manifest**（仅含单条 T-001，格式与大任务一致）。跳到 Step 5。
        - **大任务 (> 1 天)**: 进入步骤 2。
    - **简化版 Manifest 格式**:
        ```markdown
        # Task Manifest: [Feature Name]
        > 工作量评估: < 1 天，采用单任务模式。

        ## 1. 架构概览
        [简要说明涉及的模块和文件]

        ## 2. 任务列表
        - [ ] **T-001: [任务标题]**
          - 路径: `docs/tasks/[id]/sub_prds/[name].md`
          - 说明: [任务描述]
          - 预估工时: [N 小时]
          - 对应 PRD 章节: §X.X
          - 依赖: 无
        ```

2.  **架构设计 (Manifest)**
    - **动作**: 运行 `system-architect` 技能。
    - **输入**:
        - `docs/prd/[name]-rough.md`（真理之源）
        - `docs/reviews/[name]/summary.md`（变更日志，确保评审结论不丢失）
    - **输出**: `docs/tasks/[id]/manifest.md`（包含架构图、DAG 任务列表）。

3.  **串行生成子 PRD (Sequential Sub-PRD Generation)**
    - **动作**: 遍历 `manifest.md` 中的任务列表。
    - **循环**: 对每个 `T-xxx` 任务：
        - **指令**:
            ```powershell
            codex exec --full-auto "请读取 .agent/prompts/roles/sub_prd_writer.md 扮演该角色。结合 rough.md 和 manifest.md，编写任务 [TaskID] 的子 PRD。需参考前序任务摘要: [PreviousSummary]..." -o docs/tasks/[id]/sub_prds/[task_name].md
            ```
        - **上下文**: 传递 `rough.md`, `manifest.md`, 以及 *前序* Sub-PRD 的摘要 (确保一致性)。
        - **输出**: `docs/tasks/[id]/sub_prds/[task_name].md`。

4.  **PM 审计 (一致性检查)**
    - **动作**: Agent (PM) 读取所有生成的 Sub-PRD + rough.md + manifest.md。
    - **检查维度**:
        | 检查项 | 说明 |
        |--------|------|
        | 需求覆盖 | rough.md 中每个功能点是否都有对应的 Sub-PRD 实现？ |
        | 数据一致 | 跨 Sub-PRD 的数据模型定义是否一致？（字段名、类型、枚举值） |
        | 接口匹配 | 上游 Sub-PRD 的输出是否与下游 Sub-PRD 的输入对齐？ |
        | 验收继承 | rough.md 的验收标准是否被细化到了对应的 Sub-PRD 中？ |
    - **输出**: 生成 `docs/tasks/[id]/audit.md` — **一致性审计表**：
        ```markdown
        # 一致性审计: [Feature Name]

        ## 审计结果
        | Sub-PRD | 需求覆盖 | 数据一致 | 接口匹配 | 验收继承 | 结果 |
        |---------|---------|---------|---------|---------|------|
        | T-001 | ✅ | ✅ | ✅ | ✅ | 通过 |
        | T-002 | ✅ | ❌ | ✅ | ✅ | 需修复 |

        ## 需修复项
        | Sub-PRD | 检查项 | 问题描述 | 修复动作 |
        |---------|--------|---------|---------|
        | T-002 | 数据一致 | User 模型缺少 avatar 字段 | 补充字段定义，与 T-001 对齐 |

        ## 结论
        - [全部通过 | N 项需修复]
        ```
    - **修复**: 若存在"需修复"项，自动重跑对应 Sub-PRD 的生成（Step 3 循环），修复后更新审计表。

5.  **用户确认门禁 (User Confirmation Gate)**
    - **动作**: 展示 Manifest + Sub-PRD 列表 + 审计结果。
    - **询问**: "任务拆解已完成。一致性审计通过。是否准备开发？"
    - **路径**:
        - **是**: 触发工作流 `.agent/workflows/4-implementing.md`。
        - **否**: 在此停止。
    - **偏离处理 (Deviation Handling)** — *v2.2*:
        - 若用户回复不匹配以上任何路径:
          1. 先满足用户的即时请求。
          2. 调用 `GateDeviationDetector.record_deviation(gate_id="3-decomposing:step5", workflow_file=".agent/workflows/3-decomposing.md", expected_paths=["是", "否"], ...)` 记录。
          3. 主动询问: "这个操作目前不在工作流中。需要我把它作为永久步骤添加到流程里吗？"
          4. 用户同意 → 触发 `.agent/workflows/handle-deviation.md` Step 3+。
          5. 无论是否同意修改，偏离均已记录，用于进化分析。

6.  **决策记录 (Decision Recording)** — *v2.0*
    - **触发**: Step 5 用户确认后自动执行。
    - **动作**: 调用 `DecisionRecorder.record()`，记录本次拆解决策：
        - `phase`: "decomposing"
        - `context`: 功能名称 + 任务数量
        - `options`: 拆解方案的备选（如"按层拆 vs 按功能拆"）
        - `chosen`: 最终采用的拆解方式
        - `reason`: 选择理由
        - `knowledge_used`: Step 0 注入的知识 ID 列表
    - **记录**: 追加到 `.agent/memory/evolution/decision_log.md`。
