"""
Universal Story Board - 快照管理服务
处理全局状态快照的创建和加载
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.global_snapshot import GlobalSnapshot
from app.models.project import Project
from datetime import datetime


class SnapshotService:
    """快照管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_snapshot(
        self,
        project_id: str,
        chapter_result: dict,
        assets: dict
    ) -> GlobalSnapshot:
        """
        创建新快照

        Args:
            project_id: 项目 ID
            chapter_result: 章节结果（包含 script, style_guide 等）
            assets: 资产数据（包含 characters, scenes）

        Returns:
            创建的快照对象
        """
        # 1. 加载最新快照（若存在）
        latest_snapshot = self.get_latest(project_id)
        version = (latest_snapshot.version + 1) if latest_snapshot else 1

        # 2. 增量更新（合并新资产）
        if latest_snapshot:
            characters = {**latest_snapshot.characters, **assets.get('characters', {})}
            scenes = {**latest_snapshot.scenes, **assets.get('scenes', {})}
        else:
            characters = assets.get('characters', {})
            scenes = assets.get('scenes', {})

        # 3. 更新剧情摘要（增量）
        plot_summary = self._update_plot_summary(
            latest_snapshot.plot_summary if latest_snapshot else "",
            chapter_result.get('script', '')
        )

        # 4. 创建快照
        snapshot = GlobalSnapshot(
            project_id=project_id,
            version=version,
            plot_summary=plot_summary,
            characters=characters,
            scenes=scenes,
            style_guide=chapter_result.get('style_guide', {}),
            chapter_count=(latest_snapshot.chapter_count + 1) if latest_snapshot else 1
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        print(f"[SnapshotService] 快照创建成功: {project_id} v{version}")

        return snapshot

    def get_latest(self, project_id: str) -> Optional[GlobalSnapshot]:
        """
        获取最新快照

        Args:
            project_id: 项目 ID

        Returns:
            最新快照对象，不存在则返回 None
        """
        return self.db.query(GlobalSnapshot).filter(
            GlobalSnapshot.project_id == project_id
        ).order_by(GlobalSnapshot.version.desc()).first()

    def load_as_context(self, project_id: str) -> dict:
        """
        加载快照作为上下文

        Args:
            project_id: 项目 ID

        Returns:
            上下文字典，包含：
                - plot_summary: 剧情摘要
                - existing_characters: 现有角色资产
                - existing_scenes: 现有场景资产
                - style_guide: 风格规范
                - global_version: 全局版本
        """
        snapshot = self.get_latest(project_id)
        if not snapshot:
            return {}

        return {
            "plot_summary": snapshot.plot_summary,
            "existing_characters": snapshot.characters,
            "existing_scenes": snapshot.scenes,
            "style_guide": snapshot.style_guide,
            "global_version": snapshot.version
        }

    def _update_plot_summary(self, old_summary: str, new_script: str) -> str:
        """
        增量更新剧情摘要（简单实现）

        Args:
            old_summary: 旧摘要
            new_script: 新剧本

        Returns:
            更新后的摘要
        """
        # MVP 阶段可以简单拼接或截取
        if len(old_summary) + len(new_script) > 2000:  # 限制摘要长度
            return old_summary + "\n\n...（内容截取）\n\n" + new_script[-1000:]
        return old_summary + "\n\n" + new_script
