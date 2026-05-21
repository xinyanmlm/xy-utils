# XY-Utils 🚀

![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

**xinyan的工具包，code with deepseek。**
一个高效、实用的Python工具集合，专注于文本处理和智能创作辅助。

## 📋 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
-[安装指南](#安装指南)
-[使用方法](#使用方法)
-[都市言情小说MCP记忆服务器](#都市言情小说mcp记忆服务器)
-[开发指南](#开发指南)
-[贡献指南](#贡献指南)
-[许可证](#许可证)

## ✨ 功能特性

### 🗂️ **ChatMarkdown 处理器** (`process_cherry_md.py`)
- 🗑️ **智能清理**: 自动删除用户发送的内容 (`## 🧑‍💻 User` 及其后续消息)
- 🎯 **精准提取**: 移除AI回复的标记行 (`## 🤖 Assistant`)，但保留AI回复正文
- ⏰ **智能命名**: 输出文件命名格式：`原文件名-整合版-时间戳.md`
- 🔧 **批量处理**: 支持指定输出目录，方便批量处理
- 📘 **格式转换**: 支持转换为ePub3格式（需自己额外安装pandoc）
- 🛠️ **状态机设计**: 使用normal、user、assistant三种状态精确处理

### 🔗 **Markdown 文件合并器** (`append_md.py`)
- 📂 **双模式操作**: 支持双文件追加和目录合并模式
- 🔢 **智能排序**: 自然排序文件名（支持 chapter-001.md, chapter-001-status.md 等格式）
- 📝 **自动补全**: 为无标题文件自动添加标题（使用文件名作为标题）
- 🎯 **灵活过滤**: 支持主文件过滤 (`--main-only`) 和正则过滤 (`--filter`)
- 📦 **批量合并**: 按文件名排序合并目录下所有.md文件
- 📄 **格式保持**: 自动在文件间添加空行分隔，保持格式整洁

### 📖 **都市言情小说MCP记忆服务器** (`xy_novel_memory.py`)
- 📚 **结构化存储**: SQLite数据库管理小说创作要素
- 🤖 **AI集成**: MCP协议支持，可与AI写作助手（如Reasonix）集成
- 👥 **角色管理**: 创建/更新角色，记录状态、人格特征、形象描述
- 🔗 **关系跟踪**: 记录角色间复杂关系（血缘、情侣、朋友、敌对等）
- ⏳ **伏笔管理**: 管理伏笔的埋设和回收，避免遗漏
- 📝 **情节记录**: 按章节记录小说发展情节
- 🔎 **智能查询**: 按角色状态、未回收伏笔等条件搜索

### 🚪 **主程序** (`main.py`)
- 简单的项目入口，打印欢迎信息

## 📁 项目结构

```
xy-utils/
├── README.md                     # 项目说明文档
├── pyproject.toml               # Python项目配置
├── uv.lock                      # uv依赖锁定文件
├── .python-version              # Python版本配置 (3.14)
├── main.py                      # 主模块入口
├── process_cherry_md.py         # ChatMarkdown处理器
├── append_md.py                 # Markdown文件合并器
├── xy_novel_memory.py           # 都市言情小说MCP记忆服务器
├── xy_novel_memory设计文档.md    # MCP服务器技术规格文档
└── .gitignore                   # Git忽略规则
```

## 📦 安装指南

### 环境要求
- **Python 3.14+** (通过`.python-version`指定)
- **操作系统**: Windows, macOS, Linux
- **包管理器**: 推荐使用[uv](https://github.com/astral-sh/uv)

### 安装步骤

#### 方法1: 使用uv (推荐)
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

#### 方法2: 传统方式
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

### ChatMarkdown处理器

```bash
# 基本用法
python process_cherry_md.py input.md

# 指定输出目录
python process_cherry_md.py input.md -o ./output/

# 转换为ePub格式
python process_cherry_md.py input.md --epub

# 查看完整帮助
python process_cherry_md.py --help
```

**示例：**
```bash
# 处理单个文件
python process_cherry_md.py my_chat.md
# 处理后生成: my_chat-整合版-20250121_143022.md
```

**状态机处理逻辑：**
```
输入文件 chat.md:
  ## 🧑‍💻 User
  Hello, how are you?
  ---
  ## 🤖 Assistant
  I'm doing well, thank you!

输出文件:
  I'm doing well, thank you!
```

### Markdown文件合并器

```bash
# 双文件模式：将B.md的内容追加到A.md末尾
python append_md.py A.md B.md

# 目录模式：合并当前目录所有.md文件到combined.md
python append_md.py ./ combined.md

# 只合并主章节文件（过滤掉status、notes等文件）
python append_md.py ./ combined.md --main-only

# 使用自定义正则过滤
python append_md.py ./ combined.md --filter "^chapter.*\.md$"

# 查看完整帮助
python append_md.py --help
```

**智能排序示例：**
```
chapter-001.md
chapter-002.md
chapter-002-notes.md
chapter-003.md
chapter-003-status.md
```

### 主程序
```bash
python main.py
# 输出: Hello from xy-utils!
```

## 📖 都市言情小说MCP记忆服务器

这是一个为长篇都市言情小说创作设计的智能记忆服务器，通过MCP协议与AI写作助手集成。

### 数据库结构
1. **entities表**: 存储人物、地点、物品等实体
2. **relationships表**: 存储角色间关系
3. **plot_points表**: 存储章节摘要和情节发展
4. **foreshadowings表**: 存储未回收和已回收的伏笔

### 提供的工具

#### 角色管理
- `upsert_character`: 创建/更新角色信息
```json
{
  "name": "李欣然",
  "type": "角色",
  "status": "主角",
  "personality": "独立坚强但内心深处柔软",
  "appearance": "长发及腰，眼眸如秋水"
}
```

- `get_character_info`: 查询角色详细信息
- `list_characters_by_status`: 按状态（主角、配角、反派）搜索角色

#### 关系管理
- `add_relationship`: 添加角色关系
```json
{
  "source_character": "李欣然",
  "target_character": "顾辰风",
  "relationship_type": "情侣",
  "description": "从商业竞争对手到相互欣赏的伴侣"
}
```

#### 情节和伏笔管理
- `record_plot`: 记录章节情节发展
- `add_foreshadowing`: 添加伏笔
- `resolve_foreshadowing`: 回收伏笔
- `list_unresolved_foreshadowings`: 列出未回收伏笔
- `get_chapter_summary`: 获取章节摘要

### 使用方法

#### 启动MCP服务器
```bash
python xy_novel_memory.py
```

#### 与AI助手集成
配置AI助手（如Reasonix）连接到此MCP服务器，即可在对话中使用上述工具管理小说创作。

详细技术规格和调用示例请参考 [xy_novel_memory设计文档.md](xy_novel_memory设计文档.md)。

## 💻 开发指南

### 依赖管理
```toml
# pyproject.toml
dependencies = [
    "mcp>=1.27.1",      # MCP协议支持
    "sqlite-utils>=3.39", # SQLite操作工具
]
```

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

## 🤝 贡献指南

欢迎贡献代码！以下是参与贡献的方式：

### 如何贡献
1. **Fork项目**: 点击GitHub页面的Fork按钮
2. **创建分支**: `git checkout -b feature/your-feature`
3. **提交更改**: `git commit -m "Add: your feature description"`
4. **推送分支**: `git push origin feature/your-feature`
5. **创建PR**: 在GitHub上提交Pull Request

### 贡献规范
- 📝 **提交信息**: 使用语义化提交 (feat:, fix:, docs:, chore:)
- ✅ **代码质量**: 通过静态检查 (ruff, mypy)
- 📖 **文档更新**: 修改代码时同步更新相关文档
- 🧪 **测试覆盖**: 新功能需包含单元测试

## 📄 许可证

本项目采用 **MIT许可证**。

## ⚠️ 注意事项

1. **文件备份**: 处理重要文件前建议备份原始文件
2. **编码问题**: 确保输入文件使用UTF-8编码
3. **Python版本**: 需要Python 3.14或更高版本
4. **权限问题**: 确保有读写目标目录的权限
5. **MCP服务器**: 首次使用需配置AI助手连接

## 🌟 感谢

感谢DeepSeek的支持和社区的贡献！

---

**项目状态**: 🔧 **积极维护中** - 欢迎使用和贡献！

> 💡 **提示**: 每个工具都包含详细的使用说明，可通过`--help`查看帮助信息，首次使用前建议先查看。