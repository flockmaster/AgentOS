"""
Workflow Optimizer — 工作流优化器

自动检测工作流瓶颈并生成调优建议:
  - 基于历史指标检测瓶颈阶段
  - 建议门禁调优 (阈值、重试策略)
  - 生成模板改进建议

Usage:
    from evolution.workflow_optimizer import WorkflowOptimizer
    wo = WorkflowOptimizer(base_dir=".agent/memory")
    bottlenecks = wo.detect_bottlenecks()
    suggestions = wo.suggest_gate_tuning()
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from evolution.metrics import WorkflowMetrics


class WorkflowOptimizer:
    """
    工作流优化器。

    职责:
    1. 检测工作流瓶颈
    2. 建议门禁调优
    3. 生成模板改进建议
    """

    # 优化阈值
    DURATION_THRESHOLD = 30       # 平均耗时 > 30 min 视为可优化
    SUCCESS_THRESHOLD = 0.8       # 成功率 < 80% 视为需要关注
    REWORK_THRESHOLD = 2          # 返工次数 > 2 视为瓶颈
    GATE_PASS_THRESHOLD = 0.7     # 门禁首次通过率 < 70% 视为门禁过严

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.metrics = WorkflowMetrics(base_dir)

    # ── Public API ──

    def detect_bottlenecks(self) -> list[dict]:
        """
        检测工作流瓶颈。

        分析所有工作流的历史指标，找出:
        - 耗时过长的工作流
        - 成功率过低的工作流
        - 返工率过高的阶段

        Returns
        -------
        list[dict]
            [{
                "workflow": str,
                "bottleneck_type": str,  # duration | success_rate | rework
                "severity": str,         # high | medium | low
                "current_value": float,
                "threshold": float,
                "suggestion": str,
            }, ...]
        """
        bottlenecks = []
        all_insights = self.metrics.get_all_insights()

        for wf, insight in all_insights.items():
            if insight.total_runs == 0:
                continue

            # 耗时瓶颈
            if insight.avg_duration > self.DURATION_THRESHOLD:
                severity = "high" if insight.avg_duration > self.DURATION_THRESHOLD * 2 else "medium"
                bottlenecks.append({
                    "workflow": wf,
                    "bottleneck_type": "duration",
                    "severity": severity,
                    "current_value": insight.avg_duration,
                    "threshold": self.DURATION_THRESHOLD,
                    "suggestion": f"工作流 {wf} 平均耗时 {insight.avg_duration:.0f}min，"
                                  f"考虑拆分为子工作流或引入并行执行",
                })

            # 成功率瓶颈
            if insight.success_rate < self.SUCCESS_THRESHOLD:
                severity = "high" if insight.success_rate < 0.5 else "medium"
                bottlenecks.append({
                    "workflow": wf,
                    "bottleneck_type": "success_rate",
                    "severity": severity,
                    "current_value": insight.success_rate,
                    "threshold": self.SUCCESS_THRESHOLD,
                    "suggestion": f"工作流 {wf} 成功率 {insight.success_rate:.0%}，"
                                  f"建议检查常见失败原因: {insight.common_bottleneck or 'N/A'}",
                })

            # 常见瓶颈阶段
            if insight.common_bottleneck:
                bottlenecks.append({
                    "workflow": wf,
                    "bottleneck_type": "phase_bottleneck",
                    "severity": "medium",
                    "current_value": 0,
                    "threshold": 0,
                    "suggestion": f"工作流 {wf} 最常见瓶颈: {insight.common_bottleneck}，"
                                  f"考虑优化该阶段或增加预检查",
                })

        return bottlenecks

    def suggest_gate_tuning(self) -> list[dict]:
        """
        建议门禁调优。

        基于历史数据分析门禁是否过严或过松:
        - 门禁首次通过率过低 → 建议放宽条件
        - 门禁从未拦截 → 建议收紧条件或移除

        Returns
        -------
        list[dict]
            [{
                "gate": str,
                "current_behavior": str,
                "suggestion": str,
                "priority": str,  # high | medium | low
            }, ...]
        """
        suggestions = []

        # 基于工作流洞察推断门禁表现
        all_insights = self.metrics.get_all_insights()
        for wf, insight in all_insights.items():
            if insight.total_runs < 3:
                continue

            # 成功率极低可能暗示门禁不足
            if insight.success_rate < 0.5:
                suggestions.append({
                    "gate": f"{wf} - 前置门禁",
                    "current_behavior": f"成功率 {insight.success_rate:.0%}",
                    "suggestion": "考虑增加前置检查门禁，在工作流开始前验证前置条件",
                    "priority": "high",
                })

            # 成功率极高可能暗示门禁过多
            if insight.success_rate > 0.95 and insight.total_runs >= 10:
                suggestions.append({
                    "gate": f"{wf} - 现有门禁",
                    "current_behavior": f"成功率 {insight.success_rate:.0%} (>95%)",
                    "suggestion": "门禁可能过于宽松或已无价值，考虑简化工作流",
                    "priority": "low",
                })

        return suggestions

    def suggest_deviation_based_tuning(self, deviation_patterns: list[dict]) -> list[dict]:
        """
        基于门禁偏离数据生成门禁调优建议。

        Parameters
        ----------
        deviation_patterns : list[dict]
            来自 GateDeviationDetector.analyze_patterns() 的偏离模式

        Returns
        -------
        list[dict]
            门禁调优建议
        """
        suggestions = []
        for pattern in deviation_patterns:
            total = pattern.get("total_deviations", 0)
            if total >= 2:
                priority = "high" if total >= 5 else "medium"
                suggestions.append({
                    "gate": pattern.get("gate_id", ""),
                    "current_behavior": f"{len(pattern.get('unique_intents', []))} 种偏离意图",
                    "suggestion": f"门禁 {pattern.get('gate_id', '')} 有 {total} 次偏离 "
                                  f"(\"{pattern.get('top_intent', '')}\")，建议添加为正式路径",
                    "priority": priority,
                })
        return suggestions

    def generate_template_improvements(self) -> list[dict]:
        """
        生成工作流模板改进建议。

        Returns
        -------
        list[dict]
            [{
                "workflow": str,
                "improvement_type": str,
                "description": str,
                "estimated_impact": str,
            }, ...]
        """
        improvements = []
        bottlenecks = self.detect_bottlenecks()

        for bn in bottlenecks:
            if bn["bottleneck_type"] == "duration" and bn["severity"] == "high":
                improvements.append({
                    "workflow": bn["workflow"],
                    "improvement_type": "parallel_execution",
                    "description": f"将 {bn['workflow']} 中的独立步骤改为并行执行",
                    "estimated_impact": "预计减少 30-50% 耗时",
                })

            if bn["bottleneck_type"] == "success_rate":
                improvements.append({
                    "workflow": bn["workflow"],
                    "improvement_type": "pre_validation",
                    "description": f"在 {bn['workflow']} 开始前增加输入验证步骤",
                    "estimated_impact": "预计提升成功率 10-20%",
                })

        return improvements

    def format_report(self) -> str:
        """生成优化报告"""
        bottlenecks = self.detect_bottlenecks()
        gate_suggestions = self.suggest_gate_tuning()
        improvements = self.generate_template_improvements()

        lines = [
            "# 🔧 工作流优化报告",
            "",
            f"## 瓶颈检测 ({len(bottlenecks)} 项)",
        ]

        if bottlenecks:
            for bn in bottlenecks:
                emoji = "🔴" if bn["severity"] == "high" else "🟡" if bn["severity"] == "medium" else "🟢"
                lines.append(f"- {emoji} **{bn['workflow']}** [{bn['bottleneck_type']}]: {bn['suggestion']}")
        else:
            lines.append("- 未检测到显著瓶颈")

        lines += [
            "",
            f"## 门禁调优建议 ({len(gate_suggestions)} 项)",
        ]
        for gs in gate_suggestions:
            lines.append(f"- **{gs['gate']}**: {gs['suggestion']} (优先级: {gs['priority']})")

        lines += [
            "",
            f"## 模板改进 ({len(improvements)} 项)",
        ]
        for imp in improvements:
            lines.append(f"- **{imp['workflow']}** [{imp['improvement_type']}]: {imp['description']} ({imp['estimated_impact']})")

        lines.append("")
        return "\n".join(lines)
