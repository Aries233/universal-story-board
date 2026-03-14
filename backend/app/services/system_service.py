"""
Universal Story Board - 系统配置服务
处理服务商凭证和模型路由配置的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.provider_credential import ProviderCredential, ProviderType
from app.models.model_route_config import ModelRouteConfig, ModelType
from app.schemas.system import (
    ProviderCredentialCreate,
    ProviderCredentialUpdate,
    ModelRouteConfigUpdate
)
from app.utils.crypto import get_crypto
from datetime import datetime


class SystemService:
    """系统配置服务"""

    def __init__(self, db: Session):
        self.db = db
        self.crypto = get_crypto()

    def list_credentials(self, provider: Optional[str] = None) -> List[ProviderCredential]:
        """
        获取服务商凭证列表

        Args:
            provider: 筛选服务商类型（可选）

        Returns:
            凭证列表
        """
        query = self.db.query(ProviderCredential)

        if provider:
            query = query.filter(ProviderCredential.provider == provider)

        return query.order_by(ProviderCredential.priority.asc()).all()

    def create_credential(self, data: ProviderCredentialCreate) -> ProviderCredential:
        """
        创建服务商凭证

        Args:
            data: 凭证创建数据

        Returns:
            创建的凭证
        """
        # 加密 API Key
        encrypted_key = self.crypto.encrypt(data.api_key)

        # 脱敏显示
        masked_key = self.crypto.mask_api_key(data.api_key)

        # 创建凭证
        credential = ProviderCredential(
            provider=ProviderType(data.provider),
            api_key=encrypted_key,
            api_key_masked=masked_key,
            name=data.name,
            priority=data.priority,
            config=data.config,
            is_active=True
        )

        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)

        return credential

    def update_credential(
        self,
        credential_id: str,
        data: ProviderCredentialUpdate
    ) -> Optional[ProviderCredential]:
        """
        更新服务商凭证

        Args:
            credential_id: 凭证 ID
            data: 凭证更新数据

        Returns:
            更新后的凭证，不存在则返回 None
        """
        credential = self.db.query(ProviderCredential).filter(
            ProviderCredential.id == credential_id
        ).first()

        if not credential:
            return None

        # 更新字段
        if data.name is not None:
            credential.name = data.name
        if data.is_active is not None:
            credential.is_active = data.is_active
        if data.priority is not None:
            credential.priority = data.priority
        if data.config is not None:
            credential.config = data.config
        if data.api_key is not None:
            # 重新加密 API Key
            credential.api_key = self.crypto.encrypt(data.api_key)
            credential.api_key_masked = self.crypto.mask_api_key(data.api_key)

        credential.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(credential)

        return credential

    def delete_credential(self, credential_id: str) -> bool:
        """
        删除服务商凭证

        Args:
            credential_id: 凭证 ID

        Returns:
            是否删除成功
        """
        credential = self.db.query(ProviderCredential).filter(
            ProviderCredential.id == credential_id
        ).first()

        if not credential:
            return False

        self.db.delete(credential)
        self.db.commit()

        return True

    def list_route_configs(self) -> List[ModelRouteConfig]:
        """
        获取所有路由配置

        Returns:
            路由配置列表
        """
        return self.db.query(ModelRouteConfig).all()

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
