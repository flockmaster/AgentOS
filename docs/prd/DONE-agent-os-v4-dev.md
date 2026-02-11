# ✅ PRD: Antigravity Agent OS v4.0 — 全面落地计划 (研发版)

> 版本: 1.0 | 日期: 2026-02-09 | 状态: 待确认

---

## 1. 技术背景

### 1.1 架构现状

Antigravity Agent OS v3.0 已建立完整的四层架构：

```
.agent/
├── memory/          # 记忆系统 (active_context / project_decisions / evolution/)
├── rules/           # 路由规则 (router.rule)
├── skills/          # 技能模块 (context-manager / evolution-engine / prd-crafter-*)
└── workflows/       # 工作流 (13 个 .md 文件)
```

**已验证的技术预研结论**:
- Codex CLI 原生支持 `--json` JSONL 事件流输出 ✅
- `exec` 模式为非交互式，运行中无法接收 stdin → 采用"重启注入"方案 ✅
- Agent 自然语言理解可替代硬编码 Markdown 解析器 ✅

### 1.2 技术债务清单

| 债务 | 严重程度 | 影响 | 本次是否解决 |
|------|---------|------|-------------|
| Dispatcher 5/7 任务未完成 | 🔴 Critical | 自动化管道完全不可用 | ✅ Phase 1 |
| Evolution Engine 10/12 任务未完成 | 🔴 Critical | 进化引擎空转 | ✅ Phase 2 |
| 全局配置绑定 Gemini | 🟡 Medium | 非 Gemini 用户无法使用 | ✅ Phase 3 |
| 无硬编码守卫 | 🟡 Medium | 关键操作可能被跳过 | ✅ Phase 3 |
| 并行调度不支持 | 🟢 Low | 长 PRD 执行慢 | ❌ v5.0 |

### 1.3 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| PM (调度器) | Python 3.10+ | 轻量级 CLI 工具 |
| Worker | Codex CLI (`codex exec`) | 独立进程，全新上下文 |
| 通信协议 | JSONL (stdout) | Worker → PM 事件流 |
| 知识存储 | Markdown + YAML Frontmatter | 与现有体系一致 |
| 守卫层 | Git Hooks + Python 脚本 | Pre-commit / Post-commit |
| 配置 | Markdown 模板 + 变量替换 | 多模型适配 |

---

## 2. 任务拆解 (3 Phase × 总计 18 个核心任务)

### Phase 1: Dispatcher MVP — 让管道跑起来

> 目标: 用户可以执行 `codex-dispatch` 端到端自动完成 PRD 中的全部任务
> 预计工期: 3-4 天

| ID | 任务 | 状态 | 描述 | 预估 | 依赖 | 验收标准 |
|----|------|------|------|-----|------|---------|
| T-101 | **Worker 封装器 (core)** | ✅ DONE | 封装 `codex exec --json --full-auto` 调用，支持 JSONL 事件流解析、超时控制 (10/15/20 min)、进程生命周期管理 | 3h | - | 单元测试: 启动 Mock Worker，解析 JSONL，超时终止 |
| T-102 | **JSONL 事件解析器** | ✅ DONE | 解析 `agent_message`/`tool_call`/`tool_result`/`error`/`session_end` 五类事件，提取结构化信息 | 2h | T-101 | 单元测试: 解析样本 JSONL 文件，正确提取各事件类型 |
| T-103 | **重启注入机制** | ✅ DONE | 检测 Worker 提问 → 终止进程 → 追加答案到 Prompt → 重启。同一任务最多 3 次重启 | 3h | T-101, T-102 | 集成测试: Mock Worker 提问 → PM 注入答案 → Worker 继续执行 |
| T-104 | **PM 自主决策引擎** | ✅ DONE | 语义分析 Worker 提问，按规则判断: 技术细节自行决定 / 需求歧义标记 BLOCKED | 2h | T-103 | 测试: 10 个样本问题，正确分类率 ≥ 80% |
| T-105 | **Git 自动提交集成** | ✅ DONE | 每个任务 DONE 后自动 `git add -A && git commit -m "feat(T-{ID}): {name}"`。失败时记录日志但不阻塞 | 1h | T-101 | 测试: 任务完成后 Git 历史中有对应 commit |
| T-106 | **PRD 状态回写** | ✅ DONE | 任务完成后自动将 PRD 中对应行从 `⏳ PENDING` 更新为 `✅ DONE` | 1.5h | T-101 | 测试: 执行一个任务后，PRD 文件被正确更新 |
| T-107 | **端到端集成测试** | ✅ DONE | 编写 Mini PRD (3 任务)，验证完整流程: 解析 → 调度 → 执行 → 提交 → 状态回写 | 3h | T-101 ~ T-106 | E2E: Mini PRD 全部任务完成，Git 历史正确 |

