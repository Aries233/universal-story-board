"""
Universal Story Board - 配置管理模块
负责读取和管理环境变量配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基本信息
    app_name: str = "Universal Story Board"
    app_version: str = "1.0.0"
    debug: bool = True

    # 数据库配置
    database_type: str = "sqlite"  # sqlite | postgresql
    database_url: str = "sqlite:///./usb.db"

    # LLM 配置（GLM-4）
    glm_api_key: str = ""
    glm_model: str = "glm-4-long"

    # 文生图配置（Stable Diffusion - 可选）
    sd_api_url: str = ""
    sd_api_key: str = ""

    # 文生视频配置（Sora2 - 可选）
    sora_api_url: str = ""
    sora_api_key: str = ""

    # 缓存配置
    cache_type: str = "memory"  # memory | redis
    redis_url: str | None = None

    # 速率限制
    rate_limit_enabled: bool = True
    rate_limit_times: int = 100
    rate_limit_seconds: int = 60

    # CORS 配置
    cors_origins: List[str] = ["*"]  # 允许所有来源（开发环境）

    # 日志配置
    log_level: str = "INFO"

    # 加密配置（用于 API Key 加密存储）
    encryption_key: str = ""  # 首次运行时为空，由 CryptoUtils 自动生成

    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
