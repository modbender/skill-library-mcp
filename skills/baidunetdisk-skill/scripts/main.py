#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度网盘操作 Skill
支持功能：文件列表、上传、下载、分享链接提取、转存、搜索
"""

import os
import sys
import json
import re
import requests
from urllib.parse import quote, unquote
from pathlib import Path

class BaiduNetdiskAPI:
    """百度网盘 API 封装"""
    
    BASE_URL = "https://pan.baidu.com/rest/2.0/xpan"
    
    def __init__(self, bduss: str, stoken: str):
        self.bduss = bduss
        self.stoken = stoken
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://pan.baidu.com/disk/home',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
    def _get_cookies(self):
        """获取认证 cookies"""
        return {
            'BDUSS': self.bduss,
            'STOKEN': self.stoken,
            'BAIDUID': 'undefined',
            'BAIDUID_BFESS': 'undefined'
        }
    
    def list_files(self, path: str = "/", order: str = "time"):
        """列出指定目录的文件"""
        url = f"{self.BASE_URL}/file"
        params = {
            'method': 'list',
            'dir': path,
            'order': order,
            'desc': 1,
            'showempty': 0,
            'web': 1,
            'page': 1,
            'num': 1000
        }
        
        try:
            resp = self.session.get(url, params=params, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                files = data.get('list', [])
                result = []
                for f in files:
                    result.append({
                        'name': f.get('server_filename'),
                        'path': f.get('path'),
                        'size': self._format_size(f.get('size', 0)),
                        'is_dir': f.get('isdir') == 1,
                        'modify_time': f.get('server_mtime'),
                        'fs_id': f.get('fs_id')
                    })
                return {'success': True, 'files': result, 'count': len(result)}
            else:
                return {'success': False, 'error': f"API错误: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_files(self, keyword: str, path: str = "/"):
        """搜索文件"""
        url = f"{self.BASE_URL}/file"
        params = {
            'method': 'search',
            'key': keyword,
            'dir': path,
            'web': 1,
            'page': 1,
            'num': 1000
        }
        
        try:
            resp = self.session.get(url, params=params, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                files = data.get('list', [])
                result = []
                for f in files:
                    result.append({
                        'name': f.get('server_filename'),
                        'path': f.get('path'),
                        'size': self._format_size(f.get('size', 0)),
                        'is_dir': f.get('isdir') == 1
                    })
                return {'success': True, 'files': result, 'count': len(result)}
            else:
                return {'success': False, 'error': f"API错误: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_share(self, share_url: str, extract_code: str = ""):
        """提取分享链接的文件列表"""
        # 提取 shorturl
        match = re.search(r'/s/([\w-]+)', share_url)
        if not match:
            return {'success': False, 'error': '无效的分享链接'}
        
        shorturl = match.group(1)
        
        # 验证提取码（如果有）
        if extract_code:
            verify_url = "https://pan.baidu.com/share/verify"
            data = {
                'surl': shorturl,
                'pwd': extract_code
            }
            try:
                resp = self.session.post(verify_url, data=data)
                verify_data = resp.json()
                if verify_data.get('errno') != 0:
                    return {'success': False, 'error': '提取码错误'}
            except Exception as e:
                return {'success': False, 'error': f'验证失败: {str(e)}'}
        
        # 获取分享文件列表
        url = f"{self.BASE_URL}/share/list"
        params = {
            'shorturl': shorturl,
            'page': 1,
            'num': 1000,
            'root': 1
        }
        
        try:
            resp = self.session.get(url, params=params, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                files = data.get('list', [])
                result = []
                for f in files:
                    result.append({
                        'name': f.get('server_filename'),
                        'path': f.get('path'),
                        'size': self._format_size(f.get('size', 0)),
                        'is_dir': f.get('isdir') == 1,
                        'fs_id': f.get('fs_id')
                    })
                return {
                    'success': True, 
                    'files': result, 
                    'count': len(result),
                    'shareid': data.get('shareid'),
                    'uk': data.get('uk')
                }
            else:
                return {'success': False, 'error': f"API错误: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def transfer_share(self, share_url: str, extract_code: str = "", save_path: str = "/我的资源"):
        """转存分享文件到自己的网盘"""
        # 先提取分享信息
        extract_result = self.extract_share(share_url, extract_code)
        if not extract_result['success']:
            return extract_result
        
        shareid = extract_result.get('shareid')
        uk = extract_result.get('uk')
        files = extract_result.get('files', [])
        
        if not files:
            return {'success': False, 'error': '分享中没有文件'}
        
        # 获取 fsid 列表
        fsids = [f['fs_id'] for f in files if 'fs_id' in f]
        
        # 执行转存
        url = f"{self.BASE_URL}/share/transfer"
        params = {
            'shareid': shareid,
            'from': uk,
            'sekey': '',
            'ondup': 'newcopy'
        }
        data = {
            'fsidlist': json.dumps(fsids),
            'path': save_path
        }
        
        try:
            resp = self.session.post(url, params=params, data=data, cookies=self._get_cookies())
            result = resp.json()
            
            if result.get('errno') == 0:
                return {
                    'success': True,
                    'message': f'成功转存 {len(fsids)} 个文件到 {save_path}'
                }
            else:
                return {'success': False, 'error': f"转存失败: {result.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_dir(self, path: str):
        """创建目录"""
        url = "https://pan.baidu.com/api/create"
        
        # 获取父目录
        parent = '/'.join(path.rstrip('/').split('/')[:-1]) or '/'
        name = path.split('/')[-1]
        
        data = {
            'path': path,
            'isdir': '1',
            'rtype': '1',
            'block_list': '[]'
        }
        
        try:
            resp = self.session.post(url, data=data, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                return {'success': True, 'message': f'目录创建成功: {path}'}
            else:
                return {'success': False, 'error': f"创建失败: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_file(self, path: str):
        """删除文件或目录"""
        url = f"{self.BASE_URL}/file"
        params = {
            'method': 'delete',
            'path': path
        }
        
        try:
            resp = self.session.post(url, params=params, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                return {'success': True, 'message': f'删除成功: {path}'}
            else:
                return {'success': False, 'error': f"删除失败: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rename_file(self, path: str, new_name: str):
        """重命名文件或目录"""
        url = "https://pan.baidu.com/api/filemanager"
        
        # 获取父目录
        parent = '/'.join(path.rstrip('/').split('/')[:-1]) or '/'
        new_path = f"{parent}/{new_name}" if parent != '/' else f"/{new_name}"
        
        data = {
            'opera': 'rename',
            'newname': json.dumps({path: new_name}),
            'async': '0'
        }
        
        try:
            resp = self.session.post(url, data=data, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                return {'success': True, 'message': f'重命名成功: {path} -> {new_path}'}
            else:
                return {'success': False, 'error': f"重命名失败: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def move_file(self, path: str, dest: str):
        """移动文件或目录"""
        url = f"{self.BASE_URL}/file"
        params = {
            'method': 'move',
            'path': path,
            'dest': dest
        }
        
        try:
            resp = self.session.post(url, params=params, cookies=self._get_cookies())
            data = resp.json()
            
            if data.get('errno') == 0:
                return {'success': True, 'message': f'移动成功: {path} -> {dest}'}
            else:
                return {'success': False, 'error': f"移动失败: {data.get('errno')}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"


def main():
    """主入口函数"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': '缺少操作参数'
        }))
        sys.exit(1)
    
    action = sys.argv[1]
    
    # 读取配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except:
        config = {}
    
    bduss = config.get('bduss', os.getenv('BAIDU_BDUSS', ''))
    stoken = config.get('stoken', os.getenv('BAIDU_STOKEN', ''))
    
    if not bduss or not stoken:
        print(json.dumps({
            'success': False,
            'error': '缺少 BDUSS 或 STOKEN 配置'
        }))
        sys.exit(1)
    
    api = BaiduNetdiskAPI(bduss, stoken)
    
    # 解析参数
    params = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            params[key] = value
    
    # 执行操作
    if action == 'list':
        result = api.list_files(
            path=params.get('path', '/'),
            order=params.get('order', 'time')
        )
    elif action == 'search':
        result = api.search_files(
            keyword=params.get('keyword', ''),
            path=params.get('path', '/')
        )
    elif action == 'extract':
        result = api.extract_share(
            share_url=params.get('share_url', ''),
            extract_code=params.get('extract_code', '')
        )
    elif action == 'transfer':
        result = api.transfer_share(
            share_url=params.get('share_url', ''),
            extract_code=params.get('extract_code', ''),
            save_path=params.get('save_path', '/我的资源')
        )
    elif action == 'mkdir':
        result = api.create_dir(
            path=params.get('path', '/')
        )
    elif action == 'delete':
        result = api.delete_file(
            path=params.get('path', '')
        )
    elif action == 'rename':
        result = api.rename_file(
            path=params.get('path', ''),
            new_name=params.get('new_name', '')
        )
    elif action == 'move':
        result = api.move_file(
            path=params.get('path', ''),
            dest=params.get('dest', '')
        )
    else:
        result = {'success': False, 'error': f'未知操作: {action}'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
