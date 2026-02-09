---
project_name: Generic Flutter Project
last_updated: 2026-02-08
---

# Project Decisions (长期记忆 - 架构决策)

这里记录本项目中不可动摇的"宪法级"技术决策。
**更新机制**: 仅在重大架构变更（如换库、换架构）时由架构师 Agent 更新。
**遗忘机制**: 当引入新方案替代旧方案时，旧方案移动到 `## Deprecated` 章节，一周后删除。

## 1. Tech Stack
- SDK: Flutter
- Language: Dart

## 2. Architecture
## 3. Coding Standards
- Lint: `flutter_lints`
- Formatting: `dart format`
- Naming: LowerCamelCase for variables, UpperCamelCase for classes.

## 4. Third-Party Libs (Whitelist)
- `stacked`: (Architecture / State Management) - [推断自现有习惯]
- `provider`: (Dependency Injection)
- `json_serializable`: (JSON)
- `shared_preferences`: (Local Storage)

## 5. Known Issues (错误模式学习)
> 格式: | 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |

| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |
|------|---------|---------|---------|---------|
| 2026-02-08 | (示例) Build Error | Pub 依赖缺失 | `flutter pub get` | 全局 |

## 6. Deprecated (废弃决策归档)
> 旧决策被新决策覆盖后移至此处，保留一周后删除。

<!-- 格式: [DEPRECATED 日期] 原决策内容 | 替代方案 | 删除日期 -->

