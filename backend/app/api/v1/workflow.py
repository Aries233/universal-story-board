"""
Universal Story Board - 工作流触发 API 路由
提供工作流启动和状态查询接口
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from app.database import get_session
from app.services.chapter_service import ChapterService
from app.agents.orchestrator import AgentOrchestrator
from app.schemas.workflow import WorkflowStartRequest, WorkflowStatusResponse
from app.agents.state_machine import ChapterStatus

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.post("/start")
async def start_workflow(
    request: WorkflowStartRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    启动工作流

    - **chapter_id**: 章节 ID
    - **mode**: 工作流模式（A=改编编剧, B=原文模式）

    返回: 202 Accepted（任务已提交，后台执行）
    """
    # 1. 验证章节是否存在
    chapter_service = ChapterService(session)
    chapter = chapter_service.get_chapter(request.chapter_id)

    if not chapter:
        raise HTTPException(status_code=404, detail=f"章节不存在: {request.chapter_id}")

    # 2. 检查章节状态
    if chapter.status in [ChapterStatus.PROCESSING, ChapterStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail=f"章节状态为 {chapter.status}，无法重新启动"
        )

    # 3. 更新章节状态为处理中
    from app.schemas.chapter import ChapterUpdate
    chapter_service.update_chapter(
        request.chapter_id,
        ChapterUpdate(status=ChapterStatus.PROCESSING)
    )

    # 4. 在后台执行工作流
    def execute_workflow():
        """后台执行工作流的函数"""
        try:
            # 创建新的数据库会话
            from app.database import engine
            from sqlmodel import Session

            with Session(engine) as bg_session:
                # 创建编排器
                orchestrator = AgentOrchestrator(bg_session)

                # 执行工作流
                result = orchestrator.execute_workflow(
                    chapter_id=request.chapter_id,
                    mode=request.mode
                )

                print(f"[Workflow] 工作流执行完成: {request.chapter_id} -> {result['status']}")

        except Exception as e:
            print(f"[Workflow] 工作流执行失败: {request.chapter_id} -> {str(e)}")

            # 更新章节状态为失败
            try:
                from app.schemas.chapter import ChapterUpdate
                with Session(engine) as bg_session:
                    chapter_service_bg = ChapterService(bg_session)
                    chapter_service_bg.update_chapter(
                        request.chapter_id,
                        ChapterUpdate(status=ChapterStatus.FAILED)
                    )
            except:
                pass

    # 提交后台任务
    background_tasks.add_task(execute_workflow)

    return {
        "message": "工作流已启动，后台执行中",
        "chapter_id": request.chapter_id,
        "mode": request.mode
    }


@router.get("/status/{chapter_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    chapter_id: str,
    session: Session = Depends(get_session)
):
    """
    获取工作流状态

    - **chapter_id**: 章节 ID

    返回: 当前章节状态、当前执行的 Agent、重试次数等
    """
    # 1. 获取章节信息
    chapter_service = ChapterService(session)
    chapter = chapter_service.get_chapter(chapter_id)

    if not chapter:
        raise HTTPException(status_code=404, detail=f"章节不存在: {chapter_id}")

    # 2. 构建状态响应
    return WorkflowStatusResponse(
        chapter_id=chapter.id,
        status=chapter.status,
        current_agent=chapter.current_agent,
        retry_count=chapter.retry_count,
        error_message=None,  # 可以从某个地方存储错误信息
        progress={
            "total_steps": 4 if chapter.status == ChapterStatus.PROCESSING else 0,
            "completed_steps": self._calculate_completed_steps(chapter.status, chapter.current_agent)
        },
        started_at=chapter.started_at,
        completed_at=chapter.completed_at
    )

    def _calculate_completed_steps(self, status: str, current_agent: Optional[str]) -> int:
        """
        计算已完成的步骤数

        Args:
            status: 章节状态
            current_agent: 当前执行的 Agent

        Returns:
            已完成的步骤数
        """
        if status == ChapterStatus.COMPLETED:
            return 4
        elif status == ChapterStatus.PENDING:
            return 0
        elif status == ChapterStatus.FAILED:
            return 0

        # 根据当前 Agent 判断步骤
        from app.agents.state_machine import AgentType

        agent_steps = {
            AgentType.WRITER: 1,
            AgentType.CHARACTER: 2,
            AgentType.SCENE: 3,
            AgentType.DIRECTOR: 4
        }

        if current_agent:
            return agent_steps.get(AgentType(current_agent), 0)
        else:
            return 0
