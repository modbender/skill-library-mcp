#!/usr/bin/env python3
"""
TTS 配置管理器 - 持久化用户 TTS 偏好设置

用法:
  python3 config_manager.py --get                  # 查看所有配置
  python3 config_manager.py --get voice             # 查看单个配置
  python3 config_manager.py --set voice zh-CN-XiaoxiaoNeural
  python3 config_manager.py --set rate "+10%"
  python3 config_manager.py --reset                 # 恢复默认
  python3 config_manager.py --to-cli                # 转为 CLI 参数
"""

import argparse
import json
import os
import sys

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".tts-config.json")

DEFAULT_CONFIG = {
    "voice": "en-US-MichelleNeural",
    "lang": "en-US",
    "rate": "+0%",
    "volume": "+0%",
    "pitch": "+0Hz",
    "subtitles": False,
    "proxy": "",
    "timeout": 60,
}


def load_config(config_path=DEFAULT_CONFIG_PATH):
    """加载配置，不存在则返回默认值"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        return {**DEFAULT_CONFIG, **loaded}
    except (FileNotFoundError, json.JSONDecodeError):
        return {**DEFAULT_CONFIG}


def save_config(config, config_path=DEFAULT_CONFIG_PATH):
    """保存配置到文件"""
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def config_to_args(config):
    """将配置转换为 tts_converter.py 的 CLI 参数"""
    args = []
    if config.get("voice"):
        args.extend(["--voice", config["voice"]])
    if config.get("lang"):
        args.extend(["--lang", config["lang"]])
    if config.get("rate") and config["rate"] != "+0%":
        args.extend(["--rate", config["rate"]])
    if config.get("volume") and config["volume"] != "+0%":
        args.extend(["--volume", config["volume"]])
    if config.get("pitch") and config["pitch"] != "+0Hz":
        args.extend(["--pitch", config["pitch"]])
    if config.get("subtitles"):
        args.append("--subtitles")
    if config.get("proxy"):
        args.extend(["--proxy", config["proxy"]])
    if config.get("timeout", 60) != 60:
        args.extend(["--timeout", str(config["timeout"])])
    return args


def main():
    parser = argparse.ArgumentParser(description="Manage TTS configuration")
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH, help="Config file path")
    parser.add_argument("--get", nargs="?", const="__all__", metavar="KEY", help="Get config value (or all)")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set config value")
    parser.add_argument("--reset", action="store_true", help="Reset to defaults")
    parser.add_argument("--to-cli", action="store_true", help="Convert config to CLI arguments")

    args = parser.parse_args()
    config_path = args.config_path

    if args.reset:
        config = {**DEFAULT_CONFIG}
        save_config(config, config_path)
        print("Configuration reset to defaults")
        print(json.dumps(config, indent=2))
        return

    if args.get is not None:
        config = load_config(config_path)
        if args.get == "__all__":
            print(json.dumps(config, indent=2))
        else:
            val = config.get(args.get)
            if val is not None:
                print(f"{args.get} = {val}")
            else:
                print(f"Unknown key: {args.get}")
                sys.exit(1)
        return

    if args.set:
        key, value = args.set
        if key not in DEFAULT_CONFIG:
            print(f"Unknown key: {key}. Valid keys: {', '.join(DEFAULT_CONFIG.keys())}")
            sys.exit(1)
        config = load_config(config_path)
        # 类型转换
        if key == "timeout":
            value = int(value)
        elif key == "subtitles":
            value = value.lower() in ("true", "1", "yes")
        config[key] = value
        save_config(config, config_path)
        print(f"Set {key} = {value}")
        return

    if args.to_cli:
        config = load_config(config_path)
        cli_args = config_to_args(config)
        print(" ".join(cli_args))
        return

    # 无参数时显示当前配置
    config = load_config(config_path)
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