**Phase 1 交付物**:
```
.agent/
└── dispatcher/
    ├── __init__.py
    ├── core.py              # Task/WorkerResult 数据类
    ├── worker.py            # Worker 封装器 (T-101)
    ├── jsonl_parser.py      # JSONL 解析器 (T-102)
    ├── restart_injector.py  # 重启注入 (T-103)
    ├── decision_engine.py   # PM 决策 (T-104)
    ├── git_ops.py           # Git 操作 (T-105)
    ├── prd_updater.py       # PRD 回写 (T-106)
    ├── main.py              # 入口: dispatch(prd_path)
    └── tests/
        ├── test_worker.py
        ├── test_parser.py
        ├── test_injector.py
        └── test_e2e.py      # (T-107)
```

---

### Phase 2: Evolution Engine 落地 — 让系统学会学习

> 目标: 每次任务完成后自动收割知识，首月积累 20+ 知识条目
> 预计工期: 4-5 天

| ID | 任务 | 状态 | 描述 | 预估 | 依赖 | 验收标准 |
|----|------|------|------|-----|------|---------|
| T-201 | **知识收割器实现** | ✅ DONE | 在 SKILL.md 中细化提取规则；任务完成后分析代码变更 + 对话上下文，生成知识条目 (Markdown + YAML Frontmatter) | 3h | - | 手动触发: 给定一段对话记录，生成符合模板的知识条目 |
| T-202 | **知识索引系统** | ✅ DONE | 实现 `knowledge_base.md` 的 CRUD: 添加条目 → 更新索引表 → 更新分类统计 → 更新标签云 | 2h | T-201 | 添加 3 条知识后，索引表/分类/标签均正确更新 |
| T-203 | **种子知识包** | ✅ DONE | 编写 20 条通用开发最佳实践 (Flutter 10 条 + Dart 5 条 + 工程规范 5 条)，预填入 `knowledge/` | 3h | T-202 | 知识库初始含 20+ 条 active 条目，覆盖 5 个 category |
| T-204 | **Confidence 衰减引擎** | ✅ DONE | 实现 Confidence 分数更新: 验证 +0.1 / 引用 +0.05 / 误导 -0.2 / 30 天未用 -0.1 / < 0.5 标记 deprecated | 2h | T-202 | 单元测试: 模拟各触发事件，Confidence 正确计算 |
| T-205 | **反思工作流实现** | ✅ DONE | `workflows/reflect.md` 的落地: 读取任务完成情况 → 生成 WWW/WCI/Learnings/Action Items → 追加到 `reflection_log.md` | 2h | T-201 | 执行 `/reflect` 后，反思日志新增一条完整记录 |
| T-206 | **模式检测器 MVP** | ✅ DONE | 代码提交后扫描 `git diff`，与 `pattern_library.md` 匹配；出现 ≥ 3 次的结构自动提升为 ACTIVE 模式 | 3h | T-202 | 手动提交含重复模式的代码后，模式库新增条目 |
| T-207 | **学习队列处理器** | ✅ DONE | 实现 `learning_queue.md` 的完整生命周期: 入队 → 按优先级处理 → 输出知识/模式 → 标记已处理 → 7 天后清理 | 2h | T-201, T-206 | 队列有 3 条素材时，`/evolve` 全部处理完毕 |
| T-208 | **工作流指标追踪** | ✅ DONE | 在 feature-flow / analyze-error / start 的关键节点插入计时器，完成后写入 `workflow_metrics.md` | 2h | - | 执行 feature-flow 后，指标表新增一行记录 |

