---
description: Phase 1.5: 专家评审与意见汇总工作流
---

# 工作流：专家评审 (Phase 1.5)

本工作流通过 5 个专家角色的视角，对 PRD 初稿进行反馈和优化。

## 前置条件
- PRD 初稿存在于 `docs/prd/[name]-draft.md`。

## 执行步骤

0.  **知识注入 (Knowledge Injection)** — *v2.0*
    // turbo
    - **动作**: 调用 `KnowledgeInjector.retrieve_relevant(phase="reviewing", keywords=[从 PRD 初稿提取])`。
    - **注入类别**: `debugging`, `anti-pattern`, `architecture`。
    - **输出**: 将 top-5 知识条目（历史拒绝原因、反模式、架构决策）注入评审上下文。
    - **记录**: 追加注入事件到 `.agent/memory/evolution/injection_log.md`。

1.  **并行专家评审 (Parallel Expert Review)**
    > **CRITICAL**: 您必须 **并行** 执行以下 `codex exec` 命令。禁止自行模拟评审结果。禁止串行等待。
    > **注意**: 请确保 `docs/reviews/[name]/` 目录已创建。

    // turbo
    - **动作**: 并行运行 5 个 `codex exec` 命令 (Terminal / PowerShell / Bash)。
    - **指令**:
        ```powershell
        # 1. Scope Guardian (范围守门人)
        codex exec --full-auto "请读取 .agent/prompts/roles/product_director.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。按照角色定义的输出格式，生成包含 Blocker/Major/Minor 分级的评审报告。" -o docs/reviews/[name]/review_scope.md

        # 2. System Architect Reviewer (架构评审员)
        codex exec --full-auto "请读取 .agent/prompts/roles/tech_lead.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。按照角色定义的输出格式，生成包含 Blocker/Major/Minor 分级的评审报告。" -o docs/reviews/[name]/review_architecture.md

        # 3. UX Flow Analyst (交互流程分析师)
        codex exec --full-auto "请读取 .agent/prompts/roles/ux_director.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。按照角色定义的输出格式，生成包含状态矩阵和 Blocker/Major/Minor 分级的评审报告。" -o docs/reviews/[name]/review_ux_flow.md

        # 4. Domain Validator (领域验证员)
        codex exec --full-auto "请读取 .agent/prompts/roles/domain_expert.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。按照角色定义的输出格式，生成包含前提声明和 Blocker/Major/Minor 分级的评审报告。" -o docs/reviews/[name]/review_domain.md

        # 5. Quality Strategist (质量策略师)
        codex exec --full-auto "请读取 .agent/prompts/roles/critic.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。按照角色定义的输出格式，生成包含测试矩阵、安全清单和 Blocker/Major/Minor 分级的评审报告。" -o docs/reviews/[name]/review_quality.md
        ```
    - **等待**: 确保 5 份评审报告均已生成于 `docs/reviews/[name]/`。

2.  **汇总与同步 (Aggregate & Sync)**
    - **动作**: 运行 `review-aggregator` 技能。
        - 输入: 5 份评审报告 + 原始初稿。
    - **过程**:
        - 汇总所有 Blocker/Major/Minor 条目。
        - 基于优先级解决冲突 (安全 > 架构 > 领域逻辑 > 流程完整 > 范围)。
        - 生成闭环追踪表：每条 Blocker/Major 必须标注 `处理状态（接受/拒绝）+ 理由 + PRD 修改位置`。
        - 将初稿重写为 `docs/prd/[name]-rough.md`。
        - 同步至飞书文档 (Cloud)。
    - **输出**: 飞书文档链接 + 闭环追踪表。

3.  **用户确认门禁 (User Confirmation Gate)**
    - **动作**: 展示飞书文档链接。
    - **询问**: "专家评审已完成。这是最终的粗设 PRD: [链接]。是否进入任务拆解阶段？"
    - **路径**:
        - **是**: 触发工作流 `.agent/workflows/3-decomposing.md`.
        - **修改**: 用户可要求手动修改。如有需要可重跑步骤 2。
        - **否**: 在此停止。
    - **偏离处理 (Deviation Handling)** — *v2.2*:
        - 若用户回复不匹配以上任何路径:
          1. 先满足用户的即时请求。
          2. 调用 `GateDeviationDetector.record_deviation(gate_id="2-reviewing:step3", workflow_file=".agent/workflows/2-reviewing.md", expected_paths=["是", "修改", "否"], ...)` 记录。
          3. 主动询问: "这个操作目前不在工作流中。需要我把它作为永久步骤添加到流程里吗？"
          4. 用户同意 → 触发 `.agent/workflows/handle-deviation.md` Step 3+。
          5. 无论是否同意修改，偏离均已记录，用于进化分析。
