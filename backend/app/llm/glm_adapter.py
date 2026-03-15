"""
Universal Story Board - GLM 适配器实现
使用智谱 AI 的 GLM 模型
"""
import httpx
from typing import Dict, List, Optional, Any
from app.llm.base_adapter import BaseLLMAdapter


class GLMAdapter(BaseLLMAdapter):
    """智谱 GLM 适配器"""

    # GLM API 端点
    API_BASE = "https://open.bigmodel.cn/api/paas/v4"

    def __init__(self, api_key: str):
        """
        初始化 GLM 适配器

        Args:
            api_key: 智谱 AI 的 API Key
        """
        super().__init__(api_key)
        self.client = httpx.Client(timeout=60.0)

    def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        model: str = "glm-4-plus"
    ) -> str:
        """
        调用 GLM 聊天接口

        Args:
            messages: 消息列表
            temperature: 温度参数（0-2）
            model: 模型名称（glm-4-plus, glm-4-long, glm-4-air 等）

        Returns:
            模型返回的文本

        Mock 模式：
            如果 API Key 以 mock_ 开头，直接返回静态 Mock 数据，不发起网络请求
        """
        # 检查是否为 Mock 模式
        if self.api_key.startswith("mock_"):
            return self._mock_chat(messages, temperature, model)

        url = f"{self.API_BASE}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            # 提取返回的文本
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return ""
        except httpx.HTTPStatusError as e:
            raise Exception(f"GLM API 调用失败: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"GLM API 调用异常: {str(e)}")

    def _mock_chat(
        self,
        messages: List[Dict],
        temperature: float,
        model: str
    ) -> str:
        """
        Mock 聊天接口（返回静态数据）

        Args:
            messages: 消息列表（忽略）
            temperature: 温度参数（忽略）
            model: 模型名称（忽略）

        Returns:
            静态 Mock 文本
        """
        return """# 场次 1: 古老的书房

时间: 白天
氛围: 宁静、典雅
环境: 古色古香的房间，墙上挂着山水画，书案林立

镜头 1: 中景 00:00:05
【林峰】: （睁眼，疑惑地）这是哪里？我怎么会在这里？
【动作】: 缓缓坐起，环顾四周
备注: 主角穿越到唐朝，初醒状态

镜头 2: 特写 00:00:10
【动作】: 手指触摸古床，感受材质
备注: 展现主角对新环境的疑惑

镜头 3: 中景 00:00:15
【林峰】: （自言自语）记得我是在爬山时摔落的，难道是穿越了？
【动作】: 试图回忆，表情从疑惑变为震惊
备注: 主角意识到穿越的事实

---

# 场次 2: 书房走廊

时间: 白天
氛围: 宁静
环境: 古朴的走廊，两旁是木质的柱子

镜头 1: 中景 00:00:20
【动作】: 起身，走向门口
备注: 主角准备探索新环境

镜头 2: 中景 00:00:25
【动作】: 推开门，看到走廊
备注: 展现古代建筑风格

镜头 3: 特写 00:00:30
【林峰】: （低声）这里的人穿着古风，难道真的是唐朝？
【动作】: 观察走廊两侧的装饰
备注: 主角确认自己的猜测

---

# 场次 3: 走廊相遇

时间: 白天
氛围: 宁静
环境: 走廊尽头，通向大厅

镜头 1: 中景 00:00:35
【动作】: 沿着走廊向前走
备注: 主角向前探索

镜头 2: 远景 00:00:40
【动作】: 看到远处有一个人影
备注: 前方有不明人物

镜头 3: 中景 00:00:45
【老者】: （招手）这位小兄弟，你终于醒了
【动作】: 老者向主角招手
备注: 引入关键 NPC

镜头 4: 特写 00:00:50
【林峰】: （惊讶）老人家，您是谁？我为什么会在这里？
【动作】: 主角走向老者，表情疑惑
备注: 主角与关键 NPC 第一次相遇

---

# 场次 4: 走廊对话

时间: 白天
氛围: 宁静
环境: 走廊中，林峰与老者面对面

镜头 1: 中景 00:00:55
【老者】: （微笑）这里是翰林院，你在这里已经昏迷了三天
【动作】: 老者温和地解释
备注: 老者提供重要背景信息

镜头 2: 特写 00:01:00
【林峰】: （震惊）昏迷了三天？那我以后该怎么办？
【动作】: 主角表情从疑惑变为焦虑
备注: 主角意识到自己被困在古代

镜头 3: 中景 00:01:05
【老者】: （安抚）别担心，既来之则安，或许这是上天给你的机会
【动作】: 老者拍拍林峰的肩膀
备注: 老者为主角提供安慰

镜头 4: 特写 00:01:10
【林峰】: （沉思）既来之则安...好吧，我会尝试适应这里的生活
【动作】: 主角开始接受现实
备注: 主角心态转变，开始适应新环境

---

"""

    def chat_with_json_output(
        self,
        messages: List[Dict],
        schema: Dict[str, Any],
        temperature: float = 0.7,
        model: str = "glm-4-plus"
    ) -> Dict[str, Any]:
        """
        调用 GLM 结构化输出接口（通过提示词）

        Args:
            messages: 消息列表
            schema: Pydantic Schema 的字典描述
            temperature: 温度参数
            model: 模型名称

        Returns:
            模型返回的结构化数据（已解析为 Python 字典）

        Mock 模式：
            如果 API Key 以 mock_ 开头，直接返回静态 Mock 数据，不发起网络请求
        """
        # 检查是否为 Mock 模式
        if self.api_key.startswith("mock_"):
            return self._mock_chat_with_json_output(messages, schema, temperature, model)

        # 在 system 消息中添加 JSON 输出约束
        system_prompt = f"""你是一个 JSON 数据助手。请严格按照以下 Schema 格式输出 JSON 数据，不要输出任何其他文本：

Schema 定义:
{schema}

输出要求:
1. 只输出有效的 JSON 数据，不要输出任何说明性文字
2. 确保所有必填字段都存在
3. 确保数据类型正确
4. 确保枚举值在允许的范围内
"""

        # 构建消息列表
        full_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages

        # 调用聊天接口
        response_text = self.chat(full_messages, temperature, model)

        # 解析 JSON
        import json

        try:
            # 提取 JSON 部分（去除可能的 Markdown 代码块标记）
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            # 解析 JSON
            result = json.loads(clean_text)

            return result
        except json.JSONDecodeError as e:
            raise Exception(f"GLM 返回的 JSON 解析失败: {str(e)}\n原始文本: {response_text}")

    def _mock_chat_with_json_output(
        self,
        messages: List[Dict],
        schema: Dict[str, Any],
        temperature: float,
        model: str
    ) -> Dict[str, Any]:
        """
        Mock 结构化输出接口（返回静态数据）

        Args:
            messages: 消息列表（忽略）
            schema: Pydantic Schema（忽略）
            temperature: 温度参数（忽略）
            model: 模型名称（忽略）

        Returns:
            静态 Mock 数据（符合 ScriptOutput 结构）
        """
        return {
            "chapter_id": "mock-chapter-id",
            "scenes": [
                {
                    "scene_id": "scene-1",
                    "scene_name": "古老的书房",
                    "shots": [
                        {
                            "shot_id": "shot-1",
                            "timecode": "00:00:05",
                            "duration": 5,
                            "shot_type": "中景",
                            "movement": "固定镜头",
                            "dialogue": "【林峰】: （睁眼，疑惑地）这是哪里？",
                            "audio": None,
                            "visual_prompt": "古代书房场景，林峰从古床上醒来，神情疑惑"
                        },
                        {
                            "shot_id": "shot-2",
                            "timecode": "00:00:10",
                            "duration": 5,
                            "shot_type": "特写",
                            "movement": "推镜头",
                            "dialogue": None,
                            "audio": "轻微的风声",
                            "visual_prompt": "古床特写，林峰手指触摸床单"
                        },
                        {
                            "shot_id": "shot-3",
                            "timecode": "00:00:15",
                            "duration": 10,
                            "shot_type": "中景",
                            "movement": "缓慢摇镜头",
                            "dialogue": "【林峰】: 记得我是在爬山时摔落的，难道是穿越了？",
                            "audio": None,
                            "visual_prompt": "林峰面部特写，从疑惑变为震惊"
                        }
                    ]
                },
                {
                    "scene_id": "scene-2",
                    "scene_name": "书房走廊",
                    "shots": [
                        {
                            "shot_id": "shot-4",
                            "timecode": "00:00:20",
                            "duration": 5,
                            "shot_type": "中景",
                            "movement": "跟随镜头",
                            "dialogue": None,
                            "audio": None,
                            "visual_prompt": "林峰走向走廊，古代建筑风格"
                        },
                        {
                            "shot_id": "shot-5",
                            "timecode": "00:00:25",
                            "duration": 5,
                            "shot_type": "中景",
                            "movement": "开门镜头",
                            "dialogue": None,
                            "audio": "木门开启的声音",
                            "visual_prompt": "推开门看到走廊"
                        },
                        {
                            "shot_id": "shot-6",
                            "timecode": "00:00:30",
                            "duration": 5,
                            "shot_type": "特写",
                            "movement": "慢动作",
                            "dialogue": "【林峰】: 这里的人穿着古风，难道真的是唐朝？",
                            "audio": None,
                            "visual_prompt": "林峰观察走廊装饰"
                        }
                    ]
                }
            ]
        }

    def chat_with_function_calling(
        self,
        messages: List[Dict],
        functions: List[Dict],
        temperature: float = 0.7,
        model: str = "glm-4-plus"
    ) -> Dict[str, Any]:
        """
        调用 GLM 函数调用接口

        Args:
            messages: 消息列表
            functions: 可用函数列表
            temperature: 温度参数
            model: 模型名称

        Returns:
            模型返回的函数调用结果
        """
        url = f"{self.API_BASE}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "functions": functions,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            # 提取函数调用结果
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0]["message"]
                if "tool_calls" in message:
                    # 返回函数调用信息
                    return {
                        "role": message.get("role"),
                        "tool_calls": message.get("tool_calls"),
                        "content": message.get("content", "")
                    }
                elif "function_call" in message:
                    # 兼容旧版本的函数调用格式
                    return {
                        "role": message.get("role"),
                        "function_call": message.get("function_call"),
                        "content": message.get("content", "")
                    }

            return {"content": result["choices"][0]["message"]["content"]}

        except httpx.HTTPStatusError as e:
            raise Exception(f"GLM API 调用失败: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"GLM API 调用异常: {str(e)}")

    def close(self):
        """关闭客户端连接"""
        if self.client:
            self.client.close()
