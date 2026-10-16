"""目标国合规审查 Agent 节点（RAG grounding）。"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import ComplianceClauseInput, ComplianceClauseOutput
from utils.llm_utils import get_text_content, parse_json_response
from utils.trade_law_kb import search_trade_law


def compliance_clause_node(
    state: ComplianceClauseInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> ComplianceClauseOutput:
    """
    title: 目标国合规审查
    desc: 先从外贸法律知识库检索相关法条，再基于检索条文（grounding）审查目标国合规风险。
    integrations: 大语言模型、外贸法律知识库
    """
    ctx = runtime.context

    cfg_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), config["metadata"]["llm_cfg"])
    with open(cfg_path, "r", encoding="utf-8") as fd:
        _cfg = json.load(fd)
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # RAG grounding：先从知识库检索与合同相关的权威法条
    refs = search_trade_law(state.contract_text, ctx, top_k=6)
    if refs:
        law_refs = "\n".join("【来源：" + r["source"] + "】" + r["content"] for r in refs)
    else:
        law_refs = "（未从知识库检索到相关法条，请谨慎判断并在每条 references 中明确标注依据缺失）"

    up_tpl = Template(up)
    user_prompt = up_tpl.render(
        {
            "contract_text": state.contract_text,
            "target_country": state.target_country,
            "our_party": state.our_party,
            "law_refs": law_refs,
        }
    )

    client = LLMClient(ctx=ctx)
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt),
    ]
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model"),
        temperature=llm_config.get("temperature"),
        top_p=llm_config.get("top_p"),
        thinking=llm_config.get("thinking"),
        max_completion_tokens=llm_config.get("max_completion_tokens"),
    )

    text = get_text_content(response.content)
    data = parse_json_response(text)
    summary = data.get("review_summary", "未获取到目标国合规审查结论。")
    if not isinstance(summary, str):
        summary = str(summary)
    risk_items = data.get("risk_items", [])
    if not isinstance(risk_items, list):
        risk_items = []

    return ComplianceClauseOutput(compliance_review_summary=summary, compliance_risk_items=risk_items)