"""
Universal Story Board - 项目数据模型
定义项目的基本信息和配置
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Project(SQLModel, table=True):
    """项目模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="项目唯一ID")
    name: str = Field(max_length=200, index=True, description="项目名称")
    description: Optional[str] = Field(default=None, description="项目描述")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    # 配置选项
    workflow_mode: str = Field(default="A", description="工作流模式: A=改编编剧模式, B=原文模式")

    # 快速统计（可选）
    chapter_count: int = Field(default=0, description="章节数量")
    completed_chapters: int = Field(default=0, description="已完成章节")
