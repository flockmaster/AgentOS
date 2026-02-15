"""
Knowledge Harvester — 知识收割器 (T-201)

从任务完成记录、代码变更和对话上下文中提取可复用知识，
生成标准化知识条目 (Markdown + YAML Frontmatter)。

Usage:
    from evolution.harvester import KnowledgeHarvester
    h = KnowledgeHarvester(base_dir=".agent/memory")
    entry = h.harvest(source_type="code_change", context={...})
"""

from __future__ import annotations

import os
import re
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

KNOWLEDGE_DIR = "knowledge"
EVOLUTION_DIR = "evolution"
KNOWLEDGE_BASE = "knowledge_base.md"


# ─── Data Classes ────────────────────────────────────────────

@dataclass
class KnowledgeEntry:
    """知识条目数据结构"""
    id: str                        # e.g. "k-006"
    title: str
    category: str                  # architecture | debugging | pattern | workflow | tooling | anti-pattern | reference-project
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.7
    summary: str = ""
    details: str = ""
    code_example: str = ""
    related: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    created: str = ""
    # v2.0 新增: 因果追踪字段 (向后兼容，新字段可选默认空)
    outcomes: list[dict] = field(default_factory=list)     # [{task, result, time_saved, bugs}]
    causal_score: float = 0.0                               # 基于 outcomes 计算
    last_applied: str = ""                                   # ISO date
    application_count: int = 0

    def __post_init__(self):
        if not self.created:
            self.created = datetime.date.today().isoformat()

    # ── Serialization ──

    def to_markdown(self) -> str:
        """生成标准 Markdown 知识条目"""
        lines = [
            "---",
            f"id: {self.id}",
            f"title: {self.title}",
            f"category: {self.category}",
            f"tags: [{', '.join(self.tags)}]",
            f"created: {self.created}",
            f"confidence: {self.confidence}",
            f"references: [{', '.join(self.references)}]",
            "---",
            "",
            "## Summary",
            self.summary,
            "",
            "## Details",
            self.details,
        ]
        if self.code_example:
            lines += [
                "",
                "## Code Example",
                "```",
                self.code_example,
                "```",
            ]
        if self.related:
            lines += [
                "",
                "## Related Knowledge",
            ]
            for r in self.related:
                lines.append(f"- {r}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def slug(title: str) -> str:
        """title → slug (for filename)"""
        slug = title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        return slug[:60]


# ─── Source Types ────────────────────────────────────────────

VALID_CATEGORIES = {"architecture", "debugging", "pattern", "workflow", "tooling", "anti-pattern", "reference-project"}
VALID_SOURCE_TYPES = {"code_change", "error_fix", "workflow_run", "user_feedback", "conversation", "reference_project"}


# ─── Harvester ───────────────────────────────────────────────

class KnowledgeHarvester:
    """
    知识收割器：分析 source 并生成知识条目。

    Parameters
    ----------
    base_dir : str | Path
        .agent/memory 目录路径
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / KNOWLEDGE_DIR
        self.evolution_dir = self.base_dir / EVOLUTION_DIR
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ──

    def next_id(self) -> str:
        """自动生成下一个知识 ID (k-006, k-007, ...)"""
        existing = list(self.knowledge_dir.glob("k-*.md"))
        max_num = 0
        for f in existing:
            m = re.match(r"k-(\d+)", f.stem)
            if m:
                max_num = max(max_num, int(m.group(1)))
        return f"k-{max_num + 1:03d}"

    def harvest(
        self,
        source_type: str,
        title: str,
        summary: str,
        category: str = "architecture",
        tags: list[str] | None = None,
        details: str = "",
        code_example: str = "",
        related: list[str] | None = None,
        references: list[str] | None = None,
        confidence: float = 0.7,
    ) -> KnowledgeEntry:
        """
        收割一条知识并持久化。

        Parameters
        ----------
        source_type : str
            来源类型 (code_change | error_fix | workflow_run | ...)
        title : str
            知识标题
        summary : str
            一句话概述
        category : str
            类别 (architecture | debugging | pattern | workflow | tooling)
        tags : list[str]
            标签列表
        details : str
            详细说明
        code_example : str
            代码示例
        related : list[str]
            关联知识 ID 列表
        references : list[str]
            引用来源 ID 列表
        confidence : float
            初始置信度 (0.0 ~ 1.0)

        Returns
        -------
        KnowledgeEntry
            已保存的知识条目
        """
        if source_type not in VALID_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {source_type}. Must be one of {VALID_SOURCE_TYPES}")
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {confidence}")

        kid = self.next_id()
        entry = KnowledgeEntry(
            id=kid,
            title=title,
            category=category,
            tags=tags or [],
            confidence=confidence,
            summary=summary,
            details=details,
            code_example=code_example,
            related=related or [],
            references=references or [source_type],
            created=datetime.date.today().isoformat(),
        )
        self._save_entry(entry)
        return entry

    def harvest_from_error_fix(
        self,
        error_type: str,
        root_cause: str,
        solution: str,
        tags: list[str] | None = None,
        references: list[str] | None = None,
    ) -> KnowledgeEntry:
        """快捷方法: 从错误修复中提取知识"""
        return self.harvest(
            source_type="error_fix",
            title=f"Fix: {error_type}",
            summary=f"Root cause: {root_cause}",
            category="debugging",
            tags=tags or [error_type.lower().replace(" ", "-")],
            details=f"## Root Cause\n{root_cause}\n\n## Solution\n{solution}",
            confidence=0.8,
            references=references or ["error_fix"],
        )

    def harvest_from_code_change(
        self,
        title: str,
        summary: str,
        code_example: str = "",
        category: str = "pattern",
        tags: list[str] | None = None,
        references: list[str] | None = None,
    ) -> KnowledgeEntry:
        """快捷方法: 从代码变更中提取知识"""
        return self.harvest(
            source_type="code_change",
            title=title,
            summary=summary,
            category=category,
            tags=tags or [],
            code_example=code_example,
            confidence=0.7,
            references=references or ["code_change"],
        )

    def harvest_anti_knowledge(
        self,
        title: str,
        summary: str,
        details: str = "",
        tags: list[str] | None = None,
        references: list[str] | None = None,
        related: list[str] | None = None,
    ) -> KnowledgeEntry:
        """
        收割反知识 (anti-knowledge)。

        反知识是应用后反而导致问题的知识条目，
        记录为 anti-pattern 类别以供未来决策参考。
        """
        return self.harvest(
            source_type="error_fix",
            title=f"Anti-Pattern: {title}",
            summary=summary,
            category="anti-pattern",
            tags=["anti-pattern"] + (tags or []),
            details=details,
            confidence=0.85,
            related=related or [],
            references=references or ["causal_analysis"],
        )

    def harvest_from_reference_project(
        self,
        title: str,
        summary: str,
        details: str = "",
        code_example: str = "",
        tags: list[str] | None = None,
        project_path: str = "",
    ) -> KnowledgeEntry:
        """
        从参考项目学习中提取知识。

        Parameters
        ----------
        title : str
            知识标题
        summary : str
            一句话概述
        details : str
            详细说明
        code_example : str
            代码示例
        tags : list[str]
            标签列表
        project_path : str
            参考项目路径
        """
        return self.harvest(
            source_type="reference_project",
            title=title,
            summary=summary,
            category="reference-project",
            tags=["reference-project"] + (tags or []),
            details=details,
            code_example=code_example,
            confidence=0.75,
            references=[f"ref-project:{project_path}"] if project_path else ["reference_project"],
        )

    # ── Private ──

    def _save_entry(self, entry: KnowledgeEntry) -> Path:
        """保存知识条目 Markdown 文件"""
        slug = KnowledgeEntry.slug(entry.title)
        filename = f"{entry.id}-{slug}.md"
        filepath = self.knowledge_dir / filename
        filepath.write_text(entry.to_markdown(), encoding="utf-8")
        return filepath

    # ── Knowledge Index Operations (T-202 에서 확장) ──

    def list_entries(self) -> list[dict]:
        """列出所有知识条目的元信息"""
        entries = []
        for f in sorted(self.knowledge_dir.glob("k-*.md")):
            meta = self._parse_frontmatter(f)
            if meta:
                entries.append(meta)
        return entries

    def get_entry(self, kid: str) -> Optional[str]:
        """按 ID 获取知识条目全文"""
        for f in self.knowledge_dir.glob(f"{kid}-*.md"):
            return f.read_text(encoding="utf-8")
        return None

    def search(self, query: str) -> list[dict]:
        """按关键词搜索知识库"""
        query_lower = query.lower()
        results = []
        for entry in self.list_entries():
            title = entry.get("title", "").lower()
            category = entry.get("category", "").lower()
            tags = " ".join(entry.get("tags", [])).lower()
            if query_lower in title or query_lower in category or query_lower in tags:
                results.append(entry)
        return results

    @staticmethod
    def _parse_frontmatter(filepath: Path) -> Optional[dict]:
        """解析 YAML Frontmatter"""
        text = filepath.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return None
        meta = {}
        for line in m.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                # Parse list values like [tag1, tag2]
                if val.startswith("[") and val.endswith("]"):
                    val = [v.strip() for v in val[1:-1].split(",") if v.strip()]
                meta[key] = val
        meta["_file"] = str(filepath)
        return meta
