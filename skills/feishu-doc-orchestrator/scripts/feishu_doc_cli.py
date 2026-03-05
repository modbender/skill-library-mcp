#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档创建CLI工具 - OpenClaw技能包装器
将Markdown文件转换为飞书文档
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
import tempfile
import shutil

def load_config():
    """加载飞书配置"""
    config_paths = [
        Path.home() / ".openclaw" / "feishu-config.env",
        Path.home() / ".claude" / "feishu-config.env",
        Path("feishu-config.env"),
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            print(f"[配置] 使用配置文件: {config_path}")
            return str(config_path)
    
    print("[错误] 未找到飞书配置文件")
    print("请创建 ~/.openclaw/feishu-config.env 包含以下内容:")
    print("FEISHU_APP_ID=cli_xxxxxxxxxxxxx")
    print("FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxx")
    print("FEISHU_API_DOMAIN=https://open.feishu.cn")
    return None

def run_orchestrator(markdown_file, title=None, doc_id=None, verbose=False):
    """运行主编排器"""
    # 获取技能根目录
    skill_root = Path(__file__).parent.parent
    original_skill = skill_root / "original-skill"
    
    # 如果原始技能存在，使用它
    if (original_skill / "feishu-doc-orchestrator" / "scripts" / "orchestrator.py").exists():
        orchestrator_script = original_skill / "feishu-doc-orchestrator" / "scripts" / "orchestrator.py"
    else:
        print("[错误] 原始技能文件未找到")
        print(f"请运行安装脚本: python {skill_root}/scripts/install_skill.py")
        return False
    
    # 构建命令
    cmd = [sys.executable, str(orchestrator_script), str(markdown_file)]
    
    if title:
        cmd.extend(["--title", title])
    if doc_id:
        cmd.extend(["--doc-id", doc_id])
    if verbose:
        cmd.append("--verbose")
    
    # 设置环境变量
    env = os.environ.copy()
    config_file = load_config()
    if config_file:
        # 设置配置路径环境变量
        env["FEISHU_CONFIG_PATH"] = config_file
        
        # 同时复制配置到技能目录（兼容性）
        try:
            import shutil
            skill_config = original_skill / "feishu-config.env"
            if Path(config_file).exists() and not skill_config.exists():
                shutil.copy2(config_file, skill_config)
                print(f"[配置] 复制配置文件到技能目录: {skill_config}")
        except:
            pass
    
    print(f"[执行] 命令: {' '.join(cmd)}")
    print(f"[环境] 配置路径: {config_file}")
    
    try:
        result = subprocess.run(
            cmd, 
            env=env, 
            capture_output=True, 
            text=True,
            timeout=300  # 5分钟超时
        )
        
        # 输出结果
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.stderr.strip():
            print("[错误输出]", result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print("[成功] 转换完成")
            return True
        else:
            print(f"[失败] 转换失败，退出码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[错误] 转换超时（5分钟），请检查网络或文档大小")
        return False
    except Exception as e:
        print(f"[异常] 执行过程中发生错误: {e}")
        return False

def simple_conversion(markdown_file, title=None, doc_id=None):
    """简化版转换（如果完整技能不可用）"""
    print("[警告] 使用简化版转换，功能有限")
    
    # 这里可以实现一个简化版本
    # 但现在先返回错误
    print("完整技能包未安装，请运行安装脚本")
    return False

def install_skill():
    """安装完整技能包"""
    skill_root = Path(__file__).parent.parent
    original_skill = skill_root / "original-skill"
    
    print(f"[安装] 正在安装完整技能包到 {original_skill}")
    
    # 检查是否已有git仓库
    if original_skill.exists():
        print(f"[信息] 技能包已存在于 {original_skill}")
        return True
    
    # 创建目录
    original_skill.mkdir(parents=True, exist_ok=True)
    
    # 尝试克隆仓库
    repo_url = "https://github.com/rosalynYANG/feishu-doc-creator-skill.git"
    print(f"[安装] 正在克隆仓库: {repo_url}")
    
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, str(original_skill)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[成功] 技能包安装完成")
            return True
        else:
            print("[错误] 克隆失败:", result.stderr)
            return False
    except Exception as e:
        print(f"[错误] 安装失败: {e}")
        print("请手动克隆仓库:")
        print(f"git clone {repo_url} {original_skill}")
        return False

def main():
    parser = argparse.ArgumentParser(description="飞书文档创建工具")
    parser.add_argument("--input", "-i", required=True, help="输入的Markdown文件")
    parser.add_argument("--title", "-t", help="文档标题（默认使用文件名）")
    parser.add_argument("--doc-id", "-d", help="现有文档ID（追加内容，不创建新文档）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--install", action="store_true", help="安装完整技能包")
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"[错误] 输入文件不存在: {input_file}")
        return 1
    
    # 安装模式
    if args.install:
        if install_skill():
            print("[成功] 安装完成，现在可以使用完整功能")
            return 0
        else:
            print("[错误] 安装失败")
            return 1
    
    # 设置默认标题
    if not args.title:
        args.title = input_file.stem
    
    # 运行转换
    print(f"[开始] 转换Markdown文件: {input_file}")
    print(f"[参数] 文档标题: {args.title}")
    if args.doc_id:
        print(f"[参数] 目标文档ID: {args.doc_id}")
    
    # 检查配置
    config_file = load_config()
    if not config_file:
        return 1
    
    # 运行转换
    success = run_orchestrator(
        input_file,
        title=args.title,
        doc_id=args.doc_id,
        verbose=args.verbose
    )
    
    if success:
        print("[完成] 文档转换成功")
        return 0
    else:
        print("[失败] 文档转换失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())