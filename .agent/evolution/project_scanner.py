"""
Project Scanner — 项目扫描器

扫描参考项目结构、检测项目类型、提取命名规范和架构模式:
  - 检测项目类型 (Flutter/React/Python/Go/Rust/Java)
  - 扫描目录结构 (层级组织、文件数量分布)
  - 提取命名规范 (文件命名、类名、变量名模式)
  - 提取架构模式 (分层结构、依赖注入、状态管理)

Usage:
    from evolution.project_scanner import ProjectScanner
    ps = ProjectScanner()
    result = ps.scan_structure("/path/to/project")
    project_type = ps.detect_project_type("/path/to/project")
"""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path
from typing import Optional


# 项目类型检测规则
PROJECT_TYPE_MARKERS = {
    "flutter": ["pubspec.yaml"],
    "react": ["package.json"],      # 需要进一步检查 react 依赖
    "vue": ["package.json"],         # 需要进一步检查 vue 依赖
    "python": ["pyproject.toml", "setup.py", "requirements.txt"],
    "go": ["go.mod"],
    "rust": ["Cargo.toml"],
    "java": ["pom.xml", "build.gradle"],
    "kotlin": ["build.gradle.kts"],
}

# 忽略的目录
IGNORE_DIRS = {
    ".git", ".svn", "node_modules", "__pycache__", ".dart_tool",
    "build", "dist", ".next", ".nuxt", "target", "vendor",
    ".idea", ".vscode", ".gradle", ".pub-cache", "coverage",
    ".agent", ".gemini",
}

# 文件采样上限
MAX_SCAN_FILES = 1000


