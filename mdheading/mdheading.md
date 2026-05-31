以下是 `mdheading` 工具的最终设计与说明文档

---

# Markdown 标题等级调整工具 — mdheading

## 1. 概述

`mdheading` 是一个命令行工具，用于统一调整 Markdown 文件中所有 ATX 风格标题（行首 `#`）的**相对等级**。用户只需指定一个目标最高标题等级（1 ~ 6），工具会自动将文件内的各级标题进行等量偏移，使其最高级变为目标等级，其余标题按同样差值升降级。

当降级导致某些标题等级超过六级时，默认会报错并列出越界的标题；若启用 `--force` 参数，这些标题将被转换为加粗正文（`**文本**`）以避免破坏 Markdown 结构。

该工具属于个人工具集 `xy-utils`，作为一个独立子包实现，与项目中的其他脚本解耦，并可通过 `uv run mdheading` 直接调用。

---

## 2. 功能需求

1. **ATX 标题识别**  
   识别标准 Markdown 标题：行首 1 ~ 6 个 `#` 后跟至少一个空白及标题文本，允许尾部存在空白和可选 `#`（如 `## Section ##`）。

2. **偏移计算**  
   扫描文件中所有标题，找到原始最高等级，计算：
   ```
   offset = target_level - max_original_level
   ```

3. **标题等级调整**  
   将每个标题的等级加上 `offset`，生成新的 `#` 数量。

4. **越界处理**  
   - 新等级 **< 1**：视为严重错误，即使 `--force` 也拒绝处理，输出错误退出。
   - 新等级 **> 6**：默认输出错误并列出所有越界标题行；若启用 `--force`，将这些标题转为粗体正文。

5. **文件输出**  
   - 默认覆盖原文件（原地修改）。
   - 支持通过 `-o` 输出到新文件。
   - 覆盖前可通过 `-b` 创建备份（如 `.bak`）。
   - 提供 `-n` / `--dry-run` 试运行，仅显示差异而不写入。

6. **安全写入**  
   使用临时文件 + 原子替换，防止写入过程中断导致文件损坏。

7. **边界情况**  
   - 文件中无标题：正常退出，不修改文件。
   - 目标等级等于原最高等级：无需修改，提示并退出。

---

## 3. 命令行接口

```
usage: mdheading [-h] [-t LEVEL] [-f] [-o OUTPUT] [-b SUFFIX] [-n] INPUT

调整 Markdown 文件中所有标题的相对等级

positional arguments:
  INPUT                 输入的 Markdown 文件路径

optional arguments:
  -h, --help           显示帮助信息
  -t LEVEL, --target-level LEVEL
                        目标最高标题等级 (1-6)，默认为 1
  -f, --force          当降级导致标题等级超过 6 级时，将其转为加粗正文
  -o OUTPUT, --output OUTPUT
                        输出文件路径，默认覆盖输入文件
  -b SUFFIX, --backup SUFFIX
                        覆盖原文件前创建备份，使用指定后缀（如 .bak）
  -n, --dry-run        仅显示将修改的内容，不实际写入文件
```

### 使用示例

```bash
# 将 example.md 的最高标题调整为三级（原最高为一级时，一级→三级，二级→四级...）
uv run mdheading example.md -t 3

# 强制处理：超过六级的标题转为 **粗体**
uv run mdheading example.md -t 6 --force

# 输出到新文件，保留原文件不变
uv run mdheading example.md -t 2 -o result.md

# 覆盖原文件前备份为 example.md.bak
uv run mdheading example.md -t 4 -b .bak

# 试运行查看变更
uv run mdheading example.md -t 3 --dry-run
```

---

## 4. 设计与架构

### 4.1 项目结构

```
xy-utils/                    # 个人工具集根目录
├── pyproject.toml          # 项目配置，含 scripts 入口
├── ...                     # 其他已有脚本
└── mdheading/              # mdheading 独立子包
    ├── __init__.py         # 包标记
    ├── __main__.py         # 允许 python -m mdheading 调用
    ├── cli.py              # 命令行参数解析与主流程
    └── processor.py        # 核心处理逻辑（与界面无关）
```

**模块职责：**

- `processor.py`  
  包含 `HeadingLine` 数据类（表示一个标题行）和 `MarkdownHeadingProcessor` 类。负责标题识别、偏移计算、越界验证和文本转换。所有逻辑与命令行参数无关，可单独测试。

- `cli.py`  
  使用 `argparse` 构建命令行解析器，定义主函数 `main()`。流程：读取文件 → 实例化 `MarkdownHeadingProcessor` → 调用 `adjust()` → 输出或写文件。

- `__main__.py`  
  简单转发 `from .cli import main; main()`，使 `python -m mdheading` 能正常运行。

### 4.2 核心类与算法

#### HeadingLine
```python
@dataclass
class HeadingLine:
    line_number: int       # 行号（0-based）
    original_level: int    # 1..6
    text: str              # 去除标记符的纯文本
    trailing: str          # 尾部空白和可选 #
    raw_line: str          # 原始行
```
提供 `to_new_heading(new_level)` 和 `to_bold_paragraph()` 方法。

