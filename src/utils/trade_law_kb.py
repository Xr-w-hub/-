"""外贸法律知识库检索工具：基于用户导入的法律文档做语义检索（RAG grounding）。

用法（在节点内）：
    from utils.trade_law_kb import search_trade_law
    refs = search_trade_law(state.contract_text, ctx, top_k=6)
返回 [{ "content": 法条原文, "score": 相似度, "source": 来源文档名, "doc_id": "..." }]
"""

import json
import os
from typing import Any, Dict, List, Optional

from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.runtime_ctx.context import Context

DATASET = "coze_doc_knowledge"


def _load_doc_map() -> Dict[str, str]:
    """加载 doc_id -> 来源文档名 映射，用于标注权威来源。"""
    path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), "assets/kb_doc_map.json")
    try:
        with open(path, "r", encoding="utf-8") as fd:
            data = json.load(fd)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        return {}
    return {}


def search_trade_law(
    query: str,
    ctx: Context,
    top_k: int = 6,
    min_score: float = 0.35,
) -> List[Dict[str, Any]]:
    """在知识库中检索与 query 相关的权威法律条文。

    Args:
        query: 检索查询文本（一般传入合同全文或合同相关片段）。
        ctx: 请求追踪上下文（来自节点 runtime.context）。
        top_k: 返回结果数量上限。
        min_score: 最小相似度阈值，低于该阈值的结果被丢弃。

    Returns:
        检索到的法条列表，每个元素包含 content/score/source/doc_id。
    """
    client = KnowledgeClient(config=Config(), ctx=ctx, verbose=False)
    resp = client.search(
        query=query,
        table_names=[DATASET],
        top_k=top_k,
        min_score=min_score,
    )
    mapping = _load_doc_map()
    chunks = getattr(resp, "chunks", None) or []
    results: List[Dict[str, Any]] = []
    for c in chunks:
        doc_id = str(getattr(c, "doc_id", ""))
        content = getattr(c, "content", "") or ""
        score = getattr(c, "score", 0) or 0
        if not content.strip():
            continue
        results.append(
            {
                "content": content.strip(),
                "score": float(score),
                "source": mapping.get(doc_id, "外贸法律法规知识库"),
                "doc_id": doc_id,
            }
        )
    return results