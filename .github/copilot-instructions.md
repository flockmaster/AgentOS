# Copilot Instructions (AgentOS)

你在 VS Code 的 Copilot Chat / Agent 模式中工作。

## 目录约定（非常重要）
- 系统真实的“记忆/偏好/决策”在 `.agents/` 下（不是 `.agent/`）。
- 旧文档/旧工作流若写了 `.agent/memory/...`，在执行时一律映射到 `.agents/memory/...`。

## 工作流调用方式
- 本仓库的工作流定义在 `.agent/workflows/*.md` 与 `.agents/workflows/*.md`。
- 用户说“运行 /status”“执行 /feature-flow”等时，优先使用 `.github/prompts/` 下同名 prompt 作为入口。
- 入口 prompt 会指示你读取对应 workflow 文件并按步骤执行。

## 工具使用约束
- 读文件用 `read_file`。
- 修改文件用 `apply_patch`。
- 运行命令用 `run_in_terminal`（macOS/zsh）。
- 需要并行读取多个文件时使用并行工具。

## 输出原则
- 只输出必要的关键信息与结果摘要，避免把长日志/JSONL 全量塞进对话上下文。
