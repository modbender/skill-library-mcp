#!/usr/bin/env python3
"""
Zvukogram Balance Checker
Проверка баланса токенов
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://zvukogram.com/index.php?r=api"


def load_config():
    """Загрузка конфигурации"""
    config_path = Path.home() / ".config/zvukogram/config.json"
    
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    token = os.environ.get("ZVUKOGRAM_TOKEN")
    email = os.environ.get("ZVUKOGRAM_EMAIL")
    
    if token and email:
        return {"token": token, "email": email}
    
    return None


def check_balance(token, email):
    """Проверка баланса"""
    url = f"{API_BASE}/balance"
    data = urllib.parse.urlencode({"token": token, "email": email}).encode()
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result.get("balans")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def main():
    config = load_config()
    if not config:
        print("Error: Не найдена конфигурация", file=sys.stderr)
        sys.exit(1)
    
    balance = check_balance(config["token"], config["email"])
    
    if balance is not None:
        print(f"Баланс: {balance} токенов")
        print(f"Примерно {(float(balance) / 0.5):.0f} тысяч символов (голос Алена)")
    else:
        print("Не удалось получить баланс", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
