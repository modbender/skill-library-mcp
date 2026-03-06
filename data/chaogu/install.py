#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Stock Analysis Skill - 安装脚本"""

import os
import subprocess
import sys

def install_dependencies():
    """安装依赖包"""
    print("[安装] 安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "akshare", "pandas"], check=True)
        print("[成功] 依赖包安装成功")
    except subprocess.CalledProcessError as e:
        print(f"[错误] 依赖包安装失败: {e}")
        return False
    return True

def test_akshare():
    """测试 akshare 连接"""
    print("\n[测试] 测试 akshare 连接...")
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        print(f"[成功] akshare 连接成功，获取到 {len(df)} 只股票数据")
        return True
    except Exception as e:
        print(f"[错误] akshare 连接失败: {e}")
        return False

def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("Stock Analysis Skill 安装完成")
    print("=" * 60)
    print("\n[使用] 使用方法：")
    print("\n1. 实时行情分析:")
    print("   python ~/.openclaw/skills/stock-analysis/scripts/quick_analysis.py")
    print("\n2. 股票推荐:")
    print("   python ~/.openclaw/skills/stock-analysis/scripts/stock_recommend.py")
    print("\n3. 早盘报告:")
    print("   python ~/.openclaw/skills/stock-analysis/scripts/morning_report.py")
    print("\n4. 定时自动分析:")
    print("   openclaw cron add --name 'A股数据分析-每小时' --cron '0 * * * *' --tz 'Asia/Shanghai' ...")
    print("\n[文档] 更多信息请查看: ~/.openclaw/skills/stock-analysis/README.md")
    print("\n[快速开始]")
    print("   python ~/.openclaw/skills/stock-analysis/scripts/quick_analysis.py")
    print("=" * 60)

def main():
    """主函数"""
    print("=" * 60)
    print("Stock Analysis Skill 安装程序")
    print("=" * 60)

    # 安装依赖
    if not install_dependencies():
        print("\n[警告] 依赖包安装失败，技能可能无法正常使用")
        return

    # 测试连接
    if test_akshare():
        show_usage()
        print("\n[成功] 技能安装完成，可以开始使用！")
    else:
        print("\n[警告] akshare 连接测试失败，请检查网络连接")

if __name__ == "__main__":
    main()
