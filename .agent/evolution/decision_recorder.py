"""
Decision Recorder — 决策记录器

记录 Agent 在工作流中做出的每个决策，支持回放和相似决策查找：
  - 记录决策上下文、选项、选择理由
  - 基于关键词重叠评分查找相似历史决策
  - 持久化到 decision_log.md

Usage:
    from evolution.decision_recorder import DecisionRecorder
    dr = DecisionRecorder(base_dir=".agent/memory")
    dr.record(phase="drafting", context="需要选择状态管理方案",
              options=["Provider", "Riverpod", "Bloc"],
              chosen="Riverpod", reason="团队熟悉度高")
    similar = dr.find_similar("状态管理方案选择")
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DecisionRecord:
    """决策记录数据结构"""
    id: str = ""                           # D-001, D-002, ...
    phase: str = ""                        # 所处工作流阶段
    context: str = ""                      # 决策背景/问题描述
    options: list[str] = field(default_factory=list)   # 可选方案
    chosen: str = ""                       # 最终选择
    reason: str = ""                       # 选择理由
    outcome: str = ""                      # 结果 (可事后补填)
    knowledge_used: list[str] = field(default_factory=list)  # 参考的知识条目
    date: str = ""                         # ISO date
    keywords: list[str] = field(default_factory=list)  # 自动提取的关键词

    def __post_init__(self):
        if not self.date:
            self.date = datetime.date.today().isoformat()
        if not self.keywords:
            self.keywords = self._extract_keywords()

    def _extract_keywords(self) -> list[str]:
        """从 context + chosen + reason 中提取关键词"""
        text = f"{self.context} {self.chosen} {self.reason}".lower()
        # 移除常见停用词，提取有意义的词
        stopwords = {"的", "了", "在", "是", "和", "与", "或", "不", "要", "需要",
                     "the", "a", "an", "is", "are", "to", "for", "and", "or", "in"}
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)
        return [w for w in words if w not in stopwords and len(w) > 1]


class DecisionRecorder:
    """
    决策记录器。

    职责:
    1. 记录决策上下文、选项、理由
    2. 基于关键词重叠查找相似历史决策
    3. 持久化到 decision_log.md
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.log_file = self.base_dir / "evolution" / "decision_log.md"
        self._ensure_log()

    def _ensure_log(self) -> None:
        """确保 decision_log.md 存在"""
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text(
                "# Decision Log\n\n"
                "决策历史记录，用于回放和相似决策查找。\n\n"
                "---\n\n",
                encoding="utf-8",
            )

    # ── Public API ──

    def record(
        self,
        phase: str,
        context: str,
        options: list[str] | None = None,
        chosen: str = "",
        reason: str = "",
        outcome: str = "",
        knowledge_used: list[str] | None = None,
    ) -> DecisionRecord:
        """
        记录一次决策。

        Parameters
        ----------
        phase : str
            工作流阶段 (drafting, reviewing, decomposing, implementing)
        context : str
            决策背景/问题描述
        options : list[str]
            可选方案列表
        chosen : str
            最终选择
        reason : str
            选择理由
        outcome : str
            结果 (可事后补填)
        knowledge_used : list[str]
            参考的知识条目 ID 列表

        Returns
        -------
        DecisionRecord
        """
        did = self._next_id()
        record = DecisionRecord(
            id=did,
            phase=phase,
            context=context,
            options=options or [],
            chosen=chosen,
            reason=reason,
            outcome=outcome,
            knowledge_used=knowledge_used or [],
        )
        self._append_record(record)
        return record

    def find_similar(self, context: str, top_k: int = 5) -> list[dict]:
        """
        查找与给定上下文相似的历史决策。

        基于关键词重叠评分:
        similarity = |keywords_A ∩ keywords_B| / max(|keywords_A|, |keywords_B|)

        Parameters
        ----------
        context : str
            当前决策上下文
        top_k : int
            返回 top-k 个最相似的决策

        Returns
        -------
        list[dict]
            [{id, phase, context, chosen, reason, outcome, similarity}, ...]
        """
        query_keywords = set(self._extract_keywords(context))
        if not query_keywords:
            return []

        records = self._load_all_records()
        scored = []

        for rec in records:
            rec_keywords = set(rec.get("keywords", []))
            if not rec_keywords:
                continue
            overlap = len(query_keywords & rec_keywords)
            max_len = max(len(query_keywords), len(rec_keywords))
            similarity = overlap / max_len if max_len > 0 else 0.0

            if similarity > 0.0:
                scored.append({
                    "id": rec.get("id", ""),
                    "phase": rec.get("phase", ""),
                    "context": rec.get("context", ""),
                    "chosen": rec.get("chosen", ""),
                    "reason": rec.get("reason", ""),
                    "outcome": rec.get("outcome", ""),
                    "similarity": round(similarity, 3),
                })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def update_outcome(self, decision_id: str, outcome: str) -> bool:
        """
        事后更新决策的结果。

        Returns
        -------
        bool
            是否成功更新
        """
        if not self.log_file.exists():
            return False

        text = self.log_file.read_text(encoding="utf-8")
        marker = f"### {decision_id}"
        if marker not in text:
            return False

        # 查找并更新 outcome 行
        old_pattern = rf"(### {re.escape(decision_id)}.*?- \*\*Outcome\*\*: )(.*?)(\n)"
        new_text = re.sub(old_pattern, rf"\g<1>{outcome}\3", text, flags=re.DOTALL)

        if new_text != text:
            self.log_file.write_text(new_text, encoding="utf-8")
            return True
        return False

    # ── Private Methods ──

    def _next_id(self) -> str:
        """生成下一个决策 ID"""
        if not self.log_file.exists():
            return "D-001"

        text = self.log_file.read_text(encoding="utf-8")
        ids = re.findall(r"### (D-\d+)", text)
        if not ids:
            return "D-001"

        max_num = max(int(d.split("-")[1]) for d in ids)
        return f"D-{max_num + 1:03d}"

    def _append_record(self, record: DecisionRecord) -> None:
        """追加决策记录到 log 文件"""
        text = self.log_file.read_text(encoding="utf-8")
        entry = (
            f"### {record.id}\n"
            f"- **Date**: {record.date}\n"
            f"- **Phase**: {record.phase}\n"
            f"- **Context**: {record.context}\n"
            f"- **Options**: {', '.join(record.options)}\n"
            f"- **Chosen**: {record.chosen}\n"
            f"- **Reason**: {record.reason}\n"
            f"- **Outcome**: {record.outcome}\n"
            f"- **Knowledge Used**: {', '.join(record.knowledge_used)}\n"
            f"- **Keywords**: {', '.join(record.keywords)}\n"
            f"\n---\n\n"
        )
        text = text.rstrip() + "\n\n" + entry
        self.log_file.write_text(text, encoding="utf-8")

    def _load_all_records(self) -> list[dict]:
        """加载所有决策记录"""
        if not self.log_file.exists():
            return []

        text = self.log_file.read_text(encoding="utf-8")
        records = []
        blocks = re.split(r"### (D-\d+)", text)

        # blocks[0] is header, then alternating [id, content, id, content, ...]
        for i in range(1, len(blocks) - 1, 2):
            did = blocks[i]
            content = blocks[i + 1]
            rec = {"id": did}
            for field_name in ["Phase", "Context", "Options", "Chosen", "Reason", "Outcome", "Keywords"]:
                m = re.search(rf"\*\*{field_name}\*\*:\s*(.*?)(?:\n|$)", content)
                if m:
                    val = m.group(1).strip()
                    key = field_name.lower()
                    if key in ("options", "keywords"):
                        val = [v.strip() for v in val.split(",") if v.strip()]
                    rec[key] = val
            records.append(rec)

        return records

    @staticmethod
    def _extract_keywords(text: str) -> list[str]:
        """从文本中提取关键词"""
        text_lower = text.lower()
        stopwords = {"的", "了", "在", "是", "和", "与", "或", "不", "要", "需要",
                     "the", "a", "an", "is", "are", "to", "for", "and", "or", "in"}
        words = re.findall(r'[\w\u4e00-\u9fff]+', text_lower)
        return [w for w in words if w not in stopwords and len(w) > 1]
