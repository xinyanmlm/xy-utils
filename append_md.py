"""
Markdown 文件合并工具
- 双文件模式：将 B.md 追加到 A.md 末尾（直接修改 A）
- 目录模式  ：按文件名排序，合并目录下所有 .md 至新文件
用法:
  python append_md.py A.md B.md
  python append_md.py --dir <目录> [-o 输出文件] [--main-only] [--filter 正则]

新选项：
  --main-only   只合并主章节文件（如 chapter-001.md），排除状态/后缀文件
  --filter      自定义正则过滤文件名（与 --main-only 互斥）

修复内容：
  1. 目录模式排序采用自然顺序（按章节号升序，同章节主文件在前）
  2. 被合并文件若无标题（首行非#开头），自动插入 `# 文件名` 作为标题
  3. 支持过滤文件（--main-only 或 --filter）
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


def sort_key(file_path: Path):
    """
    自定义排序键，用于文件名如 'chapter-001.md', 'chapter-001-status.md' 的自然排序。
    提取数字部分，主文件优先，其余按后缀排序；不符合规则的文件排在最后。
    """
    name = file_path.stem  # 去掉扩展名
    match = re.match(r"chapter-(\d+)", name)
    if match:
        num = int(match.group(1))
        suffix = name[match.end():]   # 剩余部分，例如 "-status" 或 ""
        is_main = (suffix == "")
        # 元组：(数字, 是否非主文件, 后缀) -> 数字升序，主文件(False)优先，后缀按字母序
        return (num, not is_main, suffix)
    else:
        # 不匹配的文件（如 README）放在最后
        return (float('inf'), False, name)


def ensure_title(content: str, file_stem: str) -> str:
    """
    如果内容不以 # 开头（不计前导空白），则在最前面添加 `# file_stem` 作为标题。
    否则保持原样。
    """
    stripped = content.lstrip()
    if stripped and stripped[0] == '#':
        # 已有标题，不做修改
        return content
    else:
        title_line = f"# {file_stem}\n"
        # 保留原始内容（可能为空或带空白）
        return title_line + (content if content else "")


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

    # ---- 检查并补全标题 ----
    content_b = ensure_title(content_b, Path(file_b).stem)

    try:
        with open(file_a, 'a', encoding='utf-8') as fa:
            fa.write('\n')
            fa.write(content_b)
    except Exception as e:
        print(f"写入 {file_a} 失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"已将 {file_b} 的内容追加到 {file_a} 末尾。")


def merge_directory(dir_path: str, output_path: str = None,
                    main_only: bool = False, pattern: str = None) -> None:
    """目录合并模式：按文件名排序合并目录下所有 .md 文件，支持过滤"""
    base_dir = Path(dir_path)
    if not base_dir.is_dir():
        print(f"错误：目录不存在 - {base_dir}", file=sys.stderr)
        sys.exit(1)

    # 获取所有 .md 文件
    all_files = list(base_dir.glob('*.md'))
    if not all_files:
        print(f"警告：目录 {base_dir} 中没有找到 .md 文件", file=sys.stderr)
        return

    # ---- 新增过滤逻辑 ----
    if main_only:
        # 只保留主章节文件：chapter-数字.md（数字后无额外后缀）
        regex = re.compile(r'^chapter-\d+\.md$')
        filtered = [f for f in all_files if regex.match(f.name)]
    elif pattern:
        # 用户自定义正则过滤文件名
        try:
            regex = re.compile(pattern)
        except re.error as e:
            print(f"错误：无效的正则表达式 '{pattern}': {e}", file=sys.stderr)
            sys.exit(1)
        filtered = [f for f in all_files if regex.match(f.name)]
    else:
        # 默认不过滤，保留所有
        filtered = all_files

    if not filtered:
        print(f"警告：过滤后没有 .md 文件被匹配", file=sys.stderr)
        return

    # 对过滤后的文件进行自然排序
    md_files = sorted(filtered, key=sort_key)

    # 输出路径处理
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path.cwd() / f"merged_{timestamp}.md"
    else:
        output_path = Path(output_path)

    # 执行合并
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for i, md_file in enumerate(md_files):
                try:
                    content = md_file.read_text(encoding='utf-8')
                except Exception as e:
                    print(f"警告：读取 {md_file.name} 失败: {e}，已跳过", file=sys.stderr)
                    continue

                # 补全标题
                content = ensure_title(content, md_file.stem)

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
    parser.add_argument('--dir', metavar='DIRECTORY', help='合并目录下所有 .md 文件')
    parser.add_argument('-o', '--output', metavar='OUTPUT', help='输出文件路径（仅目录模式，默认 merged_时间戳.md）')

    # 新增过滤选项
    parser.add_argument('--main-only', action='store_true',
                        help='仅合并主章节文件（如 chapter-001.md），排除带后缀的文件')
    parser.add_argument('--filter', metavar='REGEX',
                        help='正则表达式过滤文件名（仅目录模式，与 --main-only 互斥）')

    args = parser.parse_args()

    # 参数验证
    if args.dir:
        if args.files:
            print("错误：--dir 模式下不能同时提供文件参数", file=sys.stderr)
            sys.exit(1)
        if args.main_only and args.filter:
            print("错误：--main-only 与 --filter 不能同时使用", file=sys.stderr)
            sys.exit(1)
        merge_directory(args.dir, args.output, main_only=args.main_only, pattern=args.filter)
    else:
        if args.files and len(args.files) != 2:
            print("错误：请提供两个文件路径，或使用 --dir 指定目录", file=sys.stderr)
            parser.print_usage()
            sys.exit(1)
        # 单文件或零文件也报错
        if len(args.files) != 2:
            print("错误：请提供两个文件路径，或使用 --dir 指定目录", file=sys.stderr)
            sys.exit(1)
        # 忽略目录模式下的过滤参数
        if args.main_only or args.filter:
            print("警告：--main-only 和 --filter 仅在 --dir 模式下生效，已忽略", file=sys.stderr)
        append_file(args.files[0], args.files[1])


if __name__ == "__main__":
    main()