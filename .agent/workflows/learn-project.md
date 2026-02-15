---
description: /learn-project — 从参考项目学习开发规范和架构模式
---

# 工作流：参考项目学习 (/learn-project)

本工作流从指定的参考项目中自动提取开发规范、架构设计和编码风格，生成知识卡片以确保后续代码风格一致。

## 触发方式

```
/learn-project [path]
```

- `[path]`: 参考项目的路径 (相对或绝对路径)
- 示例: `/learn-project .` (学习当前项目), `/learn-project ../other-project`

## 执行步骤

1. **验证项目路径**
   - 检查路径是否存在且为有效目录
   - 检查是否已在 `learned_projects.md` 中注册 (避免重复学习)
   - 若已学习过，提示用户确认是否重新学习

2. **检测项目类型**
   - 调用 `ProjectScanner.detect_project_type(path)`
   - 输出: 项目类型 (Flutter/React/Vue/Python/Go/Rust/Java)、主语言、检测置信度
   - 标志文件检测规则:
     | 标志文件 | 项目类型 |
     |---------|---------|
     | `pubspec.yaml` | Flutter/Dart |
     | `package.json` + `react` | React |
     | `package.json` + `vue` | Vue |
     | `pyproject.toml` / `setup.py` | Python |
     | `go.mod` | Go |
     | `Cargo.toml` | Rust |
     | `pom.xml` / `build.gradle` | Java/Kotlin |

3. **扫描目录结构**
   - 调用 `ProjectScanner.scan_structure(path)`
   - 限制: 最多扫描 1000 个文件
   - 输出: 文件数、目录数、层级深度、文件类型分布、顶级目录

4. **提取命名规范**
   - 调用 `ProjectScanner.extract_naming_conventions(path)`
   - 采样分析: 文件名、目录名、类名、函数名模式
   - 输出: snake_case / camelCase / kebab-case / PascalCase

5. **提取架构模式**
   - 调用 `ProjectScanner.extract_architecture_patterns(path)`
   - 检测: 分层结构、设计模式、状态管理、依赖注入
   - 输出: 架构分层列表、检测到的模式列表

6. **提取编码标准**
   - 调用 `ConventionExtractor.extract_coding_style(path)`
   - 检测: lint 配置、格式化规则、错误处理模式、import 风格
   - 输出: 编码风格概况

7. **提取依赖管理**
   - 调用 `ConventionExtractor.extract_dependency_patterns(path)`
   - 检测: 包管理器、依赖数量、版本策略、lock 文件
   - 输出: 依赖管理概况

8. **提取 Git 规范**
   - 调用 `ConventionExtractor.extract_git_conventions(path)`
   - 检测: Commit 消息格式、分支策略、CI 工具
   - 输出: Git 规范概况

9. **生成知识卡片 + 输出报告**
   - 调用 `ConventionExtractor.generate_knowledge_cards(...)` 生成 5-6 张知识卡片
   - 更新 `learned_projects.md` 注册表
   - 更新知识库索引
   - 输出学习报告，展示所有发现

## 输出格式

```markdown
# 📖 项目学习报告: {project_name}

## 基本信息
- **路径**: {path}
- **类型**: {type} ({language})
- **文件数**: {total_files} | **目录数**: {total_dirs}

## 命名规范
- 文件: {file_naming}
- 类: {class_pattern}
- 函数: {function_pattern}

## 架构模式
- 分层: {layers}
- 模式: {patterns}
- 状态管理: {state_management}

## 编码风格
- Lint: {lint_tools}
- 错误处理: {error_handling}

## 依赖管理
- 包管理器: {package_manager}
- 依赖数: {total_deps}

## Git 规范
- Commit 格式: {commit_format}
- 分支策略: {branch_strategy}

## 生成的知识卡片
- {k-xxx}: {title}
- {k-xxx}: {title}
...

---
学习完成! 共生成 {N} 张知识卡片。
```

## 限制

- 最多扫描 1000 个文件
- 代码采样分析限制 50 个文件
- 已学习的项目会在 `learned_projects.md` 中注册
