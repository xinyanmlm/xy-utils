# XY-Utils

xinyan 的工具包，code with deepseek。

一个包含实用工具的 Python 包，目前主要功能是处理 Cherry Studio 导出的聊天记录 Markdown 文件。

## 功能特性

- **ChatMarkdown 处理器** (`process_cherry_md.py`): 处理 Cherry Studio 导出的聊天记录 Markdown 文件
  - 自动删除用户发送的内容 (`## 🧑‍💻 User` 及其后续消息)
  - 移除 AI 回复的标记行 (`## 🤖 Assistant`)，但保留 AI 回复正文
  - 输出文件命名格式：`原文件名-整合版-时间戳.md`

## 项目结构

```
.
├── main.py                    # 主模块入口
├── process_cherry_md.py       # Cherry Studio Markdown 处理工具
├── pyproject.toml            # Python 项目配置
├── uv.lock                   # uv 依赖锁定文件
├── .python-version           # Python 版本配置
└── README.md                 # 本文件
```

## 安装

推荐使用 [uv](https://github.com/astral-sh/uv) 进行 Python 包管理：

```bash
# 克隆项目
git clone <repository-url>
cd xy-utils

# 创建虚拟环境（如果使用 uv）
uv venv
source .venv/bin/activate   # Linux/macOS
# 或
.venv\Scripts\activate      # Windows
```

## 使用方法

### ChatMarkdown 处理器

```bash
# 基本用法
python process_cherry_md.py <input_file.md>

# 指定输出目录
python process_cherry_md.py <input_file.md> -o ./output/

# 查看帮助
python process_cherry_md.py --help
```

**示例：**
假设有一个从 Cherry Studio 导出的文件 `我的聊天记录.md`，运行：

```bash
python process_cherry_md.py 我的聊天记录.md
```

将生成一个名为 `我的聊天记录-整合版-20241204_143022.md` 的新文件，其中：
- 所有用户消息（以 `## 🧑‍💻 User` 开头的部分）已被删除
- AI 助手标记行（`## 🤖 Assistant`）被移除，但助手的回复内容被保留
- 其他格式如分隔线（`---`）保持不变

### 主模块

```bash
python main.py
# 输出: Hello from xy-utils!
```

## 处理规则

处理过程使用状态机实现，支持三种状态：

1. **normal 状态**: 正常输出内容
2. **user 状态**: 遇到 `## 🧑‍💻 User` 后进入，跳过所有用户消息内容
3. **assistant 状态**: 遇到 `## 🤖 Assistant` 后进入，输出助手内容但不输出标记行

状态转换通过内容行和分隔符（`---`）触发。

## 开发要求

- Python >= 3.14
- 使用 `pyproject.toml` 进行项目管理
- 推荐使用 uv 作为包管理器和构建工具

## 许可证

本项目遵循 MIT 许可证。

## 联系方式

如需联系或反馈问题，请通过项目仓库提交 issues。