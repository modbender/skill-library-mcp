#!/usr/bin/env python3
"""
Claw Security Scanner - OpenClaw技能安全扫描器
检测技能文件中的安全威胁，保护用户免受恶意代码侵害
"""

import os
import re
import json
import yaml
import hashlib
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import warnings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 禁用一些警告
warnings.filterwarnings('ignore')

class RiskLevel(Enum):
    """风险评估等级"""
    CRITICAL = "critical"      # 严重风险
    HIGH = "high"              # 高风险  
    MEDIUM = "medium"          # 中等风险
    LOW = "low"                # 低风险
    INFO = "info"              # 信息性

class DetectionCategory(Enum):
    """检测类别"""
    CREDENTIALS = "credentials"       # 凭据泄露
    MALWARE = "malware"               # 恶意代码
    VULNERABILITY = "vulnerability"   # 漏洞
    CONFIGURATION = "configuration"   # 配置问题
    PERMISSIONS = "permissions"       # 权限问题
    DEPENDENCY = "dependency"         # 依赖安全问题
    CODE_QUALITY = "code_quality"     # 代码质量问题

@dataclass
class SecurityFinding:
    """安全发现"""
    id: str                           # 唯一标识
    category: DetectionCategory       # 检测类别
    risk_level: RiskLevel             # 风险等级
    file_path: str                    # 文件路径
    line_number: int                  # 行号（如有）
    description: str                  # 问题描述
    evidence: str                     # 证据/匹配内容
    recommendation: str               # 修复建议
    detector_name: str                # 检测器名称
    
    # 可选字段
    cve_id: Optional[str] = None      # CVE编号（如有）
    fix_available: bool = False       # 是否有可用修复
    auto_fixable: bool = False        # 是否可自动修复

@dataclass
class ScanResult:
    """扫描结果"""
    skill_path: str                   # 技能路径
    skill_name: str                   # 技能名称
    total_files: int                  # 总文件数
    scanned_files: int                # 已扫描文件数
    findings: List[SecurityFinding] = field(default_factory=list)  # 所有发现
    scan_duration: float = 0.0        # 扫描耗时（秒）
    
    # 风险统计
    def risk_statistics(self) -> Dict[str, int]:
        """计算风险统计"""
        stats = {level.value: 0 for level in RiskLevel}
        for finding in self.findings:
            stats[finding.risk_level.value] += 1
        return stats
    
    def has_critical_or_high(self) -> bool:
        """是否有严重或高风险"""
        for finding in self.findings:
            if finding.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['findings'] = [asdict(f) for f in self.findings]
        result['risk_statistics'] = self.risk_statistics()
        result['has_critical_or_high'] = self.has_critical_or_high()
        return result
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

