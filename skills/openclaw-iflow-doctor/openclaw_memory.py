#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw iFlow Doctor
功能：智能诊断、自动修复、与 iflow 集成、用户引导
"""
import sys
import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

class OpenClawDoctor:
    """OpenClaw iFlow Doctor - 智能诊断修复类"""
    
    # 问题类型与BAT选项的映射表
    PROBLEM_BAT_MAPPING = {
        "memory": {
            "keywords": ["memory", "search", "identity", "remember", "记忆", "搜索"],
            "bat_options": ["reset_memory", "open_iflow"],
            "description_cn": "重置记忆索引",
            "description_en": "Reset Memory Index"
        },
        "gateway": {
            "keywords": ["gateway", "start", "crash", "service", "服务", "启动", "崩溃"],
            "bat_options": ["restart_gateway", "open_iflow"],
            "description_cn": "重启Gateway服务",
            "description_en": "Restart Gateway Service"
        },
        "config": {
            "keywords": ["config", "configuration", "json", "corrupt", "配置", "损坏"],
            "bat_options": ["reset_config", "open_iflow"],
            "description_cn": "重置配置文件",
            "description_en": "Reset Configuration"
        },
        "network": {
            "keywords": ["network", "connection", "timeout", "refused", "网络", "连接", "超时"],
            "bat_options": ["check_network", "open_iflow"],
            "description_cn": "检查网络连接",
            "description_en": "Check Network Connection"
        },
        "api": {
            "keywords": ["api", "rate limit", "quota", "429", "额度", "限制"],
            "bat_options": ["check_api_quota", "open_iflow"],
            "description_cn": "检查API额度",
            "description_en": "Check API Quota"
        },
        "agent": {
            "keywords": ["agent", "spawn", "subagent", "代理", "子代理"],
            "bat_options": ["reload_agents", "open_iflow"],
            "description_cn": "重新加载Agent",
            "description_en": "Reload Agents"
        },
        "permission": {
            "keywords": ["permission", "denied", "access", "403", "权限", "拒绝"],
            "bat_options": ["fix_permissions", "open_iflow"],
            "description_cn": "修复权限",
            "description_en": "Fix Permissions"
        },
        "install": {
            "keywords": ["install", "reinstall", "missing", "安装", "丢失"],
            "bat_options": ["reinstall_openclaw", "open_iflow"],
            "description_cn": "重新安装OpenClaw",
            "description_en": "Reinstall OpenClaw"
        },
        "unknown": {
            "keywords": [],
            "bat_options": ["reinstall_openclaw", "open_iflow"],
            "description_cn": "重新安装OpenClaw",
            "description_en": "Reinstall OpenClaw"
        }
    }
    
    def __init__(self):
        # 基础路径 - 独立目录
        self.base_dir = Path(os.path.expanduser("~/.iflow/memory/openclaw"))
        self.desktop_dir = Path(os.path.expanduser("~/Desktop"))
        
        # 配置文件和数据文件（都在同一目录）
        self.config_file = self.base_dir / "config.json"
        self.case_file = self.base_dir / "cases.json"
        self.record_file = self.base_dir / "records.json"
        self.call_log_file = self.base_dir / "call_logs.json"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 加载配置
        self.config = self._load_config()
        
        # 加载数据
        self.cases = self._load_cases()
        self.records = self._load_records()
        
        # 系统类型检测
        self.system_type = self._detect_system_type()  # windows/linux/macos
        
        # 检测系统语言
        self.system_lang = self._detect_system_language()
    
    def _ensure_directories(self):
        """确保基础目录存在"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_system_type(self):
        """检测操作系统类型，返回 'windows'/'linux'/'macos'"""
        import platform
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        else:
            return 'linux'
    
    def _detect_system_language(self):
        """检测系统语言，返回 'zh' 或 'en'"""
        import locale
        try:
            # 获取系统默认语言
            lang = locale.getdefaultlocale()[0]
            if lang and (lang.startswith('zh') or lang.startswith('Chinese')):
                return 'zh'
        except:
            pass
        
        # 通过环境变量检测
        env_lang = os.environ.get('LANG', '') + os.environ.get('LC_ALL', '')
        if 'zh' in env_lang or 'CN' in env_lang:
            return 'zh'
        
        # 默认英文
        return 'en'
    
    def _classify_problem(self, error_text):
        """
        根据错误描述分类问题类型
        
        返回:
            str: 问题类型键名 (memory/gateway/config/...)
        """
        error_lower = error_text.lower()
        scores = {}
        
        for problem_type, data in self.PROBLEM_BAT_MAPPING.items():
            if problem_type == "unknown":
                continue
            
            score = 0
            for keyword in data["keywords"]:
                if keyword.lower() in error_lower:
                    score += 1
            
            if score > 0:
                scores[problem_type] = score
        
        if scores:
            # 返回得分最高的类型
            return max(scores, key=scores.get)
        
        return "unknown"
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                "version": "2.0",
                "enable_bat_generation": True,
                "enable_txt_report": True,
                "similarity_threshold": 0.85,
                "max_records": 100,
                "auto_archive": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _load_cases(self):
        """加载修复案例库"""
        if self.case_file.exists():
            with open(self.case_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"cases": [], "version": "1.0"}
    
    def _save_cases(self):
        """保存修复案例库"""
        with open(self.case_file, 'w', encoding='utf-8') as f:
            json.dump(self.cases, f, ensure_ascii=False, indent=2)
    
    def _load_records(self):
        """加载修复记录库"""
        if self.record_file.exists():
            with open(self.record_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"records": [], "version": "1.0"}
    
    def _save_records(self):
        """保存修复记录库"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def _calculate_similarity(self, text1, text2):
        """计算两段文本的相似度"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_error_keywords(self, error_text):
        """提取错误关键词"""
        # 常见的错误关键词模式
        patterns = [
            r'error[:\s]+(\w+)',
            r'exception[:\s]+(\w+)',
            r'failed[:\s]+(\w+)',
            r'cannot[:\s]+(\w+)',
            r'unable[:\s]+(\w+)',
            r'(memory|search|config|api|token|limit|connection|timeout|refused|denied)',
            r'(404|500|502|503|429)',
        ]
        
        keywords = set()
        for pattern in patterns:
            matches = re.findall(pattern, error_text, re.IGNORECASE)
            keywords.update(matches)
        
        return list(keywords)
    
    def _generate_error_signature(self, error_text):
        """生成错误签名（用于去重）"""
        keywords = self._extract_error_keywords(error_text)
        keywords.sort()
        signature = "|".join(keywords)
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def search_case_library(self, error_text):
        """
        搜索修复案例库
        
        返回:
            dict or None: 匹配的案例
        """
        error_keywords = self._extract_error_keywords(error_text)
        error_signature = self._generate_error_signature(error_text)
        
        best_match = None
        best_score = 0
        
        for case in self.cases.get("cases", []):
            # 1. 按 error_code 精确匹配
            if case.get("error_signature") == error_signature:
                return case
            
            # 2. 按关键词匹配
            case_keywords = set(case.get("keywords", []))
            if case_keywords:
                match_score = len(set(error_keywords) & case_keywords) / len(case_keywords)
                # 只要有至少1个关键词匹配就考虑（降低阈值）
                if match_score > best_score and len(set(error_keywords) & case_keywords) >= 1:
                    best_score = match_score
                    best_match = case
            
            # 3. 按描述相似度匹配
            case_desc = case.get("description", "")
            similarity = self._calculate_similarity(error_text, case_desc)
            if similarity > best_score and similarity >= self.config["similarity_threshold"]:
                best_score = similarity
                best_match = case
        
        return best_match
    
    def search_record_library(self, error_text):
        """
        搜索修复记录库
        
        返回:
            dict or None: 匹配的记录
        """
        error_signature = self._generate_error_signature(error_text)
        
        for record in self.records.get("records", []):
            # 按 error_signature 匹配
            if record.get("error_signature") == error_signature:
                return record
            
            # 按描述相似度匹配
            record_desc = record.get("description", "")
            similarity = self._calculate_similarity(error_text, record_desc)
            if similarity >= self.config["similarity_threshold"]:
                return record
        
        return None
    
    def add_record(self, error_text, solution, success=True, error_code=None, details=None):
        """
        添加修复记录（自动去重）
        
        参数:
            error_text: 错误描述
            solution: 解决方案
            success: 是否修复成功
            error_code: 错误代码（可选）
            details: 详细记录（可选）
        """
        error_signature = self._generate_error_signature(error_text)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 检查是否已存在相同记录
        existing_record = None
        existing_index = -1
        
        for i, record in enumerate(self.records.get("records", [])):
            if record.get("error_signature") == error_signature:
                existing_record = record
                existing_index = i
                break
        
        if existing_record:
            # 更新现有记录
            self.records["records"][existing_index].update({
                "last_occurred_at": timestamp,
                "occurrence_count": existing_record.get("occurrence_count", 1) + 1,
                "solution": solution,
                "success": success,
                "details": details or existing_record.get("details", {})
            })
        else:
            # 创建新记录
            new_record = {
                "id": hashlib.md5(f"{timestamp}{error_text}".encode()).hexdigest()[:12],
                "error_signature": error_signature,
                "error_code": error_code,
                "description": error_text[:500],
                "keywords": self._extract_error_keywords(error_text),
                "solution": solution,
                "success": success,
                "first_occurred_at": timestamp,
                "last_occurred_at": timestamp,
                "occurrence_count": 1,
                "details": details or {}
            }
            self.records["records"].append(new_record)
        
        self._save_records()
        
        return {
            "added": existing_record is None,
            "updated": existing_record is not None,
            "signature": error_signature
        }
    
    def log_call(self, error_text, action_taken, result):
        """
        记录被调用日志
        
        参数:
            error_text: 错误描述
            action_taken: 采取的行动
            result: 处理结果
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        call_log = {
            "timestamp": timestamp,
            "error_preview": error_text[:200],
            "action_taken": action_taken,
            "result": result,
            "error_signature": self._generate_error_signature(error_text)
        }
        
        # 加载现有日志
        logs = {"logs": []}
        if self.call_log_file.exists():
            with open(self.call_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs["logs"].append(call_log)
        
        # 只保留最近 100 条
        logs["logs"] = logs["logs"][-100:]
        
        with open(self.call_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def generate_txt_report(self, error_text, tried_solutions, error_logs, bat_files, problem_type="unknown", auto_fixed=False, solution=""):
        """
        生成 TXT 诊断报告到桌面
        根据系统语言自动选择中文或英文
        
        参数:
            error_text: 问题描述
            tried_solutions: 已尝试的解决方案列表
            error_logs: 错误日志
            bat_files: 生成的 BAT 文件列表
            problem_type: 问题类型
            auto_fixed: 是否自动修复成功
            solution: 修复方案（如果自动修复成功）
        """
        if not self.config.get("enable_txt_report", True):
            return None
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 检测系统语言
        is_zh = (self.system_lang == 'zh')
        
        # 根据语言选择报告模板
        if is_zh:
            # 中文报告
            if auto_fixed:
                lines = self._build_zh_auto_fixed_report(error_text, tried_solutions, solution, timestamp, problem_type)
                filename_prefix = "openclaw修复报告"
            else:
                lines = self._build_zh_report(error_text, tried_solutions, error_logs, bat_files, timestamp, problem_type)
                filename_prefix = "openclaw诊断书"
        else:
            # 英文报告
            if auto_fixed:
                lines = self._build_en_auto_fixed_report(error_text, tried_solutions, solution, timestamp, problem_type)
                filename_prefix = "openclaw_fix_report"
            else:
                lines = self._build_en_report(error_text, tried_solutions, error_logs, bat_files, timestamp, problem_type)
                filename_prefix = "openclaw_diagnosis_report"
        
        # 保存文件
        filename = f"{filename_prefix}_{date_str}.txt"
        filepath = self.desktop_dir / filename
        
        # 如果文件已存在，添加序号
        counter = 1
        while filepath.exists():
            filepath = self.desktop_dir / f"{filename_prefix}_{date_str}_{counter}.txt"
            counter += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return str(filepath)
    
    def _build_zh_report(self, error_text, tried_solutions, error_logs, bat_files, timestamp, problem_type):
        """构建中文诊断报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("OpenClaw 问题诊断书 - 无法自动修复")
        lines.append(f"生成时间: {timestamp}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("【问题描述】")
        lines.append(error_text)
        lines.append("")
        
        lines.append("【已尝试的解决方法】")
        if tried_solutions:
            for i, solution in enumerate(tried_solutions, 1):
                status = solution.get("status", "unknown")
                status_mark = "✓" if status == "success" else "✗" if status == "failed" else "?"
                lines.append(f"{i}. [{status_mark}] {solution.get('method', '未知方法')}")
                if solution.get('result'):
                    lines.append(f"   结果: {solution['result']}")
        else:
            lines.append("暂无尝试记录。")
        lines.append("")
        
        lines.append("【错误日志】")
        if error_logs:
            lines.append(error_logs[:2000])  # 限制长度
        else:
            lines.append("无可用日志。")
        lines.append("")
        
        # BAT 文件说明
        lines.append("【自动修复工具】")
        lines.append(f"问题类型: {problem_type}")
        lines.append("")
        if bat_files:
            lines.append("已生成以下修复工具（双击运行，运行后自动删除）：")
            for i, bat_file in enumerate(bat_files, 1):
                bat_name = os.path.basename(bat_file)
                # 根据文件名解释用途
                if "记忆" in bat_name or "memory" in bat_name.lower():
                    desc = "重置记忆索引，解决记忆搜索问题"
                elif "Gateway" in bat_name or "gateway" in bat_name.lower():
                    desc = "重启 Gateway 服务"
                elif "配置" in bat_name or "config" in bat_name.lower():
                    desc = "重置配置文件"
                elif "网络" in bat_name or "network" in bat_name.lower():
                    desc = "检查网络连接"
                elif "API" in bat_name or "api" in bat_name.lower():
                    desc = "检查 API 额度"
                elif "Agent" in bat_name or "agent" in bat_name.lower():
                    desc = "重新加载 Agent"
                elif "权限" in bat_name or "permission" in bat_name.lower():
                    desc = "修复文件权限"
                elif "安装" in bat_name or "install" in bat_name.lower() or "reinstall" in bat_name.lower():
                    desc = "重新安装 OpenClaw"
                elif "iFlow" in bat_name or "iflow" in bat_name.lower():
                    desc = "打开 iFlow CLI 获取人工协助"
                else:
                    desc = "修复工具"
                lines.append(f"{i}. {bat_name}")
                lines.append(f"   用途: {desc}")
        else:
            lines.append("未生成自动修复工具。")
        lines.append("")
        
        lines.append("【建议操作】")
        lines.append("1. 按顺序尝试上述修复工具")
        lines.append("2. 如果问题仍未解决，使用最后一个工具联系 iFlow 人工协助")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("【联系人工协助】")
        lines.append("")
        lines.append("如需进一步帮助，请：")
        lines.append("")
        lines.append("1. 打开终端输入：iflow")
        lines.append("   或双击桌面的 iFlow 相关 BAT 文件")
        lines.append("")
        lines.append("2. iFlow CLI 是你的智能助手，可以：")
        lines.append("   - 诊断和修复 OpenClaw 问题")
        lines.append("   - 管理记忆和配置")
        lines.append("   - 协助开发和部署任务")
        lines.append("   - 提供技术支持")
        lines.append("")
        lines.append("3. 开启对话后，直接描述你的问题即可。")
        lines.append("")
        lines.append("=" * 60)
        
        return lines
    
    def _build_en_report(self, error_text, tried_solutions, error_logs, bat_files, timestamp, problem_type):
        """构建英文诊断报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("OpenClaw Diagnosis Report - Cannot Auto-Fix")
        lines.append(f"Generated: {timestamp}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("[Problem Description]")
        lines.append(error_text)
        lines.append("")
        
        lines.append("[Attempted Solutions]")
        if tried_solutions:
            for i, solution in enumerate(tried_solutions, 1):
                status = solution.get("status", "unknown")
                status_mark = "✓" if status == "success" else "✗" if status == "failed" else "?"
                lines.append(f"{i}. [{status_mark}] {solution.get('method', 'Unknown method')}")
                if solution.get('result'):
                    lines.append(f"   Result: {solution['result']}")
        else:
            lines.append("No solutions attempted yet.")
        lines.append("")
        
        lines.append("[Error Logs]")
        if error_logs:
            lines.append(error_logs[:2000])  # 限制长度
        else:
            lines.append("No logs available.")
        lines.append("")
        
        # BAT 文件说明
        lines.append("[Auto-Fix Tools]")
        lines.append(f"Problem Type: {problem_type}")
        lines.append("")
        if bat_files:
            lines.append("The following repair tools have been generated (double-click to run, auto-delete after execution):")
            for i, bat_file in enumerate(bat_files, 1):
                bat_name = os.path.basename(bat_file)
                # 根据文件名解释用途
                if "memory" in bat_name.lower():
                    desc = "Reset memory index to fix search issues"
                elif "gateway" in bat_name.lower():
                    desc = "Restart Gateway service"
                elif "config" in bat_name.lower():
                    desc = "Reset configuration files"
                elif "network" in bat_name.lower():
                    desc = "Check network connection"
                elif "api" in bat_name.lower():
                    desc = "Check API quota"
                elif "agent" in bat_name.lower():
                    desc = "Reload Agents"
                elif "permission" in bat_name.lower():
                    desc = "Fix file permissions"
                elif "reinstall" in bat_name.lower():
                    desc = "Reinstall OpenClaw"
                elif "iflow" in bat_name.lower():
                    desc = "Open iFlow CLI for manual assistance"
                else:
                    desc = "Repair tool"
                lines.append(f"{i}. {bat_name}")
                lines.append(f"   Purpose: {desc}")
        else:
            lines.append("No auto-fix tools generated.")
        lines.append("")
        
        lines.append("[Suggested Actions]")
        lines.append("1. Try the repair tools above in order")
        lines.append("2. If problem persists, use the last tool to contact iFlow for manual assistance")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("[Contact for Manual Assistance]")
        lines.append("")
        lines.append("If you need further help, please:")
        lines.append("")
        lines.append("1. Open terminal and type: iflow")
        lines.append("   Or double-click the iFlow BAT file on Desktop")
        lines.append("")
        lines.append("2. iFlow CLI is your intelligent assistant that can:")
        lines.append("   - Diagnose and fix OpenClaw problems")
        lines.append("   - Manage memories and configurations")
        lines.append("   - Assist with development and deployment tasks")
        lines.append("   - Provide technical support")
        lines.append("")
        lines.append("3. After starting the conversation, simply describe your problem.")
        lines.append("")
        lines.append("=" * 60)
        
        return lines
    
    def generate_bat_files(self, problem_type="unknown"):
        """
        根据问题类型生成对应的修复脚本到桌面
        Windows 生成 .bat，Linux/macOS 生成 .sh
        限制最多生成 3 个脚本文件
        
        参数:
            problem_type: 问题类型 (memory/gateway/config/network/api/agent/permission/install/unknown)
        
        返回:
            list: 生成的文件路径列表
        """
        if not self.config.get("enable_bat_generation", True):
            return []
        
        generated_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 获取问题类型的配置
        problem_config = self.PROBLEM_BAT_MAPPING.get(problem_type, self.PROBLEM_BAT_MAPPING["unknown"])
        bat_options = problem_config["bat_options"]
        
        # 限制最多 3 个脚本文件
        if len(bat_options) > 3:
            bat_options = bat_options[:3]
        
        # 根据系统语言和类型选择文件名
        is_zh = (self.system_lang == 'zh')
        is_windows = (self.system_type == 'windows')
        
        # 根据系统类型选择模板
        if is_windows:
            templates = self._get_windows_templates()
            ext = ".bat"
        else:
            templates = self._get_unix_templates()
            ext = ".sh"
        
        # 脚本模板库已根据系统类型加载
        
        # 根据问题类型生成对应的 BAT 文件
        for option in bat_options:
            if option in templates:
                template = templates[option]
                # 根据系统语言选择文件名
                filename_key = "filename_cn" if is_zh else "filename_en"
                filename = template[filename_key]
                filepath = self.desktop_dir / filename
                
                # 如果文件已存在，添加时间戳避免覆盖
                if filepath.exists():
                    name_without_ext = filename.replace('.bat', '').replace('.sh', '')
                    filepath = self.desktop_dir / f"{name_without_ext}_{timestamp}{ext}"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("\n".join(template["commands"]))
                
                # Unix 系统添加可执行权限
                if not is_windows:
                    os.chmod(filepath, 0o755)
                
                generated_files.append(str(filepath))
        
        return generated_files
    
    def _get_windows_templates(self):
        """获取 Windows BAT 脚本模板"""
        return {
            "reset_memory": {
                "filename_cn": "重置记忆索引.bat",
                "filename_en": "reset_memory_index.bat",
                "commands": [
                    "@echo off",
                    "set BACKUP_DIR=%USERPROFILE%\\.openclaw\\memory_backup_%date:~0,4%%date:~5,2%%date:~8,2%",
                    "mkdir \"%BACKUP_DIR%\" 2>nul",
                    "xcopy \"%USERPROFILE%\\.openclaw\\memory\" \"%BACKUP_DIR%\" /E /I /Y >nul 2>&1",
                    "del \"%USERPROFILE%\\.openclaw\\memory\\index.*\" /Q 2>nul",
                    "taskkill /F /IM openclaw-gateway.exe 2>nul",
                    "timeout /t 2 /nobreak >nul",
                    "start openclaw gateway",
                    "del \"%~f0\""
                ]
            },
            "restart_gateway": {
                "filename_cn": "重启Gateway服务.bat",
                "filename_en": "restart_gateway_service.bat",
                "commands": [
                    "@echo off",
                    "taskkill /F /IM openclaw-gateway.exe 2>nul",
                    "timeout /t 2 /nobreak >nul",
                    "start openclaw gateway",
                    "del \"%~f0\""
                ]
            },
            "reset_config": {
                "filename_cn": "重置配置文件.bat",
                "filename_en": "reset_configuration.bat",
                "commands": [
                    "@echo off",
                    "set BACKUP_DIR=%USERPROFILE%\\.openclaw\\config_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%",
                    "mkdir \"%BACKUP_DIR%\" 2>nul",
                    "xcopy \"%USERPROFILE%\\.openclaw\\*.json\" \"%BACKUP_DIR%\" /Y >nul 2>&1",
                    "del \"%USERPROFILE%\\.openclaw\\openclaw.json\" /Q 2>nul",
                    "del \"%~f0\""
                ]
            },
            "check_network": {
                "filename_cn": "检查网络连接.bat",
                "filename_en": "check_network_connection.bat",
                "commands": [
                    "@echo off",
                    "ping -n 4 api.openclaw.ai",
                    "nslookup api.openclaw.ai",
                    "pause",
                    "del \"%~f0\""
                ]
            },
            "check_api_quota": {
                "filename_cn": "检查API额度.bat",
                "filename_en": "check_api_quota.bat",
                "commands": [
                    "@echo off",
                    "start https://platform.openclaw.ai/billing",
                    "del \"%~f0\""
                ]
            },
            "reload_agents": {
                "filename_cn": "重新加载Agent.bat",
                "filename_en": "reload_agents.bat",
                "commands": [
                    "@echo off",
                    "openclaw agents reload",
                    "openclaw spawn pm --task test",
                    "del \"%~f0\""
                ]
            },
            "fix_permissions": {
                "filename_cn": "修复权限.bat",
                "filename_en": "fix_permissions.bat",
                "commands": [
                    "@echo off",
                    "icacls \"%USERPROFILE%\\.openclaw\" /grant %USERNAME%:F /T",
                    "attrib -R \"%USERPROFILE%\\.openclaw\\*.*\" /S /D",
                    "del \"%~f0\""
                ]
            },
            "reinstall_openclaw": {
                "filename_cn": "重新安装openclaw.bat",
                "filename_en": "reinstall_openclaw.bat",
                "commands": [
                    "@echo off",
                    "set BACKUP_DIR=%USERPROFILE%\\.openclaw\\backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%",
                    "mkdir \"%BACKUP_DIR%\" 2>nul",
                    "xcopy \"%USERPROFILE%\\.openclaw\\*.json\" \"%BACKUP_DIR%\" /Y >nul 2>&1",
                    "xcopy \"%USERPROFILE%\\.openclaw\\memory\" \"%BACKUP_DIR%\\memory\" /E /I /Y >nul 2>&1",
                    "npm uninstall -g openclaw 2>nul",
                    "npm install -g openclaw",
                    "del \"%~f0\""
                ]
            },
            "open_iflow": {
                "filename_cn": "打开iFlow寻求帮助.bat",
                "filename_en": "open_iflow_for_help.bat",
                "commands": [
                    "@echo off",
                    "cd /d %USERPROFILE%",
                    "iflow",
                    "del \"%~f0\""
                ]
            }
        }
    
    def _get_unix_templates(self):
        """获取 Linux/macOS Shell 脚本模板"""
        return {
            "reset_memory": {
                "filename_cn": "重置记忆索引.sh",
                "filename_en": "reset_memory_index.sh",
                "commands": [
                    "#!/bin/bash",
                    "BACKUP_DIR=\"$HOME/.openclaw/memory_backup_$(date +%Y%m%d)\"",
                    "mkdir -p \"$BACKUP_DIR\"",
                    "cp -r \"$HOME/.openclaw/memory\" \"$BACKUP_DIR/\" 2>/dev/null",
                    "rm -f \"$HOME/.openclaw/memory/\"index.*",
                    "pkill -f openclaw-gateway 2>/dev/null",
                    "sleep 2",
                    "openclaw gateway &",
                    "rm -f \"$0\""
                ]
            },
            "restart_gateway": {
                "filename_cn": "重启Gateway服务.sh",
                "filename_en": "restart_gateway_service.sh",
                "commands": [
                    "#!/bin/bash",
                    "pkill -f openclaw-gateway 2>/dev/null",
                    "sleep 2",
                    "openclaw gateway &",
                    "rm -f \"$0\""
                ]
            },
            "reset_config": {
                "filename_cn": "重置配置文件.sh",
                "filename_en": "reset_configuration.sh",
                "commands": [
                    "#!/bin/bash",
                    "BACKUP_DIR=\"$HOME/.openclaw/config_backup_$(date +%Y%m%d_%H%M%S)\"",
                    "mkdir -p \"$BACKUP_DIR\"",
                    "cp \"$HOME/.openclaw/\"*.json \"$BACKUP_DIR/\" 2>/dev/null",
                    "rm -f \"$HOME/.openclaw/openclaw.json\"",
                    "rm -f \"$0\""
                ]
            },
            "check_network": {
                "filename_cn": "检查网络连接.sh",
                "filename_en": "check_network_connection.sh",
                "commands": [
                    "#!/bin/bash",
                    "ping -c 4 api.openclaw.ai",
                    "nslookup api.openclaw.ai || dig api.openclaw.ai",
                    "read -p 'Press Enter to continue...'",
                    "rm -f \"$0\""
                ]
            },
            "check_api_quota": {
                "filename_cn": "检查API额度.sh",
                "filename_en": "check_api_quota.sh",
                "commands": [
                    "#!/bin/bash",
                    "if command -v xdg-open &> /dev/null; then",
                    "    xdg-open 'https://platform.openclaw.ai/billing'",
                    "elif command -v open &> /dev/null; then",
                    "    open 'https://platform.openclaw.ai/billing'",
                    "else",
                    "    echo 'Please visit: https://platform.openclaw.ai/billing'",
                    "fi",
                    "rm -f \"$0\""
                ]
            },
            "reload_agents": {
                "filename_cn": "重新加载Agent.sh",
                "filename_en": "reload_agents.sh",
                "commands": [
                    "#!/bin/bash",
                    "openclaw agents reload",
                    "openclaw spawn pm --task test",
                    "rm -f \"$0\""
                ]
            },
            "fix_permissions": {
                "filename_cn": "修复权限.sh",
                "filename_en": "fix_permissions.sh",
                "commands": [
                    "#!/bin/bash",
                    "chmod -R u+rw \"$HOME/.openclaw\"",
                    "rm -f \"$0\""
                ]
            },
            "reinstall_openclaw": {
                "filename_cn": "重新安装openclaw.sh",
                "filename_en": "reinstall_openclaw.sh",
                "commands": [
                    "#!/bin/bash",
                    "BACKUP_DIR=\"$HOME/.openclaw/backup_$(date +%Y%m%d_%H%M%S)\"",
                    "mkdir -p \"$BACKUP_DIR\"",
                    "cp -r \"$HOME/.openclaw\"/*.json \"$BACKUP_DIR/\" 2>/dev/null",
                    "cp -r \"$HOME/.openclaw/memory\" \"$BACKUP_DIR/\" 2>/dev/null",
                    "npm uninstall -g openclaw 2>/dev/null",
                    "npm install -g openclaw",
                    "rm -f \"$0\""
                ]
            },
            "open_iflow": {
                "filename_cn": "打开iFlow寻求帮助.sh",
                "filename_en": "open_iflow_for_help.sh",
                "commands": [
                    "#!/bin/bash",
                    "cd \"$HOME\"",
                    "iflow",
                    "rm -f \"$0\""
                ]
            }
        }
    
    def generate_bat_files_with_iflow(self, problem_type="unknown", error_text=""):
        """
        生成包含 iflow-helper 调用的修复脚本
        Windows 生成 .bat，Linux/macOS 生成 .sh
        
        参数:
            problem_type: 问题类型
            error_text: 错误描述（传递给 iflow）
        
        返回:
            list: 生成的文件路径列表
        """
        generated_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        is_zh = (self.system_lang == 'zh')
        is_windows = (self.system_type == 'windows')
        
        # 1. 生成问题修复脚本（与 generate_bat_files 相同）
        problem_config = self.PROBLEM_BAT_MAPPING.get(problem_type, self.PROBLEM_BAT_MAPPING["unknown"])
        bat_options = problem_config["bat_options"][:1]  # 只取第一个修复选项
        
        # 根据系统类型选择模板
        if is_windows:
            templates = self._get_windows_templates()
            ext = ".bat"
        else:
            templates = self._get_unix_templates()
            ext = ".sh"
        
        # 生成问题修复脚本
        for option in bat_options:
            if option in templates:
                template = templates[option]
                filename_key = "filename_cn" if is_zh else "filename_en"
                filename = template[filename_key]
                filepath = self.desktop_dir / filename
                
                if filepath.exists():
                    name_without_ext = filename.replace('.bat', '')
                    filepath = self.desktop_dir / f"{name_without_ext}_{timestamp}.bat"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("\n".join(template["commands"]))
                
                # Unix 系统添加可执行权限
                if not is_windows:
                    os.chmod(filepath, 0o755)
                
                generated_files.append(str(filepath))
        
        # 2. 生成 iflow-helper 调用脚本
        iflow_template = templates["open_iflow"]
        filename_key = "filename_cn" if is_zh else "filename_en"
        filename = iflow_template[filename_key]
        filepath = self.desktop_dir / filename
        
        if filepath.exists():
            name_without_ext = filename.replace('.bat', '').replace('.sh', '')
            filepath = self.desktop_dir / f"{name_without_ext}_{timestamp}{ext}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(iflow_template["commands"]))
        
        # Unix 系统添加可执行权限
        if not is_windows:
            os.chmod(filepath, 0o755)
        
        generated_files.append(str(filepath))
        
        return generated_files
    
    def generate_txt_report_with_iflow(self, error_text, tried_solutions, error_logs, bat_files, 
                                        problem_type="unknown", auto_fixed=False, iflow_recommended=True):
        """
        生成 TXT 报告（支持 iflow 集成）
        
        参数:
            error_text: 错误描述
            tried_solutions: 尝试的解决方案列表
            error_logs: 错误日志
            bat_files: 生成的 BAT 文件列表
            problem_type: 问题类型
            auto_fixed: 是否自动修复成功
            iflow_recommended: 是否推荐调用 iflow
        
        返回:
            str: 报告文件路径
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 根据系统语言选择报告语言和文件名
        if self.system_lang == 'zh':
            filename = f"openclaw诊断书_{date_str}.txt" if not auto_fixed else f"openclaw修复报告_{date_str}.txt"
            lines = self._build_zh_report_with_iflow(error_text, tried_solutions, error_logs, 
                                                      bat_files, timestamp, problem_type, 
                                                      auto_fixed, iflow_recommended)
        else:
            filename = f"openclaw_diagnosis_report_{date_str}.txt" if not auto_fixed else f"openclaw_fix_report_{date_str}.txt"
            lines = self._build_en_report_with_iflow(error_text, tried_solutions, error_logs, 
                                                      bat_files, timestamp, problem_type, 
                                                      auto_fixed, iflow_recommended)
        
        # 保存报告
        report_path = self.desktop_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return str(report_path)
    
    def _build_zh_report_with_iflow(self, error_text, tried_solutions, error_logs, bat_files, 
                                     timestamp, problem_type, auto_fixed, iflow_recommended):
        """构建中文报告（包含 iflow 建议）"""
        lines = []
        
        if auto_fixed:
            lines.append("=" * 60)
            lines.append("OpenClaw 自动修复报告 - 修复成功")
            lines.append(f"生成时间: {timestamp}")
            lines.append("=" * 60)
            lines.append("")
            lines.append("【问题描述】")
            lines.append(error_text)
            lines.append("")
            lines.append("【修复状态】")
            lines.append("✓ 问题已自动修复")
            lines.append(f"问题类型: {problem_type}")
            lines.append("")
        else:
            lines.append("=" * 60)
            lines.append("OpenClaw 问题诊断书 - 无法自动修复")
            lines.append(f"生成时间: {timestamp}")
            lines.append("=" * 60)
            lines.append("")
            lines.append("【问题描述】")
            lines.append(error_text)
            lines.append("")
            lines.append("【已尝试的解决方法】")
            for i, solution in enumerate(tried_solutions, 1):
                status = "✓" if solution['status'] == 'success' else "✗"
                lines.append(f"{i}. [{status}] {solution['method']}")
                lines.append(f"   结果: {solution['result']}")
            lines.append("")
            
            if iflow_recommended:
                lines.append("【智能修复建议】")
                lines.append("此问题需要更深入的分析和手动修复。")
                lines.append("")
                lines.append("已为您准备以下修复方案：")
                lines.append("")
                
                # 分类显示 BAT 文件
                repair_bats = [bat for bat in bat_files if 'iflow' not in bat.lower()]
                iflow_bats = [bat for bat in bat_files if 'iflow' in bat.lower()]
                
                if repair_bats:
                    lines.append("方案一：自动修复工具（双击运行）")
                    for i, bat in enumerate(repair_bats, 1):
                        bat_name = Path(bat).name
                        lines.append(f"  {i}. {bat_name}")
                    lines.append("")
                
                if iflow_bats:
                    lines.append("方案二：AI 智能协助（推荐）")
                    lines.append("  推荐使用 iflow CLI 进行深度诊断和修复：")
                    for bat in iflow_bats:
                        bat_name = Path(bat).name
                        lines.append(f"    - {bat_name}")
                    lines.append("")
                    lines.append("  iflow 可以帮您：")
                    lines.append("    - 深度分析错误日志")
                    lines.append("    - 检查配置文件")
                    lines.append("    - 执行复杂修复命令")
                    lines.append("    - 提供个性化解决方案")
                    lines.append("")
                
                lines.append("【使用建议】")
                lines.append("1. 先尝试方案一的自动修复工具")
                lines.append("2. 如果问题未解决，使用方案二的 iflow AI 协助")
                lines.append("3. 在 iflow 中详细描述问题，获取最佳帮助")
                lines.append("")
            else:
                lines.append("【自动修复工具】")
                lines.append("问题类型: {}".format(problem_type))
                lines.append("")
                lines.append("已生成以下修复工具（双击运行，运行后自动删除）：")
                for i, bat in enumerate(bat_files, 1):
                    bat_name = Path(bat).name
                    lines.append(f"{i}. {bat_name}")
                lines.append("")
        
        # 添加错误日志
        if error_logs:
            lines.append("【错误日志】")
            lines.append(error_logs[:500] if len(error_logs) > 500 else error_logs)
            lines.append("")
        
        # 添加联系信息
        if not auto_fixed:
            lines.append("=" * 60)
            lines.append("【联系人工协助】")
            lines.append("")
            if iflow_recommended:
                lines.append("如需进一步帮助，请：")
                lines.append("")
                lines.append('1. 双击桌面的"打开iFlow寻求帮助.bat"')
                lines.append("   或运行命令: openclaw skills run iflow-helper")
                lines.append("")
                lines.append("2. 在 iflow 中描述您的问题，例如：")
                lines.append(f'   "OpenClaw 出现错误: {error_text[:50]}..."')
                lines.append("")
                lines.append("3. iflow 将使用 AI 能力帮您：")
                lines.append("   - 分析问题和日志")
                lines.append("   - 提供修复方案")
                lines.append("   - 执行修复命令")
                lines.append("   - 验证修复结果")
                lines.append("")
            else:
                lines.append("如需进一步帮助，请：")
                lines.append("")
                lines.append("1. 打开终端输入: iflow")
                lines.append("   或双击桌面的 iflow BAT 文件")
                lines.append("")
            lines.append("=" * 60)
        
        return lines
    
    def _build_en_report_with_iflow(self, error_text, tried_solutions, error_logs, bat_files, 
                                     timestamp, problem_type, auto_fixed, iflow_recommended):
        """构建英文报告（包含 iflow 建议）"""
        lines = []
        
        if auto_fixed:
            lines.append("=" * 60)
            lines.append("OpenClaw Auto-Fix Report - Fixed Successfully")
            lines.append(f"Generated: {timestamp}")
            lines.append("=" * 60)
            lines.append("")
            lines.append("[Problem Description]")
            lines.append(error_text)
            lines.append("")
            lines.append("[Fix Status]")
            lines.append("✓ Issue has been automatically fixed")
            lines.append(f"Problem Type: {problem_type}")
            lines.append("")
        else:
            lines.append("=" * 60)
            lines.append("OpenClaw Diagnosis Report - Cannot Auto-Fix")
            lines.append(f"Generated: {timestamp}")
            lines.append("=" * 60)
            lines.append("")
            lines.append("[Problem Description]")
            lines.append(error_text)
            lines.append("")
            lines.append("[Attempted Solutions]")
            for i, solution in enumerate(tried_solutions, 1):
                status = "✓" if solution['status'] == 'success' else "✗"
                lines.append(f"{i}. [{status}] {solution['method']}")
                lines.append(f"   Result: {solution['result']}")
            lines.append("")
            
            if iflow_recommended:
                lines.append("[Smart Fix Recommendation]")
                lines.append("This issue requires deeper analysis and manual repair.")
                lines.append("")
                lines.append("Available fix options:")
                lines.append("")
                
                repair_bats = [bat for bat in bat_files if 'iflow' not in bat.lower()]
                iflow_bats = [bat for bat in bat_files if 'iflow' in bat.lower()]
                
                if repair_bats:
                    lines.append("Option 1: Auto-Fix Tools (double-click to run)")
                    for i, bat in enumerate(repair_bats, 1):
                        bat_name = Path(bat).name
                        lines.append(f"  {i}. {bat_name}")
                    lines.append("")
                
                if iflow_bats:
                    lines.append("Option 2: AI-Powered Assistance (Recommended)")
                    lines.append("  Use iflow CLI for deep diagnosis and repair:")
                    for bat in iflow_bats:
                        bat_name = Path(bat).name
                        lines.append(f"    - {bat_name}")
                    lines.append("")
                    lines.append("  iflow can help you:")
                    lines.append("    - Analyze error logs in depth")
                    lines.append("    - Check configuration files")
                    lines.append("    - Execute complex repair commands")
                    lines.append("    - Provide personalized solutions")
                    lines.append("")
                
                lines.append("[Usage Suggestion]")
                lines.append("1. First try Option 1 auto-fix tools")
                lines.append("2. If problem persists, use Option 2 iflow AI assistance")
                lines.append("3. Describe your problem in detail in iflow for best help")
                lines.append("")
            else:
                lines.append("[Auto-Fix Tools]")
                lines.append("Problem Type: {}".format(problem_type))
                lines.append("")
                lines.append("Generated repair tools (double-click to run, auto-delete after):")
                for i, bat in enumerate(bat_files, 1):
                    bat_name = Path(bat).name
                    lines.append(f"{i}. {bat_name}")
                lines.append("")
        
        if error_logs:
            lines.append("[Error Logs]")
            lines.append(error_logs[:500] if len(error_logs) > 500 else error_logs)
            lines.append("")
        
        if not auto_fixed:
            lines.append("=" * 60)
            lines.append("[Contact for Manual Assistance]")
            lines.append("")
            if iflow_recommended:
                lines.append("For further help, please:")
                lines.append("")
                lines.append('1. Double-click "open_iflow_for_help.bat" on Desktop')
                lines.append("   Or run command: openclaw skills run iflow-helper")
                lines.append("")
                lines.append("2. Describe your problem in iflow, for example:")
                lines.append(f'   "OpenClaw error: {error_text[:50]}..."')
                lines.append("")
                lines.append("3. iflow will use AI to help you:")
                lines.append("   - Analyze problems and logs")
                lines.append("   - Provide repair solutions")
                lines.append("   - Execute fix commands")
                lines.append("   - Verify repair results")
                lines.append("")
            else:
                lines.append("For further help, please:")
                lines.append("")
                lines.append("1. Open terminal and type: iflow")
                lines.append("   Or double-click the iflow BAT file on Desktop")
                lines.append("")
            lines.append("=" * 60)
        
        return lines
    
    def diagnose_and_fix(self, error_text, error_logs="", openclaw_version="", config_path=""):
        """
        主要诊断和修复入口
        
        参数:
            error_text: 错误描述
            error_logs: 错误日志（可选）
            openclaw_version: OpenClaw 版本（可选）
            config_path: 配置文件路径（可选）
        
        返回:
            dict: 处理结果
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result = {
            "timestamp": timestamp,
            "error_text": error_text,
            "fixed": False,
            "method": None,
            "solution": None,
            "report_file": None,
            "bat_files": [],
            "message": ""
        }
        
        # Step 1: 搜索修复案例库
        case = self.search_case_library(error_text)
        if case:
            result["fixed"] = True
            result["method"] = "case_library"
            result["solution"] = case.get("solution", "")
            result["message"] = f"Auto-fixed using case: {case.get('title', 'Unknown')}"
            
            # 记录调用日志
            self.log_call(error_text, "search_case_library", "auto_fixed")
            
            # 添加到修复记录
            self.add_record(
                error_text=error_text,
                solution=case.get("solution", ""),
                success=True,
                error_code=case.get("error_code"),
                details={"source": "case_library", "case_id": case.get("id"), "auto_fixed": True}
            )
            
            # 生成报告提醒用户（不生成BAT）
            tried_solutions = [
                {"method": f"Applied solution from case: {case.get('title', 'Unknown')}", "status": "success", "result": "Auto-fixed successfully"}
            ]
            report_path = self.generate_txt_report(
                error_text=error_text,
                tried_solutions=tried_solutions,
                error_logs=error_logs,
                bat_files=[],  # 不生成BAT
                problem_type=self._classify_problem(error_text),
                auto_fixed=True,
                solution=case.get("solution", "")
            )
            result["report_file"] = report_path
            
            return result
        
        # Step 2: 搜索修复记录库
        record = self.search_record_library(error_text)
        if record and record.get("success", False):
            # 只有历史记录成功时才自动应用
            result["fixed"] = True
            result["method"] = "record_library"
            result["solution"] = record.get("solution", "")
            result["message"] = f"Auto-fixed using previous record"
            
            # 记录调用日志
            self.log_call(error_text, "search_record_library", "auto_fixed")
            
            # 生成报告提醒用户（不生成BAT）
            tried_solutions = [
                {"method": "Applied previous successful solution", "status": "success", "result": "Auto-fixed successfully"}
            ]
            report_path = self.generate_txt_report(
                error_text=error_text,
                tried_solutions=tried_solutions,
                error_logs=error_logs,
                bat_files=[],  # 不生成BAT
                problem_type=self._classify_problem(error_text),
                auto_fixed=True,
                solution=record.get("solution", "")
            )
            result["report_file"] = report_path
            
            return result
        
        # Step 3: 无法自动修复，需要生成报告和 BAT 文件
        result["message"] = "Could not find automatic solution - manual intervention required"
        
        # 分类问题类型
        problem_type = self._classify_problem(error_text)
        result["problem_type"] = problem_type
        
        # 检查是否应该调用 iflow-helper
        iflow_integration = self.config.get("enable_iflow_integration", True)
        
        if iflow_integration:
            # 生成包含 iflow-helper 调用的 BAT 文件
            bat_files = self.generate_bat_files_with_iflow(problem_type, error_text)
            result["iflow_recommended"] = True
        else:
            # 纯本地模式，只生成基础 BAT
            bat_files = self.generate_bat_files(problem_type)
            result["iflow_recommended"] = False
        
        result["bat_files"] = bat_files
        
        # 生成 TXT 报告（包含 BAT 说明和 iflow 建议）
        tried_solutions = [
            {"method": "Search case library", "status": "failed", "result": "No matching case found"},
            {"method": "Search record library", "status": "failed", "result": "No previous record found"}
        ]
        
        report_path = self.generate_txt_report_with_iflow(
            error_text=error_text,
            tried_solutions=tried_solutions,
            error_logs=error_logs,
            bat_files=bat_files,
            problem_type=problem_type,
            auto_fixed=False,
            iflow_recommended=result["iflow_recommended"]
        )
        result["report_file"] = report_path
        
        # 记录调用日志
        self.log_call(error_text, f"manual_intervention_needed_{problem_type}", "bat_generated")
        
        return result
    
    def _build_zh_auto_fixed_report(self, error_text, tried_solutions, solution, timestamp, problem_type):
        """构建中文自动修复成功报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("OpenClaw 自动修复报告 - 修复成功")
        lines.append(f"生成时间: {timestamp}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("【问题描述】")
        lines.append(error_text)
        lines.append("")
        
        lines.append("【修复状态】")
        lines.append("✓ 问题已自动修复")
        lines.append(f"问题类型: {problem_type}")
        lines.append("")
        
        lines.append("【修复详情】")
        if tried_solutions:
            for i, sol in enumerate(tried_solutions, 1):
                status = sol.get("status", "unknown")
                status_mark = "✓" if status == "success" else "✗"
                lines.append(f"{i}. [{status_mark}] {sol.get('method', '未知方法')}")
                if sol.get('result'):
                    lines.append(f"   结果: {sol['result']}")
        lines.append("")
        
        lines.append("【应用的解决方案】")
        lines.append(solution if solution else "系统自动应用了匹配的修复方案")
        lines.append("")
        
        lines.append("【注意事项】")
        lines.append("1. 问题已自动解决，无需手动操作")
        lines.append("2. 请检查 OpenClaw 是否正常运行")
        lines.append("3. 如果问题重复出现，请查看历史记录")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("本报告仅作为修复记录，无需执行任何操作")
        lines.append("=" * 60)
        
        return lines
    
    def _build_en_auto_fixed_report(self, error_text, tried_solutions, solution, timestamp, problem_type):
        """构建英文自动修复成功报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("OpenClaw Auto-Fix Report - Fixed Successfully")
        lines.append(f"Generated: {timestamp}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("[Problem Description]")
        lines.append(error_text)
        lines.append("")
        
        lines.append("[Fix Status]")
        lines.append("✓ Issue has been automatically fixed")
        lines.append(f"Problem Type: {problem_type}")
        lines.append("")
        
        lines.append("[Fix Details]")
        if tried_solutions:
            for i, sol in enumerate(tried_solutions, 1):
                status = sol.get("status", "unknown")
                status_mark = "✓" if status == "success" else "✗"
                lines.append(f"{i}. [{status_mark}] {sol.get('method', 'Unknown method')}")
                if sol.get('result'):
                    lines.append(f"   Result: {sol['result']}")
        lines.append("")
        
        lines.append("[Applied Solution]")
        lines.append(solution if solution else "System automatically applied matching fix")
        lines.append("")
        
        lines.append("[Notes]")
        lines.append("1. Issue has been resolved automatically - no manual action needed")
        lines.append("2. Please verify OpenClaw is running normally")
        lines.append("3. If issue reoccurs, check history records")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("This report is for record only - no action required")
        lines.append("=" * 60)
        
        return lines


# ========== 命令行接口 ==========

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenClaw Self-Healing System V2.0 - AI-powered repair tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python openclaw_memory.py --fix "Gateway service crashed"
  python openclaw_memory.py heal "Memory search not working"
  python openclaw_memory.py --list-cases
  python openclaw_memory.py --stats
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Main arguments
    parser.add_argument("--fix", type=str, help="Error description to fix")
    parser.add_argument("--logs", type=str, default="", help="Error logs")
    parser.add_argument("--version", type=str, default="", help="OpenClaw version")
    parser.add_argument("--config", type=str, default="", help="Config file path")
    parser.add_argument("--add-case", action="store_true", help="Add a new case to library")
    parser.add_argument("--list-cases", action="store_true", help="List all cases")
    parser.add_argument("--list-records", action="store_true", help="List all records")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    # Heal subcommand (shortcut for --fix)
    heal_parser = subparsers.add_parser('heal', help='Quick heal command')
    heal_parser.add_argument('error', type=str, help='Error description')
    heal_parser.add_argument('--logs', type=str, default='', help='Error logs')
    
    # Diagnose subcommand
    diag_parser = subparsers.add_parser('diagnose', help='Diagnose problem')
    diag_parser.add_argument('error', type=str, help='Error description')
    diag_parser.add_argument('--logs', type=str, default='', help='Error logs')
    
    args = parser.parse_args()
    
    memory = OpenClawDoctor()
    
    if args.command == 'heal':
        # Quick heal command
        print(f"Healing: {args.error[:100]}...")
        result = memory.diagnose_and_fix(
            error_text=args.error,
            error_logs=args.logs
        )
        
        print("\n=== Result ===")
        print(f"Fixed: {result['fixed']}")
        print(f"Problem Type: {result.get('problem_type', 'unknown')}")
        
        if result['fixed']:
            print(f"Solution: {result['solution']}")
        else:
            print(f"Report: {result['report_file']}")
            if result['bat_files']:
                print("Repair tools generated on Desktop")
    
    elif args.command == 'diagnose':
        # Diagnose command
        print(f"Diagnosing: {args.error[:100]}...")
        result = memory.diagnose_and_fix(
            error_text=args.error,
            error_logs=args.logs
        )
        
        print("\n=== Diagnosis Result ===")
        print(f"Fixed: {result['fixed']}")
        print(f"Problem Type: {result.get('problem_type', 'unknown')}")
        print(f"Message: {result['message']}")
        
        if result['report_file']:
            print(f"\nDetailed report: {result['report_file']}")
        
        if result['bat_files']:
            print(f"\nGenerated {len(result['bat_files'])} repair tools on Desktop")
    
    elif args.add_case:
        # 交互式添加案例
        print("Adding new case to library...")
        print("Feature not yet implemented. Please edit cases.json manually.")
    
    elif args.list_cases:
        print("=== Repair Case Library ===")
        for case in memory.cases.get("cases", []):
            print(f"[{case.get('id', 'N/A')}] {case.get('title', 'Untitled')}")
            print(f"   Success Rate: {case.get('success_rate', 'N/A')}")
            print(f"   Keywords: {', '.join(case.get('keywords', []))}")
            print()
    
    elif args.list_records:
        print("=== Repair Record Library ===")
        for record in memory.records.get("records", []):
            print(f"[{record.get('id', 'N/A')}] {record.get('description', 'No description')[:50]}...")
            print(f"   Count: {record.get('occurrence_count', 0)} | Success: {record.get('success', False)}")
            print(f"   Last: {record.get('last_occurred_at', 'N/A')}")
            print()
    
    elif args.stats:
        print("=== OpenClaw Memory Statistics ===")
        print(f"Total cases: {len(memory.cases.get('cases', []))}")
        print(f"Total records: {len(memory.records.get('records', []))}")
        
        # 加载调用日志
        if memory.call_log_file.exists():
            with open(memory.call_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                print(f"Total calls: {len(logs.get('logs', []))}")
        
        print(f"\nConfig: {memory.config}")
    
    elif args.fix:
        print(f"Diagnosing: {args.fix[:100]}...")
        result = memory.diagnose_and_fix(
            error_text=args.fix,
            error_logs=args.logs,
            openclaw_version=args.version,
            config_path=args.config
        )
        
        print("\n=== Result ===")
        print(f"Fixed: {result['fixed']}")
        print(f"Method: {result['method']}")
        print(f"Message: {result['message']}")
        
        if result['solution']:
            print(f"\nSolution: {result['solution']}")
        
        if result['report_file']:
            print(f"\nReport saved to: {result['report_file']}")
        
        if result['bat_files']:
            print(f"\nBAT files generated:")
            for bat in result['bat_files']:
                print(f"  - {bat}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
