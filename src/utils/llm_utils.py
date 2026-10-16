"""LLM 通用工具函数：安全提取响应文本与解析 JSON。"""

import json
import re
from typing import Any, Dict, List, Union


def get_text_content(content: Union[str, List[Any], None]) -> str:
    """安全地从 LLM 响应 content 中提取纯文本。

    content 可能是 str / list[dict] / list[str] / None。
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                txt = item.get("text")
                if isinstance(txt, str):
                    parts.append(txt)
        return " ".join(parts)
    return str(content)


def parse_json_response(text: str) -> Dict[str, Any]:
    """从 LLM 返回文本中安全解析出 JSON 字典。

    优先尝试直接解析，失败则抽取代码块或首个 {...} 片段。
    """
    if not text:
        return {}
    text = text.strip()
    # 尝试直接解析
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        pass
    # 抽取 ```json ... ``` 代码块
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if code_block:
        try:
            data = json.loads(code_block.group(1).strip())
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    # 抽取第一个 {...} 片段
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            data = json.loads(brace_match.group(0))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}