**Phase 2 交付物**:
```
.agent/memory/
├── knowledge/
│   ├── k-001 ~ k-005 (已有)
│   ├── k-006-flutter-widget-lifecycle.md        # 种子知识 (示例)
│   ├── k-007-dart-null-safety-patterns.md       # 种子知识 (示例)
│   ├── ...
│   └── k-025-git-commit-conventions.md          # 种子知识 (示例)
└── evolution/
    ├── knowledge_base.md    # 索引已填充 25+ 条目
    ├── learning_queue.md    # 队列处理器已激活
    ├── pattern_library.md   # 模式检测已上线
    ├── reflection_log.md    # 反思日志可自动生成
    └── workflow_metrics.md  # 指标追踪已集成
```

---

### Phase 3: 加固 & 多模型适配 — 让系统值得信赖

> 目标: 关键操作遵循率 ≥ 95%，支持 Gemini / Claude / GPT 三大模型
> 预计工期: 3-4 天

| ID | 任务 | 状态 | 描述 | 预估 | 依赖 | 验收标准 |
|----|------|------|------|-----|------|---------|
| T-301 | **Pre-commit 守卫** | ✅ DONE | Git pre-commit hook: 检查 `active_context.md` 是否在本次提交中被更新；若未更新则警告 (非阻断) | 1.5h | - | 提交代码时，若未更新 active_context 则输出警告 |
| T-302 | **Post-commit 守卫** | ✅ DONE | Git post-commit hook: 自动创建 checkpoint tag (如果上一个 checkpoint 超过 30 分钟) | 1h | T-301 | 提交代码后，自动生成 `checkpoint-*` tag |
| T-303 | **Session 看门狗** | ✅ DONE | 轻量 Python 脚本: 监控 `.agent/memory/active_context.md` 的最后修改时间，超过 30 分钟未更新则在终端提醒 | 2h | - | 启动看门狗后，30 分钟无更新触发提醒 |
| T-304 | **配置抽象层** | ✅ DONE | 创建 `.agent/config/agent_config.md` 统一配置模板，支持 `model_provider` / `global_config_path` / `api_style` 变量 | 2h | - | 配置文件存在且定义了 3 种模型后端 |
| T-305 | **Gemini 适配器** | ✅ DONE | 将现有 `GEMINI.md` 逻辑迁移为 Gemini 适配器模板，保持完全向后兼容 | 1.5h | T-304 | 使用 Gemini 配置时行为与 v3.0 完全一致 |
| T-306 | **Claude 适配器** | ✅ DONE | 创建 `.claude/CLAUDE.md` 适配器: 将 router.rule 中的 Gemini 特定 API 名称映射为 Claude 对应操作 | 2h | T-304 | Claude 用户复制 `.agent/` + `.claude/` 后可使用基础功能 |
| T-307 | **GPT 适配器** | ✅ DONE | 创建 `.copilot/copilot-instructions.md` 适配器: 适配 Copilot/GPT 系列 | 2h | T-304 | GPT 用户复制 `.agent/` + `.copilot/` 后可使用基础功能 |
| T-308 | **`/status` 仪表盘增强** | ✅ DONE | 输出结构化 Markdown: 任务进度条 + 知识库统计 + 最近 5 条反思摘要 + 工作流指标趋势 | 2h | T-208 | 执行 `/status` 输出完整仪表盘，含所有区块 |
| T-309 | **全系统回归测试** | ✅ DONE | 分别在 Gemini / Claude / GPT 环境中执行 Mini PRD，验证端到端流程 | 3h | T-305 ~ T-307 | 3 个模型环境均通过 E2E 测试 |

**Phase 3 交付物**:
```
.agent/
├── config/
│   └── agent_config.md          # 统一配置模板 (NEW)
├── guards/
│   ├── pre-commit               # Git Hook (NEW)
│   ├── post-commit              # Git Hook (NEW)
│   └── session_watchdog.py      # 会话看门狗 (NEW)
└── adapters/
    ├── gemini/
    │   └── GEMINI.md            # Gemini 适配器 (MIGRATED)
    ├── claude/
    │   └── CLAUDE.md            # Claude 适配器 (NEW)
    └── copilot/
        └── copilot-instructions.md  # GPT/Copilot 适配器 (NEW)
```

---

## 3. 完整依赖图

