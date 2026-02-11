# PRD 复杂度评估与拆解流水线 (Sub-Workflow)

本流程旨在解决大型项目 PRD "粗设" 无法直接指导开发的问题。通过引入工作量评估门禁，将复杂需求拆解为可执行的原子任务单元。

## ✅ 适用场景
- **复杂功能模块**: 涉及多个页面跳转或复杂状态机。
- **跨端协作**: 需要明确的前后端接口定义。
- **大型重构**: 涉及核心架构变更或数据迁移。
- **预估工时**: > 1 人日 (8 小时)。

## 🔄 流程图 (Mermaid)

```mermaid
graph TD
    %% 样式定义
    classDef actor fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef process fill:#fff3e0,stroke:#ff9800,stroke-width:2px;
    classDef gate fill:#ffebee,stroke:#b71c1c,stroke-width:4px;
    classDef artifact fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef subworkflow fill:#e0f2f1,stroke:#00695c,stroke-width:2px,stroke-dasharray: 5 5;
    classDef cloud fill:#e1f5fe,stroke:#01579b,stroke-width:2px,stroke-dasharray: 5 5;

    %% 上下文衔接 (Post-Approval)
    MainFlowStart(("🔗 来自主流程<br/>(Prd Confirmed)")):::cloud --> Input
    
    Input["📄 PRD (粗设终稿)"]:::artifact --> Read["📖 深度阅读 &<br/>上下文理解"]:::process
    
    Read --> GlobalMap["🗺️ 绘制业务全景图 &<br/>🚦 关键状态机 (按需)"]:::artifact
    
    GlobalMap --> DirSetup["📂 建立任务目录结构<br/>(docs/tasks/T-xxx/)"]:::process
    
    DirSetup --> Decompose["🧠 制定拆分策略 &<br/>🕸️ 识别依赖关系"]:::process

    Decompose --> InitManifest["📋 初始化任务清单 (Manifest)<br/>(含全景图/文件路径/状态)"]:::artifact

    subgraph "Content Generation (撰写详情)"
        direction TB
        InitManifest --> WriteSub["📝 撰写 Sub-PRD 内容<br/>(常规/按需图表)"]:::process
        WriteSub --> CheckCoverage{{"✅ 所有文件已生成?"}}:::process
        CheckCoverage -- "No" --> WriteSub
    end

    CheckCoverage -- "Yes" --> PMAudit{{"🤖 PM 终审<br/>(一致性/自洽性检查)"}}:::gate
    
    PMAudit -- "❌ 跑偏/冲突" --> Decompose
    
    PMAudit -- "✅ Pass" --> Summary["📝 生成简报 (Summary)"]:::artifact
    
    Summary --> UserGate{{"👤 用户最终确认<br/>(View Summary & Manifest)"}}:::gate
    
    UserGate -- "No" --> Decompose
    UserGate -- "Yes" --> Output["📦 交付用户<br/>(Summary + Manifest)"]:::artifact

    %% 输出衔接
    Output --> MainFlowEnd(("🔗 进入研发阶段<br/>(Implementation Phase)")):::cloud
```

## 📝 拆解标准与规范

### 1. 拆解维度
- **按技术栈**: 前端 UI / 后端 API / 数据库 Migration
- **按功能模块**: 用户系统 / 订单系统 / 支付网关
- **按依赖关系**: 核心基础层 -> 业务逻辑层 -> UI 表现层 (便于并行)

### 2. 子 PRD 必备要素
每个拆解后的子 PRD (Sub-PRD) 必须包含：
- **目标 (Goal)**: 明确单一职责。
- **状态 (Status)**: `[ ] Pending` / `[x] Done` (用于任务管理)。
- **依赖 (Dependencies)**: 明确前置任务 ID (如: `Pre: T-101`)。
- **输入/输出 (I/O)**: 数据结构定义。
- **流程图/状态机 (Optional)**: 仅当逻辑复杂时提供，简单增删改查可省略。
- **验收标准 (AC)**: Gherkin 格式的测试用例。

### 3. 输出物示例 (Manifest)
```markdown
# Task Manifest: 用户注册模块 (T-100)

## 1. 业务全景图
```mermaid
graph TD
  Start --> PhoneVerify --> Profile --> Complete
```

## 2. 任务列表
- [ ] **T-101: 短信服务接口**
  - Path: `docs/tasks/T-100/sub_prds/sms_service.md`
  - Desc: 对接阿里云短信 API
- [ ] **T-102: 手机号验证 UI**
  - Path: `docs/tasks/T-100/sub_prds/phone_ui.md`
  - Dep: T-101
  - Chart: (见子文档内部)
- [ ] **T-103: 用户资料补全**
  - Path: `docs/tasks/T-100/sub_prds/profile.md`
  - Dep: T-102
```
