#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import platform
import re
from datetime import datetime

class OpenClawTroubleshooter:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_dir = os.path.abspath(os.path.join(self.script_dir, '..', '..', '..', '..'))
        self.workspace_dir = os.path.join(self.project_dir, 'workspace')
    
    def diagnose_system(self):
        """Diagnose system environment"""
        print("=== OpenClaw系统诊断 ===")
        results = {
            "timestamp": datetime.now().isoformat(),
            "os_info": self.get_os_info(),
            "python_info": self.get_python_info(),
            "openclaw_info": self.get_openclaw_info(),
            "dependencies": self.check_dependencies(),
            "permissions": self.check_permissions(),
            "workspace": self.check_workspace()
        }
        
        self.print_diagnosis(results)
        return results
    
    def get_os_info(self):
        """Get operating system information"""
        try:
            system = platform.system()
            version = platform.release()
            machine = platform.machine()
            
            if system == 'Darwin':
                mac_version = subprocess.check_output(['sw_vers', '-productVersion'], text=True).strip()
                return {
                    "system": system,
                    "version": mac_version,
                    "machine": machine,
                    "full_version": platform.version()
                }
            elif system == 'Linux':
                distro = subprocess.check_output(['lsb_release', '-d'], text=True).strip().split(':')[1].strip()
                return {
                    "system": system,
                    "version": version,
                    "distro": distro,
                    "machine": machine
                }
            elif system == 'Windows':
                return {
                    "system": system,
                    "version": version,
                    "machine": machine
                }
            else:
                return {
                    "system": system,
                    "version": version,
                    "machine": machine
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_python_info(self):
        """Get Python information"""
        try:
            version = platform.python_version()
            interpreter = sys.executable
            pip_version = subprocess.check_output([sys.executable, '-m', 'pip', '--version'], text=True).strip()
            
            return {
                "version": version,
                "interpreter": interpreter,
                "pip_version": pip_version,
                "version_info": list(sys.version_info)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_openclaw_info(self):
        """Get OpenClaw information"""
        try:
            openclaw_path = '/opt/homebrew/lib/node_modules/openclaw'
            if os.path.exists(openclaw_path):
                package_json = os.path.join(openclaw_path, 'package.json')
                with open(package_json, 'r', encoding='utf-8') as f:
                    pkg_info = json.load(f)
                
                return {
                    "version": pkg_info.get('version'),
                    "path": openclaw_path,
                    "installed": True
                }
            else:
                return {
                    "installed": False,
                    "path": "Not found"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def check_dependencies(self):
        """Check Python dependencies"""
        required_packages = ['requests', 'beautifulsoup4', 'lxml', 'json5', 'python-dotenv']
        installed_packages = []
        missing_packages = []
        
        try:
            pip_output = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], text=True)
            
            for package in required_packages:
                if re.search(rf'\b{re.escape(package)}\b', pip_output, re.IGNORECASE):
                    installed_packages.append(package)
                else:
                    missing_packages.append(package)
            
            return {
                "required": required_packages,
                "installed": installed_packages,
                "missing": missing_packages,
                "status": "ok" if not missing_packages else "warning"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_permissions(self):
        """Check permissions"""
        try:
            permissions = []
            
            # Check workspace permissions
            if os.path.exists(self.workspace_dir):
                workspace_stat = os.stat(self.workspace_dir)
                permissions.append({
                    "path": self.workspace_dir,
                    "readable": bool(workspace_stat.st_mode & 0o400),
                    "writable": bool(workspace_stat.st_mode & 0o200),
                    "executable": bool(workspace_stat.st_mode & 0o100)
                })
            
            # Check custom skills directory
            custom_skills_dir = os.path.join(self.workspace_dir, 'custom-skills')
            if os.path.exists(custom_skills_dir):
                skills_stat = os.stat(custom_skills_dir)
                permissions.append({
                    "path": custom_skills_dir,
                    "readable": bool(skills_stat.st_mode & 0o400),
                    "writable": bool(skills_stat.st_mode & 0o200),
                    "executable": bool(skills_stat.st_mode & 0o100)
                })
            
            return {
                "checks": permissions,
                "status": "ok" if all(check['readable'] and check['writable'] for check in permissions) else "warning"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_workspace(self):
        """Check workspace structure"""
        required_dirs = ['custom-skills', 'projects', 'memory']
        found_dirs = []
        missing_dirs = []
        
        try:
            for dir_name in required_dirs:
                dir_path = os.path.join(self.workspace_dir, dir_name)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    found_dirs.append(dir_name)
                else:
                    missing_dirs.append(dir_name)
            
            return {
                "required": required_dirs,
                "found": found_dirs,
                "missing": missing_dirs,
                "status": "ok" if not missing_dirs else "warning"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_dependencies(self):
        """Check Python dependencies"""
        required_packages = ['requests', 'beautifulsoup4', 'lxml', 'json5', 'python-dotenv']
        installed_packages = []
        missing_packages = []
        
        try:
            pip_output = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], text=True)
            
            for package in required_packages:
                if re.search(rf'\b{re.escape(package)}\b', pip_output, re.IGNORECASE):
                    installed_packages.append(package)
                else:
                    missing_packages.append(package)
            
            return {
                "required": required_packages,
                "installed": installed_packages,
                "missing": missing_packages,
                "status": "ok" if not missing_packages else "warning"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def print_diagnosis(self, results):
        """Print diagnosis results"""
        print(f"\n🔧 系统信息: {results['os_info']['system']} {results['os_info']['version']}")
        print(f"🐍 Python: {results['python_info']['version']}")
        print(f"📦 OpenClaw: {results['openclaw_info'].get('version', 'Not found')}")
        
        print("\n📦 依赖检查:")
        if 'dependencies' in results and 'status' in results['dependencies']:
            if results['dependencies']['status'] == 'ok':
                print(f"✅ 所有{len(results['dependencies']['required'])}个依赖项已安装")
            else:
                print(f"⚠️ 缺少依赖项: {', '.join(results['dependencies']['missing'])}")
        
        print("\n📂 工作区检查:")
        if 'workspace' in results and 'status' in results['workspace']:
            if results['workspace']['status'] == 'ok':
                print("✅ 工作区结构完整")
            else:
                print(f"⚠️ 缺少目录: {', '.join(results['workspace']['missing'])}")
        
        print("\n🔐 权限检查:")
        if 'permissions' in results and 'status' in results['permissions']:
            if results['permissions']['status'] == 'ok':
                print("✅ 权限配置正常")
            else:
                print("⚠️ 权限配置存在问题")
    
    def fix_issue(self, issue_type):
        """Fix common issues"""
        print(f"=== 修复问题: {issue_type} ===")
        
        if issue_type == "dependencies":
            return self.fix_dependencies()
        elif issue_type == "permissions":
            return self.fix_permissions()
        elif issue_type == "workspace":
            return self.fix_workspace()
        elif issue_type == "all":
            return self.fix_all()
        else:
            print(f"❌ 不支持的修复类型: {issue_type}")
            return False
    
    def fix_dependencies(self):
        """Fix missing dependencies"""
        try:
            missing_packages = self.check_dependencies()['missing']
            if not missing_packages:
                print("✅ 所有依赖项已安装")
                return True
            
            print(f"📦 安装缺少的依赖项: {', '.join(missing_packages)}")
            
            # Try to install with --break-system-packages flag
            try:
                for package in missing_packages:
                    subprocess.check_output([sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'])
                
                print("✅ 依赖项安装完成")
                return True
            
            except Exception as e1:
                print(f"❌ 安装失败: {e1}")
                print("🔄 尝试使用用户模式安装")
                
                # Try to install with --user flag
                try:
                    for package in missing_packages:
                        subprocess.check_output([sys.executable, '-m', 'pip', 'install', package, '--user'])
                    
                    print("✅ 依赖项安装完成")
                    return True
                except Exception as e2:
                    print(f"❌ 用户模式安装失败: {e2}")
                    return False
            
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False
    
    def fix_permissions(self):
        """Fix permissions issues"""
        try:
            # Fix workspace permissions
            if os.path.exists(self.workspace_dir):
                subprocess.check_output(['chmod', '-R', '755', self.workspace_dir])
            
            # Fix custom skills directory permissions
            custom_skills_dir = os.path.join(self.workspace_dir, 'custom-skills')
            if os.path.exists(custom_skills_dir):
                subprocess.check_output(['chmod', '-R', '755', custom_skills_dir])
            
            print("✅ 权限修复完成")
            return True
        except Exception as e:
            print(f"❌ 权限修复失败: {e}")
            return False
    
    def fix_workspace(self):
        """Fix workspace structure"""
        try:
            required_dirs = ['custom-skills', 'projects', 'memory']
            for dir_name in required_dirs:
                dir_path = os.path.join(self.workspace_dir, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"📂 创建目录: {dir_path}")
            
            print("✅ 工作区结构修复完成")
            return True
        except Exception as e:
            print(f"❌ 工作区修复失败: {e}")
            return False
    
    def fix_all(self):
        """Fix all common issues"""
        print("=== 全面修复 ===")
        results = []
        
        results.append(("依赖项", self.fix_dependencies()))
        results.append(("权限", self.fix_permissions()))
        results.append(("工作区", self.fix_workspace()))
        
        print("\n=== 修复结果 ===")
        all_success = True
        for issue, success in results:
            if success:
                print(f"✅ {issue}修复成功")
            else:
                print(f"❌ {issue}修复失败")
                all_success = False
        
        return all_success

def main():
    if __name__ == "__main__":
        import argparse
        
        parser = argparse.ArgumentParser(
            description="OpenClaw常见问题解决方案",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument("command", choices=["diagnose", "fix"], 
                          help="命令: diagnose（诊断）或 fix（修复）")
        
        parser.add_argument("target", nargs="?", default="system",
                          help="诊断/修复目标: system（系统）或 specific issue（特定问题）")
        
        args = parser.parse_args()
        
        troubleshooter = OpenClawTroubleshooter()
        
        if args.command == "diagnose":
            if args.target == "system":
                troubleshooter.diagnose_system()
            else:
                print(f"❌ 不支持的诊断目标: {args.target}")
        elif args.command == "fix":
            success = troubleshooter.fix_issue(args.target)
            if success:
                print("✅ 修复完成")
            else:
                print("❌ 修复失败")
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
