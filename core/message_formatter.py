from datetime import datetime
from telethon.tl.types import Message
import re

def _sanitize_content(text: str) -> str:
    """
    清理可能触发钉钉安全审核的内容

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    if not text:
        return text

    # 替换敏感词为星号（可根据需要扩展）
    # 这里只做基础处理，避免触发钉钉审核

    # 移除 URL 中的敏感部分
    text = re.sub(r'https?://[^\s]+', '[链接已隐藏]', text)

    # 限制文本长度，避免过长内容触发审核
    if len(text) > 500:
        text = text[:500] + "...(内容过长已截断)"

    return text

def format_message(message: Message, group_name: str, media_info: dict = None) -> tuple[str, str]:
    """
    格式化 Telegram 消息为钉钉消息格式

    Args:
        message: Telegram 消息对象
        group_name: 群组名称
        media_info: 媒体信息字典（可选）

    Returns:
        (标题, 消息内容) 元组
    """
    # 提取发送者信息
    sender_name = "未知用户"
    if message.sender:
        if hasattr(message.sender, 'first_name'):
            sender_name = message.sender.first_name or ""
            if hasattr(message.sender, 'last_name') and message.sender.last_name:
                sender_name += f" {message.sender.last_name}"
        elif hasattr(message.sender, 'title'):
            sender_name = message.sender.title

    # 格式化时间
    msg_time = message.date
    time_str = msg_time.strftime("%Y年%m月%d日 %H:%M:%S")

    # 构建标题（包含关键词"Telegram"）
    title = f"Telegram消息 - {group_name}"

    # 构建消息内容（第一行包含关键词"Telegram"以满足钉钉安全设置）
    text_parts = [
        f"**【Telegram消息提醒】**",
        f"**群组**: {group_name}",
        f"**发送者**: {sender_name}",
        f"**时间**: {time_str}",
        "",
    ]

    # 添加消息文本（清理敏感内容）
    if message.text:
        sanitized_text = _sanitize_content(message.text)
        text_parts.append(f"**内容**:\n{sanitized_text}")

    # 添加媒体信息
    if media_info and media_info.get("has_media"):
        media_type = media_info.get("media_type")
        file_size = media_info.get("file_size", 0)
        file_name = media_info.get("file_name")

        if media_type == "photo":
            text_parts.append("\n📷 *包含图片*")
        elif media_type == "video":
            size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
            text_parts.append(f"\n🎬 *包含视频* ({size_mb:.1f}MB)")
            if file_name:
                text_parts.append(f"   文件名: {file_name}")
        elif media_type == "audio":
            text_parts.append("\n🎵 *包含音频*")
        elif media_type == "document":
            text_parts.append("\n📎 *包含文件*")
            if file_name:
                text_parts.append(f"   文件名: {file_name}")
    elif message.media:
        # 兼容旧版本
        media_type = type(message.media).__name__
        if "Photo" in media_type:
            text_parts.append("\n📷 *包含图片*")
        elif "Document" in media_type:
            text_parts.append("\n📎 *包含文件*")
        elif "Video" in media_type:
            text_parts.append("\n🎬 *包含视频*")
        else:
            text_parts.append(f"\n📎 *包含媒体: {media_type}*")

    # 添加消息链接（如果是公开群组）
    if hasattr(message, 'chat') and hasattr(message.chat, 'username') and message.chat.username:
        msg_link = f"https://t.me/{message.chat.username}/{message.id}"
        text_parts.append(f"\n[查看原消息]({msg_link})")

    text = "\n".join(text_parts)

    return title, text
