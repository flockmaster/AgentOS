# Sub-PRD: Warning Interaction (T-MW-003)

> **Status**: APPROVED (Decomposed)
> **Parent**: Memory Watchdog Lite (v0.2)
> **Assignee**: Codex Worker (UX Specialist)

## 1. Goal (目标)
修改 AgentOS 的 **System Prompt 注入逻辑**，使 Agent 能在回复前主动读取 `watchdog_status.lock`，并根据状态（WARNING/CRITICAL）调整话术。

## 2. Requirements (需求)

### 2.1 Dynamic Prompt Injection (动态提示注入)
- **读取逻辑**: 在 `codex exec` 的 `--instruction` 或 `User Message` 构造阶段，先读取 `watchdog_status.lock`。
- **Condition**:
  - IF `STATUS == NORMAL`: 不做任何修改。
  - IF `STATUS == WARNING`: 在提示词末尾追加 `[Warning: Memory Limit Approaching]`。
  - IF `STATUS == CRITICAL`: 在提示词头部追加 `[CRITICAL: Memory Limit Reached]`。

### 2.2 Response Behavior (响应行为)
- **Warning State**:
  - Agent 回复应当简洁 (Be concise)。
  - 在回复末尾添加温馨提示: `(Tip: Memory is high, consider /suspend)`。
- **Critical State**:
  - Agent 回复必须以红色警告开头。
  - 强制建议: `Please run /suspend immediately.`

### 2.3 UX Test (交互验证)
- 模拟 `.agent/memory/watchdog_status.lock` 为 `{"status": "CRITICAL"}`。
- 然后向 Agent 提问 "Hello"。
- **Expected Output**:
  > 🔴 **CRITICAL MEMORY ALERT**
  > System context is full. Please suspend now.
  >
  > Hello! (Concise reply...)

## 3. Implementation Details
- **File**: `.agent/prompts/system_prompt.md` 或 `agent-runner.ps1` (Prompt Assembly Logic)。
- **Safety**: 确保读取 `lock` 文件时不会因为文件被占用而报错 (使用 `FileShare.ReadWrite`)。
