# 评审总结: Memory Watchdog Lite

## 1. 关键决策 (Key Decisions)
- **安全与完整性 (Critic/Tech)**:
  - **决策**: 采用 **原子两阶段写入** 模式 (写临时文件 -> 移动) 以防止竞态条件。
  - **决策**: 将状态文件移动至 `.agent/memory/watchdog_status.lock` 以避免污染根目录。
  - **决策**: 在状态文件中增加 `TIMESTAMP` 和 `SESSION_ID` 以防止读取过期状态。
- **UX & 交互 (UX/Domain)**:
  - **决策**: 采用 **双级阈值**:
    - **80% (Warning)**: 温和提示 ("接近限制")。
    - **100% (Critical)**: 强阻断 ("性能降级，建议挂起")。
  - **决策**: 将概念上的 "[Yes]" 按钮替换为明确的 **Slash Commands** (`/suspend`) 指令。
- **架构 (Tech)**:
  - **决策**: 脚本必须接受 `SessionID` 或 `LogPath` 参数，以正确指向特定的 `.pb` 文件（避免多会话环境下的歧义）。

## 2. 范围变更 (Scope Changes)
- **新增**:
  - 状态文件中的 `TIMESTAMP` 字段。
  - `CRITICAL` 状态逻辑。
  - `Check-Memory.ps1` 中的原子写入机制。
- **移除**:
  - 根目录 `.agent/.status` (移至 internal memory)。
  - "交互式按钮" 概念 (替换为文本指令)。

## 3. 评审共识 (Review Consensus)
- **结果**: **通过并修改 (Pass with Modifications)** (并发写入需 POC)。
- **下一步**: 进行 **任务拆解 (Decomposition)** 与 **实现 (Implementation)**。
