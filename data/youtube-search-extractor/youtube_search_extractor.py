#!/usr/bin/env python3
"""YouTube搜索结果视频链接提取器 - YouTube Search Extractor"""

import subprocess
import re
import sys
import argparse
from datetime import datetime
import time

class YouTubeSearchExtractor:
    """YouTube搜索结果视频链接提取器类"""
    
    def __init__(self, headless=True, wait_time=5, max_links=50):
        self.headless = headless
        self.wait_time = wait_time
        self.max_links = max_links
        self.agent_browser_cmd = ['agent-browser']
    
    def search_youtube(self, search_query):
        """
        使用agent-browser执行YouTube搜索
        """
        print(f"🔍 正在搜索: {search_query}")
        
        try:
            # 关闭现有的浏览器实例
            subprocess.run(self.agent_browser_cmd + ['close'], capture_output=True, text=True)
            
            # 打开搜索页面
            search_url = f"https://www.youtube.com/results?search_query={self._url_encode(search_query)}"
            print(f"📌 访问搜索页面: {search_url}")
            
            result = subprocess.run(
                self.agent_browser_cmd + ['open', search_url],
                capture_output=True, text=True, check=True
            )
            
            if result.returncode == 0:
                print("✅ 搜索页面已加载")
                
                # 等待页面加载
                print(f"⏳ 等待 {self.wait_time} 秒让页面加载...")
                time.sleep(self.wait_time)
                
                # 获取页面HTML内容
                result = subprocess.run(
                    self.agent_browser_cmd + ['get', 'html', 'body'],
                    capture_output=True, text=True, check=True
                )
                
                if result.returncode == 0:
                    print("✅ 页面内容获取成功")
                    return result.stdout
                
                else:
                    print(f"❌ 获取页面内容失败: {result.returncode}")
                    if result.stderr:
                        print(f"错误信息: {result.stderr}")
                    return None
                    
            else:
                print(f"❌ 访问搜索页面失败: {result.returncode}")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 执行命令失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            return None
            
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def extract_video_links(self, html_content):
        """
        从HTML内容中提取视频链接
        """
        print("🔍 正在提取视频链接...")
        
        video_links = []
        
        patterns = [
            r'href=["\'](/watch\?v=[\w-]+[^"\']*)["\']',
            r'href=["\'](https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+[^"\']*)["\']',
            r'href=["\'](https?://(?:www\.)?youtu\.be/[\w-]+[^"\']*)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if match.startswith('/watch'):
                    full_url = f"https://www.youtube.com{match}"
                else:
                    full_url = match
                
                if 'v=' in full_url or 'youtu.be/' in full_url:
                    if '?' in full_url:
                        params = full_url.split('?')[1].split('&')
                        filtered_params = []
                        for param in params:
                            if param.startswith('v=') or param.startswith('pp='):
                                filtered_params.append(param)
                        
                        if filtered_params:
                            full_url = full_url.split('?')[0] + '?' + '&'.join(filtered_params)
                
                if full_url not in video_links:
                    video_links.append(full_url)
        
        print(f"✅ 找到 {len(video_links)} 个视频链接")
        return video_links[:self.max_links]
    
    def save_results(self, search_query, video_links, output_file):
        """
        保存搜索结果
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存HTML内容
        try:
            with open(f"{output_file}.html", 'w', encoding='utf-8') as f:
                f.write(self.html_content)
            print(f"✅ 搜索结果HTML已保存到 {output_file}.html")
        except Exception as e:
            print(f"❌ 保存HTML失败: {e}")
        
        # 保存链接列表
        try:
            with open(f"{output_file}_links.txt", 'w', encoding='utf-8') as f:
                f.write(f"# YouTube搜索结果：'{search_query}' ({timestamp})\n")
                f.write(f"# 找到 {len(video_links)} 个相关视频\n")
                f.write(f"\n")
                
                for i, link in enumerate(video_links, 1):
                    f.write(f"{i}. {link}\n")
            
            print(f"✅ 视频链接已保存到 {output_file}_links.txt")
            return f"{output_file}_links.txt"
        except Exception as e:
            print(f"❌ 保存链接列表失败: {e}")
            return None
    
    def run_search(self, search_query, output_file):
        """
        完整的搜索和提取流程
        """
        print(f"🚀 开始搜索 '{search_query}'...")
        
        # 1. 执行搜索
        self.html_content = self.search_youtube(search_query)
        
        if not self.html_content:
            print("❌ 搜索失败，无法继续")
            return False
        
        # 2. 提取视频链接
        video_links = self.extract_video_links(self.html_content)
        
        if not video_links:
            print("⚠️  没有找到相关的视频链接")
            return False
        
        # 3. 保存结果
        output_path = self.save_results(search_query, video_links, output_file)
        
        if output_path:
            print(f"\n🎯 任务完成！结果已保存到 {output_path}")
            return True
        else:
            print("❌ 任务失败")
            return False
    
    def _url_encode(self, text):
        """URL编码"""
        import urllib.parse
        return urllib.parse.quote(text)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="YouTube搜索结果视频链接提取器 - YouTube Search Extractor"
    )
    
    parser.add_argument(
        "search_query",
        help="搜索关键词（例如：'hydrasynth 实战应用'）"
    )
    
    parser.add_argument(
        "output_file",
        help="输出文件名（不包含扩展名）"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="使用无头浏览器模式"
    )
    
    parser.add_argument(
        "--wait-time",
        type=int,
        default=5,
        help="页面加载等待时间（秒，默认5秒）"
    )
    
    parser.add_argument(
        "--max-links",
        type=int,
        default=50,
        help="最大提取链接数量（默认50个）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用详细输出"
    )
    
    args = parser.parse_args()
    
    # 创建提取器实例
    extractor = YouTubeSearchExtractor(
        headless=args.headless,
        wait_time=args.wait_time,
        max_links=args.max_links
    )
    
    # 执行搜索
    success = extractor.run_search(args.search_query, args.output_file)
    
    # 清理
    try:
        subprocess.run(['agent-browser', 'close'], capture_output=True, text=True)
    except:
        pass
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
