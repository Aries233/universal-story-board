"""
Universal Story Board - 加密工具模块
用于 API Key 的加密存储与脱敏显示
"""
from cryptography.fernet import Fernet
import os


class CryptoUtils:
    """加密工具类（用于 API Key 加密存储）"""

    def __init__(self):
        # 从环境变量读取加密密钥（首次运行时自动生成）
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key().decode()
            print(f"⚠️  请将以下加密密钥添加到 .env 文件：")
            print(f"ENCRYPTION_KEY={key}")
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        """加密"""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密"""
        return self.cipher.decrypt(ciphertext.encode()).decode()

    def mask_api_key(self, api_key: str, show_chars: int = 4) -> str:
        """
        脱敏显示
        Args:
            api_key: 原始 API Key
            show_chars: 前后各显示的字符数
        Returns:
            脱敏后的字符串，如 "sk-****abcd"
        """
        if len(api_key) <= show_chars * 2:
            return "*" * len(api_key)
        return api_key[:show_chars] + "*" * (len(api_key) - show_chars * 2) + api_key[-show_chars:]


# 全局实例
crypto = CryptoUtils()
