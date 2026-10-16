"""违约与争议解决条款审查 Agent 节点。"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import DisputeClauseInput, DisputeClauseOutput
from utils.llm_utils import get_text_content, parse_json_response


def dispute_clause_node(
    state: DisputeClauseInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> DisputeClauseOutput:
    """
    title: 违约与争议解决审查
    desc: 审查违约责任、解除、不可抗力、适用法律与仲裁管辖等条款风险。
    integrations: 大语言模型
    """
    ctx = runtime.context

    cfg_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), config["metadata"]["llm_cfg"])
    with open(cfg_path, "r", encoding="utf-8") as fd:
        _cfg = json.load(fd)
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    up_tpl = Template(up)
    user_prompt = up_tpl.render(
        {
            "contract_text": state.contract_text,
            "target_country": state.target_country,
            "our_party": state.our_party,
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
    summary = data.get("review_summary", "未获取到违约与争议解决审查结论。")
    if not isinstance(summary, str):
        summary = str(summary)
    risk_items = data.get("risk_items", [])
    if not isinstance(risk_items, list):
        risk_items = []

    return DisputeClauseOutput(dispute_review_summary=summary, dispute_risk_items=risk_items)