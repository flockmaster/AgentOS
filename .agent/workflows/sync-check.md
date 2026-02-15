---
description: Sync Check (v2.1) - 依赖同步检查：分析文件变更的连锁影响
---

# /sync-check - 依赖同步检查

> **"修改一个文件，连锁影响一目了然。"**

分析当前 git 变更文件的依赖关系，识别可能需要同步升级的关联文件。

## Trigger
- **自动触发**: 修改 `.agent/` 下的配置文件后，自动执行依赖影响分析 (见 CLAUDE.md §6.1)
- **自动触发**: `/evolve` 的 Step 4.5 自动调用
- **手动触发**: 用户输入 `/sync-check` 或 "同步检查" / "依赖检查" / "影响分析"

## Steps

### Step 1: 构建依赖图谱
1. 调用 `DependencyAnalyzer.build_graph()` 扫描 `.agent/` 目录。
2. 自动检测文件间的引用关系：
   - 工作流 → 技能调用 (`invokes`)
   - 工作流 → 工作流链式触发 (`chain_next`)
   - 文件 → 角色/规则引用 (`references`)
   - Python 模块 → import 依赖 (`imports`)
   - 工作流 → 记忆文件读写 (`reads`/`writes`)

### Step 2: 获取变更文件
1. 读取 `git diff --name-only` + `git ls-files --others` 获取所有变更文件。
2. 过滤出 `.agent/` 目录下的变更文件。

### Step 3: 影响分析
1. 对每个变更文件执行 `impact_analysis()`。
2. BFS 逐层传播，最多 3 层:
   - **直接依赖**: 直接引用了变更文件的文件
   - **二级依赖**: 引用了直接依赖的文件
   - **三级依赖**: 更远的传播链
3. 过滤掉同样已在变更列表中的文件 (已同步)。

### Step 4: 生成报告
输出格式化的影响分析报告:

```markdown
# 🔗 依赖同步检查报告

## 图谱概况
- **节点数**: X
- **边数**: X
- **类型分布**: workflow: X, skill: X, role: X, ...

## 变更文件
- `file1.md`
- `file2.py`

## 需要同步检查 (N 个文件)

### [直接依赖] `.agent/rules/router.rule`
- **关系**: references
- **描述**: 引用了被修改的工作流
- **传播链**: 1-drafting.md → router.rule

## 已同步的关联文件 (M 个)
- `file3.md`
```

### Step 5: 用户决策
- 提示用户逐个检查 "需要同步检查" 的文件。
- 用户可选择:
  - **逐个打开**: 依次查看每个需同步的文件
  - **全部跳过**: 确认当前变更无需连锁更新
  - **标记完成**: 手动确认某个文件已检查

## Post-Check Actions
1. 将同步检查结果记录到 `decision_log.md` (如有用户决策)。
2. 更新图谱中的 `version_hash` 以反映最新文件状态。
