<div align="center">

# 🌌 Antigravity Agent OS

### 给你的 AI 编程助手装上"大脑"

<br/>

**让 AI 不再是金鱼记忆，而是一个越用越聪明的编程搭档。**

<br/>

[![Dispatcher v4.7](https://img.shields.io/badge/🎯_任务调度-v4.7-ff6b35?style=for-the-badge)](docs/prd/codex-dispatcher-user.md)
[![Evolution Engine v1.0](https://img.shields.io/badge/🧬_进化引擎-v1.0-blueviolet?style=for-the-badge)](docs/prd/evolution-engine.md)
[![Status](https://img.shields.io/badge/🟢_状态-可用-success?style=for-the-badge)](#-30-秒快速上手)
[![Framework](https://img.shields.io/badge/🔌_适配-任意项目-blue?style=for-the-badge)](#-适配任何项目)

</div>

---

## 🏁 一键安装

克隆仓库，运行初始化向导——脚本会交互式地帮你配好一切：

```bash
git clone https://github.com/flockmaster/agent-os.git
cd agent-os

# macOS / Linux
bash setup.sh /path/to/your-project

# Windows (PowerShell)
pwsh setup.ps1 -TargetDir "D:\your-project"
```

> 向导会询问你的**项目名称**、**技术栈**和**AI 工具**，然后自动完成：
> - 将 `.agent/` 复制到你的项目
> - 生成定制化的记忆文件
> - 写入 `.gitignore` 规则
> - 安装 AI 全局配置

<details>
<summary>📸 <b>安装向导长什么样？</b>（点击展开）</summary>
<br/>

```
╔══════════════════════════════════════════╗
║   🌌 Antigravity Agent OS — Setup        ║
║   给你的 AI 编程助手装上大脑              ║
╚══════════════════════════════════════════╝

🔧 Step 1/5 — 设置目标项目
   ✅ 目标目录: D:\my-awesome-app

🔧 Step 2/5 — 项目信息
   项目名称: My Awesome App
   选择技术栈:
     [1] Flutter / Dart
     [2] React / TypeScript
     [3] Vue / TypeScript
     ...
   ✅ 项目: My Awesome App | React / TypeScript / Component

🔧 Step 3/5 — 选择你的 AI 编程工具
     [1] Gemini
     [2] GitHub Copilot
     [3] Claude
   ✅ AI 工具: GitHub Copilot

🔧 Step 4/5 — 安装 Agent OS 到项目
   ✅ 已复制 .agent/
   ✅ 已初始化 project_decisions.md
   ✅ 已重置 active_context.md
   ✅ 已追加 .gitignore 规则

🔧 Step 5/5 — 安装 AI 全局配置
   ✅ 已安装全局配置

╔══════════════════════════════════════════╗
║   🎉 安装完成！                          ║
╚══════════════════════════════════════════╝
   👉 对 AI 说: /start
```

</details>

---

## 😤 痛不痛？

你有没有遇到过这些场景：

| 场景 | 痛感指数 |
|------|:------:|
| 新开一个聊天窗口，又要从头跟 AI 解释项目背景 | 🔥🔥🔥🔥🔥 |
| 让 AI 改完代码，它忘了 commit，你也忘了 | 🔥🔥🔥🔥 |
| 同样的 bug 上周修过一次，今天 AI 又走了一遍弯路 | 🔥🔥🔥🔥🔥 |
| 让 AI 写个功能，写一半停下来问"要继续吗？" | 🔥🔥🔥 |
| PRD 拆了 20 个子任务，在一个窗口做完上下文必爆 | 🔥🔥🔥🔥🔥 |
| AI 每次都像新来的实习生，你是永远的导师 | 🔥🔥🔥🔥🔥 |

> **根本原因：AI Agent 没有记忆，没有流程，没有成长机制。**

Antigravity 就是解决这个问题 —— **一个 `.agent/` 文件夹，给你的 AI 装上大脑。**

---

## 🧠 它能做什么？

<table>
<tr>
<td width="50%">

### 💾 记得住事
AI 终于有了"长短期记忆"，不再每次从零开始。

- 🟢 **项目背景**：架构、技术栈、关键决策，只说一次就够
- 🟢 **工作进度**：关掉窗口明天接着干，断点续传
- 🟢 **你的偏好**：代码风格、沟通习惯，越用越懂你

</td>
<td width="50%">

### 🧬 学得会
每完成一个任务，AI 会自动总结经验教训。

- 🟢 **知识积累**：踩过的坑自动记录，绝不踩第二次
- 🟢 **模式识别**：自动发现代码中的通用模板
- 🟢 **效能优化**：追踪工作效率，自动调优流程

</td>
</tr>
<tr>
<td width="50%">

### 🚀 干得完
不再"做一步问一步"，而是全自动交付。

- 🟢 **一句话需求** → 自动生成方案 + 写代码 + 测试 + 提交
- 🟢 **并行加速**：同时派发多个相关任务，效率翻倍
- 🟢 **自主闭环**：Worker 完成任务后自动更新清单，无需人工介入

</td>
<td width="50%">

### 🔌 搬得走
不绑定任何框架，哪个项目都能用。

- 🟢 **即插即用**：拷贝一个文件夹到项目里就行
- 🟢 **技术无关**：Flutter、React、Python、Go... 全都行
- 🟢 **团队共享**：打包给同事，开箱即用

</td>
</tr>
</table>

---

## 🎯 杀手锏：Manifest Driven Dispatcher (v4.7)

> **解决最核心的痛点：大型 PRD 在单个对话窗口中上下文爆炸。**

Antigravity v4.7 引入了 **Manifest Driven (清单驱动)** 开发模式，不再是简单的 PM -> Worker，而是工业级的 **三阶段流水线**：

### Phase 1: 专家评审团 (The Expert Board)
> *Ref: `docs/01_Workflow_Expert_Review.md`*

在写第一行代码前，AI 专家团并发对需求进行 360° 体检：
- 🕵️ **体验总监**: 交互流程是否顺畅？
- 👨‍🏫 **行业专家**: 业务逻辑是否闭环？
- 🙅 **批判者**: 有没有安全漏洞？
- 👨‍💻 **技术专家**: 技术可行性与成本评估。

### Phase 2: 任务拆解 (Decomposition)
> *Ref: `docs/02_Workflow_Task_Decomposition.md`*

对于 > 1 人日的大型需求，自动拆解为 **原子任务清单 (`manifest.md`)**：
- 🗺️ **业务全景图**: 宏观把控。
- 📋 **Task Manifest**: 详细的子任务列表与依赖关系。
- 📄 **Sub-PRDs**: 每个子任务独立的需求文档。

### Phase 3: 并行实施 (Parallel Implementation)
> *Ref: `docs/03_Workflow_Implementation.md`*

基于 Manifest 的全自动交付流水线：

```mermaid
graph TD
    Manifest[📋 Manifest 清单] --> DAG{🕸️ 依赖分析}
    DAG --> |"无依赖 Set"| Batch[🚀 并行派发]
    
    subgraph "Parallel Micro-Cycles (Max 3 Workers)"
        W1[Worker A] --> |Design -> Code -> Test| Check1[✅]
        W2[Worker B] --> |Design -> Code -> Test| Check2[✅]
    end
    
    Check1 & Check2 --> Sync[🔄 状态同步]
    Sync --> |"解锁后续任务"| Update[📝 更新 Manifest]
    Update --> DAG
```

**为什么这很重要？**

| 对比 | 传统 Agent | Antigravity v4.7 |
|------|:---------:|:-----------:|
| **上下文** | 单窗口爆炸 (幻觉) | **Sub-PRD 独立上下文** (永远清醒) |
| **执行方式** | 串行 (慢) | **DAG 并行调度** (快) |
| **质量控制** | 开盲盒 | **专家评审 + 单元测试** (严谨) |
| **闭环能力** | 需人工确认 | **Manifest 自主闭环** |

**模式 B：程序化调度**（大型项目 / CI 集成）

```bash
# 直接用命令行跑，适合 20+ 任务的大型 PRD
python -m dispatcher.main --prd docs/prd/feature-x-dev.md

# 先预览不执行
python -m dispatcher.main --prd docs/prd/feature-x-dev.md --dry-run
```

---

## ⚡ 30 秒快速上手

**方式一：运行安装向导（推荐）**

```bash
# 向导会交互式引导你完成所有配置
bash setup.sh /path/to/your-project       # macOS / Linux
pwsh setup.ps1 -TargetDir "D:\project"     # Windows
```

**方式二：手动安装**

```bash
# 1️⃣ 把 .agent/ 文件夹拷贝到你的项目根目录
cp -r .agent/ /path/to/your-project/

# 2️⃣ 编辑 .agent/memory/project_decisions.md，填入你的技术栈

# 3️⃣ 在 IDE 中打开项目，对 AI 说：
```

> **你说**：`/start`
> **AI 回**："系统就绪，记忆已加载。请吩咐。"

---

## 🎬 日常使用长什么样？

### 场景一：大型需求开发 (Manifest Driven)

```
你：帮我开发一个完整的"用户积分系统"
AI：需求有点大，我先叫专家团评审一下...
    🕵️ 体验总监: "积分动效要流畅"
    👨‍🏫 行业专家: "得有防刷机制"
    ...
    ✅ 评审通过，已拆解为 5 个子任务 (Manifest)。

你：执行
AI：🚀 启动并行调度...
    ▶ [T-101 数据库] (Worker A) ⚡ Running
    ▶ [T-102 API 接口] (Worker B) ⚡ Running
    ...
    ✅ T-101 完成 -> 解锁 T-103
    🎉 所有任务完成！
```

### 场景二：开发新功能 (Quick)

```
你：加一个"一键复制"按钮
AI：小任务，直接执行。
    ✅ 代码已写完 → ✅ 测试通过 → ✅ 已提交 Git
```

### 场景三：遇到 Bug

```
你：（粘贴一大堆红色报错）
AI：检测到 NullPointerException...
    → 第 1 次修复尝试 ❌
    → 第 2 次修复尝试 ✅ 已解决！模式已记入知识库。
```

---

## 🗂️ 系统结构一览

.agent/                          ← "大脑"核心 (全平台通用)
│
├── 📂 memory/                   ← 记忆中枢
│   ├── active_context.md            短期记忆 (Context)
│   ├── project_decisions.md         长期记忆 (宪法)
│   ├── user_preferences.md          你喜欢什么风格？
│   ├── 📂 evolution/               进化引擎数据
│   └── 📂 knowledge/               AI 积累的知识库
│
├── 📂 workflows/                ← 自动化流程 (Manifest Driven)
│   ├── codex-dispatch.md            🎯 核心调度器 (v4.7)
│   ├── ai-review.md                 🕵️ 专家评审流程
│   ├── prd-decomposition.md         🔪 任务拆解流程
│   └── rd-implementation.md         🚀 研发交付流程
│
├── 📂 skills/                   ← 技能模块 (Plugins)
│   ├── evolution-engine/            自进化引擎
│   ├── context-manager/             记忆管理器
│   └── prd-crafter/                 需求文档生成器
│
├── 📂 rules/                    ← 行为规则
│   └── router.rule                  任务分发路由
│
├── 📂 adapters/                 ← 多模型适配器 (Claude/Gemini/Copilot)
├── 📂 dispatcher/               ← 任务调度器核心逻辑
├── 📂 guards/                   ← 安全门禁规则
├── 📂 config/                   ← 系统配置
└── 📂 prompts/                  ← 结构化提示词模板

docs/                            ← 文档驱动核心 (Documentation)
├── 00_PRD_Review_System_Design.md   系统设计总览
├── 01_Workflow_Expert_Review.md     评审流详细设计
├── 02_Workflow_Task_Decomposition.md 拆解流详细设计
└── 03_Workflow_Implementation.md    实施流详细设计

---

## 🔌 适配任何项目

Antigravity 与技术栈无关。只需修改一行配置：

```markdown
# .agent/memory/project_decisions.md

Tech Stack: Flutter / Dart / MVVM    ← 改成你的技术栈就行
```

| 已验证 | 理论兼容 |
|:------|:--------|
| Flutter / Dart | React / TypeScript |
| Python / Django | Vue / Nuxt |
| Node.js / Express | Go / Gin |

---

## ⌨️ 命令速查表

| 命令 | 干什么用 | 一句话说明 |
|:---:|---------|-----------|
| `/start` | ⚡ 开机 | 加载记忆，恢复上下文 |
| `/suspend` | 💾 存档 | 保存进度，下次接着干 |
| `/feature-flow` | 🚀 造功能 | 需求→方案→编码→测试→提交，一条龙 |
| `/analyze-error` | 🔥 灭火 | 智能分析报错，自动修复 |
| `/evolve` | 🧬 进化 | 整理知识库，让 AI 变聪明 |
| `/reflect` | 💭 复盘 | 总结经验教训 |
| `/status` | 📊 看板 | 当前任务做到哪了 |
| `/rollback` | ⏪ 后悔药 | 回到上一个安全版本 |
| `/use-flutter-template` | 🧩 Flutter 规范 | 加载 flutter-ai-advanced-template 规范包 |
| `/meta` | 🔧 改系统 | 修改 AI 自身的行为规则 |
| `/dispatch` | 🎯 调度 | PM 模式：拆任务→派 Worker→逐个完成 |
| `/export` | 📦 打包 | 导出干净的系统副本给别人 |

---

## 🔄 它是怎么运转的？

```mermaid
graph LR
    A((💤 空闲)) -->|你说了个需求| B(📝 规划)
    B -->|生成方案| C{👀 你确认}
    C -->|"Go!"| D[⚡ 执行中]
    D -->|报错了| E(🔧 自动修复)
    E -->|修好了| D
    E -->|修不好| F[🚨 求助人类]
    D -->|成功| G(📚 存档学习)
    G -->|还有任务| D
    G -->|全做完了| A
```

> **关键设计**：AI 遇到错误不会立刻停下，而是自动重试最多 3 次。只有真的搞不定才会打扰你。

---

## 🌟 成果展示 (Showcase)

**Agent OS 官网 (Branding Site)** 完全由 Agent OS **v4.7** 自身构建 (Dogfooding)。

- **技术栈**: Vanilla HTML/CSS/JS (零依赖)
- **开发模式**: `Manifest Driven` + `Parallel Dispatch`
- **特性**:
  - 🎨 **Glassmorphism**: 深度玻璃拟态设计体系
  - ⚡ **Performance**: `IntersectionObserver` 驱动的高性能滚动引擎 (Lighthouse 100)
  - 📱 **Responsive**: 完美适配 Mobile (375px) ~ Desktop (1440px)
  - 🖥️ **Visual Terminal**: 模拟 Agent 启动的打字机交互动画

> 👉 **本地查看**: `start branding-site/index.html`

---

## 📝 版本演进

| 版本 | 里程碑 |
|:---:|-------|
| **v4.7** 🆕 | **Manifest Driven**: 专家评审 -> 任务拆解 -> 并行实施 (文档驱动架构) |
| **v4.0** | **Task Dispatcher**: PM→Worker 分离架构，上下文隔离 |
| **v3.0** | 自进化引擎：知识收割 + 模式库 + 自动反思 |
| **v2.1** | 状态机 + Git 检查点保护 |
| **v1.0** | 基础规则引擎 + 对话驱动 |



---

## 🤔 常见问题

<details>
<summary><b>Q：这跟直接写 Prompt 有啥区别？</b></summary>
<br/>
Prompt 是"一次性的叮嘱"，关掉窗口就没了。Antigravity 是"持久化的操作系统"——记忆、规则、知识库都存在文件里，AI 每次启动都自动加载。就像给 AI 从"每天新入职"变成"老员工"。
</details>

<details>
<summary><b>Q：会不会搞乱我的项目代码？</b></summary>
<br/>
不会。系统所有文件都在 <code>.agent/</code> 文件夹里，与你的业务代码完全隔离。加一行 <code>.gitignore</code> 就能控制哪些文件纳入版本管理。
</details>

<details>
<summary><b>Q：支持哪些 AI 工具？</b></summary>
<br/>
理论上支持所有能读取项目文件的 AI 编程助手（Cursor、Copilot、Gemini Code Assist 等）。核心原理是通过文件系统传递上下文，不依赖任何特定 API。<br/><br/>
<b>Dispatcher 调度功能</b>目前需要搭配 <a href="https://github.com/openai/codex">Codex CLI</a> 使用（作为 Worker 执行器）。PM 角色可由 Antigravity (Gemini)、Copilot 或 Claude 担任。
</details>

<details>
<summary><b>Q：Dispatcher 和直接让 AI 写代码有什么区别？</b></summary>
<br/>
直接让 AI 在一个窗口做 20 个任务，到后面它会“忘记”前面做过的事，产生幻觉。Dispatcher 让每个子任务在<b>独立的上下文</b>中执行——就像给每个任务安排一个“新员工”，但有一个“项目经理”在上面统筹协调。PM 的上下文只保留摘要，不会爆炸。
</details>

<details>
<summary><b>Q：记忆库会不会越来越大？</b></summary>
<br/>
不会。系统内置了"遗忘机制"——过期决策自动标记 Deprecated 并清理，完成的任务归档压缩，知识库定期整理去重。
</details>

---

<div align="center">

**⭐ 如果觉得有用，给个 Star 是最大的鼓励**

Made with 🧠 by **Antigravity Systems**

*让每一次对话，都不白聊。*

</div>
