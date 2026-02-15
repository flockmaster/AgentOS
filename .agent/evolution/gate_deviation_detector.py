"""
Gate Deviation Detector — 门禁偏离检测器

检测用户在工作流门禁处的偏离行为，支持工作流自进化:
  - 记录门禁偏离事件
  - 基于关键词重叠查找相似历史偏离
  - 分析偏离模式 (按门禁聚合)
  - 生成工作流修改提案 (Markdown diff)
  - 安全应用修改 (备份 + 验证 + 回滚)

Usage:
    from evolution.gate_deviation_detector import GateDeviationDetector
    gdd = GateDeviationDetector(base_dir=".agent/memory")
    gdd.record_deviation(gate_id="1-drafting:step6",
                         workflow_file=".agent/workflows/1-drafting.md",
                         expected_paths=["满意", "修改", "推翻", "停止"],
                         user_input="把PRD发到飞书",
                         user_intent="export_to_feishu",
                         action_taken="调用 feishu-doc-assistant 上传 PRD")
    proposal = gdd.propose_modification("GD-001")
"""

from __future__ import annotations

import datetime
import difflib
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DeviationRecord:
    """门禁偏离记录数据结构"""
    id: str = ""                                             # GD-001, GD-002, ...
    gate_id: str = ""                                        # "1-drafting:step6"
    workflow_file: str = ""                                   # ".agent/workflows/1-drafting.md"
    expected_paths: list[str] = field(default_factory=list)   # ["满意", "修改", "推翻", "停止"]
    user_input: str = ""                                      # 用户原始输入
    user_intent: str = ""                                     # 分类后的意图标签
    action_taken: str = ""                                    # 执行的即时响应
    proposed_modification: str = ""                           # Markdown diff 预览
    modification_status: str = "recorded"                     # recorded|proposed|accepted|rejected|applied
    date: str = ""                                            # ISO date
    keywords: list[str] = field(default_factory=list)         # 自动提取的关键词

    def __post_init__(self):
        if not self.date:
            self.date = datetime.date.today().isoformat()
        if not self.keywords:
            self.keywords = self._extract_keywords()

    def _extract_keywords(self) -> list[str]:
        """从 user_input + user_intent + action_taken 中提取关键词"""
        text = f"{self.user_input} {self.user_intent} {self.action_taken}".lower()
        stopwords = {"的", "了", "在", "是", "和", "与", "或", "不", "要", "需要",
                     "把", "到", "给", "请", "这个", "那个", "一下",
                     "the", "a", "an", "is", "are", "to", "for", "and", "or", "in"}
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)
        return [w for w in words if w not in stopwords and len(w) > 1]


