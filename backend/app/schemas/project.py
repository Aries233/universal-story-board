"""
Universal Story Board - 项目管理 Pydantic Schemas
用于请求/响应数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    workflow_mode: str = Field(default="A", description="工作流模式: A=改编编剧, B=原文模式")

    @field_validator('workflow_mode')
    def validate_workflow_mode(cls, v):
        if v not in ['A', 'B']:
            raise ValueError("工作流模式必须是 'A' 或 'B'")
        return v


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    workflow_mode: Optional[str] = Field(None, description="工作流模式: A=改编编剧, B=原文模式")

    @field_validator('workflow_mode')
    def validate_workflow_mode(cls, v):
        if v is not None and v not in ['A', 'B']:
            raise ValueError("工作流模式必须是 'A' 或 'B'")
        return v


class ProjectResponse(BaseModel):
    """项目响应"""
    id: str
    name: str
    description: Optional[str]
    workflow_mode: str
    chapter_count: int
    completed_chapters: int
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int
    items: List[ProjectResponse]
