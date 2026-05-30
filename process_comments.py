# -*- coding: utf-8 -*-
"""
B站评论数据格式转换脚本
功能：为各行添加前缀标签，删除"点击前往"行，支持评论多行和缺失行
"""

import sys


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


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法：python process_comments.py <输入文件> <输出文件>')
        print('示例：python process_comments.py input.txt output.txt')
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_file(input_file, output_file)
