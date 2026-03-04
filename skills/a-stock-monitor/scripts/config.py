#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

# ============ Tushare配置 ============
# 注册地址: https://tushare.pro/register
# Token获取: https://tushare.pro/user/token

TUSHARE_TOKEN = None  # 不使用Tushare（需要积分）

# 如果没有token，系统会自动使用免费数据源（新浪+akshare）

# ============ 监控股票列表 ============
WATCHED_STOCKS = [
    '600900',  # 长江电力
    '601985',  # 中国核电
    '600905',  # 三峡能源
    '600930',  # 华电新能
    '603808',  # 歌力思
    '300896',  # 爱美客
    '688223',  # 晶科能源
    '603127',  # 昭衍新药
]

# ============ WebSocket配置 ============
ENABLE_WEBSOCKET = True  # 是否启用WebSocket实时推送
WEBSOCKET_UPDATE_INTERVAL = 3  # WebSocket更新间隔（秒）

# ============ 数据源优先级 ============
# 实时行情: 新浪财经（优先） > akshare（备用）
# 历史数据: akshare
# 说明: 新浪财经速度快但可能不稳定，akshare稳定但较慢

# ============ Web配置 ============
WEB_HOST = '0.0.0.0'
WEB_PORT = 5000
PASSWORD = 'stock2024'
