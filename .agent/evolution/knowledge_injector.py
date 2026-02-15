"""
Knowledge Injector — 知识注入器

在工作流各阶段开始前，自动检索并注入相关知识:
  - 按 causal_score * confidence 排序
  - 返回 top-k 条知识摘要 (每条 ≤200 字)
  - 格式化为 Prompt 注入块

Usage:
    from evolution.knowledge_injector import KnowledgeInjector
    ki = KnowledgeInjector(base_dir=".agent/memory")
    entries = ki.retrieve_relevant(phase="drafting", keywords=["状态管理", "Flutter"])
    prompt_block = ki.format_for_prompt(entries)
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

from evolution.harvester import KnowledgeHarvester
from evolution.confidence import ConfidenceEngine
from evolution.causal_metrics import CausalMetrics


class KnowledgeInjector:
    """
    知识注入器。

    职责:
    1. 根据工作流阶段和关键词检索相关知识
    2. 按 causal_score * confidence 排序
    3. 格式化为 Prompt 注入块 (每条 ≤200 字)
    4. 记录注入事件到 injection_log.md
    """

    # 阶段-类别关联映射
    PHASE_CATEGORY_MAP = {
        "drafting": ["architecture", "workflow", "reference-project"],
        "reviewing": ["debugging", "anti-pattern", "architecture"],
        "decomposing": ["pattern", "architecture", "workflow"],
        "implementing": ["pattern", "debugging", "tooling", "reference-project"],
    }

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.harvester = KnowledgeHarvester(base_dir)
        self.confidence_engine = ConfidenceEngine(base_dir)
        self.causal_metrics = CausalMetrics(base_dir)
        self.injection_log = self.base_dir / "evolution" / "injection_log.md"
        self._ensure_log()

    def _ensure_log(self) -> None:
        """确保 injection_log.md 存在"""
        if not self.injection_log.exists():
            self.injection_log.parent.mkdir(parents=True, exist_ok=True)
            self.injection_log.write_text(
                "# Injection Log\n\n"
                "知识注入事件日志，用于元学习分析。\n\n"
                "| Date | Phase | Keywords | Injected IDs | Count |\n"
                "|------|-------|----------|-------------|-------|\n",
                encoding="utf-8",
            )

    # ── Public API ──

    def retrieve_relevant(
        self,
        phase: str,
        keywords: list[str],
        top_k: int = 5,
    ) -> list[dict]:
        """
        检索与当前阶段和关键词相关的知识条目。

        排序依据: composite_score = causal_score * 0.4 + confidence * 0.6
        (causal_score 为 0 时回退到纯 confidence 排序)

        Parameters
        ----------
        phase : str
            工作流阶段 (drafting, reviewing, decomposing, implementing)
        keywords : list[str]
            当前任务关键词
        top_k : int
            返回条目数上限

        Returns
        -------
        list[dict]
            [{id, title, category, confidence, causal_score, composite_score, summary}, ...]
        """
        all_entries = self.harvester.list_entries()
        preferred_categories = self.PHASE_CATEGORY_MAP.get(phase, [])

        scored_entries = []
        for entry in all_entries:
            title = entry.get("title", "").lower()
            tags = " ".join(entry.get("tags", [])).lower() if isinstance(entry.get("tags"), list) else str(entry.get("tags", "")).lower()
            category = entry.get("category", "").lower()
            kid = entry.get("id", "")

            # 关键词匹配评分
            keyword_score = 0
            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in title:
                    keyword_score += 2
                if kw_lower in tags:
                    keyword_score += 1
                if kw_lower in category:
                    keyword_score += 1

            if keyword_score == 0 and category not in preferred_categories:
                continue

            # 类别偏好加分
            if category in preferred_categories:
                keyword_score += 1

            confidence = float(entry.get("confidence", 0.7))
            causal = self.causal_metrics.causal_score(kid)

            # composite_score: causal_score 为 0 时回退到 confidence
            if causal != 0.0:
                composite = causal * 0.4 + confidence * 0.6
            else:
                composite = confidence

            # 关键词匹配作为乘数
            final_score = composite * (1 + keyword_score * 0.2)

            scored_entries.append({
                "id": kid,
                "title": entry.get("title", ""),
                "category": category,
                "confidence": confidence,
                "causal_score": causal,
                "composite_score": round(final_score, 3),
                "summary": self._get_summary(kid),
            })

        # 按 composite_score 降序排序
        scored_entries.sort(key=lambda x: x["composite_score"], reverse=True)
        result = scored_entries[:top_k]

        # 记录注入事件
        if result:
            self._log_injection(phase, keywords, result)

        return result

    def format_for_prompt(self, entries: list[dict]) -> str:
        """
        格式化知识条目为 Prompt 注入块。

        每条 ≤200 字，整体格式:
        ```
        📚 知识注入 (共 N 条)
        ---
        [k-001] Title (confidence: 0.9, causal: 0.7)
        Summary text...
        ---
        ```

        Parameters
        ----------
        entries : list[dict]
            retrieve_relevant() 返回的条目列表

        Returns
        -------
        str
            格式化的 Prompt 注入块
        """
        if not entries:
            return ""

        lines = [f"📚 知识注入 (共 {len(entries)} 条)", ""]
        for entry in entries:
            kid = entry.get("id", "")
            title = entry.get("title", "")
            conf = entry.get("confidence", 0.0)
            causal = entry.get("causal_score", 0.0)
            summary = entry.get("summary", "")

            # 截断到 200 字
            if len(summary) > 200:
                summary = summary[:197] + "..."

            lines.append("---")
            causal_str = f", causal: {causal}" if causal != 0.0 else ""
            lines.append(f"**[{kid}]** {title} (confidence: {conf}{causal_str})")
            lines.append(summary)

        lines.append("---")
        lines.append("")
        return "\n".join(lines)

    # ── Private Methods ──

    def _get_summary(self, kid: str) -> str:
        """获取知识条目摘要"""
        content = self.harvester.get_entry(kid)
        if not content:
            return ""

        # 提取 Summary 部分
        lines = content.split("\n")
        in_summary = False
        summary_lines = []
        for line in lines:
            if line.strip() == "## Summary":
                in_summary = True
                continue
            if in_summary and line.startswith("## "):
                break
            if in_summary and line.strip():
                summary_lines.append(line.strip())

        return " ".join(summary_lines)[:200]

    def _log_injection(self, phase: str, keywords: list[str], entries: list[dict]) -> None:
        """记录注入事件到 injection_log.md"""
        today = datetime.date.today().isoformat()
        ids = ", ".join(e["id"] for e in entries)
        kw = ", ".join(keywords[:5])
        row = f"| {today} | {phase} | {kw} | {ids} | {len(entries)} |"

        text = self.injection_log.read_text(encoding="utf-8")
        text = text.rstrip() + "\n" + row + "\n"
        self.injection_log.write_text(text, encoding="utf-8")
