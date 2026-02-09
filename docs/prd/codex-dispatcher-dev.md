# PRD: Codex Task Dispatcher (研发版)

> 版本: 3.0 | 日期: 2026-02-09 | 状态: 进行中

## 1. 技术背景

### 1.1 架构概览

Dispatcher v3.0 采用 **Agent 原生 (PM ↔ Worker)** 模式。

- **PM**: Antigravity Agent 自身，通过自然语言理解来调度
- **Worker**: 独立的 `codex exec` 进程 (CLI)
- **通信**:
  - PM → Worker: 启动参数 (Prompt) + 重启注入 (Context Injection)
  - Worker → PM: `stdout` JSONL 事件流

### 1.2 核心设计原则

> **Agent 即调度器**: 利用大模型的自然语言理解能力来解析 PRD 和选择任务，
> 而不是用 Python/Shell 脚本硬编码解析。

| 传统方式 (v2.0) | Agent 原生 (v3.0) |
|----------------|------------------|
| parser.py 解析 Markdown | Agent 自然语言理解 |
| dispatch_loop.sh 循环 | Agent 思考判断下一步 |
| 依赖固定表格格式 | 支持任意 PRD 结构 |
| 脚本黑盒执行 | 每步透明可见 |

### 1.3 核心组件

| 组件 | 职责 | 实现方式 |
|-----|------|---------| 
| **Workflow (codex-dispatch.md)** | 指导 Agent 的调度思维流程 | Markdown 工作流 |
| **Worker Process** | 执行具体任务 | `codex exec` CLI |
| **Event Stream Parser** | 解析 Worker 输出 | JSONL Parser (可选用 Python 辅助) |
| **Agent Judgment** | 选择任务、处理问题 | 大模型自然语言理解 |

---

## 2. 任务拆解 (精简后 7 个核心任务)

> ✅ **架构调整**: 移除硬编码解析依赖，Agent 即调度器。

| ID | 任务 | 状态 | 描述 | 预估 | 依赖 |
|----|------|------|------|-----|------|
| T-001 | **定义核心数据结构** | ✅ DONE | Task/WorkerResult 数据类 (core.py) | 0.5h | - |
| T-002 | **实现 Worker 封装器** | ⏳ PENDING | 封装 `codex exec` 调用，支持 JSONL 解析和超时控制 | 2h | T-001 |
| T-003 | **实现"重启注入"机制** | ⏳ PENDING | 终止进程，构造新 Prompt (含答案)，重启 Worker | 2h | T-002 |
| T-004 | **集成 Git 自动提交** | ⏳ PENDING | 任务完成后自动执行 git commit | 1h | T-002 |
| T-005 | **实现 PRD 状态回写工具** | ⏳ PENDING | 提供辅助方法更新 Markdown 表格状态 (可选) | 1h | - |
| T-006 | **编写 Agent 调度 Workflow** | ✅ DONE | codex-dispatch.md v3.0 (Agent 原生调度) | 1h | - |
| T-007 | **端到端测试与文档** | ⏳ PENDING | 验证完整流程，更新用户手册 | 2h | T-002, T-006 |

---

## 3. 风险缓解计划

| 风险 | 缓解措施 |
|-----|---------|
| **Codex 上下文限制** | 每次重启 Worker 都会重新加载上下文，需确保 Prompt 包含必要历史摘要。 |
| **JSONL 解析异常** | 增加异常捕获，若解析失败则回退到 raw text 记录。 |
| **僵尸进程** | 在 PM 退出钩子 (atexit) 中强制 kill 所有子进程。 |

---

## 4. 测试策略

### 4.1 单元测试
- **WorkerWrapperTest**: 测试 Worker 封装器的启动、超时、JSONL 解析
- **RestartInjectionTest**: 测试重启注入机制

### 4.2 集成测试
- **MockWorker**: 模拟一个会提问的 Worker，测试 Agent 的回答注入流程
- **TimeoutTest**: 模拟死循环 Worker，验证超时终止机制
- **E2E_Test**: 端到端执行一个简单 PRD，验证完整流程

---

## 5. 里程碑

| Milestone | 包含任务 | 预计完成 | 目标 |
|-----------|---------|---------|------|
| **M1: 核心执行器** | T-001, T-002 | Day 1 | Worker 能启动并解析输出 |
| **M2: 交互增强** | T-003, T-004 | Day 1 | 支持重启注入和 Git 提交 |
| **M3: 完整自动化** | T-005, T-006, T-007 | Day 2 | 全流程验证 |

---

## 6. 执行协议 (Worker Protocol)

> 本文档是自动化执行的单一事实来源 (SSOT)。

### 状态定义
| 状态 | 图标 | 说明 |
|-----|------|-----|
| PENDING | ⏳ | 等待执行 |
| IN_PROGRESS | 🔄 | 正在执行中 |
| DONE | ✅ | 任务已完成 |
| BLOCKED | 🚫 | 需要 User 介入 |
| SKIPPED | ⏭️ | 临时跳过 |

### 执行规则
1. **Agent 选择**: Agent 读取 PRD，用自然语言理解选择第一个 PENDING 且依赖满足的任务。
2. **原子提交**: 每个任务完成后建议进行 Git 提交。
3. **自我更新**: 任务完成后，Agent 更新本文档中对应的状态为 `✅ DONE`。

---

## 7. 废弃组件

以下组件在 v3.0 中已废弃：

| 组件 | 原用途 | 替代方案 |
|-----|-------|---------|
| `parser.py` (硬编码解析) | 解析 Markdown 表格 | Agent 自然语言理解 |
| `dispatch_task.sh` | Shell 循环调度 | codex-dispatch.md Workflow |
| `dispatch_loop.sh` | 循环包装器 | Agent 调度循环 |

这些文件保留在代码库中仅供参考，不再在生产流程中使用。
