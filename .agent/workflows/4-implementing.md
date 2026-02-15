---
description: Phase 3: 实施、测试、编译与汇报生成工作流
---

# 工作流：实施交付 (Phase 3)

本工作流执行 Manifest 中的任务，通过逐任务质量门禁和全量编译保证质量，并交付可编译的版本。

## 前置条件
- 已确认的 Manifest 存在于 `docs/tasks/[id]/manifest.md`。
- Sub-PRD 文件存在于 `docs/tasks/[id]/sub_prds/` 目录下。
- 一致性审计表存在于 `docs/tasks/[id]/audit.md`（结论为"全部通过"）。

## 执行步骤

0.  **知识注入 + 模式脚手架 + 决策回放 (Knowledge Injection + Scaffolding + Replay)** — *v2.0*
    // turbo
    - **知识注入**: 调用 `KnowledgeInjector.retrieve_relevant(phase="implementing", keywords=[从 Manifest 提取])`。
    - **注入类别**: `pattern`, `debugging`, `tooling`, `reference-project`。
    - **模式脚手架**: 调用 `PatternScaffolder.suggest_and_scaffold(description)` 生成代码模板。
    - **决策回放**: 调用 `DecisionReplay.recommend(context)` 查找相似历史决策，提供推荐/避免选项。
    - **输出**: 将知识 + 模式 + 历史决策注入实施上下文。
    - **记录**: 追加注入事件到 `.agent/memory/evolution/injection_log.md`。

1.  **DAG 分析与分发 (DAG Analysis & Dispatch)**
    - **动作**: 读取 `manifest.md`。识别依赖已满足 (Ready to Start) 的任务。
    - **并行执行**:
        - **指令**: 对每个可并行任务，启动一个后台 `codex exec` 进程：
            ```powershell
            codex exec --full-auto "你是一名全栈开发专家。请完成以下任务:
            1. 阅读任务 Sub-PRD: [Sub-PRD Path]
            2. 阅读全局架构: docs/tasks/[id]/manifest.md §1 架构概览
            3. 遵循项目现有编码规范（命名、分层、错误处理）
            4. 编写代码实现 Sub-PRD 中定义的所有接口
            5. 为每个验收标准编写对应的单元测试
            6. 完成后运行 flutter analyze 和对应测试，确保全部通过
            7. 更新 Manifest 中该任务状态为 [x]
            " -o docs/tasks/[id]/implementation_[task_id].md
            ```
        - **并发控制**: 保持最多 3 个并行 Worker。
    - **循环**: 监控后台进程。任务完成后，进入 Step 2 单任务门禁。通过后检查 DAG 是否有新任务解锁。重复直至所有任务完成。

2.  **单任务质量门禁 (Per-Task Quality Gate)**
    - **触发**: 每个 Worker 完成代码编写后立即执行。
    - **检查项**:
        | 检查项 | 命令 / 动作 | 通过条件 |
        |--------|-----------|---------|
        | 静态分析 | `flutter analyze` | 无 error（warning 可接受） |
        | 单元测试 | `flutter test [对应测试文件]` | 全部 pass |
        | 验收覆盖 | 对照 Sub-PRD §5 验收标准 | 每条验收标准至少有 1 个对应测试 |
    - **通过**: 标记 Manifest 中该任务为 `[x]`，解锁下游任务。
    - **失败**:
        - 触发 `/analyze-error` 工作流（传入失败日志 + Sub-PRD 路径）。
        - 修复后重跑本步骤。
        - **熔断**: 同一任务连续 3 次失败，标记为 `BLOCKED`，跳过并继续其他任务。

3.  **全量编译门禁 (Full Compilation Gate)**
    - **触发**: 所有非 BLOCKED 任务通过 Step 2 后执行。
    - **动作**: 运行全量构建命令（如 `flutter build apk --debug`）。
    - **路径**:
        - **成功 (Exit Code 0)**: 进入 Step 4。
        - **失败**: 触发 `/analyze-error` 工作流 → 修复 → 重试。

4.  **汇报与交付 (Reporting & Handover)**
    - **动作**: 生成 **研发交付报告**。
    - **文件**: `docs/reports/rd_report_[date].md`
    - **报告模板**:
        ```markdown
        # 研发交付报告: [Feature Name]

        > **日期**: YYYY-MM-DD
        > **来源 PRD**: `docs/prd/[name]-rough.md`
        > **Manifest**: `docs/tasks/[id]/manifest.md`

        ## 1. 任务完成情况
        | 任务 | 名称 | 状态 | 测试数 | 备注 |
        |------|------|------|--------|------|
        | T-001 | ... | ✅ 完成 | N 个 | |
        | T-002 | ... | ✅ 完成 | N 个 | |
        | T-003 | ... | ❌ BLOCKED | — | [阻塞原因] |

        ## 2. 测试覆盖
        | 维度 | 数据 |
        |------|------|
        | 单元测试总数 | N |
        | 通过 / 失败 | N / 0 |
        | 验收标准覆盖率 | N / M (X%) |

        ## 3. 构建信息
        | 项目 | 值 |
        |------|-----|
        | 构建命令 | `flutter build apk --debug` |
        | 构建结果 | 成功 / 失败 |
        | 构建包路径 | `build/app/outputs/...` |
        | 静态分析 | 0 errors, N warnings |

        ## 4. 已知问题
        | # | 任务 | 问题描述 | 严重度 | 建议 |
        |---|------|---------|--------|------|
        | 1 | T-003 | ... | 高/中/低 | ... |

        ## 5. 飞书链接
        - [交付报告](URL)
        ```
    - **云端同步**: 调用 `feishu-doc-assistant` 上传报告，获取飞书链接。
    - **通知**: "交付完成！报告: [链接] | 构建包: [路径]"

5.  **知识收割 + 决策记录 (Evolution Hook)** — *v2.0*
    - **触发**: Step 4 完成后自动执行。
    - **知识收割**: 自动触发 `/evolve`，从本次实施中提取知识：
        - 代码模式 → `pattern` 类知识卡片
        - 遇到的 bug + 修复方案 → `debugging` 类知识卡片
        - 工具链经验 → `tooling` 类知识卡片
    - **决策记录**: 调用 `DecisionRecorder.record()`：
        - `phase`: "implementing"
        - `context`: 功能名称 + 完成/阻塞任务数
        - `chosen`: 关键技术选型（如状态管理方案、第三方库选择）
        - `knowledge_used`: Step 0 注入的知识 ID 列表
    - **结果追踪**: 对使用过的知识调用 `record_outcome()`，标记 success/failure。

## 完成
用户验收交付物。
