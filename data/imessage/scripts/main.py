#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iMessage Skill for OpenClaw - 安全增强版
通过 AppleScript 实现 iMessage 消息的发送和接收
包含可信名单、发送确认、接收消息控制 OpenClaw 等安全机制
"""

import subprocess
import sys
import json
import sqlite3
import os
import hashlib
import getpass
import re
import time
import threading
from datetime import datetime
from pathlib import Path


class SecurityManager:
    """安全管理器 - 处理可信名单、发送确认和接收消息控制"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.config_path = os.path.join(skill_path, 'config.json')
        self.security_log_path = os.path.join(skill_path, 'security.log')
        self.control_log_path = os.path.join(skill_path, 'control.log')
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                'trusted_contacts': [],
                'admin_contacts': [],  # 管理员联系人（可控制 OpenClaw）
                'require_confirmation': True,
                'max_daily_messages': 100,
                'enable_logging': True,
                'enable_remote_control': False,  # 是否启用远程控制
                'allowed_commands': ['status', 'help', 'list', 'info'],  # 允许的命令
                'blocked_commands': ['delete', 'rm', 'remove', 'uninstall'],  # 禁止的命令
                'command_prefix': '!'  # 命令前缀
            }
            self._save_config()
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _log_security_event(self, event: str, details: dict = None):
        """记录安全事件"""
        if not self.config.get('enable_logging', True):
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = getpass.getuser()
        log_entry = {
            'timestamp': timestamp,
            'user': user,
            'event': event,
            'details': details or {}
        }
        
        with open(self.security_log_path, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _log_control_event(self, event: str, details: dict = None):
        """记录控制事件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'event': event,
            'details': details or {}
        }
        
        with open(self.control_log_path, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def is_trusted_contact(self, phone: str) -> bool:
        """检查联系人是否在可信名单中"""
        trusted = self.config.get('trusted_contacts', [])
        return phone in trusted
    
    def is_admin_contact(self, phone: str) -> bool:
        """检查联系人是否是管理员"""
        admins = self.config.get('admin_contacts', [])
        return phone in admins
    
    def add_trusted_contact(self, phone: str) -> dict:
        """添加可信联系人"""
        if not phone:
            return {'success': False, 'error': '手机号不能为空'}
        
        trusted = self.config.get('trusted_contacts', [])
        if phone in trusted:
            return {'success': False, 'error': f'{phone} 已在可信名单中'}
        
        trusted.append(phone)
        self.config['trusted_contacts'] = trusted
        self._save_config()
        
        self._log_security_event('ADD_TRUSTED_CONTACT', {'phone': phone})
        
        return {
            'success': True,
            'message': f'已添加 {phone} 到可信名单',
            'trusted_count': len(trusted)
        }
    
    def remove_trusted_contact(self, phone: str) -> dict:
        """移除可信联系人"""
        trusted = self.config.get('trusted_contacts', [])
        if phone not in trusted:
            return {'success': False, 'error': f'{phone} 不在可信名单中'}
        
        trusted.remove(phone)
        self.config['trusted_contacts'] = trusted
        self._save_config()
        
        self._log_security_event('REMOVE_TRUSTED_CONTACT', {'phone': phone})
        
        return {
            'success': True,
            'message': f'已从可信名单移除 {phone}',
            'trusted_count': len(trusted)
        }
    
    def add_admin_contact(self, phone: str) -> dict:
        """添加管理员联系人"""
        if not phone:
            return {'success': False, 'error': '手机号不能为空'}
        
        admins = self.config.get('admin_contacts', [])
        if phone in admins:
            return {'success': False, 'error': f'{phone} 已是管理员'}
        
        admins.append(phone)
        self.config['admin_contacts'] = admins
        self._save_config()
        
        self._log_security_event('ADD_ADMIN_CONTACT', {'phone': phone})
        
        return {
            'success': True,
            'message': f'已添加 {phone} 为管理员',
            'admin_count': len(admins)
        }
    
    def remove_admin_contact(self, phone: str) -> dict:
        """移除管理员"""
        admins = self.config.get('admin_contacts', [])
        if phone not in admins:
            return {'success': False, 'error': f'{phone} 不是管理员'}
        
        admins.remove(phone)
        self.config['admin_contacts'] = admins
        self._save_config()
        
        self._log_security_event('REMOVE_ADMIN_CONTACT', {'phone': phone})
        
        return {
            'success': True,
            'message': f'已移除 {phone} 的管理员权限',
            'admin_count': len(admins)
        }
    
    def list_trusted_contacts(self) -> dict:
        """列出所有可信联系人"""
        trusted = self.config.get('trusted_contacts', [])
        admins = self.config.get('admin_contacts', [])
        return {
            'success': True,
            'trusted_contacts': trusted,
            'admin_contacts': admins,
            'trusted_count': len(trusted),
            'admin_count': len(admins),
            'require_confirmation': self.config.get('require_confirmation', True),
            'enable_remote_control': self.config.get('enable_remote_control', False)
        }
    
    def check_daily_limit(self) -> bool:
        """检查每日发送限制"""
        max_daily = self.config.get('max_daily_messages', 100)
        
        today = datetime.now().strftime('%Y-%m-%d')
        count = 0
        
        if os.path.exists(self.security_log_path):
            with open(self.security_log_path, 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        if log.get('event') == 'SEND_MESSAGE':
                            if log.get('timestamp', '').startswith(today):
                                count += 1
                    except:
                        continue
        
        return count < max_daily
    
    def confirm_send(self, phone: str, message: str) -> bool:
        """发送前确认（命令行交互）"""
        if not self.config.get('require_confirmation', True):
            return True
        
        if self.is_trusted_contact(phone):
            return True
        
        print(f"\n⚠️  安全警告", file=sys.stderr)
        print(f"您正在向非可信联系人发送消息:", file=sys.stderr)
        print(f"  接收者: {phone}", file=sys.stderr)
        print(f"  消息内容: {message[:50]}{'...' if len(message) > 50 else ''}", file=sys.stderr)
        print(f"\n是否继续发送? (yes/no): ", file=sys.stderr, end='')
        
        try:
            response = input().strip().lower()
            return response in ['yes', 'y', '是']
        except:
            return False
    
    def authorize_send(self, phone: str, message: str) -> dict:
        """授权发送检查"""
        if not self.check_daily_limit():
            return {
                'success': False,
                'error': '已达到每日发送限制，请明天再试',
                'code': 'DAILY_LIMIT_EXCEEDED'
            }
        
        is_trusted = self.is_trusted_contact(phone)
        
        if not is_trusted:
            if sys.stdin.isatty():
                if not self.confirm_send(phone, message):
                    self._log_security_event('SEND_DENIED', {'phone': phone, 'reason': 'user_cancelled'})
                    return {
                        'success': False,
                        'error': '用户取消了发送',
                        'code': 'USER_CANCELLED'
                    }
            else:
                return {
                    'success': False,
                    'error': f'{phone} 不在可信名单中，无法自动发送',
                    'code': 'NOT_TRUSTED',
                    'suggestion': '请先将该联系人添加到可信名单: python3 main.py trust phone=xxx'
                }
        
        return {'success': True, 'authorized': True}
    
    def parse_control_command(self, message: str) -> dict:
        """解析控制命令"""
        prefix = self.config.get('command_prefix', '!')
        
        if not message.startswith(prefix):
            return None
        
        command_text = message[len(prefix):].strip()
        parts = command_text.split()
        
        if not parts:
            return None
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return {
            'command': command,
            'args': args,
            'raw': command_text
        }
    
    def validate_control_command(self, phone: str, command: dict) -> dict:
        """验证控制命令权限"""
        # 检查是否启用远程控制
        if not self.config.get('enable_remote_control', False):
            return {
                'success': False,
                'error': '远程控制功能未启用',
                'code': 'REMOTE_CONTROL_DISABLED'
            }
        
        # 检查是否是管理员
        if not self.is_admin_contact(phone):
            return {
                'success': False,
                'error': '您没有权限控制 OpenClaw',
                'code': 'NOT_ADMIN'
            }
        
        cmd = command['command']
        
        # 检查禁止的命令
        blocked = self.config.get('blocked_commands', [])
        if cmd in blocked:
            self._log_security_event('BLOCKED_COMMAND_ATTEMPT', {
                'phone': phone,
                'command': cmd
            })
            return {
                'success': False,
                'error': f'命令 "{cmd}" 被禁止执行',
                'code': 'COMMAND_BLOCKED'
            }
        
        # 检查允许的命令
        allowed = self.config.get('allowed_commands', [])
        if allowed and cmd not in allowed:
            return {
                'success': False,
                'error': f'命令 "{cmd}" 不在允许列表中',
                'code': 'COMMAND_NOT_ALLOWED'
            }
        
        return {'success': True, 'authorized': True}
    
    def execute_control_command(self, command: dict) -> dict:
        """执行控制命令"""
        cmd = command['command']
        args = command['args']
        
        try:
            if cmd == 'status':
                return self._cmd_status()
            elif cmd == 'help':
                return self._cmd_help()
            elif cmd == 'list':
                return self._cmd_list()
            elif cmd == 'info':
                return self._cmd_info()
            elif cmd == 'echo':
                return {'success': True, 'message': ' '.join(args)}
            else:
                return {
                    'success': False,
                    'error': f'未知命令: {cmd}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行命令失败: {str(e)}'
            }
    
    def _cmd_status(self) -> dict:
        """获取 OpenClaw 状态"""
        try:
            result = subprocess.run(
                ['openclaw', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': True,
                'message': 'OpenClaw 状态',
                'output': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _cmd_help(self) -> dict:
        """显示帮助信息"""
        allowed = self.config.get('allowed_commands', [])
        prefix = self.config.get('command_prefix', '!')
        
        help_text = f"""
可用命令（前缀: {prefix}）:
{prefix}status - 查看 OpenClaw 状态
{prefix}help - 显示此帮助
{prefix}list - 列出已安装的 skills
{prefix}info - 显示系统信息
{prefix}echo <消息> - 回显消息

管理员: {', '.join(self.config.get('admin_contacts', []))}
        """.strip()
        
        return {
            'success': True,
            'message': help_text
        }
    
    def _cmd_list(self) -> dict:
        """列出 skills"""
        try:
            result = subprocess.run(
                ['npx', 'clawhub', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'success': True,
                'message': '已安装的 Skills',
                'output': result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _cmd_info(self) -> dict:
        """显示系统信息"""
        return {
            'success': True,
            'message': '系统信息',
            'info': {
                'remote_control_enabled': self.config.get('enable_remote_control', False),
                'trusted_contacts_count': len(self.config.get('trusted_contacts', [])),
                'admin_contacts_count': len(self.config.get('admin_contacts', [])),
                'allowed_commands': self.config.get('allowed_commands', []),
                'blocked_commands': self.config.get('blocked_commands', [])
            }
        }


class iMessageController:
    """iMessage 控制器"""
    
    def __init__(self, skill_path: str):
        self.chat_db_path = os.path.expanduser("~/Library/Messages/chat.db")
        self.security = SecurityManager(skill_path)
    
    def send_message(self, phone: str, message: str, force: bool = False):
        """发送 iMessage 消息（带安全检查）"""
        try:
            if not force:
                auth_result = self.security.authorize_send(phone, message)
                if not auth_result['success']:
                    return auth_result
            
            applescript = f'''
            tell application "Messages"
                set targetService to 1st service whose service type = iMessage
                set targetBuddy to buddy "{phone}" of targetService
                send "{message}" to targetBuddy
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.security._log_security_event('SEND_MESSAGE', {
                    'phone': phone,
                    'message_length': len(message),
                    'trusted': self.security.is_trusted_contact(phone)
                })
                
                return {
                    'success': True,
                    'message': f'消息已发送给 {phone}',
                    'content': message,
                    'trusted': self.security.is_trusted_contact(phone)
                }
            else:
                return {
                    'success': False,
                    'error': f'发送失败: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '发送超时'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_image(self, phone: str, image_path: str):
        """发送图片（带安全检查）"""
        try:
            if not os.path.exists(image_path):
                return {'success': False, 'error': f'图片不存在: {image_path}'}
            
            auth_result = self.security.authorize_send(phone, f"[图片] {image_path}")
            if not auth_result['success']:
                return auth_result
            
            applescript = f'''
            tell application "Messages"
                set targetService to 1st service whose service type = iMessage
                set targetBuddy to buddy "{phone}" of targetService
                set theImage to POSIX file "{image_path}"
                send theImage to targetBuddy
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.security._log_security_event('SEND_IMAGE', {
                    'phone': phone,
                    'image': image_path,
                    'trusted': self.security.is_trusted_contact(phone)
                })
                
                return {
                    'success': True,
                    'message': f'图片已发送给 {phone}',
                    'image': image_path,
                    'trusted': self.security.is_trusted_contact(phone)
                }
            else:
                return {
                    'success': False,
                    'error': f'发送失败: {result.stderr}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_recent_messages(self, phone: str = "", limit: int = 10, check_control: bool = False):
        """获取最近的消息
        
        Args:
            phone: 指定联系人
            limit: 返回消息数量
            check_control: 是否检查控制命令
        """
        try:
            if not os.path.exists(self.chat_db_path):
                return {
                    'success': False,
                    'error': '无法访问 Messages 数据库，请检查权限'
                }
            
            conn = sqlite3.connect(self.chat_db_path)
            cursor = conn.cursor()
            
            if phone:
                query = """
                SELECT 
                    m.text,
                    m.date,
                    m.is_from_me,
                    h.id as phone
                FROM message m
                JOIN handle h ON m.handle_id = h.ROWID
                WHERE h.id = ?
                ORDER BY m.date DESC
                LIMIT ?
                """
                cursor.execute(query, (phone, limit))
            else:
                query = """
                SELECT 
                    m.text,
                    m.date,
                    m.is_from_me,
                    h.id as phone
                FROM message m
                JOIN handle h ON m.handle_id = h.ROWID
                ORDER BY m.date DESC
                LIMIT ?
                """
                cursor.execute(query, (limit,))
            
            messages = []
            control_results = []
            
            for row in cursor.fetchall():
                text, date, is_from_me, phone_num = row
                apple_epoch = datetime(2001, 1, 1)
                msg_time = apple_epoch.timestamp() + date
                msg_datetime = datetime.fromtimestamp(msg_time)
                
                msg_data = {
                    'text': text,
                    'time': msg_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'from_me': bool(is_from_me),
                    'phone': phone_num
                }
                
                # 检查是否是控制命令
                if check_control and not is_from_me and text:
                    command = self.security.parse_control_command(text)
                    if command:
                        # 验证并执行命令
                        validation = self.security.validate_control_command(phone_num, command)
                        if validation['success']:
                            result = self.security.execute_control_command(command)
                            control_results.append({
                                'phone': phone_num,
                                'command': command['command'],
                                'result': result
                            })
                            
                            # 发送回复
                            if result.get('success'):
                                reply = result.get('message', '命令执行成功')
                                if 'output' in result:
                                    reply += f"\n{result['output'][:500]}"
                            else:
                                reply = f"命令执行失败: {result.get('error', '未知错误')}"
                            
                            self.send_message(phone_num, reply, force=True)
                        else:
                            # 权限不足，发送错误信息
                            self.send_message(
                                phone_num, 
                                f"权限错误: {validation.get('error', '无法执行命令')}",
                                force=True
                            )
                
                messages.append(msg_data)
            
            conn.close()
            
            result = {
                'success': True,
                'messages': messages,
                'count': len(messages)
            }
            
            if control_results:
                result['control_executed'] = control_results
            
            return result
            
        except sqlite3.Error as e:
            return {
                'success': False,
                'error': f'数据库错误: {str(e)}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_contacts(self, limit: int = 20):
        """获取最近的联系人列表"""
        try:
            if not os.path.exists(self.chat_db_path):
                return {
                    'success': False,
                    'error': '无法访问 Messages 数据库'
                }
            
            conn = sqlite3.connect(self.chat_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT DISTINCT
                h.id,
                MAX(m.date) as last_date
            FROM handle h
            JOIN message m ON h.ROWID = m.handle_id
            GROUP BY h.id
            ORDER BY last_date DESC
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            
            contacts = []
            for row in cursor.fetchall():
                phone, last_date = row
                apple_epoch = datetime(2001, 1, 1)
                last_time = apple_epoch.timestamp() + last_date
                last_datetime = datetime.fromtimestamp(last_time)
                
                is_trusted = self.security.is_trusted_contact(phone)
                is_admin = self.security.is_admin_contact(phone)
                
                contacts.append({
                    'phone': phone,
                    'last_message_time': last_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'trusted': is_trusted,
                    'admin': is_admin
                })
            
            conn.close()
            
            return {
                'success': True,
                'contacts': contacts,
                'count': len(contacts)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def enable_remote_control(self, enable: bool = True) -> dict:
        """启用/禁用远程控制"""
        self.security.config['enable_remote_control'] = enable
        self.security._save_config()
        
        status = "启用" if enable else "禁用"
        self.security._log_security_event(f'REMOTE_CONTROL_{status.upper()}')
        
        return {
            'success': True,
            'message': f'远程控制已{status}',
            'enabled': enable
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': '请指定操作: send, send_image, recent, contacts, trust, untrust, list_trusted, admin, unadmin, enable_control, disable_control'
        }, ensure_ascii=False))
        return
    
    action = sys.argv[1]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.dirname(script_dir)
    
    controller = iMessageController(skill_path)
    security = controller.security
    
    params = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            params[key] = value
    
    if action == 'send':
        result = controller.send_message(
            phone=params.get('phone', ''),
            message=params.get('message', ''),
            force=params.get('force', '').lower() == 'true'
        )
    elif action == 'send_image':
        result = controller.send_image(
            phone=params.get('phone', ''),
            image_path=params.get('image', '')
        )
    elif action == 'recent':
        result = controller.get_recent_messages(
            phone=params.get('phone', ''),
            limit=int(params.get('limit', 10)),
            check_control=params.get('check_control', '').lower() == 'true'
        )
    elif action == 'contacts':
        result = controller.list_contacts(
            limit=int(params.get('limit', 20))
        )
    elif action == 'trust':
        result = security.add_trusted_contact(params.get('phone', ''))
    elif action == 'untrust':
        result = security.remove_trusted_contact(params.get('phone', ''))
    elif action == 'list_trusted':
        result = security.list_trusted_contacts()
    elif action == 'admin':
        result = security.add_admin_contact(params.get('phone', ''))
    elif action == 'unadmin':
        result = security.remove_admin_contact(params.get('phone', ''))
    elif action == 'enable_control':
        result = controller.enable_remote_control(True)
    elif action == 'disable_control':
        result = controller.enable_remote_control(False)
    else:
        result = {'success': False, 'error': f'未知操作: {action}'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
