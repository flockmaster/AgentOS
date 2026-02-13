# Sub-PRD: Check-Memory Script (T-MW-001)

> **Status**: APPROVED (Decomposed)
> **Parent**: Memory Watchdog Lite (v0.2)
> **Assignee**: Codex Worker (Script Specialist)

## 1. Goal (目标)
开发核心 PowerShell 脚本 `Check-Memory.ps1`，用于检测指定会话 `.pb` 文件的大小，并根据双级阈值原子写入状态文件。

## 2. Requirements (需求)

### 2.1 Parameters (输入参数)
- `SessionId` (String, Mandatory): 当前会话的 ID，用于定位 `.pb` 文件。
  - Path Logic: `d:\Baic-Flutter-APP\AgentOS\AgentOS\.agent\memory\sessions\{SessionId}.pb` (需适配实际存储路径)
- `Threshold` (Int, Optional): 基础阈值 (MB)。Default: 2MB。

### 2.2 Threshold Logic (阈值逻辑)
- **Safe**: Size < 80% Threshold -> `STATUS=NORMAL`
- **Warning**: 80% <= Size < 100% Threshold -> `STATUS=WARNING`
- **Critical**: Size >= 100% Threshold -> `STATUS=CRITICAL`

### 2.3 Atomic Write (原子写入)
- 目标文件: `.agent/memory/watchdog_status.lock`
- 写入内容 (JSON):
  ```json
  {
    "status": "WARNING",
    "size_mb": 1.7,
    "limit_mb": 2.0,
    "timestamp": 1715621234,
    "session_id": "abc-123"
  }
  ```
- **关键**: 先写入 `watchdog_status.tmp`，然后 `Move-Item -Force` 覆盖目标文件。

## 3. Implementation Details
- **Error Handling**: 如果找不到 `.pb` 文件，视为第一次运行或无历史，写入 `STATUS=NORMAL`，不报错。
- **Output**: 静默运行，无 Stdout 输出（除非 `-Verbose`）。

## 4. Verification Check
- `pwsh ./Check-Memory.ps1 -SessionId "test-session"` -> 生成 JSON 文件。
- `pwsh ./Check-Memory.ps1` (无参) -> 报错提示缺少 Parameters。
