"""
处理 Cherry Studio 导出的聊天记录 Markdown 文件：
- 删除用户发送的内容（## 🧑‍💻 User 及其后续内容）
- 删除 AI 回复的标记行（## 🤖 Assistant），但保留 AI 回复正文
- 输出文件命名格式：原文件名-整合版-时间戳.md
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


def process_chat_md(input_path: str, output_dir: str = None):
    """
    读取输入的 Markdown 文件，按规则处理，写入新文件。

    Args:
        input_path: 输入文件路径
        output_dir: 输出目录，默认为输入文件所在目录
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = input_path.stem
    output_name = f"{stem}-整合版-{timestamp}.md"

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_name
    else:
        output_path = input_path.parent / output_name

    # 状态机：normal, user, assistant
    state = "normal"

    # 预编译匹配模式
    user_pattern = re.compile(r'^##\s+🧑‍💻\s+User\s*$')
    assistant_pattern = re.compile(r'^##\s+🤖\s+Assistant\s*$')
    separator = '---'

    with (
        open(input_path, 'r', encoding='utf-8', newline='') as infile,
        open(output_path, 'w', encoding='utf-8', newline='') as outfile,
    ):
        for raw_line in infile:
            line = raw_line.rstrip('\n\r')  # 保留原格式判断，写回时添加原行尾

            if state == "normal":
                if user_pattern.match(line):
                    state = "user"
                elif assistant_pattern.match(line):
                    state = "assistant"
                else:
                    outfile.write(raw_line)

            elif state == "user":
                # 删除所有用户内容，直到遇到 --- 或 ## 🤖 Assistant
                if user_pattern.match(line):
                    # 仍然是用户标记，保持状态（理论上不会嵌套）
                    pass
                elif assistant_pattern.match(line):
                    # 直接进入助手状态，不输出此行
                    state = "assistant"
                elif line.strip() == separator:
                    # 分隔线，保留并回到普通状态
                    outfile.write(raw_line)
                    state = "normal"
                # 其余内容均为用户消息，跳过

            elif state == "assistant":
                if user_pattern.match(line):
                    state = "user"
                elif assistant_pattern.match(line):
                    # 遇到新的助手标记，保持助手状态但不输出此行
                    pass
                else:
                    outfile.write(raw_line)

    print(f"处理完成，输出文件：{output_path}")


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
    args = parser.parse_args()

    try:
        process_chat_md(args.input, args.output_dir)
    except Exception as e:
        print(f"错误：{e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()