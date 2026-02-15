"""
Dependency Analyzer — 依赖图谱分析器

构建 .agent/ 目录内文件的结构性依赖图谱，支持:
  - 自动扫描文件间引用关系 (build_graph)
  - 变更影响分析 (impact_analysis)
  - Git 变更同步检查 (sync_check)

当文件被修改时，自动识别所有需要连锁升级的关联文件。

Usage:
    from evolution.dependency_analyzer import DependencyAnalyzer
    da = DependencyAnalyzer(base_dir=".agent/memory")
    da.build_graph()
    report = da.sync_check()
    impact = da.impact_analysis([".agent/skills/requirement-analyst/SKILL.md"])
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class DependencyEdge:
    """依赖边"""
    source: str          # 源文件 (依赖方)
    target: str          # 目标文件 (被依赖方)
    edge_type: str       # invokes | reads | writes | references | chain_next | imports | mirrors
    context: str = ""    # 关系描述


# ── 静态引用模式 (仅用于记忆文件和规则文件等不可自动发现的引用) ──

# 记忆文件引用关键词 → 路径
MEMORY_REFERENCES = {
    "active_context.md": ".agent/memory/active_context.md",
    "project_decisions.md": ".agent/memory/project_decisions.md",
    "knowledge_base.md": ".agent/memory/evolution/knowledge_base.md",
    "pattern_library.md": ".agent/memory/evolution/pattern_library.md",
    "learning_queue.md": ".agent/memory/evolution/learning_queue.md",
    "decision_log.md": ".agent/memory/evolution/decision_log.md",
    "decision_graph.json": ".agent/memory/evolution/decision_graph.json",
    "injection_log.md": ".agent/memory/evolution/injection_log.md",
    "outcome_tracker.md": ".agent/memory/evolution/outcome_tracker.md",
    "meta_insights.md": ".agent/memory/evolution/meta_insights.md",
    "learned_projects.md": ".agent/memory/evolution/learned_projects.md",
    "evolution_config.md": ".agent/memory/evolution/evolution_config.md",
    "workflow_metrics.md": ".agent/memory/evolution/workflow_metrics.md",
    "gate_deviation_log.md": ".agent/memory/evolution/gate_deviation_log.md",
    "reflection_log.md": ".agent/memory/evolution/reflection_log.md",
    "state_machine.md": ".agent/memory/state_machine.md",
    "user_preferences.md": ".agent/memory/user_preferences.md",
}

# 规则文件引用
RULE_REFERENCES = {
    "router.rule": ".agent/rules/router.rule",
    "skills.rule": ".agent/rules/skills.rule",
    "gatekeepers.rule": ".agent/rules/gatekeepers.rule",
}


def _file_type(path: str) -> str:
    """根据路径推断节点类型"""
    if "/workflows/" in path:
        return "workflow"
    if "/skills/" in path:
        return "skill"
    if "/prompts/roles/" in path:
        return "role"
    if "/rules/" in path:
        return "rule"
    if "/adapters/" in path:
        return "adapter"
    if "/evolution/" in path:
        return "evolution"
    if "/memory/" in path:
        return "memory"
    return "other"


def _content_hash(content: str) -> str:
    """计算内容的短 hash"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()[:12]


