# Dispatcher 目录

> **v3.0 架构**: Agent 原生调度

## 当前状态

此目录已简化。Python 封装层已归档至 `deprecated/dispatcher-python-legacy/`。

## 调度方式

PM (Antigravity) 通过 `.agent/workflows/codex-dispatch.md` 工作流直接调度 Codex Worker：

```
1. run_command("codex exec --json --dangerously-bypass-approvals-and-sandbox {Prompt}")
2. command_status(CommandId, WaitDurationSeconds=60)
3. 解析 JSONL 事件流
4. 根据结果决定下一步
```

## 相关文件

- **工作流**: `.agent/workflows/codex-dispatch.md`
- **归档**: `.agent/deprecated/dispatcher-python-legacy/`

---

_Updated: 2026-02-10_
