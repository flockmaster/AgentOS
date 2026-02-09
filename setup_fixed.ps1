#!/usr/bin/env pwsh
# ============================================================
#  Antigravity Agent OS 鈥?鍒濆鍖栧悜瀵?(Windows / PowerShell)
#  鐢ㄦ硶: pwsh setup.ps1 [-TargetDir <path>]
# ============================================================

param(
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 鈹€鈹€ 棰滆壊杈呭姪 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
function Write-Step  { param($msg) Write-Host "`n馃敡 $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "   鉁?$msg" -ForegroundColor Green }
function Write-Info  { param($msg) Write-Host "   鈩癸笍  $msg" -ForegroundColor DarkGray }
function Write-Warn  { param($msg) Write-Host "   鈿狅笍  $msg" -ForegroundColor Yellow }

# 鈹€鈹€ Banner 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
Write-Host ""
Write-Host "   鈺斺晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晽" -ForegroundColor Magenta
Write-Host "   鈺?  馃寣 Antigravity Agent OS 鈥?Setup        鈺? -ForegroundColor Magenta
Write-Host "   鈺?  缁欎綘鐨?AI 缂栫▼鍔╂墜瑁呬笂澶ц剳              鈺? -ForegroundColor Magenta
Write-Host "   鈺氣晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨暆" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: 閫夋嫨鐩爣椤圭洰
# ============================================================
Write-Step "Step 1/6 鈥?璁剧疆鐩爣椤圭洰"

if ($TargetDir -eq "") {
    Write-Host "   璇疯緭鍏ヤ綘鐨勯」鐩矾寰?(鐣欑┖ = 褰撳墠鐩綍): " -NoNewline -ForegroundColor Yellow
    $TargetDir = Read-Host
    if ($TargetDir -eq "") { $TargetDir = Get-Location }
}
$TargetDir = Resolve-Path $TargetDir -ErrorAction SilentlyContinue
if (-not $TargetDir -or -not (Test-Path $TargetDir)) {
    Write-Host "   鉂?璺緞涓嶅瓨鍦? $TargetDir" -ForegroundColor Red
    exit 1
}
Write-Ok "鐩爣鐩綍: $TargetDir"

# 妫€娴嬫槸鍚﹀凡鍒濆鍖?
if (Test-Path "$TargetDir\.agent\memory\active_context.md") {
    Write-Warn "妫€娴嬪埌璇ラ」鐩凡瀹夎 Agent OS (.agent/ 宸插瓨鍦?銆?
    Write-Host "   鏄惁瑕嗙洊閰嶇疆锛?y/N): " -NoNewline -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "   馃憢 宸插彇娑堛€? -ForegroundColor Gray
        exit 0
    }
}

# ============================================================
# Step 2: 椤圭洰淇℃伅
# ============================================================
Write-Step "Step 2/6 鈥?椤圭洰淇℃伅"

Write-Host "   椤圭洰鍚嶇О: " -NoNewline -ForegroundColor Yellow
$ProjectName = Read-Host
if ($ProjectName -eq "") { $ProjectName = Split-Path -Leaf $TargetDir }

Write-Host ""
Write-Host "   閫夋嫨鎶€鏈爤:" -ForegroundColor Yellow
Write-Host "     [1] Flutter / Dart"
Write-Host "     [2] React / TypeScript"
Write-Host "     [3] Vue / TypeScript"
Write-Host "     [4] Python / Django"
Write-Host "     [5] Node.js / Express"
Write-Host "     [6] Go / Gin"
Write-Host "     [0] 鑷畾涔?
Write-Host "   杈撳叆缂栧彿 (榛樿 1): " -NoNewline -ForegroundColor Yellow
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
    Write-Host "   SDK/妗嗘灦: " -NoNewline; $customSdk = Read-Host
    Write-Host "   璇█: " -NoNewline;     $customLang = Read-Host
    Write-Host "   鏋舵瀯: " -NoNewline;     $customArch = Read-Host
    $stack = @{ sdk = $customSdk; lang = $customLang; arch = $customArch; lint = "N/A"; fmt = "N/A"; run = "N/A"; test = "N/A"; analyze = "N/A"; build = "N/A" }
} else {
    $stack = $TechStacks[$stackChoice]
    if (-not $stack) { $stack = $TechStacks["1"] }
}

