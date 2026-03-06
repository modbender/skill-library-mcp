#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 内置浏览器切换工具
===========================

一键启用/禁用 OpenClaw 内置浏览器

用法：
    python browser_toggle.py --enable    # 启用内置浏览器
    python browser_toggle.py --disable   # 禁用（恢复默认）
    python browser_toggle.py --status    # 查看状态
    python browser_toggle.py --headless  # 切换到无头模式

作者：AI Assistant
日期：2026-02-28
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserToggle:
    """浏览器配置切换器"""
    
    def __init__(self):
        # 配置文件路径
        self.config_file = Path.home() / ".openclaw" / "openclaw.json"
        self.backup_dir = Path.home() / ".openclaw" / "workspace" / "backups"
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 内置浏览器配置
        self.browser_config = {
            "browser": {
                "enabled": True,
                "defaultProfile": "openclaw",
                "headless": False,
                "noSandbox": False,
                "attachOnly": False,
                "executablePath": self._get_chrome_path()
            }
        }
    
    def _get_chrome_path(self) -> str:
        """获取 Chrome 安装路径"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        elif system == "Darwin":  # macOS
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:  # Linux
            # 尝试多个可能的路径
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
            for path in paths:
                if Path(path).exists():
                    return path
            return "/usr/bin/google-chrome"  # 默认
    
    def load_config(self) -> Optional[Dict]:
        """加载配置文件"""
        if not self.config_file.exists():
            logger.error(f"配置文件不存在：{self.config_file}")
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"加载配置失败：{e}")
            return None
    
    def save_config(self, config: Dict) -> bool:
        """保存配置文件"""
        try:
            # 先备份
            self._backup_config()
            
            # 写入配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存：{self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败：{e}")
            return False
    
    def _backup_config(self) -> Optional[str]:
        """备份配置文件"""
        if not self.config_file.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_file = self.backup_dir / f"openclaw-{timestamp}-before-browser-toggle.json"
            shutil.copy2(self.config_file, backup_file)
            logger.info(f"配置已备份：{backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.warning(f"备份失败：{e}")
            return None
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """从备份恢复"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"备份文件不存在：{backup_file}")
                return False
            
            shutil.copy2(backup_path, self.config_file)
            logger.info(f"配置已恢复：{backup_file}")
            return True
        except Exception as e:
            logger.error(f"恢复失败：{e}")
            return False
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        config = self.load_config()
        if not config:
            return {"error": "无法加载配置"}
        
        browser_config = config.get("browser", {})
        is_enabled = browser_config.get("enabled", False)
        profile = browser_config.get("defaultProfile", "chrome")
        headless = browser_config.get("headless", True)
        
        return {
            "enabled": is_enabled,
            "profile": profile,
            "headless": headless,
            "mode": "内置浏览器" if is_enabled and profile == "openclaw" else "Chrome 扩展"
        }
    
    def enable_browser(self, headless: bool = False) -> bool:
        """启用内置浏览器"""
        logger.info("启用内置浏览器...")
        
        config = self.load_config()
        if not config:
            return False
        
        # 更新配置
        config["browser"] = {
            "enabled": True,
            "defaultProfile": "openclaw",
            "headless": headless,
            "noSandbox": False,
            "attachOnly": False,
            "executablePath": self.browser_config["browser"]["executablePath"]
        }
        
        # 保存配置
        if self.save_config(config):
            logger.info("✅ 内置浏览器已启用")
            logger.info(f"   Profile: openclaw")
            logger.info(f"   无头模式：{'是' if headless else '否'}")
            logger.info(f"   Chrome 路径：{self.browser_config['browser']['executablePath']}")
            logger.info("\n⚠️ 需要重启 OpenClaw 才能生效")
            logger.info("   运行：openclaw gateway restart")
            return True
        
        return False
    
    def disable_browser(self) -> bool:
        """禁用内置浏览器（恢复默认）"""
        logger.info("禁用内置浏览器，恢复默认配置...")
        
        config = self.load_config()
        if not config:
            return False
        
        # 移除 browser 配置
        if "browser" in config:
            del config["browser"]
        
        # 保存配置
        if self.save_config(config):
            logger.info("✅ 已恢复默认配置")
            logger.info("   使用 Chrome 扩展模式")
            logger.info("\n⚠️ 需要重启 OpenClaw 才能生效")
            logger.info("   运行：openclaw gateway restart")
            return True
        
        return False
    
    def set_headless(self, headless: bool) -> bool:
        """切换无头模式"""
        logger.info(f"切换无头模式：{'开启' if headless else '关闭'}")
        
        config = self.load_config()
        if not config:
            return False
        
        if "browser" not in config:
            logger.error("内置浏览器未启用，请先运行 --enable")
            return False
        
        config["browser"]["headless"] = headless
        
        if self.save_config(config):
            logger.info(f"✅ 无头模式已{'开启' if headless else '关闭'}")
            logger.info("\n⚠️ 需要重启 OpenClaw 才能生效")
            return True
        
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw 内置浏览器切换工具")
    parser.add_argument("--enable", action="store_true", help="启用内置浏览器")
    parser.add_argument("--disable", action="store_true", help="禁用内置浏览器")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--headless", action="store_true", help="切换到无头模式")
    parser.add_argument("--visible", action="store_true", help="切换到可视化模式")
    parser.add_argument("--restore", type=str, help="从备份文件恢复")
    
    args = parser.parse_args()
    
    toggle = BrowserToggle()
    
    if args.status:
        status = toggle.get_status()
        print("\n" + "=" * 50)
        print("OpenClaw 浏览器配置状态")
        print("=" * 50)
        print(f"模式：{status.get('mode', '未知')}")
        print(f"已启用：{status.get('enabled', False)}")
        print(f"Profile: {status.get('profile', '未知')}")
        print(f"无头模式：{status.get('headless', False)}")
        print("=" * 50)
    
    elif args.enable:
        headless = args.headless  # 如果同时指定 --headless
        if toggle.enable_browser(headless=headless):
            print("\n✅ 启用成功！")
            sys.exit(0)
        else:
            print("\n❌ 启用失败！")
            sys.exit(1)
    
    elif args.disable:
        if toggle.disable_browser():
            print("\n✅ 禁用成功！")
            sys.exit(0)
        else:
            print("\n❌ 禁用失败！")
            sys.exit(1)
    
    elif args.headless:
        if toggle.set_headless(True):
            print("\n✅ 已切换到无头模式")
            sys.exit(0)
        else:
            print("\n❌ 切换失败！")
            sys.exit(1)
    
    elif args.visible:
        if toggle.set_headless(False):
            print("\n✅ 已切换到可视化模式")
            sys.exit(0)
        else:
            print("\n❌ 切换失败！")
            sys.exit(1)
    
    elif args.restore:
        if toggle.restore_from_backup(args.restore):
            print("\n✅ 恢复成功！")
            sys.exit(0)
        else:
            print("\n❌ 恢复失败！")
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\n" + "=" * 50)
        print("示例：")
        print("  启用内置浏览器：python browser_toggle.py --enable")
        print("  启用（无头模式）：python browser_toggle.py --enable --headless")
        print("  禁用内置浏览器：python browser_toggle.py --disable")
        print("  查看状态：python browser_toggle.py --status")
        print("  切换到无头：python browser_toggle.py --headless")
        print("  切换到可视：python browser_toggle.py --visible")
        print("=" * 50)


if __name__ == "__main__":
    main()
