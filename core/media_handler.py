import os
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

def _safe_join_url(base: str, key: str) -> str:
    """安全拼接 URL"""
    b = (base or "").rstrip("/")
    k = (key or "").lstrip("/")
    return f"{b}/{k}" if b else k

def upload_to_r2(file_path: str, *, object_key: Optional[str] = None) -> Optional[str]:
    """
    上传文件到 Cloudflare R2（S3 兼容）

    需要配置：
    - R2_ENDPOINT_URL
    - R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY
    - R2_BUCKET
    - R2_PUBLIC_BASE_URL（用于拼出公网访问 URL）

    Args:
        file_path: 文件路径
        object_key: 可选的对象键，默认使用文件名

    Returns:
        成功返回公网 URL，失败返回 None
    """
    if not (
        settings.R2_ENDPOINT_URL
        and settings.R2_ACCESS_KEY_ID
        and settings.R2_SECRET_ACCESS_KEY
        and settings.R2_BUCKET
        and settings.R2_PUBLIC_BASE_URL
    ):
        logger.debug("R2 配置不完整，跳过 R2 上传")
        return None

    if not file_path or not os.path.exists(file_path):
        logger.error(f"❌ 文件路径不存在: {file_path}")
        return None

    try:
        import boto3
        from botocore.config import Config
    except ImportError as e:
        logger.error(f"❌ 未安装 boto3/botocore，无法使用 R2 上传: {e}")
        logger.info("💡 请运行: pip install boto3")
        return None

    key = object_key or f"telegram_to_dingtalk/{os.path.basename(file_path)}"
    size = os.path.getsize(file_path)
    logger.info(f"正在上传文件到 Cloudflare R2: {file_path}")
    logger.info(f"文件大小: {size} bytes ({size / 1024 / 1024:.2f} MB)")

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

        # 根据文件扩展名判断 Content-Type
        ext = os.path.splitext(file_path)[1].lower()
        content_type_map = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        content_type = content_type_map.get(ext, 'application/octet-stream')

        with open(file_path, "rb") as f:
            s3.put_object(
                Bucket=settings.R2_BUCKET,
                Key=key,
                Body=f,
                ContentType=content_type,
                CacheControl="public, max-age=31536000, immutable",
            )

        url = _safe_join_url(settings.R2_PUBLIC_BASE_URL, key)
        logger.info(f"✅ R2 上传成功: {url}")
        return url

    except Exception as e:
        logger.exception(f"❌ R2 上传错误: {e}")
        return None

def get_file_size_mb(file_path: str) -> float:
    """
    获取文件大小（MB）

    Args:
        file_path: 文件路径

    Returns:
        文件大小（MB）
    """
    if not os.path.exists(file_path):
        return 0
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

