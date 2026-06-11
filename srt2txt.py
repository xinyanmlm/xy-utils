import sys
import os

def srt_to_txt(srt_path: str) -> str:
    """将SRT字幕文本提取合并为纯文本，返回输出文件路径"""
    if not os.path.isfile(srt_path):
        raise FileNotFoundError(f"文件不存在: {srt_path}")

    # 读取SRT文件
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    text_lines = []
    for line in lines:
        stripped = line.strip()
        # 跳过空行、纯数字序号行、包含时间轴的行
        if not stripped:
            continue
        if stripped.isdigit():
            continue
        if '-->' in stripped:
            continue
        # 剩下的就是字幕文本
        text_lines.append(stripped)

    # 合并为一段文章（句子间用空格分隔）
    article = ' '.join(text_lines)

    # 输出路径：同目录，同名，扩展名为.txt
    base = os.path.splitext(srt_path)[0]
    txt_path = base + '.txt'

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(article)

    return txt_path

def main():
    if len(sys.argv) != 2:
        print("用法: python srt_to_txt.py <srt文件路径>")
        sys.exit(1)

    srt_file = sys.argv[1]
    try:
        out_path = srt_to_txt(srt_file)
        print(f"已生成: {out_path}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()