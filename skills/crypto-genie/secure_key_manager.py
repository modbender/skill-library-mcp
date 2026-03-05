"""
Secure Key Storage for Crypto Genie
Encrypts API keys locally with user-provided password
"""

import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureKeyManager:
    """Manages encrypted storage of API keys"""
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path.home() / ".config" / "crypto-genie"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.keyfile = self.config_dir / "encrypted_keys.json"
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def store_api_key(self, api_key: str, password: str) -> bool:
        """
        Encrypt and store API key with user password
        
        Args:
            api_key: The Etherscan API key to encrypt
            password: User's password for encryption
            
        Returns:
            bool: True if successful
        """
        try:
            # Generate random salt
            salt = os.urandom(16)
            
            # Derive encryption key from password
            encryption_key = self._derive_key(password, salt)
            
            # Encrypt API key
            fernet = Fernet(encryption_key)
            encrypted_key = fernet.encrypt(api_key.encode())
            
            # Store encrypted key and salt
            data = {
                "salt": base64.b64encode(salt).decode('utf-8'),
                "encrypted_key": base64.b64encode(encrypted_key).decode('utf-8')
            }
            
            with open(self.keyfile, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set restrictive permissions (owner only)
            os.chmod(self.keyfile, 0o600)
            
            return True
            
        except Exception as e:
            print(f"Error storing API key: {e}")
            return False
    
    def retrieve_api_key(self, password: str) -> str:
        """
        Decrypt and retrieve API key
        
        Args:
            password: User's password for decryption
            
        Returns:
            str: Decrypted API key or empty string if failed
        """
        try:
            if not self.keyfile.exists():
                return ""
            
            # Load encrypted data
            with open(self.keyfile, 'r') as f:
                data = json.load(f)
            
            salt = base64.b64decode(data['salt'])
            encrypted_key = base64.b64decode(data['encrypted_key'])
            
            # Derive decryption key
            decryption_key = self._derive_key(password, salt)
            
            # Decrypt API key
            fernet = Fernet(decryption_key)
            api_key = fernet.decrypt(encrypted_key).decode()
            
            return api_key
            
        except Exception as e:
            print(f"Error retrieving API key (wrong password?): {e}")
            return ""
    
    def has_stored_key(self) -> bool:
        """Check if encrypted key exists"""
        return self.keyfile.exists()
    
    def delete_stored_key(self) -> bool:
        """Delete stored encrypted key"""
        try:
            if self.keyfile.exists():
                self.keyfile.unlink()
            return True
        except Exception as e:
            print(f"Error deleting key: {e}")
            return False


# Helper functions for easy integration

def setup_api_key():
    """Interactive setup for API key encryption"""
    import getpass
    
    print("🔐 Secure API Key Setup")
    print("=" * 50)
    
    manager = SecureKeyManager()
    
    if manager.has_stored_key():
        print("⚠️  You already have a stored API key.")
        overwrite = input("Do you want to overwrite it? (yes/no): ").lower()
        if overwrite != 'yes':
            print("Setup cancelled.")
            return False
    
    print("\nGet your free Etherscan API key:")
    print("👉 https://etherscan.io/myapikey")
    print()
    
    api_key = input("Enter your Etherscan API key: ").strip()
    if not api_key:
        print("❌ No API key provided.")
        return False
    
    print("\nCreate a password to encrypt your API key locally.")
    print("This password will be needed each time you use the skill.")
    
    password = getpass.getpass("Enter encryption password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("❌ Passwords don't match!")
        return False
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        return False
    
    if manager.store_api_key(api_key, password):
        print("\n✅ API key encrypted and stored successfully!")
        print(f"📁 Location: {manager.keyfile}")
        print("\n🔒 Your API key is now encrypted on disk.")
        print("   You'll need your password to use it.")
        return True
    else:
        print("❌ Failed to store API key.")
        return False


def get_api_key(password: str = None) -> str:
    """
    Get API key (from environment, encrypted storage, or prompt)
    
    Args:
        password: Optional password for decryption
        
    Returns:
        str: API key or empty string
    """
    # 1. Check environment variable first (highest priority)
    if env_key := os.environ.get("ETHERSCAN_API_KEY"):
        return env_key
    
    # 2. Try to load from encrypted storage
    manager = SecureKeyManager()
    
    if manager.has_stored_key():
        if password is None:
            # In automated/server mode, can't prompt
            return ""
        
        return manager.retrieve_api_key(password)
    
    # 3. No key available
    return ""


if __name__ == "__main__":
    # Run setup wizard
    setup_api_key()
