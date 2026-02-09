---
description: Agent 状态机定义 - 规范化的状态转换模型
version: 1.0
---

# Agent State Machine (状态机模型)

本文件定义 Agent 的完整生命周期状态及其转换规则。

## 1. 状态定义 (States)

| 状态 | 代码 | 描述 | 允许的操作 |
|-----|------|-----|-----------|
| 空闲 | `IDLE` | 无活跃任务，等待用户输入 | 接收需求、查看历史 |
| 规划中 | `PLANNING` | 正在生成 PRD | 取消、暂停 |
| 待确认 | `CONFIRMING` | PRD 已生成，等待用户确认 | 确认、修改、取消 |
| 执行中 | `EXECUTING` | 正在执行任务队列 | 暂停、查看进度 |
| 自动修复 | `AUTO_FIX` | 遇到错误，正在尝试自动修复 | 查看错误、强制停止 |
| 阻塞 | `BLOCKED` | 熔断，需要人工介入 | 提供修复、回滚、跳过 |
| 归档中 | `ARCHIVING` | 所有任务完成，正在归档 | 等待完成 |

## 2. 状态转换规则 (Transitions)

```
┌─────────────────────────────────────────────────────────────────┐
│                        STATE MACHINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────┐  用户输入需求   ┌──────────┐                         │
│   │ IDLE │ ──────────────> │ PLANNING │                         │
│   └──────┘                 └──────────┘                         │
│       ▲                         │                                │
│       │                         │ PRD 生成完成                   │
│       │                         ▼                                │
│       │                   ┌────────────┐                         │
│       │ 用户取消           │ CONFIRMING │                         │
│       │◄──────────────────└────────────┘                         │
│       │                         │                                │
│       │                         │ 用户确认 "Go"                  │
│       │                         ▼                                │
│       │                   ┌───────────┐                          │
│       │                   │ EXECUTING │◄─────────────┐           │
│       │                   └───────────┘              │           │
│       │                         │                    │           │
│       │                         │ 遇到错误           │ 修复成功  │
│       │                         ▼                    │           │
│       │                   ┌──────────┐               │           │
│       │                   │ AUTO_FIX │───────────────┘           │
│       │                   └──────────┘                           │
│       │                         │                                │
│       │                         │ 3次修复失败                    │
│       │                         ▼                                │
│       │                   ┌─────────┐                            │
│       │ 人工修复/回滚     │ BLOCKED │                            │
│       │◄──────────────────└─────────┘                            │
│       │                                                          │
│       │                   ┌───────────┐                          │
│       │ 归档完成          │ ARCHIVING │                          │
│       │◄──────────────────└───────────┘                          │
│       │                         ▲                                │
│       │                         │ 所有任务完成                   │
│       └─────────────────────────┘                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 3. 转换触发器 (Triggers)

| 触发器 | 源状态 | 目标状态 | 触发条件 |
|-------|-------|---------|---------|
| `USER_INPUT_REQUIREMENT` | IDLE | PLANNING | 用户输入新需求 |
| `PRD_GENERATED` | PLANNING | CONFIRMING | PRD 文档生成完成 |
| `USER_CONFIRM` | CONFIRMING | EXECUTING | 用户确认 "Go/Yes/OK" |
| `USER_CANCEL` | CONFIRMING | IDLE | 用户取消或修改需求 |
| `USER_CANCEL` | PLANNING | IDLE | 用户主动取消规划 |
| `ERROR_DETECTED` | EXECUTING | AUTO_FIX | `flutter analyze` 或 `flutter test` 失败 |
| `FIX_SUCCESS` | AUTO_FIX | EXECUTING | 自动修复后验证通过 |
| `FIX_FAILED_3X` | AUTO_FIX | BLOCKED | 连续 3 次修复失败 |
| `HUMAN_INTERVENTION` | BLOCKED | EXECUTING | 人工提供修复方案 |
| `ROLLBACK` | BLOCKED | IDLE | 回滚到上一个 Checkpoint |
| `ALL_TASKS_DONE` | EXECUTING | ARCHIVING | 任务队列全部完成 |
| `ARCHIVE_COMPLETE` | ARCHIVING | IDLE | 归档完成 |

## 4. 状态持久化

当前状态存储在 `active_context.md` 的 YAML Frontmatter 中：

```yaml
---
session_id: "abc123"
task_status: EXECUTING        # 当前状态
auto_fix_attempts: 1          # 自动修复尝试次数 (仅 AUTO_FIX 状态有效)
last_checkpoint: "chk-202602081200"  # 最近的 Git Checkpoint
---
```

## 5. 状态查询命令

Agent 可通过以下方式查询/更新状态：
- **查询**: 读取 `active_context.md` 的 frontmatter
- **更新**: 调用 `context-manager` 技能的 `update_progress` 方法
