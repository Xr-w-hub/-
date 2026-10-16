## 项目概述
- **名称**: 跨境货物买卖合同多 Agent 智能审查平台
- **功能**: 面向平陆运河经济带中小微外贸企业，针对越南、泰国、马来西亚跨境货物买卖合同进行多维度智能风险自查，输出结构化综合风险报告。

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| contract_read | `nodes/contract_read_node.py` | task | 读取上传的买卖合同并提取全文 | - | - |
| party_clause | `nodes/party_clause_node.py` | agent | 主体资格与合同效力审查 | - | `config/party_clause_llm_cfg.json` |
| delivery_clause | `nodes/delivery_clause_node.py` | agent | 货物与交付条款审查（INCOTERMS/验收/风险转移） | - | `config/delivery_clause_llm_cfg.json` |
| payment_clause | `nodes/payment_clause_node.py` | agent | 付款与结算条款审查（T/T、L/C、汇率） | - | `config/payment_clause_llm_cfg.json` |
| compliance_clause | `nodes/compliance_clause_node.py` | agent | 目标国合规审查（VNM/THA/MYS 法规与进口合规） | - | `config/compliance_clause_llm_cfg.json` |
| dispute_clause | `nodes/dispute_clause_node.py` | agent | 违约与争议解决条款审查 | - | `config/dispute_clause_llm_cfg.json` |
| risk_summary | `nodes/risk_summary_node.py` | agent | 汇总各维度结论生成综合风险报告 | - | `config/risk_summary_llm_cfg.json` |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

### 图结构（DAG）
```
contract_read
  ├──→ party_clause ──────────┐
  ├──→ delivery_clause ───────┤
  ├──→ payment_clause ────────┤ (并行) 
  ├──→ compliance_clause ─────┤→ risk_summary → END
  └──→ dispute_clause ────────┘
```

### 技能使用
- `party_clause` / `delivery_clause` / `payment_clause` / `compliance_clause` / `dispute_clause` / `risk_summary` 节点使用「大语言模型」技能。

### 共享工具
- `utils/llm_utils.py`: `get_text_content`（安全提取响应文本）、`parse_json_response`（稳定解析 LLM 返回 JSON）。

### 输入输出
- 输入: `contract_file`(File 合同文件)、`target_country`(越南/泰国/马来西亚)、`our_party`(我方名称，可选)
- 输出: `risk_report`(结构化综合风险报告)