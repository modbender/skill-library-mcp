#!/usr/bin/env python3
"""
Claw Problem Diagnoser - OpenClaw问题诊断器
自动诊断和修复常见的OpenClaw技术问题
"""

import os
import sys
import json
import yaml
import subprocess
import shutil
import platform
import socket
import requests
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import warnings

# 可选依赖
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 禁用一些警告
warnings.filterwarnings('ignore')

class IssueSeverity(Enum):
    """问题严重性等级"""
    CRITICAL = "critical"      # 严重问题
    HIGH = "high"              # 高问题  
    MEDIUM = "medium"          # 中等问题
    LOW = "low"                # 低问题
    INFO = "info"              # 信息性

class DiagnosticCategory(Enum):
    """诊断类别"""
    CONFIGURATION = "configuration"       # 配置问题
    DEPENDENCIES = "dependencies"         # 依赖问题
    SERVICE = "service"                   # 服务问题
    PERMISSIONS = "permissions"           # 权限问题
    PERFORMANCE = "performance"           # 性能问题
    NETWORK = "network"                   # 网络问题
    SECURITY = "security"                 # 安全问题
    STORAGE = "storage"                   # 存储问题

@dataclass
class DiagnosticIssue:
    """诊断问题"""
    id: str                           # 唯一标识
    category: DiagnosticCategory      # 问题类别
    severity: IssueSeverity           # 严重性等级
    title: str                        # 问题标题
    description: str                  # 详细描述
    cause: str                        # 原因分析
    recommendation: str               # 修复建议
    location: str                     # 问题位置（文件、服务等）
    
    # 可选字段
    auto_fixable: bool = False        # 是否可自动修复
    fix_script: Optional[str] = None  # 修复脚本（如有）
    reference: Optional[str] = None   # 参考链接
    detected_at: float = field(default_factory=time.time)  # 检测时间

@dataclass
class DiagnosticResult:
    """诊断结果"""
    system_info: Dict[str, Any]       # 系统信息
    openclaw_info: Dict[str, Any]     # OpenClaw信息
    issues: List[DiagnosticIssue] = field(default_factory=list)  # 所有问题
    checks_performed: int = 0         # 执行的检查数量
    diagnosis_duration: float = 0.0   # 诊断耗时（秒）
    
    # 统计信息
    def statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        stats = {
            "total_issues": len(self.issues),
            "by_severity": {level.value: 0 for level in IssueSeverity},
            "by_category": {cat.value: 0 for cat in DiagnosticCategory},
            "auto_fixable": sum(1 for i in self.issues if i.auto_fixable)
        }
        
        for issue in self.issues:
            stats["by_severity"][issue.severity.value] += 1
            stats["by_category"][issue.category.value] += 1
        
        return stats
    
    def has_critical_or_high(self) -> bool:
        """是否有严重或高问题"""
        for issue in self.issues:
            if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['issues'] = [asdict(i) for i in self.issues]
        result['statistics'] = self.statistics()
        result['has_critical_or_high'] = self.has_critical_or_high()
        return result
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

