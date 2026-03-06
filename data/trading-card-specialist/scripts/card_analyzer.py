#!/usr/bin/env python3
"""
Trading Card Market Analysis Tool
Provides basic card analysis capabilities for the free tier

Security Features:
- Environment variable token management (no hardcoded credentials)
- Rate limiting (2 second delay between API calls)
- Ethical web scraping practices
- Input validation and error handling

Usage:
    export EBAY_TOKEN="your_ebay_api_token"
    python card_analyzer.py
"""

import requests
import json
import re
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys

class CardAnalyzer:
    """Basic trading card analysis tool for market research and pricing"""
    
    def __init__(self):
        # Security: Use environment variables for API tokens
        ebay_token = os.getenv('EBAY_TOKEN')
        if not ebay_token:
            raise ValueError(
                "EBAY_TOKEN environment variable not set. "
                "Please run: export EBAY_TOKEN='your_actual_token'"
            )
        
        self.base_url = "https://api.ebay.com/buy/browse/v1"
        self.headers = {
            "Authorization": f"Bearer {ebay_token}",
            "Content-Type": "application/json"
        }
    
    def analyze_card(self, card_query: str, max_results: int = 50) -> Dict:
        """
        Analyze a specific card's market performance
        
        Args:
            card_query: Search string for the card (e.g. "2023 Topps Chrome Ja Morant PSA 10")
            max_results: Maximum number of sold listings to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        print(f"🔍 Analyzing: {card_query}")
        
        # Simulate eBay sold listings data (replace with actual API call)
        sales_data = self._get_sold_listings(card_query, max_results)
        
        if not sales_data:
            return {"error": "No sales data found", "query": card_query}
        
        analysis = {
            "card": card_query,
            "analysis_date": datetime.now().isoformat(),
            "sales_summary": self._calculate_sales_summary(sales_data),
            "price_trends": self._analyze_price_trends(sales_data),
            "market_insights": self._generate_insights(sales_data),
            "recommendations": self._generate_recommendations(sales_data)
        }
        
        return analysis
    
    def _get_sold_listings(self, query: str, limit: int) -> List[Dict]:
        """Get sold listings data with ethical rate limiting"""
        # Rate limiting: 2 second delay between API calls to respect servers
        time.sleep(2)
        
        # TODO: Implement actual eBay API calls here
        # This is currently sample data for development/testing
        print(f"⚠️  Using sample data. Query: '{query}', Limit: {limit}")
        print("📋 To enable real API calls:")
        print("   1. Set EBAY_TOKEN environment variable")  
        print("   2. Implement eBay API search endpoint")
        print("   3. Review eBay API terms of service")
        
        # Sample data structure for development/testing
        sample_data = [
            {"price": 125.00, "date": "2024-03-01", "condition": "PSA 10", "title": "2023 Topps Chrome Ja Morant PSA 10"},
            {"price": 110.50, "date": "2024-02-28", "condition": "PSA 10", "title": "2023 Topps Chrome Ja Morant PSA 10"},
            {"price": 135.00, "date": "2024-02-25", "condition": "PSA 10", "title": "2023 Topps Chrome Ja Morant PSA 10 Refractor"},
            {"price": 98.99, "date": "2024-02-20", "condition": "PSA 9", "title": "2023 Topps Chrome Ja Morant PSA 9"},
            {"price": 142.50, "date": "2024-02-15", "condition": "PSA 10", "title": "2023 Topps Chrome Ja Morant PSA 10"},
        ]
        
        return sample_data[:limit]
    
    def _calculate_sales_summary(self, sales_data: List[Dict]) -> Dict:
        """Calculate basic sales statistics"""
        if not sales_data:
            return {}
        
        prices = [float(sale["price"]) for sale in sales_data]
        
        return {
            "total_sales": len(prices),
            "average_price": round(sum(prices) / len(prices), 2),
            "median_price": round(sorted(prices)[len(prices)//2], 2),
            "min_price": min(prices),
            "max_price": max(prices),
            "price_range": round(max(prices) - min(prices), 2),
            "date_range": {
                "earliest": min(sale["date"] for sale in sales_data),
                "latest": max(sale["date"] for sale in sales_data)
            }
        }
    
    def _analyze_price_trends(self, sales_data: List[Dict]) -> Dict:
        """Analyze price movement trends over time"""
        if len(sales_data) < 3:
            return {"trend": "insufficient_data"}
        
        # Sort by date
        sorted_sales = sorted(sales_data, key=lambda x: x["date"])
        prices = [float(sale["price"]) for sale in sorted_sales]
        
        # Simple trend analysis (first vs last third of data)
        first_third = prices[:len(prices)//3] if len(prices) >= 3 else prices[:1]
        last_third = prices[-len(prices)//3:] if len(prices) >= 3 else prices[-1:]
        
        avg_early = sum(first_third) / len(first_third)
        avg_recent = sum(last_third) / len(last_third)
        
        change_percent = ((avg_recent - avg_early) / avg_early) * 100
        
        if change_percent > 10:
            trend = "rising"
        elif change_percent < -10:
            trend = "falling"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 1),
            "early_avg": round(avg_early, 2),
            "recent_avg": round(avg_recent, 2)
        }
    
    def _generate_insights(self, sales_data: List[Dict]) -> List[str]:
        """Generate market insights based on sales data"""
        insights = []
        summary = self._calculate_sales_summary(sales_data)
        trends = self._analyze_price_trends(sales_data)
        
        # Volume insights
        if summary["total_sales"] > 20:
            insights.append("High liquidity - card trades frequently")
        elif summary["total_sales"] < 5:
            insights.append("Low liquidity - limited market activity")
        
        # Price stability insights
        volatility = (summary["price_range"] / summary["average_price"]) * 100
        if volatility > 30:
            insights.append("High price volatility - proceed with caution")
        elif volatility < 10:
            insights.append("Stable pricing - predictable market")
        
        # Trend insights
        if trends["trend"] == "rising":
            insights.append(f"Upward trend detected (+{trends['change_percent']}%)")
        elif trends["trend"] == "falling":
            insights.append(f"Downward trend detected ({trends['change_percent']}%)")
        
        return insights
    
    def _generate_recommendations(self, sales_data: List[Dict]) -> Dict:
        """Generate buying/selling recommendations"""
        summary = self._calculate_sales_summary(sales_data)
        trends = self._analyze_price_trends(sales_data)
        
        # Simple recommendation logic
        target_buy = round(summary["average_price"] * 0.85, 2)  # 15% below average
        target_sell = round(summary["average_price"] * 1.15, 2)  # 15% above average
        
        recommendation = "HOLD"  # Default
        if trends["trend"] == "rising":
            recommendation = "BUY"
        elif trends["trend"] == "falling":
            recommendation = "SELL"
        
        return {
            "action": recommendation,
            "target_buy_price": target_buy,
            "target_sell_price": target_sell,
            "confidence": "medium",  # Would be calculated based on data quality
            "reasoning": f"Based on {summary['total_sales']} sales with {trends['trend']} trend"
        }
    
    def generate_report(self, analysis: Dict) -> str:
        """Generate a formatted analysis report"""
        if "error" in analysis:
            return f"❌ Analysis Error: {analysis['error']}"
        
        summary = analysis["sales_summary"]
        trends = analysis["price_trends"]
        insights = analysis["market_insights"]
        recs = analysis["recommendations"]
        
        report = f"""
