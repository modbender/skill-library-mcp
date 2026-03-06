#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股异步数据获取器 v2.0
使用智能数据源：efinance(实时) + baostock(历史)
"""

import asyncio
from smart_data_source import SmartDataSource
from stock_cache_db import StockCache
from datetime import datetime
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')


class StockAsyncFetcher:
    """异步股票数据获取器"""
    
    def __init__(self):
        self.cache = StockCache()
        self.ds = SmartDataSource()
    
    def fetch_and_cache(self, stock_codes: List[str]) -> List[Dict]:
        """
        获取并缓存股票数据
        
        Args:
            stock_codes: 股票代码列表
        
        Returns:
            成功获取的股票数据列表
        """
        print(f"📊 开始获取 {len(stock_codes)} 只股票数据...")
        print(f"⏰ 交易状态: {'交易时间' if self.ds.is_trading_time() else '非交易时间'}")
        print()
        
        results = []
        success_count = 0
        fail_count = 0
        
        for code in stock_codes:
            try:
                # 检查缓存
                cached = self.cache.get_stock(code)
                if cached:
                    # 检查缓存时效（30分钟）
                    from datetime import datetime, timedelta
                    cache_time = datetime.strptime(cached['update_time'], '%Y-%m-%d %H:%M:%S.%f')
                    if datetime.now() - cache_time < timedelta(minutes=30):
                        print(f"✅ {code} - 使用缓存")
                        results.append(cached)
                        success_count += 1
                        continue
                
                # 获取新数据
                quote = self.ds.get_realtime_quote(code)
                
                if quote:
                    # 保存到缓存
                    stock_data = {
                        'code': quote['code'],
                        'name': quote['name'],
                        'price': quote['price'],
                        'change_pct': quote['change_pct'],
                        'volume': quote['volume'],
                        'amount': quote['amount']
                    }
                    
                    self.cache.save_stocks([stock_data])  # 批量保存
                    results.append(stock_data)
                    
                    source_icon = '🟢' if quote['source'] == 'efinance' else '🔵'
                    print(f"{source_icon} {code} - {quote['name']} | ¥{quote['price']:.2f} ({quote['change_pct']:+.2f}%)")
                    success_count += 1
                else:
                    print(f"❌ {code} - 获取失败")
                    fail_count += 1
                
            except Exception as e:
                print(f"❌ {code} - 错误: {e}")
                fail_count += 1
        
        print()
        print(f"✅ 成功: {success_count} | ❌ 失败: {fail_count}")
        return results
    
    def fetch_history_data(self, code: str, days: int = 60) -> Dict:
        """
        获取历史K线数据
        
        Args:
            code: 股票代码
            days: 天数
        
        Returns:
            历史数据DataFrame
        """
        try:
            df = self.ds.get_history_data(code, days=days)
            if df is not None and not df.empty:
                return {
                    'code': code,
                    'data': df,
                    'days': len(df),
                    'source': 'efinance' if len(df) > days * 0.8 else 'baostock'
                }
        except Exception as e:
            print(f"获取{code}历史数据失败: {e}")
        
        return None
    
    def fetch_fund_flow(self, code: str) -> Dict:
        """
        获取资金流向
        
        Args:
            code: 股票代码
        
        Returns:
            资金流数据
        """
        try:
            fund = self.ds.get_fund_flow(code)
            if fund:
                # 保存到缓存
                fund_data = {
                    'main_in': fund['main_in'],
                    'retail_in': fund['retail_in'],
                    'main_ratio': fund['main_ratio']
                }
                self.cache.save_fund_flow(code, fund_data)
                return fund_data
        except Exception as e:
            print(f"获取{code}资金流失败: {e}")
        
        return None
    
    def close(self):
        """关闭连接"""
        self.cache.close()
        self.ds.close()
    
    def __del__(self):
        self.close()


def fetch_all_market():
    """
    获取全市场股票数据
    用于市场热度计算
    """
    import akshare as ak
    
    print("=" * 60)
    print("🌐 获取全市场股票数据")
    print("=" * 60)
    print()
    
    fetcher = StockAsyncFetcher()
    
    try:
        # 获取沪深A股实时行情
        print("📊 正在获取沪深A股行情...")
        df = ak.stock_zh_a_spot_em()
        
        if df.empty:
            print("❌ 未获取到数据")
            fetcher.close()
            return
        
        print(f"✅ 获取到 {len(df)} 只股票")
        
        # 转换为标准格式
        stocks_data = []
        for _, row in df.iterrows():
            try:
                code = str(row['代码'])
                name = row['名称']
                price = float(row['最新价'])
                change_pct = float(row['涨跌幅'])
                volume = float(row['成交量']) if '成交量' in row else 0
                amount = float(row['成交额']) if '成交额' in row else 0
                
                stocks_data.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': change_pct,
                    'volume': volume,
                    'amount': amount
                })
            except Exception as e:
                continue
        
        # 批量保存到缓存
        print(f"💾 正在保存到缓存...")
        fetcher.cache.save_stocks(stocks_data)
        
        print(f"✅ 成功保存 {len(stocks_data)} 只股票数据")
        
        # 统计信息
        up_count = sum(1 for s in stocks_data if s['change_pct'] > 0)
        down_count = sum(1 for s in stocks_data if s['change_pct'] < 0)
        zt_count = sum(1 for s in stocks_data if s['change_pct'] >= 9.9)
        dt_count = sum(1 for s in stocks_data if s['change_pct'] <= -9.9)
        
        print()
        print(f"📈 上涨: {up_count} | 📉 下跌: {down_count}")
        print(f"🔥 涨停: {zt_count} | ❄️ 跌停: {dt_count}")
        print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    finally:
        fetcher.close()


def test():
    """测试函数"""
    print("=" * 60)
    print("股票数据获取器 v2.0 测试")
    print("=" * 60)
    print()
    
    fetcher = StockAsyncFetcher()
    
    # 测试批量获取
    test_codes = ['600276', '601012', '600036']
    results = fetcher.fetch_and_cache(test_codes)
    
    print()
    print(f"共获取 {len(results)} 只股票数据")
    
    # 测试历史数据
    print()
    print("=" * 60)
    print("测试历史数据")
    print("=" * 60)
    
    hist = fetcher.fetch_history_data('600276', days=10)
    if hist:
        print(f"✅ {hist['code']}: {hist['days']} 天数据 (来源: {hist['source']})")
    
    # 测试资金流
    print()
    print("=" * 60)
    print("测试资金流")
    print("=" * 60)
    
    fund = fetcher.fetch_fund_flow('600276')
    if fund:
        print(f"✅ 主力净流入: {fund['main_in']/10000:.2f}万")
    
    fetcher.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        fetch_all_market()
    else:
        test()
