#!/usr/bin/env python3
"""
Memory Encryption Module for QST Memory System
使用 Fernet (AES-128-CBC + HMAC) 對稱加密

Usage:
    from crypto import MemoryCrypto
    
    crypto = MemoryCrypto()
    encrypted = crypto.encrypt("敏感數據")
    decrypted = crypto.decrypt(encrypted)
"""

import os
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class MemoryCrypto:
    """記憶加密管理器"""
    
    def __init__(self, key_file: str = None, password: str = None):
        """
        初始化加密器
        
        Args:
            key_file: 密鑰文件路徑 (默認 ~/.qst_memory.key)
            password: 主密碼（可選，用於生成密鑰）
        """
        self.key_file = Path(key_file or Path.home() / ".qst_memory.key")
        self._fernet = None
        self._init_key(password)
    
    def _init_key(self, password: str = None):
        """初始化或生成密鑰"""
        if self.key_file.exists():
            # 讀取現有密鑰
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # 生成新密鑰
            if password:
                # 從密碼派生密鑰
                key = self._derive_key(password)
            else:
                # 生成隨機密鑰
                key = Fernet.generate_key()
            
            # 保存密鑰
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # 設置權限
            os.chmod(self.key_file, 0o600)
            print(f"✅ 新密鑰已生成: {self.key_file}")
        
        self._fernet = Fernet(key)
    
    def _derive_key(self, password: str) -> bytes:
        """從密碼派生密鑰"""
        salt = b"QST_MEMORY_SALT_2026"  # 固定鹽值
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密文本
        
        Args:
            plaintext: 明文
        
        Returns:
            加密後的 base64 字符串（帶 ENC:: 前綴）
        """
        if not plaintext:
            return plaintext
        
        encrypted = self._fernet.encrypt(plaintext.encode())
        return f"ENC::{encrypted.decode()}"
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密文本
        
        Args:
            ciphertext: 密文（帶 ENC:: 前綴）
        
        Returns:
            解密後的明文
        """
        if not ciphertext.startswith("ENC::"):
            return ciphertext
        
        encrypted = ciphertext[5:].encode()  # 移除 ENC:: 前綴
        decrypted = self._fernet.decrypt(encrypted)
        return decrypted.decode()
    
    def is_encrypted(self, text: str) -> bool:
        """檢查文本是否已加密"""
        return text.startswith("ENC::")
    
    def encrypt_memory(self, content: str, sensitive_keywords: list = None) -> str:
        """
        智能加密記憶
        自動識別敏感內容並加密
        
        Args:
            content: 記憶內容
            sensitive_keywords: 敏感關鍵詞列表
        
        Returns:
            加密後的內容
        """
        if sensitive_keywords is None:
            sensitive_keywords = [
                'password', 'pwd', 'secret', 'key', 'token', 
                'api_key', 'apikey', 'credential', 'auth',
                '密碼', '金鑰', '憑證', 'PAT', 'OAuth'
            ]
        
        content_lower = content.lower()
        
        # 檢查是否包含敏感關鍵詞
        is_sensitive = any(kw.lower() in content_lower for kw in sensitive_keywords)
        
        if is_sensitive:
            return self.encrypt(content)
        
        return content


def main():
    """測試加密功能"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QST Memory Encryption")
    parser.add_argument("--generate-key", action="store_true", help="生成新密鑰")
    parser.add_argument("--encrypt", type=str, help="加密文本")
    parser.add_argument("--decrypt", type=str, help="解密文本")
    parser.add_argument("--password", type=str, help="主密碼")
    
    args = parser.parse_args()
    
    crypto = MemoryCrypto(password=args.password)
    
    if args.generate_key:
        print(f"✅ 密鑰文件: {crypto.key_file}")
    
    if args.encrypt:
        encrypted = crypto.encrypt(args.encrypt)
        print(f"加密結果:\n{encrypted}")
    
    if args.decrypt:
        decrypted = crypto.decrypt(args.decrypt)
        print(f"解密結果:\n{decrypted}")
    
    if not any([args.generate_key, args.encrypt, args.decrypt]):
        # 互動測試
        print("\n=== QST Memory 加密測試 ===\n")
        
        test_text = "GitHub PAT: ghp_xxxxxxxxxxxx"
        print(f"原文: {test_text}")
        
        encrypted = crypto.encrypt(test_text)
        print(f"加密: {encrypted[:50]}...")
        
        decrypted = crypto.decrypt(encrypted)
        print(f"解密: {decrypted}")
        
        print(f"\n✅ 加密測試成功！")


if __name__ == "__main__":
    main()
