# ============================================================
# Antigravity Agent OS — Pre-commit Guard (T-301) [Windows]
#
# PowerShell 版本，适用于 Windows Git 环境
# 安装: Copy-Item .agent\guards\pre-commit.ps1 .git\hooks\pre-commit.ps1
# ============================================================

$CONTEXT_FILE = "active_context.md"
$GUARD_NAME = "Antigravity Guard"

# ── 1. 检查 active_context.md 是否被 staged ──
$stagedFiles = git diff --cached --name-only
if ($stagedFiles -notcontains $CONTEXT_FILE -and
    ($stagedFiles | Where-Object { $_ -like "*$CONTEXT_FILE" }).Count -eq 0) {
    Write-Host ""
    Write-Host "⚠️  [$GUARD_NAME] $CONTEXT_FILE 未在本次提交中更新。" -ForegroundColor Yellow
    Write-Host "   建议: 请确保任务状态已同步到记忆文件。" -ForegroundColor Yellow
    Write-Host "   提示: 执行 /suspend 可自动保存上下文。" -ForegroundColor Yellow
    Write-Host ""
    # 不阻断，仅警告
}

# ── 2. 检查是否有未解决的冲突标记 ──
$conflictFound = $false
foreach ($file in $stagedFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
        if ($content -match "<<<<<<<") {
            Write-Host "❌ [$GUARD_NAME] 检测到未解决的合并冲突: $file" -ForegroundColor Red
            $conflictFound = $true
        }
    }
}
if ($conflictFound) {
    Write-Host "   请手动解决冲突后再提交。" -ForegroundColor Red
    exit 1
}

# ── 3. 检查 .agent/ 中的 TODO/FIXME ──
$agentFiles = $stagedFiles | Where-Object { $_ -like ".agent/*" -or $_ -like ".agent\*" }
foreach ($file in $agentFiles) {
    if (Test-Path $file) {
        $matches = Select-String -Path $file -Pattern "TODO|FIXME|HACK|XXX" -ErrorAction SilentlyContinue
        if ($matches) {
            Write-Host ""
            Write-Host "💡 [$GUARD_NAME] $file 中发现 TODO/FIXME:" -ForegroundColor Cyan
            $matches | Select-Object -First 5 | ForEach-Object { Write-Host "   $_" }
            Write-Host ""
        }
    }
}

exit 0
