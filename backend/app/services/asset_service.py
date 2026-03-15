"""
Universal Story Board - 资产管理服务
处理资产 CRUD 的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.asset import Asset, AssetType
from app.schemas.asset import AssetCreate, AssetUpdate
from datetime import datetime


class AssetService:
    """资产管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_assets(
        self,
        project_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[int, List[Asset]]:
        """
        获取资产列表

        Args:
            project_id: 项目 ID（可选）
            asset_type: 资产类型（可选）
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (总数, 资产列表)
        """
        query = self.db.query(Asset)

        if project_id:
            query = query.filter(Asset.project_id == project_id)

        if asset_type:
            query = query.filter(Asset.asset_type == AssetType(asset_type))

        total = query.count()
        assets = query\
            .order_by(Asset.updated_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return total, assets

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """
        获取资产详情

        Args:
            asset_id: 资产 ID

        Returns:
            资产对象，不存在则返回 None
        """
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def create_asset(self, data: AssetCreate) -> Asset:
        """
        创建资产

        Args:
            data: 资产创建数据

        Returns:
            创建的资产
        """
        asset = Asset(
            project_id=data.project_id,
            asset_type=AssetType(data.asset_type),
            name=data.name,
            description=data.description,
            tags=data.tags,
            # 角色特有字段
            age=data.age,
            personality=data.personality,
            appearance=data.appearance,
            costume=data.costume,
            props=data.props,
            # 场景特有字段
            time_of_day=data.time_of_day,
            atmosphere=data.atmosphere,
            environment=data.environment,
            # AI 生成提示词
            prompts=data.prompts,
            # 生成的媒体文件
            image_url=data.image_url,
            video_url=data.video_url
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def update_asset(
        self,
        asset_id: str,
        data: AssetUpdate
    ) -> Optional[Asset]:
        """
        更新资产

        Args:
            asset_id: 资产 ID
            data: 资产更新数据

        Returns:
            更新后的资产，不存在则返回 None
        """
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()

        if not asset:
            return None

        # 更新通用字段
        if data.name is not None:
            asset.name = data.name
        if data.description is not None:
            asset.description = data.description
        if data.tags is not None:
            asset.tags = data.tags

        # 更新角色特有字段
        if data.age is not None:
            asset.age = data.age
        if data.personality is not None:
            asset.personality = data.personality
        if data.appearance is not None:
            asset.appearance = data.appearance
        if data.costume is not None:
            asset.costume = data.costume
        if data.props is not None:
            asset.props = data.props

        # 更新场景特有字段
        if data.time_of_day is not None:
            asset.time_of_day = data.time_of_day
        if data.atmosphere is not None:
            asset.atmosphere = data.atmosphere
        if data.environment is not None:
            asset.environment = data.environment

        # 更新 AI 生成提示词
        if data.prompts is not None:
            asset.prompts = data.prompts

        # 更新生成的媒体文件
        if data.image_url is not None:
            asset.image_url = data.image_url
        if data.video_url is not None:
            asset.video_url = data.video_url

        asset.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(asset)

        return asset

    def delete_asset(self, asset_id: str) -> bool:
        """
        删除资产

        Args:
            asset_id: 资产 ID

        Returns:
            是否删除成功
        """
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()

        if not asset:
            return False

        self.db.delete(asset)
        self.db.commit()

        return True
