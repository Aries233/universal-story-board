"""
Universal Story Board - 资产管理 Pydantic Schemas
用于请求/响应数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime


class AssetCreate(BaseModel):
    """创建资产请求"""
    project_id: str = Field(description="所属项目 ID")
    asset_type: str = Field(description="资产类型：character, scene, prop")
    name: str = Field(min_length=1, max_length=200, description="资产名称")
    description: str = Field(min_length=10, description="资产描述")
    tags: List[str] = Field(default_factory=list, description="标签列表")

    # 角色特有字段
    age: Optional[str] = Field(None, description="年龄段（角色专用）")
    personality: Optional[List[str]] = Field(None, description="性格特征（角色专用）")
    appearance: Optional[str] = Field(None, description="外貌描述（角色专用）")
    costume: Optional[str] = Field(None, description="服装描述（角色专用）")
    props: Optional[List[str]] = Field(None, description="道具列表（角色专用）")

    # 场景特有字段
    time_of_day: Optional[str] = Field(None, description="时间（场景专用）")
    atmosphere: Optional[str] = Field(None, description="氛围（场景专用）")
    environment: Optional[str] = Field(None, description="环境细节（场景专用）")

    # AI 生成提示词
    prompts: Dict[str, str] = Field(default_factory=dict, description="文生图/视频提示词字典")

    # 生成的媒体文件
    image_url: Optional[str] = Field(None, description="生成的图片 URL")
    video_url: Optional[str] = Field(None, description="生成的视频 URL")

    @field_validator('asset_type')
    def validate_asset_type(cls, v):
        valid_types = ['character', 'scene', 'prop']
        if v not in valid_types:
            raise ValueError(f"资产类型必须是以下之一: {', '.join(valid_types)}")
        return v


class AssetUpdate(BaseModel):
    """更新资产请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="资产名称")
    description: Optional[str] = Field(None, min_length=1, description="资产描述")
    tags: Optional[List[str]] = Field(None, description="标签列表")

    # 角色特有字段
    age: Optional[str] = Field(None, description="年龄段（角色专用）")
    personality: Optional[List[str]] = Field(None, description="性格特征（角色专用）")
    appearance: Optional[str] = Field(None, description="外貌描述（角色专用）")
    costume: Optional[str] = Field(None, description="服装描述（角色专用）")
    props: Optional[List[str]] = Field(None, description="道具列表（角色专用）")

    # 场景特有字段
    time_of_day: Optional[str] = Field(None, description="时间（场景专用）")
    atmosphere: Optional[str] = Field(None, description="氛围（场景专用）")
    environment: Optional[str] = Field(None, description="环境细节（场景专用）")

    # AI 生成提示词
    prompts: Optional[Dict[str, str]] = Field(None, description="文生图/视频提示词字典")

    # 生成的媒体文件
    image_url: Optional[str] = Field(None, description="生成的图片 URL")
    video_url: Optional[str] = Field(None, description="生成的视频 URL")


class AssetResponse(BaseModel):
    """资产响应"""
    id: str
    project_id: str
    asset_type: str
    name: str
    description: str
    tags: List[str]

    # 角色特有字段
    age: Optional[str]
    personality: Optional[List[str]]
    appearance: Optional[str]
    costume: Optional[str]
    props: Optional[List[str]]

    # 场景特有字段
    time_of_day: Optional[str]
    atmosphere: Optional[str]
    environment: Optional[str]

    # AI 生成提示词
    prompts: Dict[str, str]

    # 生成的媒体文件
    image_url: Optional[str]
    video_url: Optional[str]

    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    """资产列表响应"""
    total: int
    items: List[AssetResponse]
