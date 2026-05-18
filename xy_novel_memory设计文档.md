
---

# 都市言情小说专用 MCP 记忆服务器 - 技术规格文档

## 1. 项目概述
构建一个基于 Python + MCP 官方 SDK 的记忆服务器，为长篇都市言情小说的 AI 辅助创作提供结构化知识管理。服务器通过 SQLite 数据库存储实体（人物、地点、特殊物品）、关系、伏笔和章节摘要，并提供专用工具供 Reasonix 在创作过程中调用。

## 2. 技术栈
- Python 3.10+
- `mcp` 官方 Python SDK
- `sqlite-utils`（简化 SQLite 操作）
- 通信方式：STDIO (标准输入/输出)

## 3. 数据库设计

数据库文件名通过命令行参数 `--db` 指定，默认为 `novel_memory.db`。

### 3.1 表结构

```sql
-- 实体表 (entities)
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,       -- 实体唯一名称
    type TEXT NOT NULL,              -- 类型：character | location | item | organization
    attributes TEXT,                 -- JSON 格式属性，如 {"age":24, "gender":"女", "traits":["温柔","坚韧"]}
    current_status TEXT,            -- 当前状态描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关系表 (relationships)
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity TEXT NOT NULL,     -- 源实体名称
    target_entity TEXT NOT NULL,     -- 目标实体名称
    relation_type TEXT NOT NULL,     -- 关系类型：恋人 | 暗恋 | 前任 | 朋友 | 同事 | 情敌 | 家人 等
    description TEXT,                -- 关系详细说明
    start_chapter INTEGER,           -- 关系开始的章节
    end_chapter INTEGER,             -- 关系结束的章节（NULL表示持续中）
    FOREIGN KEY (source_entity) REFERENCES entities(name) ON DELETE CASCADE,
    FOREIGN KEY (target_entity) REFERENCES entities(name) ON DELETE CASCADE
);

-- 情节表 (plot_points)
CREATE TABLE IF NOT EXISTS plot_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter INTEGER NOT NULL,        -- 章节号
    summary TEXT NOT NULL,           -- 本章关键情节摘要
    involved_entities TEXT,          -- 涉及实体名称列表，逗号分隔
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 伏笔表 (foreshadowings)
CREATE TABLE IF NOT EXISTS foreshadowings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,       -- 伏笔描述
    planted_chapter INTEGER,        -- 埋下伏笔的章节
    status TEXT DEFAULT 'pending',  -- pending | resolved
    resolved_chapter INTEGER,       -- 回收章节
    related_entities TEXT,          -- 相关实体，逗号分隔
    notes TEXT,                     -- 额外说明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. MCP 工具定义

服务器需提供以下工具，每个工具需定义清晰的 inputSchema。

### 4.1 `upsert_character`
创建或更新一个角色实体。

- **参数**：
  - `name` (string, 必填): 角色名称。
  - `attributes` (string, 可选): JSON 格式的属性，例如 `{"age":24, "gender":"女", "occupation":"设计师"}`。
  - `current_status` (string, 可选): 当前状态描述。
- **行为**：若角色已存在则更新，否则插入。
- **返回**：操作成功或失败的提示文本。

### 4.2 `get_character_info`
查询指定角色的完整信息，包括其属性和所有关系。

- **参数**：
  - `name` (string, 必填): 角色名称。
- **返回**：格式化的文本，包含角色属性、当前状态以及该角色参与的所有关系（源或目标）。若角色不存在则提示。

### 4.3 `add_relationship`
添加一条人际关系。

- **参数**：
  - `source` (string, 必填): 源角色名称。
  - `target` (string, 必填): 目标角色名称。
  - `relation` (string, 必填): 关系类型（如 "恋人"、"情敌" 等）。
  - `description` (string, 可选): 关系详细说明。
  - `start_chapter` (integer, 可选): 关系开始的章节。
- **行为**：插入关系记录，并自动确保双向性（例如添加一条 "A 暗恋 B"，同时可添加 "B 被暗恋 A" 的反向关系，但本工具只记录单向，由调用者自行添加反向关系）。检查源和目标实体存在。
- **返回**：操作结果。

### 4.4 `record_plot`
记录一个章节的关键情节。

- **参数**：
  - `chapter` (integer, 必填): 章节号。
  - `summary` (string, 必填): 本章摘要。
  - `involved_entities` (string, 可选): 逗号分隔的涉及实体名称。
- **返回**：成功提示。

### 4.5 `add_foreshadowing`
添加一个伏笔。

- **参数**：
  - `description` (string, 必填): 伏笔描述。
  - `planted_chapter` (integer, 必填): 埋下伏笔的章节。
  - `related_entities` (string, 可选): 相关实体，逗号分隔。
- **返回**：成功提示。

### 4.6 `resolve_foreshadowing`
将一个伏笔标记为已回收。

- **参数**：
  - `id` (integer, 必填): 伏笔记录的 ID。
  - `resolved_chapter` (integer, 必填): 回收章节。
  - `notes` (string, 可选): 回收说明。
- **返回**：操作结果。

### 4.7 `list_unresolved_foreshadowings`
列出所有未回收的伏笔。

- **无参数**
- **返回**：格式化的未回收伏笔列表（ID、描述、埋下章节）。

### 4.8 `list_characters_by_status`
根据当前状态搜索角色。

- **参数**：
  - `status_keyword` (string, 可选): 状态关键词，若不提供则返回所有角色。
- **返回**：匹配的角色名称及当前状态列表。

### 4.9 `get_chapter_summary`
获取指定章节的摘要。

- **参数**：
  - `chapter` (integer, 必填): 章节号。
- **返回**：章节摘要及涉及实体。

## 5. 环境变量与运行参数

- 服务器支持通过命令行参数 `--db` 指定数据库文件路径（默认 `novel_memory.db`），以便不同小说项目使用独立数据库文件。
- 可选：环境变量 `NOVEL_DB_PATH` 作为备选数据库路径（优先级：命令行参数 > 环境变量 > 默认值）。

## 6. 实现要点

- 使用 `mcp.server.stdio` 创建 STDIO 传输服务器。
- 所有工具返回 `TextContent` 类型的文本。
- 对 `attributes` 参数进行 JSON 解析，存储时保持原始 JSON 字符串；查询时美化输出。
- `get_character_info` 需关联查询 `relationships` 表，展示该角色作为 source 或 target 的所有关系。
- 工具操作数据库时使用异常处理，返回友好的错误信息。
- 服务器启动时自动执行建表语句（`IF NOT EXISTS`）。

## 7. 调用示例（在 Reasonix 中）

```
[工具调用] upsert_character(name="林逸", attributes='{"age":24, "occupation":"程序员", "traits":["隐忍","温柔"]}', current_status="刚和女主吵完架，心情低落")
[返回] 角色 林逸 已创建/更新。

