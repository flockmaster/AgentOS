"""
Pattern Scaffolder — 模式脚手架

从模式库生成代码脚手架:
  - 根据模式 ID 和参数生成代码模板
  - 基于功能描述推荐匹配模式并生成脚手架

Usage:
    from evolution.pattern_scaffolder import PatternScaffolder
    ps = PatternScaffolder(base_dir=".agent/memory")
    code = ps.scaffold_from_pattern("P-001", params={"name": "UserRepository"})
    suggestions = ps.suggest_and_scaffold("需要一个用户数据仓库")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from evolution.pattern_detector import PatternDetector


class PatternScaffolder:
    """
    模式脚手架生成器。

    职责:
    1. 根据模式 ID 和参数生成代码模板
    2. 基于功能描述推荐匹配模式
    3. 生成可直接使用的代码脚手架
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.pattern_detector = PatternDetector(base_dir)

    # ── Public API ──

    def scaffold_from_pattern(
        self,
        pattern_id: str,
        params: dict | None = None,
    ) -> dict:
        """
        从模式库中的模式生成代码脚手架。

        Parameters
        ----------
        pattern_id : str
            模式 ID (P-xxx)
        params : dict
            模板参数 (e.g. {"name": "UserRepository", "entity": "User"})

        Returns
        -------
        dict
            {
                "pattern_id": str,
                "pattern_name": str,
                "scaffold": str,     # 生成的代码
                "instructions": str,  # 使用说明
                "files_to_create": list[str]
            }
        """
        params = params or {}
        patterns = self.pattern_detector.load_patterns()
        pattern = None

        for p in patterns:
            if p.get("id") == pattern_id:
                pattern = p
                break

        if not pattern:
            return {
                "pattern_id": pattern_id,
                "pattern_name": "未找到",
                "scaffold": "",
                "instructions": f"模式 {pattern_id} 不存在于模式库中",
                "files_to_create": [],
            }

        template = pattern.get("template", "")
        name = pattern.get("name", "Unknown Pattern")

        # 替换模板参数
        scaffold = template
        for key, val in params.items():
            scaffold = scaffold.replace(f"{{{{{key}}}}}", val)
            scaffold = scaffold.replace(f"${{{key}}}", val)

        instructions = (
            f"模式: {name} ({pattern_id})\n"
            f"类别: {pattern.get('category', 'N/A')}\n"
            f"描述: {pattern.get('description', 'N/A')}\n"
            f"使用次数: {pattern.get('occurrences', 0)}\n"
        )

        return {
            "pattern_id": pattern_id,
            "pattern_name": name,
            "scaffold": scaffold,
            "instructions": instructions,
            "files_to_create": [],
        }

    def suggest_and_scaffold(
        self,
        description: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        基于功能描述推荐匹配模式并生成脚手架。

        Parameters
        ----------
        description : str
            功能描述
        top_k : int
            返回推荐数量

        Returns
        -------
        list[dict]
            [{pattern_id, pattern_name, confidence, scaffold, instructions}, ...]
        """
        suggestions = self.pattern_detector.suggest_reuse(description)

        results = []
        for match in suggestions[:top_k]:
            pid = match.get("pattern_id", "")
            result = self.scaffold_from_pattern(pid)
            result["match_confidence"] = match.get("confidence", 0.0)
            results.append(result)

        return results

    def format_for_prompt(self, suggestions: list[dict]) -> str:
        """
        格式化模式脚手架建议为 Prompt 注入块。

        Parameters
        ----------
        suggestions : list[dict]
            suggest_and_scaffold() 返回的建议列表

        Returns
        -------
        str
            格式化的 Prompt 块
        """
        if not suggestions:
            return ""

        lines = ["🏗️ 模式脚手架建议", ""]

        for i, sug in enumerate(suggestions, 1):
            pid = sug.get("pattern_id", "")
            name = sug.get("pattern_name", "")
            conf = sug.get("match_confidence", 0.0)
            instructions = sug.get("instructions", "")

            lines.append(f"**{i}. [{pid}] {name}** (匹配度: {conf:.0%})")
            if instructions:
                for inst_line in instructions.split("\n"):
                    if inst_line.strip():
                        lines.append(f"   {inst_line}")
            lines.append("")

        return "\n".join(lines)
