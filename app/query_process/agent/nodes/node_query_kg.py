import os
import sys
from typing import List, Dict, Any

from app.utils.task_utils import add_running_task, add_done_task
from app.clients.neo4j_utils import get_neo4j_driver
from app.core.logger import logger


# 围绕已确认商品名查询其相关属性 / 故障 / 操作 / 组件等关系。
# Schema 约定（由 scripts/init_neo4j_kg.py 写入演示数据）：
#   节点:  (:Product {name})
#          (:Spec {title, text}) (:Feature {title, text})
#          (:Fault {title, text}) (:Step {title, text}) (:Component {title, text})
#   关系:  (:Product)-[:HAS_SPEC|HAS_FEATURE|HAS_FAULT|HAS_STEP|HAS_COMPONENT]->(节点)
KG_CYPHER = """
MATCH (p:Product) WHERE p.name IN $names
MATCH (p)-[r]->(n)
RETURN p.name           AS product,
       type(r)          AS rel,
       coalesce(labels(n)[0], '')                AS label,
       coalesce(n.title, '')                     AS title,
       coalesce(n.text, n.value, '')             AS text,
       elementId(n)                              AS nid
LIMIT 50
"""


def _format_chunk(rec: Dict[str, Any]) -> Dict[str, Any]:
    """把一条 Cypher 记录格式化为下游 RRF / Rerank 能识别的 chunk-like 结构。"""
    product = rec.get("product") or ""
    rel = rec.get("rel") or ""
    label = rec.get("label") or ""
    title = (rec.get("title") or "").strip()
    text = (rec.get("text") or "").strip()
    nid = rec.get("nid") or ""

    head = f"【{product} - {label}/{rel}】"
    body_parts = [p for p in (title, text) if p]
    content = (head + " " + " ".join(body_parts)).strip()

    return {
        "chunk_id": f"kg::{rel}::{nid}",
        "content": content,
        "item_name": product,
        # KG 命中默认给一个常量分；真正的优先级靠 RRF 通过排名（rank）来体现。
        "score": 1.0,
    }


def node_query_kg(state):
    """
    节点功能：在 Neo4j 知识图谱中按已确认商品名做关系查询，返回 chunk-like 列表写入 state.kg_chunks。

    数据流：
      上游  node_item_name_confirm 写入 state.item_names
      本节点 → state.kg_chunks: List[Dict]，与 embedding_chunks 保持兼容字段（chunk_id / content / item_name / score）
      下游  node_rrf 把 kg_chunks 作为一路融入 RRF（权重 0.5），最终交给 rerank + answer_output
    """
    logger.info("---node_query_kg (知识图谱查询) 开始处理---")
    add_running_task(state["session_id"], sys._getframe().f_code.co_name, state.get("is_stream"))

    item_names: List[str] = state.get("item_names") or []
    kg_chunks: List[Dict[str, Any]] = []

    if not item_names:
        logger.info("node_query_kg: item_names 为空，跳过 KG 查询")
        add_done_task(state['session_id'], sys._getframe().f_code.co_name, state.get("is_stream"))
        return {"kg_chunks": []}

    try:
        driver = get_neo4j_driver()
        # NEO4J_DATABASE 在社区版只能是 'neo4j'；这里读环境变量但容错：.env 中可能写为 `neo4j #注释`，需剥掉评论
        db_raw = os.getenv("NEO4J_DATABASE", "neo4j") or "neo4j"
        db = db_raw.split("#", 1)[0].strip() or "neo4j"

        with driver.session(database=db) as session:
            logger.info(f"node_query_kg: Cypher 查询，item_names={item_names}")
            result = session.run(KG_CYPHER, names=item_names)
            for rec in result:
                kg_chunks.append(_format_chunk(rec.data()))

        logger.info(f"node_query_kg: 命中 {len(kg_chunks)} 条 KG 关系")
    except Exception as e:
        # KG 不可用不应阻塞主流程：与 web_search_mcp 一致，优雅降级
        logger.error(f"node_query_kg: 查询失败，降级返回空结果: {e}", exc_info=True)
        kg_chunks = []

    add_done_task(state['session_id'], sys._getframe().f_code.co_name, state.get("is_stream"))
    logger.info("---node_query_kg 处理结束---")
    return {"kg_chunks": kg_chunks}


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print(">>> 启动 node_query_kg 本地测试")
    print("=" * 50)

    test_state = {
        "session_id": "test_kg_session_001",
        "is_stream": False,
        "item_names": ["RS-12数字万用表"],
    }

    try:
        result = node_query_kg(test_state)
        chunks = result.get("kg_chunks", [])
        print(f"\n>>> 测试完成！KG 命中 {len(chunks)} 条")
        for i, c in enumerate(chunks[:5], 1):
            print(f"[{i}] chunk_id={c['chunk_id']}")
            print(f"    content={c['content'][:120]}")
        if not chunks:
            print(">>> 提示：图谱为空，先跑 scripts/init_neo4j_kg.py 写入演示数据")
    except Exception as e:
        logger.exception(f"测试运行失败: {e}")