```
Phase 1 (Dispatcher MVP)
═══════════════════════════════════════════
T-101 (Worker 封装器) ──┬── T-102 (JSONL 解析)
                        ├── T-105 (Git 提交)
                        └── T-106 (PRD 回写)
T-102 ──────────────────┬── T-103 (重启注入)
                        │
T-103 ──────────────────┬── T-104 (PM 决策)
                        │
T-101 ~ T-106 ──────────┴── T-107 (E2E 测试) ←── Phase 1 Gate

Phase 2 (Evolution Engine)
═══════════════════════════════════════════
T-201 (知识收割) ───────┬── T-202 (索引系统)
                        │
T-202 ──────────────────┬── T-203 (种子知识包)
                        ├── T-204 (Confidence 衰减)
                        └── T-206 (模式检测)
                        │
T-201 + T-206 ──────────┬── T-207 (学习队列)
                        │
T-201 ──────────────────┬── T-205 (反思工作流)
                        │
T-208 (工作流指标) ─────┴── 独立，无依赖 ←── Phase 2 Gate

Phase 3 (加固 & 多模型)
═══════════════════════════════════════════
T-301 (Pre-commit) ─────┬── T-302 (Post-commit)
T-303 (看门狗) ─────────┤   独立
T-304 (配置抽象) ───────┬── T-305 (Gemini 适配)
                        ├── T-306 (Claude 适配)
                        └── T-307 (GPT 适配)
T-208 ──────────────────┬── T-308 (/status 增强)
T-305 ~ T-307 ──────────┴── T-309 (回归测试) ←── Phase 3 Gate
```

---

## 4. 里程碑

| Milestone | 包含任务 | 预计完成 | 交付目标 | Gate 条件 |
|-----------|---------|---------|---------|----------|
| **M1: 核心执行器** | T-101, T-102 | Day 1 | Worker 能启动、解析输出、超时终止 | 单元测试全通过 |
| **M2: 交互 & 提交** | T-103 ~ T-106 | Day 2-3 | 重启注入 + PM 决策 + Git 提交 + PRD 回写 | 集成测试通过 |
| **M3: Dispatcher 闭环** | T-107 | Day 3-4 | 端到端自动执行 Mini PRD | E2E 测试通过 |
| **M4: 知识系统** | T-201 ~ T-204 | Day 5-7 | 知识可自动收割、索引、衰减 | 知识库 ≥ 25 条 |
| **M5: 反思 & 模式** | T-205 ~ T-208 | Day 7-9 | 反思/模式检测/指标追踪全上线 | `/evolve` 命令完整可用 |
| **M6: 守卫层** | T-301 ~ T-303 | Day 9-10 | 关键路径有硬编码保障 | Hook 安装后自动生效 |
| **M7: 多模型 & 发布** | T-304 ~ T-309 | Day 10-12 | 3 模型可用 + 全系统回归 | 3 环境 E2E 通过 |

---

## 5. 风险缓解计划

| 风险 | 概率 | 影响 | 缓解措施 | 负责 |
|------|------|------|---------|------|
| **Codex CLI `--json` 格式变更** | 中 | Worker 封装器失效 | T-102 增加版本检查头，不匹配时 fallback 到 raw text | Phase 1 |
| **重启注入 Token 爆炸** | 中 | 单任务成本激增 | T-103 限制 3 次重启；增量 Prompt 压缩 (只保留最后 500 token 上下文) | Phase 1 |
| **知识收割误提取** | 中 | 低质量知识污染库 | T-204 Confidence 衰减 + T-201 设置最低 Confidence 阈值 0.6 | Phase 2 |
| **模式误识别** | 低 | 错误模式干扰开发 | T-206 最小出现次数 ≥ 3 + 手动审核机制 | Phase 2 |
| **Git Hook 阻断开发** | 低 | 用户体验差 | T-301/T-302 设计为 warning-only，不阻断 commit | Phase 3 |
| **多模型行为差异** | 中 | 同一 Workflow 不同表现 | T-309 建立 Model Compatibility Matrix，标注已知差异 | Phase 3 |

---

## 6. 测试策略

### 6.1 Phase 1 测试矩阵

| 测试类型 | 覆盖范围 | 方法 |
|---------|---------|------|
| **单元测试** | Worker 启动/停止/超时、JSONL 解析、Git 操作 | pytest + Mock |
| **集成测试** | 重启注入全流程、PM 决策链 | Mock Worker (Python subprocess) |
| **E2E 测试** | Mini PRD (3 任务) 端到端执行 | 真实 Codex CLI |

