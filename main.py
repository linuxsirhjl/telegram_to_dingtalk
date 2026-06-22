import asyncio
import logging
import time
import os
from config.settings import settings
from core.telegram_client import TelegramMonitor
from core.notifier import send_to_dingtalk
from core.storage import load_processed_ids, add_processed_id
from core.message_formatter import format_message
from core.media_handler import get_file_size_mb, upload_to_r2

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

async def process_messages():
    """处理消息的主循环"""

    # 验证配置
    settings.validate()

    # 创建媒体下载目录
    if settings.DOWNLOAD_MEDIA:
        os.makedirs(settings.MEDIA_DIR, exist_ok=True)
        logger.info(f"媒体文件将保存到: {settings.MEDIA_DIR}")

    # 检查 R2 配置
    has_r2 = all([
        settings.R2_ENDPOINT_URL,
        settings.R2_ACCESS_KEY_ID,
        settings.R2_SECRET_ACCESS_KEY,
        settings.R2_BUCKET,
        settings.R2_PUBLIC_BASE_URL,
    ])
    if has_r2:
        logger.info("✅ Cloudflare R2 图床已配置")
    else:
        logger.warning("⚠️ R2 图床未配置，视频将只保存到本地")

    # 初始化 Telegram 客户端
    monitor = TelegramMonitor()
    await monitor.start()

    # 加载已处理的消息 ID
    processed_ids = load_processed_ids()
    logger.info(f"已加载 {len(processed_ids)} 条历史消息记录")

    try:
        while True:
            logger.info("开始检查新消息...")

            # 遍历所有配置的群组
            for group in monitor.groups:
                try:
                    # 获取最近的消息
                    messages = await monitor.get_recent_messages(group, limit=20)

                    # 过滤出未处理的消息
                    new_messages = [
                        msg for msg in messages
                        if msg.id not in processed_ids
                    ]

                    if not new_messages:
                        logger.info(f"群组 {group}: 无新消息")
                        continue

                    logger.info(f"群组 {group}: 发现 {len(new_messages)} 条新消息")

                    # 按时间顺序处理（从旧到新）
                    new_messages.sort(key=lambda m: m.date)

                    for message in new_messages:
                        try:
                            # 获取群组名称
                            entity = await monitor.client.get_entity(group)
                            group_name = getattr(entity, 'title', group)

                            # 获取媒体信息
                            media_info = await monitor.get_media_info(message)

                            # 处理视频下载和上传
                            downloaded_file = None
                            video_url = None

                            if settings.DOWNLOAD_MEDIA and media_info.get("media_type") == "video":
                                file_size_mb = media_info.get("file_size", 0) / (1024 * 1024)

                                if file_size_mb > settings.MAX_VIDEO_SIZE_MB:
                                    logger.warning(
                                        f"视频文件过大 ({file_size_mb:.1f}MB > {settings.MAX_VIDEO_SIZE_MB}MB)，跳过下载"
                                    )
                                else:
                                    logger.info(f"开始下载视频 ({file_size_mb:.1f}MB)...")
                                    downloaded_file = await monitor.download_media(
                                        message,
                                        settings.MEDIA_DIR
                                    )

                                    if downloaded_file:
                                        actual_size = get_file_size_mb(downloaded_file)
                                        logger.info(f"✅ 视频下载完成: {downloaded_file} ({actual_size:.1f}MB)")

                                        # 上传到 R2
                                        if has_r2:
                                            logger.info("开始上传视频到 Cloudflare R2...")
                                            video_url = upload_to_r2(downloaded_file)

                                            if video_url:
                                                logger.info(f"✅ 视频上传成功: {video_url}")
                                                # 上传成功后删除本地文件
                                                try:
                                                    os.unlink(downloaded_file)
                                                    logger.info(f"已删除本地文件: {downloaded_file}")
                                                except Exception as e:
                                                    logger.warning(f"删除本地文件失败: {e}")
                                            else:
                                                logger.warning("视频上传失败，保留本地文件")

                            # 格式化消息
                            title, text = format_message(message, group_name, media_info)

                            # 添加视频链接或本地路径
                            if video_url:
                                # 钉钉支持视频链接预览
                                text += f"\n\n🎬 **视频链接**: {video_url}"
                            elif downloaded_file:
                                text += f"\n\n💾 **视频已下载到本地**: `{downloaded_file}`"

                            # 发送到钉钉
                            success = send_to_dingtalk(title, text)

                            if success:
                                # 标记为已处理
                                processed_ids.add(message.id)
                                add_processed_id(message.id)
                                logger.info(f"✅ 已转发消息 {message.id}")
                            else:
                                logger.warning(f"⚠️ 消息 {message.id} 发送失败，下次重试")

                            # 避免发送过快
                            await asyncio.sleep(1)

                        except Exception as e:
                            logger.error(f"处理消息 {message.id} 失败: {e}")
                            continue

                except Exception as e:
                    logger.error(f"处理群组 {group} 失败: {e}")
                    continue

            # 等待下一次检查
            logger.info(f"等待 {settings.CHECK_INTERVAL} 秒后继续检查...")
            await asyncio.sleep(settings.CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("收到退出信号")
    finally:
        await monitor.stop()

def main():
    """程序入口"""
    try:
        asyncio.run(process_messages())
    except KeyboardInterrupt:
        logger.info("程序已退出")

if __name__ == "__main__":
    main()
