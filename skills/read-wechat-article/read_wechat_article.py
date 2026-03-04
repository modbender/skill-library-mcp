#!/usr/bin/env python3
"""
微信公众号文章阅读Skill

功能：输入公众号文章URL，自动抓取正文、清洗排版、输出结构化文本
符合Claw Hub发布标准的生产级实现
"""

import time
import requests
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 全局配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://mp.weixin.qq.com/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

TIMEOUT = 15  # 超时时间
RETRY_TIMES = 3  # 重试次数
RETRY_DELAY = 2  # 重试间隔

# 正则表达式
PUB_TIME_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})')
URL_CLEAN_PATTERN = re.compile(r'https://mp\.weixin\.qq\.com/s/[A-Za-z0-9_-]+')

class WeChatArticleError(Exception):
    """公众号文章处理异常"""
    pass

@dataclass
class WeChatArticleResult:
    """公众号文章结果数据类"""
    title: str = ""
    author: str = ""
    publish_time: str = ""
    content_markdown: str = ""
    content_text: str = ""
    images: List[str] = None
    original_url: str = ""
    word_count: int = 0
    read_time_minutes: int = 0
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.content_text:
            self.word_count = len(self.content_text.replace(' ', '').replace('\n', ''))
            self.read_time_minutes = max(1, int(self.word_count / 500))

def clean_wechat_url(url: str) -> str:
    """清理公众号URL，去除多余参数"""
    match = URL_CLEAN_PATTERN.search(url)
    if match:
        return match.group(0)
    return url

