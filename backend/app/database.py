"""
Universal Story Board - 数据库连接与会话管理模块
负责初始化数据库引擎和提供会话管理
"""
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from app.config import settings


# 创建数据库引擎
# SQLite 需要设置 check_same_thread=False 允许多线程访问
if settings.database_type == "sqlite":
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL 等其他数据库
    engine = create_engine(settings.database_url)


def init_db() -> None:
    """
    初始化数据库
    创建所有定义的数据表
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于 FastAPI 依赖注入

    Yields:
        Session: 数据库会话对象
    """
    with Session(engine) as session:
        yield session
