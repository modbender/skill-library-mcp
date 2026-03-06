#!/usr/bin/env python3
"""
富途牛牛API数据获取工具
纯数据版本，无交易功能
"""

__version__ = "1.0.0"
__author__ = "汪汪狗 (OpenClaw Assistant)"

import futu as ft
import pandas as pd
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import argparse

class FutuAPI:
    """富途API数据客户端"""
    
    def __init__(self, host="127.0.0.1", port=11111, cache_dir=".cache", cache_ttl=60):
        """
        初始化客户端
        
        Args:
            host: 富途服务器地址
            port: 富途服务器端口
            cache_dir: 缓存目录
            cache_ttl: 缓存有效期（秒）
        """
        self.host = host
        self.port = port
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.quote_ctx = None
        self.connected = False
        
        # 创建缓存目录
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        
    def connect(self, retries: int = 3, delay: float = 1.0) -> bool:
        """连接富途行情服务器"""
        for attempt in range(retries):
            try:
                self.quote_ctx = ft.OpenQuoteContext(host=self.host, port=self.port)
                self.connected = True
                print(f"✅ 连接成功 (尝试 {attempt + 1}/{retries})")
                return True
            except Exception as e:
                if attempt < retries - 1:
                    print(f"⚠️  连接失败，{delay}秒后重试... (错误: {e})")
                    time.sleep(delay)
                else:
                    print(f"❌ 连接失败，已重试{retries}次: {e}")
        
        return False
    
    def disconnect(self):
        """断开连接"""
        if self.quote_ctx:
            self.quote_ctx.close()
            self.connected = False
    
    def _get_cache_key(self, func_name: str, *args) -> str:
        """生成缓存键"""
        key_parts = [func_name] + [str(arg) for arg in args]
        return "_".join(key_parts).replace(".", "_").replace("/", "_")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """从缓存加载数据"""
        if not self.cache_dir:
            return None
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # 检查缓存是否过期
                cache_time = datetime.fromisoformat(cache_data.get('_cache_time', '2000-01-01'))
                if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                    return cache_data.get('data')
            except:
                pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """保存数据到缓存"""
        if not self.cache_dir:
            return
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            cache_data = {
                'data': data,
                '_cache_time': datetime.now().isoformat(),
                '_cache_key': cache_key
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_quote(self, symbol: str, market: str = "HK", use_cache: bool = True) -> Optional[Dict]:
        """获取股票实时行情"""
        # 检查缓存
        if use_cache:
            cache_key = self._get_cache_key('quote', symbol, market)
            cached = self._load_from_cache(cache_key)
            if cached:
                cached['_from_cache'] = True
                return cached
        
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # 订阅并获取行情
            ret_sub, _ = self.quote_ctx.subscribe([code], [ft.SubType.QUOTE])
            if ret_sub != ft.RET_OK:
                return None
            
            ret, data = self.quote_ctx.get_stock_quote([code])
            
            if ret == ft.RET_OK and len(data) > 0:
                row = data.iloc[0]
                
                # 计算涨跌幅
                last_price = row['last_price']
                prev_close = row['prev_close_price']
                change = last_price - prev_close
                change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
                
                return {
                    'symbol': symbol,
                    'market': market,
                    'price': last_price,
                    'open': row['open_price'],
                    'high': row['high_price'],
                    'low': row['low_price'],
                    'prev_close': prev_close,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': int(row['volume']),
                    'turnover': row['turnover'],
                    'time': row['data_time'],
                    'updated': datetime.now().isoformat(),
                    '_from_cache': False
                }
                
                # 保存到缓存
                if use_cache:
                    cache_key = self._get_cache_key('quote', symbol, market)
                    self._save_to_cache(cache_key, quote_data)
                
                return quote_data
        except Exception as e:
            print(f"获取行情失败: {e}")
        
        return None
    
    def get_kline(self, symbol: str, market: str = "HK", 
                 ktype: str = "day", count: int = 100, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """获取K线数据"""
        # 检查缓存
        if use_cache:
            cache_key = self._get_cache_key('kline', symbol, market, ktype, count)
            cached = self._load_from_cache(cache_key)
            if cached:
                # 将缓存数据转换为DataFrame
                if isinstance(cached, list):
                    return pd.DataFrame(cached)
                return cached
        
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # K线类型映射
            ktype_map = {
                '1m': (ft.KLType.K_1M, ft.SubType.K_1M),
                '5m': (ft.KLType.K_5M, ft.SubType.K_5M),
                '15m': (ft.KLType.K_15M, ft.SubType.K_15M),
                '30m': (ft.KLType.K_30M, ft.SubType.K_30M),
                '60m': (ft.KLType.K_60M, ft.SubType.K_60M),
                'day': (ft.KLType.K_DAY, ft.SubType.K_DAY),
                'week': (ft.KLType.K_WEEK, ft.SubType.K_WEEK),
                'month': (ft.KLType.K_MON, ft.SubType.K_MON),
            }
            
            ft_ktype, ft_subtype = ktype_map.get(ktype, (ft.KLType.K_DAY, ft.SubType.K_DAY))
            
            # 订阅并获取K线
            ret_sub, _ = self.quote_ctx.subscribe([code], [ft_subtype])
            if ret_sub != ft.RET_OK:
                return None
            
            ret, data = self.quote_ctx.get_cur_kline(code, count, ft_ktype)
            
            if ret == ft.RET_OK:
                # 保存到缓存
                if use_cache:
                    cache_key = self._get_cache_key('kline', symbol, market, ktype, count)
                    # 将DataFrame转换为可序列化的字典列表
                    if isinstance(data, pd.DataFrame):
                        cache_data = data.to_dict('records')
                        self._save_to_cache(cache_key, cache_data)
                
                return data
                
        except Exception as e:
            print(f"获取K线失败: {e}")
        
        return None
    
    def get_indicators(self, kline_data: pd.DataFrame) -> Dict:
        """计算技术指标"""
        if kline_data is None or len(kline_data) == 0:
            return {}
        
        try:
            indicators = {}
            
            # 移动平均线
            closes = kline_data['close']
            if len(closes) >= 5:
                indicators['ma5'] = closes.rolling(5).mean().iloc[-1]
            if len(closes) >= 10:
                indicators['ma10'] = closes.rolling(10).mean().iloc[-1]
            if len(closes) >= 20:
                indicators['ma20'] = closes.rolling(20).mean().iloc[-1]
            
            # RSI
            if len(closes) >= 14:
                delta = closes.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]
            
            # 布林带
            if len(closes) >= 20:
                ma20 = closes.rolling(20).mean()
                std20 = closes.rolling(20).std()
                indicators['bb_upper'] = (ma20 + 2 * std20).iloc[-1]
                indicators['bb_middle'] = ma20.iloc[-1]
                indicators['bb_lower'] = (ma20 - 2 * std20).iloc[-1]
            
            # 价格统计
            indicators['current'] = closes.iloc[-1]
            indicators['high'] = kline_data['high'].max()
            indicators['low'] = kline_data['low'].min()
            
            return indicators
            
        except Exception as e:
            print(f"计算指标失败: {e}")
            return {}
    
    def get_plates(self, market: str = "HK") -> Optional[pd.DataFrame]:
        """获取板块列表"""
        if not self.connected:
            return None
        
        try:
            ft_market = ft.Market.HK if market == "HK" else ft.Market.US
            ret, data = self.quote_ctx.get_plate_list(ft_market, ft.Plate.ALL)
            
            if ret == ft.RET_OK:
                return data
                
        except Exception as e:
            print(f"获取板块失败: {e}")
        
        return None
    
    def get_ticker(self, symbol: str, market: str = "HK", count: int = 10) -> Optional[pd.DataFrame]:
        """获取逐笔成交"""
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            ret_sub, _ = self.quote_ctx.subscribe([code], [ft.SubType.TICKER])
            if ret_sub != ft.RET_OK:
                return None
            
            ret, data = self.quote_ctx.get_rt_ticker(code, count)
            
            if ret == ft.RET_OK:
                return data
                
        except Exception as e:
            print(f"获取逐笔失败: {e}")
        
        return None
    
    def get_capital_flow(self, symbol: str, market: str = "HK") -> Optional[Dict]:
        """获取资金流向数据"""
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # 获取资金流向
            ret, data = self.quote_ctx.get_capital_flow(code)
            
            if ret == ft.RET_OK and len(data) > 0:
                # 获取最新数据
                row = data.iloc[-1]  # 最新数据在最后
                
                # 解析资金流向数据（根据实际API字段）
                capital_data = {
                    'symbol': symbol,
                    'market': market,
                    'in_flow': float(row.get('in_flow', 0)),          # 总流入
                    'super_in_flow': float(row.get('super_in_flow', 0)),  # 超大单流入
                    'big_in_flow': float(row.get('big_in_flow', 0)),      # 大单流入
                    'mid_in_flow': float(row.get('mid_in_flow', 0)),      # 中单流入
                    'sml_in_flow': float(row.get('sml_in_flow', 0)),      # 小单流入
                    'last_valid_time': str(row.get('last_valid_time', '')),  # 最后有效时间
                    'capital_flow_item_time': str(row.get('capital_flow_item_time', '')),  # 资金流向时间
                    'updated': datetime.now().isoformat()
                }
                
                # 计算各类资金净流入
                # 主力资金 = 超大单 + 大单
                capital_data['main_inflow'] = capital_data['super_in_flow'] + capital_data['big_in_flow']
                # 散户资金 = 中单 + 小单
                capital_data['retail_inflow'] = capital_data['mid_in_flow'] + capital_data['sml_in_flow']
                
                # 计算资金情绪
                total_inflow = abs(capital_data['main_inflow']) + abs(capital_data['retail_inflow'])
                if total_inflow > 0:
                    main_ratio = capital_data['main_inflow'] / total_inflow * 100
                    capital_data['main_ratio'] = main_ratio
                    
                    # 资金情绪判断
                    if capital_data['main_inflow'] > 0 and capital_data['main_ratio'] > 60:
                        capital_data['sentiment'] = '积极'
                    elif capital_data['main_inflow'] < 0 and capital_data['main_ratio'] > 60:
                        capital_data['sentiment'] = '谨慎'
                    else:
                        capital_data['sentiment'] = '中性'
                else:
                    capital_data['sentiment'] = '中性'
                
                return capital_data
                
        except Exception as e:
            print(f"获取资金流向失败: {e}")
        
        return None
    
    def get_market_state(self, market: str = "HK") -> Optional[Dict]:
        """获取市场状态"""
        if not self.connected:
            return None
        
        try:
            # 获取全局状态
            ret, data = self.quote_ctx.get_global_state()
            
            if ret == ft.RET_OK and isinstance(data, dict):
                # 市场状态映射
                state_map = {
                    'MORNING': '早市',
                    'REST': '午休',
                    'AFTERNOON': '午市',
                    'CLOSED': '收市',
                    'PRE_MARKET_BEGIN': '开市前',
                    'PRE_MARKET_END': '开市前结束',
                    'AFTER_MARKET_BEGIN': '收市后',
                    'AFTER_MARKET_END': '收市后结束',
                    'NIGHT_OPEN': '夜盘',
                    'NIGHT_END': '夜盘结束',
                    'FUTURE_OPEN': '期货开市',
                    'FUTURE_BREAK': '期货休市',
                    'FUTURE_CLOSE': '期货收市'
                }
                
                # 获取对应市场状态
                market_key = f'market_{market.lower()}'
                if market_key in data:
                    state_str = data[market_key]
                else:
                    # 默认值
                    market_key = 'market_hk'
                    state_str = data.get(market_key, 'CLOSED')
                
                # 判断是否开市
                is_open = state_str in ['MORNING', 'AFTERNOON', 'NIGHT_OPEN', 'FUTURE_OPEN']
                
                return {
                    'market': market,
                    'state_raw': state_str,
                    'state': state_map.get(state_str, state_str),
                    'is_open': is_open,
                    'update_time': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"获取市场状态失败: {e}")
        
        return None
    
    def get_stock_info(self, symbol: str, market: str = "HK") -> Optional[Dict]:
        """获取股票基础信息"""
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # 获取股票基础信息
            ret, data = self.quote_ctx.get_stock_basicinfo(ft.Market.HK if market == "HK" else ft.Market.US, 
                                                          ft.SecurityType.STOCK, [code])
            
            if ret == ft.RET_OK and len(data) > 0:
                row = data.iloc[0]
                
                return {
                    'symbol': symbol,
                    'market': market,
                    'name': row['name'],
                    'lot_size': int(row['lot_size']),
                    'stock_type': row['stock_type'],
                    'stock_child_type': row['stock_child_type'],
                    'listing_date': str(row['listing_date']) if pd.notna(row['listing_date']) else None,
                    'stock_id': int(row['stock_id']),
                    'updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"获取股票信息失败: {e}")
        
        return None
    
    def get_market_snapshot(self, symbols: List[str], market: str = "HK") -> Optional[List[Dict]]:
        """批量获取多只股票市场快照"""
        if not self.connected:
            return None
        
        try:
            codes = [f"{market}.{symbol}" if '.' not in symbol else symbol for symbol in symbols]
            
            # 获取市场快照
            ret, data = self.quote_ctx.get_market_snapshot(codes)
            
            if ret == ft.RET_OK and len(data) > 0:
                snapshots = []
                for _, row in data.iterrows():
                    # 提取股票代码
                    code = row['code']
                    symbol = code.split('.')[-1] if '.' in code else code
                    
                    # 计算涨跌幅
                    last_price = row['last_price']
                    prev_close = row['prev_close_price']
                    change = last_price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
                    
                    snapshot = {
                        'symbol': symbol,
                        'market': market,
                        'price': last_price,
                        'change': change,
                        'change_percent': change_percent,
                        'open': row['open_price'],
                        'high': row['high_price'],
                        'low': row['low_price'],
                        'volume': int(row['volume']),
                        'turnover': row['turnover'],
                        'turnover_rate': row.get('turnover_rate', 0),
                        'amplitude': row.get('amplitude', 0),
                        'time': row['update_time'],  # 修正字段名
                        'updated': datetime.now().isoformat()
                    }
                    snapshots.append(snapshot)
                
                return snapshots
                
        except Exception as e:
            print(f"获取市场快照失败: {e}")
        
        return None
    
    def get_order_book(self, symbol: str, market: str = "HK", depth: int = 10) -> Optional[Dict]:
        """获取摆盘数据（深度盘口）"""
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # 订阅并获取摆盘数据
            ret_sub, _ = self.quote_ctx.subscribe([code], [ft.SubType.ORDER_BOOK])
            if ret_sub != ft.RET_OK:
                return None
            
            ret, data = self.quote_ctx.get_order_book(code)
            
            if ret == ft.RET_OK and isinstance(data, dict):
                # 解析买盘数据
                bid_data = []
                if 'Bid' in data and isinstance(data['Bid'], list):
                    for i, bid in enumerate(data['Bid'][:depth]):
                        if len(bid) >= 2:  # (价格, 数量, ...)
                            bid_data.append({
                                'price': float(bid[0]),
                                'volume': int(bid[1]),
                                'order_count': bid[2] if len(bid) > 2 else 0
                            })
                
                # 解析卖盘数据
                ask_data = []
                if 'Ask' in data and isinstance(data['Ask'], list):
                    for i, ask in enumerate(data['Ask'][:depth]):
                        if len(ask) >= 2:
                            ask_data.append({
                                'price': float(ask[0]),
                                'volume': int(ask[1]),
                                'order_count': ask[2] if len(ask) > 2 else 0
                            })
                
                return {
                    'symbol': symbol,
                    'market': market,
                    'bids': bid_data,  # 买盘列表
                    'asks': ask_data,  # 卖盘列表
                    'bid_count': len(bid_data),
                    'ask_count': len(ask_data),
                    'updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"获取摆盘数据失败: {e}")
        
        return None
    
    def get_capital_distribution(self, symbol: str, market: str = "HK") -> Optional[Dict]:
        """获取资金分布数据"""
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # 获取资金分布
            ret, data = self.quote_ctx.get_capital_distribution(code)
            
            if ret == ft.RET_OK and len(data) > 0:
                row = data.iloc[0]
                
                # 计算各类资金净流入
                super_net = row.get('capital_in_super', 0) - row.get('capital_out_super', 0)
                big_net = row.get('capital_in_big', 0) - row.get('capital_out_big', 0)
                mid_net = row.get('capital_in_mid', 0) - row.get('capital_out_mid', 0)
                small_net = row.get('capital_in_small', 0) - row.get('capital_out_small', 0)
                
                # 计算总流入和总流出
                total_in = row.get('capital_in_super', 0) + row.get('capital_in_big', 0) + \
                          row.get('capital_in_mid', 0) + row.get('capital_in_small', 0)
                total_out = row.get('capital_out_super', 0) + row.get('capital_out_big', 0) + \
                           row.get('capital_out_mid', 0) + row.get('capital_out_small', 0)
                total_net = total_in - total_out
                
                distribution = {
                    'symbol': symbol,
                    'market': market,
                    'super_in': float(row.get('capital_in_super', 0)),      # 超大单流入
                    'super_out': float(row.get('capital_out_super', 0)),    # 超大单流出
                    'super_net': float(super_net),                          # 超大单净流入
                    'big_in': float(row.get('capital_in_big', 0)),          # 大单流入
                    'big_out': float(row.get('capital_out_big', 0)),        # 大单流出
                    'big_net': float(big_net),                              # 大单净流入
                    'mid_in': float(row.get('capital_in_mid', 0)),          # 中单流入
                    'mid_out': float(row.get('capital_out_mid', 0)),        # 中单流出
                    'mid_net': float(mid_net),                              # 中单净流入
                    'small_in': float(row.get('capital_in_small', 0)),      # 小单流入
                    'small_out': float(row.get('capital_out_small', 0)),    # 小单流出
                    'small_net': float(small_net),                          # 小单净流入
                    'total_in': float(total_in),                            # 总流入
                    'total_out': float(total_out),                          # 总流出
                    'total_net': float(total_net),                          # 总净流入
                    'update_time': str(row.get('update_time', '')),         # 更新时间
                    'updated': datetime.now().isoformat()
                }
                
                # 计算百分比
                if total_in + total_out > 0:
                    distribution['super_ratio'] = abs(super_net) / (abs(total_net) or 1) * 100
                    distribution['big_ratio'] = abs(big_net) / (abs(total_net) or 1) * 100
                    distribution['mid_ratio'] = abs(mid_net) / (abs(total_net) or 1) * 100
                    distribution['small_ratio'] = abs(small_net) / (abs(total_net) or 1) * 100
                
                return distribution
                
        except Exception as e:
            print(f"获取资金分布失败: {e}")
        
        return None
    
    def get_plate_stocks(self, plate_code: str) -> Optional[List[Dict]]:
        """获取板块成分股"""
        if not self.connected:
            return None
        
        try:
            # 获取板块成分股
            ret, data = self.quote_ctx.get_plate_stock(plate_code)
            
            if ret == ft.RET_OK and len(data) > 0:
                stocks = []
                for _, row in data.iterrows():
                    code = row['code']
                    symbol = code.split('.')[-1] if '.' in code else code
                    market = code.split('.')[0] if '.' in code else 'HK'
                    
                    stock = {
                        'symbol': symbol,
                        'market': market,
                        'name': row['stock_name'],  # 修正字段名
                        'plate_code': plate_code,
                        'lot_size': int(row.get('lot_size', 0)),
                        'stock_type': row.get('stock_type', ''),
                        'list_time': str(row.get('list_time', '')),
                        'updated': datetime.now().isoformat()
                    }
                    stocks.append(stock)
                
                return stocks
                
        except Exception as e:
            print(f"获取板块成分股失败: {e}")
        
        return None
    
    def get_owner_plates(self, symbol: str, market: str = "HK") -> Optional[List[Dict]]:
        """获取股票所属板块"""
        if not self.connected:
            return None
        
        try:
            code = f"{market}.{symbol}" if '.' not in symbol else symbol
            
            # 获取所属板块
            ret, data = self.quote_ctx.get_owner_plate(code)
            
            if ret == ft.RET_OK and len(data) > 0:
                plates = []
                for _, row in data.iterrows():
                    plate = {
                        'symbol': symbol,
                        'market': market,
                        'plate_code': row['plate_code'],
                        'plate_name': row['plate_name'],
                        'plate_type': row.get('plate_type', ''),
                        'updated': datetime.now().isoformat()
                    }
                    plates.append(plate)
                
                return plates
                
        except Exception as e:
            print(f"获取所属板块失败: {e}")
        
        return None

def format_output(data: Union[Dict, pd.DataFrame], fmt: str = "table") -> str:
    """格式化输出"""
    if fmt == "json":
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient='records', force_ascii=False, indent=2)
        else:
            return json.dumps(data, ensure_ascii=False, indent=2)
    
    elif fmt == "table":
        if isinstance(data, pd.DataFrame):
            return data.to_string()
        elif isinstance(data, dict):
            output = []
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    if abs(value) >= 1000:
                        value_str = f"{value:,.2f}"
                    else:
                        value_str = f"{value:.4f}"
                else:
                    value_str = str(value)
                output.append(f"{key:15}: {value_str}")
            return "\n".join(output)
    
    return str(data)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="富途API数据工具")
    parser.add_argument("command", help="命令: quote, kline, indicators, plates, ticker, capital, market, info, snapshot, orderbook, capdist, platestocks, ownerplates")
    parser.add_argument("symbol", nargs="?", help="股票代码")
    parser.add_argument("--market", default="HK", help="市场: HK, US")
    parser.add_argument("--type", default="day", help="K线类型: 1m,5m,15m,30m,60m,day,week,month")
    parser.add_argument("--count", type=int, default=100, help="数据条数")
    parser.add_argument("--format", default="table", help="输出格式: table, json")
    parser.add_argument("--depth", type=int, default=5, help="摆盘深度")
    
    args = parser.parse_args()
    
    # 创建客户端
    api = FutuAPI()
    
    if not api.connect():
        print("❌ 无法连接富途，请检查FutuOpenD是否运行")
        return
    
    try:
        if args.command == "quote":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_quote(args.symbol, args.market)
            if data:
                print(format_output(data, args.format))
            else:
                print("❌ 获取行情失败")
        
        elif args.command == "kline":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_kline(args.symbol, args.market, args.type, args.count)
            if data is not None:
                print(format_output(data, args.format))
            else:
                print("❌ 获取K线失败")
        
        elif args.command == "indicators":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            kline = api.get_kline(args.symbol, args.market, args.type, args.count)
            if kline is not None:
                indicators = api.get_indicators(kline)
                if indicators:
                    print(f"{args.symbol} 技术指标:")
                    print(format_output(indicators, args.format))
                else:
                    print("❌ 计算指标失败")
            else:
                print("❌ 获取K线失败")
        
        elif args.command == "plates":
            data = api.get_plates(args.market)
            if data is not None:
                print(f"{args.market}市场板块列表:")
                print(format_output(data.head(20), args.format))
            else:
                print("❌ 获取板块失败")
        
        elif args.command == "ticker":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_ticker(args.symbol, args.market, args.count)
            if data is not None:
                print(f"{args.symbol} 最近成交:")
                print(format_output(data, args.format))
            else:
                print("❌ 获取逐笔失败")
        
        elif args.command == "capital":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_capital_flow(args.symbol, args.market)
            if data:
                print(f"{args.symbol} 资金流向:")
                print(format_output(data, args.format))
            else:
                print("❌ 获取资金流向失败")
        
        elif args.command == "market":
            data = api.get_market_state(args.market)
            if data:
                print(f"{args.market}市场状态:")
                print(format_output(data, args.format))
                
                # 额外提示
                if data['is_open']:
                    print("✅ 市场正在交易中")
                else:
                    print("⏸️  市场休市中")
            else:
                print("❌ 获取市场状态失败")
        
        elif args.command == "info":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_stock_info(args.symbol, args.market)
            if data:
                print(f"{args.symbol} 股票信息:")
                print(format_output(data, args.format))
            else:
                print("❌ 获取股票信息失败")
        
        elif args.command == "snapshot":
            if not args.symbol:
                print("❌ 请提供股票代码（多个用逗号分隔）")
                return
            
            symbols = [s.strip() for s in args.symbol.split(',')]
            data = api.get_market_snapshot(symbols, args.market)
            if data:
                print(f"市场快照 ({len(symbols)}只股票):")
                for item in data:
                    print(f"\n{item['symbol']}:")
                    print(f"  价格: {item['price']:.2f} ({item['change_percent']:+.2f}%)")
                    print(f"  成交量: {item['volume']:,}")
            else:
                print("❌ 获取市场快照失败")
        
        elif args.command == "orderbook":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_order_book(args.symbol, args.market, args.depth)
            if data:
                print(f"{args.symbol} 摆盘数据 (深度{args.depth}):")
                print("\n买盘 (Bids):")
                for i, bid in enumerate(data['bids']):
                    print(f"  买{i+1}: {bid['price']:.2f} × {bid['volume']:,}")
                
                print("\n卖盘 (Asks):")
                for i, ask in enumerate(data['asks']):
                    print(f"  卖{i+1}: {ask['price']:.2f} × {ask['volume']:,}")
                
                print(f"\n买盘档位: {data['bid_count']}, 卖盘档位: {data['ask_count']}")
            else:
                print("❌ 获取摆盘数据失败")
        
        elif args.command == "capdist":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_capital_distribution(args.symbol, args.market)
            if data:
                print(f"{args.symbol} 资金分布:")
                print(f"超大单: 流入{data.get('super_in', 0):,.0f} 流出{data.get('super_out', 0):,.0f} 净流入{data.get('super_net', 0):+,.0f}")
                print(f"大单:   流入{data.get('big_in', 0):,.0f} 流出{data.get('big_out', 0):,.0f} 净流入{data.get('big_net', 0):+,.0f}")
                print(f"中单:   流入{data.get('mid_in', 0):,.0f} 流出{data.get('mid_out', 0):,.0f} 净流入{data.get('mid_net', 0):+,.0f}")
                print(f"小单:   流入{data.get('small_in', 0):,.0f} 流出{data.get('small_out', 0):,.0f} 净流入{data.get('small_net', 0):+,.0f}")
                print(f"总计:   流入{data.get('total_in', 0):,.0f} 流出{data.get('total_out', 0):,.0f} 净流入{data.get('total_net', 0):+,.0f}")
                print(f"更新时间: {data.get('update_time', '未知')}")
            else:
                print("❌ 获取资金分布失败")
        
        elif args.command == "platestocks":
            if not args.symbol:
                print("❌ 请提供板块代码（如 HK.BK1001）")
                return
            
            data = api.get_plate_stocks(args.symbol)
            if data:
                print(f"板块 {args.symbol} 成分股 ({len(data)}只):")
                for i, stock in enumerate(data[:20]):  # 显示前20只
                    print(f"  {i+1:2d}. {stock['symbol']} - {stock['name']}")
                if len(data) > 20:
                    print(f"  ... 还有 {len(data)-20} 只股票")
            else:
                print("❌ 获取板块成分股失败")
        
        elif args.command == "ownerplates":
            if not args.symbol:
                print("❌ 请提供股票代码")
                return
            
            data = api.get_owner_plates(args.symbol, args.market)
            if data:
                print(f"{args.symbol} 所属板块 ({len(data)}个):")
                for plate in data:
                    print(f"  • {plate['plate_name']} ({plate['plate_code']})")
            else:
                print("❌ 获取所属板块失败")
        
        else:
            print(f"❌ 未知命令: {args.command}")
            print("可用命令: quote, kline, indicators, plates, ticker, capital, market, info, snapshot, orderbook, capdist, platestocks, ownerplates")
    
    finally:
        api.disconnect()

if __name__ == "__main__":
    main()