[工具调用] add_relationship(source="林逸", target="苏晚", relation="恋人", description="高中同学，大学重逢后逐渐走近", start_chapter=3)
[返回] 已添加关系：林逸 → 苏晚 (恋人)

[工具调用] add_foreshadowing(description="苏晚的手机屏保是林逸高中时画的星空", planted_chapter=5)
[返回] 伏笔已添加，ID=1。

[工具调用] list_unresolved_foreshadowings()
[返回] 未回收的伏笔：
- ID:1 苏晚的手机屏保是林逸高中时画的星空 (第5章)
```

## 8. 交付物要求

请根据本规格文档生成一个完整的、可直接运行的 Python 脚本，包括：
- 所有 MCP 工具的实现。
- 命令行参数解析 (`argparse`)。
- 服务器启动入口 (`if __name__ == "__main__":`)。

确保代码遵循 PEP8 风格，并包含必要的导入和异常处理。

---

你可以直接将以上文档发给新对话中的 AI，请求它生成对应的 Python 代码。它生成后，你可以将其保存为 `novel_memory_server.py`，并通过如下命令为不同小说项目启动独立实例：

```bash
python novel_memory_server.py --db /path/to/novel1/memory/novel1.db
```

这样你的 MCP 记忆服务器就能精准服务于都市言情小说的动态记忆需求了。