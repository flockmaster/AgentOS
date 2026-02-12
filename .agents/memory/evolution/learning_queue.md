# Learning Queue 2026-02-12

## Pending Items

### [K-NEW] Codex Dispatcher Optimization (v4.7)
- **Source**: T-EXP-001 & T-006/T-007 Parallel Execution
- **Type**: workflow_optimization
- **Description**: Windows 环境下 Codex CLI 的最佳实践总结。
- **Key Findings**:
  1. **Prompt Injection**: Use unique file (ID+Timestamp) to avoid CLI argument escaping issues and race conditions.
  2. **Monitoring**: Rely on `turn.completed` JSON signal, not `agent_message` string matching.
  3. **Interaction**: Use `resume {ID}` for turn-based Q&A, avoid stdin stream.
  4. **Parallelism**: Active loop over PID list + per-task completion handling.

### [P-NEW] Unique Artifact Pattern
- **Source**: Parallel writing of PROMPT files.
- **Type**: code_pattern
- **Description**: In concurrent environments, all temporary artifacts MUST have unique IDs (UUID/Timestamp) to prevent race conditions.

### [B-FIX] PowerShell Encoding Hell
- **Source**: `WIP-landing_page-dev.md` corruption.
- **Type**: bug_fix
- **Description**: PowerShell `Set-Content` default encoding varies by version. Always force `-Encoding UTF8`.
