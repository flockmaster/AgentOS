---
description: 待学习队列 - 记录待提取和处理的学习素材
version: 1.0
last_updated: 2026-02-09
---

# Learning Queue (待学习队列)

记录待处理的学习素材，由 Knowledge Harvester 在空闲时处理。

## 1. 队列状态

| Metric | Value |
|--------|-------|
| 待处理 | 0 |
| 处理中 | 0 |
| 今日已处理 | 1 |

## 2. 待学习素材 (Pending Items)

| ID | Source Type | Source ID | Priority | Created | Status |
|----|-------------|-----------|----------|---------|--------|
| - | - | - | - | - | 队列为空 |

### Source Types
- `conversation`: 对话记录
- `code_change`: 代码变更
- `error_fix`: 错误修复
- `workflow_run`: 工作流执行
- `user_feedback`: 用户反馈

### Priority Levels
- `P0`: 立即处理（重大发现）
- `P1`: 高优先级（成功经验）
- `P2`: 正常处理
- `P3`: 低优先级（可选）

## 3. 处理规则

### 3.1 自动入队触发器
- 任务完成后 → 添加 `code_change` 素材
- 错误修复后 → 添加 `error_fix` 素材
- 工作流完成 → 添加 `workflow_run` 素材

### 3.2 处理时机
- 状态变为 IDLE 时处理队列
- `/evolve` 命令强制处理

### 3.3 处理流程
```
1. 取出队列头部素材
2. 分析素材内容
3. 提取知识/模式
4. 更新 knowledge_base.md / pattern_library.md
5. 标记素材为已处理
```

## 4. 已处理历史 (Processed History)

| Date | Source Type | Source ID | Output | Notes |
|------|-------------|-----------|--------|-------|
| 2026-02-09 | conversation | system-validation | k-005 | System Validation Pattern 知识条目 |
