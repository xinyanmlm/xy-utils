"""
将 B.md 的内容追加到 A.md 的末尾（新行后追加）。
用法: python append_md.py A.md B.md
"""

import sys
import os


def append_file(file_a: str, file_b: str) -> None:
    """将 file_b 的内容追加到 file_a 末尾，追加前强制换新行。"""
    # 检查文件是否存在
    for fpath in (file_a, file_b):
        if not os.path.isfile(fpath):
            print(f"错误：文件不存在 - {fpath}", file=sys.stderr)
            sys.exit(1)

    # 读取 B 的内容
    try:
        with open(file_b, 'r', encoding='utf-8') as fb:
            content_b = fb.read()
    except Exception as e:
        print(f"读取 {file_b} 失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 追加到 A 的末尾
    try:
        with open(file_a, 'a', encoding='utf-8') as fa:
            fa.write('\n')
            fa.write(content_b)
    except Exception as e:
        print(f"写入 {file_a} 失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"已将 {file_b} 的内容追加到 {file_a} 末尾。")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python append_md.py A.md B.md", file=sys.stderr)
        sys.exit(1)
    append_file(sys.argv[1], sys.argv[2])