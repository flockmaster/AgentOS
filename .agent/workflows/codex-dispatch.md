---
description: 自动派发 Codex 任务流水线
---

# Codex Task Dispatcher v3.0 (Agent Native)

> **核心理念**: 利用大模型的自然语言理解能力，直接从 PRD 中识别和派发任务。
> **无需脚本解析**，完全由 Agent 主导调度。

---

## 触发方式

| 用户说... | Agent 行为 |
|----------|-----------|
| "执行 PRD" / "开始调度" | 读取 PRD，自动识别下一个任务 |
| "做 T-001" / "执行 001" | 直接跳到指定任务执行 |
| "跳过 T-002" | 将 T-002 标记为 SKIPPED |
| "继续" | 从上次中断处恢复 |

---

## 调度循环 (核心流程)

### Step 1: 定位 PRD 📄

如果用户没有指定 PRD 路径，自动查找 `docs/prd/*-dev.md` 中最新修改的文件。

### Step 2: 读取并理解 PRD 🧠

在 Copilot 环境中使用 `read_file` 读取 PRD 文件（必要时分段读取）。

**Agent 思考要点**：
1. 找到任务列表（通常是表格形式，但不强制）
2. 识别每个任务的 ID、名称、状态、依赖关系
3. 不依赖固定格式 —— 用自然语言理解任务结构

### Step 3: 选择下一个任务 🎯

**判断逻辑**（Agent 自行推理）：
1. 找出所有状态为 **PENDING** (⏳) 的任务
2. 过滤出依赖已全部 **DONE** (✅) 的任务
3. 选择其中编号最小的作为下一个

**终止条件**：
- 所有任务 DONE → 输出 "🎉 全部完成！" → 结束
- 有 PENDING 但依赖未满足 → 输出阻塞原因 → 等待用户
- 存在 BLOCKED 任务 → 询问用户如何处理

### Step 4: 构造 Worker Prompt 📝

根据选中的任务，构造给 Codex Worker 的完整 Prompt：

```
你是一个专注的开发者，负责完成以下任务。

## 任务信息
- **ID**: {任务 ID}
- **名称**: {任务名称}  
- **描述**: {任务描述}
- **工作目录**: {当前项目路径}

## 执行规范
1. 仅完成本任务描述的内容，不做超出范围的事
2. 完成后说: "任务 {ID} 完成" 
3. 如果遇到需要澄清的问题，明确说出你的疑问
4. 如果遇到致命阻塞无法继续，说明原因

## 上下文 (如有之前的补充信息)
{此处追加 PM 传递的额外信息}
```

### Step 5: 启动 Codex Worker 🚀

#### 5.0 ⚠️ Windows 沙箱问题 (2026-02-10 验证)

**重要发现**：在 Windows 环境下，`--full-auto` 和 `--sandbox workspace-write` 均无法正常写入文件。
必须使用 `--dangerously-bypass-approvals-and-sandbox` 参数才能确保 Codex 正常执行文件操作。

```bash
# ✅ Windows 正确调用方式 (已验证)
codex exec --json --dangerously-bypass-approvals-and-sandbox "{Prompt}"

# ❌ 以下方式在 Windows 上文件写入失败
codex exec --json --full-auto "{Prompt}"                    # 失败
codex exec --json --sandbox workspace-write "{Prompt}"      # 失败
codex exec --json --sandbox danger-full-access "{Prompt}"   # 失败
```

> **安全提示**：`--dangerously-bypass-approvals-and-sandbox` 绕过所有安全检查，
> 仅适用于受信任的自动化环境（如 Agent OS 内部调度）。

#### 5.1 会话启动策略 (关键决策点)

根据任务状态选择不同的 Codex 命令：

