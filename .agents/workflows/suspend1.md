---
description: Session Suspend - 会话收尾，保存状态，生成总结
---

# Suspend Workflow (收尾工作流)
当用户说 "暂停" / "休息" / "保存" / "suspend" 或主动结束会话时触发。
用于**主动保存当前状态**，确保下次会话能够无缝接力。
## Phase 1: 状态快照 (State Snapshot)
1. **获取当前时间**: 记录会话结束时间
2. **收集进度信息**:
   - 当前正在执行的 Task ID
   - Task Queue 中的 PENDING / DONE / BLOCKED 统计
   - Scratchpad 中的临时笔记
## Phase 2: 更新记忆文件 (Memory Update)
// turbo (自动执行记忆更新)
3. **更新 active_context.md**:
   ```yaml
   ---
   session_id: "[当前会话ID]"
   task_status: IDLE  # 或保持 EXECUTING 如果任务未完成
   auto_fix_attempts: 0
   last_checkpoint: "[最近的 checkpoint tag]"
   last_session_end: "2026-02-08 01:30"