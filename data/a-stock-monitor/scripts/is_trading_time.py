#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
判断当前是否是A股交易时间
"""

from datetime import datetime, time
import sys


def is_trading_day():
    """判断今天是否是交易日（排除周末）"""
    today = datetime.now()
    # 周一到周五 (0-4)
    if today.weekday() >= 5:
        return False
    
    # TODO: 这里可以进一步判断节假日
    # 目前只判断周末
    return True


def is_trading_time():
    """
    判断当前是否是交易时间
    
    交易时间:
    - 9:15-9:25 集合竞价
    - 9:30-11:30 上午盘
    - 13:00-15:00 下午盘
    
    返回: (is_trading, session_name)
    """
    if not is_trading_day():
        return False, "非交易日"
    
    now = datetime.now().time()
    
    # 集合竞价时间
    if time(9, 15) <= now < time(9, 25):
        return True, "集合竞价"
    
    # 上午盘
    if time(9, 30) <= now < time(11, 30):
        return True, "上午盘"
    
    # 下午盘
    if time(13, 0) <= now < time(15, 0):
        return True, "下午盘"
    
    # 盘后时间（15:00-16:00 可选）
    if time(15, 0) <= now < time(16, 0):
        return True, "盘后"
    
    return False, "非交易时间"


if __name__ == '__main__':
    is_trading, session = is_trading_time()
    
    if is_trading:
        print(f"✅ 当前是交易时间: {session}")
        sys.exit(0)
    else:
        print(f"❌ {session}")
        sys.exit(1)
