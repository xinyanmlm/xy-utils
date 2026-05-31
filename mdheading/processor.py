"""Markdown 标题处理核心逻辑，与命令行无关"""

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class HeadingLine:
    """表示一个 ATX 标题行"""
    line_number: int      # 行号 (0-based)
    original_level: int   # 原始等级 (1-6)
    text: str             # 标题纯文本
    trailing: str         # 尾部空白与可选 # (例如 " ##")
    raw_line: str         # 整行原始内容

    def to_new_heading(self, new_level: int) -> str:
        """生成调整等级后的标题行字符串"""
        # 保留原行的缩进？假设原行无前导空格（ATX标题通常行首开始）
        # 用 # 重建
        return f"{'#' * new_level} {self.text}{self.trailing}\n"

    def to_bold_paragraph(self) -> str:
        """转为粗体正文 (force 模式)"""
        return f"**{self.text}**\n"


class MarkdownHeadingProcessor:
    """处理 Markdown 文本中的 ATX 标题等级调整"""

    HEADING_PATTERN = re.compile(
        r'^(?P<hashes>#{1,6})\s+(?P<text>.+?)(?P<trailing>\s+#+)?\s*$',
        re.MULTILINE
    )

    def __init__(self, content: str):
        self.content = content
        self.lines = content.splitlines(keepends=True)   # 保留换行符
        self.headings: List[HeadingLine] = self._find_headings()

    def _find_headings(self) -> List[HeadingLine]:
        headings = []
        # 使用枚举更方便获取行号
        for idx, line in enumerate(self.lines):
            m = self.HEADING_PATTERN.match(line)
            if m:
                level = len(m.group('hashes'))
                text = m.group('text').strip()
                trailing = m.group('trailing') or ''
                # 这里将原始行中的尾随 # 保留（不含前导空格？原正则已经包含）
                # 注意：trailing 包含开头的空格（因为正则中(?P<trailing>\s+#+) 要求空格+#）
                headings.append(HeadingLine(
                    line_number=idx,
                    original_level=level,
                    text=text,
                    trailing=trailing,
                    raw_line=line
                ))
        return headings

    def calculate_offset(self, target_level: int) -> int:
        """计算统一的等级偏移量，若无标题返回 None"""
        if not self.headings:
            return None
        max_level = max(h.original_level for h in self.headings)
        return target_level - max_level

    def validate_and_transform(
        self,
        offset: int,
        force: bool
    ) -> Tuple[List[str], List[str]]:
        """
        生成新行列表，并返回错误消息列表。
        若存在越界且未 force，则返回空行列表和错误消息。
        """
        new_lines = self.lines.copy()
        errors = []

        # 处理每个标题
        for heading in self.headings:
            new_level = heading.original_level + offset

            # 检查下界
            if new_level < 1:
                errors.append(
                    f"行 {heading.line_number+1}: 标题 '{heading.text}' 调整后等级 {new_level} (<1)，无法处理"
                )
                continue  # 即使 force 也无法合理转换，记录错误

            if new_level > 6:
                if force:
                    # 转为粗体正文
                    new_lines[heading.line_number] = heading.to_bold_paragraph()
                else:
                    errors.append(
                        f"行 {heading.line_number+1}: 标题 '{heading.text}' 调整后等级 {new_level} (>6)，使用 --force 可转为粗体"
                    )
            else:
                # 正常调整
                new_lines[heading.line_number] = heading.to_new_heading(new_level)

        if errors:
            return [], errors
        return new_lines, []

    def adjust(self, target_level: int, force: bool) -> Tuple[str, List[str]]:
        """
        执行调整，返回调整后的文本和错误列表。
        若返回的错误列表非空，文本为空字符串。
        """
        offset = self.calculate_offset(target_level)
        if offset is None:
            # 无标题
            return self.content, []  # 原样返回，无错误

        new_lines, errors = self.validate_and_transform(offset, force)
        if errors:
            return "", errors

        # 拼接新内容
        return "".join(new_lines), []
        