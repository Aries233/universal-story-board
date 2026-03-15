"""
Universal Story Board - 工作流 Pydantic Schemas
用于工作流触发和状态查询的请求/响应数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime


class WorkflowStartRequest(BaseModel):
    """启动工作流请求"""
    chapter_id: str = Field(description="章节 ID")
    mode: str = Field(default="A", description="工作流模式: A=改编编剧, B=原文模式")

    @field_validator('mode')
    def validate_mode(cls, v):
        if v not in ['A', 'B']:
            raise ValueError("工作流模式必须是 'A' 或 'B'")
        return v


class WorkflowStatusResponse(BaseModel):
    """工作流状态响应"""
    chapter_id: str
    status: str
    current_agent: Optional[str]
    retry_count: int
    error_message: Optional[str]
    progress: Optional[Dict]  # 进度详情
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class WorkflowResult(BaseModel):
    """工作流执行结果"""
    chapter_id: str
    status: str
    message: str
    context: Optional[Dict]  # 执行上下文（包含 script, characters 等）
