"""工具函数。

提供 JSON 文件读写、文本截断等辅助功能。
"""

import json
from pathlib import Path
from typing import Any


def load_json(file_path: str | Path) -> list[dict[str, Any]]:
    """从 JSON 文件加载仓库数据。

    Args:
        file_path: JSON 文件路径。

    Returns:
        仓库数据列表。

    Raises:
        FileNotFoundError: 文件不存在时抛出。
        json.JSONDecodeError: JSON 格式错误时抛出。
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 处理原始格式：键名可能是 SQL 查询字符串
    # 取第一个键的值作为数据列表
    if isinstance(data, dict):
        if len(data) == 1:
            value = list(data.values())[0]
            if isinstance(value, list):
                return value
        return [data]

    if isinstance(data, list):
        return data

    raise ValueError(f"不支持的 JSON 格式: {type(data)}")


def save_json(data: list[dict[str, Any]], file_path: str | Path) -> None:
    """将数据保存为 JSON 文件。

    Args:
        data: 要保存的数据列表。
        file_path: 输出文件路径。
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def truncate_text(text: str, max_len: int = 2000) -> str:
    """截断文本到指定长度。

    Args:
        text: 原始文本。
        max_len: 最大长度。

    Returns:
        截断后的文本。
    """
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."