class BaseDetector:
    """检测器基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        
    def detect(self, file_path: str, content: str) -> List[SecurityFinding]:
        """检测文件内容，返回安全发现列表"""
        raise NotImplementedError("子类必须实现detect方法")
    
    def should_skip_file(self, file_path: str) -> bool:
        """是否跳过该文件"""
        skip_patterns = [
            r'node_modules/',
            r'\.git/',
            r'__pycache__/',
            r'\.pyc$',
            r'\.log$',
            r'\.tmp$',
            r'\.cache$',
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        return False

class CredentialDetector(BaseDetector):
    """凭据泄露检测器"""
    
    def __init__(self):
        super().__init__("credential_detector", "检测硬编码的凭据和敏感信息")
        
        # 常见凭据模式
        self.patterns = [
            # API密钥
            (r'(api[_-]?key|apikey)[\s=:]+["\']?([a-zA-Z0-9_\-]{20,})["\']?', RiskLevel.CRITICAL),
            (r'secret[_-]?(key|token)[\s=:]+["\']?([a-zA-Z0-9_\-]{20,})["\']?', RiskLevel.CRITICAL),
            
            # 访问令牌
            (r'access[_-]?(token|key)[\s=:]+["\']?([a-zA-Z0-9_\-]{20,})["\']?', RiskLevel.CRITICAL),
            (r'bearer[\s=:]+["\']?([a-zA-Z0-9_\-\._]{20,})["\']?', RiskLevel.CRITICAL),
            
            # 密码
            (r'password[\s=:]+["\']?([^\s"\']{6,})["\']?', RiskLevel.HIGH),
            (r'passwd[\s=:]+["\']?([^\s"\']{6,})["\']?', RiskLevel.HIGH),
            
            # 数据库连接字符串
            (r'(mysql|postgresql|mongodb)://[^:]+:[^@]+@', RiskLevel.CRITICAL),
            
            # SSH密钥
            (r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----', RiskLevel.CRITICAL),
            
            # AWS凭证
            (r'AWS_ACCESS_KEY_ID[\s=:]+["\']?([A-Z0-9]{20})["\']?', RiskLevel.CRITICAL),
            (r'AWS_SECRET_ACCESS_KEY[\s=:]+["\']?([a-zA-Z0-9/+]{40})["\']?', RiskLevel.CRITICAL),
            
            # JWT令牌
            (r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', RiskLevel.HIGH),
        ]
    
    def detect(self, file_path: str, content: str) -> List[SecurityFinding]:
        if self.should_skip_file(file_path):
            return []
        
        findings = []
        
        for pattern, risk_level in self.patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # 计算行号
                line_number = content[:match.start()].count('\n') + 1
                
                # 提取匹配的证据（前50个字符）
                evidence = match.group(0)
                if len(evidence) > 100:
                    evidence = evidence[:100] + "..."
                
                finding = SecurityFinding(
                    id=f"cred_{hashlib.md5(f'{file_path}:{line_number}'.encode()).hexdigest()[:8]}",
                    category=DetectionCategory.CREDENTIALS,
                    risk_level=risk_level,
                    file_path=file_path,
                    line_number=line_number,
                    description=f"检测到潜在的凭据泄露: {match.group(1) if match.groups() else '敏感信息'}",
                    evidence=evidence,
                    recommendation="移除硬编码的凭据，使用环境变量或安全的配置管理系统",
                    detector_name=self.name,
                    fix_available=True,
                    auto_fixable=False  # 凭据修复需要人工审查
                )
                findings.append(finding)
        
        return findings

class MalwareDetector(BaseDetector):
    """恶意代码检测器"""
    
    def __init__(self):
        super().__init__("malware_detector", "检测恶意代码模式")
        
        # 恶意代码模式
        self.malware_patterns = [
            # 远程代码执行
            (r'eval\([\s\S]{0,100}\)', RiskLevel.CRITICAL),
            (r'exec\([\s\S]{0,100}\)', RiskLevel.HIGH),
            (r'__import__\([\s\S]{0,100}\)', RiskLevel.HIGH),
            
            # 文件系统操作（可疑）
            (r'open\([^)]*["\']/(etc/passwd|etc/shadow|\.ssh/id_rsa)["\']', RiskLevel.CRITICAL),
            (r'subprocess\.(Popen|run|call)\([^)]*["\'](rm -rf|format|dd if)', RiskLevel.CRITICAL),
            
            # 网络连接（可疑）
            (r'requests\.(get|post)\([^)]*["\']https?://[^/]+/[^"\']*["\']', RiskLevel.MEDIUM),
            (r'socket\.(connect|create_connection)\([^)]*', RiskLevel.MEDIUM),
            
            # 加密挖矿
            (r'cryptocurrency|mining|bitcoin|ethereum|monero', RiskLevel.HIGH),
            (r'stratum|pool|hashrate', RiskLevel.HIGH),
            
            # 键盘记录
            (r'keyboard\.(on_press|record)', RiskLevel.CRITICAL),
            (r'pyinput|pynput', RiskLevel.HIGH),
            
            # 数据外泄
            (r'requests\.post\([^)]*webhook|telegram\.org|discord\.com', RiskLevel.HIGH),
        ]
    
    def detect(self, file_path: str, content: str) -> List[SecurityFinding]:
        if self.should_skip_file(file_path):
            return []
        
        findings = []
        
        for pattern, risk_level in self.malware_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                evidence = match.group(0)
                if len(evidence) > 100:
                    evidence = evidence[:100] + "..."
                
                finding = SecurityFinding(
                    id=f"malware_{hashlib.md5(f'{file_path}:{line_number}'.encode()).hexdigest()[:8]}",
                    category=DetectionCategory.MALWARE,
                    risk_level=risk_level,
                    file_path=file_path,
                    line_number=line_number,
                    description=f"检测到可疑的恶意代码模式",
                    evidence=evidence,
                    recommendation="审查此代码的用途，确保没有恶意行为",
                    detector_name=self.name,
                    fix_available=False,
                    auto_fixable=False
                )
                findings.append(finding)
        
        return findings

class DependencyDetector(BaseDetector):
    """依赖安全检查器"""
    
    def __init__(self):
        super().__init__("dependency_detector", "检查依赖包的安全问题")
    
    def detect(self, file_path: str, content: str) -> List[SecurityFinding]:
        if self.should_skip_file(file_path):
            return []
        
        findings = []
        
        # 检查package.json
        if file_path.endswith('package.json'):
            try:
                data = json.loads(content)
                dependencies = data.get('dependencies', {})
                dev_dependencies = data.get('devDependencies', {})
                
                # 这里可以集成真实的漏洞数据库
                # 暂时检查已知的有问题的包
                problematic_packages = {
                    'lodash': 'CVE-2021-23337',
                    'axios': '多个版本安全问题',
                    'express': 'CVE-2022-24999',
                }
                
                for pkg_name, pkg_version in {**dependencies, **dev_dependencies}.items():
                    if pkg_name in problematic_packages:
                        finding = SecurityFinding(
                            id=f"dep_{hashlib.md5(f'{file_path}:{pkg_name}'.encode()).hexdigest()[:8]}",
                            category=DetectionCategory.DEPENDENCY,
                            risk_level=RiskLevel.MEDIUM,
                            file_path=file_path,
                            line_number=1,  # 粗略的行号
                            description=f"依赖包 {pkg_name} 可能存在安全问题: {problematic_packages[pkg_name]}",
                            evidence=f"{pkg_name}: {pkg_version}",
                            recommendation=f"更新 {pkg_name} 到最新安全版本",
                            detector_name=self.name,
                            fix_available=True,
                            auto_fixable=True
                        )
                        findings.append(finding)
                        
            except json.JSONDecodeError:
                logger.warning(f"无法解析JSON文件: {file_path}")
        
        # 检查requirements.txt
        elif file_path.endswith('requirements.txt'):
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 检查版本固定
                if '>=' in line or '==' in line or '~=' in line:
                    # 版本已固定，风险较低
                    pass
                else:
                    # 未固定版本，风险中等
                    pkg_name = line.split('==')[0].split('>=')[0].split('~=')[0].strip()
                    
                    finding = SecurityFinding(
                        id=f"dep_{hashlib.md5(f'{file_path}:{line_num}'.encode()).hexdigest()[:8]}",
                        category=DetectionCategory.DEPENDENCY,
                        risk_level=RiskLevel.LOW,
                        file_path=file_path,
                        line_number=line_num,
                        description=f"依赖包 {pkg_name} 未固定版本，可能引入不兼容或安全问题",
                        evidence=line,
                        recommendation=f"固定 {pkg_name} 的版本号，如 {pkg_name}==x.x.x",
                        detector_name=self.name,
                        fix_available=True,
                        auto_fixable=True
                    )
                    findings.append(finding)
        
        return findings

class ConfigurationDetector(BaseDetector):
    """配置安全检测器"""
    
    def __init__(self):
        super().__init__("configuration_detector", "检查配置文件的安全问题")
    
    def detect(self, file_path: str, content: str) -> List[SecurityFinding]:
        if self.should_skip_file(file_path):
            return []
        
        findings = []
        
        # 检查.env文件
        if '.env' in file_path or file_path.endswith('.env.example'):
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 检查是否包含示例值但未标记
                if 'example' in line.lower() or 'demo' in line.lower() or 'test' in line.lower():
                    continue  # 这是示例，没问题
                
                # 检查是否有实际值但应该是示例
                if '=' in line:
                    key, value = line.split('=', 1)
                    if value and not value.startswith('your_') and not value.startswith('YOUR_'):
                        finding = SecurityFinding(
                            id=f"config_{hashlib.md5(f'{file_path}:{line_num}'.encode()).hexdigest()[:8]}",
                            category=DetectionCategory.CONFIGURATION,
                            risk_level=RiskLevel.MEDIUM,
                            file_path=file_path,
                            line_number=line_num,
                            description=f"配置文件可能包含硬编码的值: {key}",
                            evidence=line,
                            recommendation=f"将 {key} 的值替换为环境变量引用或占位符",
                            detector_name=self.name,
                            fix_available=True,
                            auto_fixable=True
                        )
                        findings.append(finding)
        
        # 检查YAML配置文件
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    # 检查敏感配置
                    sensitive_keys = ['password', 'secret', 'token', 'key', 'credential']
                    for key_path, value in self._flatten_dict(data):
                        for sensitive in sensitive_keys:
                            if sensitive in key_path.lower() and value and str(value).strip():
                                finding = SecurityFinding(
                                    id=f"config_{hashlib.md5(f'{file_path}:{key_path}'.encode()).hexdigest()[:8]}",
                                    category=DetectionCategory.CONFIGURATION,
                                    risk_level=RiskLevel.HIGH,
                                    file_path=file_path,
                                    line_number=1,  # 粗略行号
                                    description=f"YAML配置中包含敏感信息: {key_path}",
                                    evidence=f"{key_path}: {value}",
                                    recommendation=f"将敏感配置移出配置文件，使用环境变量或加密存储",
                                    detector_name=self.name,
                                    fix_available=True,
                                    auto_fixable=False
                                )
                                findings.append(finding)
                                break
            except yaml.YAMLError:
                logger.warning(f"无法解析YAML文件: {file_path}")
        
        return findings
    
    def _flatten_dict(self, d: Dict, parent_key: str = '') -> List[Tuple[str, Any]]:
        """展平嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items

