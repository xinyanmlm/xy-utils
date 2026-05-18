#!/usr/bin/env python3
"""
处理 Cherry Studio 导出的聊天记录 Markdown 文件：
- 删除用户发送的内容（## 🧑‍💻 User 及其后续内容）
- 删除 AI 回复的标记行（## 🤖 Assistant），但保留 AI 回复正文
- 可选通过 --to epub 调用 pandoc.exe 生成 ePub 3 电子书
- 输出文件命名格式：原文件名-整合版-时间戳.md
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import re


def process_chat_md(input_path: Path, output_dir: Path = None) -> Path:
    """
    读取输入的 Markdown 文件，按规则处理，写入新文件，返回输出文件路径。
    """
    if output_dir is None:
        output_dir = input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = input_path.stem
    output_name = f"{stem}-整合版-{timestamp}.md"
    output_path = output_dir / output_name

    # 状态机：normal, user, assistant
    state = "normal"
    user_pattern = re.compile(r'^##\s+🧑‍💻\s+User\s*$')
    assistant_pattern = re.compile(r'^##\s+🤖\s+Assistant\s*$')
    separator = '---'

    with (
        open(input_path, 'r', encoding='utf-8', newline='') as infile,
        open(output_path, 'w', encoding='utf-8', newline='') as outfile,
    ):
        for raw_line in infile:
            line = raw_line.rstrip('\n\r')

            if state == "normal":
                if user_pattern.match(line):
                    state = "user"
                elif assistant_pattern.match(line):
                    state = "assistant"
                else:
                    outfile.write(raw_line)

            elif state == "user":
                if assistant_pattern.match(line):
                    state = "assistant"
                elif line.strip() == separator:
                    outfile.write(raw_line)
                    state = "normal"
                # 用户消息行均跳过

            elif state == "assistant":
                if user_pattern.match(line):
                    state = "user"
                elif assistant_pattern.match(line):
                    pass  # 忽略重复的 Assistant 标记
                else:
                    outfile.write(raw_line)

    return output_path


def convert_to_epub(md_path: Path) -> Path:
    """
    使用 pandoc.exe 将给定的 Markdown 文件转换为 ePub 3，返回生成的 .epub 路径。
    """
    # 检查 pandoc 是否可用
    pandoc = "pandoc.exe"
    if not shutil.which(pandoc):
        raise RuntimeError(f"未找到 {pandoc}，请确认已安装 Pandoc 并加入 PATH。")

    epub_path = md_path.with_suffix(".epub")
    cmd = [
        pandoc,
        str(md_path),
        "-o", str(epub_path),
        "--to", "epub3"
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc 转换失败：{e.stderr.strip()}") from e

    return epub_path


def main():
    parser = argparse.ArgumentParser(
        description="处理 Cherry Studio 聊天记录 Markdown 文件，删除用户内容和助手标记。"
    )
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="输出目录，默认为输入文件所在目录"
    )
    parser.add_argument(
        "--to",
        choices=["epub"],
        default=None,
        help="附加输出格式，当前仅支持 epub"
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"错误：文件不存在 - {input_path}", file=sys.stderr)
        raise SystemExit(1)

    output_dir = Path(args.output_dir) if args.output_dir else None

    try:
        md_out = process_chat_md(input_path, output_dir)
        print(f"已生成整合文件：{md_out}")

        if args.to == "epub":
            epub_out = convert_to_epub(md_out)
            print(f"已生成 ePub 文件：{epub_out}")

    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()