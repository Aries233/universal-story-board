"""
Universal Story Board - 章节管理 Pydantic Schemas
用于请求/响应数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime


class ChapterCreate(BaseModel):
    """创建章节请求"""
    project_id: str = Field(description="所属项目 ID")
    chapter_number: int = Field(gt=0, description="章节序号")
    title: str = Field(min_length=1, max_length=200, description="章节标题")
    original_text: str = Field(min_length=1, description="原始文本内容")


class ChapterUpdate(BaseModel):
    """更新章节请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="章节标题")
    original_text: Optional[str] = Field(None, min_length=1, description="原始文本内容")
    status: Optional[str] = Field(None, description="处理状态")
    current_agent: Optional[str] = Field(None, description="当前处理 Agent")
    retry_count: Optional[int] = Field(None, ge=0, description="重试次数")


class ChapterResponse(BaseModel):
    """章节响应"""
    id: str
    project_id: str
    chapter_number: int
    title: str
    original_text: str
    status: str
    current_agent: Optional[str]
    retry_count: int
    script: Optional[Dict]
    doctor_feedback: Optional[Dict]
    style_guide: Optional[Dict]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class ChapterListResponse(BaseModel):
    """章节列表响应"""
    total: int
    items: List[ChapterResponse]


class ChapterBatchItem(BaseModel):
    """批量创建章节的简化项（不含 project_id）"""
    chapter_number: int = Field(gt=0, description="章节序号")
    title: str = Field(min_length=1, max_length=200, description="章节标题")
    original_text: str = Field(min_length=1, description="原始文本内容")


class ChapterBatchCreate(BaseModel):
    """批量创建章节请求"""
    project_id: str = Field(description="所属项目 ID")
    chapters: List[ChapterBatchItem] = Field(min_length=1, description="章节列表（每个章节只包含章节序号、标题、文本）")

    @field_validator('chapters')
    def validate_chapters(cls, v):
        # 检查章节序号是否重复
        chapter_numbers = [c.chapter_number for c in v]
        if len(chapter_numbers) != len(set(chapter_numbers)):
            raise ValueError("章节序号不能重复")
        return v
