"""
Universal Story Board - Agent 编排器
负责 Agent 的调度和状态管理
"""
from typing import Dict, Optional, Any
from sqlmodel import Session

from app.agents.state_machine import AgentStateMachine, AgentType, ChapterStatus
from app.agents.base_agent import BaseAgent
from app.services.system_service import SystemService
from app.services.chapter_service import ChapterService
from app.services.snapshot_service import SnapshotService


class AgentOrchestrator:
    """Agent 编排器"""

    def __init__(self, db: Session):
        """
        初始化编排器

        Args:
            db: 数据库会话
        """
        self.db = db
        self.state_machine = AgentStateMachine()
        self.agents: Dict[AgentType, BaseAgent] = {}
        self._register_agents()

        # 服务
        self.system_service = SystemService(db)
        self.chapter_service = ChapterService(db)
        self.snapshot_service = SnapshotService(db)

    def _register_agents(self):
        """注册所有 Agent"""
        from app.agents.writer_agent import WriterAgent
        from app.agents.character_agent import CharacterAgent

        # MVP 阶段只实现 Writer 和 Character Agent
        self.agents[AgentType.WRITER] = WriterAgent(self.db)
        self.agents[AgentType.CHARACTER] = CharacterAgent(self.db)

        # 预留其他 Agent（后续实现）
        # self.agents[AgentType.DOCTOR] = DoctorAgent(self.db)
        # self.agents[AgentType.SCENE] = SceneAgent(self.db)
        # self.agents[AgentType.DIRECTOR] = DirectorAgent(self.db)

    def execute_workflow(self, chapter_id: str, mode: str = "A") -> Dict:
        """
        执行工作流

        Args:
            chapter_id: 章节 ID
            mode: 工作流模式（A=改编编剧模式，B=原文模式）

        Returns:
            工作流执行结果
        """
        # 1. 构建初始上下文
        context = self._build_initial_context(chapter_id)

        # 2. 根据模式选择执行路径
        if mode == "A":
            # A 轨：改编编剧模式（Writer → Character）
            return self._execute_track_a(context)
        else:
            # B 轨：原文模式（直接 Character，跳过 Writer）
            return self._execute_track_b(context)

    def _build_initial_context(self, chapter_id: str) -> Dict:
        """
        构建初始上下文

        Args:
            chapter_id: 章节 ID

        Returns:
            上下文数据
        """
        # 获取章节信息
        chapter = self.chapter_service.get_chapter(chapter_id)
        if not chapter:
            raise ValueError(f"章节不存在: {chapter_id}")

        # 加载全局快照（作为上下文）
        snapshot_context = self.snapshot_service.load_as_context(chapter.project_id)

        return {
            "chapter_id": chapter_id,
            "project_id": chapter.project_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "original_text": chapter.original_text,
            "script": chapter.script,
            "characters": snapshot_context.get("existing_characters", {}),
            "scenes": snapshot_context.get("existing_scenes", {}),
            "style_guide": snapshot_context.get("style_guide", {})
        }

    def _execute_track_a(self, context: Dict) -> Dict:
        """
        执行 A 轨工作流（改编编剧模式）

        Args:
            context: 上下文数据

        Returns:
            执行结果
        """
        print(f"[AgentOrchestrator] 执行 A 轨工作流: {context['chapter_id']}")

        # 1. Writer Agent（编剧）
        context = self._execute_agent(AgentType.WRITER, context)
        self.state_machine.succeed()

        # 2. Character Agent（角色设计师）
        context = self._execute_agent(AgentType.CHARACTER, context)
        self.state_machine.succeed()

        # 3. 创建全局快照
        self._create_global_snapshot(context)

        # 4. 完成工作流
        self.state_machine.complete()

        # 更新章节状态为已完成
        self._update_chapter_status(context['chapter_id'], ChapterStatus.COMPLETED)

        return {
            "status": "completed",
            "message": "A 轨工作流执行完成",
            "context": context
        }

    def _execute_track_b(self, context: Dict) -> Dict:
        """
        执行 B 轨工作流（原文模式）

        Args:
            context: 上下文数据

        Returns:
            执行结果
        """
        print(f"[AgentOrchestrator] 执行 B 轨工作流: {context['chapter_id']}")

        # B 轨：原文直接作为剧本
        context['script'] = context['original_text']

        # 1. Character Agent（角色设计师）
        context = self._execute_agent(AgentType.CHARACTER, context)
        self.state_machine.succeed()

        # 2. 创建全局快照
        self._create_global_snapshot(context)

        # 3. 完成工作流
        self.state_machine.complete()

        # 更新章节状态为已完成
        self._update_chapter_status(context['chapter_id'], ChapterStatus.COMPLETED)

        return {
            "status": "completed",
            "message": "B 轨工作流执行完成",
            "context": context
        }

    def _execute_agent(self, agent_type: AgentType, context: Dict) -> Dict:
        """
        执行单个 Agent（含重试机制）

        Args:
            agent_type: Agent 类型
            context: 上下文数据

        Returns:
            执行结果

        Raises:
            Exception: 如果超过最大重试次数
        """
        agent = self.agents[agent_type]

        print(f"[{agent_type}] 开始执行")

        # 转移到目标 Agent
        self.state_machine.transition_to(agent_type)

        # 重试机制
        retry_count = 0
        max_retries = self.state_machine.max_retries

        last_error = None

        while retry_count < max_retries:
            try:
                # 执行 Agent 任务
                result = agent.execute(context)

                # 成功，返回结果（只合并需要的字段，避免覆盖已有字段）
                print(f"[{agent_type}] 执行成功")
                print(f"[{agent_type}] 返回结果类型: {type(result)}")

                # 打印结果的部分内容（用于调试）
                if isinstance(result, dict):
                    for key in result.keys():
                        print(f"[{agent_type}] 返回字段: {key} = {type(result[key])}")

                # 只合并需要的字段，避免覆盖已有字段
                # 特别是不要覆盖 script 和 style_guide
                merged_context = {**context}
                for key, value in result.items():
                    # 对于 writer_agent，保留 script 和 style_guide
                    # 对于 character_agent，添加 characters 和 assets
                    # 不要覆盖 context 中已有的字段
                    if key not in merged_context or agent_type == AgentType.WRITER:
                        merged_context[key] = value
                    elif key == "script" and merged_context.get("script") is not None and agent_type == AgentType.CHARACTER:
                        # character_agent 不要覆盖 script
                        pass
                    elif key == "style_guide" and merged_context.get("style_guide") is not None and agent_type == AgentType.CHARACTER:
                        # character_agent 不要覆盖 style_guide
                        pass

                return merged_context

            except Exception as e:
                last_error = str(e)
                import traceback
                error_trace = traceback.format_exc()

                retry_count += 1
                print(f"[{agent_type}] 执行失败（第 {retry_count} 次重试）")
                print(f"[{agent_type}] 错误类型: {type(e).__name__}")
                print(f"[{agent_type}] 错误信息: {str(e)}")
                print(f"[{agent_type}] 错误堆栈:\n{error_trace}")

                # 失败处理
                if retry_count >= max_retries:
                    # 超过最大重试次数
                    error_message = f"{agent_type} 执行失败（第 {retry_count} 次重试）: {last_error}"

                    # 写入错误信息到数据库
                    try:
                        self._update_chapter_error_message(
                            context['chapter_id'],
                            error_message
                        )
                    except:
                        pass

                    self.state_machine.fail(error_message)
                    raise

                # 继续重试

        # 不应该到这里
        raise Exception(f"{agent_type} 执行失败，超过最大重试次数")

    def _update_chapter_error_message(self, chapter_id: str, error_message: str):
        """
        更新章节的错误信息

        Args:
            chapter_id: 章节 ID
            error_message: 错误信息
        """
        try:
            from app.schemas.chapter import ChapterUpdate
            self.chapter_service.update_chapter(
                chapter_id,
                ChapterUpdate(error_message=error_message[:500])  # 限制长度
            )
        except Exception as e:
            print(f"[AgentOrchestrator] 更新章节错误信息失败: {str(e)}")

    def _create_global_snapshot(self, context: Dict):
        """
        创建全局快照

        Args:
            context: 上下文数据
        """
        try:
            # 提取资产
            assets = {
                "characters": context.get("characters", {}),
                "scenes": context.get("scenes", {})
            }

            # 创建快照
            self.snapshot_service.create_snapshot(
                project_id=context['project_id'],
                chapter_result={
                    "script": context.get('script', '')
                },
                assets=assets
            )

            print(f"[AgentOrchestrator] 全局快照创建成功: {context['project_id']}")
        except Exception as e:
            print(f"[AgentOrchestrator] 全局快照创建失败: {str(e)}")

    def _update_chapter_status(self, chapter_id: str, status: ChapterStatus):
        """
        更新章节状态

        Args:
            chapter_id: 章节 ID
            status: 目标状态
        """
        try:
            from app.schemas.chapter import ChapterUpdate

            # 更新状态
            self.chapter_service.update_chapter(chapter_id, ChapterUpdate(status=status.value))

            # 更新时间
            chapter = self.chapter_service.get_chapter(chapter_id)
            if chapter and status == ChapterStatus.COMPLETED:
                chapter.completed_at = chapter.updated_at
                self.db.commit()

            print(f"[AgentOrchestrator] 章节状态更新: {chapter_id} -> {status.value}")
        except Exception as e:
            print(f"[AgentOrchestrator] 章节状态更新失败: {str(e)}")

    def get_workflow_status(self, chapter_id: str) -> Dict:
        """
        获取工作流状态

        Args:
            chapter_id: 章节 ID

        Returns:
            状态信息
        """
        # 获取章节信息
        chapter = self.chapter_service.get_chapter(chapter_id)
        if not chapter:
            raise ValueError(f"章节不存在: {chapter_id}")

        return {
            "chapter_id": chapter_id,
            "status": chapter.status,
            "current_agent": chapter.current_agent,
            "retry_count": chapter.retry_count,
            "state_machine_info": self.state_machine.get_status_info()
        }
