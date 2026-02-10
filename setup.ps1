#!/usr/bin/env pwsh
# ============================================================
#  Antigravity Agent OS — 初始化向导 (Windows / PowerShell)
#  用法: pwsh setup.ps1 [-TargetDir <path>]
# ============================================================

param(
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── 颜色辅助 ──────────────────────────────────────────────
function Write-Step  { param($msg) Write-Host "`n🔧 $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "   ✅ $msg" -ForegroundColor Green }
function Write-Info  { param($msg) Write-Host "   ℹ️  $msg" -ForegroundColor DarkGray }
function Write-Warn  { param($msg) Write-Host "   ⚠️  $msg" -ForegroundColor Yellow }

# ── Banner ────────────────────────────────────────────────
Write-Host ""
Write-Host "   ╔══════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "   ║   🌌 Antigravity Agent OS — Setup        ║" -ForegroundColor Magenta
Write-Host "   ║   给你的 AI 编程助手装上大脑              ║" -ForegroundColor Magenta
Write-Host "   ╚══════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: 选择目标项目
# ============================================================
Write-Step "Step 1/6 — 设置目标项目"

if ($TargetDir -eq "") {
    Write-Host "   请输入你的项目路径 (留空 = 当前目录): " -NoNewline -ForegroundColor Yellow
    $TargetDir = Read-Host
    if ($TargetDir -eq "") { $TargetDir = Get-Location }
}
$TargetDir = Resolve-Path $TargetDir -ErrorAction SilentlyContinue
if (-not $TargetDir -or -not (Test-Path $TargetDir)) {
    Write-Host "   ❌ 路径不存在: $TargetDir" -ForegroundColor Red
    exit 1
}
Write-Ok "目标目录: $TargetDir"

# 检测是否已初始化
if (Test-Path "$TargetDir\.agent\memory\active_context.md") {
    Write-Warn "检测到该项目已安装 Agent OS (.agent/ 已存在)。"
    Write-Host "   是否覆盖配置？(y/N): " -NoNewline -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "   👋 已取消。" -ForegroundColor Gray
        exit 0
    }
}

# ============================================================
# Step 2: 项目信息
# ============================================================
Write-Step "Step 2/6 — 项目信息"

Write-Host "   项目名称: " -NoNewline -ForegroundColor Yellow
$ProjectName = Read-Host
if ($ProjectName -eq "") { $ProjectName = Split-Path -Leaf $TargetDir }

Write-Host ""
Write-Host "   选择技术栈:" -ForegroundColor Yellow
Write-Host "     [1] Flutter / Dart"
Write-Host "     [2] React / TypeScript"
Write-Host "     [3] Vue / TypeScript"
Write-Host "     [4] Python / Django"
Write-Host "     [5] Node.js / Express"
Write-Host "     [6] Go / Gin"
Write-Host "     [0] 自定义"
Write-Host "   输入编号 (默认 1): " -NoNewline -ForegroundColor Yellow
$stackChoice = Read-Host
if ($stackChoice -eq "") { $stackChoice = "1" }

$TechStacks = @{
    "1" = @{ sdk = "Flutter"; lang = "Dart"; arch = "MVVM"; lint = "flutter_lints"; fmt = "dart format"; run = "flutter run"; test = "flutter test"; analyze = "flutter analyze"; build = "flutter build" }
    "2" = @{ sdk = "React";   lang = "TypeScript"; arch = "Component"; lint = "eslint"; fmt = "prettier"; run = "npm run dev"; test = "npm test"; analyze = "npm run lint"; build = "npm run build" }
    "3" = @{ sdk = "Vue";     lang = "TypeScript"; arch = "Composition API"; lint = "eslint"; fmt = "prettier"; run = "npm run dev"; test = "npm test"; analyze = "npm run lint"; build = "npm run build" }
    "4" = @{ sdk = "Django";  lang = "Python"; arch = "MTV"; lint = "flake8"; fmt = "black"; run = "python manage.py runserver"; test = "python manage.py test"; analyze = "flake8 ."; build = "N/A" }
    "5" = @{ sdk = "Express"; lang = "JavaScript"; arch = "MVC"; lint = "eslint"; fmt = "prettier"; run = "npm start"; test = "npm test"; analyze = "npm run lint"; build = "npm run build" }
    "6" = @{ sdk = "Gin";     lang = "Go"; arch = "Clean Architecture"; lint = "golint"; fmt = "gofmt"; run = "go run ."; test = "go test ./..."; analyze = "go vet ./..."; build = "go build" }
}

if ($stackChoice -eq "0") {
    Write-Host "   SDK/框架: " -NoNewline; $customSdk = Read-Host
    Write-Host "   语言: " -NoNewline;     $customLang = Read-Host
    Write-Host "   架构: " -NoNewline;     $customArch = Read-Host
    $stack = @{ sdk = $customSdk; lang = $customLang; arch = $customArch; lint = "N/A"; fmt = "N/A"; run = "N/A"; test = "N/A"; analyze = "N/A"; build = "N/A" }
} else {
    $stack = $TechStacks[$stackChoice]
    if (-not $stack) { $stack = $TechStacks["1"] }
}

Write-Ok "项目: $ProjectName | $($stack.sdk) / $($stack.lang) / $($stack.arch)"

# ============================================================
# Step 3: 选择 AI 工具
# ============================================================
Write-Step "Step 3/6 — 选择你的 AI 编程工具"

Write-Host "     [1] Gemini (Google AI / Android Studio)"
Write-Host "     [2] GitHub Copilot (VS Code / JetBrains)"
Write-Host "     [3] Claude (Anthropic / Cursor)"
Write-Host "   输入编号 (默认 1): " -NoNewline -ForegroundColor Yellow
$aiChoice = Read-Host
if ($aiChoice -eq "") { $aiChoice = "1" }

$providers = @{
    "1" = @{ name = "gemini";  display = "Gemini";  adapter = "adapters/gemini/GEMINI.md";  globalDir = "$env:USERPROFILE\.gemini"; globalFile = "GEMINI.md" }
    "2" = @{ name = "copilot"; display = "Copilot"; adapter = "adapters/copilot/copilot-instructions.md"; globalDir = "$env:USERPROFILE\.copilot"; globalFile = "copilot-instructions.md" }
    "3" = @{ name = "claude";  display = "Claude";  adapter = "adapters/claude/CLAUDE.md";  globalDir = "$env:USERPROFILE\.claude"; globalFile = "CLAUDE.md" }
}
$provider = $providers[$aiChoice]
if (-not $provider) { $provider = $providers["1"] }
Write-Ok "AI 工具: $($provider.display)"

# ============================================================
# Step 4: 复制文件并初始化
# ============================================================
Write-Step "Step 4/6 — 安装 Agent OS 到项目"

# 4.1 复制 .agent/ 目录
$agentSrc = Join-Path $ScriptDir ".agent"
$agentDst = Join-Path $TargetDir ".agent"

if ($agentSrc -ne $agentDst) {
    if (Test-Path $agentDst) { Remove-Item $agentDst -Recurse -Force }
    Copy-Item $agentSrc $agentDst -Recurse -Force
    Write-Ok "已复制 .agent/ → $agentDst"
} else {
    Write-Ok ".agent/ 已在当前目录，跳过复制"
}

# 4.1.1 复制 .agents/（如果存在）
$agentsSrc = Join-Path $ScriptDir ".agents"
$agentsDst = Join-Path $TargetDir ".agents"
if (Test-Path $agentsSrc) {
    if (Test-Path $agentsDst) { Remove-Item $agentsDst -Recurse -Force }
    Copy-Item $agentsSrc $agentsDst -Recurse -Force
    Write-Ok "已复制 .agents/ → $agentsDst"
} else {
    Write-Info "仓库中无 .agents/，跳过复制"
}

# 4.1.1.1 Flutter 规范包（可选）
if ($stack.sdk -eq "Flutter") {
    Write-Host "   是否下载 flutter-ai-advanced-template 规范包？(y/N): " -NoNewline -ForegroundColor Yellow
    $installFlutterTemplate = Read-Host
    if ($installFlutterTemplate -eq "y" -or $installFlutterTemplate -eq "Y") {
        $gitCmd = Get-Command git -ErrorAction SilentlyContinue
        if (-not $gitCmd) {
            Write-Warn "未检测到 git，跳过规范包下载"
        } else {
            $templateDir = Join-Path $agentsDst "templates\flutter-ai-advanced-template"
            if (Test-Path $templateDir) {
                Write-Info "已存在 flutter-ai-advanced-template，跳过下载"
            } else {
                New-Item -ItemType Directory -Force -Path (Split-Path $templateDir) | Out-Null
                git clone --depth 1 https://github.com/flockmaster/flutter-ai-advanced-template.git $templateDir
                Write-Ok "已下载 flutter-ai-advanced-template"
            }
        }
    }
}

# 4.1.2 复制 .github/（Copilot prompts）
$githubSrc = Join-Path $ScriptDir ".github"
$githubDst = Join-Path $TargetDir ".github"
if (Test-Path $githubSrc) {
    if (Test-Path $githubDst) { Remove-Item $githubDst -Recurse -Force }
    Copy-Item $githubSrc $githubDst -Recurse -Force
    Write-Ok "已复制 .github/ → $githubDst"
} else {
    Write-Info "仓库中无 .github/，跳过复制"
}

# 4.2 清除 __pycache__
Get-ChildItem -Path $agentDst -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
Write-Ok "已清理 __pycache__"

# 4.3 写入 project_decisions.md
$today = Get-Date -Format "yyyy-MM-dd"
$decisionsContent = @"
---
project_name: $ProjectName
last_updated: $today
---

# Project Decisions (长期记忆 - 架构决策)

这里记录本项目中不可动摇的"宪法级"技术决策。
**更新机制**: 仅在重大架构变更时由架构师 Agent 更新。
**遗忘机制**: 新方案替代旧方案时，旧方案移至 Deprecated，一周后删除。

## 1. Tech Stack
- SDK: $($stack.sdk)
- Language: $($stack.lang)

## 2. Architecture
- Pattern: $($stack.arch)

## 3. Coding Standards
- Lint: ``$($stack.lint)``
- Formatting: ``$($stack.fmt)``
- Naming: (请根据语言规范填写)

## 4. Third-Party Libs (Whitelist)
> 在此登记项目允许使用的第三方库

| 库名 | 用途 | 添加日期 |
|------|------|---------|
| (示例) | (示例用途) | $today |

## 5. Known Issues (错误模式学习)

| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |
|------|---------|---------|---------|---------|

## 6. Deprecated (废弃决策归档)
<!-- 旧决策被覆盖后移至此处，保留一周后删除 -->

"@
Set-Content -Path "$agentDst\memory\project_decisions.md" -Value $decisionsContent -Encoding UTF8
Write-Ok "已初始化 project_decisions.md"

# 4.4 重置 active_context.md
$contextContent = @"
---
task_status: IDLE
last_session: $today
current_task: null
---

# Active Context (短期记忆 - 当前任务)

> 系统已初始化。输入 ``/start`` 开始你的第一个任务。

## Current Task
无

## History
| 日期 | 任务 | 状态 | 详情链接 |
|------|------|------|---------|

"@
Set-Content -Path "$agentDst\memory\active_context.md" -Value $contextContent -Encoding UTF8
Write-Ok "已重置 active_context.md"

# 4.5 更新 agent_config.md 中的 ACTIVE_PROVIDER
$configPath = "$agentDst\config\agent_config.md"
if (Test-Path $configPath) {
    (Get-Content $configPath -Raw) -replace 'ACTIVE_PROVIDER:\s*\w+', "ACTIVE_PROVIDER: $($provider.name)" |
        Set-Content $configPath -Encoding UTF8
    Write-Ok "已设置 ACTIVE_PROVIDER: $($provider.name)"
}

# 4.6 写入 .gitignore 追加
$gitignorePath = Join-Path $TargetDir ".gitignore"
$agentIgnoreBlock = @"

# === Antigravity Agent OS ===
# 动态文件 (不入库)
.agent/memory/active_context.md
.agent/memory/history/
.agent/memory/evolution/workflow_metrics.md
.agent/memory/evolution/learning_queue.md
.agent/memory/evolution/reflection_log.md
# agents (current)
.agents/memory/active_context.md
.agents/memory/history/
.agents/memory/evolution/workflow_metrics.md
.agents/memory/evolution/learning_queue.md
.agents/memory/evolution/reflection_log.md
# 编译缓存
.agent/**/__pycache__/
.agents/**/__pycache__/
"@

if (Test-Path $gitignorePath) {
    $existing = Get-Content $gitignorePath -Raw
    if ($existing -notmatch "Antigravity Agent OS") {
        Add-Content -Path $gitignorePath -Value $agentIgnoreBlock -Encoding UTF8
        Write-Ok "已追加 .gitignore 规则"
    } else {
        Write-Info ".gitignore 中已有 Agent OS 规则，跳过"
    }
} else {
    Set-Content -Path $gitignorePath -Value $agentIgnoreBlock.TrimStart() -Encoding UTF8
    Write-Ok "已创建 .gitignore"
}

# ============================================================
# Step 5: 安装全局配置
# ============================================================
Write-Step "Step 5/6 — 安装 AI 全局配置"

$adapterSrc = Join-Path $agentDst $provider.adapter
$globalDirExpanded = $ExecutionContext.InvokeCommand.ExpandString($provider.globalDir)
$globalFilePath = Join-Path $globalDirExpanded $provider.globalFile

Write-Host "   将把 Agent OS 规则安装到:" -ForegroundColor Yellow
Write-Host "   → $globalFilePath" -ForegroundColor White
Write-Host ""
Write-Host "   是否安装？(Y/n): " -NoNewline -ForegroundColor Yellow
$installGlobal = Read-Host
if ($installGlobal -eq "" -or $installGlobal -eq "y" -or $installGlobal -eq "Y") {
    if (-not (Test-Path $globalDirExpanded)) {
        New-Item -ItemType Directory -Path $globalDirExpanded -Force | Out-Null
    }
    if (Test-Path $globalFilePath) {
        $backupPath = "$globalFilePath.bak"
        Copy-Item $globalFilePath $backupPath -Force
        Write-Info "已备份原文件 → $backupPath"
    }
    Copy-Item $adapterSrc $globalFilePath -Force
    Write-Ok "已安装全局配置到 $globalFilePath"
} else {
    Write-Info "跳过全局配置安装。你可以之后手动复制:"
    Write-Info "  cp $adapterSrc $globalFilePath"
}

# ============================================================
# Step 6 (可选): 检测 Codex CLI (Dispatcher 功能)
# ============================================================
Write-Step "Step 6 (可选) — 检测 Codex CLI (任务调度器)"

$codexAvailable = $false
try {
    $null = Get-Command "codex" -ErrorAction Stop
    $codexAvailable = $true
    Write-Ok "Codex CLI 已安装，Dispatcher 可用"
} catch {
    Write-Info "Codex CLI 未安装 — Dispatcher 调度功能不可用"
    Write-Info "安装方法: npm install -g @openai/codex"
    Write-Info "安装后就能用 Antigravity 作为 PM 调度 Codex 执行大型 PRD"
}

# ============================================================
# 完成！
# ============================================================
Write-Host ""
Write-Host "   ╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "   ║   🎉 安装完成！                          ║" -ForegroundColor Green
Write-Host "   ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "   📂 项目: $ProjectName" -ForegroundColor White
Write-Host "   🔧 技术栈: $($stack.sdk) / $($stack.lang)" -ForegroundColor White
Write-Host "   🤖 AI 工具: $($provider.display)" -ForegroundColor White
if ($codexAvailable) {
    Write-Host "   🎯 Dispatcher: ✅ 可用" -ForegroundColor White
} else {
    Write-Host "   🎯 Dispatcher: ⚠️ 需安装 Codex CLI" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "   👉 下一步:" -ForegroundColor Cyan
Write-Host "      1. 在 IDE 中打开项目" -ForegroundColor White
Write-Host "      2. 对 AI 说: /start" -ForegroundColor White
Write-Host "      3. 开始享受不再失忆的 AI 体验！" -ForegroundColor White
Write-Host ""
