#!/usr/bin/env python3
# Multi Source Tech News Digest - 多源科技新闻摘要
# 版本: 1.0.0

import json
import os
import sys
from datetime import datetime
from typing import List, Dict

class MultiSourceTechNewsDigest:
    """多源科技新闻摘要技能"""
    
    def __init__(self):
        self.name = "Multi Source Tech News Digest"
        self.version = "1.0.0"
        self.description = "自动聚合、评分并交付来自 RSS、Twitter/X、GitHub releases 和网页搜索等 109+ 来源的科技新闻"
        self.author = "hesamsheikh"
        self.tags = ["awesome-list", "clawdbot", "moltbot", "openclaw", "openclaw-plugin"]
        
        # 初始化配置
        self.config = {
            "rss_sources": [
                "https://techcrunch.com/feed/",
                "https://www.wired.com/feed/",
                "https://www.theverge.com/feed/",
                "https://arstechnica.com/feed/",
                "https://www.zdnet.com/feed/"
            ],
            "github_repos": [
                "https://api.github.com/repos/trending",
                "https://api.github.com/repos/awesome"
            ],
            "web_sources": [
                "https://news.google.com/search?q=technology",
                "https://www.techmeme.com/"
            ],
            "max_news_per_source": 5,
            "min_score_threshold": 50
        }
        
        # 存储数据
        self.news_data = []
        self.last_update = None
    
    def fetch_rss_news(self, source_url: str) -> List[Dict]:
        """从RSS源获取新闻"""
        try:
            # 使用OpenClaw的web_fetch工具获取内容
            import subprocess
            result = subprocess.run([
                sys.executable, "-c", 
                f"import requests; import feedparser; \
                feed = feedparser.parse('{source_url}'); \
                print(json.dumps([{{'title': e.title, 'link': e.link, 'summary': e.summary[:200] if hasattr(e, 'summary') else '', 'published': e.published if hasattr(e, 'published') else ''}} for e in feed.entries[:{self.config['max_news_per_source']}]]))"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            return []
        except Exception as e:
            print(f"Error fetching RSS from {source_url}: {e}")
            return []
    
    def fetch_github_releases(self) -> List[Dict]:
        """获取GitHub releases"""
        try:
            releases = []
            for repo in self.config["github_repos"]:
                import subprocess
                result = subprocess.run([
                    sys.executable, "-c",
                    f"import requests; \
                    response = requests.get('{repo}', headers={{'Accept': 'application/vnd.github.v3+json'}}); \
                    print(json.dumps(response.json()[:{self.config['max_news_per_source']}]))"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    repo_releases = json.loads(result.stdout.strip())
                    for release in repo_releases:
                        releases.append({
                            "title": release.get("name", ""),
                            "link": release.get("html_url", ""),
                            "summary": release.get("body", "")[:200] if release.get("body") else "",
                            "published": release.get("published_at", ""),
                            "source": "GitHub"
                        })
            return releases
        except Exception as e:
            print(f"Error fetching GitHub releases: {e}")
            return []
    
    def score_news(self, news_item: Dict) -> int:
        """为新闻评分"""
        score = 0
        
        # 基于标题关键词评分
        tech_keywords = ["AI", "artificial intelligence", "machine learning", "blockchain", 
                        "quantum", "robotics", "5G", "6G", "cloud", "cybersecurity"]
        title = news_item.get("title", "").lower()
        
        for keyword in tech_keywords:
            if keyword.lower() in title:
                score += 20
        
        # 基于摘要长度评分
        summary = news_item.get("summary", "")
        if len(summary) > 100:
            score += 10
        
        # 基于来源可信度评分
        source = news_item.get("source", "")
        trusted_sources = ["TechCrunch", "Wired", "The Verge", "Ars Technica"]
        for trusted in trusted_sources:
            if trusted.lower() in source.lower():
                score += 15
        
        return score
    
    def get_news(self, force_refresh: bool = False) -> List[Dict]:
        """获取新闻（带缓存）"""
        if not force_refresh and self.news_data and self.last_update:
            # 如果数据存在且不是强制刷新，返回缓存数据
            time_diff = datetime.now() - self.last_update
            if time_diff.total_seconds() < 3600:  # 1小时内不刷新
                return self.news_data
        
        # 获取新数据
        all_news = []
        
        # 从RSS源获取
        for source in self.config["rss_sources"]:
            news = self.fetch_rss_news(source)
            for item in news:
                item["source"] = source.split("//")[1].split("/")[0]
                item["score"] = self.score_news(item)
                all_news.append(item)
        
        # 从GitHub获取
        github_news = self.fetch_github_releases()
        all_news.extend(github_news)
        
        # 过滤低分新闻
        filtered_news = [item for item in all_news if item["score"] >= self.config["min_score_threshold"]]
        
        # 按评分排序
        filtered_news.sort(key=lambda x: x["score"], reverse=True)
        
        # 更新缓存
        self.news_data = filtered_news[:20]  # 最多保存20条
        self.last_update = datetime.now()
        
        return self.news_data
    
    def generate_daily_digest(self) -> str:
        """生成每日摘要"""
        news = self.get_news()
        
        if not news:
            return "今日未获取到符合条件的科技新闻。"
        
        digest = f"📰 今日科技新闻摘要 ({len(news)}条)\n\n"
        
        for i, item in enumerate(news[:10], 1):  # 只显示前10条
            digest += f"{i}. {item['title']}\n"
            digest += f"   📊 评分: {item['score']} | 🌐 来源: {item['source']}\n"
            digest += f"   📝 摘要: {item['summary']}...\n"
            digest += f"   🔗 链接: {item['link']}\n\n"
        
        return digest
    
    def run(self, args: List[str] = None) -> Dict:
        """运行技能"""
        if args is None:
            args = []
        
        action = args[0] if args else "digest"
        
        if action == "digest":
            result = self.generate_daily_digest()
            return {"status": "success", "content": result}
        elif action == "list":
            news = self.get_news()
            return {"status": "success", "data": news}
        elif action == "refresh":
            news = self.get_news(force_refresh=True)
            return {"status": "success", "message": f"已刷新，获取到 {len(news)} 条新闻"}
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

def main():
    """主函数"""
    skill = MultiSourceTechNewsDigest()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        result = skill.run([action])
        
        if result["status"] == "success":
            if "content" in result:
                print(result["content"])
            elif "data" in result:
                print(json.dumps(result["data"], indent=2))
            else:
                print(result["message"])
        else:
            print(f"错误: {result['message']}", file=sys.stderr)
            sys.exit(1)
    else:
        # 默认生成摘要
        result = skill.run(["digest"])
        print(result["content"])

if __name__ == "__main__":
    main()
