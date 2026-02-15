"""
Decision Graph — 决策图 (跨会话因果推理)

构建决策因果链图谱，支持:
  - 跨会话因果推理
  - 后悔分析 (regret analysis)
  - 决策路径查找

Usage:
    from evolution.decision_graph import DecisionGraph
    dg = DecisionGraph(base_dir=".agent/memory")
    dg.add_node(decision_id="D-001", ...)
    paths = dg.find_similar_paths(context)
    prediction = dg.predict_outcome(context)
"""

from __future__ import annotations

import json
import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class DecisionNode:
    """决策图节点"""
    id: str                                 # 决策 ID (D-xxx)
    context: str = ""                       # 决策上下文
    chosen: str = ""                        # 选择
    outcome: str = ""                       # 结果
    outcome_score: float = 0.0              # 结果评分 (-1.0 ~ 1.0)
    phase: str = ""                         # 工作流阶段
    date: str = ""                          # ISO date
    causes: list[str] = field(default_factory=list)     # 前因节点 ID
    effects: list[str] = field(default_factory=list)    # 后果节点 ID
    knowledge_used: list[str] = field(default_factory=list)  # 使用的知识
    tags: list[str] = field(default_factory=list)       # 标签

    def __post_init__(self):
        if not self.date:
            self.date = datetime.date.today().isoformat()


