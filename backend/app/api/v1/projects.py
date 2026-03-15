"""
Universal Story Board - 项目管理 API 路由
提供项目 CRUD 接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.services.project_service import ProjectService
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    session: Session = Depends(get_session)
):
    """
    获取项目列表

    - **skip**: 跳过数量（默认 0）
    - **limit**: 返回数量（默认 20，最大 100）
    """
    service = ProjectService(session)
    total, projects = service.list_projects(skip=skip, limit=limit)

    return {
        "total": total,
        "items": projects
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    session: Session = Depends(get_session)
):
    """
    获取项目详情

    - **project_id**: 项目 ID
    """
    service = ProjectService(session)
    project = service.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return project


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    session: Session = Depends(get_session)
):
    """
    创建项目

    - **name**: 项目名称（必填）
    - **description**: 项目描述（可选）
    - **workflow_mode**: 工作流模式（A=改编编剧，B=原文模式，默认 A）
    """
    service = ProjectService(session)
    project = service.create_project(data)

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    session: Session = Depends(get_session)
):
    """
    更新项目

    - **project_id**: 项目 ID
    - **name**: 项目名称
    - **description**: 项目描述
    - **workflow_mode**: 工作流模式
    """
    service = ProjectService(session)
    project = service.update_project(project_id, data)

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    session: Session = Depends(get_session)
):
    """
    删除项目

    - **project_id**: 项目 ID
    """
    service = ProjectService(session)
    success = service.delete_project(project_id)

    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {"message": "项目已删除"}
