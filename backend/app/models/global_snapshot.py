"""
Universal Story Board - 全局快照数据模型
定义项目的全局状态快照，用于跨章节的上下文管理
"""
from sqlmodel import SQLModel, Field, Column, JSON, ForeignKey
from typing import Optional, Dict
from datetime import datetime
import uuid


class GlobalSnapshot(SQLModel, table=True):
    """全局状态快照模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="快照唯一ID")
    project_id: str = Field(foreign_key="project.id", index=True, description="所属项目ID")
    version: int = Field(default=1, description="快照版本号")

    # 全局状态数据（JSON 字段）
    plot_summary: str = Field(default="", description="剧情摘要")
    characters: Dict = Field(default_factory=dict, sa_column=Column(JSON), description="角色资产引用字典")
    scenes: Dict = Field(default_factory=dict, sa_column=Column(JSON), description="场景资产引用字典")
    style_guide: Dict = Field(default_factory=dict, sa_column=Column(JSON), description="风格规范字典")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    chapter_count: int = Field(default=0, description="累计处理章节数")
