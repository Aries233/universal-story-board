"""
Universal Story Board - 模型路由配置数据模型
支持多模态任务的动态路由与故障切换
"""
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import ConfigDict
from typing import Dict, List
from datetime import datetime
import enum
import uuid


class ModelType(str, enum.Enum):
    """模型类型枚举"""
    TEXT = "text"                # 文本大模型
    IMAGE = "image"              # 文生图模型
    VIDEO = "video"              # 文生视频模型


class ModelRouteConfig(SQLModel, table=True):
    """模型路由配置模型"""

    # Pydantic V2 配置：禁用保护命名空间（允许 model_ 开头的字段）
    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="路由配置唯一ID")
    model_type: ModelType = Field(index=True, description="模型类型")

    # 路由策略
    primary_model: str = Field(description="首选模型（如 glm-4-plus）")
    fallback_models: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="备用模型列表")

    # 模型映射（模型名称 → 服务商）
    model_to_provider: Dict[str, str] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="模型名称到服务商的映射（如 {'glm-4-plus': 'zhipu'}）"
    )

    # 路由规则（JSON 字段，灵活配置路由策略）
    routing_rules: Dict = Field(default_factory=dict, sa_column=Column(JSON), description="路由规则配置")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


# 默认路由配置示例（初始化时使用）
DEFAULT_ROUTE_CONFIGS = [
    {
        "model_type": ModelType.TEXT,
        "primary_model": "glm-4-plus",
        "fallback_models": ["qwen-max", "gemini-pro", "gpt-4-turbo"],
        "model_to_provider": {
            "glm-4-plus": "zhipu",
            "glm-4-long": "zhipu",
            "qwen-max": "qwen",
            "gemini-pro": "gemini",
            "gpt-4-turbo": "openai"
        },
        "routing_rules": {
            "auto_retry": True,
            "max_retries": 3
        }
    },
    {
        "model_type": ModelType.IMAGE,
        "primary_model": "cogview-3",
        "fallback_models": ["sd3", "dalle-3"],
        "model_to_provider": {
            "cogview-3": "zhipu",
            "sd3": "stability",
            "dalle-3": "openai"
        },
        "routing_rules": {
            "auto_retry": True,
            "max_retries": 2
        }
    },
    {
        "model_type": ModelType.VIDEO,
        "primary_model": "sora2",
        "fallback_models": ["runway-gen2"],
        "model_to_provider": {
            "sora2": "runway",
            "runway-gen2": "runway"
        },
        "routing_rules": {
            "auto_retry": True,
            "max_retries": 1
        }
    }
]
