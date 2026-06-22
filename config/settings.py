import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """配置类"""

    # Telegram 配置
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")

    # 钉钉配置
    DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
    DINGTALK_SECRET = os.getenv("DINGTALK_SECRET", "")  # 可选的加签密钥

    # 监控的群组列表
    TELEGRAM_GROUPS = os.getenv("TELEGRAM_GROUPS", "").split(",")

    # 检查间隔
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

    # 代理配置（可选）
    PROXY_TYPE = os.getenv("PROXY_TYPE", "")  # socks5, http, https
    PROXY_HOST = os.getenv("PROXY_HOST", "")
    PROXY_PORT = os.getenv("PROXY_PORT", "")
    PROXY_USERNAME = os.getenv("PROXY_USERNAME", "")
    PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")

    # 媒体下载配置
    DOWNLOAD_MEDIA = os.getenv("DOWNLOAD_MEDIA", "true").lower() == "true"
    MEDIA_DIR = os.getenv("MEDIA_DIR", "downloads")
    MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", 20))  # 钉钉限制

    # Cloudflare R2 图床配置（与 twitter_weasy 相同）
    R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
    R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    R2_BUCKET = os.getenv("R2_BUCKET")
    R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL")

    def validate(self):
        """验证必要的配置项"""
        missing = []

        if not self.TELEGRAM_API_ID:
            missing.append("TELEGRAM_API_ID")
        if not self.TELEGRAM_API_HASH:
            missing.append("TELEGRAM_API_HASH")
        if not self.TELEGRAM_PHONE:
            missing.append("TELEGRAM_PHONE")
        if not self.DINGTALK_WEBHOOK:
            missing.append("DINGTALK_WEBHOOK")
        if not self.TELEGRAM_GROUPS or not any(g.strip() for g in self.TELEGRAM_GROUPS):
            missing.append("TELEGRAM_GROUPS")

        if missing:
            raise RuntimeError(
                f"❌ 缺少必要环境变量: {', '.join(missing)}\n"
                f"请复制 .env.example 为 .env 并填写配置"
            )

settings = Settings()
