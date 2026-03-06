#!/usr/bin/env python3
"""
OpenClaw Skill Loader
从 clawhub.ai 下载的 zip 文件安装 OpenClaw skill

用法:
    python openclaw_skill_loader.py [filename].zip
    python openclaw_skill_loader.py --list
"""

import os
import sys
import zipfile
import shutil
import subprocess
import json
import argparse
from pathlib import Path
from typing import Optional, Tuple


class OpenClawSkillLoader:
    def __init__(self):
        self.openclaw_path = None
        self.skills_dir = None
        self.user_config_dir = os.path.expanduser("~/.openclaw")
        
    def find_openclaw_installation(self) -> Optional[str]:
        """查找 OpenClaw 安装位置"""
        print("🔍 正在搜索 OpenClaw 安装位置...")
        
        # 方法1: 通过 which 命令
        try:
            result = subprocess.run(
                ["which", "openclaw"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                openclaw_bin = result.stdout.strip()
                # 获取实际的安装目录
                openclaw_path = os.path.realpath(openclaw_bin)
                # 从 bin 目录向上查找 node_modules/openclaw
                path_parts = Path(openclaw_path).parts
                openclaw_root = None
                for i, part in enumerate(path_parts):
                    if part == "node_modules" and i + 1 < len(path_parts):
                        openclaw_root = os.path.join(*path_parts[:i+2])
                        break
                if openclaw_root:
                    print(f"✅ 找到 OpenClaw: {openclaw_root}")
                    return openclaw_root
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # 方法2: 检查常见的 nvm 安装路径
        nvm_patterns = [
            os.path.expanduser("~/.nvm/versions/node/*/lib/node_modules/openclaw"),
            "/usr/local/lib/node_modules/openclaw",
            "/opt/node_modules/openclaw",
        ]
        
        for pattern in nvm_patterns:
            matches = sorted(Path(pattern).parent.glob("*"), reverse=True)
            for match in matches:
                openclaw_path = match / "openclaw"
                if openclaw_path.exists():
                    print(f"✅ 找到 OpenClaw: {openclaw_path}")
                    return str(openclaw_path)
        
        print("❌ 未找到 OpenClaw 安装位置")
        return None
    
    def find_skills_directory(self, openclaw_root: str) -> Optional[str]:
        """查找 skills 目录"""
        print("🔍 正在搜索 skills 目录...")
        
        # 检查 OpenClaw 安装目录下的 skills
        skills_dir = os.path.join(openclaw_root, "skills")
        if os.path.exists(skills_dir):
            print(f"✅ 找到 skills 目录: {skills_dir}")
            return skills_dir
        
        print("❌ 未找到 skills 目录")
        return None
    
    def validate_skill_structure(self, skill_path: str) -> Tuple[bool, str]:
        """验证 skill 目录结构"""
        print(f"🔍 正在验证 skill 结构: {skill_path}")
        
        # 检查是否存在 SKILL.md
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_md):
            return False, "缺少 SKILL.md 文件"
        
        # 检查 SKILL.md 格式
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.startswith('---'):
                    return False, "SKILL.md 格式错误: 必须以 --- 开头"
        except Exception as e:
            return False, f"无法读取 SKILL.md: {e}"
        
        return True, "skill 结构有效"
    
    def extract_zip(self, zip_path: str, extract_to: str) -> Tuple[bool, str]:
        """解压 zip 文件"""
        print(f"📦 正在解压: {zip_path}")
        
        if not os.path.exists(zip_path):
            return False, f"文件不存在: {zip_path}"
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"✅ 解压成功到: {extract_to}")
            return True, "解压成功"
        except zipfile.BadZipFile:
            return False, "无效的 zip 文件"
        except Exception as e:
            return False, f"解压失败: {e}"
    
    def install_skill(self, zip_path: str) -> Tuple[bool, str]:
        """安装 skill"""
        print(f"\n{'='*60}")
        print(f"🚀 开始安装 skill: {zip_path}")
        print(f"{'='*60}\n")
        
        # 1. 查找 OpenClaw 安装位置
        self.openclaw_path = self.find_openclaw_installation()
        if not self.openclaw_path:
            return False, "未找到 OpenClaw 安装位置"
        
        # 2. 查找 skills 目录
        self.skills_dir = self.find_skills_directory(self.openclaw_path)
        if not self.skills_dir:
            return False, "未找到 skills 目录"
        
        # 3. 创建临时解压目录
        temp_dir = os.path.join("/tmp", "openclaw_skill_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # 4. 解压 zip 文件
            success, message = self.extract_zip(zip_path, temp_dir)
            if not success:
                return False, message
            
            # 5. 查找解压后的 skill 目录
            # 检查是否有根目录
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                skill_source = os.path.join(temp_dir, extracted_items[0])
            else:
                skill_source = temp_dir
            
            # 6. 验证 skill 结构
            success, message = self.validate_skill_structure(skill_source)
            if not success:
                return False, message
            
            # 7. 获取 skill 名称
            skill_name = os.path.basename(skill_source)
            if skill_name == "openclaw_skill_temp":
                # 尝试从 SKILL.md 读取名称
                skill_md = os.path.join(skill_source, "SKILL.md")
                if os.path.exists(skill_md):
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('name:'):
                                skill_name = line.split(':', 1)[1].strip()
                                break
                if skill_name == "openclaw_skill_temp":
                    skill_name = os.path.splitext(os.path.basename(zip_path))[0]
            
            # 8. 目标目录
            target_dir = os.path.join(self.skills_dir, skill_name)
            
            # 9. 如果已存在，询问是否覆盖
            if os.path.exists(target_dir):
                print(f"⚠️  Skill 已存在: {skill_name}")
                print(f"📁 目标目录: {target_dir}")
                response = input("是否覆盖? (y/N): ").strip().lower()
                if response != 'y':
                    return False, "用户取消安装"
                shutil.rmtree(target_dir)
            
            # 10. 复制 skill 到目标目录
            print(f"📋 正在安装到: {target_dir}")
            shutil.copytree(skill_source, target_dir)
            print(f"✅ Skill 安装成功: {skill_name}")
            
            # 11. 更新 Gateway
            print(f"\n🔄 正在更新 Gateway...")
            try:
                subprocess.run(
                    ["openclaw", "daemon", "restart"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                print("✅ Gateway 更新成功")
            except subprocess.TimeoutExpired:
                print("⚠️  Gateway 重启超时，请手动执行: openclaw daemon restart")
            except Exception as e:
                print(f"⚠️  Gateway 更新失败: {e}")
                print(f"💡 请手动执行: openclaw daemon restart")
            
            print(f"\n{'='*60}")
            print(f"✨ Skill 安装完成!")
            print(f"{'='*60}")
            print(f"📦 Skill 名称: {skill_name}")
            print(f"📁 安装位置: {target_dir}")
            print(f"💡 现在可以在 OpenClaw skill 界面中使用了")
            print(f"{'='*60}\n")
            
            return True, "安装成功"
            
        except Exception as e:
            return False, f"安装失败: {e}"
        finally:
            # 清理临时目录
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def list_installed_skills(self):
        """列出已安装的 skills"""
        print(f"\n{'='*60}")
        print(f"📋 已安装的 Skills")
        print(f"{'='*60}\n")
        
        # 查找 skills 目录
        self.openclaw_path = self.find_openclaw_installation()
        if not self.openclaw_path:
            return
        
        self.skills_dir = self.find_skills_directory(self.openclaw_path)
        if not self.skills_dir:
            return
        
        # 列出所有 skills
        skills = []
        for item in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, item)
            if os.path.isdir(skill_path):
                skill_md = os.path.join(skill_path, "SKILL.md")
                if os.path.exists(skill_md):
                    # 读取 skill 名称和描述
                    name = item
                    description = "无描述"
                    try:
                        with open(skill_md, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 解析 YAML frontmatter
                            if content.startswith('---'):
                                parts = content.split('---', 2)
                                if len(parts) >= 2:
                                    yaml_content = parts[1]
                                    for line in yaml_content.split('\n'):
                                        if line.startswith('name:'):
                                            name = line.split(':', 1)[1].strip()
                                        elif line.startswith('description:'):
                                            description = line.split(':', 1)[1].strip()
                                            break
                    except Exception:
                        pass
                    
                    skills.append({
                        'name': name,
                        'folder': item,
                        'description': description,
                        'path': skill_path
                    })
        
        if not skills:
            print("❌ 未找到已安装的 skills")
            return
        
        # 打印 skills 列表
        for i, skill in enumerate(skills, 1):
            print(f"{i}. {skill['name']}")
            print(f"   📁 文件夹: {skill['folder']}")
            print(f"   📝 描述: {skill['description']}")
            print(f"   📍 路径: {skill['path']}")
            print()
        
        print(f"{'='*60}")
        print(f"总计: {len(skills)} 个 skills")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw Skill Loader - 从 zip 文件安装 OpenClaw skill',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python openclaw_skill_loader.py my-skill.zip
  python openclaw_skill_loader.py --list
        """
    )
    
    parser.add_argument(
        'zip_file',
        nargs='?',
        help='要安装的 skill zip 文件路径'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出已安装的 skills'
    )
    
    args = parser.parse_args()
    
    loader = OpenClawSkillLoader()
    
    if args.list:
        loader.list_installed_skills()
    elif args.zip_file:
        # 检查文件路径
        zip_path = args.zip_file
        if not os.path.isabs(zip_path):
            zip_path = os.path.join(os.getcwd(), zip_path)
        
        # 安装 skill
        success, message = loader.install_skill(zip_path)
        
        if not success:
            print(f"\n❌ 错误: {message}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
