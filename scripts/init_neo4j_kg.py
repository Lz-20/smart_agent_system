"""
向 Neo4j 写入一份最小演示知识图谱（基于 RS-12 数字万用表）。

用法（项目根目录下）：
    uv run python scripts/init_neo4j_kg.py

副作用：
- 会先 DETACH DELETE 掉已有的 (:Product {name: 'RS-12数字万用表'}) 子图，
  再重建演示节点与关系，**只影响演示用商品**，不会动到其它产品数据。

Schema 约定（与 app/query_process/agent/nodes/node_query_kg.py 中的 Cypher 对齐）：
    (:Product {name})
    (:Spec      {title, text})
    (:Feature   {title, text})
    (:Component {title, text})
    (:Step      {title, text})
    (:Fault     {title, text})
    (:Product)-[:HAS_SPEC|HAS_FEATURE|HAS_COMPONENT|HAS_STEP|HAS_FAULT]->(节点)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 让脚本可以独立运行：把项目根加到 sys.path，并按项目约定加载 .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from neo4j import GraphDatabase  # noqa: E402  (放在 load_dotenv 之后是有意为之)


PRODUCT_NAME = "RS-12数字万用表"

# 演示数据：按节点类别组织，每条 (title, text)
SEED_DATA = {
    "Spec": [
        ("最大显示", "3 1/2 位液晶显示，最大显示值 1999"),
        ("电源", "9V 6F22 叠层电池一节，欠压指示"),
        ("环境温度", "工作温度 0~40℃，相对湿度 < 75%"),
        ("外形尺寸", "约 145 × 73 × 35 mm"),
    ],
    "Feature": [
        ("过载保护", "全量程过载保护"),
        ("自动归零", "上电后自动校准零点"),
        ("低电指示", "电池电压不足时屏幕显示低电符号"),
    ],
    "Component": [
        ("黑色表笔", "插入 COM 端口，固定为公共负端"),
        ("红色表笔", "根据测量项目插入 VΩ / mA / 10A 三种端口之一"),
        ("功能转换开关", "用于在 VDC / VAC / ADC / Ω 等档位间切换"),
        ("液晶显示屏", "显示测量数值与极性符号"),
    ],
    "Step": [
        ("测量直流电压", "1) 旋钮置于 VDC 档；2) 黑表笔接 COM，红表笔接 VΩ；3) 表笔并联接入被测电路；4) 读取屏幕数值，负号代表反向"),
        ("测量交流电压", "1) 旋钮置于 VAC 档；2) 表笔接法同直流；3) 注意人身安全，避免直接接触带电体"),
        ("测量小电流", "1) 旋钮置于 mA 档；2) 红表笔改插 mA 端口；3) 表笔串联接入电路"),
        ("测量大电流", "1) 旋钮置于 10A 档；2) 红表笔改插 10A 端口；3) 单次连续测量不超过 15 秒"),
        ("测量电阻", "1) 旋钮置于 Ω 档；2) 表笔接法同电压；3) 必须断电测量，避免误差与损坏仪表"),
    ],
    "Fault": [
        ("无显示", "检查电池是否安装到位、电量是否充足；必要时更换 9V 电池"),
        ("读数明显偏离", "检查表笔是否插对端口、量程是否匹配，重新归零后再测"),
        ("保险丝熔断", "在 mA 或 10A 档误测高电压会烧保险丝，需打开后盖更换同规格保险丝"),
    ],
}

REL_BY_LABEL = {
    "Spec": "HAS_SPEC",
    "Feature": "HAS_FEATURE",
    "Component": "HAS_COMPONENT",
    "Step": "HAS_STEP",
    "Fault": "HAS_FAULT",
}


def _strip_env_comment(value: str | None, default: str) -> str:
    """.env 里写 `neo4j #社区版` 这种行尾注释不会被 dotenv 自动剥，这里手动处理。"""
    if not value:
        return default
    return value.split("#", 1)[0].strip() or default


def main() -> int:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = _strip_env_comment(os.getenv("NEO4J_USERNAME"), "neo4j")
    pwd = _strip_env_comment(os.getenv("NEO4J_PASSWORD"), "neo4j")
    db = _strip_env_comment(os.getenv("NEO4J_DATABASE"), "neo4j")

    print(f"[init_kg] 目标: {uri} (db={db}, user={user})")

    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    try:
        driver.verify_connectivity()
    except Exception as e:
        print(f"[init_kg] 连接失败：{e}")
        print("[init_kg] 请先确认 docker compose up -d neo4j 已经把 smart-agent-neo4j 拉起且 healthy。")
        return 1

    total_nodes = 0
    total_rels = 0

    with driver.session(database=db) as session:
        # 1) 唯一约束：每次重跑都先确保有
        session.run(
            "CREATE CONSTRAINT product_name_unique IF NOT EXISTS "
            "FOR (p:Product) REQUIRE p.name IS UNIQUE"
        )

        # 2) 清掉本演示商品的旧子图，避免重复堆数据
        deleted = session.run(
            "MATCH (p:Product {name: $name})-[r]->(n) "
            "DETACH DELETE n "
            "RETURN count(n) AS removed",
            name=PRODUCT_NAME,
        ).single()
        if deleted:
            print(f"[init_kg] 已清理旧演示子图: {deleted['removed']} 个属性节点")

        # 3) 重建 Product 主节点
        session.run("MERGE (p:Product {name: $name})", name=PRODUCT_NAME)
        total_nodes += 1

        # 4) 写入各类别节点 + 关系
        for label, items in SEED_DATA.items():
            rel = REL_BY_LABEL[label]
            for title, text in items:
                session.run(
                    f"""
                    MATCH (p:Product {{name: $name}})
                    CREATE (n:{label} {{title: $title, text: $text}})
                    CREATE (p)-[:{rel}]->(n)
                    """,
                    name=PRODUCT_NAME,
                    title=title,
                    text=text,
                )
                total_nodes += 1
                total_rels += 1

        # 5) 抽样验证
        verify = session.run(
            """
            MATCH (p:Product {name: $name})-[r]->(n)
            RETURN type(r) AS rel, count(n) AS cnt
            ORDER BY rel
            """,
            name=PRODUCT_NAME,
        ).data()

    driver.close()

    print(f"[init_kg] 写入完成：节点 {total_nodes} 个，关系 {total_rels} 条")
    print("[init_kg] 关系按类别统计：")
    for row in verify:
        print(f"    {row['rel']:>16} : {row['cnt']}")
    print("[init_kg] 完成。可在 http://localhost:7474 (neo4j / 见 .env) 用以下 Cypher 验证：")
    print(f"    MATCH (p:Product {{name: '{PRODUCT_NAME}'}})-[r]->(n) RETURN p,r,n LIMIT 50")
    return 0


if __name__ == "__main__":
    sys.exit(main())
