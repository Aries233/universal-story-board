"""
Universal Story Board - 章节管理 API 路由
提供章节 CRUD 接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.services.chapter_service import ChapterService
from app.schemas.chapter import (
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterListResponse,
    ChapterBatchCreate
)

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("", response_model=ChapterListResponse)
async def list_chapters(
    project_id: str = Query(None, description="项目 ID"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    session: Session = Depends(get_session)
):
    """
    获取章节列表

    - **project_id**: 项目 ID（可选）
    - **skip**: 跳过数量（默认 0）
    - **limit**: 返回数量（默认 20，最大 100）
    """
    service = ChapterService(session)
    total, chapters = service.list_chapters(
        project_id=project_id,
        skip=skip,
        limit=limit
    )

    return {
        "total": total,
        "items": chapters
    }


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: str,
    session: Session = Depends(get_session)
):
    """
    获取章节详情

    - **chapter_id**: 章节 ID
    """
    service = ChapterService(session)
    chapter = service.get_chapter(chapter_id)

    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    return chapter


@router.post("", response_model=ChapterResponse, status_code=201)
async def create_chapter(
    data: ChapterCreate,
    session: Session = Depends(get_session)
):
    """
    创建章节

    - **project_id**: 项目 ID
    - **chapter_number**: 章节序号
    - **title**: 章节标题
    - **original_text**: 原始文本内容
    """
    service = ChapterService(session)
    chapter = service.create_chapter(data)

    return chapter


@router.post("/batch", response_model=list[ChapterResponse], status_code=201)
async def batch_create_chapters(
    data: ChapterBatchCreate,
    session: Session = Depends(get_session)
):
    """
    批量创建章节

    - **project_id**: 项目 ID
    - **chapters**: 章节列表（每个章节只包含章节序号、标题、文本）
    """
    service = ChapterService(session)

    # 直接传递 ChapterBatchCreate 对象
    chapters = service.batch_create_chapters(data)

    return chapters


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: str,
    data: ChapterUpdate,
    session: Session = Depends(get_session)
):
    """
    更新章节

    - **chapter_id**: 章节 ID
    - **title**: 章节标题
    - **original_text**: 原始文本内容
    - **status**: 处理状态
    - **retry_count**: 重试次数
    """
    service = ChapterService(session)
    chapter = service.update_chapter(chapter_id, data)

    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    return chapter


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: str,
    session: Session = Depends(get_session)
):
    """
    删除章节

    - **chapter_id**: 章节 ID
    """
    service = ChapterService(session)
    success = service.delete_chapter(chapter_id)

    if not success:
        raise HTTPException(status_code=404, detail="章节不存在")

    return {"message": "章节已删除"}