#### MarkdownHeadingProcessor
- **正则表达式**：`^(#{1,6})\s+(.+?)(\s+#+)?\s*$`（多行模式）
- **`_find_headings()`**：遍历所有行，生成 `HeadingLine` 列表。
- **`calculate_offset(target_level)`**：找到 `max(original_level)` 计算偏移量；若无标题返回 `None`。
- **`validate_and_transform(offset, force)`**：
  - 对每个标题计算 `new_level = original_level + offset`。
  - 若 `new_level < 1` → 总是错误。
  - 若 `new_level > 6` 且未 `force` → 错误；若 `force` → 调用 `to_bold_paragraph()`。
  - 正常等级 → 调用 `to_new_heading(new_level)`。
  - 返回 `(new_lines, errors)`。
- **`adjust(target_level, force)`**：组合上述步骤，返回调整后全文和错误列表。

#### 处理流程
```
1. 读取文件内容 → content (str)
2. 实例化 MarkdownHeadingProcessor(content)
3. offset = processor.calculate_offset(target_level)
4. new_content, errors = processor.adjust(target_level, force)
5. 如果有 errors → 打印并退出(1)
6. 如果 dry-run → 打印差异
7. 否则写入目标文件（临时文件 + 原子替换）
```

### 4.3 安全与健壮性设计

- **文件原子写入**：使用 `tempfile.NamedTemporaryFile` 在目标目录创建临时文件，写入完成后通过 `shutil.move` 替换原文件，避免写入过程中程序崩溃导致文件损坏。
- **备份机制**：仅当 `--backup` 指定后缀时，且输出文件即为原文件时，先复制原文件为 `原文件.后缀`。
- **编码**：统一使用 UTF-8，与绝大多数 Markdown 文件兼容。
- **换行保留**：`splitlines(keepends=True)` 保留原行尾序列，重建文本时维持原样。

---

## 5. 限制与注意事项

- **仅支持 ATX 标题**（`#` 开头）。Setext 风格（下划线）暂不支持，代码中保留了扩展点。
- **不忽略代码块**：若代码块或引用块内出现 `#` 开头的行，也会被当作标题处理。复杂场景可考虑增加代码块状态机，当前版本为轻量工具，未实现。
- **前导空白**：假定 ATX 标题行无前导空白（严格标准）；若存在缩进，生成的标题仍从行首开始，可能丢失原始缩进（一般不推荐缩进标题）。
- **force 对低于 1 级无效**：当原文件最高为 6 级，目标为 1 级时，某些低级标题可能变为负数等级，此时无法转换为合理 Markdown，工具会始终报错。

---

## 6. 测试用例

### 基础降级
**输入** (`test.md`)：
```
# Title
## Section
### Subsection
```
**命令**：`mdheading test.md -t 3`  
**输出**：
```
### Title
#### Section
##### Subsection
```

### 升级
**输入**：原最高为 `##` (Section)  
**命令**：`mdheading test.md -t 1`  
**输出**：`##` → `#`，`###` → `##`，以此类推。

### 超出六级无 force
**输入**：包含 `#` ~ `######` 六个等级  
**命令**：`mdheading test.md -t 6` （offset = 5）  
**预期**：报错，列出所有 `new_level > 6` 的行。

### 超出六级有 force
**同上，加 `--force`**  
**预期**：原 `#` 变为 `######`，其余标题全部转为 `**文本**`。

### 无标题文件
**输入**：只有普通正文  
**命令**：任意目标等级  
**预期**：输出“文件中未检测到任何标题”，正常退出，不修改文件。

### 标题尾随 `#`
**输入**：`## Section ##`  
**命令**：`-t 4` （假设原最高为 2）  
**输出**：`#### Section ##`

### 边界：原最高 6 → 目标 1
**输入**：`###### Top` 和 `# Bottom`  
**命令**：`-t 1` （offset = -5）  
**预期**：无论是否 `--force`，都会因 `new_level < 1` 报错退出。

---

## 7. 安装与运行

本工具作为 `xy-utils` 项目的一部分，无需单独安装。确保项目根目录下的 `pyproject.toml` 包含：

```toml
[project.scripts]
mdheading = "mdheading.cli:main"
```

然后在项目根目录下使用 `uv run mdheading` 执行。

若希望全局调用，可执行：
```bash
uv tool install --editable .
```
之后即可在任何位置直接运行 `mdheading`。

---

## 8. 扩展计划

- 支持 Setext 标题（`===` / `---`）。
- 智能跳过代码围栏和引用块内的 `#` 行。
- 允许自定义粗体包裹样式（如 `__bold__`）。
- 支持管道输入/输出（如 `cat file.md | mdheading -`）。
- 彩色差异展示。

---

此文档为 `mdheading` 的最终设计与说明，随代码一起维护。