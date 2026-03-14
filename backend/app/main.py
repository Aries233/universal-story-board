"""
Universal Story Board - FastAPI 应用入口
初始化 FastAPI 应用和数据库
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, engine
from sqlmodel import Session

# ========== 重要：导入所有 SQLModel 模型类 ==========
# 必须在 init_db() 之前导入，确保所有模型都被注册到 SQLModel.metadata
# 这样 create_all(engine) 才能创建所有数据表
# =====================================================
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.global_snapshot import GlobalSnapshot
from app.models.asset import Asset
from app.models.shot import Shot
from app.models.provider_credential import ProviderCredential
from app.models.model_route_config import ModelRouteConfig
# =====================================================

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 AI 的 2D 动画分镜生成平台",
    debug=settings.debug
)


# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    初始化数据库，创建所有数据表，初始化默认路由配置
    """
    # 1. 初始化数据库
    init_db()

    # 2. 初始化默认路由配置（如果不存在）
    init_default_route_configs()

    print(f"✅ {settings.app_name} v{settings.app_version} 启动成功")
    print(f"📦 数据库: {settings.database_url}")
    print(f"🔌 支持的多模型路由: 文本/图片/视频")


def init_default_route_configs():
    """
    初始化默认路由配置
    如果数据库中不存在路由配置，则插入默认配置

    注意：此函数必须在 init_db() 之后调用，确保表已创建
    """
    from app.models.model_route_config import DEFAULT_ROUTE_CONFIGS

    with Session(engine) as session:
        # 检查是否已存在路由配置
        existing_configs = session.query(ModelRouteConfig).count()
        if existing_configs > 0:
            print(f"✅ 路由配置已存在（共 {existing_configs} 条），跳过初始化")
            return

        # 插入默认配置
        for config_data in DEFAULT_ROUTE_CONFIGS:
            config = ModelRouteConfig(
                model_type=config_data["model_type"],
                primary_model=config_data["primary_model"],
                fallback_models=config_data["fallback_models"],
                model_to_provider=config_data["model_to_provider"],
                routing_rules=config_data["routing_rules"]
            )
            session.add(config)

        session.commit()
        print(f"✅ 已初始化 {len(DEFAULT_ROUTE_CONFIGS)} 条默认路由配置")


@app.get("/")
async def root():
    """根路径，返回 API 基本信息"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "database": settings.database_type
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
