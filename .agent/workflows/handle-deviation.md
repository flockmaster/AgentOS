---
description: 门禁偏离处理与工作流自进化
---

# 工作流：门禁偏离处理 (Gate Deviation Handler) — v2.2

当门禁处检测到用户偏离预期路径时触发，支持工作流自进化。

## Trigger
- 自动: 门禁处用户输入不匹配任何已定义路径
- 手动: `/handle-deviation`

## 执行步骤

1.  **即时响应 (Immediate Fulfillment)**
    // turbo
    - **动作**: 解析用户意图，调用对应技能/工具完成用户的即时请求。
    - **记录**: 调用 `GateDeviationDetector.record_deviation()`:
        - `gate_id`: 当前门禁标识 (如 `1-drafting:step6`)
        - `workflow_file`: 当前工作流文件路径
        - `expected_paths`: 门禁定义的路径列表
        - `user_input`: 用户原始输入
        - `user_intent`: 分类后的意图标签
        - `action_taken`: 执行的响应操作描述

2.  **自进化提议 (Evolution Proposal)**
    - **动作**: 主动询问用户:
        > "这个操作目前不在工作流中。需要我把它作为永久步骤添加到流程里吗？"
    - **路径**:
        - **用户同意**: 进入 Step 3。
        - **用户拒绝**: 标记 `modification_status = "rejected"`，返回原门禁继续工作流。
    - **无论用户是否同意**: 偏离均已在 Step 1 记录完毕，用于进化分析。

3.  **生成修改提案 (Generate Proposal)**
    - **动作**: 调用 `GateDeviationDetector.propose_modification(deviation_id)`.
    - **修改类型选择**:
        - `add_gate_path` — 在门禁路径中添加新选项（默认，最常见）
        - `add_step_before_gate` — 在门禁步骤前插入新步骤
        - `add_step_after_gate` — 在门禁步骤后插入新步骤
    - **展示**: 向用户展示 diff 预览 (unified diff 格式):
        ```
        ## 工作流修改提案 (GD-xxx)

        **偏离模式**: 用户在 [gate_id] 门禁处要求 "[user_intent]"
        **建议修改类型**: [modification_type]

        [diff 预览]

        确认应用此修改？
        ```
    - **路径**:
        - **确认**: 进入 Step 4。
        - **调整**: 用户提出修改建议 → 更新提案参数 → 重复 Step 3。
        - **取消**: 标记 `modification_status = "rejected"`，返回原门禁。

4.  **安全应用 (Safe Apply)**
    - **动作**: 调用 `GateDeviationDetector.apply_modification(deviation_id)`.
    - **安全协议**:
        1. 创建工作流文件时间戳备份 → `.agent/memory/evolution/workflow_backups/`
        2. 应用 Markdown 修改。
        3. 运行 `_validate_workflow()` 结构验证:
            - YAML frontmatter 是否完整
            - 步骤编号是否连续
        4. 运行 `DependencyAnalyzer.impact_analysis()` 评估影响范围。
    - **成功**:
        - 报告: "工作流修改已应用。备份: [backup_path]。影响文件: [N] 个。"
        - 提示: "如需回滚，可运行 `/handle-deviation rollback GD-xxx`。"
    - **失败** (验证不通过):
        - 自动回滚到备份。
        - 报告错误原因。
    - **输出**: 返回原门禁继续工作流。

5.  **决策记录 (Decision Recording)**
    - **触发**: Step 4 完成后自动执行。
    - **动作**: 调用 `DecisionRecorder.record()`:
        - `phase`: "workflow-evolution"
        - `context`: 偏离描述 + 修改内容
        - `options`: ["add_gate_path", "add_step_before_gate", "add_step_after_gate", "reject"]
        - `chosen`: 实际采取的操作
        - `reason`: 用户确认

## 回滚

运行 `/handle-deviation rollback GD-xxx` 可回滚指定偏离的工作流修改:
1. 从备份恢复工作流文件。
2. 更新偏离记录状态为 `rejected`。