### 6.2 Phase 2 测试矩阵

| 测试类型 | 覆盖范围 | 方法 |
|---------|---------|------|
| **数据测试** | 知识条目 CRUD、索引一致性、Confidence 计算 | 手动验证 Markdown 文件 |
| **流程测试** | `/evolve`、`/reflect` 完整链路 | 对话模拟 |
| **种子数据验证** | 20 条种子知识格式正确性 | Lint 脚本 |

### 6.3 Phase 3 测试矩阵

| 测试类型 | 覆盖范围 | 方法 |
|---------|---------|------|
| **Hook 测试** | Pre/Post-commit 在 Windows/Mac/Linux | 手动测试 + CI |
| **适配器测试** | 3 种模型后端的启动/路由/记忆读写 | 各模型环境 E2E |
| **回归测试** | 全系统 13 个命令可用性 | Checklist 逐一验证 |

---

## 7. 技术规格详述

### 7.1 Worker 封装器 (T-101) 详细设计

```python
# core.py - 数据类定义
@dataclass
class TaskSpec:
    id: str                    # e.g., "T-001"
    name: str                  # e.g., "实现基础调度器"
    description: str           # 任务详细描述
    dependencies: list[str]    # e.g., ["T-001"]
    status: TaskStatus         # PENDING / IN_PROGRESS / DONE / BLOCKED / FAILED
    timeout_seconds: int = 600  # 默认 10 分钟

@dataclass
class WorkerResult:
    task_id: str
    success: bool
    output: str                # Worker 最终输出
    events: list[JSONLEvent]   # 所有 JSONL 事件
    questions: list[str]       # Worker 提出的问题 (如有)
    duration_seconds: float
    restart_count: int         # 重启次数

class TaskStatus(Enum):
    PENDING = "⏳"
    IN_PROGRESS = "🔄"
    DONE = "✅"
    BLOCKED = "🚫"
    RETRY = "🔁"
    FAILED = "❌"
    SKIPPED = "⏭️"
```

### 7.2 JSONL 事件解析 (T-102) 详细设计

```python
# jsonl_parser.py
@dataclass
class JSONLEvent:
    type: str        # agent_message / tool_call / tool_result / error / session_end
    timestamp: float
    content: dict    # 原始 JSON 内容

class JSONLParser:
    def parse_line(self, line: str) -> JSONLEvent | None:
        """解析单行 JSONL，异常时返回 None 而非抛出"""
    
    def detect_question(self, event: JSONLEvent) -> str | None:
        """语义分析: 检测 agent_message 中是否包含疑问"""
        # 检测模式: 疑问句 / 选择请求 / 阻塞声明 / 确认请求
    
    def detect_completion(self, event: JSONLEvent) -> bool:
        """检测 session_end 事件"""
    
    def detect_error(self, event: JSONLEvent) -> str | None:
        """检测 error 事件并提取错误消息"""
```

### 7.3 重启注入 (T-103) 详细设计

```python
# restart_injector.py
class RestartInjector:
    MAX_RESTARTS = 3
    
    def should_restart(self, task_id: str, question: str) -> bool:
        """判断是否应该重启 (未超过次数上限 + 不是风险操作)"""
    
    def build_injected_prompt(
        self, 
        original_prompt: str, 
        qa_pairs: list[tuple[str, str]]
    ) -> str:
        """在原始 Prompt 尾部追加所有 Q&A 对"""
        # 格式:
        # ---
        # [补充信息 1] 关于 "Q1"，答案是: A1
        # [补充信息 2] 关于 "Q2"，答案是: A2
    
    def compress_context(self, prompt: str) -> str:
        """增量压缩: 如果 Prompt 超过 4000 token，截取最后 2000"""
```

### 7.4 配置抽象层 (T-304) 详细设计

```markdown
# .agent/config/agent_config.md

## Model Provider Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PROVIDER` | gemini | gemini / claude / copilot |
| `GLOBAL_CONFIG_PATH` | ~/.gemini/GEMINI.md | 全局配置文件路径 |
| `VIEW_FILE_CMD` | view_file | 读取文件的 API 名称 |
| `REPLACE_FILE_CMD` | replace_file_content | 编辑文件的 API 名称 |
| `RUN_CMD` | flutter run | 项目运行命令 |
| `TEST_CMD` | flutter test | 项目测试命令 |
| `ANALYZE_CMD` | flutter analyze | 项目静态分析命令 |

