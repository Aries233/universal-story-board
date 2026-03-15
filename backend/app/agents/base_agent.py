"""
Universal Story Board - Agent 基类
定义所有 Agent 的统一接口
"""
from abc import ABC, abstractmethod
from typing import Dict
from sqlmodel import Session


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, db: Session):
        """
        初始化 Agent

        Args:
            db: 数据库会话
        """
        self.db = db

    @abstractmethod
    def execute(self, context: Dict) -> Dict:
        """
        执行 Agent 任务

        Args:
            context: 上下文数据，包含：
                - chapter_id: 章节 ID
                - project_id: 项目 ID
                - original_text: 原始文本
                - script: 剧本（如果有）
                - characters: 现有角色资产
                - scenes: 现有场景资产
                - style_guide: 风格规范
                - 其他相关信息

        Returns:
            Agent 执行结果，根据不同 Agent 返回不同的数据：
            - WriterAgent: 剧本数据
            - DoctorAgent: 剧本医生反馈
            - CharacterAgent: 角色资产列表
            - SceneAgent: 场景资产列表
            - DirectorAgent: 分镜镜头列表
        """
        pass

    def _log_execute(self, context: Dict):
        """
        记录执行日志

        Args:
            context: 上下文数据
        """
        agent_name = self.__class__.__name__
        chapter_id = context.get('chapter_id', 'unknown')
        print(f"[{agent_name}] 执行章节: {chapter_id}")
