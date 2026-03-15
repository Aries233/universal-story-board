"""
Universal Story Board - 编剧 Agent
根据原始文本或全局上下文生成剧本
"""
from typing import Dict, List, Any
from sqlmodel import Session

from app.agents.base_agent import BaseAgent
from app.schemas.workflow import ScriptOutput, ScriptScene, Shot
from app.schemas.system import ProviderCredentialUpdate
from app.services.system_service import SystemService
from app.services.model_router_service import ModelRouterService


class WriterAgent(BaseAgent):
    """编剧 Agent（生成剧本）"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.system_service = SystemService(db)
        self.router_service = ModelRouterService(db)

    def execute(self, context: Dict) -> Dict:
        """
        执行编剧任务

        Args:
            context: 上下文数据，包含：
                - chapter_id: 章节 ID
                - project_id: 项目 ID
                - original_text: 原始文本
                - characters: 现有角色资产
                - scenes: 现有场景资产
                - style_guide: 风格规范

        Returns:
            剧本数据：
            {
                "script": 剧本文本,
                "style_guide": 风格规范
            }
        """
        self._log_execute(context)

        # 1. 加载模型配置（从数据库查询 API Key）
        model_config = self._load_model_config()

        # 2. 构建提示词
        prompt = self._build_prompt(context)

        # 3. 调用 LLM 生成剧本
        script_text = self._call_llm(prompt, model_config)

        # 4. 提取风格规范
        style_guide = self._extract_style_guide(context)

        return {
            "script": script_text,
            "style_guide": style_guide
        }

    def _load_model_config(self) -> Dict:
        """
        加载文本大模型配置（从数据库查询 API Key）

        Returns:
            模型配置：
            {
                "provider": 服务商类型,
                "model": 模型名称,
                "api_key": API Key
            }
        """
        from app.models.model_route_config import ModelType

        # 从数据库获取路由配置
        route_configs = self.system_service.list_route_configs()
        text_config = next((c for c in route_configs if c.model_type == ModelType.TEXT), None)

        if not text_config:
            raise ValueError("未找到文本模型路由配置")

        # 解析模型配置（包含服务商信息）
        provider_name = text_config.model_to_provider.get(text_config.primary_model)

        # 从数据库获取服务商凭证（API Key）
        credentials = self.system_service.list_credentials(provider_name)

        if not credentials:
            raise ValueError(f"未找到 {provider_name} 的 API Key")

        # 获取激活的凭证（按优先级）
        credential = credentials[0]  # 已按优先级排序

        # 解密 API Key
        from app.utils.crypto import get_crypto
        crypto = get_crypto()
        api_key = crypto.decrypt(credential.api_key)

        return {
            "provider": credential.provider,
            "model": text_config.primary_model,
            "api_key": api_key,
            "credential_id": credential.id
        }

    def _build_prompt(self, context: Dict) -> str:
        """
        构建编剧提示词

        Args:
            context: 上下文数据

        Returns:
            提示词
        """
        # 提取上下文信息
        project_id = context.get('project_id', '')
        chapter_number = context.get('chapter_number', 1)
        original_text = context.get('original_text', '')
        characters = context.get('characters', {})
        scenes = context.get('scenes', {})
        style_guide = context.get('style_guide', {})

        # 构建角色和场景描述
        character_descs = "\n".join([
            f"- {name}: {desc.get('description', 'N/A')}"
            for name, desc in characters.items()
        ])

        scene_descs = "\n".join([
            f"- {name}: {desc.get('description', 'N/A')}"
            for name, desc in scenes.items()
        ])

        # 风格规范
        style_desc = "\n".join([
            f"- {k}: {v}"
            for k, v in style_guide.items()
        ])

        # 构建提示词
        prompt = f"""你是一个专业的 2D 动画编剧。请根据以下信息为项目 {project_id} 的第 {chapter_number} 章创作剧本：

## 原始文本
{original_text}

## 现有角色
{character_descs if character_descs else '（暂无角色信息）'}

## 现有场景
{scene_descs if scene_descs else '（暂无场景信息）'}

## 风格规范
{style_desc if style_desc else '（暂无风格规范）'}

## 要求
1. 保留原始文本的核心剧情
2. 根据角色和场景信息，补充对话、动作、场景描述
3. 保持风格规范的一致性
4. 输出结构：场次 → 镜头 → 台词/动作 → 备注
5. 每个场次包含：场景名称、时间、氛围、镜头列表
6. 每个镜头包含：镜头编号、时间码、景别、运动、台词、动作、备注

## 输出格式
请按以下格式输出剧本：

---
# 场次 1: [场景名称]
时间: [时间]
氛围: [氛围]
环境: [环境描述]

镜头 1: [景别] [时间码]
[角色]: [台词]
[动作]: [动作描述]
备注: [备注]

镜头 2: ...

---

# 场次 2: [场景名称]
...

请开始创作：
"""

        return prompt

    def _call_llm(self, prompt: str, model_config: Dict) -> str:
        """
        调用 LLM 生成剧本

        Args:
            prompt: 提示词
            model_config: 模型配置

        Returns:
            生成的剧本文本
        """
        from app.llm.glm_adapter import GLMAdapter
        from app.models.provider_credential import ProviderType

        # 根据服务商创建 Adapter
        if model_config['provider'] == ProviderType.ZHIPU:
            adapter = GLMAdapter(model_config['api_key'])
        else:
            raise ValueError(f"暂不支持 {model_config['provider']} 服务商")

        # 调用聊天接口
        messages = [
            {"role": "user", "content": prompt}
        ]

        try:
            script_text = adapter.chat(messages, temperature=0.7, model=model_config['model'])

            # 记录调用统计（使用 Pydantic 模型实例化）
            # 1. 先查询凭证对象
            credential = self.system_service.get_credential(model_config['credential_id'])
            
            # 2. 确保凭证存在
            if credential is None:
                raise ValueError(f"凭证不存在: {model_config['credential_id']}")
            
            # 3. 增加调用次数
            self.system_service.update_credential(
                model_config['credential_id'],
                data=ProviderCredentialUpdate(call_count=credential.call_count + 1)
            )

            return script_text
        except Exception as e:
            raise Exception(f"LLM 调用失败: {str(e)}")

    def _extract_style_guide(self, context: Dict) -> Dict:
        """
        从上下文中提取风格规范

        Args:
            context: 上下文数据

        Returns:
            风格规范字典
        """
        # 简单提取，可以后续优化为智能提取
        original_text = context.get('original_text', '')

        # 简单的风格规范推断
        style_guide = {
            "visual_style": "2D 动画",
            "tone": original_text[:100] if len(original_text) > 0 else "",
            "artistic_direction": "根据角色和场景信息补充"
        }

        return style_guide
