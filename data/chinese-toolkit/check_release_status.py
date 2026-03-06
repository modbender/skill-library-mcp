#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文工具包发布状态检查脚本
检查所有必要的发布文件是否就绪
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: 文件不存在")
        return False

def check_file_content(file_path, min_size=100):
    """检查文件内容是否完整"""
    if not os.path.exists(file_path):
        return False
    
    file_size = os.path.getsize(file_path)
    if file_size < min_size:
        print(f"⚠️  {os.path.basename(file_path)}: 文件过小 ({file_size}字节)")
        return False
    
    return True

def check_skill_structure():
    """检查技能结构"""
    print("🔍 检查技能结构...")
    print("=" * 50)
    
    # 必需的核心文件
    essential_files = [
        ("SKILL.md", "技能文档", 1000),
        ("README.md", "项目说明文档", 5000),
        ("chinese_tools_core.py", "核心Python模块", 5000),
        ("config.json", "配置文件", 100),
        ("requirements.txt", "Python依赖文件", 50),
        ("LICENSE", "许可证文件", 500),
        (".gitignore", "Git忽略文件", 100),
    ]
    
    # 可选的发布文件
    optional_files = [
        ("setup.py", "Python包配置", 500),
        ("CHANGELOG.md", "变更日志", 500),
        ("CONTRIBUTING.md", "贡献指南", 500),
        ("CODE_OF_CONDUCT.md", "行为准则", 500),
        ("PUBLISH_CHECKLIST.md", "发布检查清单", 1000),
        ("FINAL_RELEASE_GUIDE.md", "最终发布指南", 1000),
        ("one_click_release.ps1", "一键发布脚本", 1000),
    ]
    
    # 检查目录结构
    essential_dirs = [
        ("examples", "示例目录"),
        ("tests", "测试目录"),
        ("references", "参考文档目录"),
        ("scripts", "脚本目录"),
    ]
    
    all_ok = True
    
    # 检查必需文件
    print("\n📁 必需文件检查:")
    for file_name, description, min_size in essential_files:
        file_path = Path(file_name)
        if check_file_exists(file_path, description):
            if not check_file_content(file_path, min_size):
                all_ok = False
        else:
            all_ok = False
    
    # 检查可选文件
    print("\n📁 可选文件检查:")
    optional_count = 0
    for file_name, description, min_size in optional_files:
        file_path = Path(file_name)
        if check_file_exists(file_path, description):
            optional_count += 1
            check_file_content(file_path, min_size)
    
    # 检查目录结构
    print("\n📁 目录结构检查:")
    for dir_name, description in essential_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {description}: {dir_name}/")
        else:
            print(f"⚠️  {description}: 目录不存在")
    
    # 检查配置文件
    print("\n⚙️ 配置文件检查:")
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ config.json: 格式正确")
            
            # 检查必要的配置项
            required_keys = ['api_keys', 'local_services']
            for key in required_keys:
                if key in config:
                    print(f"  ✅ 包含 {key} 配置")
                else:
                    print(f"  ⚠️  缺少 {key} 配置")
                    
        except json.JSONDecodeError as e:
            print(f"❌ config.json: JSON格式错误 - {e}")
            all_ok = False
    else:
        print("❌ config.json: 文件不存在")
        all_ok = False
    
    # 检查依赖文件
    print("\n📦 依赖文件检查:")
    req_path = Path("requirements.txt")
    if req_path.exists():
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_packages = ['jieba', 'pypinyin', 'requests']
        found_packages = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                for pkg in required_packages:
                    if pkg in line.lower():
                        found_packages.append(pkg)
        
        for pkg in required_packages:
            if pkg in found_packages:
                print(f"✅ 包含 {pkg}")
            else:
                print(f"⚠️  缺少 {pkg}")
                all_ok = False
    else:
        print("❌ requirements.txt: 文件不存在")
        all_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 检查结果总结:")
    
    if all_ok:
        print("✅ 所有必需文件就绪，可以发布！")
        print("\n🚀 下一步:")
        print("1. 运行一键发布脚本: .\\one_click_release.ps1 -GitHubUsername 你的用户名")
        print("2. 或按照 FINAL_RELEASE_GUIDE.md 手动发布")
    else:
        print("❌ 存在文件缺失或问题，请修复后再发布")
        print("\n🔧 需要修复:")
        print("1. 检查缺失的必需文件")
        print("2. 修复配置文件格式")
        print("3. 补充依赖包")
    
    print("\n📈 统计信息:")
    print(f"• 必需文件: {len(essential_files)}个")
    print(f"• 可选文件: {optional_count}/{len(optional_files)}个")
    print(f"• 目录结构: {len(essential_dirs)}个")
    
    return all_ok

