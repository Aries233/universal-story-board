"""
Universal Story Board - 资产数据模型
定义角色、场景、道具等资产的详细信息
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, List
from datetime import datetime
import enum
import uuid


class AssetType(str, enum.Enum):
    """资产类型枚举"""
    CHARACTER = "character"  # 角色
    SCENE = "scene"          # 场景
    PROP = "prop"            # 道具


class Asset(SQLModel, table=True):
    """资产模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="资产唯一ID")
    project_id: str = Field(foreign_key="project.id", index=True, description="所属项目ID")
    asset_type: AssetType = Field(index=True, description="资产类型")

    # 基本信息
    name: str = Field(max_length=200, index=True, description="资产名称")
    description: str = Field(description="资产描述")
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="标签列表")

    # 角色特有字段
    age: Optional[str] = Field(default=None, description="年龄段（角色专用）")
    personality: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="性格特征（角色专用）")
    appearance: Optional[str] = Field(default=None, description="外貌描述（角色专用）")
    costume: Optional[str] = Field(default=None, description="服装描述（角色专用）")
    props: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="道具列表（角色专用）")

    # 场景特有字段
    time_of_day: Optional[str] = Field(default=None, description="时间（场景专用）")
    atmosphere: Optional[str] = Field(default=None, description="氛围（场景专用）")
    environment: Optional[str] = Field(default=None, description="环境细节（场景专用）")

    # AI 生成提示词
    prompts: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON), description="文生图/视频提示词字典")

    # 生成的媒体文件
    image_url: Optional[str] = Field(default=None, description="生成的图片URL")
    video_url: Optional[str] = Field(default=None, description="生成的视频URL")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
