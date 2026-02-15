#!/usr/bin/env python3
"""
dep_sync_check.py — Post-commit 依赖同步检查

提交后自动检查 .agent/ 文件的依赖关系，发现未同步的关联文件时输出警告。
供 post-commit hook 调用，也可独立运行。

行为: 非阻断，任何异常都安全退出。

Usage:
    python .agent/guards/dep_sync_check.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

GUARD_NAME = "Dep Sync"


def find_repo_root() -> Path:
    """通过 git rev-parse 定位仓库根目录"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path.cwd()


def get_committed_agent_files() -> list[str]:
    """获取本次提交中变更的 .agent/ 文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().split("\n")
                if f.startswith(".agent/") and f.strip()]
    except Exception:
        return []


def main() -> int:
    # 1. 检查是否有 .agent/ 文件变更
    agent_files = get_committed_agent_files()
    if not agent_files:
        return 0

    # 2. 定位项目根目录和 evolution 模块
    repo_root = find_repo_root()
    agent_dir = repo_root / ".agent"
    memory_dir = agent_dir / "memory"

    if not agent_dir.exists():
        return 0

    # 3. 导入 DependencyAnalyzer
    sys.path.insert(0, str(agent_dir))
    try:
        from evolution.dependency_analyzer import DependencyAnalyzer
    except ImportError:
        # evolution 模块不可用，静默跳过
        return 0

    # 4. 重建依赖图谱
    da = DependencyAnalyzer(base_dir=str(memory_dir))
    da.build_graph()

    # 5. 运行同步检查
    report = da.sync_check()
    needs_sync = report.get("needs_sync", [])

    # 6. 输出结果
    if needs_sync:
        print(f"⚠️  [{GUARD_NAME}] 检测到 {len(needs_sync)} 个关联文件可能需要同步:")
        for item in needs_sync:
            depth_label = {1: "直接依赖", 2: "二级依赖", 3: "三级依赖"}.get(
                item.get("depth", 1), ""
            )
            print(f"   [{depth_label}] {item.get('file', '?')}")
        print(f"   💡 运行 /sync-check 查看详细报告")
    else:
        print(f"✅ [{GUARD_NAME}] 依赖图谱已更新，{len(agent_files)} 个 Agent 文件同步状态正常")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # 任何异常都不阻断 git 操作
        sys.exit(0)
