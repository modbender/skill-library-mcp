#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能市场数据更新器
只在交易时间更新数据，非交易时间跳过
"""

from is_trading_time import is_trading_time
from update_all_market_data import update_all_market_data
from datetime import datetime
import sys


def main():
    """智能更新：仅在交易时间执行"""
    print(f"\n{'='*60}")
    print(f"🤖 智能市场数据更新器")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    is_trading, session = is_trading_time()
    
    if is_trading:
        print(f"✅ 当前是交易时间: {session}")
        print(f"🔄 开始更新全市场数据...\n")
        
        # 执行数据更新
        success_count = update_all_market_data()
        
        if success_count > 0:
            print(f"\n✅ 更新成功！共 {success_count} 只股票")
            sys.exit(0)
        else:
            print(f"\n⚠️ 未获取到有效数据（可能是集合竞价或其他原因）")
            sys.exit(1)
    else:
        print(f"⏸️  {session}，跳过更新")
        print(f"💡 非交易时间将显示最近一次的市场数据\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