class ProjectScanner:
    """
    项目扫描器。

    职责:
    1. 检测项目类型
    2. 扫描目录结构
    3. 提取命名规范
    4. 提取架构模式
    """

    # ── Public API ──

    def detect_project_type(self, project_path: str | Path) -> dict:
        """
        检测项目类型。

        Returns
        -------
        dict
            {
                "type": str,           # flutter | react | vue | python | go | rust | java | kotlin | unknown
                "markers_found": list, # 发现的标志文件
                "confidence": float,   # 检测置信度
                "language": str,       # 主语言
            }
        """
        path = Path(project_path)
        if not path.exists():
            return {"type": "unknown", "markers_found": [], "confidence": 0.0, "language": "unknown"}

        markers_found = []
        detected_type = "unknown"
        confidence = 0.0
        language = "unknown"

        # 检查标志文件
        for ptype, markers in PROJECT_TYPE_MARKERS.items():
            for marker in markers:
                if (path / marker).exists():
                    markers_found.append(marker)

        # Flutter/Dart
        if "pubspec.yaml" in markers_found:
            detected_type = "flutter"
            language = "dart"
            confidence = 0.95

        # React/Vue (需要检查 package.json 内容)
        elif "package.json" in markers_found:
            pkg_content = self._read_file_safe(path / "package.json")
            if '"react"' in pkg_content or '"react-dom"' in pkg_content:
                detected_type = "react"
                language = "javascript/typescript"
                confidence = 0.9
            elif '"vue"' in pkg_content:
                detected_type = "vue"
                language = "javascript/typescript"
                confidence = 0.9
            else:
                detected_type = "node"
                language = "javascript/typescript"
                confidence = 0.7

        # Python
        elif any(m in markers_found for m in ["pyproject.toml", "setup.py", "requirements.txt"]):
            detected_type = "python"
            language = "python"
            confidence = 0.9

        # Go
        elif "go.mod" in markers_found:
            detected_type = "go"
            language = "go"
            confidence = 0.95

        # Rust
        elif "Cargo.toml" in markers_found:
            detected_type = "rust"
            language = "rust"
            confidence = 0.95

        # Java/Kotlin
        elif "pom.xml" in markers_found or "build.gradle" in markers_found:
            if "build.gradle.kts" in markers_found:
                detected_type = "kotlin"
                language = "kotlin"
            else:
                detected_type = "java"
                language = "java"
            confidence = 0.9

        return {
            "type": detected_type,
            "markers_found": markers_found,
            "confidence": confidence,
            "language": language,
        }

    def scan_structure(self, project_path: str | Path) -> dict:
        """
        扫描目录结构。

        Returns
        -------
        dict
            {
                "total_files": int,
                "total_dirs": int,
                "max_depth": int,
                "file_types": dict,     # {extension: count}
                "top_dirs": list,       # 顶级目录列表
                "dir_tree": dict,       # 简化的目录树
                "large_dirs": list,     # 文件数 > 50 的目录
            }
        """
        path = Path(project_path)
        if not path.exists():
            return {"total_files": 0, "total_dirs": 0, "max_depth": 0,
                    "file_types": {}, "top_dirs": [], "dir_tree": {}, "large_dirs": []}

        total_files = 0
        total_dirs = 0
        max_depth = 0
        file_types = Counter()
        dir_file_counts = Counter()
        top_dirs = []

        # 收集顶级目录
        for item in sorted(path.iterdir()):
            if item.is_dir() and item.name not in IGNORE_DIRS:
                top_dirs.append(item.name)

        # 扫描文件 (限制上限)
        for root, dirs, files in os.walk(path):
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            rel_root = os.path.relpath(root, path)
            depth = rel_root.count(os.sep) + 1 if rel_root != "." else 0
            max_depth = max(max_depth, depth)

            total_dirs += 1
            dir_file_counts[rel_root] = len(files)

            for f in files:
                total_files += 1
                ext = Path(f).suffix.lower()
                if ext:
                    file_types[ext] += 1

                if total_files >= MAX_SCAN_FILES:
                    break
            if total_files >= MAX_SCAN_FILES:
                break

        # 找出文件数较多的目录
        large_dirs = [
            {"dir": d, "file_count": c}
            for d, c in dir_file_counts.most_common(10)
            if c > 20
        ]

        return {
            "total_files": total_files,
            "total_dirs": total_dirs,
            "max_depth": max_depth,
            "file_types": dict(file_types.most_common(20)),
            "top_dirs": top_dirs,
            "large_dirs": large_dirs,
        }

    def extract_naming_conventions(self, project_path: str | Path) -> dict:
        """
        提取命名规范。

        Returns
        -------
        dict
            {
                "file_naming": str,        # snake_case | camelCase | kebab-case | PascalCase
                "dir_naming": str,
                "class_pattern": str,      # 从代码中提取的类名模式
                "function_pattern": str,   # 函数名模式
                "examples": dict,
            }
        """
        path = Path(project_path)
        file_names = []
        dir_names = []
        class_names = []
        function_names = []

        file_count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for d in dirs:
                dir_names.append(d)
            for f in files:
                stem = Path(f).stem
                if stem and not stem.startswith("."):
                    file_names.append(stem)

                # 采样读取代码文件提取类名/函数名
                ext = Path(f).suffix.lower()
                if ext in (".py", ".dart", ".js", ".ts", ".java", ".kt", ".go", ".rs"):
                    file_count += 1
                    if file_count <= 50:  # 采样 50 个文件
                        content = self._read_file_safe(Path(root) / f)
                        class_names.extend(re.findall(r'class\s+(\w+)', content))
                        function_names.extend(re.findall(r'(?:def|func|function|fn)\s+(\w+)', content))

            if file_count >= MAX_SCAN_FILES:
                break

        return {
            "file_naming": self._detect_naming_style(file_names),
            "dir_naming": self._detect_naming_style(dir_names),
            "class_pattern": self._detect_naming_style(class_names) if class_names else "PascalCase",
            "function_pattern": self._detect_naming_style(function_names) if function_names else "unknown",
            "examples": {
                "files": file_names[:10],
                "dirs": dir_names[:10],
                "classes": class_names[:10],
                "functions": function_names[:10],
            },
        }

    def extract_architecture_patterns(self, project_path: str | Path) -> dict:
        """
        提取架构模式。

        Returns
        -------
        dict
            {
                "layer_structure": list,    # 检测到的分层 (ui, domain, data, ...)
                "patterns_detected": list,  # 检测到的设计模式
                "state_management": str,    # 状态管理方案
                "di_pattern": str,          # 依赖注入模式
                "test_structure": dict,     # 测试组织
            }
        """
        path = Path(project_path)
        top_dirs = [d.name.lower() for d in path.iterdir()
                    if d.is_dir() and d.name not in IGNORE_DIRS]

        # 检测分层结构
        layer_keywords = {
            "ui": ["ui", "views", "pages", "screens", "components", "widgets"],
            "domain": ["domain", "models", "entities", "usecases", "use_cases"],
            "data": ["data", "repositories", "services", "api", "network", "db"],
            "core": ["core", "common", "shared", "utils", "helpers"],
            "config": ["config", "settings", "constants"],
        }

        layers = []
        for layer, keywords in layer_keywords.items():
            for kw in keywords:
                if kw in top_dirs:
                    layers.append({"layer": layer, "dir": kw})
                    break

        # 检测状态管理
        state_mgmt = self._detect_state_management(path)

        # 检测依赖注入
        di_pattern = self._detect_di_pattern(path)

        # 检测设计模式
        patterns = self._detect_design_patterns(path)

        # 测试结构
        test_dirs = [d for d in top_dirs if "test" in d]
        test_structure = {
            "test_dirs": test_dirs,
            "has_unit_tests": any("unit" in d for d in test_dirs) or "test" in top_dirs,
            "has_integration_tests": any("integration" in d for d in test_dirs),
            "has_e2e_tests": any("e2e" in d for d in test_dirs),
        }

        return {
            "layer_structure": layers,
            "patterns_detected": patterns,
            "state_management": state_mgmt,
            "di_pattern": di_pattern,
            "test_structure": test_structure,
        }

    # ── Private Methods ──

    def _detect_naming_style(self, names: list[str]) -> str:
        """检测命名风格"""
        if not names:
            return "unknown"

        styles = Counter()
        for name in names:
            if "_" in name and name == name.lower():
                styles["snake_case"] += 1
            elif "-" in name:
                styles["kebab-case"] += 1
            elif name[0].isupper() and not "_" in name:
                styles["PascalCase"] += 1
            elif name[0].islower() and any(c.isupper() for c in name):
                styles["camelCase"] += 1
            else:
                styles["other"] += 1

        if styles:
            return styles.most_common(1)[0][0]
        return "unknown"

    def _detect_state_management(self, path: Path) -> str:
        """检测状态管理方案"""
        pkg_files = ["pubspec.yaml", "package.json", "requirements.txt", "Cargo.toml", "go.mod"]
        for pkg_file in pkg_files:
            content = self._read_file_safe(path / pkg_file)
            if not content:
                continue

            # Flutter/Dart
            if "stacked" in content.lower():
                return "Stacked (MVVM)"
            if "riverpod" in content.lower():
                return "Riverpod"
            if "flutter_bloc" in content.lower() or "bloc:" in content.lower():
                return "BLoC"
            if "provider:" in content.lower():
                return "Provider"
            if "getx" in content.lower() or "get:" in content.lower():
                return "GetX"

            # React
            if "redux" in content.lower():
                return "Redux"
            if "zustand" in content.lower():
                return "Zustand"
            if "recoil" in content.lower():
                return "Recoil"
            if "mobx" in content.lower():
                return "MobX"

            # Vue
            if "vuex" in content.lower():
                return "Vuex"
            if "pinia" in content.lower():
                return "Pinia"

        return "unknown"

    def _detect_di_pattern(self, path: Path) -> str:
        """检测依赖注入模式"""
        content = ""
        for pkg_file in ["pubspec.yaml", "package.json", "build.gradle"]:
            content += self._read_file_safe(path / pkg_file)

        if "get_it" in content or "injectable" in content:
            return "get_it + injectable"
        if "inversify" in content:
            return "InversifyJS"
        if "dagger" in content.lower() or "hilt" in content.lower():
            return "Dagger/Hilt"
        if "spring" in content.lower():
            return "Spring DI"

        return "unknown"

    def _detect_design_patterns(self, path: Path) -> list[str]:
        """检测常见设计模式"""
        patterns = []
        top_dirs = [d.name.lower() for d in path.iterdir()
                    if d.is_dir() and d.name not in IGNORE_DIRS]

        if "repositories" in top_dirs or "repository" in top_dirs:
            patterns.append("Repository Pattern")
        if "services" in top_dirs or "service" in top_dirs:
            patterns.append("Service Layer")
        if "viewmodels" in top_dirs or "view_models" in top_dirs:
            patterns.append("MVVM")
        if "controllers" in top_dirs or "controller" in top_dirs:
            patterns.append("MVC/Controller")
        if "usecases" in top_dirs or "use_cases" in top_dirs:
            patterns.append("Clean Architecture (Use Cases)")
        if "bloc" in top_dirs or "blocs" in top_dirs:
            patterns.append("BLoC Pattern")
        if "middleware" in top_dirs:
            patterns.append("Middleware Pattern")
        if "factories" in top_dirs or "factory" in top_dirs:
            patterns.append("Factory Pattern")

        return patterns

    @staticmethod
    def _read_file_safe(filepath: Path) -> str:
        """安全读取文件内容"""
        try:
            if filepath.exists() and filepath.stat().st_size < 100_000:
                return filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            pass
        return ""
