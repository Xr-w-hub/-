"""合同读取节点：从文件对象中提取合同全文。"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from utils.file.file import FileOps
from graphs.state import ContractReadInput, ContractReadOutput


def contract_read_node(
    state: ContractReadInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> ContractReadOutput:
    """
    title: 合同文本读取
    desc: 读取上传的买卖合同文件并提取全文文本，作为各审查 Agent 的输入。
    """
    ctx = runtime.context
    _ = ctx

    if state.contract_file is None:
        raise ValueError("审查模式缺少必填输入：合同文件 contract_file")

    content = FileOps.extract_text(state.contract_file)

    return ContractReadOutput(contract_text=content)