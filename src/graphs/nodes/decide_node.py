"""入口路由节点：根据输入判断运行模式（新增法条 / 合同审查）。"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import DecideMode, DecideOutput


def decide_node(
    state: DecideMode,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> DecideOutput:
    """
    title: 入口路由
    desc: 根据输入判断运行模式：提供法条文件则进入「新增法条」入库流程，否则进入「跨境合同审查」流程。
    """
    # 计算运行模式并透出，便于条件分发与状态回显
    mode = "新增法条" if state.law_file is not None else "合同审查"
    return DecideOutput(mode=mode)