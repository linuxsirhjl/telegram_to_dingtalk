"""
列出你加入的所有 Telegram 群组

运行此脚本可以查看你加入的所有群组的名称、用户名和 ID
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from config.settings import settings
import socks

async def list_groups():
    """列出所有群组"""

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
            print(f"✅ 使用代理: {settings.PROXY_TYPE}://{settings.PROXY_HOST}:{settings.PROXY_PORT}")

    # 创建客户端
    client = TelegramClient(
        'session',
        int(settings.TELEGRAM_API_ID),
        settings.TELEGRAM_API_HASH,
        proxy=proxy,
        connection_retries=5,
        retry_delay=3
    )

    await client.start(phone=settings.TELEGRAM_PHONE)
    print("✅ 已连接到 Telegram\n")
    print("=" * 80)
    print("你加入的群组列表：")
    print("=" * 80)

    # 获取所有对话
    dialogs = await client.get_dialogs()

    group_count = 0
    for dialog in dialogs:
        entity = dialog.entity

        # 只显示群组和超级群组
        if isinstance(entity, (Channel, Chat)):
            group_count += 1

            # 群组名称
            title = entity.title

            # 群组 ID
            group_id = entity.id

            # 用户名（如果是公开群组）
            username = getattr(entity, 'username', None)

            # 群组类型
            if isinstance(entity, Channel):
                if entity.megagroup:
                    group_type = "超级群组"
                elif entity.broadcast:
                    group_type = "频道"
                else:
                    group_type = "群组"
            else:
                group_type = "普通群组"

            print(f"\n{group_count}. {title}")
            print(f"   类型: {group_type}")
            print(f"   ID: {group_id}")

            if username:
                print(f"   用户名: @{username}")
                print(f"   链接: https://t.me/{username}")
                print(f"   ✅ 配置格式: @{username}")
            else:
                print(f"   用户名: (私有群组，无用户名)")
                print(f"   ✅ 配置格式: {group_id}")

            print("-" * 80)

    print(f"\n总共找到 {group_count} 个群组/频道")
    print("\n" + "=" * 80)
    print("使用说明：")
    print("1. 复制上面的 '配置格式' 内容")
    print("2. 填入 .env 文件的 TELEGRAM_GROUPS 配置项")
    print("3. 多个群组用逗号分隔，例如：")
    print("   TELEGRAM_GROUPS=@group1,@group2,-1001234567890")
    print("=" * 80)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_groups())
