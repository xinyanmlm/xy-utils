"""
Markdown 文件合并工具
- 双文件模式：将 B.md 追加到 A.md 末尾（直接修改 A）
- 目录模式  ：按文件名排序，合并目录下所有 .md 至新文件
用法:
  python append_md.py A.md B.md
  python append_md.py --dir <目录> [-o 输出文件]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def append_file(file_a: str, file_b: str) -> None:
    """双文件追加模式：将 file_b 的内容追加到 file_a 末尾（新行后追加）"""
    for fpath in (file_a, file_b):
        if not Path(fpath).is_file():
            print(f"错误：文件不存在 - {fpath}", file=sys.stderr)
            sys.exit(1)

    try:
        content_b = Path(file_b).read_text(encoding='utf-8')
    except Exception as e:
        print(f"读取 {file_b} 失败: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_a, 'a', encoding='utf-8') as fa:
            fa.write('\n')
            fa.write(content_b)
    except Exception as e:
        print(f"写入 {file_a} 失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"已将 {file_b} 的内容追加到 {file_a} 末尾。")


def merge_directory(dir_path: str, output_path: str = None) -> None:
    """目录合并模式：按文件名排序合并目录下所有 .md 文件"""
    base_dir = Path(dir_path)
    if not base_dir.is_dir():
        print(f"错误：目录不存在 - {base_dir}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(base_dir.glob('*.md'))
    if not md_files:
        print(f"警告：目录 {base_dir} 中没有找到 .md 文件", file=sys.stderr)
        return

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path.cwd() / f"merged_{timestamp}.md"
    else:
        output_path = Path(output_path)

    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for i, md_file in enumerate(md_files):
                try:
                    content = md_file.read_text(encoding='utf-8')
                except Exception as e:
                    print(f"警告：读取 {md_file.name} 失败: {e}，已跳过", file=sys.stderr)
                    continue
                if i > 0:
                    outfile.write('\n')   # 文件之间加空行分隔
                outfile.write(content)
        print(f"已合并 {len(md_files)} 个文件 → {output_path}")
    except Exception as e:
        print(f"写入输出文件失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Markdown 文件合并工具")
    parser.add_argument('files', nargs='*', help='两个文件路径（旧模式：A.md B.md）')
    parser.add_argument('--dir', metavar='DIRECTORY', help='合并目录下所有 .md 文件（新模式）')
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='输出文件路径（仅目录模式有效，默认 merged_时间戳.md）')
    args = parser.parse_args()

    if args.dir:
        if args.files:
            print("错误：--dir 模式下不能同时提供文件参数", file=sys.stderr)
            sys.exit(1)
        merge_directory(args.dir, args.output)
    else:
        if len(args.files) != 2:
            print("错误：请提供两个文件路径，或使用 --dir 指定目录", file=sys.stderr)
            parser.print_usage()
            sys.exit(1)
        append_file(args.files[0], args.files[1])


if __name__ == "__main__":
    main()