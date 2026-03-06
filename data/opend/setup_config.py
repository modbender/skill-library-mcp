#!/usr/bin/env python3
"""
Setup encrypted config file for MooMoo API credentials.
"""
import getpass
from pathlib import Path

from credentials import generate_key, save_encrypted_config

KEY_PATH = Path("config.key")


def main():
    password = getpass.getpass("Enter MooMoo API password: ")
    config = {'password': password}
    key = generate_key()
    save_encrypted_config(config, key)
    KEY_PATH.write_text(key.decode(), encoding="utf-8")
    KEY_PATH.chmod(0o600)
    print("Encrypted config saved to config.enc")
    print("Legacy credential warning: config.enc is not the recommended OpenClaw deployment mode.")
    print(f"Generated MOOMOO_CONFIG_KEY saved to {KEY_PATH} with mode 600.")
    print("Move that key into a secret manager or OS keychain before using the config method.")

if __name__ == "__main__":
    main()