class BaseDiagnosticCheck:
    """诊断检查基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        
    def check(self) -> List[DiagnosticIssue]:
        """执行检查，返回问题列表"""
        raise NotImplementedError("子类必须实现check方法")
    
    def fix(self, issue: DiagnosticIssue) -> bool:
        """修复问题，返回是否成功"""
        raise NotImplementedError("子类可以实现fix方法")

class ConfigurationCheck(BaseDiagnosticCheck):
    """配置检查"""
    
    def __init__(self):
        super().__init__("configuration_check", "检查OpenClaw配置文件")
    
    def check(self) -> List[DiagnosticIssue]:
        issues = []
        
        # 检查配置文件路径
        config_paths = [
            "~/.openclaw/config.json",
            "~/.openclaw/config.yaml",
            "~/.openclaw/config.yml",
            "/etc/openclaw/config.json",
        ]
        
        config_found = False
        for path_template in config_paths:
            path = os.path.expanduser(path_template)
            if os.path.exists(path):
                config_found = True
                # 检查配置文件可读性
                try:
                    with open(path, 'r') as f:
                        if path.endswith('.json'):
                            json.load(f)
                        elif path.endswith('.yaml') or path.endswith('.yml'):
                            yaml.safe_load(f)
                    logger.info(f"配置文件验证通过: {path}")
                except json.JSONDecodeError as e:
                    issue = DiagnosticIssue(
                        id=f"config_json_error_{hash(path)}",
                        category=DiagnosticCategory.CONFIGURATION,
                        severity=IssueSeverity.CRITICAL,
                        title="配置文件JSON语法错误",
                        description=f"配置文件 {path} 包含JSON语法错误",
                        cause=f"JSON解析错误: {e}",
                        recommendation="修复JSON语法错误或使用有效的配置文件",
                        location=path,
                        auto_fixable=False
                    )
                    issues.append(issue)
                except yaml.YAMLError as e:
                    issue = DiagnosticIssue(
                        id=f"config_yaml_error_{hash(path)}",
                        category=DiagnosticCategory.CONFIGURATION,
                        severity=IssueSeverity.CRITICAL,
                        title="配置文件YAML语法错误",
                        description=f"配置文件 {path} 包含YAML语法错误",
                        cause=f"YAML解析错误: {e}",
                        recommendation="修复YAML语法错误或使用有效的配置文件",
                        location=path,
                        auto_fixable=False
                    )
                    issues.append(issue)
                except Exception as e:
                    issue = DiagnosticIssue(
                        id=f"config_read_error_{hash(path)}",
                        category=DiagnosticCategory.CONFIGURATION,
                        severity=IssueSeverity.HIGH,
                        title="配置文件读取失败",
                        description=f"无法读取配置文件 {path}",
                        cause=f"读取错误: {e}",
                        recommendation="检查文件权限或修复文件损坏",
                        location=path,
                        auto_fixable=False
                    )
                    issues.append(issue)
        
        if not config_found:
            issue = DiagnosticIssue(
                id="config_not_found",
                category=DiagnosticCategory.CONFIGURATION,
                severity=IssueSeverity.HIGH,
                title="未找到配置文件",
                description="未找到任何OpenClaw配置文件",
                cause="OpenClaw未正确安装或配置文件丢失",
                recommendation="创建配置文件或重新安装OpenClaw",
                location="~/.openclaw/",
                auto_fixable=True,
                fix_script="openclaw init"
            )
            issues.append(issue)
        
        return issues
    
    def fix(self, issue: DiagnosticIssue) -> bool:
        if issue.id == "config_not_found":
            try:
                # 尝试运行openclaw init
                result = subprocess.run(["openclaw", "init"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("成功初始化OpenClaw配置")
                    return True
                else:
                    logger.error(f"初始化失败: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"执行修复失败: {e}")
                return False
        return False

class DependenciesCheck(BaseDiagnosticCheck):
    """依赖检查"""
    
    def __init__(self):
        super().__init__("dependencies_check", "检查Python依赖包")
    
    def check(self) -> List[DiagnosticIssue]:
        issues = []
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            issue = DiagnosticIssue(
                id="python_version_too_low",
                category=DiagnosticCategory.DEPENDENCIES,
                severity=IssueSeverity.CRITICAL,
                title="Python版本过低",
                description=f"当前Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}",
                cause="OpenClaw需要Python 3.8或更高版本",
                recommendation="升级Python到3.8或更高版本",
                location="系统环境",
                auto_fixable=False
            )
            issues.append(issue)
        
        # 检查关键依赖包
        critical_packages = [
            ("openclaw", "OpenClaw核心包"),
            ("requests", "HTTP请求库"),
            ("psutil", "系统监控库"),
            ("pyyaml", "YAML解析库"),
        ]
        
        for package, description in critical_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                issue = DiagnosticIssue(
                    id=f"missing_package_{package}",
                    category=DiagnosticCategory.DEPENDENCIES,
                    severity=IssueSeverity.HIGH if package == "openclaw" else IssueSeverity.MEDIUM,
                    title=f"缺失关键依赖: {package}",
                    description=f"未找到{description}: {package}",
                    cause="依赖包未安装或安装失败",
                    recommendation=f"使用pip安装: pip install {package}",
                    location="Python环境",
                    auto_fixable=True,
                    fix_script=f"pip install {package}"
                )
                issues.append(issue)
        
        return issues
    
    def fix(self, issue: DiagnosticIssue) -> bool:
        if issue.fix_script:
            try:
                result = subprocess.run(issue.fix_script.split(), 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"成功安装依赖: {issue.title}")
                    return True
                else:
                    logger.error(f"安装失败: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"执行修复失败: {e}")
                return False
        return False

class ServiceCheck(BaseDiagnosticCheck):
    """服务检查"""
    
    def __init__(self):
        super().__init__("service_check", "检查OpenClaw服务状态")
    
    def check(self) -> List[DiagnosticIssue]:
        issues = []
        
        # 检查OpenClaw进程
        openclaw_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('openclaw' in part.lower() for part in cmdline):
                    openclaw_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not openclaw_processes:
            issue = DiagnosticIssue(
                id="openclaw_not_running",
                category=DiagnosticCategory.SERVICE,
                severity=IssueSeverity.CRITICAL,
                title="OpenClaw服务未运行",
                description="未找到运行的OpenClaw进程",
                cause="服务可能未启动或已崩溃",
                recommendation="启动OpenClaw服务: openclaw start",
                location="系统进程",
                auto_fixable=True,
                fix_script="openclaw start"
            )
            issues.append(issue)
        else:
            # 检查服务健康状态
            try:
                # 尝试连接本地API
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code != 200:
                    issue = DiagnosticIssue(
                        id="openclaw_health_check_failed",
                        category=DiagnosticCategory.SERVICE,
                        severity=IssueSeverity.HIGH,
                        title="OpenClaw健康检查失败",
                        description=f"健康检查返回状态码: {response.status_code}",
                        cause="服务可能未正确响应",
                        recommendation="检查服务日志并重启",
                        location="localhost:8080",
                        auto_fixable=False
                    )
                    issues.append(issue)
            except requests.ConnectionError:
                issue = DiagnosticIssue(
                    id="openclaw_api_unreachable",
                    category=DiagnosticCategory.SERVICE,
                    severity=IssueSeverity.HIGH,
                    title="OpenClaw API不可达",
                    description="无法连接到OpenClaw API端点",
                    cause="服务可能未监听端口或网络问题",
                    recommendation="检查服务配置和端口监听",
                    location="localhost:8080",
                    auto_fixable=False
                )
                issues.append(issue)
            except Exception as e:
                logger.warning(f"健康检查异常: {e}")
        
        # 检查端口占用
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8080))
            sock.close()
            
            if result != 0:  # 端口未监听
                issue = DiagnosticIssue(
                    id="port_not_listening",
                    category=DiagnosticCategory.SERVICE,
                    severity=IssueSeverity.HIGH,
                    title="OpenClaw端口未监听",
                    description="端口8080未在监听",
                    cause="服务可能未启动或配置了不同端口",
                    recommendation="启动服务或检查端口配置",
                    location="localhost:8080",
                    auto_fixable=False
                )
                issues.append(issue)
        except Exception as e:
            logger.warning(f"端口检查异常: {e}")
        
        return issues
    
    def fix(self, issue: DiagnosticIssue) -> bool:
        if issue.id == "openclaw_not_running" and issue.fix_script:
            try:
                result = subprocess.run(issue.fix_script.split(), 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("成功启动OpenClaw服务")
                    return True
                else:
                    logger.error(f"启动失败: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"执行修复失败: {e}")
                return False
        return False

class PermissionsCheck(BaseDiagnosticCheck):
    """权限检查"""
    
    def __init__(self):
        super().__init__("permissions_check", "检查文件和目录权限")
    
    def check(self) -> List[DiagnosticIssue]:
        issues = []
        
        # 检查关键目录权限
        critical_paths = [
            "~/.openclaw",
            "~/.openclaw/config.json",
            "~/.openclaw/workspace",
            "~/.openclaw/logs",
        ]
        
        for path_template in critical_paths:
            path = os.path.expanduser(path_template)
            if os.path.exists(path):
                # 检查可读性
                if os.path.isfile(path):
                    if not os.access(path, os.R_OK):
                        issue = DiagnosticIssue(
                            id=f"file_not_readable_{hash(path)}",
                            category=DiagnosticCategory.PERMISSIONS,
                            severity=IssueSeverity.HIGH,
                            title=f"文件不可读: {os.path.basename(path)}",
                            description=f"无法读取文件: {path}",
                            cause="文件权限设置不正确",
                            recommendation=f"修改文件权限: chmod +r {path}",
                            location=path,
                            auto_fixable=True,
                            fix_script=f"chmod +r {path}"
                        )
                        issues.append(issue)
                    
                    if os.access(path, os.W_OK) and path.endswith('.json'):
                        # 配置文件可写可能不安全
                        issue = DiagnosticIssue(
                            id=f"config_writable_{hash(path)}",
                            category=DiagnosticCategory.SECURITY,
                            severity=IssueSeverity.MEDIUM,
                            title=f"配置文件可写: {os.path.basename(path)}",
                            description=f"配置文件可写可能带来安全风险: {path}",
                            cause="文件权限过于宽松",
                            recommendation=f"限制文件写权限: chmod 400 {path}",
                            location=path,
                            auto_fixable=True,
                            fix_script=f"chmod 400 {path}"
                        )
                        issues.append(issue)
                
                # 检查目录可访问性
                elif os.path.isdir(path):
                    if not os.access(path, os.R_OK | os.X_OK):
                        issue = DiagnosticIssue(
                            id=f"dir_not_accessible_{hash(path)}",
                            category=DiagnosticCategory.PERMISSIONS,
                            severity=IssueSeverity.HIGH,
                            title=f"目录不可访问: {os.path.basename(path)}",
                            description=f"无法访问目录: {path}",
                            cause="目录权限设置不正确",
                            recommendation=f"修改目录权限: chmod +rx {path}",
                            location=path,
                            auto_fixable=True,
                            fix_script=f"chmod +rx {path}"
                        )
                        issues.append(issue)
        
        return issues
    
    def fix(self, issue: DiagnosticIssue) -> bool:
        if issue.fix_script:
            try:
                result = subprocess.run(issue.fix_script.split(), 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    logger.info(f"成功修复权限: {issue.title}")
                    return True
                else:
                    logger.error(f"权限修复失败: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"执行修复失败: {e}")
                return False
        return False

class PerformanceCheck(BaseDiagnosticCheck):
    """性能检查"""
    
    def __init__(self):
        super().__init__("performance_check", "检查系统性能")
        if not HAS_PSUTIL:
            self.enabled = False
    
    def check(self) -> List[DiagnosticIssue]:
        if not HAS_PSUTIL or not self.enabled:
            return []
        
        issues = []
        
        # 检查内存使用
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issue = DiagnosticIssue(
                id="high_memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                severity=IssueSeverity.HIGH,
                title="内存使用率过高",
                description=f"内存使用率: {memory.percent}%",
                cause="系统内存不足可能影响性能",
                recommendation="关闭不必要的进程或增加内存",
                location="系统内存",
                auto_fixable=False
            )
            issues.append(issue)
        elif memory.percent > 70:
            issue = DiagnosticIssue(
                id="moderate_memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                severity=IssueSeverity.MEDIUM,
                title="内存使用率较高",
                description=f"内存使用率: {memory.percent}%",
                cause="内存使用率较高可能影响性能",
                recommendation="监控内存使用并优化",
                location="系统内存",
                auto_fixable=False
            )
            issues.append(issue)
        
        # 检查CPU使用
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            issue = DiagnosticIssue(
                id="high_cpu_usage",
                category=DiagnosticCategory.PERFORMANCE,
                severity=IssueSeverity.MEDIUM,
                title="CPU使用率过高",
                description=f"CPU使用率: {cpu_percent}%",
                cause="CPU使用率过高可能影响响应速度",
                recommendation="检查高CPU进程并优化",
                location="系统CPU",
                auto_fixable=False
            )
            issues.append(issue)
        
        # 检查磁盘空间
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            issue = DiagnosticIssue(
                id="low_disk_space",
                category=DiagnosticCategory.STORAGE,
                severity=IssueSeverity.HIGH,
                title="磁盘空间不足",
                description=f"磁盘使用率: {disk.percent}%",
                cause="磁盘空间不足可能导致服务异常",
                recommendation="清理磁盘空间或增加存储",
                location="根目录",
                auto_fixable=False
            )
            issues.append(issue)
        elif disk.percent > 80:
            issue = DiagnosticIssue(
                id="moderate_disk_space",
                category=DiagnosticCategory.STORAGE,
                severity=IssueSeverity.MEDIUM,
                title="磁盘空间紧张",
                description=f"磁盘使用率: {disk.percent}%",
                cause="磁盘空间紧张可能影响性能",
                recommendation="监控磁盘使用并清理",
                location="根目录",
                auto_fixable=False
            )
            issues.append(issue)
        
        return issues

class ProblemDiagnoser:
    """问题诊断器主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.checks = self._initialize_checks()
        
        # 收集系统信息
        self.system_info = self._collect_system_info()
        self.openclaw_info = self._collect_openclaw_info()
    
    def _initialize_checks(self) -> List[BaseDiagnosticCheck]:
        """初始化检查器"""
        return [
            ConfigurationCheck(),
            DependenciesCheck(),
            ServiceCheck(),
            PermissionsCheck(),
            PerformanceCheck(),
        ]
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """收集系统信息"""
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cpu_count": psutil.cpu_count(),
            "total_memory": psutil.virtual_memory().total,
            "total_disk": psutil.disk_usage('/').total,
        }
    
    def _collect_openclaw_info(self) -> Dict[str, Any]:
        """收集OpenClaw信息"""
        info = {
            "openclaw_version": "unknown",
            "config_files": [],
            "skills_installed": 0,
        }
        
        # 尝试获取OpenClaw版本
        try:
            result = subprocess.run(["openclaw", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                info["openclaw_version"] = result.stdout.strip()
        except:
            pass
        
        # 检查配置文件
        config_paths = [
            "~/.openclaw/config.json",
            "~/.openclaw/config.yaml",
            "~/.openclaw/config.yml",
        ]
        
        for path_template in config_paths:
            path = os.path.expanduser(path_template)
            if os.path.exists(path):
                info["config_files"].append(path)
        
        # 检查技能目录
        skills_dir = os.path.expanduser("~/.openclaw/skills")
        if os.path.exists(skills_dir):
            try:
                skills = [d for d in os.listdir(skills_dir) 
                         if os.path.isdir(os.path.join(skills_dir, d))]
                info["skills_installed"] = len(skills)
            except:
                pass
        
        return info
    
    def run_diagnosis(self, categories: Optional[List[str]] = None) -> DiagnosticResult:
        """运行诊断"""
        logger.info("开始运行OpenClaw问题诊断")
        
        # 初始化结果
        result = DiagnosticResult(
            system_info=self.system_info,
            openclaw_info=self.openclaw_info,
            issues=[],
            checks_performed=0,
            diagnosis_duration=0.0
        )
        
        import time
        start_time = time.time()
        
        # 运行检查
        for check in self.checks:
            if not check.enabled:
                continue
                
            if categories and check.name.split('_')[0] not in categories:
                continue
                
            try:
                logger.info(f"运行检查: {check.name}")
                issues = check.check()
                result.issues.extend(issues)
                result.checks_performed += 1
                
                if issues:
                    logger.info(f"  发现 {len(issues)} 个问题")
                else:
                    logger.info("  未发现问题")
                    
            except Exception as e:
                logger.error(f"检查 {check.name} 失败: {e}")
        
        result.diagnosis_duration = time.time() - start_time
        
        logger.info(f"诊断完成: 执行了 {result.checks_performed} 个检查，发现 {len(result.issues)} 个问题")
        
        return result
    
    def apply_fixes(self, result: DiagnosticResult, auto_only: bool = True) -> Dict[str, Any]:
        """应用修复"""
        fixes_applied = []
        fixes_failed = []
        
        for issue in result.issues:
            if not issue.auto_fixable:
                continue
                
            if auto_only and not issue.auto_fixable:
                continue
                
            # 找到对应的检查器
            for check in self.checks:
                if check.name.startswith(issue.category.value.split('_')[0]):
                    try:
                        logger.info(f"尝试修复: {issue.title}")
                        success = check.fix(issue)
                        if success:
                            fixes_applied.append(issue.id)
                            logger.info(f"  修复成功: {issue.id}")
                        else:
                            fixes_failed.append(issue.id)
                            logger.warning(f"  修复失败: {issue.id}")
                    except Exception as e:
                        logger.error(f"修复异常 {issue.id}: {e}")
                        fixes_failed.append(issue.id)
                    break
        
        return {
            "applied": fixes_applied,
            "failed": fixes_failed,
            "total_applied": len(fixes_applied),
            "total_failed": len(fixes_failed),
        }
    
    def generate_report(self, result: DiagnosticResult, format: str = "console") -> str:
        """生成报告"""
        if format == "json":
            return result.to_json()
        elif format == "console":
            return self._generate_console_report(result)
        elif format == "markdown":
            return self._generate_markdown_report(result)
        else:
            raise ValueError(f"不支持的报告格式: {format}")
    
    def _generate_console_report(self, result: DiagnosticResult) -> str:
        """生成控制台报告"""
        try:
            import colorama
            from colorama import Fore, Style
            colorama.init()
            has_color = True
        except ImportError:
            has_color = False
        
        report_lines = []
        
        if has_color:
            report_lines.append(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            report_lines.append(f"{Fore.GREEN}Claw Problem Diagnoser 诊断报告{Style.RESET_ALL}")
            report_lines.append(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        else:
            report_lines.append("=" * 60)
            report_lines.append("Claw Problem Diagnoser 诊断报告")
            report_lines.append("=" * 60)
        
        # 系统信息
        report_lines.append("")
        report_lines.append("📊 系统信息:")
        report_lines.append(f"  平台: {result.system_info['platform']}")
        report_lines.append(f"  Python: {result.system_info['python_version']}")
        report_lines.append(f"  主机名: {result.system_info['hostname']}")
        report_lines.append(f"  CPU核心: {result.system_info['cpu_count']}")
        report_lines.append(f"  内存: {result.system_info['total_memory'] // (1024**3)} GB")
        report_lines.append(f"  磁盘: {result.system_info['total_disk'] // (1024**3)} GB")
        
        # OpenClaw信息
        report_lines.append("")
        report_lines.append("🦞 OpenClaw信息:")
        report_lines.append(f"  版本: {result.openclaw_info['openclaw_version']}")
        report_lines.append(f"  配置文件: {len(result.openclaw_info['config_files'])} 个")
        report_lines.append(f"  已安装技能: {result.openclaw_info['skills_installed']} 个")
        
        # 诊断统计
        report_lines.append("")
        report_lines.append("📈 诊断统计:")
        report_lines.append(f"  检查数量: {result.checks_performed}")
        report_lines.append(f"  发现问题: {len(result.issues)}")
        report_lines.append(f"  诊断耗时: {result.diagnosis_duration:.2f}秒")
        
        stats = result.statistics()
        if stats['total_issues'] > 0:
            report_lines.append("")
            if has_color:
                report_lines.append(f"{Fore.YELLOW}⚠️  问题统计:{Style.RESET_ALL}")
            else:
                report_lines.append("⚠️  问题统计:")
            
            report_lines.append("  严重性分布:")
            for level, count in stats['by_severity'].items():
                if count > 0:
                    report_lines.append(f"    - {level.upper()}: {count}")
            
            report_lines.append("  类别分布:")
            for category, count in stats['by_category'].items():
                if count > 0:
                    report_lines.append(f"    - {category}: {count}")
            
            report_lines.append(f"  可自动修复: {stats['auto_fixable']}")
        
        # 问题详情
        if result.issues:
            report_lines.append("")
            if has_color:
                report_lines.append(f"{Fore.RED}🔍 问题详情:{Style.RESET_ALL}")
            else:
                report_lines.append("🔍 问题详情:")
            
            # 按严重性排序
            severity_order = {
                IssueSeverity.CRITICAL: 0,
                IssueSeverity.HIGH: 1,
                IssueSeverity.MEDIUM: 2,
                IssueSeverity.LOW: 3,
                IssueSeverity.INFO: 4
            }
            
            sorted_issues = sorted(result.issues, key=lambda x: severity_order[x.severity])
            
            for i, issue in enumerate(sorted_issues[:10], 1):  # 只显示前10个
                if has_color:
                    severity_colors = {
                        IssueSeverity.CRITICAL: Fore.RED,
                        IssueSeverity.HIGH: Fore.LIGHTRED_EX,
                        IssueSeverity.MEDIUM: Fore.YELLOW,
                        IssueSeverity.LOW: Fore.GREEN,
                        IssueSeverity.INFO: Fore.BLUE
                    }
                    color = severity_colors.get(issue.severity, Fore.WHITE)
                    report_lines.append(f"{color}  {i}. [{issue.severity.value.upper()}] {issue.title}{Style.RESET_ALL}")
                else:
                    report_lines.append(f"  {i}. [{issue.severity.value.upper()}] {issue.title}")
                
                report_lines.append(f"     类别: {issue.category.value}")
                report_lines.append(f"     位置: {issue.location}")
                if issue.auto_fixable:
                    report_lines.append(f"     可自动修复: 是")
                report_lines.append("")
        
        else:
            report_lines.append("")
            if has_color:
                report_lines.append(f"{Fore.GREEN}✅ 未发现任何问题！{Style.RESET_ALL}")
            else:
                report_lines.append("✅ 未发现任何问题！")
        
        if has_color:
            report_lines.append(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        else:
            report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def _generate_markdown_report(self, result: DiagnosticResult) -> str:
        """生成Markdown报告"""
        report_lines = []
        report_lines.append("# Claw Problem Diagnoser 诊断报告")
        report_lines.append("")
        report_lines.append(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**诊断耗时**: {result.diagnosis_duration:.2f}秒")
        report_lines.append("")
        
        # 系统信息
        report_lines.append("## 系统信息")
        report_lines.append("")
        report_lines.append("| 项目 | 值 |")
        report_lines.append("|------|-----|")
        report_lines.append(f"| 平台 | {result.system_info['platform']} |")
        report_lines.append(f"| Python版本 | {result.system_info['python_version']} |")
        report_lines.append(f"| 主机名 | {result.system_info['hostname']} |")
        report_lines.append(f"| CPU核心 | {result.system_info['cpu_count']} |")
        report_lines.append(f"| 总内存 | {result.system_info['total_memory'] // (1024**3)} GB |")
        report_lines.append(f"| 总磁盘 | {result.system_info['total_disk'] // (1024**3)} GB |")
        report_lines.append("")
        
        # OpenClaw信息
        report_lines.append("## OpenClaw信息")
        report_lines.append("")
        report_lines.append("| 项目 | 值 |")
        report_lines.append("|------|-----|")
        report_lines.append(f"| 版本 | {result.openclaw_info['openclaw_version']} |")
        report_lines.append(f"| 配置文件 | {len(result.openclaw_info['config_files'])} 个 |")
        report_lines.append(f"| 已安装技能 | {result.openclaw_info['skills_installed']} 个 |")
        report_lines.append("")
        
        # 诊断统计
        stats = result.statistics()
        report_lines.append("## 诊断统计")
        report_lines.append("")
        report_lines.append("| 统计项 | 值 |")
        report_lines.append("|--------|-----|")
        report_lines.append(f"| 检查数量 | {result.checks_performed} |")
        report_lines.append(f"| 发现问题 | {stats['total_issues']} |")
        report_lines.append(f"| 可自动修复 | {stats['auto_fixable']} |")
        report_lines.append("")
        
        if stats['total_issues'] > 0:
            # 严重性分布
            report_lines.append("## 问题严重性分布")
            report_lines.append("")
            for level, count in stats['by_severity'].items():
                if count > 0:
                    report_lines.append(f"- **{level.upper()}**: {count}")
            report_lines.append("")
            
            # 类别分布
            report_lines.append("## 问题类别分布")
            report_lines.append("")
            for category, count in stats['by_category'].items():
                if count > 0:
                    report_lines.append(f"- **{category}**: {count}")
            report_lines.append("")
            
            # 问题详情
            report_lines.append("## 问题详情")
            report_lines.append("")
            
            # 按严重性排序
            severity_order = {
                IssueSeverity.CRITICAL: 0,
                IssueSeverity.HIGH: 1,
                IssueSeverity.MEDIUM: 2,
                IssueSeverity.LOW: 3,
                IssueSeverity.INFO: 4
            }
            
            sorted_issues = sorted(result.issues, key=lambda x: severity_order[x.severity])
            
            for i, issue in enumerate(sorted_issues, 1):
                report_lines.append(f"### {i}. [{issue.severity.value.upper()}] {issue.title}")
                report_lines.append("")
                report_lines.append(f"**类别**: {issue.category.value}")
                report_lines.append("")
                report_lines.append(f"**描述**: {issue.description}")
                report_lines.append("")
                report_lines.append(f"**原因**: {issue.cause}")
                report_lines.append("")
                report_lines.append(f"**建议**: {issue.recommendation}")
                report_lines.append("")
                report_lines.append(f"**位置**: `{issue.location}`")
                report_lines.append("")
                if issue.auto_fixable:
                    report_lines.append(f"**可自动修复**: 是")
                    if issue.fix_script:
                        report_lines.append(f"**修复脚本**: `{issue.fix_script}`")
                report_lines.append("")
        else:
            report_lines.append("## 诊断结果")
            report_lines.append("")
            report_lines.append("✅ **未发现任何问题！**")
            report_lines.append("")
            report_lines.append("您的OpenClaw系统运行良好。")
        
        report_lines.append("---")
        report_lines.append("*报告生成工具: Claw Problem Diagnoser v0.1.0*")
        
        return "\n".join(report_lines)

# 命令行接口
def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claw Problem Diagnoser - OpenClaw问题诊断器')
    parser.add_argument('--categories', help='指定诊断类别 (用逗号分隔: config,dependencies,service,permissions,performance)')
    parser.add_argument('--format', choices=['console', 'json', 'markdown'], default='console',
                       help='报告格式 (default: console)')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--auto-fix', action='store_true', help='自动修复可修复的问题')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 解析类别
    categories = None
    if args.categories:
        categories = [cat.strip() for cat in args.categories.split(',')]
    
    # 运行诊断
    diagnostor = ProblemDiagnoser()
    result = diagnostor.run_diagnosis(categories)
    
    # 自动修复
    if args.auto_fix:
        logger.info("尝试自动修复...")
        fixes = diagnostor.apply_fixes(result, auto_only=True)
        logger.info(f"修复完成: {fixes['total_applied']} 成功, {fixes['total_failed']} 失败")
    
    # 生成报告
    report = diagnostor.generate_report(result, args.format)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)
    
    # 退出码：如果有严重或高问题，返回非零
    if result.has_critical_or_high():
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()