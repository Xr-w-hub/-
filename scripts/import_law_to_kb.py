#!/usr/bin/env python
"""
法条一键入库脚本（替代可视化“添加知识库”入口）

用法（把要新增的法条文档路径作为参数传入）:
    python scripts/import_law_to_kb.py assets/新增法条.docx assets/另一部法.pdf

功能:
    1. 读取每个文档(.docx/.pdf/.txt 等)的文本;
    2. 加【来源：<文件名>】前缀后写入知识库数据集 coze_doc_knowledge;
    3. 自动把 doc_id -> 文件名 映射合并进 assets/kb_doc_map.json,
       使审查节点 references 能正确标注来源。

说明:
    - 本脚本重复导入同一文档会产生重复块，请勿重复运行同一文件;
    - 也可用等价 CLI: coze-coding-ai knowledge add --dataset coze_doc_knowledge --url <url>
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from coze_coding_dev_sdk import (  # noqa: E402
    KnowledgeClient,
    Config,
    KnowledgeDocument,
    DataSourceType,
)
from coze_coding_utils.runtime_ctx.context import new_context  # noqa: E402
from utils.file.file import File, FileOps  # noqa: E402

DATASET = "coze_doc_knowledge"
MAP_PATH = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "assets/kb_doc_map.json")


def load_map(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_map(path: str, mapping: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def main(files):
    ctx = new_context(method="invoke")
    client = KnowledgeClient(config=Config(), ctx=ctx)
    mapping = load_map(MAP_PATH)

    for f in files:
        if not os.path.exists(f):
            print(f"[跳过] 文件不存在: {f}")
            continue
        try:
            text = FileOps.extract_text(File(url=f))
        except Exception as e:
            print(f"[读取失败] {f}: {e}")
            continue
        title = os.path.basename(f)
        content = f"【来源：{title}】\n{text}"
        doc = KnowledgeDocument(source=DataSourceType.TEXT, raw_data=content)
        resp = client.add_documents(documents=[doc], table_name=DATASET)
        code = getattr(resp, "code", None)
        if code not in (0, None):
            print(f"[入库失败] {title}: code={code} msg={getattr(resp, 'msg', '')}")
            continue
        doc_ids = getattr(resp, "doc_ids", None) or []
        for did in doc_ids:
            mapping[str(did)] = title
        print(f"[入库成功] {title} -> {doc_ids}")

    save_map(MAP_PATH, mapping)
    print("映射已更新:", MAP_PATH)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    main(sys.argv[1:])