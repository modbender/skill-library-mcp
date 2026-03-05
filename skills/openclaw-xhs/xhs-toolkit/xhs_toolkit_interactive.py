#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书工具包 - 交互式界面

提供友好的交互式菜单，方便用户操作
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.text_utils import safe_print
from src.cli.manual_commands import manual_command
from src.core.config import XHSConfig
from src.auth.cookie_manager import CookieManager
from src import __version__


class InteractiveMenu:
    """交互式菜单类"""
    
    def __init__(self):
        self.config = XHSConfig()
        self.cookie_manager = CookieManager(self.config)
        
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """打印头部信息"""
        self.clear_screen()
        safe_print(f"""
╭─────────────────────────────────────────╮
│       小红书MCP工具包 v{__version__}        │
│        快速操作菜单系统                 │
╰─────────────────────────────────────────╯
""")
    
    def print_status(self):
        """打印状态信息"""
        # 检查cookies状态
        cookies_valid = self.cookie_manager.validate_cookies()
        cookies_status = "✅ 已登录" if cookies_valid else "❌ 未登录"
        
        safe_print(f"状态: {cookies_status}")
        safe_print("─" * 45)
    
    def main_menu(self):
        """主菜单"""
        while True:
            self.print_header()
            self.print_status()
            
            safe_print("""
【主菜单】

1. 🔄 数据收集
2. 🌐 浏览器操作
3. 📊 数据管理
4. 🍪 Cookie管理
5. 🚀 MCP服务器
6. ⚙️  系统工具
0. 退出

""")
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == "0":
                safe_print("\n👋 感谢使用，再见！")
                break
            elif choice == "1":
                self.data_collection_menu()
            elif choice == "2":
                self.browser_menu()
            elif choice == "3":
                self.data_management_menu()
            elif choice == "4":
                self.cookie_menu()
            elif choice == "5":
                self.server_menu()
            elif choice == "6":
                self.system_menu()
            else:
                safe_print("❌ 无效选择，请重新输入")
                time.sleep(1)
    
    def data_collection_menu(self):
        """数据收集菜单"""
        while True:
            self.print_header()
            safe_print("""
【数据收集】

1. 收集所有数据 (推荐)
2. 只收集Dashboard数据
3. 只收集内容分析数据
4. 只收集粉丝数据
5. 自定义收集
0. 返回主菜单

""")
            choice = input("请选择操作 (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                safe_print("\n📊 开始收集所有数据...")
                manual_command("collect", data_type="all", dimension="both")
                input("\n按回车键继续...")
            elif choice == "2":
                safe_print("\n📊 开始收集Dashboard数据...")
                manual_command("collect", data_type="dashboard", dimension="both")
                input("\n按回车键继续...")
            elif choice == "3":
                safe_print("\n📊 开始收集内容分析数据...")
                manual_command("collect", data_type="content", dimension="both")
                input("\n按回车键继续...")
            elif choice == "4":
                safe_print("\n📊 开始收集粉丝数据...")
                manual_command("collect", data_type="fans", dimension="both")
                input("\n按回车键继续...")
            elif choice == "5":
                self.custom_collection_menu()
            else:
                safe_print("❌ 无效选择")
                time.sleep(1)
    
    def custom_collection_menu(self):
        """自定义收集菜单"""
        self.print_header()
        safe_print("【自定义数据收集】\n")
        
        # 选择数据类型
        safe_print("数据类型:")
        safe_print("1. Dashboard")
        safe_print("2. 内容分析")
        safe_print("3. 粉丝数据")
        safe_print("4. 所有数据")
        
        type_choice = input("\n选择数据类型 (1-4): ").strip()
        type_map = {"1": "dashboard", "2": "content", "3": "fans", "4": "all"}
        data_type = type_map.get(type_choice, "all")
        
        # 选择时间维度
        safe_print("\n时间维度:")
        safe_print("1. 最近7天")
        safe_print("2. 最近30天")
        safe_print("3. 两者都要")
        
        dim_choice = input("\n选择时间维度 (1-3): ").strip()
        dim_map = {"1": "7days", "2": "30days", "3": "both"}
        dimension = dim_map.get(dim_choice, "both")
        
        safe_print(f"\n📊 开始收集 {data_type} 数据 ({dimension})...")
        manual_command("collect", data_type=data_type, dimension=dimension)
        input("\n按回车键继续...")
    
    def browser_menu(self):
        """浏览器操作菜单"""
        while True:
            self.print_header()
            safe_print("""
【浏览器操作】

1. 打开创作者中心首页
2. 打开发布页面
3. 打开数据分析页面
4. 打开粉丝管理页面
5. 打开内容管理页面
6. 打开个人主页
7. 打开发现页面
0. 返回主菜单

""")
            choice = input("请选择页面 (0-7): ").strip()
            
            page_map = {
                "1": "home",
                "2": "publish", 
                "3": "data",
                "4": "fans",
                "5": "content",
                "6": "notes",
                "7": "explore"
            }
            
            if choice == "0":
                break
            elif choice in page_map:
                page = page_map[choice]
                safe_print(f"\n🌐 正在打开页面...")
                result = manual_command("browser", page=page, stay_open=True)
                if not result:
                    safe_print("❌ 打开浏览器失败")
                    input("\n按回车键继续...")
            else:
                safe_print("❌ 无效选择")
                time.sleep(1)
    
    def data_management_menu(self):
        """数据管理菜单"""
        while True:
            self.print_header()
            safe_print("""
【数据管理】

1. 📈 分析数据趋势
2. 📤 导出为Excel
3. 📤 导出为JSON
4. 💾 备份数据
5. 📂 恢复备份
0. 返回主菜单

""")
            choice = input("请选择操作 (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                safe_print("\n📈 分析数据中...")
                manual_command("analyze")
                input("\n按回车键继续...")
            elif choice == "2":
                safe_print("\n📤 导出Excel中...")
                manual_command("export", format="excel")
                input("\n按回车键继续...")
            elif choice == "3":
                safe_print("\n📤 导出JSON中...")
                manual_command("export", format="json")
                input("\n按回车键继续...")
            elif choice == "4":
                safe_print("\n💾 备份数据中...")
                manual_command("backup", include_cookies=True)
                input("\n按回车键继续...")
            elif choice == "5":
                self.restore_backup_menu()
            else:
                safe_print("❌ 无效选择")
                time.sleep(1)
    
    def restore_backup_menu(self):
        """恢复备份菜单"""
        self.print_header()
        safe_print("【恢复备份】\n")
        
        # 列出可用的备份
        backup_dir = Path.cwd() / "backups"
        if backup_dir.exists():
            backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()])
            if backups:
                safe_print("可用的备份:")
                for i, backup in enumerate(backups, 1):
                    safe_print(f"{i}. {backup.name}")
                
                choice = input("\n选择备份编号 (0返回): ").strip()
                if choice.isdigit() and 0 < int(choice) <= len(backups):
                    backup_path = str(backups[int(choice) - 1])
                    safe_print(f"\n📂 恢复备份中...")
                    manual_command("restore", backup_path=backup_path)
                    input("\n按回车键继续...")
                    return
        
        safe_print("❌ 没有找到可用的备份")
        input("\n按回车键继续...")
    
    def cookie_menu(self):
        """Cookie管理菜单"""
        while True:
            self.print_header()
            safe_print("""
【Cookie管理】

1. 🍪 获取新的Cookies
2. 👀 查看Cookies信息
3. ✅ 验证Cookies有效性
4. 🧪 测试ChromeDriver
0. 返回主菜单

""")
            choice = input("请选择操作 (0-4): ").strip()
            
            script_dir = Path(__file__).parent
            
            if choice == "0":
                break
            elif choice == "1":
                safe_print("\n🍪 获取新的Cookies...")
                from src.auth.cookie_manager import CookieManager
                cookie_manager = CookieManager(self.config)
                success = cookie_manager.save_cookies_interactive()
                if success:
                    safe_print("\n✅ Cookies保存成功！")
                else:
                    safe_print("\n❌ Cookies保存失败")
                input("\n按回车键继续...")
            elif choice == "2":
                safe_print("\n👀 查看Cookies信息...")
                from src.auth.cookie_manager import CookieManager
                cookie_manager = CookieManager(self.config)
                cookie_manager.display_cookies_info()
                input("\n按回车键继续...")
            elif choice == "3":
                safe_print("\n✅ 验证Cookies...")
                from src.auth.cookie_manager import CookieManager
                cookie_manager = CookieManager(self.config)
                is_valid = cookie_manager.validate_cookies()
                if is_valid:
                    safe_print("\n✅ Cookies验证通过！")
                else:
                    safe_print("\n❌ Cookies验证失败，建议重新获取")
                input("\n按回车键继续...")
            elif choice == "4":
                safe_print("\n🧪 测试ChromeDriver...")
                from src.auth.cookie_manager import CookieManager
                cookie_manager = CookieManager(self.config)
                success = cookie_manager.test_chromedriver_config()
                input("\n按回车键继续...")
            else:
                safe_print("❌ 无效选择")
                time.sleep(1)
    
    def server_menu(self):
        """MCP服务器菜单"""
        while True:
            self.print_header()
            safe_print("""
【MCP服务器】

1. 🚀 启动服务器
2. 📊 查看配置信息
0. 返回主菜单

""")
            choice = input("请选择操作 (0-2): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                safe_print("\n🚀 启动MCP服务器...")
                safe_print("提示: 按Ctrl+C停止服务器")
                try:
                    from src.server.mcp_server import MCPServer
                    server = MCPServer(self.config)
                    server.start()
                except KeyboardInterrupt:
                    safe_print("\n\n👋 服务器已停止")
                except Exception as e:
                    safe_print(f"\n❌ 启动失败: {e}")
                    input("\n按回车键继续...")
            elif choice == "2":
                safe_print("\n📊 MCP服务器配置:")
                safe_print(f"端口: {self.config.server_port}")
                safe_print(f"主机: {self.config.server_host}")
                input("\n按回车键继续...")
            else:
                safe_print("❌ 无效选择")
                time.sleep(1)
    
    def system_menu(self):
        """系统工具菜单"""
        while True:
            self.print_header()
            safe_print("""
【系统工具】

1. 📊 查看系统状态
2. 🔧 查看配置信息
3. ✅ 验证配置
4. 📄 生成配置示例
0. 返回主菜单

""")
            choice = input("请选择操作 (0-4): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_system_status()
                input("\n按回车键继续...")
            elif choice == "2":
                self.show_config_info()
                input("\n按回车键继续...")
            elif choice == "3":
                self.validate_config()
                input("\n按回车键继续...")
            elif choice == "4":
                safe_print("\n📄 生成配置示例...")
                self.config.save_env_example()
                safe_print("✅ 已生成 env_example 文件")
                safe_print("💡 请复制为 .env 文件并根据需要修改配置")
                input("\n按回车键继续...")
            else:
                safe_print("❌ 无效选择")
                time.sleep(1)
    
    def show_system_status(self):
        """显示系统状态"""
        safe_print("\n📊 系统状态检查:")
        safe_print("=" * 50)
        
        # 配置状态
        validation = self.config.validate_config()
        safe_print(f"🔧 配置状态: {'✅ 正常' if validation['valid'] else '❌ 有问题'}")
        if not validation["valid"]:
            for issue in validation["issues"]:
                safe_print(f"   • {issue}")
        
        # Cookies状态
        cookies = self.cookie_manager.load_cookies()
        safe_print(f"🍪 Cookies状态: {'✅ 已加载' if cookies else '❌ 未找到'} ({len(cookies)} 个)")
        
        # 系统信息
        import platform
        safe_print(f"💻 操作系统: {platform.system()} {platform.release()}")
        safe_print(f"🐍 Python版本: {platform.python_version()}")
    
    def show_config_info(self):
        """显示配置信息"""
        safe_print("\n🔧 当前配置信息:")
        safe_print("=" * 50)
        config_dict = self.config.to_dict()
        for key, value in config_dict.items():
            if "password" in key.lower() or "secret" in key.lower():
                value = "******"
            safe_print(f"{key}: {value}")
    
    def validate_config(self):
        """验证配置"""
        safe_print("\n🔍 验证配置...")
        validation = self.config.validate_config()
        
        if validation["valid"]:
            safe_print("✅ 配置验证通过")
        else:
            safe_print("❌ 配置验证失败:")
            for issue in validation["issues"]:
                safe_print(f"   • {issue}")


def main():
    """主函数"""
    try:
        menu = InteractiveMenu()
        menu.main_menu()
    except KeyboardInterrupt:
        safe_print("\n\n👋 操作已取消")
    except Exception as e:
        safe_print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()