| 场景 | 命令 | 说明 |
|------|------|------|
| **全新任务** | `codex exec --json --dangerously-bypass-approvals-and-sandbox` | 干净上下文，零污染，完整写入权限 |
| **任务中断恢复** (同任务继续) | `codex exec resume --last --dangerously-bypass-approvals-and-sandbox` | 保持完整对话历史，接着干 |
| **任务中断恢复** (指定会话) | `codex exec resume {SESSION_ID} --dangerously-bypass-approvals-and-sandbox` | 精确恢复到指定会话 |
| **任务失败重试** (换策略) | `codex fork --last` | 继承上下文但走新分支，避免重复踩坑 |
| **交互式调试** | `codex resume --last` | 手动介入，人机协作排查问题 |

#### 5.2 何时用 resume (恢复)

**适用场景**：任务未完成，需要在 **同一上下文** 中继续执行。

```bash
# 非交互式：恢复最近会话并注入新指令
codex exec resume --last --full-auto "继续完成之前的任务"

# 非交互式：恢复指定会话
codex exec resume {SESSION_ID} --full-auto "请继续"

# 交互式：恢复最近会话，手动操作
codex resume --last

# 交互式：弹出选择器，选择历史会话
codex resume

# 查看所有会话（包括其他目录的）
codex resume --all
```

**典型场景**：
- Worker 执行到一半因超时被终止，需要接着做
- PM 回答了 Worker 的 QUESTION 后，需要继续原任务
- 网络断开后重连，恢复之前的工作

#### 5.3 何时用 fork (分叉)

**适用场景**：需要 **保留历史上下文** 但 **走不同的路径**。

```bash
# 交互式：分叉最近会话
codex fork --last

# 交互式：分叉并注入新方向
codex fork --last "用方案 B 重新实现这个功能"

# 交互式：选择历史会话分叉
codex fork {SESSION_ID}
```

**典型场景**：
- Worker 第 3 次尝试失败，PM 决定换一个技术方案
- 同一个任务需要尝试两种不同实现，对比效果
- 之前的对话积累了有价值的分析，但执行方向需要调整

#### 5.4 何时用全新会话

**适用场景**：新任务，无需任何历史上下文。

```bash
# 非交互式 (推荐用于调度) - Windows 验证通过
codex exec --json --dangerously-bypass-approvals-and-sandbox "{Prompt}"

# 交互式 (手动开发)
codex --full-auto "{Prompt}"
```

**典型场景**：
- PRD 中的下一个独立任务 (无依赖关系)
- 之前的任务已经完成并提交
- 刻意需要"干净的大脑"来避免上下文污染

#### 5.5 PM 调度决策流程图

```
任务开始
    ↓
检查是否有该任务的历史会话
    ├─ 无 → 全新会话: codex exec --full-auto
    └─ 有 → 检查历史会话状态
              ├─ 会话成功完成 → 全新会话 (新任务)
              ├─ 会话中断/超时 → resume (继续原任务)
              ├─ 会话失败 (< 3次) → resume (重试)
              └─ 会话失败 (≥ 3次) → fork (换策略重试)
                                    └─ fork 也失败 → 标记 BLOCKED
```

#### 5.6 会话 ID 管理

PM 应在 `.agents/memory/active_context.md` 中记录每个任务的 Codex 会话 ID：

```markdown
## 活跃会话

| 任务 ID | 会话 ID (SESSION_ID) | 状态 | 备注 |
|---------|---------------------|------|------|
| T-002 | a1b2c3d4-... | 执行中 | 第 1 次尝试 |
| T-003 | e5f6g7h8-... | 已中断 | 待 resume |
```

使用 `--json` 输出时，会话 ID 会在事件流中返回，PM 需要捕获并记录。

#### 5.7 exec 完整参数参考

```bash
codex exec [OPTIONS] [PROMPT]

# 关键选项:
--dangerously-bypass-approvals-and-sandbox  # ⭐ Windows 必须使用，绕过沙箱限制
--full-auto                 # 全自动模式 (sandbox=workspace-write + approval=on-request)
--json                      # JSONL 事件流输出，便于程序化监控
-m, --model <MODEL>         # 指定模型 (如 o3, gpt-4.1 等)
-C, --cd <DIR>              # 指定工作目录
-s, --sandbox <MODE>        # 沙箱策略: read-only | workspace-write | danger-full-access
-o, --output-last-message <FILE>  # 将最后一条消息写入文件
--output-schema <FILE>      # 指定输出 JSON Schema，约束返回格式
--skip-git-repo-check       # 允许在非 Git 仓库中运行
--add-dir <DIR>             # 添加额外可写目录
```