class DependencyAnalyzer:
    """
    依赖图谱分析器。

    职责:
    1. 扫描 .agent/ 目录内文件间的引用关系
    2. 构建依赖图谱 (dependency_graph.json)
    3. 分析变更影响范围 (impact_analysis)
    4. 对比 git diff 检测未同步文件 (sync_check)
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.graph_file = self.base_dir / "evolution" / "file_dependency_graph.json"
        # .agent 根目录 (base_dir 的父级)
        self.agent_dir = self.base_dir.parent
        # 项目根目录 (.agent 的父级)
        self.project_root = self.agent_dir.parent
        # 动态发现的引用映射 (每次 build_graph 时刷新)
        self._skill_names: dict[str, str] = {}
        self._role_names: dict[str, str] = {}
        self._workflow_commands: dict[str, str] = {}
        self._workflow_keywords: dict[str, str] = {}
        self._evolution_modules: dict[str, str] = {}
        self._python_imports: dict[str, str] = {}
        self._peer_groups: list[list[str]] = []

    # ── Public API ──

    def build_graph(self) -> dict:
        """
        扫描 .agent/ 目录，构建文件依赖图谱。

        扫描范围:
        - workflows/*.md
        - skills/*/SKILL.md
        - prompts/roles/*.md
        - rules/*.rule
        - adapters/*/CLAUDE.md 等
        - evolution/*.py

        新增文件会被自动发现并纳入图谱。

        Returns
        -------
        dict
            {"nodes": {...}, "edges": [...], "metadata": {...}}
        """
        # Step 0: 动态发现所有引用映射 (替代硬编码字典)
        self._discover_references()

        nodes = {}
        edges = []

        # 收集所有需扫描的文件
        scan_files = self._collect_scannable_files()

        for abs_path in scan_files:
            rel_path = self._to_rel_path(abs_path)
            if not rel_path:
                continue

            content = self._read_file_safe(abs_path)
            if not content:
                continue

            # 构建节点
            nodes[rel_path] = {
                "path": rel_path,
                "type": _file_type(rel_path),
                "version_hash": _content_hash(content),
                "dependencies": [],
                "dependents": [],
            }

            # 检测引用关系
            file_edges = self._detect_references(rel_path, content)
            edges.extend(file_edges)

        # Step N: 添加同族 (peer/mirrors) 关系
        peer_edges = self._build_peer_edges(nodes)
        edges.extend(peer_edges)

        # 将边信息回填到节点的 dependencies / dependents
        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            if src in nodes and tgt not in nodes[src]["dependencies"]:
                nodes[src]["dependencies"].append(tgt)
            if tgt in nodes and src not in nodes[tgt]["dependents"]:
                nodes[tgt]["dependents"].append(src)

        graph = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "version": "1.1",
                "last_rebuilt": datetime.date.today().isoformat(),
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "peer_groups": len(self._peer_groups),
            },
        }

        self._save_graph(graph)
        return graph

    def impact_analysis(self, changed_files: list[str]) -> list[dict]:
        """
        分析变更文件的影响范围。

        使用 BFS 逐层传播，返回按层级排序的受影响文件。

        Parameters
        ----------
        changed_files : list[str]
            已变更文件的相对路径列表

        Returns
        -------
        list[dict]
            [{
                "file": str,           # 受影响文件路径
                "depth": int,          # 影响层级 (1=直接依赖, 2=二级, ...)
                "impact_chain": list,  # 传播链路 [changed -> ... -> this]
                "edge_type": str,      # 关系类型
                "context": str,        # 关系描述
            }, ...]
        """
        graph = self._load_graph()
        if not graph.get("nodes"):
            return []

        # BFS 传播
        visited = set(changed_files)
        queue = []  # (file, depth, chain)
        results = []

        # 初始化队列: 所有 changed_files 的直接 dependents
        for cf in changed_files:
            node = graph["nodes"].get(cf, {})
            for dep in node.get("dependents", []):
                if dep not in visited:
                    # 找到对应的边信息
                    edge_info = self._find_edge(graph, dep, cf)
                    queue.append((dep, 1, [cf, dep]))
                    visited.add(dep)
                    results.append({
                        "file": dep,
                        "depth": 1,
                        "impact_chain": [cf, dep],
                        "edge_type": edge_info.get("edge_type", "references"),
                        "context": edge_info.get("context", ""),
                    })

        # BFS 层级展开 (最多 3 层)
        while queue:
            current, depth, chain = queue.pop(0)
            if depth >= 3:
                continue

            node = graph["nodes"].get(current, {})
            for dep in node.get("dependents", []):
                if dep not in visited:
                    edge_info = self._find_edge(graph, dep, current)
                    new_chain = chain + [dep]
                    visited.add(dep)
                    queue.append((dep, depth + 1, new_chain))
                    results.append({
                        "file": dep,
                        "depth": depth + 1,
                        "impact_chain": new_chain,
                        "edge_type": edge_info.get("edge_type", "references"),
                        "context": edge_info.get("context", ""),
                    })

        # 按层级排序
        results.sort(key=lambda x: x["depth"])
        return results

    def sync_check(self) -> dict:
        """
        对比 git 变更与依赖图谱，检测未同步的关联文件。

        Returns
        -------
        dict
            {
                "changed_files": list,      # git 中已变更的文件
                "needs_sync": list[dict],   # 需要同步检查的文件
                "already_synced": list,      # 已在变更中的关联文件 (无需额外操作)
                "summary": str,             # 人类可读的摘要
            }
        """
        # 获取 git 变更文件
        changed_files = self._detect_git_changes()
        if not changed_files:
            return {
                "changed_files": [],
                "needs_sync": [],
                "already_synced": [],
                "summary": "没有检测到 git 变更文件。",
            }

        # 确保图谱是最新的
        graph = self._load_graph()
        if not graph.get("nodes"):
            self.build_graph()

        # 影响分析
        all_impacts = self.impact_analysis(changed_files)

        # 分类: 已同步 vs 需同步
        changed_set = set(changed_files)
        needs_sync = []
        already_synced = []

        for impact in all_impacts:
            if impact["file"] in changed_set:
                already_synced.append(impact["file"])
            else:
                needs_sync.append(impact)

        # 生成摘要
        summary_lines = []
        if needs_sync:
            summary_lines.append(f"发现 {len(needs_sync)} 个关联文件可能需要同步更新:")
            for item in needs_sync:
                depth_label = {1: "直接依赖", 2: "二级依赖", 3: "三级依赖"}.get(
                    item["depth"], f"{item['depth']}级依赖"
                )
                chain_str = " -> ".join(
                    os.path.basename(f) for f in item["impact_chain"]
                )
                summary_lines.append(
                    f"  - [{depth_label}] {item['file']}"
                    f"\n    链路: {chain_str}"
                    f"\n    关系: {item['edge_type']} ({item['context']})"
                )
        else:
            summary_lines.append("所有关联文件均已同步更新，无需额外操作。")

        if already_synced:
            summary_lines.append(
                f"\n已同步的关联文件 ({len(already_synced)} 个): "
                + ", ".join(os.path.basename(f) for f in already_synced)
            )

        return {
            "changed_files": changed_files,
            "needs_sync": needs_sync,
            "already_synced": already_synced,
            "summary": "\n".join(summary_lines),
        }

    def get_stats(self) -> dict:
        """
        获取依赖图谱统计。

        Returns
        -------
        dict
            {
                "total_nodes": int,
                "total_edges": int,
                "by_type": dict,        # 按节点类型分组统计
                "top_dependents": list,  # 被依赖最多的文件 (扇入最高)
                "top_dependencies": list, # 依赖最多的文件 (扇出最高)
                "isolated_nodes": int,   # 孤立节点数
            }
        """
        graph = self._load_graph()
        nodes = graph.get("nodes", {})

        if not nodes:
            return {
                "total_nodes": 0, "total_edges": 0, "by_type": {},
                "top_dependents": [], "top_dependencies": [],
                "isolated_nodes": 0,
            }

        # 按类型分组
        by_type = defaultdict(int)
        for node in nodes.values():
            by_type[node.get("type", "other")] += 1

        # 扇入排名 (被依赖最多)
        fan_in = [
            (path, len(node.get("dependents", [])))
            for path, node in nodes.items()
        ]
        fan_in.sort(key=lambda x: x[1], reverse=True)

        # 扇出排名 (依赖最多)
        fan_out = [
            (path, len(node.get("dependencies", [])))
            for path, node in nodes.items()
        ]
        fan_out.sort(key=lambda x: x[1], reverse=True)

        # 孤立节点
        isolated = sum(
            1 for node in nodes.values()
            if not node.get("dependencies") and not node.get("dependents")
        )

        return {
            "total_nodes": len(nodes),
            "total_edges": len(graph.get("edges", [])),
            "by_type": dict(by_type),
            "top_dependents": [
                {"file": p, "count": c} for p, c in fan_in[:5] if c > 0
            ],
            "top_dependencies": [
                {"file": p, "count": c} for p, c in fan_out[:5] if c > 0
            ],
            "isolated_nodes": isolated,
        }

    def format_sync_report(self, sync_result: dict) -> str:
        """
        将 sync_check 结果格式化为 Markdown 报告。

        Parameters
        ----------
        sync_result : dict
            sync_check() 的返回值

        Returns
        -------
        str
            Markdown 格式的报告
        """
        stats = self.get_stats()
        lines = [
            "# 🔗 依赖同步检查报告",
            "",
            "## 图谱概况",
            f"- **节点数**: {stats['total_nodes']}",
            f"- **边数**: {stats['total_edges']}",
            f"- **孤立节点**: {stats['isolated_nodes']}",
        ]

        if stats.get("by_type"):
            lines.append("- **类型分布**: " + ", ".join(
                f"{t}: {c}" for t, c in stats["by_type"].items()
            ))

        lines += ["", "## 变更文件"]
        changed = sync_result.get("changed_files", [])
        if changed:
            for f in changed:
                lines.append(f"- `{f}`")
        else:
            lines.append("- 无变更文件")

        needs_sync = sync_result.get("needs_sync", [])
        if needs_sync:
            lines += [
                "",
                f"## 需要同步检查 ({len(needs_sync)} 个文件)",
                "",
            ]
            for item in needs_sync:
                depth_label = {1: "直接", 2: "二级", 3: "三级"}.get(
                    item["depth"], f"{item['depth']}级"
                )
                chain_str = " → ".join(
                    os.path.basename(f) for f in item["impact_chain"]
                )
                lines.append(f"### [{depth_label}依赖] `{item['file']}`")
                lines.append(f"- **关系**: {item['edge_type']}")
                lines.append(f"- **描述**: {item['context']}")
                lines.append(f"- **传播链**: {chain_str}")
                lines.append("")
        else:
            lines += [
                "",
                "## 同步状态",
                "",
                "所有关联文件均已同步，无需额外操作。",
            ]

        already = sync_result.get("already_synced", [])
        if already:
            lines += [
                "",
                f"## 已同步的关联文件 ({len(already)} 个)",
                "",
            ]
            for f in already:
                lines.append(f"- `{f}`")

        lines += [
            "",
            "---",
            f"*Dependency Analyzer v1.0 | {datetime.date.today().isoformat()}*",
        ]

        return "\n".join(lines)

    # ── Private Methods ──

    def _collect_scannable_files(self) -> list[Path]:
        """收集所有需扫描的文件"""
        files = []
        agent_dir = self.agent_dir

        # workflows/*.md
        wf_dir = agent_dir / "workflows"
        if wf_dir.exists():
            for f in wf_dir.glob("*.md"):
                if not f.name.startswith("_"):
                    files.append(f)

        # skills/*/SKILL.md
        skills_dir = agent_dir / "skills"
        if skills_dir.exists():
            for f in skills_dir.glob("*/SKILL.md"):
                if "/_archive/" not in str(f):
                    files.append(f)

        # prompts/roles/*.md
        roles_dir = agent_dir / "prompts" / "roles"
        if roles_dir.exists():
            for f in roles_dir.glob("*.md"):
                files.append(f)

        # rules/*.rule
        rules_dir = agent_dir / "rules"
        if rules_dir.exists():
            for f in rules_dir.glob("*.rule"):
                files.append(f)

        # adapters/*/*.md (CLAUDE.md, COPILOT.md, etc.)
        adapters_dir = agent_dir / "adapters"
        if adapters_dir.exists():
            for f in adapters_dir.glob("*/*.md"):
                files.append(f)
            for f in adapters_dir.glob("*/*.rules"):
                files.append(f)

        # evolution/*.py
        evo_dir = agent_dir / "evolution"
        if evo_dir.exists():
            for f in evo_dir.glob("*.py"):
                files.append(f)

        return files

    def _to_rel_path(self, abs_path: Path) -> str:
        """将绝对路径转为相对于项目根的路径"""
        try:
            return str(abs_path.relative_to(self.project_root))
        except ValueError:
            return ""

    def _detect_references(self, source_path: str, content: str) -> list[dict]:
        """
        检测文件内容中的引用关系。

        使用动态发现的引用映射，自动适配新增文件。
        返回从 source_path 指向其他文件的边列表。
        """
        edges = []
        seen_targets = set()

        def _add_edge(target: str, edge_type: str, context: str):
            if target != source_path and target not in seen_targets:
                seen_targets.add(target)
                edges.append(asdict(DependencyEdge(
                    source=source_path,
                    target=target,
                    edge_type=edge_type,
                    context=context,
                )))

        # 1. 显式文件路径引用 (.agent/.../*.md, .agent/.../*.py, .agent/.../*.rule)
        path_pattern = re.compile(r'\.agent/[\w/.-]+\.(?:md|py|rule|json)')
        for match in path_pattern.finditer(content):
            ref_path = match.group(0)
            _add_edge(ref_path, "references", "显式路径引用")

        # 2. 技能名称引用 (动态)
        for skill_name, skill_path in self._skill_names.items():
            pattern = re.compile(
                rf'(?:技能|skill|`){re.escape(skill_name)}`?|{re.escape(skill_name)}(?:\s*(?:技能|skill))',
                re.IGNORECASE,
            )
            if pattern.search(content):
                _add_edge(skill_path, "invokes", f"引用技能 {skill_name}")

        # 3. 角色名称引用 (动态)
        for role_name, role_path in self._role_names.items():
            if role_name in content or f"{role_name}.md" in content:
                _add_edge(role_path, "references", f"引用角色 {role_name}")

        # 4. 工作流斜杠命令引用 (动态)
        for cmd, wf_path in self._workflow_commands.items():
            if cmd in content and wf_path != source_path:
                _add_edge(wf_path, "references", f"引用工作流 {cmd}")

        # 5. 工作流链式引用 (动态)
        for wf_key, wf_path in self._workflow_keywords.items():
            if wf_key in content and wf_path != source_path:
                if re.search(rf'(?:进入|触发|→)\s*.*{re.escape(wf_key)}', content):
                    _add_edge(wf_path, "chain_next", f"链式触发 {wf_key}")
                else:
                    _add_edge(wf_path, "references", f"引用工作流 {wf_key}")

        # 6. 进化引擎模块引用 — 类名 (动态)
        for class_name, mod_path in self._evolution_modules.items():
            if class_name in content and mod_path != source_path:
                _add_edge(mod_path, "references", f"引用模块 {class_name}")

        # 7. Python import 引用 (动态)
        for mod_name, mod_path in self._python_imports.items():
            import_pattern = re.compile(
                rf'from\s+{re.escape(mod_name)}\s+import|import\s+{re.escape(mod_name)}'
            )
            if import_pattern.search(content) and mod_path != source_path:
                _add_edge(mod_path, "imports", f"Python 导入 {mod_name}")

        # 8. 记忆文件引用 (静态 — 记忆文件路径相对固定)
        for mem_name, mem_path in MEMORY_REFERENCES.items():
            if mem_name in content:
                if re.search(
                    rf'(?:写入|追加|更新|write|append|save).*{re.escape(mem_name)}',
                    content, re.IGNORECASE,
                ):
                    _add_edge(mem_path, "writes", f"写入 {mem_name}")
                elif re.search(
                    rf'(?:读取|检查|加载|read|load|check).*{re.escape(mem_name)}',
                    content, re.IGNORECASE,
                ):
                    _add_edge(mem_path, "reads", f"读取 {mem_name}")
                else:
                    _add_edge(mem_path, "references", f"引用 {mem_name}")

        # 9. 规则文件引用 (静态)
        for rule_name, rule_path in RULE_REFERENCES.items():
            if rule_name in content and rule_path != source_path:
                _add_edge(rule_path, "references", f"引用规则 {rule_name}")

        return edges

    def _discover_references(self) -> None:
        """
        动态扫描 .agent/ 目录，构建所有引用映射。

        替代硬编码字典，自动发现新增的技能、角色、工作流、进化模块。
        同时构建同族分组 (peer groups)。
        """
        agent_dir = self.agent_dir

        # 1. 动态发现技能 (skills/*/SKILL.md)
        self._skill_names = {}
        skills_dir = agent_dir / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        name = skill_dir.name  # e.g., "requirement-analyst"
                        rel = f".agent/skills/{name}/SKILL.md"
                        self._skill_names[name] = rel

        # 2. 动态发现角色 (prompts/roles/*.md)
        self._role_names = {}
        roles_dir = agent_dir / "prompts" / "roles"
        if roles_dir.exists():
            for f in roles_dir.glob("*.md"):
                name = f.stem  # e.g., "product_director"
                rel = f".agent/prompts/roles/{f.name}"
                self._role_names[name] = rel

        # 3. 动态发现工作流 (workflows/*.md)
        self._workflow_commands = {}
        self._workflow_keywords = {}
        wf_dir = agent_dir / "workflows"
        if wf_dir.exists():
            for f in wf_dir.glob("*.md"):
                if f.name.startswith("_"):
                    continue
                stem = f.stem  # e.g., "evolve", "1-drafting"
                rel = f".agent/workflows/{f.name}"
                # 斜杠命令: /evolve, /analyze-error, etc.
                self._workflow_commands[f"/{stem}"] = rel
                # 关键词引用: "1-drafting", "evolve"
                self._workflow_keywords[stem] = rel

        # 4. 动态发现进化模块 (evolution/*.py)
        self._evolution_modules = {}
        self._python_imports = {}
        evo_dir = agent_dir / "evolution"
        if evo_dir.exists():
            for f in evo_dir.glob("*.py"):
                if f.name == "__init__.py":
                    continue
                stem = f.stem  # e.g., "harvester"
                rel = f".agent/evolution/{f.name}"
                # Python import 名: "evolution.harvester"
                mod_name = f"evolution.{stem}"
                self._python_imports[mod_name] = rel
                # 从文件内容中提取类名
                content = self._read_file_safe(f)
                for match in re.finditer(r'^class\s+(\w+)', content, re.MULTILINE):
                    class_name = match.group(1)
                    self._evolution_modules[class_name] = rel

        # 5. 构建同族分组 (Peer Groups)
        #    同族 = 同一目录类型下功能对等的文件
        self._peer_groups = []

        # 5a. 适配器同族: adapters/*/下的主文件互为 mirrors
        adapters_dir = agent_dir / "adapters"
        if adapters_dir.exists():
            adapter_files = []
            for adapter_dir in sorted(adapters_dir.iterdir()):
                if not adapter_dir.is_dir():
                    continue
                # 每个适配器目录的主文件 (第一个 .md)
                md_files = sorted(adapter_dir.glob("*.md"))
                if md_files:
                    adapter_files.append(
                        self._to_rel_path(md_files[0])
                    )
            if len(adapter_files) > 1:
                self._peer_groups.append(adapter_files)

            # 5b. copilot 有两个文件 (COPILOT.md + copilot-instructions.md)
            #     copilot-instructions.md 也是适配器的一部分
            copilot_dir = adapters_dir / "copilot"
            if copilot_dir.exists():
                copilot_files = [
                    self._to_rel_path(f) for f in sorted(copilot_dir.glob("*.md"))
                ]
                if len(copilot_files) > 1:
                    self._peer_groups.append(copilot_files)

    def _build_peer_edges(self, nodes: dict) -> list[dict]:
        """
        为同族文件组构建 mirrors 边 (双向)。

        同族文件修改一个，其他都需要同步检查。
        """
        edges = []
        for group in self._peer_groups:
            # 过滤出实际存在于图谱中的节点
            valid = [f for f in group if f in nodes]
            if len(valid) < 2:
                continue
            # 每对文件之间建立双向 mirrors 边
            for i, src in enumerate(valid):
                for tgt in valid[i + 1:]:
                    edges.append(asdict(DependencyEdge(
                        source=src,
                        target=tgt,
                        edge_type="mirrors",
                        context="同族适配器，需保持多平台同步",
                    )))
                    edges.append(asdict(DependencyEdge(
                        source=tgt,
                        target=src,
                        edge_type="mirrors",
                        context="同族适配器，需保持多平台同步",
                    )))

        return edges

    def _find_edge(self, graph: dict, source: str, target: str) -> dict:
        """在图谱中查找指定的边"""
        for edge in graph.get("edges", []):
            if edge["source"] == source and edge["target"] == target:
                return edge
        return {}

    def _detect_git_changes(self) -> list[str]:
        """
        检测 git 变更文件 (staged + unstaged + untracked)。

        只返回 .agent/ 目录下的文件。
        """
        try:
            # staged + unstaged
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True, text=True,
                cwd=str(self.project_root),
                timeout=10,
            )
            files = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()

            # unstaged (未 add 的修改)
            result2 = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True,
                cwd=str(self.project_root),
                timeout=10,
            )
            if result2.stdout.strip():
                files.update(result2.stdout.strip().split("\n"))

            # untracked
            result3 = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True, text=True,
                cwd=str(self.project_root),
                timeout=10,
            )
            if result3.stdout.strip():
                files.update(result3.stdout.strip().split("\n"))

            # 只保留 .agent/ 目录下的文件
            return [f for f in sorted(files) if f.startswith(".agent/") and f]

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _load_graph(self) -> dict:
        """加载依赖图谱"""
        try:
            text = self.graph_file.read_text(encoding="utf-8")
            return json.loads(text)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"nodes": {}, "edges": [], "metadata": {}}

    def _save_graph(self, graph: dict) -> None:
        """保存依赖图谱"""
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        self.graph_file.write_text(
            json.dumps(graph, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _read_file_safe(filepath: Path) -> str:
        """安全读取文件内容"""
        try:
            if filepath.exists() and filepath.stat().st_size < 200_000:
                return filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            pass
        return ""