class DecisionGraph:
    """
    决策图引擎。

    职责:
    1. 构建决策因果链图谱
    2. 查找相似决策路径
    3. 预测决策结果
    4. 后悔分析
    5. 自动归档过期节点
    """

    ARCHIVE_DAYS = 90  # 90 天无因果链节点自动归档

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.graph_file = self.base_dir / "evolution" / "decision_graph.json"
        self._ensure_graph()

    def _ensure_graph(self) -> None:
        """确保 decision_graph.json 存在"""
        if not self.graph_file.exists():
            self.graph_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_graph({"nodes": {}, "metadata": {
                "created": datetime.date.today().isoformat(),
                "version": "2.0",
                "total_nodes": 0,
                "last_updated": datetime.date.today().isoformat(),
            }})

    # ── Public API ──

    def add_node(
        self,
        decision_id: str,
        context: str = "",
        chosen: str = "",
        outcome: str = "",
        outcome_score: float = 0.0,
        phase: str = "",
        causes: list[str] | None = None,
        effects: list[str] | None = None,
        knowledge_used: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> DecisionNode:
        """
        添加决策节点到图谱。

        Parameters
        ----------
        decision_id : str
            决策 ID
        context : str
            决策上下文
        chosen : str
            选择
        outcome : str
            结果
        outcome_score : float
            结果评分 (-1.0 ~ 1.0)
        phase : str
            工作流阶段
        causes : list[str]
            前因节点 ID 列表
        effects : list[str]
            后果节点 ID 列表

        Returns
        -------
        DecisionNode
        """
        node = DecisionNode(
            id=decision_id,
            context=context,
            chosen=chosen,
            outcome=outcome,
            outcome_score=outcome_score,
            phase=phase,
            causes=causes or [],
            effects=effects or [],
            knowledge_used=knowledge_used or [],
            tags=tags or [],
        )

        graph = self._load_graph()
        graph["nodes"][decision_id] = asdict(node)

        # 更新因果关系 (双向链接)
        for cause_id in node.causes:
            if cause_id in graph["nodes"]:
                effects_list = graph["nodes"][cause_id].get("effects", [])
                if decision_id not in effects_list:
                    effects_list.append(decision_id)
                    graph["nodes"][cause_id]["effects"] = effects_list

        for effect_id in node.effects:
            if effect_id in graph["nodes"]:
                causes_list = graph["nodes"][effect_id].get("causes", [])
                if decision_id not in causes_list:
                    causes_list.append(decision_id)
                    graph["nodes"][effect_id]["causes"] = causes_list

        graph["metadata"]["total_nodes"] = len(graph["nodes"])
        graph["metadata"]["last_updated"] = datetime.date.today().isoformat()
        self._save_graph(graph)

        return node

    def find_similar_paths(self, context: str, top_k: int = 3) -> list[dict]:
        """
        查找与给定上下文相似的决策路径。

        Returns
        -------
        list[dict]
            [{
                "start_node": str,
                "path": list[str],   # 节点 ID 链
                "outcome_score": float,
                "similarity": float,
            }, ...]
        """
        graph = self._load_graph()
        context_words = set(self._tokenize(context))
        if not context_words:
            return []

        # 找到相似的起始节点
        scored_nodes = []
        for nid, node in graph["nodes"].items():
            node_words = set(self._tokenize(node.get("context", "") + " " + node.get("chosen", "")))
            if not node_words:
                continue
            overlap = len(context_words & node_words)
            max_len = max(len(context_words), len(node_words))
            similarity = overlap / max_len if max_len > 0 else 0.0
            if similarity > 0.0:
                scored_nodes.append((nid, similarity))

        scored_nodes.sort(key=lambda x: x[1], reverse=True)

        # 从每个相似节点追踪因果路径
        paths = []
        for nid, sim in scored_nodes[:top_k]:
            path = self._trace_path(graph, nid)
            if path:
                # 计算路径的平均 outcome_score
                scores = [graph["nodes"].get(p, {}).get("outcome_score", 0.0) for p in path]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                paths.append({
                    "start_node": nid,
                    "path": path,
                    "outcome_score": round(avg_score, 3),
                    "similarity": round(sim, 3),
                })

        return paths

    def predict_outcome(self, context: str) -> dict:
        """
        基于历史路径预测决策结果。

        Returns
        -------
        dict
            {
                "predicted_score": float,
                "confidence": float,
                "based_on": int,         # 参考路径数
                "similar_paths": list,
            }
        """
        paths = self.find_similar_paths(context)
        if not paths:
            return {
                "predicted_score": 0.0,
                "confidence": 0.0,
                "based_on": 0,
                "similar_paths": [],
            }

        # 加权平均 (相似度作为权重)
        total_weight = sum(p["similarity"] for p in paths)
        if total_weight > 0:
            predicted = sum(p["outcome_score"] * p["similarity"] for p in paths) / total_weight
        else:
            predicted = 0.0

        confidence = min(1.0, len(paths) / 5.0 * max(p["similarity"] for p in paths))

        return {
            "predicted_score": round(predicted, 3),
            "confidence": round(confidence, 3),
            "based_on": len(paths),
            "similar_paths": paths,
        }

    def regret_analysis(self, min_score: float = -0.3) -> list[dict]:
        """
        后悔分析: 找出 outcome_score 低于阈值的决策。

        Returns
        -------
        list[dict]
            [{
                "id": str,
                "context": str,
                "chosen": str,
                "outcome": str,
                "outcome_score": float,
                "effects": list,          # 受影响的后续决策
                "suggestion": str,
            }, ...]
        """
        graph = self._load_graph()
        regrets = []

        for nid, node in graph["nodes"].items():
            score = node.get("outcome_score", 0.0)
            if score < min_score:
                effects = node.get("effects", [])
                affected = []
                for eid in effects:
                    if eid in graph["nodes"]:
                        affected.append({
                            "id": eid,
                            "context": graph["nodes"][eid].get("context", "")[:50],
                        })

                regrets.append({
                    "id": nid,
                    "context": node.get("context", ""),
                    "chosen": node.get("chosen", ""),
                    "outcome": node.get("outcome", ""),
                    "outcome_score": score,
                    "date": node.get("date", ""),
                    "effects": affected,
                    "suggestion": f"决策 {nid} 评分 {score}，考虑标记为反知识或记录教训",
                })

        regrets.sort(key=lambda x: x["outcome_score"])
        return regrets

    def archive_stale_nodes(self) -> int:
        """
        归档过期节点 (90 天无因果链)。

        Returns
        -------
        int
            归档的节点数
        """
        graph = self._load_graph()
        cutoff = (datetime.date.today() - datetime.timedelta(days=self.ARCHIVE_DAYS)).isoformat()
        to_archive = []

        for nid, node in graph["nodes"].items():
            node_date = node.get("date", "")
            if node_date and node_date < cutoff:
                # 无因果链的孤立节点
                if not node.get("causes") and not node.get("effects"):
                    to_archive.append(nid)

        for nid in to_archive:
            del graph["nodes"][nid]

        if to_archive:
            graph["metadata"]["total_nodes"] = len(graph["nodes"])
            graph["metadata"]["last_updated"] = datetime.date.today().isoformat()
            self._save_graph(graph)

        return len(to_archive)

    def get_stats(self) -> dict:
        """获取图谱统计"""
        graph = self._load_graph()
        nodes = graph.get("nodes", {})
        return {
            "total_nodes": len(nodes),
            "nodes_with_causes": sum(1 for n in nodes.values() if n.get("causes")),
            "nodes_with_effects": sum(1 for n in nodes.values() if n.get("effects")),
            "avg_outcome_score": (
                sum(n.get("outcome_score", 0) for n in nodes.values()) / len(nodes)
                if nodes else 0.0
            ),
            "negative_outcomes": sum(1 for n in nodes.values() if n.get("outcome_score", 0) < 0),
        }

    # ── Private Methods ──

    def _load_graph(self) -> dict:
        """加载决策图"""
        try:
            text = self.graph_file.read_text(encoding="utf-8")
            return json.loads(text)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"nodes": {}, "metadata": {}}

    def _save_graph(self, graph: dict) -> None:
        """保存决策图"""
        self.graph_file.write_text(
            json.dumps(graph, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _trace_path(self, graph: dict, start_id: str, max_depth: int = 5) -> list[str]:
        """从起始节点追踪因果路径"""
        path = [start_id]
        current = start_id
        visited = {start_id}

        for _ in range(max_depth):
            node = graph["nodes"].get(current)
            if not node:
                break
            effects = node.get("effects", [])
            # 选择第一个未访问的 effect
            next_node = None
            for eid in effects:
                if eid not in visited and eid in graph["nodes"]:
                    next_node = eid
                    break
            if next_node is None:
                break
            path.append(next_node)
            visited.add(next_node)
            current = next_node

        return path

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """简单分词"""
        import re
        text_lower = text.lower()
        words = re.findall(r'[\w\u4e00-\u9fff]+', text_lower)
        stopwords = {"的", "了", "在", "是", "和", "与", "或", "不", "要",
                     "the", "a", "an", "is", "are", "to", "for", "and", "or", "in"}
        return [w for w in words if w not in stopwords and len(w) > 1]