class SecurityScanner:
    """安全扫描器主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.detectors = self._initialize_detectors()
        
        # 支持的文件扩展名
        self.supported_extensions = [
            '.py', '.js', '.ts', '.json', '.yaml', '.yml', 
            '.md', '.txt', '.sh', '.bash', '.env', '.toml'
        ]
    
    def _initialize_detectors(self) -> List[BaseDetector]:
        """初始化检测器"""
        return [
            CredentialDetector(),
            MalwareDetector(),
            DependencyDetector(),
            ConfigurationDetector(),
        ]
    
    def scan_skill(self, skill_path: str) -> ScanResult:
        """扫描技能目录"""
        skill_path = os.path.abspath(skill_path)
        skill_name = os.path.basename(skill_path)
        
        logger.info(f"开始扫描技能: {skill_name} ({skill_path})")
        
        # 收集所有文件
        all_files = self._collect_files(skill_path)
        logger.info(f"找到 {len(all_files)} 个文件")
        
        # 初始化扫描结果
        result = ScanResult(
            skill_path=skill_path,
            skill_name=skill_name,
            total_files=len(all_files),
            scanned_files=0,
            findings=[]
        )
        
        import time
        start_time = time.time()
        
        # 扫描每个文件
        scanned_count = 0
        for file_path in all_files:
            if not self._should_scan_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 运行所有检测器
                for detector in self.detectors:
                    if detector.enabled:
                        findings = detector.detect(file_path, content)
                        result.findings.extend(findings)
                
                scanned_count += 1
                
            except Exception as e:
                logger.warning(f"扫描文件失败 {file_path}: {e}")
        
        result.scanned_files = scanned_count
        result.scan_duration = time.time() - start_time
        
        logger.info(f"扫描完成: 扫描了 {scanned_count} 个文件，发现 {len(result.findings)} 个问题")
        
        return result
    
    def _collect_files(self, directory: str) -> List[str]:
        """收集目录中的所有文件"""
        all_files = []
        for root, dirs, files in os.walk(directory):
            # 跳过一些目录
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
            
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        
        return all_files
    
    def _should_scan_file(self, file_path: str) -> bool:
        """判断是否应该扫描该文件"""
        # 检查扩展名
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.supported_extensions:
            return True
        
        # 检查特殊文件
        special_files = ['Dockerfile', 'docker-compose.yml', 'Makefile', 'package.json', 'requirements.txt']
        if os.path.basename(file_path) in special_files:
            return True
        
        # 检查没有扩展名的文件
        if not ext:
            # 尝试读取前几行判断内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                    if first_line.startswith('#!') and ('python' in first_line or 'bash' in first_line or 'sh' in first_line):
                        return True
            except:
                pass
        
        return False
    
    def generate_report(self, result: ScanResult, format: str = "console") -> str:
        """生成报告"""
        if format == "json":
            return result.to_json()
        elif format == "console":
            return self._generate_console_report(result)
        elif format == "markdown":
            return self._generate_markdown_report(result)
        else:
            raise ValueError(f"不支持的报告格式: {format}")
    
    def _generate_console_report(self, result: ScanResult) -> str:
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
            report_lines.append(f"{Fore.GREEN}Claw Security Scanner 报告{Style.RESET_ALL}")
            report_lines.append(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        else:
            report_lines.append("=" * 60)
            report_lines.append("Claw Security Scanner 报告")
            report_lines.append("=" * 60)
        report_lines.append(f"技能: {result.skill_name}")
        report_lines.append(f"路径: {result.skill_path}")
        report_lines.append(f"扫描时间: {result.scan_duration:.2f}秒")
        report_lines.append(f"文件统计: {result.scanned_files}/{result.total_files} 个文件已扫描")
        report_lines.append("")
        
        # 风险统计
        stats = result.risk_statistics()
        if has_color:
            report_lines.append(f"{Fore.YELLOW}风险统计:{Style.RESET_ALL}")
        else:
            report_lines.append("风险统计:")
        
        for level_name, count in stats.items():
            if has_color:
                color = {
                    'critical': Fore.RED,
                    'high': Fore.LIGHTRED_EX,
                    'medium': Fore.YELLOW,
                    'low': Fore.GREEN,
                    'info': Fore.BLUE
                }.get(level_name, Fore.WHITE)
                report_lines.append(f"  {color}{level_name.upper():<10}{Style.RESET_ALL}: {count}")
            else:
                report_lines.append(f"  {level_name.upper():<10}: {count}")
        
        report_lines.append("")
        
        if not result.findings:
            if has_color:
                report_lines.append(f"{Fore.GREEN}✅ 未发现安全问题！{Style.RESET_ALL}")
            else:
                report_lines.append("✅ 未发现安全问题！")
        else:
            # 按风险等级分组
            critical_high = [f for f in result.findings if f.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
            medium_low = [f for f in result.findings if f.risk_level in [RiskLevel.MEDIUM, RiskLevel.LOW]]
            info = [f for f in result.findings if f.risk_level == RiskLevel.INFO]
            
            if critical_high:
                if has_color:
                    report_lines.append(f"{Fore.RED}⚠️  严重/高风险问题 ({len(critical_high)}个):{Style.RESET_ALL}")
                else:
                    report_lines.append(f"⚠️  严重/高风险问题 ({len(critical_high)}个):")
                for finding in critical_high[:5]:  # 只显示前5个
                    if has_color:
                        risk_color = Fore.RED if finding.risk_level == RiskLevel.CRITICAL else Fore.LIGHTRED_EX
                        report_lines.append(f"  {risk_color}● {finding.description}{Style.RESET_ALL}")
                    else:
                        report_lines.append(f"  ● {finding.description}")
                    report_lines.append(f"     文件: {finding.file_path}")
                    if finding.line_number > 0:
                        report_lines.append(f"     行号: {finding.line_number}")
                    report_lines.append(f"     建议: {finding.recommendation}")
                    report_lines.append("")
            
            if medium_low:
                if has_color:
                    report_lines.append(f"{Fore.YELLOW}中等/低风险问题 ({len(medium_low)}个):{Style.RESET_ALL}")
                else:
                    report_lines.append(f"中等/低风险问题 ({len(medium_low)}个):")
                for finding in medium_low[:3]:
                    report_lines.append(f"  ● {finding.description}")
                    report_lines.append(f"     文件: {finding.file_path}")
                    report_lines.append("")
            
            if info:
                if has_color:
                    report_lines.append(f"{Fore.BLUE}信息性建议 ({len(info)}个):{Style.RESET_ALL}")
                else:
                    report_lines.append(f"信息性建议 ({len(info)}个):")
                for finding in info[:2]:
                    report_lines.append(f"  ● {finding.description}")
                    report_lines.append("")
        
        if has_color:
            report_lines.append(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        else:
            report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def _generate_markdown_report(self, result: ScanResult) -> str:
        """生成Markdown报告"""
        report_lines = []
        report_lines.append("# Claw Security Scanner 报告")
        report_lines.append("")
        report_lines.append(f"**技能**: {result.skill_name}")
        report_lines.append(f"**路径**: `{result.skill_path}`")
        report_lines.append(f"**扫描时间**: {result.scan_duration:.2f}秒")
        report_lines.append(f"**文件统计**: {result.scanned_files}/{result.total_files} 个文件已扫描")
        report_lines.append("")
        
        # 风险统计
        stats = result.risk_statistics()
        report_lines.append("## 风险统计")
        report_lines.append("")
        report_lines.append("| 风险等级 | 数量 |")
        report_lines.append("|----------|------|")
        for level_name, count in stats.items():
            report_lines.append(f"| {level_name.upper()} | {count} |")
        report_lines.append("")
        
        if not result.findings:
            report_lines.append("✅ **未发现安全问题！**")
        else:
            # 分组显示
            critical_high = [f for f in result.findings if f.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
            medium_low = [f for f in result.findings if f.risk_level in [RiskLevel.MEDIUM, RiskLevel.LOW]]
            
            if critical_high:
                report_lines.append("## ⚠️ 严重/高风险问题")
                report_lines.append("")
                for i, finding in enumerate(critical_high, 1):
                    report_lines.append(f"### {i}. {finding.description}")
                    report_lines.append("")
                    report_lines.append(f"- **文件**: `{finding.file_path}`")
                    if finding.line_number > 0:
                        report_lines.append(f"- **行号**: {finding.line_number}")
                    report_lines.append(f"- **风险等级**: {finding.risk_level.value.upper()}")
                    report_lines.append(f"- **证据**: `{finding.evidence}`")
                    report_lines.append(f"- **建议**: {finding.recommendation}")
                    report_lines.append("")
            
            if medium_low:
                report_lines.append("## 中等/低风险问题")
                report_lines.append("")
                for i, finding in enumerate(medium_low[:10], 1):
                    report_lines.append(f"{i}. **{finding.description}**")
                    report_lines.append(f"   - 文件: `{finding.file_path}`")
                    report_lines.append(f"   - 风险: {finding.risk_level.value}")
                    report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("*报告生成时间: 2026-02-11*")
        
        return "\n".join(report_lines)

# 命令行接口
def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claw Security Scanner - OpenClaw技能安全扫描器')
    parser.add_argument('skill_path', help='技能目录路径')
    parser.add_argument('--format', choices=['console', 'json', 'markdown'], default='console',
                       help='报告格式 (default: console)')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 检查路径是否存在
    if not os.path.exists(args.skill_path):
        print(f"错误: 路径不存在: {args.skill_path}")
        sys.exit(1)
    
    # 运行扫描
    scanner = SecurityScanner()
    result = scanner.scan_skill(args.skill_path)
    
    # 生成报告
    report = scanner.generate_report(result, args.format)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)
    
    # 退出码：如果有严重或高风险，返回非零
    if result.has_critical_or_high():
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()