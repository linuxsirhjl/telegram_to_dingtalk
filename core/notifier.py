import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

def _generate_sign(secret: str, timestamp: int) -> str:
    """
    生成钉钉加签

    Args:
        secret: 钉钉机器人密钥
        timestamp: 当前时间戳（毫秒）

    Returns:
        签名字符串
    """
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign

def send_to_dingtalk(
    title: str,
    text: str,
    image_url: Optional[str] = None,
    webhook: Optional[str] = None,
    secret: Optional[str] = None
) -> bool:
    """
    发送消息到钉钉

    Args:
        title: 消息标题
        text: 消息内容
        image_url: 图片 URL（可选）
        webhook: 钉钉 webhook URL（可选，默认使用配置中的）
        secret: 钉钉加签密钥（可选，默认使用配置中的）

    Returns:
        是否发送成功
    """
    webhook = webhook or settings.DINGTALK_WEBHOOK
    secret = secret or settings.DINGTALK_SECRET

    # 构建消息内容
    # 重要：确保消息包含关键词"Telegram"，以满足钉钉自定义关键词安全设置
    md_text = text
    if image_url:
        md_text += f"\n\n![image]({image_url})"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": md_text
        }
    }

    # 如果配置了加签，添加签名参数
    url = webhook
    if secret:
        timestamp = int(time.time() * 1000)
        sign = _generate_sign(secret, timestamp)
        url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        result = resp.json()

        if result.get("errcode") == 0:
            logger.info(f"✅ 消息发送成功: {title}")
            return True
        elif result.get("errcode") == 430104:
            # 内容安全风险，尝试发送简化版本
            logger.warning(f"⚠️ 消息包含敏感内容，尝试发送简化版本")
            return _send_simplified_message(title, webhook, secret)
        else:
            logger.error(f"❌ 钉钉返回错误: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ 发送钉钉消息失败: {e}")
        return False

def _send_simplified_message(title: str, webhook: str, secret: Optional[str]) -> bool:
    """
    发送简化版本的消息（当原消息触发安全审核时）

    Args:
        title: 消息标题
        webhook: 钉钉 webhook URL
        secret: 钉钉加签密钥

    Returns:
        是否发送成功
    """
    # 只发送标题和提示信息
    simplified_text = f"**【Telegram消息提醒】**\n\n收到新消息，但内容可能包含敏感信息，已自动过滤。\n\n请前往 Telegram 查看原消息。"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": simplified_text
        }
    }

    url = webhook
    if secret:
        timestamp = int(time.time() * 1000)
        sign = _generate_sign(secret, timestamp)
        url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        result = resp.json()

        if result.get("errcode") == 0:
            logger.info(f"✅ 简化消息发送成功")
            return True
        else:
            logger.error(f"❌ 简化消息也发送失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 发送简化消息失败: {e}")
        return False