class GateDeviationDetector:
    """
    门禁偏离检测器。

    职责:
    1. 记录门禁偏离事件 (record_deviation)
    2. 基于关键词重叠查找相似历史偏离 (find_similar)
    3. 按门禁聚合分析偏离模式 (analyze_patterns)
    4. 生成工作流修改提案 (propose_modification)
    5. 安全应用修改 (apply_modification)
    6. 从备份回滚 (rollback_modification)
    """

    SIMILARITY_THRESHOLD = 0.6    # 判定为同类偏离的相似度阈值

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.log_file = self.base_dir / "evolution" / "gate_deviation_log.md"
        self.backup_dir = self.base_dir / "evolution" / "workflow_backups"
        self._ensure_log()

    def _ensure_log(self) -> None:
        """确保 gate_deviation_log.md 和备份目录存在"""
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text(
                "# Gate Deviation Log\n\n"
                "门禁偏离记录，用于工作流自进化分析。\n\n"
                "---\n\n",
                encoding="utf-8",
            )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ──

    def record_deviation(
        self,
        gate_id: str,
        workflow_file: str,
        expected_paths: list[str],
        user_input: str,
        user_intent: str = "",
        action_taken: str = "",
    ) -> DeviationRecord:
        """
        记录一次门禁偏离事件。

        Parameters
        ----------
        gate_id : str
            门禁标识，如 "1-drafting:step6"
        workflow_file : str
            工作流文件路径，如 ".agent/workflows/1-drafting.md"
        expected_paths : list[str]
            门禁定义的预期路径列表
        user_input : str
            用户原始输入
        user_intent : str
            分类后的意图标签
        action_taken : str
            执行的即时响应描述

        Returns
        -------
        DeviationRecord
        """
        did = self._next_id()
        record = DeviationRecord(
            id=did,
            gate_id=gate_id,
            workflow_file=workflow_file,
            expected_paths=expected_paths,
            user_input=user_input,
            user_intent=user_intent,
            action_taken=action_taken,
        )
        self._append_record(record)
        return record

    def find_similar(
        self,
        user_input: str,
        gate_id: str = "",
        top_k: int = 5,
    ) -> list[dict]:
        """
        查找与给定输入相似的历史偏离。

        基于关键词重叠评分:
        similarity = |keywords_A ∩ keywords_B| / max(|keywords_A|, |keywords_B|)

        Parameters
        ----------
        user_input : str
            用户输入文本
        gate_id : str
            可选，限定在某个门禁范围内搜索
        top_k : int
            返回 top-k 个最相似的偏离

        Returns
        -------
        list[dict]
            [{id, gate_id, user_input, user_intent, modification_status, similarity}, ...]
        """
        query_keywords = set(self._extract_keywords(user_input))
        if not query_keywords:
            return []

        records = self._load_all_records()
        scored = []

        for rec in records:
            if gate_id and rec.get("gate_id", "") != gate_id:
                continue

            rec_keywords = set(rec.get("keywords", []))
            if not rec_keywords:
                continue
            overlap = len(query_keywords & rec_keywords)
            max_len = max(len(query_keywords), len(rec_keywords))
            similarity = overlap / max_len if max_len > 0 else 0.0

            if similarity > 0.0:
                scored.append({
                    "id": rec.get("id", ""),
                    "gate_id": rec.get("gate_id", ""),
                    "user_input": rec.get("user_input", ""),
                    "user_intent": rec.get("user_intent", ""),
                    "modification_status": rec.get("modification_status", ""),
                    "similarity": round(similarity, 3),
                })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def analyze_patterns(self) -> list[dict]:
        """
        按门禁聚合分析偏离模式。

        Returns
        -------
        list[dict]
            [{
                "gate_id": str,
                "workflow_file": str,
                "total_deviations": int,
                "unique_intents": list[str],
                "top_intent": str,
                "has_pending_proposal": bool,
                "applied_count": int,
            }, ...]
        """
        records = self._load_all_records()
        if not records:
            return []

        gate_groups: dict[str, list[dict]] = {}
        for rec in records:
            gid = rec.get("gate_id", "unknown")
            gate_groups.setdefault(gid, []).append(rec)

        patterns = []
        for gate_id, recs in gate_groups.items():
            intents = [r.get("user_intent", "") for r in recs if r.get("user_intent")]
            statuses = [r.get("modification_status", "") for r in recs]
            patterns.append({
                "gate_id": gate_id,
                "workflow_file": recs[0].get("workflow_file", ""),
                "total_deviations": len(recs),
                "unique_intents": list(set(intents)),
                "top_intent": max(set(intents), key=intents.count) if intents else "",
                "has_pending_proposal": any(s in ("recorded", "proposed") for s in statuses),
                "applied_count": sum(1 for s in statuses if s == "applied"),
            })

        patterns.sort(key=lambda x: x["total_deviations"], reverse=True)
        return patterns

    def propose_modification(
        self,
        deviation_id: str,
        new_path_name: str = "",
        new_path_action: str = "",
        modification_type: str = "add_gate_path",
    ) -> dict:
        """
        生成工作流修改提案。

        Parameters
        ----------
        deviation_id : str
            偏离记录 ID (GD-xxx)
        new_path_name : str
            新路径名称（为空时从 user_intent 推断）
        new_path_action : str
            新路径动作描述（为空时从 action_taken 推断）
        modification_type : str
            修改类型: add_gate_path | add_step_before_gate | add_step_after_gate

        Returns
        -------
        dict
            {
                "deviation_id": str,
                "workflow_file": str,
                "modification_type": str,
                "original_section": str,
                "proposed_section": str,
                "diff_preview": str,
                "rationale": str,
                "success": bool,
                "error": str,
            }
        """
        record = self._load_record(deviation_id)
        if not record:
            return {"success": False, "error": f"偏离记录 {deviation_id} 不存在"}

        workflow_path = self._resolve_workflow_path(record.get("workflow_file", ""))
        if not workflow_path or not workflow_path.exists():
            return {"success": False, "error": f"工作流文件不存在: {record.get('workflow_file', '')}"}

        content = workflow_path.read_text(encoding="utf-8")
        gate_id = record.get("gate_id", "")
        user_intent = record.get("user_intent", "")
        action_taken = record.get("action_taken", "")

        if not new_path_name:
            new_path_name = user_intent or record.get("user_input", "")
        if not new_path_action:
            new_path_action = action_taken or "执行用户请求"

        if modification_type == "add_gate_path":
            result = self._generate_path_addition(content, gate_id, new_path_name, new_path_action)
        elif modification_type == "add_step_before_gate":
            result = self._generate_step_insertion(content, gate_id, new_path_name, new_path_action, before=True)
        elif modification_type == "add_step_after_gate":
            result = self._generate_step_insertion(content, gate_id, new_path_name, new_path_action, before=False)
        else:
            return {"success": False, "error": f"不支持的修改类型: {modification_type}"}

        if not result["success"]:
            return result

        # 生成 unified diff
        original_lines = content.splitlines(keepends=True)
        proposed_lines = result["proposed_content"].splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            proposed_lines,
            fromfile=f"{record.get('workflow_file', '')} (原始)",
            tofile=f"{record.get('workflow_file', '')} (修改后)",
            lineterm="",
        )
        diff_preview = "\n".join(diff)

        # 更新记录状态
        self._update_record_field(deviation_id, "Proposed Modification", modification_type)
        self._update_record_field(deviation_id, "Modification Status", "proposed")

        return {
            "deviation_id": deviation_id,
            "workflow_file": record.get("workflow_file", ""),
            "modification_type": modification_type,
            "original_section": result.get("original_section", ""),
            "proposed_section": result.get("proposed_section", ""),
            "proposed_content": result["proposed_content"],
            "diff_preview": diff_preview,
            "rationale": f"用户在门禁 {gate_id} 偏离，意图: {user_intent}，动作: {action_taken}",
            "success": True,
            "error": "",
        }

    def apply_modification(self, deviation_id: str) -> dict:
        """
        应用已提议的工作流修改。

        安全协议:
        1. 创建时间戳备份
        2. 应用修改
        3. 验证修改后的文件结构
        4. 返回影响分析所需信息

        Parameters
        ----------
        deviation_id : str
            偏离记录 ID

        Returns
        -------
        dict
            {
                "success": bool,
                "backup_path": str,
                "validation_errors": list[str],
                "workflow_file": str,
                "error": str,
            }
        """
        record = self._load_record(deviation_id)
        if not record:
            return {"success": False, "error": f"偏离记录 {deviation_id} 不存在"}

        if record.get("modification_status") != "proposed":
            return {"success": False, "error": f"记录状态非 proposed，当前: {record.get('modification_status', '')}"}

        workflow_path = self._resolve_workflow_path(record.get("workflow_file", ""))
        if not workflow_path or not workflow_path.exists():
            return {"success": False, "error": f"工作流文件不存在: {record.get('workflow_file', '')}"}

        # 重新生成提案（确保使用最新的文件内容）
        mod_type = record.get("proposed_modification", "add_gate_path")
        proposal = self.propose_modification(deviation_id, modification_type=mod_type)
        if not proposal.get("success"):
            return {"success": False, "error": proposal.get("error", "提案生成失败")}

        # 1. 创建备份
        backup_path = self._create_backup(workflow_path)

        # 2. 应用修改
        proposed_content = proposal.get("proposed_content", "")
        if not proposed_content:
            return {"success": False, "error": "提案内容为空"}

        workflow_path.write_text(proposed_content, encoding="utf-8")

        # 3. 验证
        validation_errors = self._validate_workflow(proposed_content)
        if validation_errors:
            # 验证失败，自动回滚
            shutil.copy2(backup_path, workflow_path)
            self._update_record_field(deviation_id, "Modification Status", "rejected")
            return {
                "success": False,
                "backup_path": str(backup_path),
                "validation_errors": validation_errors,
                "workflow_file": record.get("workflow_file", ""),
                "error": f"验证失败，已自动回滚: {'; '.join(validation_errors)}",
            }

        # 4. 更新记录状态
        self._update_record_field(deviation_id, "Modification Status", "applied")

        return {
            "success": True,
            "backup_path": str(backup_path),
            "validation_errors": [],
            "workflow_file": record.get("workflow_file", ""),
            "error": "",
        }

    def rollback_modification(self, deviation_id: str) -> dict:
        """
        回滚已应用的工作流修改。

        Parameters
        ----------
        deviation_id : str
            偏离记录 ID

        Returns
        -------
        dict
            {"success": bool, "restored_from": str, "error": str}
        """
        record = self._load_record(deviation_id)
        if not record:
            return {"success": False, "restored_from": "", "error": f"偏离记录 {deviation_id} 不存在"}

        if record.get("modification_status") != "applied":
            return {"success": False, "restored_from": "", "error": "该记录未处于 applied 状态，无需回滚"}

        workflow_path = self._resolve_workflow_path(record.get("workflow_file", ""))
        if not workflow_path:
            return {"success": False, "restored_from": "", "error": "工作流文件路径无效"}

        # 查找最新备份
        stem = workflow_path.stem
        backups = sorted(self.backup_dir.glob(f"{stem}_backup_*.md"), reverse=True)
        if not backups:
            return {"success": False, "restored_from": "", "error": f"未找到 {stem} 的备份文件"}

        backup_path = backups[0]
        shutil.copy2(backup_path, workflow_path)
        self._update_record_field(deviation_id, "Modification Status", "rejected")

        return {
            "success": True,
            "restored_from": str(backup_path),
            "error": "",
        }

    def format_report(self) -> str:
        """生成偏离分析报告"""
        patterns = self.analyze_patterns()
        records = self._load_all_records()

        lines = [
            "# Gate Deviation Analysis",
            "",
            f"- **Total Deviations**: {len(records)}",
            f"- **Unique Gates**: {len(patterns)}",
            "",
        ]

        if patterns:
            lines.append("## Hot Patterns")
            for p in patterns:
                status_icon = "applied" if p["applied_count"] > 0 else "pending"
                lines.append(
                    f"- **{p['gate_id']}**: {p['total_deviations']} deviations, "
                    f"top intent: \"{p['top_intent']}\", status: {status_icon}"
                )
        else:
            lines.append("No deviations recorded yet.")

        lines.append("")
        return "\n".join(lines)

    # ── Private Methods: Persistence ──

    def _next_id(self) -> str:
        """生成下一个偏离 ID"""
        if not self.log_file.exists():
            return "GD-001"

        text = self.log_file.read_text(encoding="utf-8")
        ids = re.findall(r"### (GD-\d+)", text)
        if not ids:
            return "GD-001"

        max_num = max(int(d.split("-")[1]) for d in ids)
        return f"GD-{max_num + 1:03d}"

    def _append_record(self, record: DeviationRecord) -> None:
        """追加偏离记录到 log 文件"""
        text = self.log_file.read_text(encoding="utf-8")
        entry = (
            f"### {record.id}\n"
            f"- **Date**: {record.date}\n"
            f"- **Gate**: {record.gate_id}\n"
            f"- **Workflow**: {record.workflow_file}\n"
            f"- **Expected Paths**: {', '.join(record.expected_paths)}\n"
            f"- **User Input**: {record.user_input}\n"
            f"- **User Intent**: {record.user_intent}\n"
            f"- **Action Taken**: {record.action_taken}\n"
            f"- **Proposed Modification**: {record.proposed_modification or '[pending]'}\n"
            f"- **Modification Status**: {record.modification_status}\n"
            f"- **Keywords**: {', '.join(record.keywords)}\n"
            f"\n---\n\n"
        )
        text = text.rstrip() + "\n\n" + entry
        self.log_file.write_text(text, encoding="utf-8")

    def _load_all_records(self) -> list[dict]:
        """加载所有偏离记录"""
        if not self.log_file.exists():
            return []

        text = self.log_file.read_text(encoding="utf-8")
        records = []
        blocks = re.split(r"### (GD-\d+)", text)

        for i in range(1, len(blocks) - 1, 2):
            did = blocks[i]
            content = blocks[i + 1]
            rec = {"id": did}
            for field_name in [
                "Date", "Gate", "Workflow", "Expected Paths",
                "User Input", "User Intent", "Action Taken",
                "Proposed Modification", "Modification Status", "Keywords",
            ]:
                m = re.search(rf"\*\*{re.escape(field_name)}\*\*:\s*(.*?)(?:\n|$)", content)
                if m:
                    val = m.group(1).strip()
                    # 映射 Markdown 字段名到内部字段名
                    key_map = {
                        "gate": "gate_id",
                        "workflow": "workflow_file",
                    }
                    key = field_name.lower().replace(" ", "_")
                    key = key_map.get(key, key)
                    if key in ("expected_paths", "keywords"):
                        val = [v.strip() for v in val.split(",") if v.strip()]
                    rec[key] = val
            records.append(rec)

        return records

    def _load_record(self, deviation_id: str) -> Optional[dict]:
        """加载单条偏离记录"""
        records = self._load_all_records()
        for rec in records:
            if rec.get("id") == deviation_id:
                return rec
        return None

    def _update_record_field(self, deviation_id: str, field_name: str, new_value: str) -> bool:
        """更新偏离记录中的某个字段"""
        if not self.log_file.exists():
            return False

        text = self.log_file.read_text(encoding="utf-8")
        marker = f"### {deviation_id}"
        if marker not in text:
            return False

        escaped_field = re.escape(field_name)
        old_pattern = rf"(### {re.escape(deviation_id)}.*?\*\*{escaped_field}\*\*:\s*)(.*?)(\n)"
        new_text = re.sub(old_pattern, rf"\g<1>{new_value}\3", text, count=1, flags=re.DOTALL)

        if new_text != text:
            self.log_file.write_text(new_text, encoding="utf-8")
            return True
        return False

    # ── Private Methods: Workflow Parsing ──

    def _resolve_workflow_path(self, workflow_file: str) -> Optional[Path]:
        """将相对路径解析为绝对路径"""
        if not workflow_file:
            return None
        # 支持相对于项目根目录的路径
        path = Path(workflow_file)
        if path.is_absolute() and path.exists():
            return path
        # 从 base_dir 向上找项目根目录
        project_root = self.base_dir.parent  # .agent/memory -> .agent -> project_root
        if (self.base_dir / ".." / ".." / workflow_file).resolve().exists():
            return (self.base_dir / ".." / ".." / workflow_file).resolve()
        if (project_root / ".." / workflow_file).resolve().exists():
            return (project_root / ".." / workflow_file).resolve()
        return None

    def _parse_gate_section(self, content: str, gate_id: str) -> Optional[dict]:
        """
        解析工作流文件中的门禁结构。

        Parameters
        ----------
        content : str
            工作流文件内容
        gate_id : str
            门禁标识，如 "1-drafting:step6"

        Returns
        -------
        dict | None
            {
                "step_number": int,
                "title": str,
                "start_line": int,       # 0-indexed
                "end_line": int,          # 0-indexed, exclusive
                "paths_start_line": int,  # **路径**: 所在行
                "paths_end_line": int,    # 路径块结束行
                "paths": list[str],
                "raw_content": str,
                "last_path_line": int,    # 最后一条路径所在行
            }
        """
        lines = content.split("\n")

        # 从 gate_id 提取 step 编号
        step_match = re.search(r"step(\d+)", gate_id)
        if not step_match:
            return None
        target_step = int(step_match.group(1))

        # 查找该步骤的开始
        step_start = None
        for i, line in enumerate(lines):
            # 匹配 "N.  **标题**" 模式
            m = re.match(rf"^\s*{target_step}\.\s+\*\*", line)
            if m:
                step_start = i
                break

        if step_start is None:
            return None

        # 查找下一个步骤或文件结束作为该步骤的结束
        step_end = len(lines)
        for i in range(step_start + 1, len(lines)):
            if re.match(r"^\s*\d+\.\s+\*\*", lines[i]):
                step_end = i
                break
            # 也检查顶层标题
            if re.match(r"^## ", lines[i]):
                step_end = i
                break

        # 在步骤内查找 **路径**: 块
        paths_start = None
        paths = []
        path_lines = []
        last_path_line = None

        for i in range(step_start, step_end):
            if re.search(r"\*\*路径\*\*", lines[i]):
                paths_start = i
                continue
            if paths_start is not None and i > paths_start:
                # 匹配 "- **路径名**: 描述" 或 "- **路径名，描述**: 动作"
                pm = re.match(r"^\s+- \*\*(.+?)\*\*", lines[i])
                if pm:
                    paths.append(pm.group(1).rstrip(":"))
                    path_lines.append(i)
                    last_path_line = i

        if paths_start is None:
            return None

        # 路径块的结束：最后一条路径行 + 1（或直到遇到非缩进内容）
        paths_end = step_end
        if last_path_line is not None:
            for i in range(last_path_line + 1, step_end):
                stripped = lines[i].strip()
                if stripped and not stripped.startswith("-") and not lines[i].startswith("        "):
                    # 偏离处理块或其他内容
                    if re.match(r"^\s+- \*\*偏离处理", lines[i]):
                        paths_end = i
                        break
                    if not lines[i].startswith("    "):
                        paths_end = i
                        break

        return {
            "step_number": target_step,
            "title": lines[step_start].strip(),
            "start_line": step_start,
            "end_line": step_end,
            "paths_start_line": paths_start,
            "paths_end_line": paths_end,
            "paths": paths,
            "raw_content": "\n".join(lines[step_start:step_end]),
            "last_path_line": last_path_line if last_path_line is not None else paths_start + 1,
        }

    def _generate_path_addition(
        self,
        content: str,
        gate_id: str,
        new_path_name: str,
        new_path_action: str,
    ) -> dict:
        """
        在门禁的路径列表中添加新路径（在"停止"路径前插入）。

        Returns
        -------
        dict
            {"success": bool, "proposed_content": str, "original_section": str, "proposed_section": str, "error": str}
        """
        gate = self._parse_gate_section(content, gate_id)
        if not gate:
            return {"success": False, "error": f"无法解析门禁结构: {gate_id}"}

        lines = content.split("\n")

        # 找到"停止"路径所在行，在其前插入；如果没有停止路径，在最后一条路径后插入
        insert_line = gate["last_path_line"] + 1
        for i in range(gate["paths_start_line"], gate["paths_end_line"]):
            if re.search(r"\*\*停止\*\*", lines[i]):
                insert_line = i
                break

        # 推断缩进（与现有路径对齐）
        ref_line = lines[gate["last_path_line"]]
        indent = re.match(r"^(\s*)", ref_line).group(1)

        new_line = f"{indent}- **{new_path_name}**: {new_path_action}"

        # 构建原始和修改后的片段（用于展示）
        original_section = "\n".join(lines[gate["paths_start_line"]:gate["paths_end_line"]])

        new_lines = lines[:insert_line] + [new_line] + lines[insert_line:]
        proposed_section = "\n".join(
            new_lines[gate["paths_start_line"]:gate["paths_end_line"] + 1]
        )

        return {
            "success": True,
            "proposed_content": "\n".join(new_lines),
            "original_section": original_section,
            "proposed_section": proposed_section,
            "error": "",
        }

    def _generate_step_insertion(
        self,
        content: str,
        gate_id: str,
        step_name: str,
        step_action: str,
        before: bool = True,
    ) -> dict:
        """
        在门禁步骤前/后插入新步骤（自动重编号后续步骤）。

        Returns
        -------
        dict
            {"success": bool, "proposed_content": str, "original_section": str, "proposed_section": str, "error": str}
        """
        gate = self._parse_gate_section(content, gate_id)
        if not gate:
            return {"success": False, "error": f"无法解析门禁结构: {gate_id}"}

        lines = content.split("\n")
        step_num = gate["step_number"]
        insert_at = gate["start_line"] if before else gate["end_line"]
        new_step_num = step_num if before else step_num + 1

        new_step_content = (
            f"\n{new_step_num}.  **{step_name}** — *v2.2*\n"
            f"    - **动作**: {step_action}\n"
        )

        # 插入新步骤
        new_lines = lines[:insert_at] + new_step_content.split("\n") + lines[insert_at:]
        new_content = "\n".join(new_lines)

        # 重编号后续步骤
        renumber_from = new_step_num + 1
        result_lines = new_content.split("\n")
        current_num = renumber_from
        for i, line in enumerate(result_lines):
            # 只重编号插入点之后的步骤
            if i <= insert_at:
                continue
            m = re.match(r"^(\s*)(\d+)\.\s+(\*\*)", line)
            if m:
                result_lines[i] = f"{m.group(1)}{current_num}.  {m.group(3)}{line[m.end(3):]}"
                current_num += 1

        proposed_content = "\n".join(result_lines)

        return {
            "success": True,
            "proposed_content": proposed_content,
            "original_section": f"(在步骤 {step_num} {'前' if before else '后'}插入)",
            "proposed_section": new_step_content.strip(),
            "error": "",
        }

    # ── Private Methods: Safety ──

    def _create_backup(self, workflow_path: Path) -> Path:
        """创建工作流文件的时间戳备份"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{workflow_path.stem}_backup_{timestamp}.md"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(workflow_path, backup_path)
        return backup_path

    def _validate_workflow(self, content: str) -> list[str]:
        """
        验证修改后的工作流内容结构完整性。

        检查:
        - YAML frontmatter 是否完整
        - 步骤编号是否存在
        - 基本 Markdown 结构

        Returns
        -------
        list[str]
            验证错误列表（空 = 通过）
        """
        errors = []

        # 检查 YAML frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end == -1:
                errors.append("YAML frontmatter 未闭合")
        else:
            errors.append("缺少 YAML frontmatter")

        # 检查是否存在步骤编号
        step_nums = re.findall(r"^\s*(\d+)\.\s+\*\*", content, re.MULTILINE)
        if not step_nums:
            errors.append("未找到任何步骤编号")

        # 检查步骤编号是否有序（允许从 0 或 1 开始）
        nums = [int(n) for n in step_nums]
        if nums:
            for i in range(1, len(nums)):
                if nums[i] != nums[i - 1] + 1:
                    errors.append(f"步骤编号不连续: {nums[i - 1]} → {nums[i]}")
                    break

        return errors

    @staticmethod
    def _extract_keywords(text: str) -> list[str]:
        """从文本中提取关键词"""
        text_lower = text.lower()
        stopwords = {"的", "了", "在", "是", "和", "与", "或", "不", "要", "需要",
                     "把", "到", "给", "请", "这个", "那个", "一下",
                     "the", "a", "an", "is", "are", "to", "for", "and", "or", "in"}
        words = re.findall(r'[\w\u4e00-\u9fff]+', text_lower)
        return [w for w in words if w not in stopwords and len(w) > 1]
