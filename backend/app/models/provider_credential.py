"""
Universal Story Board - 服务商凭证数据模型
支持多服务商 API Key 的动态配置与加密存储
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict
from datetime import datetime
import enum
import uuid


class ProviderType(str, enum.Enum):
    """服务商类型枚举"""
    ZHIPU = "zhipu"              # 智谱 AI（GLM 系列）
    QWEN = "qwen"                # 阿里千问
    GEMINI = "gemini"            # Google Gemini
    OPENAI = "openai"            # OpenAI（GPT 系列）
    STABILITY = "stability"      # Stability AI（Stable Diffusion）
    RUNWAY = "runway"            # Runway（Sora2 等）


class ProviderCredential(SQLModel, table=True):
    """服务商凭证模型（API Key 管理）"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="凭证唯一ID")
    provider: ProviderType = Field(index=True, description="服务商类型")
    api_key: str = Field(description="API Key（AES-256 加密存储）")
    api_key_masked: str = Field(description="脱敏显示（仅前后各4位）")

    # 凭证元数据
    name: str = Field(max_length=200, description="凭证名称（用户自定义）")
    is_active: bool = Field(default=True, index=True, description="是否启用")
    priority: int = Field(default=0, description="优先级（数字越小优先级越高）")

    # 配置项（JSON 字段，灵活存储不同服务商的特定配置）
    config: Dict = Field(default_factory=dict, sa_column=Column(JSON), description="服务商特定配置")

    # 统计数据
    call_count: int = Field(default=0, description="累计调用次数")
    success_count: int = Field(default=0, description="成功次数")
    failure_count: int = Field(default=0, description="失败次数")
    last_called_at: Optional[datetime] = Field(default=None, description="最后调用时间")
    last_error: Optional[str] = Field(default=None, description="最后错误信息")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
