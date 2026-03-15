"""
Universal Story Board - Agent 状态机
定义 Agent 执行状态和转移规则
"""
from enum import Enum
from typing import Optional, Dict


class AgentType(str, Enum):
    """Agent 类型枚举"""
    WRITER = "writer"                    # 编剧 Agent
    DOCTOR = "doctor"                    # 剧本医生 Agent
    CHARACTER = "character"              # 角色设计师 Agent
    SCENE = "scene"                      # 场景设计师 Agent
    DIRECTOR = "director"                # 分镜导演 Agent


class ChapterStatus(str, Enum):
    """章节处理状态枚举"""
    PENDING = "pending"                  # 待处理
    PROCESSING = "processing"            # 处理中
    COMPLETED = "completed"              # 已完成
    FAILED = "failed"                      # 失败
    MANUAL_INTERVENTION = "manual_intervention"  # 需人工介入


class AgentStateMachine:
    """Agent 状态机"""

    # 定义状态转移规则
    # Key: 当前状态或 Agent 类型
    # Value: 允许转移到的下一个状态或 Agent 类型
    TRANSITIONS = {
        ChapterStatus.PENDING: [AgentType.WRITER],

        AgentType.WRITER: [AgentType.DOCTOR, AgentType.CHARACTER],  # A 轨/B 轨分支
        AgentType.DOCTOR: [AgentType.WRITER, AgentType.CHARACTER],  # 重试/通过
        AgentType.CHARACTER: [AgentType.SCENE],
        AgentType.SCENE: [AgentType.DIRECTOR],
        AgentType.DIRECTOR: [ChapterStatus.COMPLETED, ChapterStatus.FAILED],
    }

    def __init__(self):
        """初始化状态机"""
        self.current_state = ChapterStatus.PENDING
        self.current_agent: Optional[AgentType] = None
        self.retry_count = 0
        self.max_retries = 3
        self.error_message: Optional[str] = None

    def can_transition_to(self, target: str) -> bool:
        """
        检查是否可以转移到目标状态或 Agent

        Args:
            target: 目标状态或 Agent 类型

        Returns:
            是否可以转移
        """
        # 尝试将目标字符串转换为枚举
        try:
            # 尝试作为 ChapterStatus
            target_status = ChapterStatus(target)
            if self.current_state == target_status:
                return True
        except ValueError:
            pass

        try:
            # 尝试作为 AgentType
            target_agent = AgentType(target)
        except ValueError:
            return False

        # 检查转移规则
        if self.current_agent is None:
            # 从初始状态开始
            if self.current_state == ChapterStatus.PENDING:
                return target_agent in self.TRANSITIONS.get(self.current_state, [])
            return False
        else:
            # 从当前 Agent 转移
            return target_agent in self.TRANSITIONS.get(self.current_agent, [])

    def transition_to(self, agent: AgentType):
        """
        转移到目标 Agent

        Args:
            agent: 目标 Agent 类型

        Raises:
            ValueError: 如果无法转移
        """
        if not self.can_transition_to(agent):
            raise ValueError(f"无法从 {self.current_agent} 转移到 {agent}")

        self.current_agent = agent
        self.current_state = ChapterStatus.PROCESSING
        self.error_message = None

    def succeed(self):
        """
        当前 Agent 成功完成
        """
        self.retry_count = 0
        self.error_message = None

    def fail(self, error_message: str = "Agent 执行失败"):
        """
        当前 Agent 失败

        Args:
            error_message: 错误信息

        Raises:
            Exception: 如果超过最大重试次数
        """
        self.error_message = error_message
        self.retry_count += 1

        if self.retry_count >= self.max_retries:
            self.current_state = ChapterStatus.MANUAL_INTERVENTION
            raise Exception(f"超过最大重试次数（{self.max_retries}），需人工介入。最后一次错误: {error_message}")

    def complete(self):
        """
        整个流程完成
        """
        self.current_state = ChapterStatus.COMPLETED
        self.current_agent = None
        self.error_message = None
        self.retry_count = 0

    def get_status_info(self) -> Dict[str, Any]:
        """
        获取状态信息

        Returns:
            状态信息字典
        """
        return {
            "current_state": self.current_state.value,
            "current_agent": self.current_agent.value if self.current_agent else None,
            "retry_count": self.retry_count,
            "error_message": self.error_message
        }
