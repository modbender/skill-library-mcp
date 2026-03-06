#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装飞书文档创建技能包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_git():
    """检查git是否可用"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def clone_repo(dest_path):
    """克隆技能仓库"""
    repo_url = "https://github.com/rosalynYANG/feishu-doc-creator-skill.git"
    
    print(f"[安装] 正在克隆技能仓库: {repo_url}")
    print(f"[安装] 目标目录: {dest_path}")
    
    if dest_path.exists():
        print(f"[信息] 目录已存在，跳过克隆")
        return True
    
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, str(dest_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("[成功] 仓库克隆完成")
            return True
        else:
            print(f"[错误] 克隆失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("[错误] 克隆超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"[错误] 克隆异常: {e}")
        return False

def copy_from_workspace(dest_path):
    """从workspace复制技能包"""
    workspace_path = Path("/home/admin/openclaw/workspace/feishu-doc-creator-skill")
    
    if not workspace_path.exists():
        print(f"[错误] workspace中未找到技能包: {workspace_path}")
        return False
    
    print(f"[安装] 从workspace复制技能包: {workspace_path}")
    
    try:
        # 删除目标目录（如果存在）
        if dest_path.exists():
            shutil.rmtree(dest_path)
        
        # 复制整个目录
        shutil.copytree(workspace_path, dest_path)
        print("[成功] 技能包复制完成")
        return True
    except Exception as e:
        print(f"[错误] 复制失败: {e}")
        return False

def create_config_template():
    """创建配置文件模板"""
    config_path = Path.home() / ".openclaw" / "feishu-config.env"
    
    if config_path.exists():
        print(f"[信息] 配置文件已存在: {config_path}")
        return True
    
    # 创建目录
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建模板
    template = """# 飞书开放平台应用配置
# 从 https://open.feishu.cn/ 获取应用凭证

# 必需配置
FEISHU_APP_ID = "cli_xxxxxxxxxxxxx"
FEISHU_APP_SECRET = "xxxxxxxxxxxxxxxxxx"
FEISHU_API_DOMAIN = "https://open.feishu.cn"

# 可选配置
# FEISHU_AUTO_COLLABORATOR_ID = "ou_xxx"    # 自动添加协作者
# FEISHU_DEFAULT_FOLDER = "folder_token"    # 默认文件夹
"""
    
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(template)
        
        print(f"[成功] 配置文件模板已创建: {config_path}")
        print("[提示] 请编辑该文件，填入您的飞书应用凭证")
        return True
    except Exception as e:
        print(f"[错误] 创建配置文件失败: {e}")
        return False

def check_dependencies():
    """检查Python依赖"""
    dependencies = ["requests", "lark-oapi"]
    
    print("[检查] Python依赖包...")
    
    try:
        import importlib
        missing = []
        
        for dep in dependencies:
            try:
                importlib.import_module(dep.replace("-", "_"))
                print(f"  ✓ {dep}")
            except ImportError:
                print(f"  ✗ {dep} (未安装)")
                missing.append(dep)
        
        if missing:
            print(f"\n[警告] 缺少依赖包: {', '.join(missing)}")
            print("请使用以下命令安装:")
            print(f"pip install {' '.join(missing)}")
            return False
        else:
            print("[成功] 所有依赖包已安装")
            return True
    except Exception as e:
        print(f"[错误] 检查依赖时出错: {e}")
        return False

def main():
    print("=" * 70)
    print("飞书文档创建技能 - 安装程序")
    print("=" * 70)
    
    # 技能根目录
    skill_root = Path(__file__).parent.parent
    original_skill = skill_root / "original-skill"
    
    # 创建配置文件模板
    print("\n[步骤1] 创建配置文件模板...")
    create_config_template()
    
    # 检查依赖
    print("\n[步骤2] 检查Python依赖...")
    check_dependencies()
    
    # 选择安装方式
    print("\n[步骤3] 安装技能包...")
    print("请选择安装方式:")
    print("  1. 从GitHub克隆（需要网络连接）")
    print("  2. 从workspace复制（如果已下载）")
    print("  3. 跳过（手动安装）")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        if not check_git():
            print("[错误] git未安装，请先安装git")
            return 1
        success = clone_repo(original_skill)
    elif choice == "2":
        success = copy_from_workspace(original_skill)
    elif choice == "3":
        print("[信息] 跳过技能包安装，请手动安装")
        success = True
    else:
        print("[错误] 无效选择")
        return 1
    
    if not success:
        print("[错误] 技能包安装失败")
        return 1
    
    # 检查安装结果
    if original_skill.exists():
        print(f"\n[成功] 技能包已安装到: {original_skill}")
        
        # 检查关键文件
        orchestrator = original_skill / "feishu-doc-orchestrator" / "scripts" / "orchestrator.py"
        if orchestrator.exists():
            print(f"  ✓ 主编排器: {orchestrator}")
        else:
            print(f"  ✗ 主编排器未找到")
        
        parser = original_skill / "feishu-md-parser" / "scripts" / "md_parser.py"
        if parser.exists():
            print(f"  ✓ Markdown解析器: {parser}")
        
        print("\n[安装完成]")
        print("下一步:")
        print("1. 编辑 ~/.openclaw/feishu-config.env 填入飞书应用凭证")
        print("2. 运行检查脚本: python scripts/check_config.py")
        print("3. 测试转换: python scripts/feishu_doc_cli.py --input test.md --title \"测试文档\"")
    else:
        print("\n[警告] 技能包目录未创建，部分功能可能受限")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())