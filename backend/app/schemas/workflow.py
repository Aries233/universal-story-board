"""
Universal Story Board - 工作流 Pydantic Schemas
用于工作流触发和状态查询的请求/响应数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any
from datetime import datetime


class ScriptScene(BaseModel):
    """剧本场次模型"""
    scene_id: str = Field(description="场次唯一标识")
    scene_name: str = Field(description="场景名称")
    shots: List[Dict] = Field(min_items=1, description="镜头列表")


class ScriptOutput(BaseModel):
    """编剧输出模型（大模型必须遵循此结构）"""
    chapter_id: str = Field(description="章节 ID")
    scenes: List[ScriptScene] = Field(min_items=1, description="场次列表")

    @field_validator('scenes')
    def validate_scene_continuity(cls, v):
        """验证场景连贯性（可选）"""
        # 可以添加自定义验证逻辑
        return v


class Shot(BaseModel):
    """镜头模型"""
    shot_id: str = Field(description="镜头唯一标识")
    timecode: str = Field(pattern=r"\d{2}:\d{2}:\d{2}", description="时间码 HH:MM:SS")
    duration: int = Field(ge=1, le=30, description="时长（秒）")
    shot_type: str = Field(description="景别，如'中景'、'特写'")
    movement: Optional[str] = Field(default=None, description="镜头运动")
    dialogue: Optional[str] = Field(default=None, description="台词")
    audio: Optional[str] = Field(default=None, description="音效")
    visual_prompt: str = Field(min_length=10, description="视听提示词")

    @field_validator('dialogue')
    def validate_dialogue_entity_links(cls, v):
        """验证台词中的实体链接格式"""
        if v and '@' in v:
            import re
            pattern = r'@[\u4e00-\u9fa5a-zA-Z0-9_]+\[[^\]]+\]'
            if not re.search(pattern, v):
                raise ValueError("台词中的实体链接格式应为 @角色名[标签]")
        return v


class CharacterAsset(BaseModel):
    """角色资产模型（严格约束大模型输出）"""
    id: str = Field(description="角色唯一标识")
    name: str = Field(min_length=1, max_length=50, description="角色姓名")
    age: str = Field(description="年龄段，如'青年'、'中年'")
    personality: List[str] = Field(min_items=1, description="性格特征列表")
    appearance: str = Field(min_length=10, description="外貌描述，至少10字")
    costume: str = Field(description="服装描述")
    props: List[str] = Field(default_factory=list, description="道具列表")
    prompts: Dict[str, str] = Field(
        description="文生图提示词字典，包含 portrait、full_body 等视角"
    )

    @field_validator('prompts')
    def validate_prompts(cls, v):
        required_keys = {'portrait', 'full_body'}
        if not all(k in v for k in required_keys):
            raise ValueError(f"prompts 必须包含 {required_keys}")
        return v


class SceneAsset(BaseModel):
    """场景资产模型"""
    id: str = Field(description="场景唯一标识")
    name: str = Field(min_length=1, max_length=50, description="场景名称")
    description: str = Field(min_length=20, description="场景描述，至少20字")
    time_of_day: str = Field(description="时间，如'白天'、'夜晚'")
    atmosphere: str = Field(description="氛围，如'宁静'、'紧张'")
    environment: str = Field(description="环境细节")
    prompts: Dict[str, str] = Field(
        description="文生图提示词字典，包含 wide_shot、detail 等视角"
    )


class WorkflowStartRequest(BaseModel):
    """启动工作流请求"""
    chapter_id: str = Field(description="章节 ID")
    mode: str = Field(default="A", description="工作流模式: A=改编编剧, B=原文模式")

    @field_validator('mode')
    def validate_mode(cls, v):
        if v not in ['A', 'B']:
            raise ValueError("工作流模式必须是 'A' 或 'B'")
        return v


class WorkflowStatusResponse(BaseModel):
    """工作流状态响应"""
    chapter_id: str
    status: str
    current_agent: Optional[str]
    retry_count: int
    error_message: Optional[str]
    progress: Optional[Dict]  # 进度详情
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class WorkflowResult(BaseModel):
    """工作流执行结果"""
    chapter_id: str
    status: str
    message: str
    context: Optional[Dict]  # 执行上下文（包含 script, characters 等）