## Provider Mapping

### Gemini
- Global Config: `~/.gemini/GEMINI.md`
- File Read: `view_file`
- File Write: `replace_file_content`

### Claude
- Global Config: `~/.claude/CLAUDE.md`
- File Read: `read_file`
- File Write: `replace_string_in_file`

### Copilot / GPT
- Global Config: `~/.copilot/copilot-instructions.md`
- File Read: `read_file`
- File Write: `replace_string_in_file`
```

### 7.5 Git 守卫层 (T-301/T-302) 详细设计

```bash
#!/bin/sh
# .agent/guards/pre-commit

# 检查 active_context.md 是否被修改
if ! git diff --cached --name-only | grep -q "active_context.md"; then
    echo "⚠️  [Antigravity Guard] active_context.md 未在本次提交中更新。"
    echo "   建议: 请确保任务状态已同步到记忆文件。"
    # 不阻断 (exit 0)，仅警告
fi
```

```bash
#!/bin/sh
# .agent/guards/post-commit

# 检查上一个 checkpoint 的时间
LAST_CP=$(git tag -l "checkpoint-*" --sort=-creatordate | head -1)
if [ -z "$LAST_CP" ]; then
    git tag "checkpoint-$(date +%Y%m%d-%H%M%S)"
    echo "✅ [Antigravity Guard] 首个检查点已创建。"
else
    LAST_CP_TIME=$(git log -1 --format=%ct "$LAST_CP" 2>/dev/null || echo 0)
    CURRENT_TIME=$(date +%s)
    DIFF=$(( CURRENT_TIME - LAST_CP_TIME ))
    if [ "$DIFF" -gt 1800 ]; then  # 30 分钟
        git tag "checkpoint-$(date +%Y%m%d-%H%M%S)"
        echo "✅ [Antigravity Guard] 新检查点已创建 (距上次 ${DIFF}s)。"
    fi
fi
```

---

## 8. 执行协议

### 8.1 状态定义 (继承 v3.0)

| 状态 | 图标 | 说明 |
|-----|------|-----|
| PENDING | ⏳ | 等待执行 |
| IN_PROGRESS | 🔄 | 正在执行中 |
| DONE | ✅ | 任务已完成 |
| BLOCKED | 🚫 | 需要 User 介入 |
| RETRY | 🔁 | 等待重试 (自动) |
| FAILED | ❌ | 失败 (需人工处理) |
| SKIPPED | ⏭️ | 临时跳过 |

### 8.2 执行规则
1. **Phase Gate**: 每个 Phase 的最后一个任务 (T-107 / T-208 / T-309) 是 Gate，通过后才进入下一 Phase
2. **原子提交**: 每个任务完成后立即 Git 提交
3. **自我更新**: 任务完成后 Agent 更新本文档中对应的状态为 `✅ DONE`
4. **Phase 内并行**: 同一 Phase 内无依赖关系的任务可并行执行

---

## 9. 废弃组件

| 组件 | 原用途 | 替代方案 | 清理时间 |
|-----|-------|---------|---------|
| `GEMINI.md.example` (根目录) | 全局配置模板 | `agent_config.md` + 各适配器 | Phase 3 完成后 |
| `parser.py` (如存在) | 硬编码 Markdown 解析 | Agent 自然语言理解 | 已废弃 |
| `dispatch_task.sh` (如存在) | Shell 调度 | `dispatcher/main.py` | 已废弃 |

---

## 10. 质量标准

| 维度 | 标准 |
|------|------|
| **代码规范** | Python: PEP 8 / Type Hints / Docstrings |
| **测试覆盖** | Phase 1 核心模块 ≥ 80% |
| **文档** | 每个公共函数有 docstring，每个模块有 README |
| **可移植性** | `pip install` 无外部依赖 (仅标准库 + typing) |
| **性能** | 单任务调度延迟 < 3 秒 (不含 Worker 执行时间) |

---

**PRD 已生成。请确认是否开始执行？(Yes/No/修改)**
