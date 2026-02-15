"""
Evolution Orchestrator — 进化协调器

整合所有进化引擎模块，提供统一入口：
  - /evolve: 完整进化周期
  - /reflect: 反思工作流
  - /knowledge: 知识查询
  - /patterns: 模式查询

Usage:
    from evolution.orchestrator import EvolutionOrchestrator
    evo = EvolutionOrchestrator(base_dir=".agent/memory")
    report = evo.evolve()         # 完整进化
    evo.reflect(session_name=...) # 反思
"""

from __future__ import annotations

import datetime
from pathlib import Path

from evolution.harvester import KnowledgeHarvester
from evolution.index_manager import KnowledgeIndexManager
from evolution.confidence import ConfidenceEngine
from evolution.reflection import ReflectionEngine
from evolution.pattern_detector import PatternDetector
from evolution.learning_queue import LearningQueue
from evolution.metrics import WorkflowMetrics
from evolution.causal_metrics import CausalMetrics
from evolution.decision_recorder import DecisionRecorder
from evolution.knowledge_injector import KnowledgeInjector
from evolution.decision_replay import DecisionReplay
from evolution.pattern_scaffolder import PatternScaffolder
from evolution.project_scanner import ProjectScanner
from evolution.convention_extractor import ConventionExtractor
from evolution.workflow_optimizer import WorkflowOptimizer
from evolution.decision_graph import DecisionGraph
from evolution.meta_learner import MetaLearner
from evolution.dependency_analyzer import DependencyAnalyzer
from evolution.gate_deviation_detector import GateDeviationDetector


