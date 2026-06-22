import logging
from typing import List, Optional
from telethon import TelegramClient
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
from config.settings import settings
import socks

logger = logging.getLogger(__name__)

class TelegramMonitor:
    """Telegram 消息监控器"""

    def __init__(self):
        # 配置代理
        proxy = None
        if settings.PROXY_TYPE and settings.PROXY_HOST and settings.PROXY_PORT:
            proxy_type_map = {
                'socks5': socks.SOCKS5,
                'socks4': socks.SOCKS4,
                'http': socks.HTTP,
                'https': socks.HTTP,
            }
            proxy_type = proxy_type_map.get(settings.PROXY_TYPE.lower())

            if proxy_type:
                # 对于 HTTP 代理，不使用 rdns
                rdns = False if settings.PROXY_TYPE.lower() in ['http', 'https'] else True

                proxy = (
                    proxy_type,
                    settings.PROXY_HOST,
                    int(settings.PROXY_PORT),
                    rdns,
                    settings.PROXY_USERNAME or None,
                    settings.PROXY_PASSWORD or None
                )
                logger.info(f"使用代理: {settings.PROXY_TYPE}://{settings.PROXY_HOST}:{settings.PROXY_PORT}")
            else:
                logger.warning(f"不支持的代理类型: {settings.PROXY_TYPE}")

        self.client = TelegramClient(
            'session',
            int(settings.TELEGRAM_API_ID),
            settings.TELEGRAM_API_HASH,
            proxy=proxy,
            connection_retries=5,
            retry_delay=3
        )
        self.groups = [g.strip() for g in settings.TELEGRAM_GROUPS if g.strip()]

    async def start(self):
        """启动客户端并登录"""
        await self.client.start(phone=settings.TELEGRAM_PHONE)
        logger.info("✅ Telegram 客户端已连接")

        # 验证群组
        for group in self.groups:
            try:
                entity = await self.client.get_entity(group)
                logger.info(f"✅ 已找到群组: {group} ({entity.title})")
            except Exception as e:
                logger.error(f"❌ 无法访问群组 {group}: {e}")

    async def get_recent_messages(self, group: str, limit: int = 10) -> List[Message]:
        """
        获取群组最近的消息

        Args:
            group: 群组标识（用户名或 ID）
            limit: 获取消息数量

        Returns:
            消息列表
        """
        try:
            entity = await self.client.get_entity(group)
            messages = await self.client.get_messages(entity, limit=limit)
            return messages
        except Exception as e:
            logger.error(f"获取群组 {group} 消息失败: {e}")
            return []

    async def download_media(self, message: Message, path: str) -> Optional[str]:
        """
        下载消息中的媒体文件

        Args:
            message: Telegram 消息对象
            path: 保存路径（目录或完整文件路径）

        Returns:
            下载的文件路径，失败返回 None
        """
        try:
            if message.media:
                logger.info(f"开始下载媒体文件: {message.id}")
                file_path = await self.client.download_media(message, path)
                if file_path:
                    logger.info(f"✅ 媒体文件下载成功: {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"下载媒体失败: {e}")
        return None

    async def get_media_info(self, message: Message) -> dict:
        """
        获取媒体文件信息

        Args:
            message: Telegram 消息对象

        Returns:
            媒体信息字典
        """
        info = {
            "has_media": False,
            "media_type": None,
            "file_size": 0,
            "file_name": None,
        }

        if not message.media:
            return info

        info["has_media"] = True

        # 获取媒体类型
        from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

        if isinstance(message.media, MessageMediaPhoto):
            info["media_type"] = "photo"
        elif isinstance(message.media, MessageMediaDocument):
            doc = message.media.document
            info["file_size"] = doc.size if hasattr(doc, 'size') else 0

            # 获取文件名
            for attr in doc.attributes:
                if hasattr(attr, 'file_name'):
                    info["file_name"] = attr.file_name
                    break

            # 判断文档类型
            mime_type = doc.mime_type if hasattr(doc, 'mime_type') else ""
            if mime_type.startswith('video/'):
                info["media_type"] = "video"
            elif mime_type.startswith('audio/'):
                info["media_type"] = "audio"
            elif mime_type.startswith('image/'):
                info["media_type"] = "image"
            else:
                info["media_type"] = "document"

        return info

    async def stop(self):
        """断开客户端连接"""
        await self.client.disconnect()
        logger.info("Telegram 客户端已断开")
