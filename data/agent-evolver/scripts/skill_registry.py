#!/usr/bin/env python3
"""
Skill Registry - 技能注册中心
让主 Agent 发现和使用技能
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SkillInfo:
    """技能信息"""
    name: str
    description: str
    triggers: Dict[str, Any]
    usage_prompt: str
    scripts: Dict[str, str]
    installed_at: str
    last_used: str


class SkillRegistry:
    """技能注册中心"""
    
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or os.path.expanduser("~/.evolver/skills_registry.json")
        self.skills: Dict[str, SkillInfo] = {}
        self.triggers: Dict[str, Dict] = {}
        self._load_registry()
    
    def _load_registry(self):
        """加载注册表"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for name, info in data.get("skills", {}).items():
                        self.skills[name] = SkillInfo(**info)
                        if info.get("triggers"):
                            self.triggers[name] = info["triggers"]
            except Exception as e:
                print(f"Failed to load registry: {e}")
    
    def _save_registry(self):
        """保存注册表"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        
        data = {
            "skills": {
                name: {
                    "name": skill.name,
                    "description": skill.description,
                    "triggers": skill.triggers,
                    "usage_prompt": skill.usage_prompt,
                    "scripts": skill.scripts,
                    "installed_at": skill.installed_at,
                    "last_used": skill.last_used
                }
                for name, skill in self.skills.items()
            },
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_skill(self, skill_path: str) -> bool:
        """注册新技能"""
        skill_md = Path(skill_path) / "SKILL.md"
        
        if not skill_md.exists():
            print(f"SKILL.md not found in {skill_path}")
            return False
        
        try:
            with open(skill_md, 'r') as f:
                content = f.read()
            
            frontmatter = self._parse_frontmatter(content)
            
            if not frontmatter:
                print("Failed to parse SKILL.md frontmatter")
                return False
            
            name = frontmatter.get("name", Path(skill_path).name)
            description = frontmatter.get("description", "")
            triggers = frontmatter.get("triggers", {})
            
            usage_prompt = self._extract_usage_prompt(content)
            
            scripts = self._find_scripts(skill_path)
            
            skill = SkillInfo(
                name=name,
                description=description,
                triggers=triggers,
                usage_prompt=usage_prompt,
                scripts=scripts,
                installed_at=datetime.now().isoformat(),
                last_used=""
            )
            
            self.skills[name] = skill
            
            if triggers:
                self.triggers[name] = triggers
            
            self._save_registry()
            
            print(f"✅ 技能 '{name}' 注册成功")
            return True
            
        except Exception as e:
            print(f"Failed to register skill: {e}")
            return False
    
    def _parse_frontmatter(self, content: str) -> Optional[Dict]:
        """解析 YAML frontmatter"""
        if not content.startswith("---"):
            return None
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        
        try:
            return yaml.safe_load(parts[1])
        except:
            return None
    
    def _extract_usage_prompt(self, content: str) -> str:
        """提取使用提示词"""
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
        return content
    
    def _find_scripts(self, skill_path: str) -> Dict[str, str]:
        """查找技能脚本"""
        scripts_dir = Path(skill_path) / "scripts"
        scripts = {}
        
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                scripts[script.stem] = str(script)
        
        return scripts
    
    def unregister_skill(self, name: str) -> bool:
        """注销技能"""
        if name in self.skills:
            del self.skills[name]
            if name in self.triggers:
                del self.triggers[name]
            self._save_registry()
            print(f"✅ 技能 '{name}' 已注销")
            return True
        return False
    
    def get_skill(self, name: str) -> Optional[SkillInfo]:
        """获取技能信息"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[SkillInfo]:
        """列出所有技能"""
        return list(self.skills.values())
    
    def get_skill_for_task(self, task_description: str) -> List[str]:
        """根据任务描述推荐技能"""
        recommended = []
        task_lower = task_description.lower()
        
        for skill_name, triggers in self.triggers.items():
            if self._match_triggers(task_lower, triggers):
                recommended.append(skill_name)
        
        return recommended
    
    def _match_triggers(self, task_description: str, triggers: Dict) -> bool:
        """检查是否匹配触发条件"""
        keywords = triggers.get("keywords", [])
        
        for keyword in keywords:
            if keyword.lower() in task_description:
                return True
        
        return False
    
    def get_skill_usage_prompt(self, skill_name: str) -> str:
        """获取技能使用提示词"""
        skill = self.skills.get(skill_name)
        if skill:
            skill.last_used = datetime.now().isoformat()
            self._save_registry()
            return skill.usage_prompt
        return ""
    
    def generate_main_agent_prompt(self) -> str:
        """生成主 Agent 可用技能提示词"""
        if not self.skills:
            return "当前没有安装任何技能。"
        
        prompt = "## 可用技能\n\n"
        
        for skill in self.skills.values():
            prompt += f"### {skill.name}\n"
            prompt += f"**描述**: {skill.description}\n\n"
            
            if skill.triggers.get("keywords"):
                prompt += f"**触发关键词**: {', '.join(skill.triggers['keywords'])}\n\n"
            
            if skill.scripts:
                prompt += "**可用脚本**:\n"
                for script_name, script_path in skill.scripts.items():
                    prompt += f"- `python3 {script_path}`\n"
                prompt += "\n"
            
            prompt += "---\n\n"
        
        return prompt


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Registry CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    register_parser = subparsers.add_parser("register", help="注册技能")
    register_parser.add_argument("path", help="技能目录路径")
    
    unregister_parser = subparsers.add_parser("unregister", help="注销技能")
    unregister_parser.add_argument("name", help="技能名称")
    
    list_parser = subparsers.add_parser("list", help="列出所有技能")
    list_parser.add_argument("--new", action="store_true", help="仅显示新技能")
    
    recommend_parser = subparsers.add_parser("recommend", help="推荐技能")
    recommend_parser.add_argument("task", help="任务描述")
    
    prompt_parser = subparsers.add_parser("prompt", help="生成主 Agent 提示词")
    
    args = parser.parse_args()
    
    registry = SkillRegistry()
    
    if args.command == "register":
        registry.register_skill(args.path)
    elif args.command == "unregister":
        registry.unregister_skill(args.name)
    elif args.command == "list":
        skills = registry.list_skills()
        for skill in skills:
            print(f"- {skill.name}: {skill.description[:50]}...")
    elif args.command == "recommend":
        recommended = registry.get_skill_for_task(args.task)
        if recommended:
            print("推荐技能:")
            for name in recommended:
                print(f"- {name}")
        else:
            print("没有找到匹配的技能")
    elif args.command == "prompt":
        print(registry.generate_main_agent_prompt())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
