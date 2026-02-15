---
name: project-learner
description: 项目学习技能 (v2.0)。从参考项目自动提取开发规范、架构设计和编码风格，生成知识卡片确保后续代码风格一致。
---

# Project Learner (项目学习技能)

本技能让 Agent 从参考项目中"学习"，提取最佳实践和规范，确保后续生成的代码风格一致。

---

## 0. 核心理念

> "学习优秀项目的规范，让每一行生成的代码都风格一致。"

- **Convention over Configuration**: 从项目实际代码中学习规范，而非依赖文档
- **Non-Invasive**: 只读扫描，不修改参考项目
- **Knowledge Reuse**: 学到的知识自动注入后续工作流

---

## 1. 触发方式

| 触发 | 方式 |
|------|------|
| `/learn-project [path]` | 主动学习指定项目 |
| "学习这个项目" | 自然语言触发 |
| "参考项目规范" | 自然语言触发 |

---

## 2. 扫描策略

### 2.1 安全限制
- **文件上限**: 最多扫描 1000 个文件
- **采样分析**: 代码文件采样 50 个进行深度分析
- **大小限制**: 跳过 > 100KB 的文件
- **忽略目录**: `.git`, `node_modules`, `build`, `dist`, `__pycache__`, `target`, `vendor`

### 2.2 扫描模块

| 模块 | 类 | 提取内容 |
|------|-----|---------|
| 项目类型检测 | `ProjectScanner` | 类型、语言、框架 |
| 结构扫描 | `ProjectScanner` | 文件分布、目录层级 |
| 命名规范 | `ProjectScanner` | 文件/类/函数命名模式 |
| 架构模式 | `ProjectScanner` | 分层、设计模式、DI |
| 编码风格 | `ConventionExtractor` | Lint、格式化、错误处理 |
| 依赖管理 | `ConventionExtractor` | 包管理器、版本策略 |
| Git 规范 | `ConventionExtractor` | Commit 格式、分支策略 |

---

## 3. 知识生成

每次学习生成 5-6 张知识卡片:

| 卡片 | 类别 | 说明 |
|------|------|------|
| 项目概览 | reference-project | 类型、结构、文件分布 |
| 命名规范 | reference-project | 命名风格和示例 |
| 架构模式 | reference-project | 分层和设计模式 |
| 编码风格 | reference-project | Lint、格式化规则 |
| 依赖管理 | reference-project | 包管理器和依赖 |
| Git 规范 | reference-project | Commit 和分支策略 |

---

## 4. 知识应用

学到的知识通过闭环反馈自动注入:
- **Drafting 阶段**: 注入参考项目的架构决策
- **Implementing 阶段**: 注入编码规范和命名风格
- **Reviewing 阶段**: 注入架构模式作为评审基准

---

## 5. 支持的项目类型

| 类型 | 标志文件 | 深度分析 |
|------|---------|---------|
| Flutter/Dart | `pubspec.yaml` | 状态管理、DI 模式 |
| React | `package.json` + react | 组件结构、状态管理 |
| Vue | `package.json` + vue | 组件结构、状态管理 |
| Python | `pyproject.toml` / `setup.py` | 包结构、类型提示 |
| Go | `go.mod` | 包组织、错误处理 |
| Rust | `Cargo.toml` | 模块结构、所有权模式 |
| Java/Kotlin | `pom.xml` / `build.gradle` | DI 模式、层结构 |

---

_Last Updated: 2026-02-14_
