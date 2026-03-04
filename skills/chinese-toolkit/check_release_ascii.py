#!/usr/bin/env python3
# ASCII版本发布状态检查脚本

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    if os.path.exists(file_path):
        print(f"[OK] {description}: {file_path}")
        return True
    else:
        print(f"[MISSING] {description}: 文件不存在")
        return False

def check_file_content(file_path, min_size=100):
    if not os.path.exists(file_path):
        return False
    
    file_size = os.path.getsize(file_path)
    if file_size < min_size:
        print(f"[WARN] {os.path.basename(file_path)}: 文件过小 ({file_size}字节)")
        return False
    
    return True

def main():
    print("=" * 60)
    print("Chinese Toolkit Release Status Check")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = Path.cwd()
    if current_dir.name != "chinese-toolkit":
        print(f"[ERROR] 请在 chinese-toolkit 目录中运行此脚本")
        print(f"当前目录: {current_dir}")
        return
    
    print(f"当前目录: {current_dir}")
    print()
    
    # 必需文件列表
    essential_files = [
        ("SKILL.md", "技能文档", 1000),
        ("README.md", "项目说明文档", 5000),
        ("chinese_tools_core.py", "核心Python模块", 5000),
        ("config.json", "配置文件", 100),
        ("requirements.txt", "Python依赖文件", 50),
        ("LICENSE", "许可证文件", 500),
        (".gitignore", "Git忽略文件", 100),
    ]
    
    # 可选文件列表
    optional_files = [
        ("setup.py", "Python包配置", 500),
        ("CHANGELOG.md", "变更日志", 500),
        ("CONTRIBUTING.md", "贡献指南", 500),
        ("CODE_OF_CONDUCT.md", "行为准则", 500),
        ("PUBLISH_CHECKLIST.md", "发布检查清单", 1000),
        ("FINAL_RELEASE_GUIDE.md", "最终发布指南", 1000),
        ("one_click_release.ps1", "一键发布脚本", 1000),
        ("check_release_status.py", "发布状态检查", 500),
    ]
    
    # 必需目录
    essential_dirs = [
        ("examples", "示例目录"),
        ("tests", "测试目录"),
        ("references", "参考文档目录"),
        ("scripts", "脚本目录"),
    ]
    
    all_ok = True
    
    # 检查必需文件
    print("[SECTION] 必需文件检查:")
    for file_name, description, min_size in essential_files:
        file_path = Path(file_name)
        if check_file_exists(file_path, description):
            if not check_file_content(file_path, min_size):
                all_ok = False
        else:
            all_ok = False
    
    # 检查可选文件
    print()
    print("[SECTION] 可选文件检查:")
    optional_count = 0
    for file_name, description, min_size in optional_files:
        file_path = Path(file_name)
        if check_file_exists(file_path, description):
            optional_count += 1
            check_file_content(file_path, min_size)
    
    # 检查目录
    print()
    print("[SECTION] 目录结构检查:")
    for dir_name, description in essential_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"[OK] {description}: {dir_name}/")
        else:
            print(f"[WARN] {description}: 目录不存在")
    
    # 检查配置文件
    print()
    print("[SECTION] 配置文件检查:")
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("[OK] config.json: 格式正确")
        except json.JSONDecodeError as e:
            print(f"[ERROR] config.json: JSON格式错误 - {e}")
            all_ok = False
    else:
        print("[ERROR] config.json: 文件不存在")
        all_ok = False
    
    # 检查依赖文件
    print()
    print("[SECTION] 依赖文件检查:")
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
                print(f"[OK] 包含 {pkg}")
            else:
                print(f"[WARN] 缺少 {pkg}")
    else:
        print("[ERROR] requirements.txt: 文件不存在")
        all_ok = False
    
    # 检查Python依赖
    print()
    print("[SECTION] Python依赖检查:")
    dependencies = [
        ('jieba', '中文分词'),
        ('pypinyin', '拼音转换'),
        ('requests', 'HTTP请求'),
    ]
    
    deps_ok = True
    for package, description in dependencies:
        try:
            __import__(package)
            print(f"[OK] {description}: {package} 可用")
        except ImportError:
            print(f"[ERROR] {description}: {package} 未安装")
            deps_ok = False
    
    # 检查核心功能
    print()
    print("[SECTION] 核心功能检查:")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from chinese_tools_core import ChineseToolkit
        print("[OK] 核心模块: 可以导入")
        
        toolkit = ChineseToolkit()
        print("[OK] 工具包: 可以初始化")
        
        # 简单测试
        test_text = "测试文本"
        result = toolkit.segment(test_text)
        print(f"[OK] 分词功能: 正常 (测试: '{test_text}' -> {result})")
        
    except Exception as e:
        print(f"[ERROR] 核心功能测试失败: {e}")
        all_ok = False
    
    # 总结
    print()
    print("=" * 60)
    print("[SUMMARY] 检查结果总结:")
    print("=" * 60)
    
    if all_ok and deps_ok:
        print("[SUCCESS] 所有检查通过，可以发布！")
        print()
        print("[ACTION] 下一步:")
        print("1. 运行一键发布脚本:")
        print('   .\\one_click_release.ps1 -GitHubUsername "你的用户名"')
        print("2. 或按照 FINAL_RELEASE_GUIDE.md 手动发布")
    else:
        print("[ISSUE] 存在需要修复的问题")
        print()
        print("[ACTION] 需要修复:")
        if not all_ok:
            print("- 检查缺失的必需文件")
        if not deps_ok:
            print("- 安装缺失的Python依赖")
            print("  pip install -r requirements.txt")
    
    print()
    print("[INFO] 统计信息:")
    print(f"- 必需文件: {len(essential_files)}个")
    print(f"- 可选文件: {optional_count}/{len(optional_files)}个")
    print(f"- 目录结构: {len(essential_dirs)}个")
    print(f"- Python依赖: {'OK' if deps_ok else '需要安装'}")
    
    print()
    print("[INFO] 详细指南:")
    print("- 发布指南: FINAL_RELEASE_GUIDE.md")
    print("- 检查清单: PUBLISH_CHECKLIST.md")
    print("- 市场页面: SKILL_MARKET_PAGE.md")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()