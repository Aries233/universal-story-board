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
        """
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
        """
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
