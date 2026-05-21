# XY-Utils 🚀

![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

**xinyan的工具包，code with deepseek。**
一个高效、实用的Python工具集合，专注于文本处理和智能文件操作。

## 📋 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [安装指南](#安装指南)
- [使用方法](#使用方法)
- [处理规则](#处理规则)
- [开发指南](#开发指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性

- **ChatMarkdown 处理器** (`process_cherry_md.py`): 处理 Cherry Studio 导出的聊天记录 Markdown 文件
  - 🗑️ **智能清理**: 自动删除用户发送的内容 (`## 🧑‍💻 User` 及其后续消息)
  - 🎯 **精准提取**: 移除 AI 回复的标记行 (`## 🤖 Assistant`)，但保留 AI 回复正文
  - ⏰ **智能命名**: 输出文件命名格式：`原文件名-整合版-时间戳.md`
  - 🔧 **批量处理**: 支持指定输出目录，方便批量处理

- **Markdown 文件合并器** (`append_md.py`): 将多个 Markdown 文件合并为一个
  - 自动在新行后追加内容
  - 完整的文件存在性检查
  - UTF-8 编码支持
  - 友好的错误提示

- **主程序** (`main.py`): 项目入口和示例

## 📁 项目结构

```
.
├── README.md                 # 项目说明文档
├── pyproject.toml           # Python 项目配置
├── uv.lock                  # uv 依赖锁定文件
├── .python-version          # Python 版本配置
├── main.py                  # 主模块入口
├── process_cherry_md.py     # Cherry Studio Markdown 处理工具
├── append_md.py             # Markdown 文件合并工具
├── .git/                    # Git 版本控制
└── .gitignore               # Git 忽略规则
```

## 📦 安装指南

### 环境要求
- **Python 3.14+** (通过 `.python-version` 指定)
- **操作系统**: Windows, macOS, Linux
- **包管理器**: 推荐使用 [uv](https://github.com/astral-sh/uv)

### 安装步骤

#### 方法 1: 使用 uv (推荐)
```bash
# 克隆项目
git clone <repository-url>
cd xy-utils

# 创建虚拟环境并安装
uv venv
source .venv/bin/activate   # Linux/macOS
# 或
.venv\Scripts\activate      # Windows

uv pip install -e .
```

#### 方法 2: 传统方式
```bash
# 克隆项目
git clone <repository-url>
cd xy-utils

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# 或
.venv\Scripts\activate      # Windows

# 安装
pip install -e .
```

## 🚀 使用方法

### ChatMarkdown 处理器

```bash
# 基本用法
python process_cherry_md.py input.md

# 指定输出目录
python process_cherry_md.py input.md -o ./output/

# 查看完整帮助
python process_cherry_md.py --help
```

**示例：**
```bash
# 处理单个文件
python process_cherry_md.py my_chat.md

# 处理后生成: my_chat-整合版-20241204_143022.md
```

**处理示例：**
```
输入文件 chat.md:
  ## 🧑‍💻 User
  Hello, how are you?
  ---
  ## 🤖 Assistant
  I'm doing well, thank you!

输出文件 chat-整合版-20241204_143022.md:
  I'm doing well, thank you!
```

### Markdown 文件合并器

```bash
# 将 B.md 的内容追加到 A.md 末尾
python append_md.py A.md B.md

# 输出：已将 B.md 的内容追加到 A.md 末尾。
```

### 主程序
```bash
python main.py
# 输出: Hello from xy-utils!
```

## 🔧 处理规则

处理过程使用状态机实现，支持三种状态：

| 状态 | 触发条件 | 行为 |
|------|----------|------|
| **normal** | 初始状态 | 正常输出内容 |
| **user** | 遇到 `## 🧑‍💻 User` | 跳过所有用户消息 |
| **assistant** | 遇到 `## 🤖 Assistant` | 保留 AI 回复内容（移除标记行） |

**状态转换器：**
- `---` 分隔线：返回 normal 状态
- Markdown 标题：根据内容切换状态

## 💻 开发指南

### 依赖管理
- 项目使用 `pyproject.toml` 管理配置
- 使用 `uv` 作为包管理器
- 当前项目无外部依赖，保持轻量

### 开发规范
```bash
# 1. 设置开发环境
uv venv
source .venv/bin/activate

# 2. 安装开发工具
uv pip install black ruff mypy

# 3. 代码格式化
black .
ruff check --fix

# 4. 类型检查
mypy .
```

### 代码结构
- **模块化设计**: 每个工具都是独立的 Python 脚本
- **清晰的接口**: 工具都支持命令行参数和 `--help` 选项
- **错误处理**: 完整的异常处理和用户反馈

## 🤝 贡献指南

欢迎贡献代码！以下是参与贡献的方式：

### 如何贡献
1. **Fork 项目**: 点击 GitHub 页面的 Fork 按钮
2. **创建分支**: `git checkout -b feature/your-feature`
3. **提交更改**: `git commit -m "Add: your feature description"`
4. **推送分支**: `git push origin feature/your-feature`
5. **创建 PR**: 在 GitHub 上提交 Pull Request

### 贡献规范
- 📝 **提交信息**: 使用语义化提交 (feat:, fix:, docs:, chore:)
- ✅ **代码质量**: 通过静态检查 (ruff, mypy)
- 📖 **文档更新**: 修改代码时同步更新文档
- 🧪 **测试覆盖**: 新功能需包含单元测试

## 📄 许可证

本项目采用 **MIT 许可证** - 查看 [LICENSE](LICENSE) 文件了解详情。


## 🔄 更新日志
详见commits界面

## ⚠️ 注意事项

1. **文件备份**: 处理重要文件前建议备份原始文件
2. **编码问题**: 确保输入文件使用 UTF-8 编码
3. **Python 版本**: 需要 Python 3.14 或更高版本
4. **权限问题**: 确保有读写目标目录的权限

## 🌟 感谢

感谢 DeepSeek 的支持和社区的贡献！

---

**项目状态**: 🔧 **积极维护中** - 欢迎使用和贡献！


> 💡 **提示**: 每个工具都包含详细的使用说明，可通过 `--help` 查看帮助信息，首次使用前建议先查看。