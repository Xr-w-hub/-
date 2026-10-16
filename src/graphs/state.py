"""跨境货物买卖合同多 Agent 智能审查平台 —— 状态定义。"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from utils.file.file import File


class GlobalState(BaseModel):
    """全局过程状态（LangGraph 自动合并节点输出）。"""

    contract_file: Optional[File] = Field(default=None, description="待审查的跨境货物买卖合同文件（审查模式必填）")
    target_country: str = Field(default="越南", description="目标贸易国家：越南/泰国/马来西亚")
    our_party: str = Field(default="", description="我方当事人名称（作为买方或卖方），可空")
    contract_text: str = Field(default="", description="合同全文文本")
    party_review_summary: str = Field(default="", description="主体资格与效力审查分析")
    party_risk_items: List[Dict[str, Any]] = Field(default=[], description="主体资格与效力风险点列表")
    delivery_review_summary: str = Field(default="", description="货物与交付条款审查分析")
    delivery_risk_items: List[Dict[str, Any]] = Field(default=[], description="货物与交付条款风险点列表")
    payment_review_summary: str = Field(default="", description="付款与结算条款审查分析")
    payment_risk_items: List[Dict[str, Any]] = Field(default=[], description="付款与结算条款风险点列表")
    compliance_review_summary: str = Field(default="", description="目标国合规审查分析")
    compliance_risk_items: List[Dict[str, Any]] = Field(default=[], description="目标国合规风险点列表")
    dispute_review_summary: str = Field(default="", description="违约与争议解决审查分析")
    dispute_risk_items: List[Dict[str, Any]] = Field(default=[], description="违约与争议解决风险点列表")
    risk_report: Dict[str, Any] = Field(default={}, description="综合风险审查报告（最终输出）")
    law_file: Optional[File] = Field(default=None, description="待入库的新增法条文件（新增法条模式）")
    dataset_name: str = Field(default="coze_doc_knowledge", description="目标知识库数据集名称")
    kb_add_result: Dict[str, Any] = Field(default={}, description="法条入库结果（新增法条模式输出）")


class GraphInput(BaseModel):
    """工作流输入（审查模式 / 新增法条模式）。"""

    contract_file: Optional[File] = Field(default=None, description="待审查的跨境货物买卖合同文件（审查模式必填）")
    target_country: str = Field(default="越南", description="目标贸易国家，可选：越南、泰国、马来西亚")
    our_party: str = Field(default="", description="我方当事人名称（作为买方或卖方），可选")
    law_file: Optional[File] = Field(default=None, description="待入库的新增法条文件（提供则进入新增法条模式）")
    dataset_name: str = Field(default="coze_doc_knowledge", description="目标知识库数据集名称")


class GraphOutput(BaseModel):
    """工作流输出（按模式返回对应结果）。"""

    risk_report: Optional[Dict[str, Any]] = Field(default=None, description="跨境货物买卖合同综合风险审查报告")
    kb_add_result: Optional[Dict[str, Any]] = Field(default=None, description="新增法条入库结果")


class DecideMode(BaseModel):
    """入口模式分流条件输入。"""

    law_file: Optional[File] = Field(default=None, description="待入库的法条文件，提供则进入新增法条模式")
    contract_file: Optional[File] = Field(default=None, description="待审查合同文件，提供则进入合同审查模式")


class DecideOutput(BaseModel):
    """入口路由节点输出。"""

    mode: str = Field(default="", description="本次运行模式：新增法条 / 合同审查")


class LawKbAddInput(BaseModel):
    """法条入库节点输入。"""

    law_file: Optional[File] = Field(default=None, description="待入库的法条文档（新增法条模式）")
    dataset_name: str = Field(default="coze_doc_knowledge", description="目标知识库数据集名称")


class LawKbAddOutput(BaseModel):
    """法条入库节点输出。"""

    kb_add_result: Dict[str, Any] = Field(..., description="入库结果：状态、来源、doc_id 列表、数据集")


class ContractReadInput(BaseModel):
    """合同读取节点输入。"""

    contract_file: Optional[File] = Field(default=None, description="待审查的买卖合同文件（审查模式必填）")


class ContractReadOutput(BaseModel):
    """合同读取节点输出。"""

    contract_text: str = Field(..., description="合同全文文本")


class PartyClauseInput(BaseModel):
    """主体资格与效力审查节点输入。"""

    contract_text: str = Field(..., description="合同全文文本")
    target_country: str = Field(..., description="目标贸易国家")
    our_party: str = Field(default="", description="我方当事人名称，可空")


class PartyClauseOutput(BaseModel):
    """主体资格与效力审查节点输出。"""

    party_review_summary: str = Field(..., description="主体资格与效力审查分析")
    party_risk_items: List[Dict[str, Any]] = Field(..., description="主体资格与效力风险点列表")


class DeliveryClauseInput(BaseModel):
    """货物与交付条款审查节点输入。"""

    contract_text: str = Field(..., description="合同全文文本")
    target_country: str = Field(..., description="目标贸易国家")
    our_party: str = Field(default="", description="我方当事人名称，可空")


class DeliveryClauseOutput(BaseModel):
    """货物与交付条款审查节点输出。"""

    delivery_review_summary: str = Field(..., description="货物与交付条款审查分析")
    delivery_risk_items: List[Dict[str, Any]] = Field(..., description="货物与交付条款风险点列表")


class PaymentClauseInput(BaseModel):
    """付款与结算条款审查节点输入。"""

    contract_text: str = Field(..., description="合同全文文本")
    target_country: str = Field(..., description="目标贸易国家")
    our_party: str = Field(default="", description="我方当事人名称，可空")


class PaymentClauseOutput(BaseModel):
    """付款与结算条款审查节点输出。"""

    payment_review_summary: str = Field(..., description="付款与结算条款审查分析")
    payment_risk_items: List[Dict[str, Any]] = Field(..., description="付款与结算条款风险点列表")


class ComplianceClauseInput(BaseModel):
    """目标国合规审查节点输入。"""

    contract_text: str = Field(..., description="合同全文文本")
    target_country: str = Field(..., description="目标贸易国家")
    our_party: str = Field(default="", description="我方当事人名称，可空")


class ComplianceClauseOutput(BaseModel):
    """目标国合规审查节点输出。"""

    compliance_review_summary: str = Field(..., description="目标国合规审查分析")
    compliance_risk_items: List[Dict[str, Any]] = Field(..., description="目标国合规风险点列表")


class DisputeClauseInput(BaseModel):
    """违约与争议解决审查节点输入。"""

    contract_text: str = Field(..., description="合同全文文本")
    target_country: str = Field(..., description="目标贸易国家")
    our_party: str = Field(default="", description="我方当事人名称，可空")


class DisputeClauseOutput(BaseModel):
    """违约与争议解决审查节点输出。"""

    dispute_review_summary: str = Field(..., description="违约与争议解决审查分析")
    dispute_risk_items: List[Dict[str, Any]] = Field(..., description="违约与争议解决风险点列表")


class RiskSummaryInput(BaseModel):
    """风险汇总节点输入。"""

    contract_text: str = Field(..., description="合同全文文本")
    target_country: str = Field(..., description="目标贸易国家")
    our_party: str = Field(default="", description="我方当事人名称，可空")
    party_review_summary: str = Field(default="", description="主体资格与效力审查分析")
    party_risk_items: List[Dict[str, Any]] = Field(default=[], description="主体资格与效力风险点列表")
    delivery_review_summary: str = Field(default="", description="货物与交付条款审查分析")
    delivery_risk_items: List[Dict[str, Any]] = Field(default=[], description="货物与交付条款风险点列表")
    payment_review_summary: str = Field(default="", description="付款与结算条款审查分析")
    payment_risk_items: List[Dict[str, Any]] = Field(default=[], description="付款与结算条款风险点列表")
    compliance_review_summary: str = Field(default="", description="目标国合规审查分析")
    compliance_risk_items: List[Dict[str, Any]] = Field(default=[], description="目标国合规风险点列表")
    dispute_review_summary: str = Field(default="", description="违约与争议解决审查分析")
    dispute_risk_items: List[Dict[str, Any]] = Field(default=[], description="违约与争议解决风险点列表")


class RiskSummaryOutput(BaseModel):
    """风险汇总节点输出。"""

    risk_report: Dict[str, Any] = Field(..., description="综合风险审查报告")