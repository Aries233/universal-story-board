"""
Universal Story Board - 章节数据模型
定义章节的基本信息、状态和处理结果
"""
from sqlmodel import SQLModel, Field, Column, JSON, ForeignKey
from typing import Optional, Dict
from datetime import datetime
import enum
import uuid


class ChapterStatus(str, enum.Enum):
    """章节处理状态枚举"""
    PENDING = "pending"                # 待处理
    PROCESSING = "processing"          # 处理中
    COMPLETED = "completed"            # 已完成
    FAILED = "failed"                  # 失败
    MANUAL_INTERVENTION = "manual_intervention"  # 需人工介入


class Chapter(SQLModel, table=True):
    """章节模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="章节唯一ID")
    project_id: str = Field(foreign_key="project.id", index=True, description="所属项目ID")

    # 章节基本信息
    chapter_number: int = Field(index=True, description="章节序号")
    title: str = Field(max_length=200, description="章节标题")
    original_text: str = Field(description="原始文本内容（B轨模式使用）")

    # 处理状态
    status: ChapterStatus = Field(default=ChapterStatus.PENDING, index=True, description="处理状态")
    current_agent: Optional[str] = Field(default=None, description="当前处理的Agent")
    retry_count: int = Field(default=0, description="重试次数")

    # 处理结果（JSON 字段）
    script: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="编剧生成的剧本")
    characters: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="角色资产")
    scenes: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="场景资产")
    shots: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="分镜镜头")
    doctor_feedback: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="剧本医生反馈")
    style_guide: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="风格规范")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    started_at: Optional[datetime] = Field(default=None, description="开始处理时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")

    # 快照引用
    snapshot_id: Optional[str] = Field(default=None, foreign_key="globalsnapshot.id", description="引用的全局快照ID")
