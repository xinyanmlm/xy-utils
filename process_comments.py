# -*- coding: utf-8 -*-
"""
B站评论数据格式转换脚本

功能：为各行添加前缀标签，删除"点击前往"行，支持评论多行和缺失行。

输入格式（每个记录）：
  视频标题
  UP主名
  评论内容（可能多行多段）
  点赞数（纯数字）
  回复数（纯数字）
  时间
  BV号
  点击前往（可能缺失，会被删除）

输出格式（每个记录）：
  视频：{标题}
  up主：{UP主名}
  评论：{评论第一行}
  {评论剩余行}
  点赞此评论数：{点赞数}
  回复此评论数：{回复数}
  时间：{时间}
  视频bv号：{BV号}
"""

import argparse


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    output_lines = []
    i = 0
    n = len(lines)
    record_count = 0

    while i < n:
        line = lines[i].strip()

        # 跳过文件末尾的空行
        if line == '' and i == n - 1:
            i += 1
            continue

        # 记录之间添加空行（第一个记录前不加）
        if record_count > 0:
            output_lines.append('')
        record_count += 1

        # 1. 视频标题行
        output_lines.append(f'视频：{lines[i]}')
        i += 1
        if i >= n:
            break

        # 2. UP主行
        output_lines.append(f'up主：{lines[i]}')
        i += 1
        if i >= n:
            break

        # 3. 评论内容（可能多行，直到遇到纯数字行为止）
        comment_lines = []
        while i < n:
            current = lines[i].strip()
            # 如果当前行是纯数字，说明是点赞数，评论结束
            if current.isdigit():
                break
            comment_lines.append(lines[i])
            i += 1

        if comment_lines:
            output_lines.append(f'评论：{comment_lines[0]}')
            for cl in comment_lines[1:]:
                output_lines.append(cl)

        if i >= n:
            break

        # 4. 点赞数
        output_lines.append(f'点赞此评论数：{lines[i]}')
        i += 1
        if i >= n:
            break

        # 5. 回复数
        output_lines.append(f'回复此评论数：{lines[i]}')
        i += 1
        if i >= n:
            break

        # 6. 时间
        output_lines.append(f'时间：{lines[i]}')
        i += 1
        if i >= n:
            break

        # 7. BV号
        output_lines.append(f'视频bv号：{lines[i]}')
        i += 1
        if i >= n:
            break

        # 8. 如果存在"点击前往"则跳过（删除）
        if lines[i].strip() == '点击前往':
            i += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
        f.write('\n')

    print(f'处理完成，已保存至：{output_path}')


def main():
    parser = argparse.ArgumentParser(
        description='B站评论数据格式转换工具：为各行添加前缀标签，删除"点击前往"行，支持评论多行和缺失行。',
        epilog='示例：python process_comments.py input.txt output.txt',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='输入文件路径（UTF-8编码）')
    parser.add_argument('output', help='输出文件路径')

    args = parser.parse_args()
    process_file(args.input, args.output)


if __name__ == '__main__':
    main()
