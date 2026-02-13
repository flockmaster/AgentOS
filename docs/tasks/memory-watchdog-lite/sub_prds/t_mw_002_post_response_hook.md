# Sub-PRD: Post-Response Hook (T-MW-002)

> **Status**: APPROVED (Decomposed)
> **Parent**: Memory Watchdog Lite (v0.2)
> **Assignee**: Codex Worker (Agent Config Specialist)

## 1. Goal (目标)
修改 AgentOS 执行逻辑，确保在**每一轮 Agent 对话结束时**（Prompt 回复生成后），自动触发 `Check-Memory.ps1` 脚本，实现无感监控。

## 2. Integration Point (集成点)
- **目标文件**: `codex-call-loop` 或 `agent-runner.ps1` (需根据实际 Codex 运行环境确定)。
- **逻辑**: 在 `Loop()` 的 `Post-Processing` 阶段插入脚本调用。

## 3. Requirements (需求)

### 3.1 Hook Trigger (触发时机)
- **Wait**: `codex exec` 完成并返回对用户回复。
- **Condition**: 如果是 `--interactive` 模式，每次 `input` 后都要检测。

### 3.2 Command Execution (静默执行)
- **Cmd**: `Start-Process ... -WindowStyle Hidden`。
- **Args**: 传递当前会话 ID 到 `Check-Memory.ps1`。
  - 需要从 `active_context.md` 或运行时环境变量中解析 `SESSION_ID`。

### 3.3 Failsafe (安全措施)
- **Timeout**: 脚本调用必须设置超时 (e.g. 2s)，防止阻塞主进程。
- **Silent Fail**: 如果脚本找不到或报错，不打断 Agent 运行，仅记录 Warning 到日志。

## 4. Verification Check
- 运行一轮对话后，检查 `.agent/memory/watchdog_status.lock` 时间戳是否更新。
