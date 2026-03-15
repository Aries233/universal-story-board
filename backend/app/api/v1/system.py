"""
Universal Story Board - 系统配置 API 路由
提供服务商凭证和模型路由配置的接口
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.services.system_service import SystemService
from app.schemas.system import (
    ProviderCredentialCreate,
    ProviderCredentialUpdate,
    ProviderCredentialResponse,
    ModelRouteConfigUpdate,
    ModelRouteConfigResponse,
    SystemConfigResponse
)

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/credentials", response_model=list[ProviderCredentialResponse])
async def list_credentials(
    provider: str = Query(None, description="筛选服务商类型"),
    session: Session = Depends(get_session)
):
    """
    获取服务商凭证列表

    - **provider**: 筛选服务商类型（可选）
    """
    service = SystemService(session)
    credentials = service.list_credentials(provider)

    return credentials


@router.post("/credentials", response_model=ProviderCredentialResponse)
async def create_credential(
    data: ProviderCredentialCreate,
    session: Session = Depends(get_session)
):
    """
    创建服务商凭证

    - **provider**: 服务商类型（zhipu, qwen, gemini, openai, stability, runway）
    - **api_key**: API Key（会自动加密存储）
    - **name**: 凭证名称
    - **priority**: 优先级（数字越小优先级越高）
    """
    service = SystemService(session)
    credential = service.create_credential(data)

    return credential


@router.get("/credentials/{credential_id}", response_model=ProviderCredentialResponse)
async def get_credential(
    credential_id: str,
    session: Session = Depends(get_session)
):
    """
    获取服务商凭证详情

    - **credential_id**: 凭证 ID
    """
    service = SystemService(session)

    # 获取单个凭证
    credentials = service.list_credentials()
    credential = next((c for c in credentials if c.id == credential_id), None)

    if not credential:
        raise HTTPException(status_code=404, detail="凭证不存在")

    return credential


@router.put("/credentials/{credential_id}", response_model=ProviderCredentialResponse)
async def update_credential(
    credential_id: str,
    data: ProviderCredentialUpdate,
    session: Session = Depends(get_session)
):
    """
    更新服务商凭证

    - **credential_id**: 凭证 ID
    - **name**: 凭证名称
    - **api_key**: API Key（会自动重新加密）
    - **is_active**: 是否启用
    - **priority**: 优先级
    """
    service = SystemService(session)
    credential = service.update_credential(credential_id, data)

    if not credential:
        raise HTTPException(status_code=404, detail="凭证不存在")

    return credential


@router.delete("/credentials/{credential_id}")
async def delete_credential(
    credential_id: str,
    session: Session = Depends(get_session)
):
    """
    删除服务商凭证

    - **credential_id**: 凭证 ID
    """
    service = SystemService(session)
    success = service.delete_credential(credential_id)

    if not success:
        raise HTTPException(status_code=404, detail="凭证不存在")

    return {"message": "凭证已删除"}


@router.get("/route-configs", response_model=list[ModelRouteConfigResponse])
async def list_route_configs(
    session: Session = Depends(get_session)
):
    """
    获取所有路由配置

    返回文本、图片、视频三种模型的路由配置
    """
    service = SystemService(session)
    configs = service.list_route_configs()

    return configs


@router.put("/route-configs/{config_id}", response_model=ModelRouteConfigResponse)
async def update_route_config(
    config_id: str,
    data: ModelRouteConfigUpdate,
    session: Session = Depends(get_session)
):
    """
    更新路由配置

    - **config_id**: 配置 ID
    - **primary_model**: 首选模型
    - **fallback_models**: 备用模型列表
    - **model_to_provider**: 模型到服务商的映射
    - **routing_rules**: 路由规则
    """
    service = SystemService(session)
    config = service.update_route_config(config_id, data)

    if not config:
        raise HTTPException(status_code=404, detail="路由配置不存在")

    return config


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config(
    session: Session = Depends(get_session)
):
    """
    获取系统配置

    返回所有路由配置和凭证列表的汇总
    """
    service = SystemService(session)
    route_configs = service.list_route_configs()
    credentials = service.list_credentials()

    return {
        "route_configs": route_configs,
        "credentials": credentials
    }
