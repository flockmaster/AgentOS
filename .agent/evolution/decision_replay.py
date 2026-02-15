"""
Decision Replay — 决策回放

查找相似的历史决策并提供推荐:
  - 基于关键词重叠评分查找相似决策
  - 分析历史决策的成功/失败模式
  - 生成决策推荐

Usage:
    from evolution.decision_replay import DecisionReplay
    dr = DecisionReplay(base_dir=".agent/memory")
    recommendations = dr.recommend(context="需要选择数据库方案")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from evolution.decision_recorder import DecisionRecorder


class DecisionReplay:
    """
    决策回放引擎。

    职责:
    1. 查找与当前上下文相似的历史决策
    2. 分析历史决策的 outcome 模式
    3. 生成决策推荐
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.recorder = DecisionRecorder(base_dir)

    # ── Public API ──

    def find_similar_decisions(self, context: str, top_k: int = 5) -> list[dict]:
        """
        查找与当前上下文相似的历史决策。

        Parameters
        ----------
        context : str
            当前决策上下文
        top_k : int
            返回最相似的 N 个决策

        Returns
        -------
        list[dict]
            [{id, phase, context, chosen, reason, outcome, similarity}, ...]
        """
        return self.recorder.find_similar(context, top_k=top_k)

    def recommend(self, context: str, top_k: int = 3) -> dict:
        """
        基于历史决策生成推荐。

        分析相似决策的 outcome，生成:
        - 推荐选项 (基于成功的历史决策)
        - 避免选项 (基于失败的历史决策)
        - 相关知识引用

        Parameters
        ----------
        context : str
            当前决策上下文
        top_k : int
            参考的历史决策数量

        Returns
        -------
        dict
            {
                "similar_decisions": [...],
                "recommended_choices": [...],
                "avoid_choices": [...],
                "knowledge_refs": [...],
                "summary": str
            }
        """
        similar = self.find_similar_decisions(context, top_k=top_k)

        recommended = []
        avoid = []
        knowledge_refs = set()

        for dec in similar:
            outcome = dec.get("outcome", "")
            chosen = dec.get("chosen", "")
            reason = dec.get("reason", "")

            if not chosen:
                continue

            # 根据 outcome 分类
            outcome_lower = outcome.lower() if outcome else ""
            if any(w in outcome_lower for w in ["成功", "success", "good", "通过"]):
                recommended.append({
                    "choice": chosen,
                    "reason": reason,
                    "from_decision": dec.get("id", ""),
                    "similarity": dec.get("similarity", 0),
                })
            elif any(w in outcome_lower for w in ["失败", "failure", "fail", "问题", "bug"]):
                avoid.append({
                    "choice": chosen,
                    "reason": f"历史决策 {dec.get('id', '')} 选择此方案后: {outcome}",
                    "from_decision": dec.get("id", ""),
                })

        # 生成摘要
        if recommended:
            summary = f"基于 {len(similar)} 个相似历史决策，推荐: {recommended[0]['choice']}"
        elif avoid:
            summary = f"基于历史经验，建议避免: {avoid[0]['choice']}"
        elif similar:
            summary = f"找到 {len(similar)} 个相似决策可供参考，但无明确推荐"
        else:
            summary = "未找到相似的历史决策"

        return {
            "similar_decisions": similar,
            "recommended_choices": recommended,
            "avoid_choices": avoid,
            "knowledge_refs": list(knowledge_refs),
            "summary": summary,
        }

    def format_for_prompt(self, recommendation: dict) -> str:
        """
        格式化推荐结果为 Prompt 注入块。

        Parameters
        ----------
        recommendation : dict
            recommend() 返回的推荐结果

        Returns
        -------
        str
            格式化的 Prompt 块
        """
        lines = ["🔄 决策回放", ""]
        lines.append(f"**摘要**: {recommendation.get('summary', '无')}")
        lines.append("")

        rec = recommendation.get("recommended_choices", [])
        if rec:
            lines.append("**推荐选项**:")
            for r in rec[:3]:
                lines.append(f"  - ✅ {r['choice']} (来自 {r['from_decision']}, 相似度 {r.get('similarity', 0):.0%})")

        avoid = recommendation.get("avoid_choices", [])
        if avoid:
            lines.append("**避免选项**:")
            for a in avoid[:3]:
                lines.append(f"  - ❌ {a['choice']} — {a['reason']}")

        similar = recommendation.get("similar_decisions", [])
        if similar and not rec and not avoid:
            lines.append("**相关历史决策**:")
            for s in similar[:3]:
                lines.append(f"  - {s.get('id', '')}: {s.get('context', '')[:50]}... → {s.get('chosen', '')}")

        lines.append("")
        return "\n".join(lines)
