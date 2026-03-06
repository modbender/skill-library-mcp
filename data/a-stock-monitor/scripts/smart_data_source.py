#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据源 v2.0 - 集成混合数据源
向后兼容原有 SmartDataSource 接口
"""

from hybrid_data_source import HybridDataSource
from datetime import datetime, time as dt_time
import pandas as pd
from typing import Optional, Dict


class SmartDataSourceV2:
    """智能数据源 v2.0（集成混合数据源）"""
    
    def __init__(self, tushare_token: Optional[str] = None):
        """初始化"""
        # 使用混合数据源
        self.hybrid = HybridDataSource(tushare_token)
        
    def is_trading_time(self) -> bool:
        """判断是否是交易时间"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()
        
        # 周末
        if weekday >= 5:
            return False
        
        # 交易时间段
        morning_start = dt_time(9, 15)
        morning_end = dt_time(11, 30)
        afternoon_start = dt_time(13, 0)
        afternoon_end = dt_time(15, 0)
        
        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)
    
    def get_realtime_price(self, code: str) -> Optional[Dict]:
        """
        获取实时行情（兼容接口）
        
        Returns:
            {
                'code': str,
                'name': str,
                'price': float,
                'change_pct': float,
                'volume': float,
                'amount': float,
                'open': float,
                'high': float,
                'low': float,
            }
        """
        return self.hybrid.get_realtime_price(code)
    
    def get_realtime_quote(self, code: str) -> Optional[Dict]:
        """获取实时行情（兼容原接口）"""
        return self.get_realtime_price(code)
    
    def is_trading_day(self) -> bool:
        """判断是否为交易日（9:00-15:30）"""
        return self.is_trading_time()
    
    def get_batch_realtime(self, codes: list) -> list:
        """批量获取实时行情"""
        return self.hybrid.get_realtime_batch(codes)
    
    def get_history_data(self, code: str, days: int = 120) -> Optional[pd.DataFrame]:
        """
        获取历史数据
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount
        """
        return self.hybrid.get_history_data(code, days)
    
    def close(self):
        """关闭连接（向后兼容，实际无操作）"""
        pass


# 向后兼容：保持原名称
SmartDataSource = SmartDataSourceV2


if __name__ == '__main__':
    print("=" * 60)
    print("智能数据源 v2.0 测试")
    print("=" * 60)
    
    # 初始化
    ds = SmartDataSource()
    
    # 测试1: 判断交易时间
    print(f"\n交易时间: {ds.is_trading_time()}")
    
    # 测试2: 获取实时行情
    print("\n测试获取实时行情...")
    data = ds.get_realtime_price('600900')
    if data:
        print(f"✅ {data.get('name', 'N/A')} ({data['code']})")
        print(f"   价格: ¥{data['price']:.2f}")
        print(f"   涨跌: {data['change_pct']:+.2f}%")
        print(f"   来源: {data.get('source', 'unknown')}")
    else:
        print("❌ 获取失败")
    
    # 测试3: 批量获取
    print("\n测试批量获取...")
    codes = ['600900', '601985']
    results = ds.get_batch_realtime(codes)
    print(f"✅ 获取到 {len(results)} 只股票")
    
    # 测试4: 历史数据
    print("\n测试历史数据...")
    df = ds.get_history_data('600900', days=5)
    if df is not None and not df.empty:
        print(f"✅ 获取到 {len(df)} 天数据")
        print(df.tail())
    else:
        print("❌ 历史数据获取失败")
