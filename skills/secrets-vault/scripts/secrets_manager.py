#!/usr/bin/env python3
"""Secrets Vault Manager - Secure storage for API keys, passwords, and credentials."""

import os
import sys
import json
import getpass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from crypto_utils import encrypt_data, decrypt_data, generate_password, check_password_strength

# Paths
VAULT_DIR = Path.home() / '.secrets-vault'
VAULT_FILE = VAULT_DIR / 'vault.enc'
CONFIG_FILE = VAULT_DIR / 'config.json'
SESSION_FILE = VAULT_DIR / '.session'

# Session timeout in seconds (default 30 minutes)
SESSION_TIMEOUT = 1800


class SecretsVault:
    def __init__(self):
        self.master_password: Optional[str] = None
        self.secrets: Dict[str, Any] = {}
        self.unlocked = False

    def _get_password_from_env(self) -> Optional[str]:
        """Get password from environment variable or file."""
        password = os.environ.get('SECRETS_VAULT_PASSWORD')
        if password:
            return password

        password_file = os.environ.get('SECRETS_VAULT_PASSWORD_FILE')
        if password_file and os.path.exists(password_file):
            with open(password_file, 'r') as f:
                return f.read().strip()

        return None

    def _get_session_password(self) -> Optional[str]:
        """Get password from session file if still valid."""
        if not SESSION_FILE.exists():
            return None

        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
            # Check timeout
            created = datetime.fromisoformat(data.get('created', '2000-01-01'))
            if (datetime.now() - created).total_seconds() < SESSION_TIMEOUT:
                return data.get('password_hash')
        except:
            pass
        return None

    def _save_session(self):
        """Save session state."""
        with open(SESSION_FILE, 'w') as f:
            json.dump({
                'created': datetime.now().isoformat(),
                'password_hash': hashlib.sha256(self.master_password.encode()).hexdigest()
            }, f)
        os.chmod(SESSION_FILE, 0o600)

    def init_vault(self, password: Optional[str] = None) -> bool:
        """Initialize a new vault."""
        if VAULT_FILE.exists():
            print("Vault already exists. Use 'unlock' to access it.")
            return False

        if not password:
            print("\n=== Initialize New Vault ===")
            print("Creating a strong master password is critical for security.")
            print("Recommend: 20+ characters with upper, lower, digits, and symbols.\n")

            # Offer to generate password
            choice = input("Generate a strong password for you? (y/n): ").strip().lower()
            if choice == 'y':
                password = generate_password(24)
                print(f"\nGenerated password: {password}")
                print("⚠️  SAVE THIS PASSWORD SECURELY! It cannot be recovered!\n")
                confirm = input("Have you saved the password? (yes): ").strip().lower()
                if confirm != 'yes':
                    print("Aborted. Password not saved.")
                    return False
            else:
                while True:
                    password = getpass.getpass("Enter master password: ")
                    strength = check_password_strength(password)
                    print(f"Password strength: {strength['rating']} (score: {strength['score']}/8)")

                    if strength['rating'] == 'weak':
                        print("Password is too weak. Please use a stronger password.")
                        continue

                    confirm = getpass.getpass("Confirm master password: ")
                    if password != confirm:
                        print("Passwords do not match. Try again.")
                        continue
                    break

        # Create empty vault
        self.secrets = {'_meta': {'created': datetime.now().isoformat(), 'version': '1.0'}}
        self._save_vault(password)
        self.master_password = password

        # Save config
        config = {'version': '1.0', 'created': datetime.now().isoformat()}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        # Set permissions
        os.chmod(VAULT_FILE, 0o600)
        os.chmod(CONFIG_FILE, 0o600)

        print("\n✓ Vault initialized successfully!")
        self.unlocked = True
        self._save_session()
        return True

    def unlock(self, password: Optional[str] = None) -> bool:
        """Unlock the vault with master password."""
        if not VAULT_FILE.exists():
            print("Vault not found. Run 'init' first.")
            return False

        # Check session
        session_pw = self._get_session_password()
        if session_pw and not password:
            # Try session password (we need the actual password, not hash)
            pass  # Session won't work for actual decryption

        if not password:
            password = self._get_password_from_env()
            if not password:
                password = getpass.getpass("Master password: ")

        try:
            with open(VAULT_FILE, 'rb') as f:
                encrypted = f.read()

            decrypted = decrypt_data(encrypted, password)
            self.secrets = json.loads(decrypted.decode('utf-8'))
            self.master_password = password
            self.unlocked = True
            self._save_session()
            print("✓ Vault unlocked.")
            return True
        except Exception as e:
            print(f"✗ Failed to unlock: Invalid password or corrupted vault.")
            return False

    def _save_vault(self, password: Optional[str] = None):
        """Save vault to disk."""
        pw = password or self.master_password
        if not pw:
            raise ValueError("No password available")

        self.secrets['_meta']['modified'] = datetime.now().isoformat()
        data = json.dumps(self.secrets, indent=2, ensure_ascii=False).encode('utf-8')
        encrypted = encrypt_data(data, pw)

        with open(VAULT_FILE, 'wb') as f:
            f.write(encrypted)

    def lock(self):
        """Lock the vault."""
        self.master_password = None
        self.secrets = {}
        self.unlocked = False
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
        print("✓ Vault locked.")

    def add_secret(self, name: str, secret_type: str = 'api_key', **kwargs):
        """Add a secret to the vault."""
        if not self.unlocked:
            print("Vault is locked. Run 'unlock' first.")
            return False

        if name in self.secrets and name != '_meta':
            print(f"Secret '{name}' already exists. Use 'update' to modify.")
            return False

        secret = {
            'type': secret_type,
            'created': datetime.now().isoformat(),
            **kwargs
        }

        self.secrets[name] = secret
        self._save_vault()
        print(f"✓ Secret '{name}' added.")
        return True

    def get_secret(self, name: str, show: bool = False) -> Optional[Dict]:
        """Get a secret from the vault."""
        if not self.unlocked:
            print("Vault is locked. Run 'unlock' first.")
            return None

        if name not in self.secrets:
            print(f"Secret '{name}' not found.")
            return None

        secret = self.secrets[name]
        print(f"\n=== {name} ===")
        print(f"Type: {secret.get('type', 'unknown')}")
        print(f"Created: {secret.get('created', 'unknown')}")

        if show:
            for key, value in secret.items():
                if key not in ['type', 'created']:
                    print(f"{key}: {value}")
        else:
            # Hide sensitive values
            for key, value in secret.items():
                if key not in ['type', 'created']:
                    if key in ['key', 'password', 'secret', 'token']:
                        print(f"{key}: {'*' * 8}")
                    else:
                        print(f"{key}: {value}")

        return secret

    def list_secrets(self):
        """List all secrets in the vault."""
        if not self.unlocked:
            print("Vault is locked. Run 'unlock' first.")
            return

        secrets = {k: v for k, v in self.secrets.items() if k != '_meta'}

        if not secrets:
            print("No secrets stored.")
            return

        print("\n=== Stored Secrets ===")
        for name, secret in secrets.items():
            tags = secret.get('tags', '')
            tag_str = f" [{tags}]" if tags else ""
            print(f"  • {name} ({secret.get('type', 'unknown')}){tag_str}")

    def delete_secret(self, name: str) -> bool:
        """Delete a secret from the vault."""
        if not self.unlocked:
            print("Vault is locked. Run 'unlock' first.")
            return False

        if name not in self.secrets:
            print(f"Secret '{name}' not found.")
            return False

        del self.secrets[name]
        self._save_vault()
        print(f"✓ Secret '{name}' deleted.")
        return True

    def update_secret(self, name: str, **kwargs) -> bool:
        """Update a secret in the vault."""
        if not self.unlocked:
            print("Vault is locked. Run 'unlock' first.")
            return False

        if name not in self.secrets:
            print(f"Secret '{name}' not found.")
            return False

        self.secrets[name].update(kwargs)
        self.secrets[name]['modified'] = datetime.now().isoformat()
        self._save_vault()
        print(f"✓ Secret '{name}' updated.")
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Secrets Vault Manager')
    parser.add_argument('command', choices=['init', 'unlock', 'lock', 'add', 'get', 'list', 'delete', 'update', 'generate'],
                        help='Command to execute')
    parser.add_argument('name', nargs='?', help='Secret name')
    parser.add_argument('--type', default='api_key', help='Secret type (api_key, database, password)')
    parser.add_argument('--key', help='API key value')
    parser.add_argument('--username', help='Username')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--host', help='Database host')
    parser.add_argument('--port', help='Database port')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--tags', help='Comma-separated tags')
    parser.add_argument('--show', action='store_true', help='Show secret values')
    parser.add_argument('--length', type=int, default=24, help='Password length for generate')
    parser.add_argument('--master-password', help='Master password (for non-interactive use)')
    parser.add_argument('--generate-master', action='store_true', help='Generate a strong master password')

    args = parser.parse_args()

    vault = SecretsVault()

    # Import hashlib for session
    global hashlib
    import hashlib

    if args.command == 'init':
        if args.generate_master:
            master_pw = generate_password(24)
            print(f"Generated master password: {master_pw}")
            print("⚠️  SAVE THIS PASSWORD SECURELY! It cannot be recovered!")
            vault.init_vault(master_pw)
        elif args.master_password:
            vault.init_vault(args.master_password)
        else:
            vault.init_vault()

    elif args.command == 'unlock':
        vault.unlock(args.master_password)

    elif args.command == 'lock':
        vault.lock()

    elif args.command == 'add':
        if not args.name:
            print("Error: Secret name required")
            sys.exit(1)

        # Interactive mode if no key provided
        if args.type == 'api_key' and not args.key:
            args.key = getpass.getpass(f"Enter API key for {args.name}: ")

        kwargs = {}
        if args.key:
            kwargs['key'] = args.key
        if args.username:
            kwargs['username'] = args.username
        if args.password:
            kwargs['password'] = args.password
        if args.host:
            kwargs['host'] = args.host
        if args.port:
            kwargs['port'] = args.port
        if args.database:
            kwargs['database'] = args.database
        if args.tags:
            kwargs['tags'] = args.tags

        vault.unlock(args.master_password) and vault.add_secret(args.name, args.type, **kwargs)

    elif args.command == 'get':
        if not args.name:
            print("Error: Secret name required")
            sys.exit(1)
        vault.unlock(args.master_password) and vault.get_secret(args.name, show=args.show)

    elif args.command == 'list':
        vault.unlock(args.master_password) and vault.list_secrets()

    elif args.command == 'delete':
        if not args.name:
            print("Error: Secret name required")
            sys.exit(1)
        vault.unlock(args.master_password) and vault.delete_secret(args.name)

    elif args.command == 'update':
        if not args.name:
            print("Error: Secret name required")
            sys.exit(1)
        kwargs = {}
        if args.key:
            kwargs['key'] = args.key
        if args.username:
            kwargs['username'] = args.username
        if args.password:
            kwargs['password'] = args.password
        if args.tags:
            kwargs['tags'] = args.tags
        vault.unlock(args.master_password) and vault.update_secret(args.name, **kwargs)

    elif args.command == 'generate':
        print(generate_password(args.length))


if __name__ == '__main__':
    main()