📊 TRADING CARD ANALYSIS REPORT
=======================================
Card: {analysis['card']}
Analysis Date: {analysis['analysis_date'][:10]}

💰 SALES SUMMARY
• Total Sales: {summary['total_sales']}
• Average Price: ${summary['average_price']}
• Price Range: ${summary['min_price']} - ${summary['max_price']}
• Date Range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}

📈 PRICE TRENDS
• Trend: {trends['trend'].upper()}
• Change: {trends.get('change_percent', 'N/A')}%
• Recent Avg: ${trends.get('recent_avg', 'N/A')}

💡 MARKET INSIGHTS
{chr(10).join(f'• {insight}' for insight in insights)}

🎯 RECOMMENDATIONS
• Action: {recs['action']}
• Target Buy: ${recs['target_buy_price']}
• Target Sell: ${recs['target_sell_price']}
• Reasoning: {recs['reasoning']}

=======================================
💎 Upgrade to Premium for:
• PSA population data
• Advanced trend analysis  
• Competitor monitoring
• Multi-platform pricing
"""
        return report


def main():
    """Command-line interface for card analysis"""
    if len(sys.argv) < 2:
        print("Usage: python card_analyzer.py 'card search query'")
        print("Example: python card_analyzer.py '2023 Topps Chrome Ja Morant PSA 10'")
        return
    
    query = " ".join(sys.argv[1:])
    analyzer = CardAnalyzer()
    
    print("🃏 Trading Card Analyzer - Free Tier")
    print("=" * 50)
    
    analysis = analyzer.analyze_card(query)
    report = analyzer.generate_report(analysis)
    
    print(report)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(report)
    
    print(f"\n📁 Report saved to: {filename}")


if __name__ == "__main__":
    main()