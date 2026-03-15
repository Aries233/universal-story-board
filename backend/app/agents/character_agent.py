"""
Universal Story Board - 角色设计师 Agent
根据剧本提取角色并生成角色资产
"""
from typing import Dict, List, Any
from sqlmodel import Session

from app.agents.base_agent import BaseAgent
from app.schemas.workflow import CharacterAsset
from app.services.system_service import SystemService
from app.services.model_router_service import ModelRouterService


class CharacterAgent(BaseAgent):
    """角色设计师 Agent（提取角色并生成角色资产）"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.system_service = SystemService(db)
        self.router_service = ModelRouterService(db)

    def execute(self, context: Dict) -> Dict:
        """
        执行角色设计任务

        Args:
            context: 上下文数据，包含：
                - chapter_id: 章节 ID
                - project_id: 项目 ID
                - script: 剧本文本
                - existing_characters: 现有角色资产

        Returns:
            角色资产列表：
            {
                "characters": [...],  # 角色资产列表
                "assets": [...]        # 创建的资产 ID 列表
            }
        """
        self._log_execute(context)

        # 1. 从剧本中提取角色信息
        characters = self._extract_characters(context['script'])

        if not characters:
            return {
                "characters": [],
                "assets": [],
                "message": "剧本中未检测到角色信息"
            }

        # 2. 为每个角色生成资产数据
        project_id = context['project_id']
        assets = []

        for char in characters:
            # 检查角色是否已存在（根据姓名）
            existing_char = self._get_existing_character(
                project_id,
                char['name']
            )

            if existing_char:
                # 角色已存在，跳过创建
                assets.append(existing_char)
                continue

            # 生成角色资产
            asset_data = self._create_character_asset(
                project_id,
                char,
                context.get('style_guide', {})
            )

            # 保存到数据库
            asset = self._save_asset(asset_data)

            assets.append(asset)

        return {
            "characters": assets,
            "assets": [a.id for a in assets],
            "message": f"成功创建 {len(assets)} 个角色资产"
        }

    def _extract_characters(self, script: str) -> List[Dict]:
        """
        从剧本中提取角色信息

        Args:
            script: 剧本文本

        Returns:
            角色信息列表
        """
        import re

        characters = []
        character_pattern = r'（([^）]+）|【([^】]+】'  # 匹配（角色名）或【角色名】

        # 查找所有角色提及
        matches = re.findall(character_pattern, script)

        # 去重并提取角色名
        seen_names = set()

        for match in matches:
            # 获取第一个非空的组
            name = match[1] if match[1] else match[2]

            if name and name not in seen_names:
                seen_names.add(name)

                # 简单推断角色信息（后续可以用 LLM 增强）
                char_info = {
                    "name": name,
                    "age": self._infer_age(name, script),
                    "personality": self._infer_personality(name, script),
                    "appearance": self._infer_appearance(name, script),
                    "costume": self._infer_costume(name, script),
                    "props": self._infer_props(name, script)
                }

                characters.append(char_info)

        return characters

    def _infer_age(self, name: str, script: str) -> str:
        """
        推断角色年龄（简单实现）

        Args:
            name: 角色名
            script: 剧本文本

        Returns:
            年龄段
        """
        # 简单的关键词匹配
        if "少年" in script or "小孩" in script or name in ["小", "童"]:
            return "少年"
        elif "老" in name or "长者" in script or "大人" in script:
            return "中年"
        else:
            return "青年"  # 默认值

    def _infer_personality(self, name: str, script: str) -> List[str]:
        """
        推断角色性格（简单实现）

        Args:
            name: 角色名
            script: 剧本文本

        Returns:
            性格特征列表
        """
        # 简单的关键词匹配
        personality_keywords = {
            "善良": ["善良", "好人", "温柔"],
            "聪明": ["聪明", "机智", "智慧", "聪明"],
            "勇敢": ["勇敢", "无畏", "大胆"],
            "谨慎": ["谨慎", "小心", "稳重"]
        }

        personality = []

        for trait, keywords in personality_keywords.items():
            for keyword in keywords:
                if keyword in script:
                    personality.append(trait)
                    break

        return personality if personality else ["普通"]

    def _infer_appearance(self, name: str, script: str) -> str:
        """
        推断角色外貌（简单实现）

        Args:
            name: 角色名
            script: 剧本文本

        Returns:
            外貌描述
        """
        # 简单推断
        if "书生" in script or "读书" in script or name in ["生", "学者"]:
            return "清秀书生，面容白净"
        elif "将军" in script or "战士" in script or name in ["将", "军"]:
            return "威武挺拔，身材魁梧"
        else:
            return "相貌端正"

    def _infer_costume(self, name: str, script: str) -> str:
        """
        推断角色服装（简单实现）

        Args:
            name: 角色名
            script: 剧本文本

        Returns:
            服装描述
        """
        if "书生" in script or "读书" in script:
            return "青色长衫，白色内衬"
        elif "将军" in script or "战士" in script:
            return "铠甲，披风"
        else:
            return "普通服装"

    def _infer_props(self, name: str, script: str) -> List[str]:
        """
        推断角色道具（简单实现）

        Args:
            name: 角色名
            script: 剧本文本

        Returns:
            道具列表
        """
        # 简单推断
        props = []

        if "书" in script or "笔" in script:
            props.append("卷轴")
            props.append("毛笔")
        elif "剑" in script or "刀" in script:
            props.append("剑")
            props.append("刀")

        return props if props else []

    def _get_existing_character(
        self,
        project_id: str,
        name: str
    ):
        """
        获取现有角色

        Args:
            project_id: 项目 ID
            name: 角色名

        Returns:
            角色资产对象，不存在则返回 None
        """
        from app.models.asset import Asset

        return self.db.query(Asset).filter(
            Asset.project_id == project_id,
            Asset.name == name,
            Asset.asset_type == "character"
        ).first()

    def _create_character_asset(
        self,
        project_id: str,
        char_info: Dict,
        style_guide: Dict
    ) -> Dict:
        """
        创建角色资产数据

        Args:
            project_id: 项目 ID
            char_info: 角色信息
            style_guide: 风格规范

        Returns:
            角色资产数据
        """
        # 生成提示词（简单实现，后续可以用 LLM 增强）
        prompts = {
            "portrait": self._generate_prompt(
                char_info, style_guide, "portrait"
            ),
            "full_body": self._generate_prompt(
                char_info, style_guide, "full_body"
            )
        }

        return {
            "project_id": project_id,
            "asset_type": "character",
            "name": char_info['name'],
            "description": f"{char_info['name']}是一个{char_info['age']}角色，性格{', '.join(char_info['personality'])}。",
            "tags": ["角色", char_info['name']],
            "age": char_info['age'],
            "personality": char_info['personality'],
            "appearance": char_info['appearance'],
            "costume": char_info['costume'],
            "props": char_info['props'],
            "prompts": prompts
        }

    def _generate_prompt(
        self,
        char_info: Dict,
        style_guide: Dict,
        view_type: str
    ) -> str:
        """
        生成提示词

        Args:
            char_info: 角色信息
            style_guide: 风格规范
            view_type: 视角类型

        Returns:
            提示词
        """
        # 简单实现，拼接关键信息
        visual_style = style_guide.get("visual_style", "2D 动画")

        if view_type == "portrait":
            return f"{visual_style} 角色肖像，{char_info['name']}，{char_info['age']}，{char_info['appearance']}，{char_info['costume']}，正面特写。"
        elif view_type == "full_body":
            return f"{visual_style} 角色全身像，{char_info['name']}，{char_info['age']}，{char_info['appearance']}，{char_info['costume']}，{'、'.join(char_info['props'])}。"
        else:
            return f"{visual_style} 角色形象，{char_info['name']}。"

    def _save_asset(self, asset_data: Dict):
        """
        保存资产到数据库

        Args:
            asset_data: 资产数据

        Returns:
            创建的资产对象
        """
        from app.models.asset import Asset
        from app.schemas.asset import AssetCreate

        # 创建 Asset 对象
        asset = Asset(
            project_id=asset_data['project_id'],
            asset_type=asset_data['asset_type'],
            name=asset_data['name'],
            description=asset_data['description'],
            tags=asset_data['tags'],
            age=asset_data.get('age'),
            personality=asset_data.get('personality'),
            appearance=asset_data.get('appearance'),
            costume=asset_data.get('costume'),
            props=asset_data.get('props'),
            prompts=asset_data.get('prompts', {})
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset
