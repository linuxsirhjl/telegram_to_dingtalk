import json
import os
import logging
from typing import Set

logger = logging.getLogger(__name__)

STATE_FILE = "last_state.json"

def load_processed_ids() -> Set[int]:
    """
    加载已处理的消息 ID 集合

    Returns:
        已处理的消息 ID 集合
    """
    if not os.path.exists(STATE_FILE):
        return set()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("processed_ids", []))
    except Exception as e:
        logger.warning(f"加载状态文件失败: {e}")
        return set()

def save_processed_ids(ids: Set[int]) -> None:
    """
    保存已处理的消息 ID 集合

    Args:
        ids: 已处理的消息 ID 集合
    """
    try:
        data = {"processed_ids": list(ids)}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"已保存状态: {len(ids)} 条消息")
    except Exception as e:
        logger.error(f"保存状态文件失败: {e}")

def add_processed_id(message_id: int) -> None:
    """
    添加已处理的消息 ID

    Args:
        message_id: 消息 ID
    """
    ids = load_processed_ids()
    ids.add(message_id)
    save_processed_ids(ids)
