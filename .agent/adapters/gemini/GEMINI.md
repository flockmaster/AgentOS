# Antigravity Agent OS — 全局规则 (GEMINI.md)
# 版本: v4.3 (Lite) | 更新时间: 2026-02-14

> 本文件是 Agent OS 的系统级入口。
> **原则**: 仅定义不可变规则，具体逻辑下沉至 `.agent/rules/`。

---

## 0. 强制语言规则 (Mandatory)
> **Absolute Rule (P0)**: 优先级最高，不可覆盖。

- **语言**: 强制中文 (Chinese Mandatory)，包括对话、注释、Commit、Log。
- **对话标题**: 必须使用中文生成历史对话记录的标题 (Session Title)。
- **简洁**: 禁止解释标准库用法，禁止复述显而易见的代码变更。

---

## 1. 启动与路由 (Boot & Router)
> **Action**: 每次会话开始或需要决策时，必须读取以下文件。

1.  **记忆检查**: 立即读取 `.agent/memory/active_context.md`。
    -   `IDLE` -> 等待指令。
    -   `EXECUTING` -> 询问是否继续。
2.  **路由决策**: 读取 `.agent/rules/router.rule`。
    -   获取工作流映射 (Workflow Map)。
3.  **技能调用**: 读取 `.agent/rules/skills.rule`。
    -   获取技能映射 (Skill Map)。

---

## 2. 门禁系统 (Gatekeeper System)
> **Constraint**: 执行关键操作前必须通过检查。

- **执行前**: 读取 `.agent/rules/gatekeepers.rule`。
- **包含**:
    -   Expert Gate (评审门禁)
    -   User Gate (PRD确认)
    -   CI Gate (编译测试)

---

## 3. Gemini 能力映射 (Native Capability)
| 操作 | API | 备注 |
| :--- | :--- | :--- |
| **读文件** | `view_file` | 支持百万级 Context |
| **写文件** | `write_to_file` / `replace_file_content` | 优先使用 `replace` |
| **搜索** | `find_by_name` | 快速定位文件 |
| **执行** | `run_command` | 支持 PowerShell |
| **自动化** | `codex exec` | Headless 模式 |

---

## 4. 目录结构索引
- **记忆**: `.agent/memory/`
- **规则**: `.agent/rules/`
- **技能**: `.agent/skills/`
- **流程**: `.agent/workflows/`

_Antigravity Agent OS v4.3 — Lite Adapter_
