---
description: Status Command - 显示当前系统状态和任务进度
---

# /status - 状态查询

显示系统当前的状态机状态、任务队列进度和关键指标。

## Trigger
- 用户输入 `/status` 或 "状态" / "进度"

## Steps

### Step 1: 读取当前状态
// turbo
1. 读取 `.agent/memory/active_context.md`
2. 解析 YAML frontmatter 获取 `task_status`

### Step 2: 统计任务进度
// turbo
1. 统计 Task Queue 中各状态任务数量
2. 计算完成百分比

### Step 3: 读取工作流指标
// turbo
1. 读取 `.agent/memory/evolution/workflow_metrics.md`
2. 提取最近的执行统计

### Step 4: 生成状态报告

## Output Format
```markdown
## 📊 System Status

### 🎯 Current State
```
task_status: IDLE
session_id: evolution-engine-v1
last_checkpoint: checkpoint-20260208-021900
```

### 📋 Task Progress
| Status | Count |
|--------|-------|
| ✅ Done | X |
| ⏳ Pending | X |
| ❌ Blocked | X |

**Progress**: ██████████░░ 80% (X/Y tasks)

### 🧬 Evolution Stats
- **Knowledge Items**: X
- **Patterns**: X
- **Learning Queue**: X pending

### 📈 Recent Workflow
| Workflow | Last Run | Duration | Status |
|----------|----------|----------|--------|
| feature-flow | 2026-02-08 | 30min | ✓ |

---
*Last updated: [timestamp]*
```
