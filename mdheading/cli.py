"""命令行参数解析与主流程控制"""

import argparse
import sys
import os
import tempfile
import shutil
from pathlib import Path
from .processor import MarkdownHeadingProcessor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mdheading",
        description="调整 Markdown 文件中所有标题的相对等级",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help="输入的 Markdown 文件路径",
    )
    parser.add_argument(
        "-t", "--target-level",
        type=int,
        choices=range(1, 7),
        default=1,
        metavar="LEVEL",
        help="目标最高标题等级 (1-6)，默认为 1",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="当降级导致标题等级超过 6 级时，将其转为加粗正文",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        metavar="OUTPUT",
        help="输出文件路径，默认覆盖输入文件",
    )
    parser.add_argument(
        "-b", "--backup",
        default=None,
        metavar="SUFFIX",
        help="覆盖原文件前创建备份，使用指定后缀（如 .bak）",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="仅显示将修改的内容，不实际写入文件",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"错误：文件 '{input_path}' 不存在或不是普通文件", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"错误：无法读取文件 '{input_path}'：{e}", file=sys.stderr)
        sys.exit(1)

    # 处理
    processor = MarkdownHeadingProcessor(content)
    new_content, errors = processor.adjust(args.target_level, args.force)

    if errors:
        print("错误：标题等级越界：", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)

    if not processor.headings:
        print("文件中未检测到任何标题，无需处理。")
        sys.exit(0)

    # 判断是否真的发生变化（无偏移）
    if new_content == content:
        print("标题等级无需调整（偏移量为0），未修改文件。")
        sys.exit(0)

    # 输出处理
    output_path = Path(args.output) if args.output else input_path

    # dry-run 模式：显示 diff（简单形式）
    if args.dry_run:
        old_lines = content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        print("--- 将要进行的修改 (dry-run) ---")
        for i, (old, new) in enumerate(zip(old_lines, new_lines)):
            if old != new:
                print(f"行 {i+1}:")
                print(f"- {old.rstrip()}")
                print(f"+ {new.rstrip()}")
        print("-------------------------------")
        sys.exit(0)

    # 安全写入
    if args.backup and not args.output:
        # 仅当覆盖原文件且指定备份时创建备份
        backup_path = input_path.with_suffix(input_path.suffix + args.backup)
        shutil.copy2(input_path, backup_path)
        print(f"已创建备份：{backup_path}")

    # 写入临时文件，然后原子替换
    try:
        # 默认输出到原文件或指定文件，统一使用临时文件保证安全
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=output_path.parent,
            prefix="tmp_mdheading_"
        ) as tmp:
            tmp.write(new_content)
            temp_name = tmp.name
        shutil.move(temp_name, output_path)
        print(f"成功更新文件：{output_path}")
    except OSError as e:
        print(f"错误：写入文件失败：{e}", file=sys.stderr)
        # 清理可能残留的临时文件
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        sys.exit(1)