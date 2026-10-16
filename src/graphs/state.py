"""跨境货物买卖合同多 Agent 智能审查平台 —— 状态定义。"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from utils.file.file import File


class GlobalState(BaseModel):
    """全局过程状态（LangGraph 自动合并节点输出）。"""

    contract_file: File = Field(..., description="待审查的跨境货物买卖合同文件")
    target_country: str = Field(..., description="目标贸易国家：越南/泰国/马来西亚")
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


class GraphInput(BaseModel):
    """工作流输入。"""

    contract_file: File = Field(..., description="待审查的跨境货物买卖合同文件")
    target_country: str = Field(..., description="目标贸易国家，可选：越南、泰国、马来西亚")
    our_party: str = Field(default="", description="我方当事人名称（作为买方或卖方），可选")


class GraphOutput(BaseModel):
    """工作流输出。"""

    risk_report: Dict[str, Any] = Field(..., description="跨境货物买卖合同综合风险审查报告")


class ContractReadInput(BaseModel):
    """合同读取节点输入。"""

    contract_file: File = Field(..., description="待审查的买卖合同文件")


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