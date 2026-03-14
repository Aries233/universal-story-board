"""
Universal Story Board - 加密工具模块
用于 API Key 的加密存储与脱敏显示
"""
from cryptography.fernet import Fernet


class CryptoUtils:
    """加密工具类（用于 API Key 加密存储）"""

    def __init__(self, encryption_key: str = ""):
        """
        初始化加密工具
        Args:
            encryption_key: 加密密钥（优先使用参数，如果为空则自动生成）
        """
        # 如果没有提供密钥，自动生成
        key = encryption_key if encryption_key else Fernet.generate_key().decode()

        # 如果密钥是自动生成的，提示用户添加到 .env 文件
        if not encryption_key:
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


# 全局实例（使用延迟导入避免循环依赖）
_crypto_instance = None


def get_crypto(encryption_key: str = "") -> CryptoUtils:
    """
    获取加密工具实例（单例模式）

    Args:
        encryption_key: 加密密钥（如果为空，则从配置中读取）

    Returns:
        CryptoUtils 实例
    """
    global _crypto_instance

    # 如果已创建实例，直接返回
    if _crypto_instance is not None:
        return _crypto_instance

    # 如果没有提供密钥，尝试从配置中读取
    if not encryption_key:
        try:
            from app.config import settings
            encryption_key = settings.encryption_key
        except ImportError:
            # 如果无法导入配置（如测试环境），使用空密钥（会自动生成）
            encryption_key = ""

    _crypto_instance = CryptoUtils(encryption_key)
    return _crypto_instance


# 为了向后兼容，提供一个全局实例（已弃用，建议使用 get_crypto()）
crypto = get_crypto()
