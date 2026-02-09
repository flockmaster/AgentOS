# Antigravity Agent OS — Claude 适配器
# Provider: Claude (Anthropic)
# Version: 1.0 | Updated: 2026-02-09

> 本文件是 Claude 用户的全局配置模板。
> 安装: 将此文件复制到 `~/.claude/CLAUDE.md`
> Windows: `C:\Users\YourName\.claude\CLAUDE.md`

---

## 0. 强制语言规则 (Mandatory)
- **语言**: 全程使用中文对话，包括代码注释、任务描述。
- **简洁**: 禁止解释标准库用法，禁止复述显而易见的代码变更。

---

## 1. 启动协议 (Boot Protocol)
> **Trigger**: 每次新会话开始时自动执行。

### 1.1 项目级配置检测
当工作目录下存在 `.agent/` 目录时：
1. **读取记忆**: 立即调用 `read_file` 读取 `.agent/memory/active_context.md`
2. **检查状态**: 解析 YAML frontmatter 中的 `task_status` 字段
3. **恢复上下文**: 根据状态自动建议下一步操作:
   - `IDLE` + 有 PENDING 任务 → 提示继续
   - `EXECUTING` → 提示上次中断，询问是否继续
   - `BLOCKED` → 提示阻塞原因

---

## 2. 工作流触发器 (Workflow Triggers)
| 用户输入模式 | 触发工作流 | 描述 |
|------------|-----------|-----|
| "继续" / "开始" / "早" | `/start` | 静默启动，恢复上下文 |
| 描述新功能需求 | `prd-crafter-pro` | 多角色协作生成 PRD |
| "确认" / "Go" (用户版PRD后) | 技术评审 | 技术总监评估可行性 |
| "确认" / "Go" (研发版PRD后) | `feature-flow` | 启动递归执行流水线 |
| "暂停" / "保存" | `/suspend` | 保存状态 |
| 粘贴错误日志 | `/analyze-error` | 智能错误分析 |
| "进化" / "学习" | `/evolve` | 触发进化引擎 |
| "反思" / "总结" | `/reflect` | 触发反思工作流 |
| "状态" / "进度" | `/status` | 显示系统状态 |
| "回滚" / "撤销" | `/rollback` | 回滚到检查点 |
| "知识 [query]" | `/knowledge` | 查询知识库 |
| "模式 [query]" | `/patterns` | 查询代码模式库 |
| "/meta [desc]" | `/meta` | 修改 Agent OS 系统 |
| "/export" | `/export` | 导出可移植压缩包 |

---

## 3. Claude 专属能力映射
| 操作 | Claude API |
|------|-----------|
| 读取文件 | `read_file` |
| 编辑文件 | `replace_string_in_file` |
| 创建文件 | `create_file` |
| 运行命令 | `run_in_terminal` |
| 搜索文件 | `grep_search` / `semantic_search` |

### Claude 注意事项
- **上下文窗口**: 200K tokens，需注意大文件分段读取
- **无 exec 模式**: Dispatcher 自动调度功能受限，建议使用对话模式执行工作流
- **编辑精度**: `replace_string_in_file` 要求精确匹配旧字符串，建议多包含上下文行
- **Tool Use**: Claude 原生支持 Tool Calling，工作流中可直接调用工具

### Claude 最佳实践
1. 使用 `grep_search` 先定位代码再用 `read_file` 读取
2. 编辑文件时提供 3-5 行上下文确保唯一匹配
3. 复杂任务拆分为小步骤，每步验证后再继续
4. 利用 `semantic_search` 进行模糊搜索

---

## 4. 门禁规则 (Gatekeeper Rules)
- **需求澄清门禁**: 用户需求存在歧义时强制反问。
- **PRD 确认门禁**: PRD 生成后必须用户明确确认方可编码。
- **编译提交门禁**: 代码修改后必须编译测试，通过后自动提交。

---

## 5. 进化引擎自动行为
| 触发事件 | 自动行为 |
|---------|---------|
| 任务完成 | 将代码变更加入 `learning_queue.md` |
| 错误修复成功 | 将修复模式加入学习队列 (P1) |
| 工作流完成 | 更新 `workflow_metrics.md` |
| 状态 → ARCHIVING | 自动触发 `/reflect` |

---

## 6. 配置参考
- **Provider**: Claude
- **配置中心**: `.agent/config/agent_config.md`
- **切换模型**: 修改 `agent_config.md` 中的 `ACTIVE_PROVIDER`

_Antigravity Agent OS v4.0 — Claude Adapter_
