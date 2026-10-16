## 项目概述
- **名称**: 跨境货物买卖合同多 Agent 智能审查平台
- **功能**: 面向平陆运河经济带中小微外贸企业，针对越南、泰国、马来西亚跨境货物买卖合同进行多维度智能风险自查，输出结构化综合风险报告。

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| decide | `nodes/decide_node.py` | task | 入口模式路由（新增法条 / 合同审查） | 提供 law_file→"新增法条";否则→"合同审查" | - |
| law_kb_add | `nodes/law_kb_add_node.py` | task | 新增法条入库：读取文件写入知识库并维护来源映射 | - | - |
| contract_read | `nodes/contract_read_node.py` | task | 读取上传的买卖合同并提取全文 | - | - |
| party_clause | `nodes/party_clause_node.py` | agent | 主体资格与合同效力审查 | - | `config/party_clause_llm_cfg.json` |
| delivery_clause | `nodes/delivery_clause_node.py` | agent | 货物与交付条款审查（INCOTERMS/验收/风险转移） | - | `config/delivery_clause_llm_cfg.json` |
| payment_clause | `nodes/payment_clause_node.py` | agent | 付款与结算条款审查（T/T、L/C、汇率） | - | `config/payment_clause_llm_cfg.json` |
| compliance_clause | `nodes/compliance_clause_node.py` | agent | 目标国合规审查（RAG grounding，先检索知识库法条再审查） | - | `config/compliance_clause_llm_cfg.json` |
| dispute_clause | `nodes/dispute_clause_node.py` | agent | 违约与争议解决条款审查（RAG grounding，先检索知识库法条再审查） | - | `config/dispute_clause_llm_cfg.json` |
| risk_summary | `nodes/risk_summary_node.py` | agent | 汇总各维度结论生成综合风险报告 | - | `config/risk_summary_llm_cfg.json` |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

### 图结构（DAG）
```
decide（入口路由）
  ├─ (提供 law_file)─→ law_kb_add ─→ END        # 新增法条入库模式
  └─ (否则)─→ contract_read
                ├──→ party_clause ──────────┐
                ├──→ delivery_clause ───────┤
                ├──→ payment_clause ────────┤ (并行)
                ├──→ compliance_clause ─────┤→ risk_summary → END
                └──→ dispute_clause ────────┘
```

### 技能使用
- `party_clause` / `delivery_clause` / `payment_clause` / `risk_summary` 节点使用「大语言模型」技能。
- `compliance_clause` / `dispute_clause` 节点使用「大语言模型」+「外贸法律知识库」（RAG grounding）。
- 知识库（`KnowledgeClient`）数据集为 `coze_doc_knowledge`，已导入用户提供的法律文档（中国外贸法/海关法/民法典合同编/2020国际贸易术语/争端解决/原产地规则/海关程序/货物贸易/贸易救济/CISG 摘录等，来源见 `assets/kb_doc_map.json`）。

### 共享工具
- `utils/llm_utils.py`: `get_text_content`（安全提取响应文本）、`parse_json_response`（稳定解析 LLM 返回 JSON）。
- `utils/trade_law_kb.py`: `search_trade_law(query, ctx, top_k=6)`，封装知识库语义检索，返回 `{content, score, source}`（法条原文、相关度、来源文档名），用于节点 RAG grounding。
- `law_kb_add` 节点（`nodes/law_kb_add_node.py`）提供「新增法条入库」能力：读取法条文档→加 `【来源：<文件名>】` 前缀→`add_documents` 写入知识库→自动合并 `doc_id→文件名` 到 `assets/kb_doc_map.json`。
- 命令行一键入库备用: `python scripts/import_law_to_kb.py <docx/pdf路径...>`（等价于 `law_kb_add` 节点）。

### 知识库维护（重要）
- 检索使用默认数据集，调用 `KnowledgeClient.search(query, table_names=["coze_doc_knowledge"], top_k, min_score)`。
- 新增法律文档时：读取文本后以 `【来源：<文件名>】` 前缀入库（便于 references 溯源），并通过 `add_documents(source=TEXT)` 写入 `coze_doc_knowledge`，同时把 `doc_id` 与文件名映射追加到 `assets/kb_doc_map.json`。

### 输入输出
- 合同审查模式: 输入 `contract_file`(File 合同文件)、`target_country`(越南/泰国/马来西亚)、`our_party`(我方名称，可选) → 输出 `risk_report`(结构化综合风险报告)
- 新增法条模式: 输入 `law_file`(File 法条文档)、`dataset_name`(默认 `coze_doc_knowledge`) → 输出 `kb_add_result`(入库状态/来源/doc_id 列表)