"""
Universal Story Board - LLM 适配器基类
定义 LLM 调用的统一接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseLLMAdapter(ABC):
    """LLM 适配器基类"""

    def __init__(self, api_key: str):
        """
        初始化适配器

        Args:
            api_key: API 密钥
        """
        self.api_key = api_key

    @abstractmethod
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            temperature: 温度参数（0-2）

        Returns:
            模型返回的文本
        """
        pass

    @abstractmethod
    def chat_with_json_output(
        self,
        messages: List[Dict],
        schema: Dict[str, Any],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        带结构化输出的聊天接口

        Args:
            messages: 消息列表
            schema: Pydantic Schema 的字典描述
            temperature: 温度参数

        Returns:
            模型返回的结构化数据（已解析为 Python 字典）
        """
        pass

    @abstractmethod
    def chat_with_function_calling(
        self,
        messages: List[Dict],
        functions: List[Dict],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        带函数调用的聊天接口

        Args:
            messages: 消息列表
            functions: 可用函数列表
            temperature: 温度参数

        Returns:
            模型返回的函数调用结果
        """
        pass
