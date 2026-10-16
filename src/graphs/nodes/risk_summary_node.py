"""风险汇总 Agent 节点：合并各维度审查结论生成综合风险报告。"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import RiskSummaryInput, RiskSummaryOutput
from utils.llm_utils import get_text_content, parse_json_response


def risk_summary_node(
    state: RiskSummaryInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> RiskSummaryOutput:
    """
    title: 综合风险汇总
    desc: 汇总五个维度审查结论，去重归一，判定整体风险等级并生成综合风险报告。
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
            "party_review_summary": state.party_review_summary,
            "party_risk_items": json.dumps(state.party_risk_items, ensure_ascii=False),
            "delivery_review_summary": state.delivery_review_summary,
            "delivery_risk_items": json.dumps(state.delivery_risk_items, ensure_ascii=False),
            "payment_review_summary": state.payment_review_summary,
            "payment_risk_items": json.dumps(state.payment_risk_items, ensure_ascii=False),
            "compliance_review_summary": state.compliance_review_summary,
            "compliance_risk_items": json.dumps(state.compliance_risk_items, ensure_ascii=False),
            "dispute_review_summary": state.dispute_review_summary,
            "dispute_risk_items": json.dumps(state.dispute_risk_items, ensure_ascii=False),
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
    report = parse_json_response(text)
    if not report:
        report = {"overall_level": "unknown", "overall_summary": "未能解析最终报告", "risk_items": []}

    return RiskSummaryOutput(risk_report=report)