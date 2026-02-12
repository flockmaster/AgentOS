---
description: 执行 Agent OS 初始化 (环境适配)
---

你将执行 Agent OS (v4.2) 的初始化工作流。

**目标**: 识别当前 AI 开发环境，安装或更新对应的适配器规则文件，确保 System Prompt 正确加载。

**步骤**:
1) **环境检测**:
   - 如果用户在 **VS Code** 且使用了 **GitHub Copilot**，检查 `.github/copilot-instructions.md`。
   - 如果用户使用 **Cursor AI**，检查项目根目录的 `.cursorrules`。
   - 如果用户使用 **Gemini 1.5 Pro** 本地环境，检查 `~/.gemini/GEMINI.md`。
   - 如果用户使用 **Antigravity CLI**，检查 `~/.antigravity/ANTIGRAVITY.md`。
   - (若不确定，请直接询问用户)

2) **备份旧配置**:
   - 如果目标文件已存在，将其重命名为 `.bak`。

3) **部署新配置**:
   - 将 `.agent/adapters/[env]/[CONFIG_FILE]` 复制到对应的位置。
   - 对于 **Copilot**，确保 `.github/copilot-instructions.md` 内容与 v4.2 一致。
   - *注意*: Windows 下用户目录通常是 `C:\Users\[User]\`，请正确处理 `~` 路径。

4) **验证**:
   - 确认文件已生成且内容包含 `Version: v4.2`。
   - 确认 `.agents` 软链接存在。

**输出**:
- 告诉用户当前识别到的环境。
- 报告已执行的操作 (备份/复制)。
- 确认系统就绪。
