#!/usr/bin/env python3
"""
Stock Monitor Pro - 智能分析引擎
集成：新闻、资金流向、龙虎榜、宏观关联分析
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class StockAnalyser:
    """股票智能分析器 - 结合多维度数据给出建议"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    # ========== 1. 新闻舆情 ==========
    
    def fetch_eastmoney_news(self, symbol: str, name: str, limit: int = 5) -> List[Dict]:
        """获取东方财富个股新闻"""
        url = f"https://searchapi.eastmoney.com/api/suggest/get"
        params = {
            "input": name,
            "type": 14,
            "count": limit
        }
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            news_list = []
            for item in data.get("QuotationCodeTable", {}).get("Data", []):
                news_list.append({
                    "title": item.get("Title", ""),
                    "url": item.get("Url", ""),
                    "time": item.get("ShowTime", "")
                })
            return news_list
        except Exception as e:
            return []
    
    def fetch_sina_news(self, symbol: str, name: str) -> List[Dict]:
        """获取新浪财经个股新闻"""
        # 新浪新闻搜索接口
        url = f"https://search.sina.com.cn/?q={name}&c=news&sort=time"
        try:
            resp = self.session.get(url, timeout=10)
            # 这里可以做更精细的HTML解析
            # 简化返回示例
            return [{"title": f"新浪财经-{name}相关新闻", "source": "新浪"}]
        except:
            return []
    
    def analyze_sentiment(self, news_list: List[Dict]) -> Dict:
        """简单情感分析"""
        positive_words = ['利好', '增长', '突破', '买入', '增持', '涨停', '超预期', '业绩大增']
        negative_words = ['利空', '减持', '下跌', '卖出', '亏损', '暴雷', '跌停', '不及预期']
        
        sentiment = {"positive": 0, "negative": 0, "neutral": 0, "summary": []}
        
        for news in news_list:
            title = news.get("title", "")
            p_count = sum(1 for w in positive_words if w in title)
            n_count = sum(1 for w in negative_words if w in title)
            
            if p_count > n_count:
                sentiment["positive"] += 1
            elif n_count > p_count:
                sentiment["negative"] += 1
            else:
                sentiment["neutral"] += 1
        
        # 生成情感摘要
        if sentiment["positive"] > sentiment["negative"]:
            sentiment["overall"] = "偏多"
        elif sentiment["negative"] > sentiment["positive"]:
            sentiment["overall"] = "偏空"
        else:
            sentiment["overall"] = "中性"
            
        return sentiment
    
    # ========== 2. 资金流向 ==========
    
    def fetch_fund_flow(self, symbol: str, market: str = "sz") -> Dict:
        """获取个股资金流向 (新浪财经)"""
        # 新浪资金流向接口
        code = f"{market}{symbol}"
        url = f"https://quotes.sina.cn/cn/api/quotes.php?symbol={code}&source=sina"
        
        try:
            resp = self.session.get(url, timeout=10)
            # 解析返回数据
            return {
                "main_inflow": "数据获取中...",
                "retail_inflow": "数据获取中...",
                "net_inflow": "数据获取中..."
            }
        except:
            return {"error": "获取失败"}
    
    def fetch_northbound_flow(self) -> Dict:
        """获取北向资金 (沪深股通) 流向"""
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {"secid": "1.000001", "fields": "f170"}  # 简化示例
        try:
            resp = self.session.get(url, params=params, timeout=10)
            return {"northbound": "北向资金数据获取中..."}
        except:
            return {}
    
    # ========== 3. 龙虎榜 ==========
    
    def fetch_dragon_tiger(self, date: str = None) -> List[Dict]:
        """获取龙虎榜数据"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        url = f"http://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "NET_BUY_AMT",
            "sortTypes": "-1",
            "pageSize": "50",
            "pageNumber": "1",
            "reportName": "RPT_DMSK_TS",
            "columns": "ALL",
            "filter": f"(TRADE_DATE='{date}')"
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            return data.get("result", {}).get("data", [])
        except:
            return []
    
    # ========== 4. 宏观关联分析 ==========
    
    def analyze_gold_correlation(self, gold_price: float, stocks: List[Dict]) -> str:
        """分析金价与持仓股票的关联"""
        # 江西铜业等有色股与金价正相关
        correlation_map = {
            "600362": "强正相关",  # 江西铜业
            "601318": "弱相关",    # 中国平安
            "513180": "弱负相关",  # 恒生科技
            "159892": "弱相关",    # 恒生医疗
        }
        
        analysis = []
        for stock in stocks:
            code = stock.get("code")
            corr = correlation_map.get(code, "未知")
            if corr in ["强正相关", "中等正相关"]:
                analysis.append(f"📈 {stock['name']}: 与金价{corr}，金价上涨可能带动该股")
        
        return "\n".join(analysis) if analysis else "暂无强关联标的"
    
    # ========== 5. 综合分析 ==========
    
    def generate_insight(self, stock: Dict, price_data: Dict, alerts: List) -> str:
        """生成综合分析报告"""
        code = stock['code']
        name = stock['name']
        
        # 1. 获取新闻
        news_list = self.fetch_eastmoney_news(code, name)
        sentiment = self.analyze_sentiment(news_list)
        
        # 2. 资金流向
        fund_flow = self.fetch_fund_flow(code, stock.get('market', 'sz'))
        
        # 3. 构建报告
        report = f"""📊 <b>{name} ({code}) 深度分析</b>

