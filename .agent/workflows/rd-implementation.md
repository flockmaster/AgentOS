---
description: R&D Implementation Workflow - 研发交付流水线 (Manifest 驱动)
---

# R&D Implementation Workflow

> 本工作流承接 PRD 拆解阶段，基于 `manifest.md` 驱动并行开发与交付。

## 1. 启动准备
- **Trigger**: 用户确认 `docs/tasks/{TaskID}/summary.md`，或直接调用 `/feature-flow`。
- **Input**: `docs/tasks/{TaskID}/manifest.md`。

## 2. 任务调度循环 (The Loop)
系统将反复执行以下步骤，直到 Manifest 中所有任务标记为 `[x]`。

### 2.1 DAG 分析与分发
- **[系统指令]**: 读取 `manifest.md`。
- **[系统指令]**: 识别所有状态为 `[ ]` 且前置依赖已满足 (`[x]`) 的任务集合。
- **[系统指令]**:
  - 如果集合为空但仍有未完成任务 -> 报错 "Deadlock detected" (循环依赖)。
  - 如果集合为空且无未完成任务 -> 跳转 [3. 交付验收]。
  - 如果集合不为空 -> **并行启动** Codex Worker (Max 3)。

### 2.2 执行单元 (Execution Unit)
对每个分发的任务 (e.g., T-101)，执行以下 Prompt：

```bash
codex exec --json --dangerously-bypass-approvals-and-sandbox "
# Role
你是一个资深的全栈工程师 (Codex Worker)。

# Task Context
- **Task ID**: {SubTaskID}
- **Artifacts**: 
  1. Main Manifest: docs/tasks/{TaskID}/manifest.md
  2. Sub-PRD: docs/tasks/{TaskID}/sub_prds/{SubTaskFile}

# Instructions
1. 阅读 Sub-PRD，理解需求。
2. 编写/修改代码 (Write Code)。
3. 编写/运行单元测试 (Run Tests)。
4. 确保测试通过 (Pass Rate 100%)。
5. 所有思考、注释和提交信息强制使用中文。

# Output
- 成功: TASK {SubTaskID} COMPLETED
- 失败: BLOCKED (说明原因)
"
```

### 2.3 状态同步
- **[系统指令]**: 轮询 Worker 状态。
- **[系统指令]**: 
  - 成功 -> 在 `manifest.md` 中将对应任务打钩 `[x]`。
  - 失败 -> 记录错误日志，暂停该分支，请求人工介入。

## 3. 交付验收 (Final Gate)
- **Action**: 运行全量集成测试/回归测试。
- **Checklist**:
  - [ ] 所有 Unit Tests 通过。
  - [ ] Integration Tests 通过。
  - [ ] Manifest 100% 完成。
- **Output**: 提示用户 "Feature {TaskID} Ready for Release".