class EvolutionOrchestrator:
    """
    进化引擎总控制器。

    整合模块:
    1. Knowledge Harvester (知识收割)
    2. Knowledge Index (索引管理)
    3. Confidence Engine (置信度管理)
    4. Reflection Engine (反思引擎)
    5. Pattern Detector (模式检测)
    6. Learning Queue (学习队列)
    7. Workflow Metrics (工作流指标)
    8. Causal Metrics (因果度量) — v2.0
    9. Decision Recorder (决策记录) — v2.0
    10. Dependency Analyzer (依赖图谱) — v2.1
    11. Gate Deviation Detector (门禁偏离检测) — v2.2
    """

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.harvester = KnowledgeHarvester(base_dir)
        self.index_mgr = KnowledgeIndexManager(base_dir)
        self.confidence = ConfidenceEngine(base_dir)
        self.reflection = ReflectionEngine(base_dir)
        self.pattern_detector = PatternDetector(base_dir)
        self.learning_queue = LearningQueue(base_dir)
        self.metrics = WorkflowMetrics(base_dir)
        # v2.0 新增
        self.causal_metrics = CausalMetrics(base_dir)
        self.decision_recorder = DecisionRecorder(base_dir)
        self.knowledge_injector = KnowledgeInjector(base_dir)
        self.decision_replay = DecisionReplay(base_dir)
        self.pattern_scaffolder = PatternScaffolder(base_dir)
        self.project_scanner = ProjectScanner()
        self.convention_extractor = ConventionExtractor(base_dir)
        self.workflow_optimizer = WorkflowOptimizer(base_dir)
        self.decision_graph = DecisionGraph(base_dir)
        self.meta_learner = MetaLearner(base_dir)
        self.dependency_analyzer = DependencyAnalyzer(base_dir)
        self.gate_deviation_detector = GateDeviationDetector(base_dir)
        self._evolve_count = 0  # meta-evolve 触发计数器

    # ── /evolve ──

    def evolve(self) -> str:
        """
        执行完整进化周期。

        Steps:
        1. 处理学习队列
        2. 重建知识索引
        3. 运行 Confidence 衰减
        4. 检测代码模式
        5. 分析工作流效能
        6. 生成进化报告

        Returns
        -------
        str
            进化报告 (Markdown)
        """
        today = datetime.date.today().isoformat()

        # Step 1: 处理学习队列
        queue_stats = self.learning_queue.get_stats()
        processed = self.learning_queue.process_queue()

        # Step 2: 重建知识索引
        self.index_mgr.rebuild_index()
        entries = self.harvester.list_entries()

        # Step 3: Confidence 衰减 (v2.0: 自适应衰减)
        causal_scores = {}
        for entry in entries:
            kid = entry.get("id", "")
            if kid:
                causal_scores[kid] = self.causal_metrics.causal_score(kid)
        decayed = self.confidence.adaptive_decay(days=30, causal_scores=causal_scores)
        deprecated = self.confidence.get_deprecated()

        # Step 4: 因果分析 (v2.0 新增)
        anti_knowledge = self.causal_metrics.get_anti_knowledge()
        for kid in anti_knowledge:
            entry_content = self.harvester.get_entry(kid)
            if entry_content and "Anti-Pattern:" not in entry_content:
                self.harvester.harvest_anti_knowledge(
                    title=f"From {kid}",
                    summary=f"知识 {kid} 因果评分为负，已标记为反知识",
                    related=[kid],
                )

        # Step 4: 模式检测
        pattern_result = self.pattern_detector.detect_and_update()

        # Step 5: 工作流洞察
        insights = self.metrics.get_all_insights()

        # Step 5.5: 门禁偏离分析 (v2.2)
        deviation_patterns = self.gate_deviation_detector.analyze_patterns()

        # Step 6: 反思摘要
        reflection_summary = self.reflection.get_reflection_summary(5)
        pending_actions = self.reflection.get_pending_action_items()

        # Step 7: 清理
        cleaned = self.learning_queue.cleanup(days=7)

        # 生成报告
        report = self._generate_report(
            today=today,
            total_knowledge=len(entries),
            queue_processed=len(processed),
            queue_pending=queue_stats.get("pending", 0),
            decayed=decayed,
            deprecated=deprecated,
            pattern_result=pattern_result,
            insights=insights,
            reflection_summary=reflection_summary,
            pending_actions=pending_actions,
            cleaned=cleaned,
            anti_knowledge=anti_knowledge,
            causal_scores=causal_scores,
            deviation_patterns=deviation_patterns,
        )

        # v2.0: meta-evolve 自动触发 (每 5 次 evolve)
        self._evolve_count += 1
        meta_report = ""
        if self._evolve_count % 5 == 0:
            meta_report = self.meta_evolve()
            report += "\n\n" + meta_report

        return report

    # ── /reflect ──

    def reflect(
        self,
        session_name: str,
        duration: int = 0,
        went_well: list[str] | None = None,
        could_improve: list[str] | None = None,
        learnings: list[str] | None = None,
        action_items: list[str] | None = None,
        auto_fix_count: int = 0,
        rollback_count: int = 0,
    ) -> str:
        """执行反思并返回报告"""
        report = self.reflection.reflect(
            session_name=session_name,
            duration=duration,
            went_well=went_well,
            could_improve=could_improve,
            learnings=learnings,
            action_items=action_items,
            auto_fix_count=auto_fix_count,
            rollback_count=rollback_count,
        )

        # 将学习成果入队
        for learning in (learnings or []):
            self.learning_queue.add_item(
                source_type="conversation",
                source_id=f"reflect-{session_name}",
                priority="P2",
                description=learning,
            )

        return report.to_markdown()

    # ── /knowledge ──

    def search_knowledge(self, query: str) -> list[dict]:
        """搜索知识库"""
        return self.harvester.search(query)

    # ── /patterns ──

    def search_patterns(self, query: str) -> list[dict]:
        """搜索模式库"""
        return self.pattern_detector.suggest_reuse(query)

    # ── Task Lifecycle Hooks ──

    def on_task_completed(self, task_id: str, description: str = "") -> None:
        """任务完成钩子: 入队学习素材"""
        self.learning_queue.add_item(
            source_type="code_change",
            source_id=task_id,
            priority="P2",
            description=description,
        )

    def on_error_fixed(
        self, error_type: str, root_cause: str, solution: str
    ) -> None:
        """错误修复钩子: 入队学习素材 + 直接生成知识条目"""
        self.learning_queue.add_item(
            source_type="error_fix",
            source_id=f"fix-{error_type[:20]}",
            priority="P1",
            description=f"{error_type}: {root_cause}",
        )
        # 直接收割为知识
        entry = self.harvester.harvest_from_error_fix(
            error_type=error_type,
            root_cause=root_cause,
            solution=solution,
        )
        # 更新索引
        self.index_mgr.add_to_index(
            kid=entry.id,
            title=entry.title,
            category=entry.category,
            confidence=entry.confidence,
            created=entry.created,
        )

    def on_workflow_completed(
        self,
        workflow: str,
        duration_min: int,
        success: bool = True,
        notes: str = "",
    ) -> None:
        """工作流完成钩子: 记录指标"""
        self.metrics.record_run(
            workflow=workflow,
            duration_min=duration_min,
            success=success,
            notes=notes,
        )

    # ── v2.0: Decision & Outcome Tracking ──

    def record_decision(
        self,
        phase: str,
        context: str,
        options: list[str] | None = None,
        chosen: str = "",
        reason: str = "",
        knowledge_used: list[str] | None = None,
    ) -> str:
        """
        记录一次决策。

        Returns
        -------
        str
            决策 ID (D-xxx)
        """
        record = self.decision_recorder.record(
            phase=phase,
            context=context,
            options=options,
            chosen=chosen,
            reason=reason,
            knowledge_used=knowledge_used,
        )
        return record.id

    def record_outcome(
        self,
        knowledge_id: str,
        task: str = "",
        result: str = "success",
        time_saved: int = 0,
        bugs_introduced: int = 0,
        notes: str = "",
    ) -> None:
        """
        记录知识应用的结果。

        同时更新 confidence:
        - success → on_applied()
        - failure → on_misleading()
        """
        self.causal_metrics.record_outcome(
            knowledge_id=knowledge_id,
            task=task,
            result=result,
            time_saved=time_saved,
            bugs_introduced=bugs_introduced,
            notes=notes,
        )
        # 根据结果调整 confidence
        if result == "success":
            self.confidence.on_applied(knowledge_id)
        elif result == "failure":
            self.confidence.on_misleading(knowledge_id)

    # ── v2.0: Closed-Loop Feedback ──

    def inject_knowledge(self, phase: str, keywords: list[str], top_k: int = 5) -> str:
        """
        为工作流阶段注入相关知识。

        Returns
        -------
        str
            格式化的知识注入 Prompt 块
        """
        entries = self.knowledge_injector.retrieve_relevant(phase, keywords, top_k)
        return self.knowledge_injector.format_for_prompt(entries)

    def replay_decision(self, context: str) -> str:
        """
        查找相似历史决策并生成推荐。

        Returns
        -------
        str
            格式化的决策回放 Prompt 块
        """
        recommendation = self.decision_replay.recommend(context)
        return self.decision_replay.format_for_prompt(recommendation)

    def scaffold_pattern(self, description: str, top_k: int = 3) -> str:
        """
        基于功能描述生成模式脚手架建议。

        Returns
        -------
        str
            格式化的模式脚手架 Prompt 块
        """
        suggestions = self.pattern_scaffolder.suggest_and_scaffold(description, top_k)
        return self.pattern_scaffolder.format_for_prompt(suggestions)

    # ── v2.0: Project Learning ──

    def learn_project(self, path: str) -> str:
        """
        从参考项目学习开发规范和架构模式。

        执行 9 步扫描+提取+生成知识卡片，返回学习报告。

        Parameters
        ----------
        path : str
            参考项目路径

        Returns
        -------
        str
            学习报告 (Markdown)
        """
        from pathlib import Path as _Path
        project_path = _Path(path).resolve()
        project_name = project_path.name

        if not project_path.exists():
            return f"错误: 项目路径不存在: {path}"

        # Step 1-2: 检测项目类型
        project_type = self.project_scanner.detect_project_type(str(project_path))

        # Step 3: 扫描目录结构
        structure = self.project_scanner.scan_structure(str(project_path))

        # Step 4: 提取命名规范
        naming = self.project_scanner.extract_naming_conventions(str(project_path))

        # Step 5: 提取架构模式
        architecture = self.project_scanner.extract_architecture_patterns(str(project_path))

        # Step 6: 提取编码风格
        coding_style = self.convention_extractor.extract_coding_style(str(project_path))

        # Step 7: 提取依赖管理
        dependencies = self.convention_extractor.extract_dependency_patterns(str(project_path))

        # Step 8: 提取 Git 规范
        git_conventions = self.convention_extractor.extract_git_conventions(str(project_path))

        # Step 9: 生成知识卡片
        created_ids = self.convention_extractor.generate_knowledge_cards(
            project_path=str(project_path),
            project_type=project_type,
            structure=structure,
            naming=naming,
            architecture=architecture,
            coding_style=coding_style,
            dependencies=dependencies,
            git_conventions=git_conventions,
        )

        # 更新索引
        self.index_mgr.rebuild_index()

        # 注册到 learned_projects.md
        self._register_learned_project(project_name, str(project_path),
                                       project_type.get("type", "unknown"), created_ids)

        # 生成报告
        report = self._generate_learn_report(
            project_name=project_name,
            project_path=str(project_path),
            project_type=project_type,
            structure=structure,
            naming=naming,
            architecture=architecture,
            coding_style=coding_style,
            dependencies=dependencies,
            git_conventions=git_conventions,
            created_ids=created_ids,
        )

        return report

    # ── v2.0: Workflow Self-Evolution + Decision Graph ──

    def optimize_workflow(self) -> str:
        """
        分析工作流瓶颈并生成优化报告。

        Returns
        -------
        str
            工作流优化报告 (Markdown)
        """
        return self.workflow_optimizer.format_report()

    def review_regrets(self, min_score: float = -0.3) -> str:
        """
        执行后悔分析: 回顾历史决策错误。

        Returns
        -------
        str
            后悔分析报告 (Markdown)
        """
        stats = self.decision_graph.get_stats()
        regrets = self.decision_graph.regret_analysis(min_score=min_score)
        archived = self.decision_graph.archive_stale_nodes()

        lines = [
            "# 🔍 后悔分析报告",
            "",
            "## 图谱概况",
            f"- **总决策**: {stats.get('total_nodes', 0)} 个",
            f"- **有因果链**: {stats.get('nodes_with_effects', 0)} 个",
            f"- **平均评分**: {stats.get('avg_outcome_score', 0):.2f}",
            f"- **负面结果**: {stats.get('negative_outcomes', 0)} 个",
            f"- **归档过期节点**: {archived} 个",
            "",
        ]

        if regrets:
            lines.append(f"## 低分决策 (共 {len(regrets)} 个)")
            lines.append("")
            for reg in regrets[:10]:
                lines.append(f"### {reg['id']}: {reg['context'][:60]}")
                lines.append(f"- **选择**: {reg['chosen']}")
                lines.append(f"- **结果**: {reg['outcome']} (评分: {reg['outcome_score']})")
                lines.append(f"- **日期**: {reg.get('date', 'N/A')}")
                if reg.get("effects"):
                    lines.append(f"- **影响**: {len(reg['effects'])} 个后续决策")
                lines.append(f"- **建议**: {reg['suggestion']}")
                lines.append("")
        else:
            lines.append("## 未发现低分决策")
            lines.append("")
            lines.append("当前所有决策评分均在可接受范围内。")

        lines += [
            "",
            "---",
            f"*分析完成! 共发现 {len(regrets)} 个需要关注的决策。*",
            "",
        ]

        return "\n".join(lines)

    def add_decision_to_graph(
        self,
        decision_id: str,
        context: str = "",
        chosen: str = "",
        outcome: str = "",
        outcome_score: float = 0.0,
        phase: str = "",
        causes: list[str] | None = None,
    ) -> None:
        """添加决策到决策图"""
        self.decision_graph.add_node(
            decision_id=decision_id,
            context=context,
            chosen=chosen,
            outcome=outcome,
            outcome_score=outcome_score,
            phase=phase,
            causes=causes,
        )

    # ── v2.0: Meta-Learning ──

    def meta_evolve(self) -> str:
        """
        执行元学习: 分析进化引擎自身的效果。

        Returns
        -------
        str
            元学习洞察报告 (Markdown)
        """
        return self.meta_learner.generate_meta_report()

    def get_knowledge_gaps(self) -> list[dict]:
        """获取知识盲区"""
        return self.meta_learner.detect_knowledge_gaps()

    def get_harvest_strategy(self) -> dict:
        """获取收割策略优化建议"""
        return self.meta_learner.optimize_harvest_strategy()

    # ── v2.1: Dependency Graph ──

    def rebuild_dependency_graph(self) -> dict:
        """
        重建文件依赖图谱。

        Returns
        -------
        dict
            图谱统计信息
        """
        self.dependency_analyzer.build_graph()
        return self.dependency_analyzer.get_stats()

    def sync_check(self) -> str:
        """
        检测当前 git 变更的依赖同步状态。

        自动重建图谱后，对比 git diff 检测未同步的关联文件，
        返回格式化的 Markdown 报告。

        Returns
        -------
        str
            依赖同步检查报告 (Markdown)
        """
        self.dependency_analyzer.build_graph()
        result = self.dependency_analyzer.sync_check()
        return self.dependency_analyzer.format_sync_report(result)

    # ── v2.2: Gate Deviation Detection ──

    def record_gate_deviation(
        self,
        gate_id: str,
        workflow_file: str,
        expected_paths: list[str],
        user_input: str,
        user_intent: str = "",
        action_taken: str = "",
    ) -> str:
        """
        记录门禁偏离事件。

        Returns
        -------
        str
            偏离记录 ID (GD-xxx)
        """
        record = self.gate_deviation_detector.record_deviation(
            gate_id=gate_id,
            workflow_file=workflow_file,
            expected_paths=expected_paths,
            user_input=user_input,
            user_intent=user_intent,
            action_taken=action_taken,
        )
        return record.id

    def propose_workflow_change(self, deviation_id: str, **kwargs) -> dict:
        """
        生成工作流修改提案。

        Returns
        -------
        dict
            包含 diff_preview 的提案详情
        """
        return self.gate_deviation_detector.propose_modification(deviation_id, **kwargs)

    def apply_workflow_change(self, deviation_id: str) -> dict:
        """
        应用已确认的工作流修改（含备份 + 验证 + 决策记录）。

        Returns
        -------
        dict
            应用结果
        """
        result = self.gate_deviation_detector.apply_modification(deviation_id)

        if result.get("success"):
            record = self.gate_deviation_detector._load_record(deviation_id)
            if record:
                self.record_decision(
                    phase="workflow-evolution",
                    context=f"Gate deviation at {record.get('gate', '')}: {record.get('user_intent', '')}",
                    options=["add_gate_path", "add_step_before_gate", "add_step_after_gate", "reject"],
                    chosen=record.get("proposed_modification", "add_gate_path"),
                    reason=f"User confirmed workflow modification for deviation {deviation_id}",
                )

                workflow_file = record.get("workflow", "")
                if workflow_file:
                    impact = self.dependency_analyzer.impact_analysis([workflow_file])
                    result["impact_analysis"] = impact

        return result

    def rollback_workflow_change(self, deviation_id: str) -> dict:
        """回滚已应用的工作流修改。"""
        return self.gate_deviation_detector.rollback_modification(deviation_id)

    def get_deviation_patterns(self) -> list[dict]:
        """获取门禁偏离模式分析。"""
        return self.gate_deviation_detector.analyze_patterns()

    def _register_learned_project(
        self, name: str, path: str, ptype: str, kid_list: list[str]
    ) -> None:
        """注册已学习的项目"""
        reg_file = self.base_dir / "evolution" / "learned_projects.md"
        if not reg_file.exists():
            return
        today = datetime.date.today().isoformat()
        ids = ", ".join(kid_list)
        row = f"| {today} | {name} | {path} | {ptype} | {ids} | {len(kid_list)} |"
        text = reg_file.read_text(encoding="utf-8")
        text = text.rstrip() + "\n" + row + "\n"
        reg_file.write_text(text, encoding="utf-8")

    def _generate_learn_report(self, **kwargs) -> str:
        """生成项目学习报告"""
        lines = [
            f"# 📖 项目学习报告: {kwargs['project_name']}",
            "",
            "## 基本信息",
            f"- **路径**: {kwargs['project_path']}",
            f"- **类型**: {kwargs['project_type'].get('type', 'unknown')} ({kwargs['project_type'].get('language', 'unknown')})",
            f"- **检测置信度**: {kwargs['project_type'].get('confidence', 0):.0%}",
            f"- **文件数**: {kwargs['structure'].get('total_files', 0)} | **目录数**: {kwargs['structure'].get('total_dirs', 0)}",
            f"- **最大深度**: {kwargs['structure'].get('max_depth', 0)}",
            f"- **顶级目录**: {', '.join(kwargs['structure'].get('top_dirs', []))}",
            "",
            "## 命名规范",
            f"- **文件**: {kwargs['naming'].get('file_naming', 'unknown')}",
            f"- **目录**: {kwargs['naming'].get('dir_naming', 'unknown')}",
            f"- **类名**: {kwargs['naming'].get('class_pattern', 'unknown')}",
            f"- **函数名**: {kwargs['naming'].get('function_pattern', 'unknown')}",
            "",
            "## 架构模式",
        ]

        layers = kwargs["architecture"].get("layer_structure", [])
        if layers:
            for layer in layers:
                lines.append(f"- **{layer['layer']}**: `{layer['dir']}/`")
        else:
            lines.append("- 未检测到明确的分层结构")

        patterns = kwargs["architecture"].get("patterns_detected", [])
        if patterns:
            lines.append(f"- **设计模式**: {', '.join(patterns)}")

        lines.append(f"- **状态管理**: {kwargs['architecture'].get('state_management', 'unknown')}")
        lines.append(f"- **依赖注入**: {kwargs['architecture'].get('di_pattern', 'unknown')}")

        lines += [
            "",
            "## 编码风格",
            f"- **Lint 工具**: {', '.join(kwargs['coding_style'].get('lint_config', {}).keys()) or 'unknown'}",
            f"- **错误处理**: {kwargs['coding_style'].get('error_handling', 'unknown')}",
            f"- **Import 风格**: {kwargs['coding_style'].get('import_style', 'unknown')}",
            "",
            "## 依赖管理",
            f"- **包管理器**: {kwargs['dependencies'].get('package_manager', 'unknown')}",
            f"- **依赖数**: {kwargs['dependencies'].get('total_dependencies', 0)}",
            f"- **版本策略**: {kwargs['dependencies'].get('version_strategy', 'unknown')}",
            f"- **Lock 文件**: {'是' if kwargs['dependencies'].get('lock_file') else '否'}",
            "",
            "## Git 规范",
            f"- **Commit 格式**: {kwargs['git_conventions'].get('commit_format', 'unknown')}",
            f"- **分支策略**: {kwargs['git_conventions'].get('branch_strategy', 'unknown')}",
            f"- **CI 工具**: {kwargs['git_conventions'].get('ci_tool', 'unknown')}",
            "",
            "## 生成的知识卡片",
        ]

        for kid in kwargs["created_ids"]:
            lines.append(f"- {kid}")

        lines += [
            "",
            "---",
            f"*学习完成! 共生成 {len(kwargs['created_ids'])} 张知识卡片。*",
            "",
        ]

        return "\n".join(lines)

    # ── Report Generation ──

    def _generate_report(
        self,
        today: str,
        total_knowledge: int,
        queue_processed: int,
        queue_pending: int,
        decayed: list,
        deprecated: list,
        pattern_result: dict,
        insights: dict,
        reflection_summary: str,
        pending_actions: list,
        cleaned: int,
        anti_knowledge: list | None = None,
        causal_scores: dict | None = None,
        deviation_patterns: list | None = None,
    ) -> str:
        """生成进化报告"""
        lines = [
            f"# 🧬 Evolution Report — {today}",
            "",
            "## 📚 Knowledge Updates",
            f"- **Total**: {total_knowledge} items",
            f"- **Decayed** (30d unused): {len(decayed)} items",
            f"- **Deprecated** (confidence < 0.5): {len(deprecated)} items",
        ]
        if deprecated:
            for d in deprecated:
                lines.append(f"  - {d['id']}: {d['title']} (conf: {d['confidence']})")

        lines += [
            "",
            "## 📥 Learning Queue",
            f"- **Processed**: {queue_processed} items",
            f"- **Remaining**: {queue_pending} items",
            f"- **Cleaned** (7d old): {cleaned} items",
        ]

        # v2.0: 因果分析章节
        anti_knowledge = anti_knowledge or []
        causal_scores = causal_scores or {}
        lines += [
            "",
            "## 🔬 Causal Analysis",
            f"- **Tracked Knowledge**: {len(causal_scores)} items with causal data",
            f"- **Anti-Knowledge Detected**: {len(anti_knowledge)} items",
        ]
        if anti_knowledge:
            for kid in anti_knowledge[:5]:
                score = causal_scores.get(kid, 0.0)
                lines.append(f"  - {kid}: causal_score = {score}")
        # 显示 top-5 高因果评分知识
        top_causal = sorted(causal_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_causal and any(s > 0 for _, s in top_causal):
            lines.append("- **Top Performing Knowledge**:")
            for kid, score in top_causal:
                if score > 0:
                    lines.append(f"  - {kid}: causal_score = {score}")

        lines += [
            "",
            "## 🔄 Pattern Detection",
            f"- **Matches**: {len(pattern_result.get('matches', []))}",
            f"- **New Patterns**: {len(pattern_result.get('new_patterns', []))}",
            f"- **Promoted**: {len(pattern_result.get('promoted', []))}",
        ]
        for p in pattern_result.get("new_patterns", []):
            lines.append(f"  - NEW: {p}")
        for p in pattern_result.get("promoted", []):
            lines.append(f"  - PROMOTED: {p}")

        # v2.2: 门禁偏离分析
        deviation_patterns = deviation_patterns or []
        lines += [
            "",
            "## 🚪 Gate Deviation Analysis",
            f"- **Total Patterns**: {len(deviation_patterns)}",
        ]
        if deviation_patterns:
            for dp in deviation_patterns:
                status = "✅ applied" if dp.get("applied_count", 0) > 0 else "⏳ pending"
                lines.append(
                    f"  - **{dp['gate_id']}**: {dp['total_deviations']} deviations, "
                    f"top intent: \"{dp.get('top_intent', '')}\", status: {status}"
                )
                if dp.get("has_pending_proposal"):
                    lines.append(f"    → 建议运行 `/handle-deviation` 生成工作流修改提案")
        else:
            lines.append("  - 暂无偏离记录")

        lines += [
            "",
            "## 📊 Workflow Insights",
            "| Workflow | Avg Duration | Success Rate | Runs | Bottleneck |",
            "|----------|--------------|--------------|------|------------|",
        ]
        for wf, insight in insights.items():
            if insight.total_runs > 0:
                lines.append(
                    f"| {wf} | {insight.avg_duration} min "
                    f"| {insight.success_rate:.0%} | {insight.total_runs} "
                    f"| {insight.common_bottleneck or 'N/A'} |"
                )
        if all(i.total_runs == 0 for i in insights.values()):
            lines.append("| - | - | - | - | 暂无数据 |")

        # Suggestions
        suggestions = [i.suggestion for i in insights.values() if i.suggestion]
        if suggestions:
            lines += ["", "### Optimization Suggestions"]
            for i, s in enumerate(suggestions, 1):
                lines.append(f"{i}. {s}")

        lines += [
            "",
            "## 💭 Reflection Summary",
            reflection_summary,
            f"- **Pending Action Items**: {len(pending_actions)}",
        ]

        lines += [
            "",
            "## 🎯 Recommended Next Steps",
        ]
        if pending_actions:
            for act in pending_actions[:5]:
                lines.append(f"1. {act}")
        else:
            lines.append("1. 继续积累知识条目")
            lines.append("2. 执行 `/reflect` 反思最近的工作")

        lines += [
            "",
            "---",
            f"*Evolution Engine v2.2 | Total Knowledge: {total_knowledge} items "
            f"| Patterns: {len(pattern_result.get('matches', []))} "
            f"| Anti-Knowledge: {len(anti_knowledge)} "
            f"| Deviations: {len(deviation_patterns)}*",
            "",
        ]

        return "\n".join(lines)
