"""跨境货物买卖合同多 Agent 智能审查平台主图编排。

流程：合同读取 -> 5 个专业审查 Agent 并行 -> 综合风险汇总。
"""

from langgraph.graph import StateGraph, END
from graphs.state import GlobalState, GraphInput, GraphOutput
from graphs.nodes.contract_read_node import contract_read_node
from graphs.nodes.party_clause_node import party_clause_node
from graphs.nodes.delivery_clause_node import delivery_clause_node
from graphs.nodes.payment_clause_node import payment_clause_node
from graphs.nodes.compliance_clause_node import compliance_clause_node
from graphs.nodes.dispute_clause_node import dispute_clause_node
from graphs.nodes.risk_summary_node import risk_summary_node

# 状态图：指定全局 State 与图出入参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点（审查类节点标记为 agent，注入各自 LLM 配置）
builder.add_node("contract_read", contract_read_node)
builder.add_node("party_clause", party_clause_node, metadata={"type": "agent", "llm_cfg": "config/party_clause_llm_cfg.json"})
builder.add_node("delivery_clause", delivery_clause_node, metadata={"type": "agent", "llm_cfg": "config/delivery_clause_llm_cfg.json"})
builder.add_node("payment_clause", payment_clause_node, metadata={"type": "agent", "llm_cfg": "config/payment_clause_llm_cfg.json"})
builder.add_node("compliance_clause", compliance_clause_node, metadata={"type": "agent", "llm_cfg": "config/compliance_clause_llm_cfg.json"})
builder.add_node("dispute_clause", dispute_clause_node, metadata={"type": "agent", "llm_cfg": "config/dispute_clause_llm_cfg.json"})
builder.add_node("risk_summary", risk_summary_node, metadata={"type": "agent", "llm_cfg": "config/risk_summary_llm_cfg.json"})

# 设置入口点
builder.set_entry_point("contract_read")

# 合同读取后并行分发到 5 个审查 Agent
builder.add_edge("contract_read", "party_clause")
builder.add_edge("contract_read", "delivery_clause")
builder.add_edge("contract_read", "payment_clause")
builder.add_edge("contract_read", "compliance_clause")
builder.add_edge("contract_read", "dispute_clause")

# 汇聚：等待 5 个并行分支全部完成后进入综合风险汇总
builder.add_edge(
    ["party_clause", "delivery_clause", "payment_clause", "compliance_clause", "dispute_clause"],
    "risk_summary",
)

builder.add_edge("risk_summary", END)

main_graph = builder.compile()