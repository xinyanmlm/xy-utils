"""
都市言情小说专用 MCP 记忆服务器
为 AI 辅助创作提供结构化知识管理，基于 MCP 官方 SDK 与 SQLite。
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from sqlite_utils import Database


# ---------- 数据库初始化 ----------
def init_db(db_path: str) -> Database:
    """创建数据库连接并初始化表结构。"""
    db = Database(db_path)

    # 实体表 —— 以 name 为主键，不再使用自增 id
    db.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            name TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            attributes TEXT,
            current_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 关系表
    db.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_entity TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            description TEXT,
            start_chapter INTEGER,
            end_chapter INTEGER,
            FOREIGN KEY (source_entity) REFERENCES entities(name) ON DELETE CASCADE,
            FOREIGN KEY (target_entity) REFERENCES entities(name) ON DELETE CASCADE
        )
    """)

    # 情节表
    db.execute("""
        CREATE TABLE IF NOT EXISTS plot_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter INTEGER NOT NULL,
            summary TEXT NOT NULL,
            involved_entities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 伏笔表
    db.execute("""
        CREATE TABLE IF NOT EXISTS foreshadowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            planted_chapter INTEGER,
            status TEXT DEFAULT 'pending',
            resolved_chapter INTEGER,
            related_entities TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    return db


# ---------- MCP 工具函数 ----------
def _entity_exists(db: Database, name: str) -> bool:
    return db["entities"].get(name) is not None


def _format_attributes(attributes_json: str | None) -> str:
    """格式化 JSON 属性字符串，便于阅读。"""
    if not attributes_json:
        return "无"
    try:
        data = json.loads(attributes_json)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return attributes_json


def _build_relations_text(db: Database, entity_name: str) -> str:
    """构建指定实体的所有关系描述文本。"""
    rels = list(
        db.query(
            """
            SELECT source_entity, target_entity, relation_type, description, start_chapter
            FROM relationships
            WHERE source_entity = ? OR target_entity = ?
            """,
            [entity_name, entity_name],
        )
    )
    if not rels:
        return "暂无记录的人际关系。"
    lines = []
    for r in rels:
        src = r["source_entity"]
        tgt = r["target_entity"]
        rtype = r["relation_type"]
        desc = r["description"] or "无详细说明"
        chap = f"（始于第{r['start_chapter']}章）" if r["start_chapter"] else ""
        lines.append(f"  {src} → {tgt} [{rtype}] {desc} {chap}")
    return "\n".join(lines)


# ---------- 工具实现 ----------
async def upsert_character(db: Database, name: str, attributes: str | None = None,
                           current_status: str | None = None) -> str:
    if attributes:
        try:
            json.loads(attributes)
        except json.JSONDecodeError:
            return "错误：attributes 参数不是有效的 JSON 格式。"

    table = db["entities"]
    existing = table.get(name)          # 按主键 name 查询
    now = datetime.now().isoformat()

    if existing:
        updates = {"updated_at": now}
        if attributes is not None:
            updates["attributes"] = attributes
        if current_status is not None:
            updates["current_status"] = current_status
        table.update(name, updates)     # 主键值 = name
        return f"角色 {name} 已更新。"
    else:
        table.insert({
            "name": name,
            "type": "character",
            "attributes": attributes,
            "current_status": current_status,
            "created_at": now,
            "updated_at": now,
        })
        return f"角色 {name} 已创建。"


async def get_character_info(db: Database, name: str) -> str:
    row = db["entities"].get(name)       # 直接用 get
    if not row:
        return f"角色 {name} 不存在。"
    lines = [
        f"角色名称：{row['name']}",
        f"类型：{row['type']}",
        f"属性：\n{_format_attributes(row['attributes'])}",
        f"当前状态：{row['current_status'] or '无'}",
        f"人际关系：\n{_build_relations_text(db, name)}",
    ]
    return "\n".join(lines)


async def add_relationship(db: Database, source: str, target: str, relation: str,
                           description: str | None = None, start_chapter: int | None = None) -> str:
    """添加人际关系。"""
    # 检查源和目标实体是否存在
    missing = []
    if not _entity_exists(db, source):
        missing.append(source)
    if not _entity_exists(db, target):
        missing.append(target)
    if missing:
        return f"错误：以下实体不存在，请先创建它们：{', '.join(missing)}"

    db["relationships"].insert({
        "source_entity": source,
        "target_entity": target,
        "relation_type": relation,
        "description": description,
        "start_chapter": start_chapter,
    })
    return f"已添加关系：{source} → {target} ({relation})"


async def record_plot(db: Database, chapter: int, summary: str,
                      involved_entities: str | None = None) -> str:
    """记录章节关键情节。"""
    db["plot_points"].insert({
        "chapter": chapter,
        "summary": summary,
        "involved_entities": involved_entities,
    })
    return f"第{chapter}章情节已记录。"


async def add_foreshadowing(db: Database, description: str, planted_chapter: int,
                            related_entities: str | None = None) -> str:
    """添加伏笔。"""
    pk = db["foreshadowings"].insert({
        "description": description,
        "planted_chapter": planted_chapter,
        "related_entities": related_entities,
        "status": "pending",
    }).last_pk
    return f"伏笔已添加，ID={pk}。"


async def resolve_foreshadowing(db: Database, id: int, resolved_chapter: int,
                                notes: str | None = None) -> str:
    table = db["foreshadowings"]
    row = table.get(id)                  # foreshadowings 的主键是 id，直接用 get
    if not row:
        return f"错误：伏笔 ID={id} 不存在。"
    updates = {"status": "resolved", "resolved_chapter": resolved_chapter}
    if notes is not None:
        updates["notes"] = notes
    table.update(id, updates)            # 按主键更新
    return f"伏笔 ID={id} 已标记为已回收（第{resolved_chapter}章）。"


async def list_unresolved_foreshadowings(db: Database) -> str:
    """列出所有未回收的伏笔。"""
    rows = list(db["foreshadowings"].rows_where("status = 'pending'", order_by="planted_chapter"))
    if not rows:
        return "当前没有未回收的伏笔。"
    lines = ["未回收的伏笔："]
    for r in rows:
        lines.append(f"- ID:{r['id']} {r['description']} (第{r['planted_chapter']}章)")
    return "\n".join(lines)


async def list_characters_by_status(db: Database, status_keyword: str | None = None) -> str:
    """根据当前状态搜索角色。"""
    if status_keyword:
        rows = list(db.query(
            "SELECT name, current_status FROM entities WHERE type='character' AND current_status LIKE ?",
            [f"%{status_keyword}%"],
        ))
    else:
        rows = list(db.query(
            "SELECT name, current_status FROM entities WHERE type='character'"
        ))
    if not rows:
        return "未找到匹配的角色。"
    lines = ["匹配的角色："]
    for r in rows:
        lines.append(f"- {r['name']} (状态：{r['current_status'] or '无'})")
    return "\n".join(lines)


async def get_chapter_summary(db: Database, chapter: int) -> str:
    """获取指定章节的摘要。"""
    rows = list(db["plot_points"].rows_where("chapter = ?", [chapter], order_by="id"))
    if not rows:
        return f"第{chapter}章暂无情节记录。"
    lines = [f"第{chapter}章情节摘要："]
    for r in rows:
        entities = f"涉及实体：{r['involved_entities']}" if r["involved_entities"] else "无特定实体"
        lines.append(f"- {r['summary']} ({entities})")
    return "\n".join(lines)


# ---------- MCP 服务器定义 ----------
def create_server(db_path: str) -> Server:
    """创建并配置 MCP 服务器。"""
    server = Server("novel-memory-server")
    db = init_db(db_path)

    # 注册工具
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="upsert_character",
                description="创建或更新一个角色实体。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "角色名称"},
                        "attributes": {
                            "type": "string",
                            "description": "JSON 格式的属性，例如 {\"age\":24, \"gender\":\"女\"}",
                        },
                        "current_status": {"type": "string", "description": "当前状态描述"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="get_character_info",
                description="查询指定角色的完整信息，包括属性和所有关系。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "角色名称"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="add_relationship",
                description="添加一条人际关系。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "源角色名称"},
                        "target": {"type": "string", "description": "目标角色名称"},
                        "relation": {"type": "string", "description": "关系类型（如 恋人、情敌）"},
                        "description": {"type": "string", "description": "关系详细说明"},
                        "start_chapter": {"type": "integer", "description": "关系开始的章节"},
                    },
                    "required": ["source", "target", "relation"],
                },
            ),
            Tool(
                name="record_plot",
                description="记录一个章节的关键情节。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "chapter": {"type": "integer", "description": "章节号"},
                        "summary": {"type": "string", "description": "本章摘要"},
                        "involved_entities": {"type": "string", "description": "逗号分隔的涉及实体名称"},
                    },
                    "required": ["chapter", "summary"],
                },
            ),
            Tool(
                name="add_foreshadowing",
                description="添加一个伏笔。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "description": "伏笔描述"},
                        "planted_chapter": {"type": "integer", "description": "埋下伏笔的章节"},
                        "related_entities": {"type": "string", "description": "相关实体，逗号分隔"},
                    },
                    "required": ["description", "planted_chapter"],
                },
            ),
            Tool(
                name="resolve_foreshadowing",
                description="将一个伏笔标记为已回收。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "伏笔记录的 ID"},
                        "resolved_chapter": {"type": "integer", "description": "回收章节"},
                        "notes": {"type": "string", "description": "回收说明"},
                    },
                    "required": ["id", "resolved_chapter"],
                },
            ),
            Tool(
                name="list_unresolved_foreshadowings",
                description="列出所有未回收的伏笔。",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="list_characters_by_status",
                description="根据当前状态搜索角色。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status_keyword": {"type": "string", "description": "状态关键词，若省略则返回所有角色"},
                    },
                },
            ),
            Tool(
                name="get_chapter_summary",
                description="获取指定章节的摘要。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "chapter": {"type": "integer", "description": "章节号"},
                    },
                    "required": ["chapter"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            if name == "upsert_character":
                result = await upsert_character(
                    db,
                    arguments["name"],
                    arguments.get("attributes"),
                    arguments.get("current_status"),
                )
            elif name == "get_character_info":
                result = await get_character_info(db, arguments["name"])
            elif name == "add_relationship":
                result = await add_relationship(
                    db,
                    arguments["source"],
                    arguments["target"],
                    arguments["relation"],
                    arguments.get("description"),
                    arguments.get("start_chapter"),
                )
            elif name == "record_plot":
                result = await record_plot(
                    db,
                    arguments["chapter"],
                    arguments["summary"],
                    arguments.get("involved_entities"),
                )
            elif name == "add_foreshadowing":
                result = await add_foreshadowing(
                    db,
                    arguments["description"],
                    arguments["planted_chapter"],
                    arguments.get("related_entities"),
                )
            elif name == "resolve_foreshadowing":
                result = await resolve_foreshadowing(
                    db,
                    arguments["id"],
                    arguments["resolved_chapter"],
                    arguments.get("notes"),
                )
            elif name == "list_unresolved_foreshadowings":
                result = await list_unresolved_foreshadowings(db)
            elif name == "list_characters_by_status":
                result = await list_characters_by_status(
                    db, arguments.get("status_keyword")
                )
            elif name == "get_chapter_summary":
                result = await get_chapter_summary(db, arguments["chapter"])
            else:
                result = f"未知工具：{name}"
            return [TextContent(type="text", text=result)]
        except Exception as e:
            return [TextContent(type="text", text=f"服务器错误：{str(e)}")]

    return server


# ---------- 入口 ----------
def parse_args():
    parser = argparse.ArgumentParser(description="都市言情小说专用 MCP 记忆服务器")
    parser.add_argument(
        "--db",
        default=os.environ.get("NOVEL_DB_PATH", "novel_memory.db"),
        help="数据库文件路径（优先级：命令行 > 环境变量 NOVEL_DB_PATH > 默认 novel_memory.db）",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    server = create_server(args.db)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())