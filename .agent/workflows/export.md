---
description: Export Command - 导出 Agent OS 系统为可移植压缩包
---

# /export - 系统导出

从当前项目中提取 **Antigravity Agent OS** 的完整或模板版本，生成可复用的压缩包。

## Trigger
- 用户输入 `/export` 或 `/export template` 或 `/export full`

## 导出模式

### 模式 1: Template (模板导出) - 默认
用于创建新项目时的干净起点。

**包含**:
- `.agent/` 目录结构（兼容旧结构）
- `.agents/` 目录结构（当前主结构：memory/skills/workflows）
- `.github/`（Copilot 配置与 Prompt Files）
- `.gemini/GEMINI.md.example`（如存在）
- `README.md`

**清空/重置**:
- `active_context.md` → 重置为初始模板
- `knowledge/` → 清空，只保留 `.gitkeep`
- `evolution/*.md` → 重置为初始模板
- `history/` → 清空

**保留**:
- 所有工作流定义 (`workflows/*.md`)
- 所有技能定义 (`skills/*/SKILL.md`)
- 路由规则 (`rules/router.rule`)
- 状态机定义 (`state_machine.md`)
- 用户偏好模板 (`user_preferences.md`)
- 项目决策模板 (`project_decisions.md`)

### 模式 2: Full (完整导出)
用于备份或迁移整个系统状态。

**包含**: 所有文件，原样打包。

## Steps

### Step 1: 确定导出模式
// turbo
1. 解析用户输入，确定是 `template` 还是 `full`。
2. 默认为 `template`。

### Step 2: 创建临时目录
```bash
exportDir="$(mktemp -d -t antigravity-export-XXXXXXXX)"
echo "Export temp dir: $exportDir"
```

### Step 3: 复制系统文件
```bash
rsync -a .agent "$exportDir/" 2>/dev/null || true
rsync -a .agents "$exportDir/" 2>/dev/null || true
[ -d .github ] && rsync -a .github "$exportDir/"
[ -d .gemini ] && rsync -a .gemini "$exportDir/"
rsync -a README.md "$exportDir/"
```

### Step 4: Template 模式清理 (仅 template 模式)
1. 重置 `active_context.md`:
   ```yaml
   ---
   session_id: null
   task_status: IDLE
   auto_fix_attempts: 0
   last_checkpoint: null
   stash_applied: false
   ---
   ```
2. 清空 `knowledge/` 目录，保留 `.gitkeep`
3. 重置 `evolution/` 目录下的所有文件为初始模板
4. 清空 `history/` 目录

### Step 5: 生成压缩包
```bash
zipName="antigravity-agent-os-$(date +%Y%m%d).zip"
(cd "$exportDir" && zip -rq "$PWD/../$zipName" .)
echo "Output: $zipName"
```

### Step 6: 清理临时目录
```bash
rm -rf "$exportDir"
```

### Step 7: 输出结果
报告压缩包位置和大小。

## Output Format
```markdown
## 📦 Export Complete

**Mode**: Template / Full
**Output**: `antigravity-agent-os-20260208.zip`
**Size**: X KB
**Location**: [Full Path]

### Included
- `.agent/` (workflows, skills, rules, memory templates)
- `.gemini/GEMINI.md.example`
- `README.md`

### Usage
1. 解压到新项目根目录
2. 编辑 `.agents/memory/project_decisions.md` 配置项目信息
3. 如存在 `.gemini/GEMINI.md.example`，复制其内容到全局配置
4. 输入 `/start` 开始使用
```

## 使用示例

| 命令 | 效果 |
|-----|-----|
| `/export` | 导出模板版本（干净） |
| `/export template` | 同上 |
| `/export full` | 导出完整版本（含所有知识） |
