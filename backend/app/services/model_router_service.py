"""
Universal Story Board - 模型路由配置服务
处理模型路由和凭证的动态解析
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.provider_credential import ProviderCredential, ProviderType
from app.models.model_route_config import ModelRouteConfig, ModelType
from app.schemas.system import ModelRouteConfigUpdate
from datetime import datetime


class ModelRouterService:
    """模型路由服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_route_configs(self) -> List[ModelRouteConfig]:
        """
        获取所有路由配置

        Returns:
            路由配置列表
        """
        return self.db.query(ModelRouteConfig).all()

    def get_route_config(self, model_type: str) -> Optional[ModelRouteConfig]:
        """
        获取指定模型类型的路由配置

        Args:
            model_type: 模型类型（text, image, video）

        Returns:
            路由配置对象，不存在则返回 None
        """
        return self.db.query(ModelRouteConfig).filter(
            ModelRouteConfig.model_type == model_type
        ).first()

    def update_route_config(
        self,
        config_id: str,
        data: ModelRouteConfigUpdate
    ) -> Optional[ModelRouteConfig]:
        """
        更新路由配置

        Args:
            config_id: 配置 ID
            data: 配置更新数据

        Returns:
            更新后的配置，不存在则返回 None
        """
        config = self.db.query(ModelRouteConfig).filter(
            ModelRouteConfig.id == config_id
        ).first()

        if not config:
            return None

        # 更新字段
        config.primary_model = data.primary_model
        config.fallback_models = data.fallback_models
        config.model_to_provider = data.model_to_provider
        if data.routing_rules is not None:
            config.routing_rules = data.routing_rules

        config.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(config)

        return config

    def resolve_model_credential(
        self,
        model_name: str,
        model_type: str
    ) -> Dict:
        """
        解析模型名称，返回对应的服务商和凭证
        支持故障自动切换

        Args:
            model_name: 模型名称
            model_type: 模型类型（text, image, video）

        Returns:
            服务商和凭证信息：
            {
                "provider": 服务商枚举,
                "model": 模型名称,
                "api_key": API Key（已解密）,
                "credential_id": 凭证 ID
            }

        Raises:
            RuntimeError: 如果所有候选模型均不可用
        """
        # 1. 获取路由配置
        route_config = self.get_route_config(model_type)
        if not route_config:
            raise RuntimeError(f"未找到 {model_type} 的路由配置")

        # 2. 确定候选模型列表（首选 + 备用）
        candidate_models = [route_config.primary_model] + route_config.fallback_models

        for candidate_model in candidate_models:
            # 3. 解析模型对应的服务商
            provider_name = route_config.model_to_provider.get(candidate_model)
            if not provider_name:
                continue

            try:
                provider = ProviderType(provider_name)
            except ValueError:
                continue

            # 4. 获取服务商凭证（按优先级排序）
            credentials = self.db.query(ProviderCredential).filter(
                ProviderCredential.provider == provider,
                ProviderCredential.is_active == True
            ).order_by(ProviderCredential.priority.asc()).all()

            if not credentials:
                continue

            # 5. 使用优先级最高的凭证
            credential = credentials[0]

            # 6. 解密 API Key
            from app.utils.crypto import get_crypto
            crypto = get_crypto()
            api_key = crypto.decrypt(credential.api_key)

            return {
                "provider": provider,
                "model": candidate_model,
                "api_key": api_key,
                "credential_id": credential.id
            }

        # 所有候选模型均不可用
        raise RuntimeError(f"无可用模型: {candidate_models}")
