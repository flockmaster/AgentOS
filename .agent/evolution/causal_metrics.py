"""
Causal Metrics — 因果度量模块

追踪知识应用的实际结果，计算因果评分：
  - 记录每次知识应用的 outcome (成功/失败/节省时间/引入 bug)
  - 计算因果评分 causal_score = success_rate * 0.5 + time_saved_norm * 0.3 - bugs_penalty * 0.2
  - 识别反知识 (anti-knowledge): 应用后反而导致问题的知识

Usage:
    from evolution.causal_metrics import CausalMetrics
    cm = CausalMetrics(base_dir=".agent/memory")
    cm.record_outcome("k-001", task="T-201", result="success", time_saved=15)
    score = cm.causal_score("k-001")
"""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class OutcomeRecord:
    """知识应用结果记录"""
    knowledge_id: str              # 关联的知识条目 ID (k-xxx)
    task: str = ""                 # 关联任务 ID (T-xxx)
    result: str = "success"        # success | failure | partial
    time_saved: int = 0            # 估计节省的分钟数 (可为负)
    bugs_introduced: int = 0       # 引入的 bug 数
    date: str = ""                 # ISO date
    notes: str = ""

    def __post_init__(self):
        if not self.date:
            self.date = datetime.date.today().isoformat()


@dataclass
class CausalMetrics:
    """
    因果度量引擎。

    职责:
    1. 记录知识应用的实际结果 (OutcomeRecord)
    2. 计算因果评分 (causal_score)
    3. 识别反知识 (anti-knowledge)
    4. 持久化到 outcome_tracker.md
    """

    base_dir: str | Path = ".agent/memory"

    def __post_init__(self):
        self.base_dir = Path(self.base_dir)
        self.tracker_file = self.base_dir / "evolution" / "outcome_tracker.md"
        self._ensure_tracker()

    def _ensure_tracker(self) -> None:
        """确保 outcome_tracker.md 存在"""
        if not self.tracker_file.exists():
            self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
            self.tracker_file.write_text(
                "# Outcome Tracker\n\n"
                "## Records\n\n"
                "| Date | Knowledge ID | Task | Result | Time Saved | Bugs | Notes |\n"
                "|------|-------------|------|--------|------------|------|-------|\n",
                encoding="utf-8",
            )

    # ── Public API ──

    def record_outcome(
        self,
        knowledge_id: str,
        task: str = "",
        result: str = "success",
        time_saved: int = 0,
        bugs_introduced: int = 0,
        notes: str = "",
    ) -> OutcomeRecord:
        """
        记录一次知识应用的结果。

        Parameters
        ----------
        knowledge_id : str
            知识条目 ID (k-xxx)
        task : str
            关联任务 ID
        result : str
            结果: success | failure | partial
        time_saved : int
            估计节省分钟数 (可为负表示浪费时间)
        bugs_introduced : int
            引入的 bug 数
        notes : str
            备注

        Returns
        -------
        OutcomeRecord
        """
        record = OutcomeRecord(
            knowledge_id=knowledge_id,
            task=task,
            result=result,
            time_saved=time_saved,
            bugs_introduced=bugs_introduced,
            notes=notes,
        )
        self._append_record(record)
        return record

    def causal_score(self, knowledge_id: str) -> float:
        """
        计算知识条目的因果评分。

        公式: success_rate * 0.5 + time_saved_norm * 0.3 - bugs_penalty * 0.2

        - success_rate: 成功次数 / 总应用次数
        - time_saved_norm: 平均节省时间归一化到 [0, 1] (以 60 min 为满分)
        - bugs_penalty: 平均 bug 数归一化到 [0, 1] (以 3 个为满分)

        Returns
        -------
        float
            因果评分 [-0.2, 1.0]，application_count < 5 时返回 0.0 (数据不足)
        """
        records = self._load_records(knowledge_id)
        if len(records) < 5:
            return 0.0

        total = len(records)
        successes = sum(1 for r in records if r["result"] == "success")
        success_rate = successes / total

        avg_time_saved = sum(r.get("time_saved", 0) for r in records) / total
        time_saved_norm = min(1.0, max(0.0, avg_time_saved / 60.0))

        avg_bugs = sum(r.get("bugs", 0) for r in records) / total
        bugs_penalty = min(1.0, avg_bugs / 3.0)

        score = success_rate * 0.5 + time_saved_norm * 0.3 - bugs_penalty * 0.2
        return round(score, 3)

    def get_anti_knowledge(self, threshold: float = -0.05) -> list[str]:
        """
        识别反知识: 因果评分低于阈值的知识条目。

        Returns
        -------
        list[str]
            反知识的 knowledge_id 列表
        """
        all_kids = self._get_all_knowledge_ids()
        anti = []
        for kid in all_kids:
            score = self.causal_score(kid)
            if score != 0.0 and score < threshold:
                anti.append(kid)
        return anti

    def get_outcomes(self, knowledge_id: str) -> list[dict]:
        """获取指定知识的所有应用结果"""
        return self._load_records(knowledge_id)

    def get_application_count(self, knowledge_id: str) -> int:
        """获取知识应用次数"""
        return len(self._load_records(knowledge_id))

    # ── Private Methods ──

    def _append_record(self, record: OutcomeRecord) -> None:
        """追加记录到 outcome_tracker.md"""
        text = self.tracker_file.read_text(encoding="utf-8")
        row = (
            f"| {record.date} | {record.knowledge_id} | {record.task} "
            f"| {record.result} | {record.time_saved} | {record.bugs_introduced} "
            f"| {record.notes} |"
        )
        text = text.rstrip() + "\n" + row + "\n"
        self.tracker_file.write_text(text, encoding="utf-8")

    def _load_records(self, knowledge_id: str) -> list[dict]:
        """从 outcome_tracker.md 加载指定知识的所有记录"""
        if not self.tracker_file.exists():
            return []

        text = self.tracker_file.read_text(encoding="utf-8")
        records = []
        in_table = False

        for line in text.split("\n"):
            if "| Date |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7 and parts[2] == knowledge_id:
                    try:
                        time_saved = int(parts[5]) if parts[5].lstrip("-").isdigit() else 0
                    except (ValueError, IndexError):
                        time_saved = 0
                    try:
                        bugs = int(parts[6]) if parts[6].isdigit() else 0
                    except (ValueError, IndexError):
                        bugs = 0
                    records.append({
                        "date": parts[1],
                        "knowledge_id": parts[2],
                        "task": parts[3],
                        "result": parts[4],
                        "time_saved": time_saved,
                        "bugs": bugs,
                        "notes": parts[7] if len(parts) > 7 else "",
                    })
            elif in_table and not line.startswith("|"):
                break

        return records

    def _get_all_knowledge_ids(self) -> set[str]:
        """获取所有有记录的知识 ID"""
        if not self.tracker_file.exists():
            return set()

        text = self.tracker_file.read_text(encoding="utf-8")
        kids = set()
        in_table = False

        for line in text.split("\n"):
            if "| Date |" in line:
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[2].startswith("k-"):
                    kids.add(parts[2])
            elif in_table and not line.startswith("|"):
                break

        return kids
