---
description: Panic Button - 错误智能分析与修复
---

# Error Analysis Workflow (错误分析工作流)

当 `feature-flow` 遇到熔断（3 次修复失败）、单任务质量门禁失败、或用户直接抛出报错时触发。

## Phase 1: 日志收集 (Log Collection)

1. **收集构建日志**: 读取 `flutter run` / `flutter analyze` 的完整输出。
2. **收集测试日志**: 读取 `flutter test` 的失败详情。
3. **收集 Git 差异**: `git diff HEAD~1` 查看最近的代码变更。
4. **收集上下文**:
   - 读取 `.agent/memory/active_context.md` 中的 `last_checkpoint`。
   - 读取触发本次分析的 Sub-PRD（如有）。

## Phase 2: 差异分析 (Diff Analysis)

5. **获取检查点**: 从 `active_context.md` 读取 `last_checkpoint`。
6. **对比差异**: `git diff [last_checkpoint]..HEAD`
7. **定位变更文件**: 识别出问题可能出在哪些文件。

## Phase 3: 根因分析 (Root Cause Analysis)

8. **知识库匹配**:
   - 调用 `KnowledgeInjector.retrieve_relevant(phase="error-analysis", keywords=[从错误日志提取])`。
   - 检索 `debugging` 和 `anti-pattern` 类知识卡片。
   - **IF 匹配到高置信度知识 (confidence > 0.8)**: 直接应用历史修复方案。
9. **外部搜索**: 如确需外部资料，优先让用户提供链接/关键词；在 Copilot 环境下可用 `fetch_webpage` 读取指定 URL 内容。
10. **AI 推理**: 基于上下文、错误日志、差异分析推断可能的根因。

## Phase 4: 解决方案 (Resolution)

### Option A - 自动修复 (高置信度)
- **条件**: 置信度 > 80%
- **动作**: 自动应用修复 → 重新运行验证（analyze + test）
- **成功**: 返回调用方，继续流程。
- **失败**: 降级为 Option B。

### Option B - 回滚 (Rollback)
- **⚠️ 用户确认**: 回滚前必须询问用户：
  > "自动修复失败。是否回滚到检查点 [tag]？这将丢弃 [N 个文件] 的变更。"
- **用户确认后执行**:
  - `git reset --hard [last_checkpoint]`
  - 清理: `git stash drop`（如有）
  - 输出: "已回滚到检查点 [tag]"

### Option C - 跳过任务 (Skip Task)
- **动作**: 将当前 Task 标记为 `BLOCKED`
- **记录**: 在 Manifest 中标注阻塞原因
- **继续**: 执行队列中的下一个任务
- **输出**: "Task-X 已跳过（原因: [...]），请后续手动处理"

## Phase 5: 学习记录 (Knowledge Harvesting)

11. **生成知识卡片**: 调用 `KnowledgeHarvester.harvest()`：
    - `source_type`: "error_fix"
    - `title`: 错误类型简述
    - `summary`: 根因 + 修复方案一句话概述
    - `category`: "debugging"
    - `tags`: [错误类型, 涉及模块, 语言/框架]
    - `code_example`: 修复前后的代码对比
12. **记录结果**: 调用 `CausalMetrics.record_outcome()`：
    - `knowledge_id`: 新生成的知识卡片 ID（或匹配到的已有卡片 ID）
    - `result`: "success" / "failure"
    - `task`: 当前任务 ID
    - `notes`: 修复过程备注
13. **更新上下文**: 在 `active_context.md` 的 Scratchpad 中记录此次错误的简要描述。

## Quick Reference (快速参考)

```bash
# 查看最近的检查点
git tag | grep checkpoint | tail -5

# 查看检查点到现在的变更
git diff checkpoint-YYYYMMDD-HHMMSS..HEAD --stat

# 回滚到检查点 (需用户确认)
git reset --hard checkpoint-YYYYMMDD-HHMMSS

# 查询知识库中的错误模式
# → 通过进化引擎: KnowledgeInjector.retrieve_relevant(phase="error-analysis", keywords=["错误关键词"])
```