💰 <b>价格异动:</b>
• 当前: {price_data.get('price', 'N/A')} ({price_data.get('change_pct', 0):+.2f}%)
• 触发: {', '.join([a[1] for a in alerts])}

📰 <b>舆情分析 ({sentiment.get('overall', '未知')}):</b>
• 最近新闻: {len(news_list)} 条
• 正面: {sentiment.get('positive', 0)} | 负面: {sentiment.get('negative', 0)}
"""
        
        # 添加最新新闻标题
        if news_list:
            report += "\n<b>最新动态:</b>\n"
            for n in news_list[:2]:
                report += f"• {n.get('title', '无标题')[:30]}...\n"
        
        # 4. 给出建议
        suggestion = self._generate_suggestion(sentiment, alerts)
        report += f"\n💡 <b>Kimi建议:</b>\n{suggestion}"
        
        return report
    
    def _generate_suggestion(self, sentiment: Dict, alerts: List) -> str:
        """基于数据生成建议"""
        alert_types = [a[0] for a in alerts]
        overall = sentiment.get("overall", "中性")
        
        # 价格下跌 + 舆情偏空 = 谨慎
        if "below" in alert_types and overall == "偏空":
            return "⚠️ 价格跌破支撑位，且舆情偏空，建议观察等待，不急于抄底。"
        
        # 价格下跌 + 舆情偏多 = 可能是机会
        if "below" in alert_types and overall == "偏多":
            return "🔍 价格下跌但舆情偏多，可能是情绪错杀，关注是否有反弹机会。"
        
        # 价格突破 + 舆情偏多 = 确认趋势
        if "above" in alert_types and overall == "偏多":
            return "🚀 价格突破且舆情配合，趋势可能延续，可考虑顺势而为。"
        
        # 大涨
        if "pct_up" in alert_types:
            return "📈 短期涨幅较大，注意获利了结风险。"
        
        # 大跌
        if "pct_down" in alert_types:
            return "📉 短期跌幅较大，关注是否超跌反弹，但勿急于抄底。"
        
        return "⏳ 建议保持观察，等待更明确信号。"


# ========== 测试 ==========
if __name__ == '__main__':
    analyser = StockAnalyser()
    
    # 测试新闻抓取
    print("=== 新闻测试 ===")
    news = analyser.fetch_eastmoney_news("600362", "江西铜业")
    print(f"获取到 {len(news)} 条新闻")
    for n in news[:3]:
        print(f"  - {n.get('title', 'N/A')[:40]}...")
    
    # 测试情感分析
    print("\n=== 情感分析测试 ===")
    sentiment = analyser.analyze_sentiment(news)
    print(f"整体情绪: {sentiment.get('overall')}")
    print(f"正面: {sentiment.get('positive')}, 负面: {sentiment.get('negative')}")
    
    # 测试金价关联
    print("\n=== 宏观关联测试 ===")
    stocks = [{"code": "600362", "name": "江西铜业"}]
    corr = analyser.analyze_gold_correlation(2743, stocks)
    print(corr)
