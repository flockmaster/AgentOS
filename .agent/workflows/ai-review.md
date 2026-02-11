
---
description: AI Expert Review Board Workflow - 多角色并行评审
---

# AI 专家评审团工作流

> 本工作流将启动 AI 专家评审团，对您的需求进行全方位体检。

## 1. 启动门禁 (Gatekeeper)
- 调用 `role_pm_gatekeeper.md` 对用户需求进行初步评估。
  - 读取用户输入的需求。
  - 检查可行性与清晰度。
  - 如果通过，生成 PRD 初稿。
  - 如果不通过，直接与用户对话澄清。

## 2. 准备评审环境 (Setup)
- 生成唯一的 Session ID (如 `review-{timestamp}`)。
- 创建临时目录 `.agent/memory/reviews/{session_id}/`。
- 将当前 PRD 草稿写入 `.agent/memory/reviews/{session_id}/prd.md`。

## 3. 专家会诊 (Parallel Expert Review)
- **[系统指令]**: 并行启动 4 个 Codex Worker 进程。请使用 `run_command` (WaitMsBeforeAsync=500) 分别执行以下命令：

    **Worker 1 (UX Director)**:
    ```bash
    codex exec --json --dangerously-bypass-approvals-and-sandbox "请扮演体验总监 (UX Director)。任务：1. 读取 .agent/memory/reviews/{session_id}/prd.md; 2. 根据 .agent/skills/ai-expert-review-board/prompts/role_ux_director.md 的标准进行评审; 3. 将评审报告写入 .agent/memory/reviews/{session_id}/review_ux.md。注意：直接输出文件，不要聊天。"
    ```

    **Worker 2 (Domain Expert)**:
    ```bash
    codex exec --json --dangerously-bypass-approvals-and-sandbox "请扮演行业专家 (Domain Expert)。任务：1. 读取 .agent/memory/reviews/{session_id}/prd.md; 2. 根据 .agent/skills/ai-expert-review-board/prompts/role_domain_expert.md 的标准进行评审; 3. 将评审报告写入 .agent/memory/reviews/{session_id}/review_domain.md。注意：直接输出文件，不要聊天。"
    ```

    **Worker 3 (The Critic)**:
    ```bash
    codex exec --json --dangerously-bypass-approvals-and-sandbox "请扮演批判者 (The Critic)。任务：1. 读取 .agent/memory/reviews/{session_id}/prd.md; 2. 根据 .agent/skills/ai-expert-review-board/prompts/role_critic.md 的标准进行评审; 3. 将评审报告写入 .agent/memory/reviews/{session_id}/review_critic.md。注意：直接输出文件，不要聊天。"
    ```

    **Worker 4 (Tech Lead)**:
    ```bash
    codex exec --json --dangerously-bypass-approvals-and-sandbox "请扮演技术专家 (Tech Lead)。任务：1. 读取 .agent/memory/reviews/{session_id}/prd.md; 2. 根据 .agent/skills/ai-expert-review-board/prompts/role_tech_lead.md 的标准进行评审; 3. 将评审报告写入 .agent/memory/reviews/{session_id}/review_tech.md。注意：直接输出文件，不要聊天。"
    ```

- **[系统指令]**: 使用 `command_status` 轮询检查这 4 个命令的状态，直到全部完成 (Status: done)。

## 4. 仲裁与定稿 (Arbitration & Finalize)
- **[系统指令]**: 读取 `.agent/memory/reviews/{session_id}/` 下生成的 4 份评审报告。
- **[系统指令]**: 扮演 **仲裁者 (Aggregator)**，依据 `role_aggregator.md`，汇总上述 4 份报告，生成《PRD 修订建议书》。
- **[系统指令]**: 最后，请作为 PM，根据建议书重写并输出 **PRD 终稿**。

## 4. 结束
- 提示用户 PRD 已就绪，询问是否进入开发阶段。