Write-Ok "椤圭洰: $ProjectName | $($stack.sdk) / $($stack.lang) / $($stack.arch)"

# ============================================================
# Step 3: 閫夋嫨 AI 宸ュ叿
# ============================================================
Write-Step "Step 3/6 鈥?閫夋嫨浣犵殑 AI 缂栫▼宸ュ叿"

Write-Host "     [1] Gemini (Google AI / Android Studio)"
Write-Host "     [2] GitHub Copilot (VS Code / JetBrains)"
Write-Host "     [3] Claude (Anthropic / Cursor)"
Write-Host "   杈撳叆缂栧彿 (榛樿 1): " -NoNewline -ForegroundColor Yellow
$aiChoice = Read-Host
if ($aiChoice -eq "") { $aiChoice = "1" }

$providers = @{
    "1" = @{ name = "gemini";  display = "Gemini";  adapter = "adapters/gemini/GEMINI.md";  globalDir = "$env:USERPROFILE\.gemini"; globalFile = "GEMINI.md" }
    "2" = @{ name = "copilot"; display = "Copilot"; adapter = "adapters/copilot/copilot-instructions.md"; globalDir = "$env:USERPROFILE\.copilot"; globalFile = "copilot-instructions.md" }
    "3" = @{ name = "claude";  display = "Claude";  adapter = "adapters/claude/CLAUDE.md";  globalDir = "$env:USERPROFILE\.claude"; globalFile = "CLAUDE.md" }
}
$provider = $providers[$aiChoice]
if (-not $provider) { $provider = $providers["1"] }
Write-Ok "AI 宸ュ叿: $($provider.display)"

# ============================================================
# Step 4: 澶嶅埗鏂囦欢骞跺垵濮嬪寲
# ============================================================
Write-Step "Step 4/6 鈥?瀹夎 Agent OS 鍒伴」鐩?

# 4.1 澶嶅埗 .agent/ 鐩綍
$agentSrc = Join-Path $ScriptDir ".agent"
$agentDst = Join-Path $TargetDir ".agent"

if ($agentSrc -ne $agentDst) {
    if (Test-Path $agentDst) { Remove-Item $agentDst -Recurse -Force }
    Copy-Item $agentSrc $agentDst -Recurse -Force
    Write-Ok "宸插鍒?.agent/ 鈫?$agentDst"
} else {
    Write-Ok ".agent/ 宸插湪褰撳墠鐩綍锛岃烦杩囧鍒?
}

# 4.2 娓呴櫎 __pycache__
Get-ChildItem -Path $agentDst -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
Write-Ok "宸叉竻鐞?__pycache__"

# 4.3 鍐欏叆 project_decisions.md
$today = Get-Date -Format "yyyy-MM-dd"
$decisionsContent = @"
---
project_name: $ProjectName
last_updated: $today
---

# Project Decisions (闀挎湡璁板繂 - 鏋舵瀯鍐崇瓥)

杩欓噷璁板綍鏈」鐩腑涓嶅彲鍔ㄦ憞鐨?瀹硶绾?鎶€鏈喅绛栥€?
**鏇存柊鏈哄埗**: 浠呭湪閲嶅ぇ鏋舵瀯鍙樻洿鏃剁敱鏋舵瀯甯?Agent 鏇存柊銆?
**閬楀繕鏈哄埗**: 鏂版柟妗堟浛浠ｆ棫鏂规鏃讹紝鏃ф柟妗堢Щ鑷?Deprecated锛屼竴鍛ㄥ悗鍒犻櫎銆?

## 1. Tech Stack
- SDK: $($stack.sdk)
- Language: $($stack.lang)

