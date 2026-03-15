"""
Universal Story Board - 资产管理 API 路由
提供资产 CRUD 接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.services.asset_service import AssetService
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse
)

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse)
async def list_assets(
    project_id: str = Query(None, description="项目 ID"),
    asset_type: str = Query(None, description="资产类型：character, scene, prop"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    session: Session = Depends(get_session)
):
    """
    获取资产列表

    - **project_id**: 项目 ID（可选）
    - **asset_type**: 资产类型（可选）
    - **skip**: 跳过数量（默认 0）
    - **limit**: 返回数量（默认 20，最大 100）
    """
    service = AssetService(session)
    total, assets = service.list_assets(
        project_id=project_id,
        asset_type=asset_type,
        skip=skip,
        limit=limit
    )

    return {
        "total": total,
        "items": assets
    }


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    session: Session = Depends(get_session)
):
    """
    获取资产详情

    - **asset_id**: 资产 ID
    """
    service = AssetService(session)
    asset = service.get_asset(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    return asset


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    data: AssetCreate,
    session: Session = Depends(get_session)
):
    """
    创建资产

    - **project_id**: 项目 ID
    - **asset_type**: 资产类型（character, scene, prop）
    - **name**: 资产名称
    - **description**: 资产描述
    - **tags**: 标签列表
    - **prompts**: 文生图/视频提示词
    """
    service = AssetService(session)
    asset = service.create_asset(data)

    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    data: AssetUpdate,
    session: Session = Depends(get_session)
):
    """
    更新资产

    - **asset_id**: 资产 ID
    - **name**: 资产名称
    - **description**: 资产描述
    - **tags**: 标签列表
    - **prompts**: 文生图/视频提示词
    - **image_url**: 生成的图片 URL
    - **video_url**: 生成的视频 URL
    """
    service = AssetService(session)
    asset = service.update_asset(asset_id, data)

    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    session: Session = Depends(get_session)
):
    """
    删除资产

    - **asset_id**: 资产 ID
    """
    service = AssetService(session)
    success = service.delete_asset(asset_id)

    if not success:
        raise HTTPException(status_code=404, detail="资产不存在")

    return {"message": "资产已删除"}
