---
description: 执行 Agent OS 初始化 (环境适配与配置)
---

# 工作流：Agent OS 初始化 (v4.2)

本工作流旨在帮助您根据当前的 AI 开发环境 (如 GitHub Copilot, Gemini, Cursor) 配置 Agent OS。

## 执行步骤

1.  **环境检测 (自动/手动)**
    - **自动检测**: 检查是否存在特定的环境特征文件。
        - **Cursor AI**: 检查 `.cursorrules` 或 `.cursor/` 目录。
        - **Gemini**: 检查用户目录下是否存在 `.gemini/` 配置。
        - **GitHub Copilot**: 检查 `.github/copilot-instructions.md`。
        - **VS Code**: 检查 `.vscode/` 目录。
    - **人工确认**: 若无法确定，询问用户："请问您当前使用的是哪种 AI 助手？(Gemini / Cursor / Copilot / Claude)"

2.  **备份旧配置**
    - **动作**: 如果目标位置已存在旧的配置文件，将其重命名备份。
        - 例如: `mv ~/.gemini/GEMINI.md ~/.gemini/GEMINI.bak`
        - 例如: `mv .cursorrules .cursorrules.bak`

3.  **安装适配器规则**
    - **场景 A: Gemini**
        - **目标**: `~/.gemini/GEMINI.md` (全局) 或项目特定路径。
        - **来源**: `.agent/adapters/gemini/GEMINI.md`
        - **命令**: `Copy-Item .agent/adapters/gemini/GEMINI.md $HOME/.gemini/GEMINI.md`
    - **场景 B: Cursor**
        - **目标**: 项目根目录 `.cursorrules`。
        - **来源**: `.agent/adapters/cursor/.cursorrules` (优先) 或 `.agent/adapters/gemini/GEMINI.md`。
        - **命令**: `Copy-Item .agent/adapters/cursor/.cursorrules .cursorrules`
    - **场景 C: GitHub Copilot**
        - **目标**: `.github/copilot-instructions.md`。
        - **来源**: 确保内容与 `.agent/adapters/copilot/COPILOT.md` 一致。
    - **场景 D: Antigravity CLI (Native)**
        - **目标**: `~/.antigravity/ANTIGRAVITY.md`。
        - **来源**: `.agent/adapters/antigravity/ANTIGRAVITY.md`。

4.  **验证安装**
    - **动作**: 读取已安装的文件，确认包含 `Version: v4.2` 字样。
    - **输出**: "Agent OS v4.2 已为 [环境名] 初始化完成。系统就绪。"

5.  **创建兼容性软链接 (可选)**
    - **动作**: 确保 `.agents` 指向 `.agent` 以兼容旧脚本。
    - **命令**: `New-Item -ItemType Junction -Path .agents -Target .agent` (Windows) 或 `ln -s .agent .agents` (Mac/Linux)。