def check_python_dependencies():
    """检查Python依赖是否可用"""
    print("\n🐍 Python依赖检查:")
    print("=" * 50)
    
    dependencies = [
        ('jieba', '中文分词'),
        ('pypinyin', '拼音转换'),
        ('requests', 'HTTP请求'),
    ]
    
    all_available = True
    for package, description in dependencies:
        try:
            __import__(package)
            print(f"✅ {description}: {package} 可用")
        except ImportError:
            print(f"❌ {description}: {package} 未安装")
            all_available = False
    
    if not all_available:
        print("\n📦 安装缺失的依赖:")
        print("pip install jieba pypinyin requests")
    
    return all_available

def check_functionality():
    """检查核心功能是否正常"""
    print("\n🔧 功能测试检查:")
    print("=" * 50)
    
    test_files = [
        ("simple_test.py", "简单功能测试"),
        ("quick_test.py", "快速功能测试"),
        ("ascii_test.py", "ASCII功能测试"),
    ]
    
    for file_name, description in test_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {description}: {file_name}")
        else:
            print(f"⚠️  {description}: 文件不存在")
    
    # 尝试导入核心模块
    try:
        sys.path.insert(0, str(Path.cwd()))
        from chinese_tools_core import ChineseToolkit
        print("✅ 核心模块: 可以导入")
        
        # 简单功能测试
        toolkit = ChineseToolkit()
        print("✅ 工具包: 可以初始化")
        
    except Exception as e:
        print(f"❌ 核心模块测试失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🌟 中文工具包发布状态检查")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    expected_dir_name = "chinese-toolkit"
    
    if current_dir.name != expected_dir_name:
        print(f"⚠️  请在 {expected_dir_name} 目录中运行此脚本")
        print(f"当前目录: {current_dir}")
        return
    
    print(f"📁 当前目录: {current_dir}")
    
    # 执行检查
    structure_ok = check_skill_structure()
    deps_ok = check_python_dependencies()
    func_ok = check_functionality()
    
    # 最终评估
    print("\n" + "=" * 50)
    print("🎯 发布准备状态评估:")
    
    if structure_ok and deps_ok and func_ok:
        print("✅ 优秀 - 完全准备好发布！")
        print("\n🚀 立即发布命令:")
        print(r'.\one_click_release.ps1 -GitHubUsername "你的用户名"')
    elif structure_ok and func_ok:
        print("✅ 良好 - 可以发布，但需要安装依赖")
        print("\n📦 先安装依赖:")
        print("pip install -r requirements.txt")
    elif structure_ok:
        print("⚠️  一般 - 需要修复功能问题")
        print("\n🔧 需要检查功能实现")
    else:
        print("❌ 需要修复 - 存在结构性问题")
        print("\n📋 请按照检查结果修复问题")
    
    print("\n📚 详细指南:")
    print("• 发布指南: FINAL_RELEASE_GUIDE.md")
    print("• 检查清单: PUBLISH_CHECKLIST.md")
    print("• 市场页面: SKILL_MARKET_PAGE.md")

if __name__ == "__main__":
    main()