#### 5.8 PM 异步等待机制 (2026-02-10 验证)

当 PM (Antigravity) 调用 Codex Worker 时，使用异步轮询机制等待结果：

```
┌─────────────────────────────────────────────────────────────────┐
│  1. run_in_terminal("codex exec ...", isBackground=true)       │
│     ↓                                                          │
│     命令启动 → 返回 terminalId (进入后台)                        │
│                                                                 │
│  2. await_terminal(terminalId, timeout=60000)                   │
│     ↓                                                          │
│     长轮询等待（可重复调用）                                     │
│     ├─ 任务完成 → 返回 exitCode + 输出（JSONL 事件流）           │
│     └─ 超时未完成 → 返回 timeout，可继续轮询                     │
│                                                                 │
│  3. 解析 JSONL 事件流（只提取关键事件 + 摘要）                   │
│     ├─ thread.started → 记录 SESSION_ID                         │
│     ├─ agent_message → 检测 QUESTION/完成                       │
│     ├─ error → 判断是否可重试                                   │
│     └─ turn.completed → 任务完成                                │
└─────────────────────────────────────────────────────────────────┘
```

**JSONL 事件类型参考**：

| 事件类型 | 含义 | PM 响应 |
|----------|------|--------|
| `thread.started` | 会话启动，包含 `thread_id` | 记录 SESSION_ID |
| `turn.started` | 轮次开始 | 无需处理 |
| `item.completed` (reasoning) | Codex 思考过程 | 可选记录 |
| `item.completed` (command_execution) | 执行命令结果 | 检查 exit_code |
| `item.completed` (agent_message) | Codex 输出消息 | 检测问题/完成 |
| `turn.completed` | 轮次结束，包含 token 用量 | 任务完成 |
| `error` | 执行错误 | 判断重试策略 |

### Step 6: 实时监控 👀

Agent 读取 Worker 的 stdout，解析 JSONL 事件：

| 事件/模式 | Agent 响应 |
|----------|-----------|
| `agent_message` 包含疑问句 | 尝试回答 → 或标记 BLOCKED |
| `tool_call` / `tool_result` | 记录进度 |
| `error` 事件 | 判断是否可重试 |
| `session_end` 且成功 | 更新 PRD 状态为 DONE |
| 超时 (15分钟无输出) | 终止进程，标记 BLOCKED |

### Step 7: 干预决策 🧑‍⚖️ (如需)

如果 Worker 提出问题，Agent 作为 PM 自主判断：

| 问题类型 | Agent 决策 |
|---------|-----------|
| 技术选型 (小) | 自行决定，采用更现代的方案 |
| 命名规范 | 遵循项目现有规范 |
| 风险操作 (删除数据等) | 标记 BLOCKED，必须询问用户 |
| 需求歧义 | 标记 BLOCKED，询问用户 |

**回答问题的方式**（上下文恢复机制）：

**方式 A: resume 恢复 (推荐)**
1. 记录当前 Worker 的 SESSION_ID
2. 等待 Worker 超时或手动终止
3. 使用 `codex exec resume {SESSION_ID} --full-auto "补充答案: {答案内容}"` 恢复

**方式 B: fork 分叉 (当需要换方向时)**
1. 终止当前 Worker
2. 使用 `codex fork {SESSION_ID} "之前的方案不行，改用: {新方案}"` 创建新分支

**方式 C: 重启注入 (兜底方案)**
1. 终止当前 Worker 进程
2. 将答案追加到原 Prompt 的"上下文"部分
3. 使用 `codex exec --full-auto` 重新启动 Worker

