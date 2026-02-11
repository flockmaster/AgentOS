# Antigravity Agent OS — 核心规则 (Core Rules)
# Version: 1.1 | Updated: 2026-02-11

> 本文件是 Agent OS 的系统级规则配置。
> 安装位置: `~/.gemini/GEMINI.md` (Windows: `C:\Users\YourName\.gemini\GEMINI.md`)

---

## 0. 强制语言规则 (Mandatory)
- **语言**: 全程使用中文对话，包括代码注释、任务描述、Prompt。
- **简洁**: 禁止解释标准库用法，禁止复述显而易见的代码变更。

---

## 1. 启动协议 (Boot Protocol)
> **Trigger**: 每次新会话开始时自动执行。

### 1.1 项目级配置检测
当工作目录下存在 `.agent/` 目录时：
1. **读取记忆**: 立即调用 `view_file` 读取 `.agent/memory/active_context.md`。
2. **检查状态**: 解析 `task_status`。
   - `IDLE`: 询问 "有什么新任务？"
   - `EXECUTING`: 提示 "上次任务未完成"，询问是否继续。
   - `BLOCKED`: 提示阻塞原因。

---

## 2. 智能工作流触发 (Smart Workflow Triggers)
> **关键机制**: 根据用户意图，自动匹配并加载 `.agent/workflows/` 下的流程文件。

| 用户意图 | 触发工作流 文件路径 | 对应指令(可选) |
| :--- | :--- | :--- |
| **提出新需求 / 做个功能** | `.agent/workflows/ai-review.md` | `/ai-review` |
| **拆解大任务 / 细化设计** | `.agent/workflows/prd-decomposition.md` | `/decompose` |
| **开始开发 / 写代码 / 执行** | `.agent/workflows/rd-implementation.md` | `/feature-flow` |
| **报错了 / 修 Bug / 分析日志** | `.agent/workflows/analyze-error.md` | `/analyze-error` |
| **反思 / 总结 / 进化** | `.agent/workflows/reflect.md` | `/reflect` |
| **导出系统 / 打包** | `.agent/workflows/export.md` | `/export` |

### 2.1 触发逻辑
当用户输入符合上述意图时：
1. **不要**直接开始干活。
2. **必须**先调用 `view_file` 读取对应的 Workflow 文件。
3. **严格**按照文件中的步骤执行。

---

## 3. Gemini 专属能力映射
| 操作 | Gemini API |
|------|-----------|
| 读取文件 | `view_file` |
| 编辑文件 | `replace_file_content` |
| 创建文件 | `write_to_file` |
| 运行命令 | `run_command` |
| 搜索文件 | `find_by_name` |

---

## 4. 门禁规则 (Gatekeeper Rules)
- **专家评审门禁**: 所有 PRD 必须经过 `ai-review` 流程（含 Gatekeeper, Parallel Review, Arbitration）。
- **PRD 确认门禁**: PRD 生成后必须用户明确确认方可进入开发。
- **复杂度门禁**: 开发前必须评估工时，>1人日必须触发 `prd-decomposition`。
- **编译提交门禁**: 代码修改后必须编译测试，通过后自动提交。

---

## 5. 进化引擎自动行为
| 触发事件 | 自动行为 |
|---------|---------|
| 任务完成 | 将代码变更加入 `learning_queue.md` |
| 错误修复成功 | 将修复模式加入学习队列 (P1) |
| 工作流完成 | 更新 `workflow_metrics.md` |

_Antigravity Agent OS v4.1 — Universal Adapter_
