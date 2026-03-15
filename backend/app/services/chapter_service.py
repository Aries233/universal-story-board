"""
Universal Story Board - 章节管理服务
处理章节 CRUD 的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chapter import Chapter, ChapterStatus
from app.schemas.chapter import ChapterCreate, ChapterUpdate
from datetime import datetime


class ChapterService:
    """章节管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_chapters(
        self,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[int, List[Chapter]]:
        """
        获取章节列表

        Args:
            project_id: 项目 ID（可选）
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (总数, 章节列表)
        """
        query = self.db.query(Chapter)

        if project_id:
            query = query.filter(Chapter.project_id == project_id)

        total = query.count()
        chapters = query\
            .order_by(Chapter.chapter_number.asc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return total, chapters

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        """
        获取章节详情

        Args:
            chapter_id: 章节 ID

        Returns:
            章节对象，不存在则返回 None
        """
        return self.db.query(Chapter).filter(Chapter.id == chapter_id).first()

    def create_chapter(self, data: ChapterCreate) -> Chapter:
        """
        创建章节

        Args:
            data: 章节创建数据

        Returns:
            创建的章节
        """
        chapter = Chapter(
            project_id=data.project_id,
            chapter_number=data.chapter_number,
            title=data.title,
            original_text=data.original_text,
            status=ChapterStatus.PENDING,
            current_agent=None,
            retry_count=0
        )

        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)

        # 更新项目的章节数
        self._update_project_chapter_count(chapter.project_id)

        return chapter

    def batch_create_chapters(self, batch_data) -> List[Chapter]:
        """
        批量创建章节

        Args:
            batch_data: 批量创建请求数据（ChapterBatchCreate 对象，包含 project_id 和 chapters 列表）

        Returns:
            创建的章节列表
        """
        from app.schemas.chapter import ChapterBatchCreate

        # 提取全局 project_id
        project_id = batch_data.project_id if hasattr(batch_data, 'project_id') else None
        chapters_items = batch_data.chapters if hasattr(batch_data, 'chapters') else batch_data

        chapters = []

        for item in chapters_items:
            chapter = Chapter(
                project_id=project_id,
                chapter_number=item.chapter_number if hasattr(item, 'chapter_number') else item.get('chapter_number'),
                title=item.title if hasattr(item, 'title') else item.get('title'),
                original_text=item.original_text if hasattr(item, 'original_text') else item.get('original_text'),
                status=ChapterStatus.PENDING,
                current_agent=None,
                retry_count=0
            )
            self.db.add(chapter)
            chapters.append(chapter)

        self.db.commit()

        # 更新项目的章节数
        if chapters:
            self._update_project_chapter_count(project_id)

        return chapters

    def update_chapter(
        self,
        chapter_id: str,
        data: ChapterUpdate
    ) -> Optional[Chapter]:
        """
        更新章节

        Args:
            chapter_id: 章节 ID
            data: 章节更新数据

        Returns:
            更新后的章节，不存在则返回 None
        """
        chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()

        if not chapter:
            return None

        # 更新字段
        if data.title is not None:
            chapter.title = data.title
        if data.original_text is not None:
            chapter.original_text = data.original_text
        if data.status is not None:
            chapter.status = ChapterStatus(data.status)
            # 状态变更时更新时间
            if chapter.status == ChapterStatus.PROCESSING and not chapter.started_at:
                chapter.started_at = datetime.utcnow()
            elif chapter.status == ChapterStatus.COMPLETED and not chapter.completed_at:
                chapter.completed_at = datetime.utcnow()
        if data.current_agent is not None:
            chapter.current_agent = data.current_agent
        if data.retry_count is not None:
            chapter.retry_count = data.retry_count

        chapter.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(chapter)

        return chapter

    def delete_chapter(self, chapter_id: str) -> bool:
        """
        删除章节

        Args:
            chapter_id: 章节 ID

        Returns:
            是否删除成功
        """
        chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()

        if not chapter:
            return False

        project_id = chapter.project_id

        self.db.delete(chapter)
        self.db.commit()

        # 更新项目的章节数
        self._update_project_chapter_count(project_id)

        return True

    def _update_project_chapter_count(self, project_id: str):
        """
        更新项目的章节数

        Args:
            project_id: 项目 ID
        """
        from app.models.project import Project

        count = self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).count()

        project = self.db.query(Project).filter(
            Project.id == project_id
        ).first()

        if project:
            project.chapter_count = count
            project.updated_at = datetime.utcnow()
            self.db.commit()