### Step 8: 上下文压缩 🗜️ (防止上下文爆炸)

> **为什么需要这一步**: PM 在 Step 6 监控 JSONL 事件流时，Codex 的 reasoning、命令输出、
> 回复消息会全部进入 PM 上下文。连续调度 4-5 个任务后，上下文可能逼近窗口上限。
> 本步骤将原始监控数据压缩为结构化摘要，释放上下文空间。

#### 8.1 压缩时机

每个任务执行完毕（无论成功、失败、阻塞）后，**立即执行压缩**，再进入下一步。

#### 8.2 压缩规则

PM 将本次任务的所有 JSONL 监控数据压缩为以下格式的**一行摘要**，然后丢弃原始数据：

```markdown
📋 T-{ID} | {状态} | 改动: {文件列表} | 测试: {结果} | 耗时: {时长} | 备注: {关键信息}
```

**示例**：
```
📋 T-002 | ✅ DONE | 改动: src/api.dart, lib/models/user.dart | 测试: 3/3 通过 | 耗时: 3m42s | 备注: 无
📋 T-003 | ❌ FAILED(2/3) | 改动: src/db.dart | 测试: 未执行 | 耗时: 5m10s | 备注: SQLite 版本不兼容
📋 T-004 | 🚫 BLOCKED | 改动: 无 | 测试: 无 | 耗时: 1m20s | 备注: 需要用户确认删除策略
```

#### 8.3 需要保留的关键信息

| 信息 | 是否保留 | 说明 |
|------|---------|------|
| 任务 ID 和最终状态 | ✅ 保留 | 后续调度需要 |
| 修改的文件列表 | ✅ 保留 | 简要列出，不含内容 |
| 测试结果 (通过/失败) | ✅ 保留 | 仅结论 |
| SESSION_ID | ✅ 保留 | 写入 `.agents/memory/active_context.md`，不占对话上下文 |
| Worker 提出的未解决问题 | ✅ 保留 | 一句话概括 |
| Codex reasoning 过程 | ❌ 丢弃 | 占用大，无后续价值 |
| 命令执行的完整输出 | ❌ 丢弃 | 占用大，结果已压缩 |
| JSONL 原始事件流 | ❌ 丢弃 | 已提取关键信息 |

#### 8.4 累积摘要管理

PM 维护一个**滚动摘要窗口**，规则如下：

- **最近 5 个任务**: 保留完整摘要行
- **更早的任务**: 合并为一行统计 `📊 已完成 T-001~T-005 (5/5 成功)`
- **失败/阻塞任务**: 无论多早，始终保留摘要（需要后续处理）

#### 8.5 极端情况: 单任务输出过大

如果单个任务的 JSONL 输出超过 PM 上下文的 20%（通过 token 用量估算）：
1. 使用 `--output-last-message <FILE>` 将 Codex 结果写入文件
2. PM 只读取文件中的最终结论，不读原始事件流
3. 在摘要中标注 `详情见: .agents/logs/T-{ID}-result.md`

### Step 9: 更新 PRD 状态 ✍️

任务完成后，使用 `apply_patch` 更新 PRD 中对应行的状态：

- PENDING (⏳) → DONE (✅) 
- 更新时保留表格格式和其他列内容

### Step 10: 循环继续 🔄

回到 **Step 3**，继续选择下一个任务，直到满足终止条件。

---

## 特殊情况处理

### 🚫 任务阻塞
1. 记录阻塞原因到 `active_context.md`
2. 查找其他无依赖的 PENDING 任务
3. 如果有 → 跳过阻塞任务，执行其他任务
4. 如果没有 → 通知用户所有待解决的阻塞问题

### ❌ Worker 失败
1. 第 1-2 次失败: `codex exec resume {SESSION_ID} --full-auto "上次失败了，请检查错误并重试"` (恢复上下文重试)
2. 第 3 次失败: `codex fork {SESSION_ID} "之前的方案多次失败，请换一种方案"` (分叉换策略)
3. fork 也失败: 标记 FAILED，询问用户

