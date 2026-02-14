---
description: Phase 1.5: 专家评审与意见汇总工作流
---

# 工作流：专家评审 (Phase 1.5)

本工作流通过 5 个专家角色的视角，对 PRD 初稿进行反馈和优化。

## 前置条件
- PRD 初稿存在于 `docs/prd/[name]-draft.md`。

## 执行步骤

1.  **并行专家评审 (Parallel Expert Review)**
    > **CRITICAL**: 您必须 **并行** 执行以下 `codex exec` 命令。禁止自行模拟评审结果。禁止串行等待。
    > **注意**: 请确保 `docs/reviews/[name]/` 目录已创建。

    // turbo
    - **动作**: 并行运行 5 个 `codex exec` 命令 (Terminal / PowerShell / Bash)。
    - **指令**:
        ```powershell
        # 1. UX Director
        codex exec "请读取 .agent/prompts/roles/ux_director.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。请输出详细的评审报告。" -o docs/reviews/[name]/ux_director_review.md
        
        # 2. Product Director
        codex exec "请读取 .agent/prompts/roles/product_director.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。请输出详细的评审报告。" -o docs/reviews/[name]/product_director_review.md
        
        # 3. Domain Expert
        codex exec "请读取 .agent/prompts/roles/domain_expert.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。请输出详细的评审报告。" -o docs/reviews/[name]/domain_expert_review.md
        
        # 4. Tech Lead
        codex exec "请读取 .agent/prompts/roles/tech_lead.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。请输出详细的评审报告。" -o docs/reviews/[name]/tech_lead_review.md
        
        # 5. Critic
        codex exec "请读取 .agent/prompts/roles/critic.md 扮演该角色，并审阅 docs/prd/[name]-draft.md。请输出详细的评审报告。" -o docs/reviews/[name]/critic_review.md
        ```
    - **等待**: 确保 5 份评审报告均已生成于 `docs/reviews/[name]/`。

2.  **汇总与同步 (Aggregate & Sync)**
    - **动作**: 运行 `review-aggregator` 技能。
        - 输入: 5 份评审报告 + 原始初稿。
    - **过程**:
        - 基于优先级解决冲突 (安全 > 技术 > 战略 > 逻辑 > 体验)。
        - 将初稿重写为 `docs/prd/[name]-rough.md`。
        - 同步至飞书文档 (Cloud)。
    - **输出**: 飞书文档链接。

3.  **用户确认门禁 (User Confirmation Gate)**
    - **动作**: 展示飞书文档链接。
    - **询问**: "专家评审已完成。这是最终的粗设 PRD: [链接]。是否进入任务拆解阶段？"
    - **路径**:
        - **是**: 触发工作流 `.agent/workflows/3-decomposing.md`.
        - **修改**: 用户可要求手动修改。如有需要可重跑步骤 2。
        - **否**: 在此停止。
