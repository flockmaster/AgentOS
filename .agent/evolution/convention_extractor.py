"""
Convention Extractor — 规范提取器

从参考项目中提取编码规范、依赖模式、Git 规范，生成知识卡片:
  - 提取编码风格 (lint 配置、格式化规则、错误处理)
  - 提取依赖模式 (依赖管理、版本策略)
  - 提取 Git 规范 (commit 格式、分支策略)
  - 生成知识卡片

Usage:
    from evolution.convention_extractor import ConventionExtractor
    ce = ConventionExtractor(base_dir=".agent/memory")
    style = ce.extract_coding_style("/path/to/project")
    cards = ce.generate_knowledge_cards(scan_result)
"""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path
from typing import Optional

from evolution.harvester import KnowledgeHarvester


class ConventionExtractor:
    """
    规范提取器。

    职责:
    1. 提取编码风格
    2. 提取依赖模式
    3. 提取 Git 规范
    4. 生成知识卡片
    """

    # 忽略的目录
    IGNORE_DIRS = {
        ".git", ".svn", "node_modules", "__pycache__", ".dart_tool",
        "build", "dist", ".next", ".nuxt", "target", "vendor",
        ".idea", ".vscode", ".gradle", ".pub-cache",
    }

    def __init__(self, base_dir: str | Path = ".agent/memory"):
        self.base_dir = Path(base_dir)
        self.harvester = KnowledgeHarvester(base_dir)

    # ── Public API ──

    def extract_coding_style(self, project_path: str | Path) -> dict:
        """
        提取编码风格。

        Returns
        -------
        dict
            {
                "lint_config": dict,       # lint 配置信息
                "format_rules": dict,      # 格式化规则
                "error_handling": str,      # 错误处理模式
                "import_style": str,       # import 组织风格
                "comment_style": str,      # 注释风格
            }
        """
        path = Path(project_path)

        # 检测 lint 配置
        lint_config = self._detect_lint_config(path)

        # 检测格式化规则
        format_rules = self._detect_format_rules(path)

        # 检测错误处理模式
        error_handling = self._detect_error_handling(path)

        # 检测 import 风格
        import_style = self._detect_import_style(path)

        # 检测注释风格
        comment_style = self._detect_comment_style(path)

        return {
            "lint_config": lint_config,
            "format_rules": format_rules,
            "error_handling": error_handling,
            "import_style": import_style,
            "comment_style": comment_style,
        }

    def extract_dependency_patterns(self, project_path: str | Path) -> dict:
        """
        提取依赖模式。

        Returns
        -------
        dict
            {
                "package_manager": str,
                "total_dependencies": int,
                "key_dependencies": list,
                "version_strategy": str,   # exact | range | latest
                "lock_file": bool,
            }
        """
        path = Path(project_path)
        result = {
            "package_manager": "unknown",
            "total_dependencies": 0,
            "key_dependencies": [],
            "version_strategy": "unknown",
            "lock_file": False,
        }

        # Flutter/Dart
        pubspec = path / "pubspec.yaml"
        if pubspec.exists():
            content = self._read_file_safe(pubspec)
            result["package_manager"] = "pub"
            result["lock_file"] = (path / "pubspec.lock").exists()
            deps = re.findall(r'^\s+(\w[\w_-]*):', content, re.MULTILINE)
            result["key_dependencies"] = deps[:15]
            result["total_dependencies"] = len(deps)
            if "^" in content:
                result["version_strategy"] = "caret (compatible)"
            elif "any" in content:
                result["version_strategy"] = "any (latest)"
            else:
                result["version_strategy"] = "exact"
            return result

        # Node.js
        pkg_json = path / "package.json"
        if pkg_json.exists():
            content = self._read_file_safe(pkg_json)
            result["package_manager"] = "npm/yarn"
            if (path / "yarn.lock").exists():
                result["package_manager"] = "yarn"
                result["lock_file"] = True
            elif (path / "package-lock.json").exists():
                result["package_manager"] = "npm"
                result["lock_file"] = True
            elif (path / "pnpm-lock.yaml").exists():
                result["package_manager"] = "pnpm"
                result["lock_file"] = True
            deps = re.findall(r'"([@\w/-]+)":\s*"', content)
            result["key_dependencies"] = deps[:15]
            result["total_dependencies"] = len(deps)
            if "^" in content:
                result["version_strategy"] = "caret (compatible)"
            elif "~" in content:
                result["version_strategy"] = "tilde (patch)"
            return result

        # Python
        for pyfile in ["pyproject.toml", "setup.py", "requirements.txt"]:
            f = path / pyfile
            if f.exists():
                content = self._read_file_safe(f)
                result["package_manager"] = "pip"
                if (path / "poetry.lock").exists():
                    result["package_manager"] = "poetry"
                    result["lock_file"] = True
                elif (path / "Pipfile.lock").exists():
                    result["package_manager"] = "pipenv"
                    result["lock_file"] = True
                deps = re.findall(r'[\w-]+(?=[>=<~!])', content)
                result["key_dependencies"] = deps[:15]
                result["total_dependencies"] = len(deps)
                return result

        # Go
        gomod = path / "go.mod"
        if gomod.exists():
            content = self._read_file_safe(gomod)
            result["package_manager"] = "go mod"
            result["lock_file"] = (path / "go.sum").exists()
            deps = re.findall(r'\t([\w./]+)', content)
            result["key_dependencies"] = deps[:15]
            result["total_dependencies"] = len(deps)
            return result

        return result

    def extract_git_conventions(self, project_path: str | Path) -> dict:
        """
        提取 Git 规范。

        Returns
        -------
        dict
            {
                "commit_format": str,           # conventional | freeform | unknown
                "commit_examples": list[str],
                "branch_strategy": str,
                "has_gitignore": bool,
                "has_ci": bool,
                "ci_tool": str,
            }
        """
        path = Path(project_path)
        result = {
            "commit_format": "unknown",
            "commit_examples": [],
            "branch_strategy": "unknown",
            "has_gitignore": (path / ".gitignore").exists(),
            "has_ci": False,
            "ci_tool": "unknown",
        }

        # 检测 CI 配置
        ci_configs = {
            ".github/workflows": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            "Jenkinsfile": "Jenkins",
            ".circleci": "CircleCI",
            ".travis.yml": "Travis CI",
            "azure-pipelines.yml": "Azure Pipelines",
        }
        for ci_path, ci_name in ci_configs.items():
            if (path / ci_path).exists():
                result["has_ci"] = True
                result["ci_tool"] = ci_name
                break

        # 读取 git log (如果有 .git 目录)
        git_dir = path / ".git"
        if git_dir.exists():
            try:
                import subprocess
                git_log = subprocess.run(
                    ["git", "-C", str(path), "log", "--oneline", "-20"],
                    capture_output=True, text=True, timeout=5
                )
                if git_log.returncode == 0:
                    commits = git_log.stdout.strip().split("\n")
                    messages = [c.split(" ", 1)[1] if " " in c else c for c in commits if c]
                    result["commit_examples"] = messages[:5]

                    # 检测 conventional commits
                    conventional = sum(1 for m in messages
                                       if re.match(r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?:', m))
                    if conventional > len(messages) * 0.5:
                        result["commit_format"] = "conventional"
                    else:
                        result["commit_format"] = "freeform"

                # 检测分支策略
                branches = subprocess.run(
                    ["git", "-C", str(path), "branch", "-a"],
                    capture_output=True, text=True, timeout=5
                )
                if branches.returncode == 0:
                    branch_list = branches.stdout.strip()
                    if "develop" in branch_list:
                        result["branch_strategy"] = "git-flow"
                    elif "release/" in branch_list:
                        result["branch_strategy"] = "release-branch"
                    else:
                        result["branch_strategy"] = "trunk-based"
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                pass

        return result

    def generate_knowledge_cards(
        self,
        project_path: str,
        project_type: dict,
        structure: dict,
        naming: dict,
        architecture: dict,
        coding_style: dict,
        dependencies: dict,
        git_conventions: dict,
    ) -> list[str]:
        """
        从扫描结果生成知识卡片。

        Returns
        -------
        list[str]
            生成的知识条目 ID 列表
        """
        created_ids = []
        project_name = Path(project_path).name

        # 1. 项目概览卡片
        overview_details = (
            f"## 项目类型\n{project_type.get('type', 'unknown')} ({project_type.get('language', 'unknown')})\n\n"
            f"## 目录结构\n- 文件数: {structure.get('total_files', 0)}\n"
            f"- 目录数: {structure.get('total_dirs', 0)}\n"
            f"- 最大深度: {structure.get('max_depth', 0)}\n"
            f"- 顶级目录: {', '.join(structure.get('top_dirs', []))}\n\n"
            f"## 文件类型分布\n"
        )
        for ext, count in list(structure.get("file_types", {}).items())[:10]:
            overview_details += f"- {ext}: {count}\n"

        entry = self.harvester.harvest_from_reference_project(
            title=f"项目概览: {project_name}",
            summary=f"{project_name} 是一个 {project_type.get('type', 'unknown')} 项目",
            details=overview_details,
            tags=[project_type.get("type", "unknown"), project_type.get("language", "unknown")],
            project_path=project_path,
        )
        created_ids.append(entry.id)

        # 2. 命名规范卡片
        naming_details = (
            f"## 命名规范\n"
            f"- 文件命名: {naming.get('file_naming', 'unknown')}\n"
            f"- 目录命名: {naming.get('dir_naming', 'unknown')}\n"
            f"- 类名模式: {naming.get('class_pattern', 'unknown')}\n"
            f"- 函数名模式: {naming.get('function_pattern', 'unknown')}\n\n"
            f"## 示例\n"
            f"- 文件: {', '.join(naming.get('examples', {}).get('files', [])[:5])}\n"
            f"- 类: {', '.join(naming.get('examples', {}).get('classes', [])[:5])}\n"
            f"- 函数: {', '.join(naming.get('examples', {}).get('functions', [])[:5])}\n"
        )
        entry = self.harvester.harvest_from_reference_project(
            title=f"命名规范: {project_name}",
            summary=f"文件: {naming.get('file_naming')}, 类: {naming.get('class_pattern')}",
            details=naming_details,
            tags=["naming", "convention"],
            project_path=project_path,
        )
        created_ids.append(entry.id)

        # 3. 架构模式卡片
        if architecture.get("layer_structure") or architecture.get("patterns_detected"):
            arch_details = "## 架构分层\n"
            for layer in architecture.get("layer_structure", []):
                arch_details += f"- {layer['layer']}: {layer['dir']}/\n"
            arch_details += f"\n## 检测到的模式\n"
            for p in architecture.get("patterns_detected", []):
                arch_details += f"- {p}\n"
            arch_details += f"\n## 状态管理: {architecture.get('state_management', 'unknown')}\n"
            arch_details += f"## 依赖注入: {architecture.get('di_pattern', 'unknown')}\n"

            entry = self.harvester.harvest_from_reference_project(
                title=f"架构模式: {project_name}",
                summary=f"分层: {len(architecture.get('layer_structure', []))} 层, 模式: {', '.join(architecture.get('patterns_detected', [])[:3])}",
                details=arch_details,
                tags=["architecture", "pattern"],
                project_path=project_path,
            )
            created_ids.append(entry.id)

        # 4. 编码风格卡片
        style_details = (
            f"## Lint 配置\n{coding_style.get('lint_config', {})}\n\n"
            f"## 格式化规则\n{coding_style.get('format_rules', {})}\n\n"
            f"## 错误处理模式\n{coding_style.get('error_handling', 'unknown')}\n\n"
            f"## Import 风格\n{coding_style.get('import_style', 'unknown')}\n"
        )
        entry = self.harvester.harvest_from_reference_project(
            title=f"编码风格: {project_name}",
            summary=f"错误处理: {coding_style.get('error_handling', 'unknown')}, Import: {coding_style.get('import_style', 'unknown')}",
            details=style_details,
            tags=["coding-style", "lint"],
            project_path=project_path,
        )
        created_ids.append(entry.id)

        # 5. 依赖管理卡片
        dep_details = (
            f"## 包管理器: {dependencies.get('package_manager', 'unknown')}\n"
            f"## 依赖总数: {dependencies.get('total_dependencies', 0)}\n"
            f"## 版本策略: {dependencies.get('version_strategy', 'unknown')}\n"
            f"## Lock 文件: {'是' if dependencies.get('lock_file') else '否'}\n\n"
            f"## 关键依赖\n"
        )
        for dep in dependencies.get("key_dependencies", [])[:10]:
            dep_details += f"- {dep}\n"

        entry = self.harvester.harvest_from_reference_project(
            title=f"依赖管理: {project_name}",
            summary=f"{dependencies.get('package_manager', 'unknown')}, {dependencies.get('total_dependencies', 0)} 依赖",
            details=dep_details,
            tags=["dependency", "package"],
            project_path=project_path,
        )
        created_ids.append(entry.id)

        # 6. Git 规范卡片
        if git_conventions.get("commit_format") != "unknown":
            git_details = (
                f"## Commit 格式: {git_conventions.get('commit_format', 'unknown')}\n"
                f"## 分支策略: {git_conventions.get('branch_strategy', 'unknown')}\n"
                f"## CI 工具: {git_conventions.get('ci_tool', 'unknown')}\n\n"
                f"## Commit 示例\n"
            )
            for ex in git_conventions.get("commit_examples", []):
                git_details += f"- {ex}\n"

            entry = self.harvester.harvest_from_reference_project(
                title=f"Git 规范: {project_name}",
                summary=f"格式: {git_conventions.get('commit_format')}, 分支: {git_conventions.get('branch_strategy')}",
                details=git_details,
                tags=["git", "convention"],
                project_path=project_path,
            )
            created_ids.append(entry.id)

        return created_ids

    # ── Private Methods ──

    def _detect_lint_config(self, path: Path) -> dict:
        """检测 lint 配置"""
        configs = {}
        lint_files = {
            "analysis_options.yaml": "dart_analyzer",
            ".eslintrc.js": "eslint",
            ".eslintrc.json": "eslint",
            ".eslintrc.yml": "eslint",
            "eslint.config.js": "eslint (flat)",
            ".pylintrc": "pylint",
            "pyproject.toml": "ruff/black",
            ".golangci.yml": "golangci-lint",
            "rustfmt.toml": "rustfmt",
            ".editorconfig": "editorconfig",
        }
        for filename, tool in lint_files.items():
            if (path / filename).exists():
                configs[tool] = filename
        return configs

    def _detect_format_rules(self, path: Path) -> dict:
        """检测格式化规则"""
        rules = {}

        # Prettier
        for prettier_file in [".prettierrc", ".prettierrc.json", ".prettierrc.js", "prettier.config.js"]:
            if (path / prettier_file).exists():
                content = self._read_file_safe(path / prettier_file)
                rules["formatter"] = "prettier"
                if "tabWidth" in content:
                    m = re.search(r'"tabWidth":\s*(\d+)', content)
                    if m:
                        rules["tab_width"] = int(m.group(1))
                break

        # EditorConfig
        editorconfig = path / ".editorconfig"
        if editorconfig.exists():
            content = self._read_file_safe(editorconfig)
            if "indent_size" in content:
                m = re.search(r'indent_size\s*=\s*(\d+)', content)
                if m:
                    rules["indent_size"] = int(m.group(1))
            if "indent_style" in content:
                m = re.search(r'indent_style\s*=\s*(\w+)', content)
                if m:
                    rules["indent_style"] = m.group(1)

        return rules

    def _detect_error_handling(self, path: Path) -> str:
        """检测错误处理模式"""
        patterns = Counter()
        file_count = 0

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for f in files:
                ext = Path(f).suffix.lower()
                if ext in (".py", ".dart", ".js", ".ts", ".java", ".kt", ".go", ".rs"):
                    file_count += 1
                    if file_count > 30:
                        break
                    content = self._read_file_safe(Path(root) / f)
                    if "try" in content and "catch" in content:
                        patterns["try-catch"] += 1
                    if "Result<" in content or "Either<" in content:
                        patterns["Result/Either"] += 1
                    if "async" in content and "await" in content:
                        patterns["async-await"] += 1
                    if "?.let" in content or "??" in content or "?." in content:
                        patterns["null-safety"] += 1
            if file_count > 30:
                break

        if patterns:
            return ", ".join(f"{k} ({v})" for k, v in patterns.most_common(3))
        return "unknown"

    def _detect_import_style(self, path: Path) -> str:
        """检测 import 组织风格"""
        # 采样几个文件检查 import 组织
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for f in files[:5]:
                ext = Path(f).suffix.lower()
                if ext in (".dart", ".py", ".js", ".ts"):
                    content = self._read_file_safe(Path(root) / f)
                    lines = content.split("\n")
                    imports = [l for l in lines if l.startswith("import ") or l.startswith("from ")]
                    if len(imports) >= 3:
                        # 检查是否按组分隔
                        has_blank_between = any(
                            i < len(lines) - 1 and lines[i + 1].strip() == ""
                            for i, l in enumerate(lines) if l.startswith("import ") or l.startswith("from ")
                        )
                        if has_blank_between:
                            return "grouped (blank line separated)"
                        else:
                            return "flat (no grouping)"
            break

        return "unknown"

    def _detect_comment_style(self, path: Path) -> str:
        """检测注释风格"""
        patterns = Counter()
        file_count = 0

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for f in files[:20]:
                ext = Path(f).suffix.lower()
                if ext in (".py", ".dart", ".js", ".ts", ".java", ".kt"):
                    file_count += 1
                    content = self._read_file_safe(Path(root) / f)
                    if "///" in content:
                        patterns["doc-comments (///)"] += 1
                    if '"""' in content:
                        patterns['docstrings (""")'] += 1
                    if "/**" in content:
                        patterns["JSDoc/JavaDoc (/**)"] += 1
                    if "# " in content and ext == ".py":
                        patterns["inline (#)"] += 1
            if file_count > 20:
                break

        if patterns:
            return patterns.most_common(1)[0][0]
        return "unknown"

    @staticmethod
    def _read_file_safe(filepath: Path) -> str:
        """安全读取文件"""
        try:
            if filepath.exists() and filepath.stat().st_size < 100_000:
                return filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            pass
        return ""
