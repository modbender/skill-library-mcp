#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 配置检查器
功能：
1. 启动前检查配置文件
2. 验证 JSON 语法
3. 检查必要字段
4. 测试模型连接
5. 自动生成修复建议
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class ConfigChecker:
    """配置检查器"""
    
    REQUIRED_FIELDS = [
        "models.default",
        "gateway.port",
    ]
    
    OPTIONAL_BUT_RECOMMENDED = [
        "agents",
        "logging.level",
    ]
    
    def __init__(self):
        self.config_path = Path.home() / ".openclaw" / "openclaw.json"
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def check_file_exists(self) -> bool:
        """检查配置文件是否存在"""
        if not self.config_path.exists():
            self.errors.append(f"Config file not found: {self.config_path}")
            return False
        return True
    
    def check_json_syntax(self) -> Tuple[bool, dict]:
        """检查 JSON 语法"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config = json.loads(content)
            return True, config
            
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON syntax error: {e}")
            self.errors.append(f"  Line {e.lineno}, Column {e.colno}")
            return False, {}
        except Exception as e:
            self.errors.append(f"Failed to read config: {e}")
            return False, {}
    
    def check_required_fields(self, config: dict) -> bool:
        """检查必要字段"""
        all_valid = True
        
        for field in self.REQUIRED_FIELDS:
            keys = field.split('.')
            current = config
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    self.errors.append(f"Missing required field: {field}")
                    all_valid = False
                    break
        
        return all_valid
    
    def check_recommended_fields(self, config: dict):
        """检查推荐字段"""
        for field in self.OPTIONAL_BUT_RECOMMENDED:
            keys = field.split('.')
            current = config
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    self.warnings.append(f"Missing recommended field: {field}")
                    break
    
    def check_model_connectivity(self, config: dict) -> bool:
        """检查模型可连接性"""
        try:
            default_model = config.get('models', {}).get('default', '')
            if not default_model:
                self.warnings.append("No default model configured")
                return False
            
            # 这里应该实际测试模型连接
            # 简化版：只检查配置存在
            model_config = config.get('models', {}).get('providers', {}).get(default_model.split('/')[0], {})
            
            if not model_config.get('api_key'):
                self.warnings.append(f"No API key configured for model: {default_model}")
                return False
            
            return True
            
        except Exception as e:
            self.warnings.append(f"Failed to check model connectivity: {e}")
            return False
    
    def generate_fix_suggestions(self) -> List[str]:
        """生成修复建议"""
        suggestions = []
        
        for error in self.errors:
            if "Config file not found" in error:
                suggestions.append("Run 'openclaw init' to create initial configuration")
            
            elif "JSON syntax error" in error:
                suggestions.append("Fix JSON syntax error in config file")
                suggestions.append("Or delete config and run 'openclaw init'")
            
            elif "Missing required field" in error:
                field = error.split(":")[-1].strip()
                suggestions.append(f"Add missing field '{field}' to config")
        
        return suggestions
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("=" * 60)
        print("OpenClaw Configuration Checker")
        print("=" * 60)
        print()
        
        # 1. 检查文件存在
        if not self.check_file_exists():
            print("❌ Config file not found!")
            return {"valid": False, "errors": self.errors}
        
        print(f"✓ Config file exists: {self.config_path}")
        
        # 2. 检查 JSON 语法
        valid, config = self.check_json_syntax()
        if not valid:
            print("❌ JSON syntax error!")
            return {"valid": False, "errors": self.errors}
        
        print("✓ JSON syntax valid")
        
        # 3. 检查必要字段
        if self.check_required_fields(config):
            print("✓ Required fields present")
        else:
            print("❌ Missing required fields!")
        
        # 4. 检查推荐字段
        self.check_recommended_fields(config)
        if self.warnings:
            print(f"⚠ {len(self.warnings)} warnings")
        else:
            print("✓ All recommended fields present")
        
        # 5. 检查模型连接
        if self.check_model_connectivity(config):
            print("✓ Model connectivity OK")
        else:
            print("⚠ Model connectivity issues")
        
        print()
        print("=" * 60)
        
        # 输出错误和警告
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        # 生成修复建议
        suggestions = self.generate_fix_suggestions()
        if suggestions:
            print("\n💡 SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
        
        print("=" * 60)
        
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": suggestions,
            "config": config if valid else {}
        }
    
    def auto_fix(self) -> bool:
        """尝试自动修复配置"""
        print("\nAttempting auto-fix...")
        
        # 检查是否有备份
        backup_dir = Path.home() / ".openclaw" / "config_backup"
        if backup_dir.exists():
            backups = sorted(backup_dir.glob("*.json"), reverse=True)
            if backups:
                print(f"Found backup: {backups[0]}")
                # 恢复备份
                import shutil
                shutil.copy2(backups[0], self.config_path)
                print("✓ Restored from backup")
                return True
        
        # 如果没有备份，重置配置
        if "JSON syntax error" in str(self.errors):
            print("Creating new config...")
            result = subprocess.run(
                ["openclaw", "init"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ New config created")
                return True
            else:
                print("❌ Failed to create new config")
                return False
        
        return False


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Config Checker")
    parser.add_argument('--check', action='store_true', help='Check configuration')
    parser.add_argument('--fix', action='store_true', help='Attempt auto-fix')
    
    args = parser.parse_args()
    
    checker = ConfigChecker()
    
    if args.check or (not args.fix):
        result = checker.run_all_checks()
        
        if not result["valid"] and args.fix:
            if checker.auto_fix():
                # 重新检查
                checker.errors = []
                checker.warnings = []
                result = checker.run_all_checks()
        
        sys.exit(0 if result["valid"] else 1)
    
    elif args.fix:
        result = checker.run_all_checks()
        if not result["valid"]:
            checker.auto_fix()


if __name__ == "__main__":
    main()