### ⏰ 超时处理
- 代码修改任务: 10 分钟超时
- 测试/构建任务: 15-20 分钟超时
- 超时后: 优先 `codex exec resume --last --full-auto "请继续完成"` 恢复
- 多次超时: 强制终止，标记 BLOCKED

---

## Git 集成

每个任务完成后自动执行：

// turbo
```bash
git add -A && git commit -m "feat(T-{ID}): {任务名称}"
```

---

## 使用示例

### 示例 1: 执行整个 PRD
```
用户: 执行 docs/prd/feature-x-dev.md
Agent: [读取 PRD] 
       找到 10 个任务，其中 T-001 已完成。
       下一个任务: T-002
       正在启动 Codex Worker...
       [监控输出]
       T-002 完成！更新 PRD。
       下一个: T-003...
       [循环]
       🎉 全部完成！共执行 9 个任务。
```

### 示例 2: 指定任务
```
用户: 做 003
Agent: 定位到 T-003: "实现交互式监控"
       依赖 T-002 状态: ✅ DONE (满足)
       启动执行...
```

### 示例 3: 处理阻塞
```
Agent: T-004 执行中...
       Worker 提问: "日志应该存放在哪个目录？"
       这是技术细节，我可以自行决定。
       回答: "使用 .agent/logs/ 目录"
       [重启 Worker 并注入答案]
       T-004 继续执行...
```

---

## 与传统方式的对比

| 维度 | v2.0 (脚本驱动) | v3.0 (Agent 原生) |
|-----|----------------|------------------|
| PRD 解析 | parser.py 硬编码 | Agent 自然语言理解 |
| PRD 格式要求 | 严格表格格式 | 灵活，任意结构 |
| 调度逻辑 | dispatch_loop.sh | Agent 思考判断 |
| 上下文管理 | 每次全新启动 | resume/fork 智能恢复 |
| 可扩展性 | 需改代码 | 直接改 Prompt |
| 透明度 | 脚本黑盒 | Agent 每步可见 |

---

## Codex CLI 命令速查表

### 会话生命周期

```
新任务 ──→ codex exec ──→ 执行中 ──→ 完成 ✅
                              │
                          中断/失败
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                 resume     fork    全新 exec
               (继续原路)  (换条路)  (从头来)
```

### 命令对照表

| 目的 | 命令 | 典型用法 |
|------|------|---------|
| 全新任务 (非交互) | `codex exec --full-auto "{prompt}"` | PM 派发新任务 |
| 全新任务 (交互) | `codex --full-auto "{prompt}"` | 手动开发 |
| 恢复最近会话 (非交互) | `codex exec resume --last --full-auto "{追加指令}"` | 任务中断后继续 |
| 恢复指定会话 (非交互) | `codex exec resume {ID} --full-auto "{追加指令}"` | 精确恢复 |
| 恢复最近会话 (交互) | `codex resume --last` | 手动接管调试 |
| 分叉最近会话 | `codex fork --last "{新方向}"` | 换策略重试 |
| 分叉指定会话 | `codex fork {ID} "{新方向}"` | 对比实验 |
| 代码审查 | `codex review` | 提交前审查 |
| 查看所有历史会话 | `codex resume --all` | 找回旧会话 |

### resume vs fork vs 新会话 决策树

```
需要执行任务
    │
    ├─ 全新任务，无历史 ──────────────→ codex exec (新会话)
    │
    └─ 有相关历史会话
         │
         ├─ 任务未完成，方向正确 ────→ codex resume (恢复)
         │   • 超时中断
         │   • 网络断开
         │   • 需要补充信息后继续
         │
         ├─ 任务失败，需要换方案 ────→ codex fork (分叉)
         │   • 多次重试失败
         │   • PM 决定换技术方案
         │   • 需要保留之前的分析但改执行路径
         │
         └─ 任务已完成/上下文pollution → codex exec (新会话)
             • 上一个任务成功提交
             • 历史上下文太杂，需要干净环境
```
