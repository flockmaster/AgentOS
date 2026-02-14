---
description: 执行 Agent OS 初始化 (全量环境配置与引导)
---

# 工作流：Agent OS 初始化 (v5.0)

本工作流负责将 Agent OS 适配到您的开发环境，建立配置文件，并引导您开始第一个任务。

> **GitHub 仓库**: [https://github.com/flockmaster/agent-os.git](https://github.com/flockmaster/agent-os.git)

## 执行步骤

### Step 1: 环境检查与配置 (Environment Check)
// turbo
1. **Git Check**:
   - 检查当前目录是否为 Git 仓库 (`.git` 存在？)。
   - 若否，询问是否执行 `git init` (推荐)。
2. **Watchdog Check**:
   - 检查 `.vscode/tasks.json` 是否存在且包含 "Start Memory Watchdog"。
   - 若否，询问是否自动创建/修补 (推荐)。
   - **Action**: 若同意，即刻创建 `.vscode` 目录并写入推荐配置。

### Step 2: 适配器配置 (Adapter Setup)
1. **AI Tool Selection**:
   - 询问用户使用的 AI 工具 (Copilot / Cursor / Gemini / Antigravity)。
2. **Rule Installation**:
   -根据选择，将对应的 Rule 文件 (`.agent/adapters/...`) 复制到标准位置 (如 `.github/copilot-instructions.md`)。
   - **Backup**: 覆盖前自动备份旧文件为 `.bak`。

### Step 3: 创建第一个任务 (First Task)
1. **Interaction**:
   > "系统已就绪。为了让我们可以立即开始协作，请告诉我您当前的首要任务是什么？"
   > (例如: "分析现有代码结构", "创建一个新的登录页面", "修复 README 里的错别字")
2. **Action**:
   - 将用户输入的内容写入 `.agent/memory/active_context.md` -> `Current Goal`。
   - 将状态标记为 `PENDING`。

### Step 4: 启动系统 (System Boot)
1. **Auto-Start**:
   - 自动触发 `/start` 工作流。
   - 加载刚才创建的上下文。
2. **Guidance**:
   - 输出指引：
     > "✅ **初始化完成！** memory watchdog 已配置 (请重启 VS Code 以生效)。
     > 
     > 下一步：
     > - **开发新功能**: 输入 `/feature-flow`
     > - **代码体检**: 输入 `/evolve`
     > - **查看状态**: 输入 `/status`"
