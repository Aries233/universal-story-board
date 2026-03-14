"""
Universal Story Board - 镜头数据模型
定义分镜镜头的详细信息
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import datetime
import uuid


class Shot(SQLModel, table=True):
    """镜头模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="镜头唯一ID")
    chapter_id: str = Field(foreign_key="chapter.id", index=True, description="所属章节ID")

    # 场次信息
    scene_id: str = Field(index=True, description="场次ID")
    scene_name: str = Field(max_length=200, description="场景名称")

    # 镜头基本信息
    shot_number: int = Field(index=True, description="镜头序号")
    timecode: str = Field(description="时间码，格式 HH:MM:SS")
    duration: int = Field(description="时长（秒）")

    # 镜头描述
    shot_type: str = Field(description="景别，如'中景'、'特写'")
    movement: Optional[str] = Field(default=None, description="镜头运动")

    # 内容
    dialogue: Optional[str] = Field(default=None, description="台词")
    audio: Optional[str] = Field(default=None, description="音效")
    visual_prompt: str = Field(description="视听提示词")

    # 生成的媒体文件
    image_url: Optional[str] = Field(default=None, description="生成的分镜图URL")
    video_url: Optional[str] = Field(default=None, description="生成的视频URL")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
