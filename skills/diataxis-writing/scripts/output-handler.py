#!/usr/bin/env python3
"""
输出方式处理工具

检测可用工具，推荐输出平台，执行输出操作。

使用方法:
    python3 output-handler.py --detect              # 检测可用工具
    python3 output-handler.py --recommend           # 生成推荐
    python3 output-handler.py --output feishu       # 输出到飞书
    python3 output-handler.py --output local        # 输出到本地
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class OutputHandler:
    """输出方式处理器"""
    
    def __init__(self):
        self.available_tools = {}
        self.mcp_config_path = "/root/config/mcporter.json"
    
    def detect_tools(self) -> Dict[str, dict]:
        """检测可用的输出工具"""
        tools = {}
        
        # 检测内置工具
        tools['chat'] = {
            'name': 'Chat Response',
            'type': 'builtin',
            'status': 'available',
            'configured': True,
        }
        
        tools['local'] = {
            'name': '本地 Markdown 文件',
            'type': 'builtin',
            'status': 'available',
            'configured': True,
            'default_path': '/root/.openclaw/workspace/docs/',
        }
        
        # 检测 MCP 服务器
        mcp_servers = self._detect_mcp_servers()
        
        # 检查飞书 MCP（优先使用 MCP 方式）
        if 'feishu' in mcp_servers:
            feishu_configured = self._check_feishu_mcp()
            tools['feishu'] = {
                'name': '飞书文档 (MCP)',
                'type': 'mcp',
                'status': 'available' if feishu_configured else 'unavailable',
                'configured': feishu_configured,
                'server': 'feishu',
                'method': 'mcporter',
                'capabilities': ['doc.create', 'doc.update', 'wiki.create'],
            }
        
        if 'github' in mcp_servers:
            tools['github'] = {
                'name': 'GitHub Repo',
                'type': 'mcp',
                'status': 'available',
                'configured': True,
                'server': 'github',
                'capabilities': ['repos.createFile', 'repos.updateFile'],
            }
        
        if 'notion' in mcp_servers:
            tools['notion'] = {
                'name': 'Notion',
                'type': 'mcp',
                'status': 'available',
                'configured': True,
                'server': 'notion',
            }
        
        # 检测 git 是否可用
        if self._check_git():
            if 'github' not in tools:
                tools['github_git'] = {
                    'name': 'GitHub (git 命令)',
                    'type': 'git',
                    'status': 'available',
                    'configured': True,
                }
        
        self.available_tools = tools
        return tools
    
    def _check_feishu_mcp(self) -> bool:
        """检查飞书 MCP 是否可用"""
        try:
            # 检查 mcporter.json 配置
            if os.path.exists(self.mcp_config_path):
                with open(self.mcp_config_path, 'r') as f:
                    config = json.load(f)
                    mcp_servers = config.get('mcpServers', {})
                    if 'feishu' in mcp_servers:
                        feishu_config = mcp_servers['feishu']
                        # 检查是否有 baseUrl 或 command
                        if 'baseUrl' in feishu_config or 'command' in feishu_config:
                            return True
            return False
        except Exception as e:
            print(f"检查飞书 MCP 配置失败：{e}")
            return False
    
    def _detect_mcp_servers(self) -> List[str]:
        """检测已配置的 MCP 服务器"""
        servers = []
        
        try:
            if os.path.exists(self.mcp_config_path):
                with open(self.mcp_config_path, 'r') as f:
                    config = json.load(f)
                    mcp_servers = config.get('mcpServers', {})
                    servers = list(mcp_servers.keys())
        except Exception as e:
            print(f"读取 MCP 配置失败：{e}")
        
        return servers
    
    def _check_git(self) -> bool:
        """检查 git 是否可用"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, 
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def generate_recommendations(self, context: str = '') -> List[str]:
        """基于场景生成推荐"""
        recommendations = []
        
        # 按优先级排序
        priority_order = ['feishu', 'local', 'github', 'notion', 'chat']
        
        for tool_id in priority_order:
            if tool_id in self.available_tools:
                tool = self.available_tools[tool_id]
                if tool['configured']:
                    recommendations.append(tool_id)
        
        return recommendations
    
    def print_status(self):
        """打印工具状态"""
        print("\n" + "="*60)
        print("可用输出工具检测")
        print("="*60 + "\n")
        
        if not self.available_tools:
            self.detect_tools()
        
        for tool_id, tool in self.available_tools.items():
            status_icon = '✅' if tool['configured'] else '❌'
            print(f"{status_icon} {tool['name']}")
            print(f"   类型：{tool['type']}")
            print(f"   状态：{'已配置' if tool['configured'] else '未配置'}")
            
            if 'capabilities' in tool:
                print(f"   能力：{', '.join(tool['capabilities'])}")
            
            if 'default_path' in tool:
                print(f"   默认路径：{tool['default_path']}")
            
            print()
        
        # 推荐
        recommendations = self.generate_recommendations()
        if recommendations:
            print("推荐使用:")
            for rec in recommendations[:3]:
                tool = self.available_tools[rec]
                print(f"  - {tool['name']}")
        
        print("\n" + "="*60 + "\n")
    
    def execute_output(self, output_type: str, content: str, 
                      title: str = '', path: str = '') -> bool:
        """执行输出操作"""
        
        if output_type == 'chat':
            # Chat 输出由调用方处理
            print(content)
            return True
        
        elif output_type == 'local':
            return self._output_local(content, path or title)
        
        elif output_type == 'feishu':
            return self._output_feishu(content, title)
        
        elif output_type == 'github':
            return self._output_github(content, title, path)
        
        else:
            print(f"不支持的输出类型：{output_type}")
            return False
    
    def _output_local(self, content: str, filename: str) -> bool:
        """输出到本地文件"""
        try:
            # 确保目录存在
            base_dir = Path('/root/.openclaw/workspace/docs')
            base_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = base_dir / filename
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已保存到：{file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存失败：{e}")
            return False
    
    def _output_feishu(self, content: str, title: str) -> bool:
        """输出到飞书文档（需要调用 mcporter）"""
        try:
            # 调用 mcporter
            cmd = [
                'mcporter', 'call', 'feishu.doc.create',
                '--title', title,
                '--content', content
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ 已创建飞书文档：{title}")
                # 解析返回的文档链接
                # TODO: 解析并显示链接
                return True
            else:
                print(f"❌ 创建失败：{result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 执行失败：{e}")
            return False
    
    def _output_github(self, content: str, title: str, path: str) -> bool:
        """输出到 GitHub"""
        print("⚠️  GitHub 输出需要额外配置，请联系管理员")
        return False


def main():
    parser = argparse.ArgumentParser(description='输出方式处理工具')
    parser.add_argument('--detect', action='store_true', 
                       help='检测可用工具')
    parser.add_argument('--recommend', action='store_true',
                       help='生成推荐')
    parser.add_argument('--output', type=str,
                       choices=['chat', 'local', 'feishu', 'github', 'notion'],
                       help='输出类型')
    parser.add_argument('--content', type=str,
                       help='输出内容')
    parser.add_argument('--title', type=str, default='',
                       help='文档标题')
    parser.add_argument('--path', type=str, default='',
                       help='输出路径')
    
    args = parser.parse_args()
    
    handler = OutputHandler()
    
    if args.detect:
        handler.detect_tools()
        handler.print_status()
    
    elif args.recommend:
        handler.detect_tools()
        recs = handler.generate_recommendations()
        print("推荐的输出方式:")
        for rec in recs:
            tool = handler.available_tools[rec]
            print(f"  - {tool['name']}")
    
    elif args.output:
        if not args.content:
            print("错误：需要指定 --content")
            sys.exit(1)
        
        handler.detect_tools()
        success = handler.execute_output(
            args.output, 
            args.content, 
            args.title,
            args.path
        )
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
