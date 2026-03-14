"""
Universal Story Board - FastAPI 应用入口
初始化 FastAPI 应用和数据库
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

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
    初始化数据库，创建所有数据表
    """
    init_db()
    print(f"✅ {settings.app_name} v{settings.app_version} 启动成功")
    print(f"📦 数据库: {settings.database_url}")


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
