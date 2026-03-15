"""
Universal Story Board - 系统配置 Pydantic Schemas
用于请求/响应数据验证
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class ProviderCredentialCreate(BaseModel):
    """创建服务商凭证请求"""
    provider: str = Field(description="服务商类型：zhipu, qwen, gemini, openai, stability, runway")
    api_key: str = Field(min_length=1, description="API Key（明文，会自动加密存储）")
    name: str = Field(max_length=200, description="凭证名称")
    priority: int = Field(default=0, ge=0, description="优先级（数字越小优先级越高）")
    config: Dict = Field(default_factory=dict, description="服务商特定配置")

    @field_validator('provider')
    def validate_provider(cls, v):
        valid_providers = ['zhipu', 'qwen', 'gemini', 'openai', 'stability', 'runway']
        if v not in valid_providers:
            raise ValueError(f"服务商类型无效，必须是以下之一: {', '.join(valid_providers)}")
        return v


class ProviderCredentialUpdate(BaseModel):
    """更新服务商凭证请求"""
    name: Optional[str] = Field(None, max_length=200, description="凭证名称")
    api_key: Optional[str] = Field(None, min_length=1, description="API Key（明文，会自动加密存储）")
    is_active: Optional[bool] = Field(None, description="是否启用")
    priority: Optional[int] = Field(None, ge=0, description="优先级")
    config: Optional[Dict] = Field(None, description="服务商特定配置")


class ProviderCredentialResponse(BaseModel):
    """服务商凭证响应（脱敏）"""
    id: str
    provider: str
    api_key_masked: str
    name: str
    is_active: bool
    priority: int
    config: Dict
    call_count: int
    success_count: int
    failure_count: int
    last_called_at: Optional[datetime]
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime


class ModelRouteConfigResponse(BaseModel):
    """模型路由配置响应"""

    # Pydantic V2 配置：禁用保护命名空间（允许 model_ 开头的字段）
    model_config = ConfigDict(protected_namespaces=())

    id: str
    model_type: str
    primary_model: str
    fallback_models: List[str]
    model_to_provider: Dict[str, str]
    routing_rules: Dict
    created_at: datetime
    updated_at: datetime


class ModelRouteConfigUpdate(BaseModel):
    """更新模型路由配置请求"""

    # Pydantic V2 配置：禁用保护命名空间（允许 model_ 开头的字段）
    model_config = ConfigDict(protected_namespaces=())

    primary_model: str = Field(description="首选模型")
    fallback_models: List[str] = Field(default_factory=list, description="备用模型列表")
    model_to_provider: Dict[str, str] = Field(default_factory=dict, description="模型到服务商的映射")
    routing_rules: Optional[Dict] = Field(None, description="路由规则配置")


class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    route_configs: List[ModelRouteConfigResponse]
    credentials: List[ProviderCredentialResponse]