## 2. Architecture
- Pattern: $($stack.arch)

## 3. Coding Standards
- Lint: ``$($stack.lint)``
- Formatting: ``$($stack.fmt)``
- Naming: (璇锋牴鎹瑷€瑙勮寖濉啓)

## 4. Third-Party Libs (Whitelist)
> 鍦ㄦ鐧昏椤圭洰鍏佽浣跨敤鐨勭涓夋柟搴?

| 搴撳悕 | 鐢ㄩ€?| 娣诲姞鏃ユ湡 |
|------|------|---------|
| (绀轰緥) | (绀轰緥鐢ㄩ€? | $today |

## 5. Known Issues (閿欒妯″紡瀛︿範)

| 鏃ユ湡 | 閿欒绫诲瀷 | 鏍瑰洜鍒嗘瀽 | 淇鏂规 | 褰卞搷鑼冨洿 |
|------|---------|---------|---------|---------|

## 6. Deprecated (搴熷純鍐崇瓥褰掓。)
<!-- 鏃у喅绛栬瑕嗙洊鍚庣Щ鑷虫澶勶紝淇濈暀涓€鍛ㄥ悗鍒犻櫎 -->

"@
Set-Content -Path "$agentDst\memory\project_decisions.md" -Value $decisionsContent -Encoding UTF8
Write-Ok "宸插垵濮嬪寲 project_decisions.md"

# 4.4 閲嶇疆 active_context.md
$contextContent = @"
---
task_status: IDLE
last_session: $today
current_task: null
---

# Active Context (鐭湡璁板繂 - 褰撳墠浠诲姟)

> 绯荤粺宸插垵濮嬪寲銆傝緭鍏?``/start`` 寮€濮嬩綘鐨勭涓€涓换鍔°€?

## Current Task
鏃?

## History
| 鏃ユ湡 | 浠诲姟 | 鐘舵€?| 璇︽儏閾炬帴 |
|------|------|------|---------|

"@
Set-Content -Path "$agentDst\memory\active_context.md" -Value $contextContent -Encoding UTF8
Write-Ok "宸查噸缃?active_context.md"

# 4.5 鏇存柊 agent_config.md 涓殑 ACTIVE_PROVIDER
$configPath = "$agentDst\config\agent_config.md"
if (Test-Path $configPath) {
    (Get-Content $configPath -Raw) -replace 'ACTIVE_PROVIDER:\s*\w+', "ACTIVE_PROVIDER: $($provider.name)" |
        Set-Content $configPath -Encoding UTF8
    Write-Ok "宸茶缃?ACTIVE_PROVIDER: $($provider.name)"
}

# 4.6 鍐欏叆 .gitignore 杩藉姞
$gitignorePath = Join-Path $TargetDir ".gitignore"
$agentIgnoreBlock = @"

# === Antigravity Agent OS ===
# 鍔ㄦ€佹枃浠?(涓嶅叆搴?
.agent/memory/active_context.md
.agent/memory/history/
.agent/memory/evolution/workflow_metrics.md
.agent/memory/evolution/learning_queue.md
.agent/memory/evolution/reflection_log.md
# 缂栬瘧缂撳瓨
.agent/**/__pycache__/
"@

if (Test-Path $gitignorePath) {
    $existing = Get-Content $gitignorePath -Raw
    if ($existing -notmatch "Antigravity Agent OS") {
        Add-Content -Path $gitignorePath -Value $agentIgnoreBlock -Encoding UTF8
        Write-Ok "宸茶拷鍔?.gitignore 瑙勫垯"
    } else {
        Write-Info ".gitignore 涓凡鏈?Agent OS 瑙勫垯锛岃烦杩?
    }
} else {
    Set-Content -Path $gitignorePath -Value $agentIgnoreBlock.TrimStart() -Encoding UTF8
    Write-Ok "宸插垱寤?.gitignore"
}

# ============================================================
# Step 5: 瀹夎鍏ㄥ眬閰嶇疆
# ============================================================
Write-Step "Step 5/6 鈥?瀹夎 AI 鍏ㄥ眬閰嶇疆"

$adapterSrc = Join-Path $agentDst $provider.adapter
$globalDirExpanded = $ExecutionContext.InvokeCommand.ExpandString($provider.globalDir)
$globalFilePath = Join-Path $globalDirExpanded $provider.globalFile

Write-Host "   灏嗘妸 Agent OS 瑙勫垯瀹夎鍒?" -ForegroundColor Yellow
Write-Host "   鈫?$globalFilePath" -ForegroundColor White
Write-Host ""
Write-Host "   鏄惁瀹夎锛?Y/n): " -NoNewline -ForegroundColor Yellow
$installGlobal = Read-Host
if ($installGlobal -eq "" -or $installGlobal -eq "y" -or $installGlobal -eq "Y") {
    if (-not (Test-Path $globalDirExpanded)) {
        New-Item -ItemType Directory -Path $globalDirExpanded -Force | Out-Null
    }
    if (Test-Path $globalFilePath) {
        $backupPath = "$globalFilePath.bak"
        Copy-Item $globalFilePath $backupPath -Force
        Write-Info "宸插浠藉師鏂囦欢 鈫?$backupPath"
    }
    Copy-Item $adapterSrc $globalFilePath -Force
    Write-Ok "宸插畨瑁呭叏灞€閰嶇疆鍒?$globalFilePath"
} else {
    Write-Info "璺宠繃鍏ㄥ眬閰嶇疆瀹夎銆備綘鍙互涔嬪悗鎵嬪姩澶嶅埗:"
    Write-Info "  cp $adapterSrc $globalFilePath"
}

# ============================================================
# Step 6 (鍙€?: 妫€娴?Codex CLI (Dispatcher 鍔熻兘)
# ============================================================
Write-Step "Step 6 (鍙€? 鈥?妫€娴?Codex CLI (浠诲姟璋冨害鍣?"

$codexAvailable = $false
try {
    $null = Get-Command "codex" -ErrorAction Stop
    $codexAvailable = $true
    Write-Ok "Codex CLI 宸插畨瑁咃紝Dispatcher 鍙敤"
} catch {
    Write-Info "Codex CLI 鏈畨瑁?鈥?Dispatcher 璋冨害鍔熻兘涓嶅彲鐢?
    Write-Info "瀹夎鏂规硶: npm install -g @openai/codex"
    Write-Info "瀹夎鍚庡氨鑳界敤 Antigravity 浣滀负 PM 璋冨害 Codex 鎵ц澶у瀷 PRD"
}

# ============================================================
# 瀹屾垚锛?
# ============================================================
Write-Host ""
Write-Host "   鈺斺晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晽" -ForegroundColor Green
Write-Host "   鈺?  馃帀 瀹夎瀹屾垚锛?                         鈺? -ForegroundColor Green
Write-Host "   鈺氣晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨暆" -ForegroundColor Green
Write-Host ""
Write-Host "   馃搨 椤圭洰: $ProjectName" -ForegroundColor White
Write-Host "   馃敡 鎶€鏈爤: $($stack.sdk) / $($stack.lang)" -ForegroundColor White
Write-Host "   馃 AI 宸ュ叿: $($provider.display)" -ForegroundColor White
if ($codexAvailable) {
    Write-Host "   馃幆 Dispatcher: 鉁?鍙敤" -ForegroundColor White
} else {
    Write-Host "   馃幆 Dispatcher: 鈿狅笍 闇€瀹夎 Codex CLI" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "   馃憠 涓嬩竴姝?" -ForegroundColor Cyan
Write-Host "      1. 鍦?IDE 涓墦寮€椤圭洰" -ForegroundColor White
Write-Host "      2. 瀵?AI 璇? /start" -ForegroundColor White
Write-Host "      3. 寮€濮嬩韩鍙椾笉鍐嶅け蹇嗙殑 AI 浣撻獙锛? -ForegroundColor White
Write-Host ""
