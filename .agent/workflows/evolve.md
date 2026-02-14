---
description: Evolve Workflow (v2.0) - 主动进化引擎：代码巡检、模式挖掘、文档同步
---

# /evolve - 进化引擎 v2.0

> **"不仅仅是记录，而是主动优化。"**

手动触发 **Agent OS 自进化周期**。不仅处理被动学习队列，更主动扫描代码库中的技术债务、重复模式和过期文档，生成可执行的优化提案。

## Trigger
- 用户输入 `/evolve` 或 "进化" / "优化系统"

## Steps

### Step 1: 学习队列处理 (Legacy Support)
// turbo
1. 读取 `.agent/memory/evolution/learning_queue.md`。
2. 如果有待处理项：
   - 提取知识点 -> 写入 `.agent/memory/knowledge/topic_<tag>.md` (分布式存储)。
   - 标记为 `DONE`。

### Step 2: 代码库健康巡检 (Active Scanning)
// turbo
1. **Tech Debt Scan**: 
   - 全局搜索 `TODO:`, `FIXME:`, `HACK:`, `XXX:`。
   - 统计数量，按文件分组。
   - 生成 "Technical Debt Report"。
2. **Hotspot Analysis**:
   - 分析最近 50 次 Commit (`git log --name-only`)。
   - 找出修改频率最高的前 5 个文件 (Hotspots)。
   -如果 Hotspot 文件超过 500 行，建议拆分。

### Step 3: 模式挖掘与重构建议 (Pattern Mining)
1. **Duplication Check**:
   - 检查重复出现的代码结构 (如相似的 Boilerplate)。
   - 如果发现 (Occurrences >= 3)，生成 "Refactoring Proposal"。
   - 建议提取为 `Shared Component` 或 `Utility`。
2. **Architecture Compliance**:
   - 检查是否违反了 `.agent/memory/project_decisions.md` 中的架构规则 (e.g. View层直接调用Database)。

### Step 4: 文档同步检查 (Doc Sync)
4. **Documentation & Config Sync (Configuration Drift)**:
   - **Installation Scripts**: 
     - 检查 `setup.ps1` / `setup.sh` 是否包含所有最新的 `.agent` 组件 (如 `.vscode`, `Watchdog`)。
   - **Copilot Prompts**:
     - 检查 `.github/` 下的 prompts 是否覆盖了新增的 Workflow (`.agent/workflows/*.md`)。
   - **Adapter Mirroring**:
     - 对比 `.agent/adapters/gemini/GEMINI.md` (Source) 与 `.gemini/GEMINI.md` (Target) 的差异。
     - 如果 Source 更新，标记为 "Need Sync"。
   - **README Check**:
     - 检查 `README.md` 中引用的文件是否存在。
   - **Decision Log**:
     - 检查 `project_decisions.md` 中的 "Known Issues" 是否已在代码中被修复。

### Step 5: 生成进化报告 (Evolution Report)
输出一份包含 **Actionable Items** 的报告，等待用户批准执行。

## Output Format (Interactive)

```markdown
# 🧬 Evolution Report (v2.0)

## 1. 🧠 Knowledge Base
- **New Insights**: [Summary of learning_queue]
- **Storage**: `knowledge/topic_*.md` updated.

## 2. 🏥 Code Health
- **Debt Score**: [Low/Medium/High]
- **Found Tags**:
  - `TODO`: 5 items (See `debt_report.md`)
  - `FIXME`: 2 critical items
- **Hotspots**:
  - `lib/main.dart` (Modified 12 times in 3 days) -> 建议拆分

## 3. 💡 Refactoring Proposals
> 以下模式可优化：
1. **[Pattern Name]**: Found 3 duplicates in [Files].
   - **Action**: Extract to `utils/input_validator.dart`?
   - **Command**: `/refactor input_validator`

## 4. 📚 Doc Sync
- `README.md`: Links are valid ✅ / Broken ❌
- `project_decisions.md`: 2 Deprecated decisions found.

---
**Reply with:**
- `/approve` to execute high-confidence fixes (Docs & Knowledge).
- `/refactor <name>` to start a specific refactoring task.
- `/ignore` to skip this cycle.
```

## Post-Evolve Actions (Automated)
1. 将 "High Confidence" 的知识点自动归档。
2. 将 "Technical Debt" 统计写入 `metrics.md` 以追踪趋势。
