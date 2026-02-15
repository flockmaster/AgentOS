"""
Meta Learner — 元学习器

系统学习"如何更好地学习":
  - 分析哪种知识最有价值
  - 优化收割策略
  - 发现知识盲区
  - 动态调优进化引擎参数

Usage:
    from evolution.meta_learner import MetaLearner
    ml = MetaLearner(base_dir=".agent/memory")
    value_report = ml.analyze_knowledge_value()
    strategy = ml.optimize_harvest_strategy()
    gaps = ml.detect_knowledge_gaps()
"""

from __future__ import annotations

import datetime
import re
from collections import Counter
from pathlib import Path
from typing import Optional

from evolution.harvester import KnowledgeHarvester
from evolution.causal_metrics import CausalMetrics
from evolution.confidence import ConfidenceEngine


class MetaLearner:
    """
    元学习引擎。

    职责:
    1. 分析知识价值分布
    2. 优化收割策略
    3. 发现知识盲区
    4. 动态调优进化引擎参数
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.harvester = KnowledgeHarvester(base_dir)
        self.causal_metrics = CausalMetrics(base_dir)
        self.confidence_engine = ConfidenceEngine(base_dir)
        self.insights_file = self.base_dir / "evolution" / "meta_insights.md"
        self.config_file = self.base_dir / "evolution" / "evolution_config.md"

    # ── Public API ──

    def analyze_knowledge_value(self) -> dict:
        """
        分析知识价值分布。

        Returns
        -------
        dict
            {
                "total_entries": int,
                "by_category": dict,       # {category: {count, avg_confidence, avg_causal}}
                "most_valuable": list,     # top-5 highest composite score
                "least_valuable": list,    # bottom-5
                "never_applied": list,     # 从未被应用的知识
                "high_decay_risk": list,   # 即将被废弃的知识
                "insights": list[str],     # 自动生成的洞察
            }
        """
        entries = self.harvester.list_entries()
        by_category = {}
        scored_entries = []
        never_applied = []
        high_decay = []

        for entry in entries:
            kid = entry.get("id", "")
            category = entry.get("category", "unknown")
            confidence = float(entry.get("confidence", 0.7))
            causal = self.causal_metrics.causal_score(kid)
            app_count = self.causal_metrics.get_application_count(kid)

            # 类别统计
            if category not in by_category:
                by_category[category] = {"count": 0, "total_confidence": 0.0, "total_causal": 0.0}
            by_category[category]["count"] += 1
            by_category[category]["total_confidence"] += confidence
            by_category[category]["total_causal"] += causal

            # composite score
            composite = causal * 0.4 + confidence * 0.6 if causal != 0.0 else confidence
            scored_entries.append({
                "id": kid,
                "title": entry.get("title", ""),
                "category": category,
                "confidence": confidence,
                "causal_score": causal,
                "composite_score": round(composite, 3),
                "application_count": app_count,
            })

            if app_count == 0:
                never_applied.append(kid)
            if confidence < 0.6:
                high_decay.append({"id": kid, "confidence": confidence})

        # 计算类别平均值
        for cat in by_category:
            count = by_category[cat]["count"]
            by_category[cat]["avg_confidence"] = round(by_category[cat]["total_confidence"] / count, 2) if count > 0 else 0.0
            by_category[cat]["avg_causal"] = round(by_category[cat]["total_causal"] / count, 2) if count > 0 else 0.0
            del by_category[cat]["total_confidence"]
            del by_category[cat]["total_causal"]

        # 排序
        scored_entries.sort(key=lambda x: x["composite_score"], reverse=True)
        most_valuable = scored_entries[:5]
        least_valuable = scored_entries[-5:] if len(scored_entries) >= 5 else scored_entries

        # 自动生成洞察
        insights = self._generate_insights(by_category, never_applied, high_decay, len(entries))

        return {
            "total_entries": len(entries),
            "by_category": by_category,
            "most_valuable": most_valuable,
            "least_valuable": least_valuable,
            "never_applied": never_applied,
            "high_decay_risk": high_decay,
            "insights": insights,
        }

    def optimize_harvest_strategy(self) -> dict:
        """
        基于知识价值分析，优化收割策略。

        Returns
        -------
        dict
            {
                "current_params": dict,
                "suggested_changes": list[dict],
                "rationale": list[str],
            }
        """
        value_analysis = self.analyze_knowledge_value()
        current_params = self._load_config()
        suggestions = []
        rationale = []

        by_category = value_analysis["by_category"]

        # 分析类别价值差异
        if by_category:
            categories_by_value = sorted(
                by_category.items(),
                key=lambda x: x[1].get("avg_causal", 0),
                reverse=True,
            )

            # 建议增加高价值类别的收割优先级
            if categories_by_value:
                top_cat = categories_by_value[0][0]
                top_val = categories_by_value[0][1]
                if top_val.get("avg_causal", 0) > 0.3:
                    suggestions.append({
                        "param": "harvest_priority",
                        "current": "equal",
                        "suggested": f"boost_{top_cat}",
                        "change": f"提高 {top_cat} 类别的收割优先级",
                    })
                    rationale.append(f"{top_cat} 类别平均因果评分最高 ({top_val.get('avg_causal', 0)})，建议优先收割")

        # 分析从未应用的知识比例
        never_applied_ratio = len(value_analysis["never_applied"]) / max(1, value_analysis["total_entries"])
        if never_applied_ratio > 0.5:
            suggestions.append({
                "param": "harvest_threshold",
                "current": "0.7",
                "suggested": "0.8",
                "change": "提高收割置信度阈值，减少低质量知识",
            })
            rationale.append(f"{never_applied_ratio:.0%} 的知识从未被应用，建议提高收割门槛")

        # 分析高衰减风险
        high_decay_ratio = len(value_analysis["high_decay_risk"]) / max(1, value_analysis["total_entries"])
        if high_decay_ratio > 0.3:
            suggestions.append({
                "param": "decay_rate",
                "current": "-0.1",
                "suggested": "-0.05",
                "change": "降低衰减速率，给知识更多应用机会",
            })
            rationale.append(f"{high_decay_ratio:.0%} 的知识面临高衰减风险，建议降低衰减速率")

        return {
            "current_params": current_params,
            "suggested_changes": suggestions,
            "rationale": rationale,
        }

    def detect_knowledge_gaps(self) -> list[dict]:
        """
        检测知识盲区。

        分析工作流中哪些阶段/类别缺乏知识支持。

        Returns
        -------
        list[dict]
            [{
                "area": str,
                "gap_type": str,          # missing | insufficient | outdated
                "severity": str,          # high | medium | low
                "suggestion": str,
            }, ...]
        """
        entries = self.harvester.list_entries()
        category_counts = Counter()
        for entry in entries:
            category_counts[entry.get("category", "unknown")] += 1

        gaps = []

        # 检查必要类别是否有足够知识
        required_categories = {
            "architecture": 5,
            "debugging": 3,
            "pattern": 3,
            "workflow": 2,
            "tooling": 2,
        }

        for cat, min_count in required_categories.items():
            actual = category_counts.get(cat, 0)
            if actual == 0:
                gaps.append({
                    "area": cat,
                    "gap_type": "missing",
                    "severity": "high",
                    "suggestion": f"缺少 {cat} 类别的知识条目，建议通过实践积累或从参考项目学习",
                })
            elif actual < min_count:
                gaps.append({
                    "area": cat,
                    "gap_type": "insufficient",
                    "severity": "medium",
                    "suggestion": f"{cat} 类别仅有 {actual} 条 (建议 >= {min_count})，建议积累更多",
                })

        # 检查是否有参考项目知识
        if category_counts.get("reference-project", 0) == 0:
            gaps.append({
                "area": "reference-project",
                "gap_type": "missing",
                "severity": "medium",
                "suggestion": "未学习过参考项目，建议执行 /learn-project 学习优秀项目的规范",
            })

        # 检查反知识覆盖
        anti = self.causal_metrics.get_anti_knowledge()
        if len(anti) > 0 and category_counts.get("anti-pattern", 0) == 0:
            gaps.append({
                "area": "anti-pattern",
                "gap_type": "missing",
                "severity": "high",
                "suggestion": f"检测到 {len(anti)} 个反知识但未有正式记录，建议运行 /evolve 生成反模式知识卡片",
            })

        # v2.2: 检查门禁偏离模式
        try:
            from evolution.gate_deviation_detector import GateDeviationDetector
            detector = GateDeviationDetector(self.base_dir)
            patterns = detector.analyze_patterns()
            pending = [p for p in patterns if p.get("has_pending_proposal")]
            if pending:
                gaps.append({
                    "area": "workflow-gates",
                    "gap_type": "insufficient",
                    "severity": "medium",
                    "suggestion": f"检测到 {len(pending)} 个门禁偏离模式待处理，"
                                  f"建议运行 /handle-deviation 更新工作流定义",
                })
        except ImportError:
            pass

        return gaps

    def evolve_evolution_rules(self) -> dict:
        """
        分析进化引擎的规则效果，建议调优。

        Returns
        -------
        dict
            {
                "analysis": dict,
                "rule_suggestions": list[dict],
                "requires_user_confirmation": bool,
            }
        """
        value = self.analyze_knowledge_value()
        gaps = self.detect_knowledge_gaps()
        strategy = self.optimize_harvest_strategy()

        rule_suggestions = []

        # 基于洞察生成规则建议
        for insight in value.get("insights", []):
            rule_suggestions.append({
                "type": "insight",
                "description": insight,
                "auto_apply": False,
            })

        for gap in gaps:
            if gap["severity"] == "high":
                rule_suggestions.append({
                    "type": "gap_fix",
                    "description": gap["suggestion"],
                    "auto_apply": False,
                })

        for change in strategy.get("suggested_changes", []):
            rule_suggestions.append({
                "type": "param_change",
                "description": f"{change['change']} ({change['param']}: {change['current']} → {change['suggested']})",
                "auto_apply": False,
            })

        # v2.2: 基于偏离模式的规则建议
        try:
            from evolution.gate_deviation_detector import GateDeviationDetector
            detector = GateDeviationDetector(self.base_dir)
            patterns = detector.analyze_patterns()
            high_freq = [p for p in patterns if p.get("total_deviations", 0) >= 3 and p.get("has_pending_proposal")]
            for p in high_freq:
                rule_suggestions.append({
                    "type": "workflow_gap",
                    "description": f"门禁 {p['gate_id']} 有 {p['total_deviations']} 次偏离 "
                                   f"(\"{p.get('top_intent', '')}\")，强烈建议添加到工作流",
                    "auto_apply": False,
                })
        except ImportError:
            pass

        return {
            "analysis": {
                "total_knowledge": value["total_entries"],
                "knowledge_gaps": len(gaps),
                "suggested_changes": len(strategy.get("suggested_changes", [])),
            },
            "rule_suggestions": rule_suggestions,
            "requires_user_confirmation": True,
        }

    def generate_meta_report(self) -> str:
        """
        生成元学习洞察报告。

        Returns
        -------
        str
            元学习报告 (Markdown)
        """
        value = self.analyze_knowledge_value()
        gaps = self.detect_knowledge_gaps()
        strategy = self.optimize_harvest_strategy()
        rules = self.evolve_evolution_rules()

        lines = [
            "# 🧠 元学习洞察报告",
            f"**Date**: {datetime.date.today().isoformat()}",
            "",
            "## 知识价值分析",
            f"- **总知识条目**: {value['total_entries']}",
            f"- **从未应用**: {len(value['never_applied'])} 条",
            f"- **高衰减风险**: {len(value['high_decay_risk'])} 条",
            "",
            "### 类别价值",
            "| Category | Count | Avg Confidence | Avg Causal |",
            "|----------|-------|----------------|-----------|",
        ]

        for cat, stats in value.get("by_category", {}).items():
            lines.append(f"| {cat} | {stats['count']} | {stats['avg_confidence']} | {stats['avg_causal']} |")

        if value.get("most_valuable"):
            lines += ["", "### 最有价值知识 (Top 5)"]
            for mv in value["most_valuable"]:
                lines.append(f"- **{mv['id']}**: {mv['title']} (composite: {mv['composite_score']})")

        lines += [
            "",
            f"## 知识盲区 ({len(gaps)} 项)",
        ]
        for gap in gaps:
            emoji = "🔴" if gap["severity"] == "high" else "🟡"
            lines.append(f"- {emoji} **{gap['area']}** [{gap['gap_type']}]: {gap['suggestion']}")

        lines += [
            "",
            "## 收割策略优化",
        ]
        for rationale in strategy.get("rationale", []):
            lines.append(f"- {rationale}")
        for change in strategy.get("suggested_changes", []):
            lines.append(f"- 建议: {change['change']}")

        lines += [
            "",
            "## 洞察",
        ]
        for insight in value.get("insights", []):
            lines.append(f"- 💡 {insight}")

        # v2.2: 门禁偏离分析
        try:
            from evolution.gate_deviation_detector import GateDeviationDetector
            detector = GateDeviationDetector(self.base_dir)
            patterns = detector.analyze_patterns()
            if patterns:
                total_deviations = sum(p.get("total_deviations", 0) for p in patterns)
                applied = sum(1 for p in patterns if p.get("applied_count", 0) > 0)
                pending = sum(1 for p in patterns if p.get("has_pending_proposal"))
                lines += [
                    "",
                    "## 门禁偏离分析",
                    f"- **已记录偏离**: {total_deviations} 次",
                    f"- **独立模式**: {len(patterns)} 个",
                    f"- **已应用修改**: {applied} 个",
                    f"- **待处理**: {pending} 个",
                ]
                for p in patterns:
                    status = "✅" if p.get("applied_count", 0) > 0 else "⏳"
                    lines.append(f"  - {status} **{p['gate_id']}**: \"{p.get('top_intent', '')}\" ({p['total_deviations']} times)")
        except ImportError:
            pass

        lines += [
            "",
            f"## 规则建议 ({len(rules.get('rule_suggestions', []))} 项)",
        ]
        for rs in rules.get("rule_suggestions", []):
            lines.append(f"- [{rs['type']}] {rs['description']}")

        lines += [
            "",
            "---",
            "*所有参数变更需用户确认后生效。*",
            "",
        ]

        # 持久化报告
        self._save_insights(lines)

        return "\n".join(lines)

    # ── Private Methods ──

    def _generate_insights(
        self,
        by_category: dict,
        never_applied: list,
        high_decay: list,
        total: int,
    ) -> list[str]:
        """生成自动洞察"""
        insights = []

        if total == 0:
            insights.append("知识库为空，建议开始积累知识条目")
            return insights

        # 类别不均衡
        if by_category:
            counts = [v["count"] for v in by_category.values()]
            if max(counts) > min(counts) * 3:
                max_cat = max(by_category, key=lambda c: by_category[c]["count"])
                min_cat = min(by_category, key=lambda c: by_category[c]["count"])
                insights.append(f"知识类别不均衡: {max_cat} ({by_category[max_cat]['count']}) vs {min_cat} ({by_category[min_cat]['count']})")

        # 未应用率
        if total > 10 and len(never_applied) > total * 0.5:
            insights.append(f"{len(never_applied)}/{total} 条知识从未被应用，知识注入可能不够主动")

        # 高衰减
        if len(high_decay) > total * 0.3:
            insights.append(f"{len(high_decay)} 条知识面临衰减风险，建议主动验证和应用")

        return insights

    def _load_config(self) -> dict:
        """加载进化引擎配置"""
        if not self.config_file.exists():
            return {
                "decay_rate": -0.1,
                "harvest_threshold": 0.7,
                "injection_top_k": 5,
                "archive_days": 90,
            }

        text = self.config_file.read_text(encoding="utf-8")
        config = {}
        for line in text.split("\n"):
            m = re.match(r'\|\s*(\w+)\s*\|\s*([^\|]+)\s*\|', line)
            if m and m.group(1) not in ("Parameter", "---"):
                key = m.group(1).strip()
                val = m.group(2).strip()
                config[key] = val
        return config or {
            "decay_rate": -0.1,
            "harvest_threshold": 0.7,
            "injection_top_k": 5,
            "archive_days": 90,
        }

    def _save_insights(self, lines: list[str]) -> None:
        """保存元学习洞察"""
        self.insights_file.parent.mkdir(parents=True, exist_ok=True)
        self.insights_file.write_text("\n".join(lines), encoding="utf-8")
