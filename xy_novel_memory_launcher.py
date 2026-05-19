"""
MCP 启动器 —— 自动根据当前项目根目录选择数据库，
然后启动真正的 MCP 服务器 xy_novel_memory.py。
"""

import os
import sys
from pathlib import Path

def find_project_root(start: Path) -> Path:
    """向上查找第一个包含 .reasonix 的目录作为项目根目录"""
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / ".reasonix").is_dir():
            return p
    raise RuntimeError(
        f"❌ 无法在 {start} 及其父目录中找到 .reasonix 项目目录。"
        f"请确保在 Reasonix 项目内运行。"
    )

def main():
    # 1. 找到当前项目根目录（假设 Reasonix 启动 MCP 时的 cwd 就是项目目录）
    try:
        project_root = find_project_root(Path.cwd())
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    # 2. 构建该项目专属的数据库路径
    db_path = project_root / ".reasonix" / "memory" / "novel1.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 3. 启动真正的 MCP 服务器，替换当前进程
    server_script = Path(__file__).parent / "xy_novel_memory.py"
    os.execv(
        sys.executable,
        [
            sys.executable,
            str(server_script),
            "--db",
            str(db_path),
        ],
    )

if __name__ == "__main__":
    main()
    