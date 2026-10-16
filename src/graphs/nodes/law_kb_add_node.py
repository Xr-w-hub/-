"""法条入库节点：读取上传的法条文档，写入知识库数据集并返回入库结果。"""

import os
import json
from urllib.parse import urlparse, unquote

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType
from utils.file.file import File, FileOps
from graphs.state import LawKbAddInput, LawKbAddOutput


def _extract_title(url: str) -> str:
    """从文件 URL 或本地路径提取来源文件名。"""
    if not url:
        return "unknown"
    parsed = urlparse(url)
    path = unquote(parsed.path or parsed.netloc or url)
    name = os.path.basename(path) or "unknown"
    return name


def law_kb_add_node(
    state: LawKbAddInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> LawKbAddOutput:
    """
    title: 法条入库
    desc: 将上传的法条文档读取为文本后写入指定知识库数据集，并返回入库结果（含来源文档与 doc_id）。
    integrations: 知识库
    """
    ctx = runtime.context
    if state.law_file is None:
        return LawKbAddOutput(kb_add_result={"status": "failed", "message": "新增法条模式缺少必填输入：法条文件 law_file"})
    dataset = state.dataset_name or "coze_doc_knowledge"
    source = _extract_title(state.law_file.url)

    try:
        text = FileOps.extract_text(state.law_file)
    except Exception as e:
        return LawKbAddOutput(kb_add_result={"status": "failed", "message": f"读取法条文档失败: {e}"})

    content = f"【来源：{source}】\n{text}"
    client = KnowledgeClient(config=Config(), ctx=ctx)
    doc = KnowledgeDocument(source=DataSourceType.TEXT, raw_data=content)
    try:
        resp = client.add_documents(documents=[doc], table_name=dataset)
    except Exception as e:
        return LawKbAddOutput(kb_add_result={"status": "failed", "source": source, "message": f"调用知识库失败: {e}"})

    code = getattr(resp, "code", None)
    if code not in (0, None):
        return LawKbAddOutput(
            kb_add_result={
                "status": "failed",
                "source": source,
                "dataset": dataset,
                "message": f"入库失败 code={code} msg={getattr(resp, 'msg', '')}",
            }
        )

    doc_ids = getattr(resp, "doc_ids", None) or []

    # 将 doc_id -> 来源合并进本地映射，供审查节点 references 溯源
    try:
        map_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "assets/kb_doc_map.json")
        mapping: dict = {}
        if os.path.exists(map_path):
            with open(map_path, "r", encoding="utf-8") as f:
                mapping = json.load(f)
        for did in doc_ids:
            mapping[str(did)] = source
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return LawKbAddOutput(
        kb_add_result={
            "status": "success",
            "source": source,
            "dataset": dataset,
            "doc_ids": doc_ids,
            "message": "法条已写入知识库并完成来源映射",
        }
    )