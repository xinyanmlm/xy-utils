# xy_novel_memory_launcher.py
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent
SERVER_SCRIPT = TOOL_DIR / "xy_novel_memory.py"
DEFAULT_DB_NAME = "novel1.db"


def find_project_root(explicit: str | None = None) -> Path:
    """
    优先级：
    1) --project-root 显式指定
    2) 环境变量 REASONIX_PROJECT_ROOT
    3) 当前工作目录及父目录中查找 .reasonix
    """

    if explicit:
        root = Path(explicit).expanduser().resolve()
        if (root / ".reasonix").exists():
            return root
        raise RuntimeError(f"指定的项目根目录不存在 .reasonix：{root}")

    env_root = os.environ.get("REASONIX_PROJECT_ROOT")
    if env_root:
        root = Path(env_root).expanduser().resolve()
        if (root / ".reasonix").exists():
            return root
        raise RuntimeError(f"环境变量 REASONIX_PROJECT_ROOT 指向的目录不存在 .reasonix：{root}")

    cwd = Path.cwd().resolve()

    if (cwd / ".reasonix").exists():
        return cwd

    for parent in [cwd, *cwd.parents]:
        if (parent / ".reasonix").exists():
            return parent

    raise RuntimeError(
        "无法定位 Reasonix 项目根目录。"
        "请设置 REASONIX_PROJECT_ROOT，或通过 --project-root 传入项目根目录。"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reasonix 小说 MCP 启动器")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Reasonix 项目根目录，例如 F:/books/AI所闻/01",
    )
    parser.add_argument(
        "--db-name",
        default=DEFAULT_DB_NAME,
        help="数据库文件名，默认 novel1.db",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="直接指定数据库完整路径；指定后会覆盖 --project-root / --db-name",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.db:
        db_path = Path(args.db).expanduser().resolve()
    else:
        project_root = find_project_root(args.project_root)
        db_path = project_root / ".reasonix" / "memory" / args.db_name

    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not SERVER_SCRIPT.exists():
        raise FileNotFoundError(f"找不到服务器脚本：{SERVER_SCRIPT}")

    print(f"[xy_novel_memory_launcher] DB = {db_path}", file=sys.stderr)

    os.execv(
        sys.executable,
        [
            sys.executable,
            str(SERVER_SCRIPT),
            "--db",
            str(db_path),
        ],
    )


if __name__ == "__main__":
    main()