def fetch_wechat_html(url: str) -> str:
    """抓取公众号文章HTML"""
    cleaned_url = clean_wechat_url(url)
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for i in range(RETRY_TIMES):
        try:
            response = session.get(
                cleaned_url,
                timeout=TIMEOUT,
                allow_redirects=True,
                verify=False  # 关闭SSL验证，解决部分环境问题
            )
            response.raise_for_status()
            
            # 检查是否需要登录
            if "请先登录" in response.text or "登录验证" in response.text or "验证中心" in response.text:
                raise WeChatArticleError("需要登录微信账号才能访问该文章")
                
            # 检查是否是404页面
            if "抱歉，该文章已被删除" in response.text or "此内容因违规无法查看" in response.text:
                raise WeChatArticleError("文章已被删除或无法访问")
                
            logger.info(f"成功获取文章HTML，状态码: {response.status_code}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"第{i+1}次请求失败: {str(e)}")
            if i == RETRY_TIMES - 1:
                raise WeChatArticleError(f"网络请求失败: {str(e)}")
            time.sleep(RETRY_DELAY)
    
    raise WeChatArticleError("多次尝试后仍无法获取文章内容")

def extract_publish_time(soup: BeautifulSoup) -> str:
    """提取发布时间"""
    try:
        # 尝试从meta标签提取
        meta_time = soup.find("meta", property="article:published_time")
        if meta_time and meta_time.get("content"):
            return meta_time.get("content")[:19].replace('T', ' ')
        
        # 尝试从rich_media_meta提取
        rich_media_meta = soup.find("div", class_="rich_media_meta_list")
        if rich_media_meta:
            meta_text = rich_media_meta.get_text()
            match = PUB_TIME_PATTERN.search(meta_text)
            if match:
                return match.group(0)
        
        # 尝试从id为publish_time的元素提取
        publish_time_elem = soup.find("em", id="publish_time")
        if publish_time_elem:
            return publish_time_elem.text.strip()
            
    except Exception as e:
        logger.warning(f"提取发布时间失败: {str(e)}")
    
    return ""

def extract_author(soup: BeautifulSoup) -> str:
    """提取作者信息"""
    try:
        # 尝试从rich_media_meta提取
        rich_media_meta = soup.find("div", class_="rich_media_meta_list")
        if rich_media_meta:
            meta_spans = rich_media_meta.find_all("span")
            for span in meta_spans:
                if "rich_media_meta_text" in span.get("class", []):
                    text = span.text.strip()
                    if text and not PUB_TIME_PATTERN.search(text):
                        return text
        
        # 尝试从原创标识提取
        original_tag = soup.find("span", class_="rich_media_meta_original_tag")
        if original_tag:
            next_span = original_tag.find_next_sibling("span")
            if next_span:
                return next_span.text.strip()
                
        # 尝试从标题下方提取
        author_elem = soup.find("a", id="js_name")
        if author_elem:
            return author_elem.text.strip()
            
    except Exception as e:
        logger.warning(f"提取作者信息失败: {str(e)}")
    
    return ""

def clean_content_html(content_div: BeautifulSoup) -> BeautifulSoup:
    """清洗内容HTML，去除无关元素"""
    try:
        # 去除不需要的标签
        remove_selectors = [
            ('div', {'class': ['rich_media_meta_list', 'rich_media_tool', 'reward_area', 'like_area', 'ad-wrap', 'js_related_article']}),
            ('script', {}),
            ('style', {}),
            ('iframe', {}),
            ('video', {}),
            ('audio', {}),
            ('span', {'class': ['rich_media_meta', 'profile_nickname']}),
            ('a', {'class': ['js_profile_link', 'js_src']}),
            ('div', {'id': ['js_view_source', 'js_reward_area']})
        ]
        
        for tag_name, attrs in remove_selectors:
            for tag in content_div.find_all(tag_name, attrs):
                tag.decompose()
        
        # 去除空标签
        for tag in content_div.find_all(['div', 'p', 'span']):
            if not tag.contents or all(
                (c.name in ['br', 'p', 'div'] and not c.contents) or 
                (not hasattr(c, 'name') and not c.strip())
                for c in tag.contents
            ):
                tag.decompose()
                
        # 清理多余的属性
        for tag in content_div.find_all(True):
            # 保留必要的属性
            keep_attrs = ['src', 'href', 'alt', 'title']
            for attr in list(tag.attrs.keys()):
                if attr not in keep_attrs:
                    del tag.attrs[attr]
                    
    except Exception as e:
        logger.warning(f"清洗内容HTML失败: {str(e)}")
    
    return content_div

def extract_images(content_div: BeautifulSoup) -> List[str]:
    """提取文章中的图片URL"""
    images = []
    try:
        for img in content_div.find_all("img"):
            img_url = img.get("data-src", img.get("src", img.get("data-lazyload", "")))
            if img_url and img_url.startswith("http"):
                # 清理图片URL参数
                img_url = re.sub(r'&tp=[A-Za-z0-9]+', '', img_url)
                if img_url not in images:
                    images.append(img_url)
                    
    except Exception as e:
        logger.warning(f"提取图片URL失败: {str(e)}")
    
    return images

def parse_wechat_article(html: str, original_url: str) -> WeChatArticleResult:
    """解析公众号文章内容"""
    try:
        soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
        result = WeChatArticleResult(original_url=original_url)
        
        # 提取标题
        try:
            title = soup.find("h1", class_="rich_media_title")
            if title:
                result.title = title.text.strip()
            else:
                title = soup.find("h1")
                if title:
                    result.title = title.text.strip()
                else:
                    logger.warning("未找到文章标题")
        except Exception as e:
            logger.warning(f"提取标题失败: {str(e)}")
        
        # 提取作者
        result.author = extract_author(soup)
        
        # 提取发布时间
        result.publish_time = extract_publish_time(soup)
        
        # 提取正文内容
        try:
            content_div = soup.find("div", id="js_content")
            if not content_div:
                content_div = soup.find("div", class_="rich_media_content")
            
            if content_div:
                # 清洗内容
                cleaned_content = clean_content_html(content_div)
                
                # 提取图片
                result.images = extract_images(cleaned_content)
                
                # 转换为Markdown
                content_html = str(cleaned_content)
                result.content_markdown = md(content_html, heading_style="ATX")
                
                # 提取纯文本
                result.content_text = cleaned_content.get_text(strip=False)
                
                # 计算字数和阅读时间
                result.word_count = len(result.content_text.replace(' ', '').replace('\n', ''))
                result.read_time_minutes = max(1, int(result.word_count / 500))
                
            else:
                raise WeChatArticleError("无法找到文章正文内容")
                
        except Exception as e:
            logger.error(f"提取正文失败: {str(e)}")
            raise WeChatArticleError(f"解析文章内容失败: {str(e)}")
        
        logger.info(f"成功解析文章: {result.title}")
        return result
        
    except Exception as e:
        logger.error(f"解析文章失败: {str(e)}")
        raise WeChatArticleError(f"处理公众号文章失败: {str(e)}")

def read_wechat_article(url: str, **kwargs) -> Dict[str, Any]:
    """
    读取微信公众号文章
    
    Args:
        url: 微信公众号文章URL
        **kwargs: 额外参数
    
    Returns:
        结构化的文章内容
    
    Raises:
        ValueError: 无效的URL格式
        WeChatArticleError: 处理文章失败
    """
    # 验证URL格式
    if not url.startswith("https://mp.weixin.qq.com/s/"):
        raise ValueError("无效的公众号文章URL，格式应为 https://mp.weixin.qq.com/s/xxxxxxx")
    
    try:
        # 抓取HTML
        logger.info(f"开始抓取公众号文章: {url}")
        html = fetch_wechat_html(url)
        
        # 解析文章
        result = parse_wechat_article(html, url)
        
        # 转换为字典
        result_dict = asdict(result)
        
        # 清理空值
        result_dict = {k: v for k, v in result_dict.items() if v not in [None, "", []]}
        
        logger.info("文章处理完成")
        return result_dict
        
    except Exception as e:
        logger.error(f"处理公众号文章失败: {str(e)}")
        raise

def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Claw Skill标准处理函数
    
    Args:
        event: 输入参数，包含url字段
        context: 上下文信息
    
    Returns:
        处理结果
    """
    try:
        url = event.get("url")
        if not url:
            return {
                "success": False,
                "error": "缺少必要参数: url"
            }
        
        result = read_wechat_article(url)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """命令行测试函数"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="微信公众号文章阅读工具")
    parser.add_argument("url", help="微信公众号文章URL")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        result = read_wechat_article(args.url)
        
        print("\n" + "=" * 60)
        print(f"📖 文章标题: {result.get('title', 'N/A')}")
        print(f"✍️ 作者: {result.get('author', 'N/A')}")
        print(f"🗓️ 发布时间: {result.get('publish_time', 'N/A')}")
        print(f"📝 字数: {result.get('word_count', 0):,}")
        print(f"⏱️ 阅读时间: {result.get('read_time_minutes', 0)}分钟")
        print(f"🖼️ 图片数量: {len(result.get('images', []))}")
        print("-" * 60)
        
        # 保存结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {args.output}")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
