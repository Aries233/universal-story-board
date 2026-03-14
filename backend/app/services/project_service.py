"""
Universal Story Board - 项目管理服务
处理项目 CRUD 的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from datetime import datetime


class ProjectService:
    """项目管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_projects(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[int, List[Project]]:
        """
        获取项目列表

        Args:
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (总数, 项目列表)
        """
        total = self.db.query(Project).count()
        projects = self.db.query(Project)\
            .order_by(Project.updated_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return total, projects

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        获取项目详情

        Args:
            project_id: 项目 ID

        Returns:
            项目对象，不存在则返回 None
        """
        return self.db.query(Project).filter(Project.id == project_id).first()

    def create_project(self, data: ProjectCreate) -> Project:
        """
        创建项目

        Args:
            data: 项目创建数据

        Returns:
            创建的项目
        """
        project = Project(
            name=data.name,
            description=data.description,
            workflow_mode=data.workflow_mode,
            chapter_count=0,
            completed_chapters=0
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def update_project(
        self,
        project_id: str,
        data: ProjectUpdate
    ) -> Optional[Project]:
        """
        更新项目

        Args:
            project_id: 项目 ID
            data: 项目更新数据

        Returns:
            更新后的项目，不存在则返回 None
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return None

        # 更新字段
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.workflow_mode is not None:
            project.workflow_mode = data.workflow_mode

        project.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        return project

    def delete_project(self, project_id: str) -> bool:
        """
        删除项目

        Args:
            project_id: 项目 ID

        Returns:
            是否删除成功
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return False

        self.db.delete(project)
        self.db.commit()

        return True
