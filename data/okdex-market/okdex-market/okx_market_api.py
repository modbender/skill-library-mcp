#!/usr/bin/env python3
"""
OKX Web3 Wallet Market API Python SDK
用于调用 OKX Market API 获取代币价格、K线、交易等数据
"""

import requests
import hmac
import hashlib
import base64
from datetime import datetime, timezone
import json
from typing import List, Dict, Optional


class OKXMarketAPI:
    """OKX Web3 Wallet Market API 客户端"""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        """
        初始化 API 客户端
        
        Args:
            api_key: OKX API Key
            secret_key: OKX Secret Key
            passphrase: OKX Passphrase
        """
        self.base_url = "https://web3.okx.com"
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
    
    def _get_timestamp(self) -> str:
        """获取 ISO 8601 格式时间戳"""
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _sign(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """
        生成请求签名
        
        Args:
            timestamp: ISO 8601 时间戳
            method: HTTP 方法 (GET/POST)
            request_path: 请求路径
            body: 请求体 (POST 请求)
        
        Returns:
            Base64 编码的签名
        """
        message = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')
    
    def _headers(self, method: str, request_path: str, body: str = '') -> Dict[str, str]:
        """生成请求头"""
        timestamp = self._get_timestamp()
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': self._sign(timestamp, method, request_path, body),
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
    
    def _get(self, path: str) -> Dict:
        """发送 GET 请求"""
        headers = self._headers('GET', path)
        response = requests.get(self.base_url + path, headers=headers)
        return response.json()
    
    def _post(self, path: str, data: List[Dict]) -> Dict:
        """发送 POST 请求"""
        body = json.dumps(data)
        headers = self._headers('POST', path, body)
        response = requests.post(self.base_url + path, headers=headers, data=body)
        return response.json()

    # ==================== 行情价格 API ====================
    
    def get_candlesticks(
        self,
        chain_index: str,
        token_address: str,
        bar: str = '1m',
        limit: int = 100,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict:
        """
        获取 K 线数据
        
        Args:
            chain_index: 链标识 (如 "1" 表示 Ethereum)
            token_address: 代币合约地址
            bar: K 线周期 (1s/1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M)
            limit: 返回数量 (最大 299)
            after: 返回该时间戳之前的数据
            before: 返回该时间戳之后的数据
        
        Returns:
            K 线数据列表 [ts, o, h, l, c, vol, volUsd, confirm]
        """
        path = f'/api/v6/dex/market/candles?chainIndex={chain_index}&tokenContractAddress={token_address}&bar={bar}&limit={limit}'
        if after:
            path += f'&after={after}'
        if before:
            path += f'&before={before}'
        return self._get(path)
    
    def get_candlesticks_history(
        self,
        chain_index: str,
        token_address: str,
        bar: str = '1m',
        limit: int = 100
    ) -> Dict:
        """
        获取历史 K 线数据 (不包含未完成的 K 线)
        
        Args:
            chain_index: 链标识
            token_address: 代币合约地址
            bar: K 线周期
            limit: 返回数量
        
        Returns:
            历史 K 线数据
        """
        path = f'/api/v6/dex/market/historical-candles?chainIndex={chain_index}&tokenContractAddress={token_address}&bar={bar}&limit={limit}'
        return self._get(path)
    
    def get_trades(self, chain_index: str, token_address: str) -> Dict:
        """
        获取最近交易记录
        
        Args:
            chain_index: 链标识
            token_address: 代币合约地址
        
        Returns:
            交易记录列表
        """
        path = f'/api/v6/dex/market/trades?chainIndex={chain_index}&tokenContractAddress={token_address}'
        return self._get(path)

    # ==================== 综合币价 API ====================
    
    def get_index_price(self, tokens: List[Dict[str, str]]) -> Dict:
        """
        获取代币指数价格 (聚合多数据源)
        
        Args:
            tokens: 代币列表，每个元素包含:
                - chainIndex: 链标识
                - tokenContractAddress: 代币地址 (空字符串表示原生代币)
        
        Returns:
            代币价格信息
        
        Example:
            api.get_index_price([
                {"chainIndex": "1", "tokenContractAddress": ""},  # ETH
                {"chainIndex": "1", "tokenContractAddress": "0x..."}  # ERC20
            ])
        """
        return self._post('/api/v6/dex/index/current-price', tokens)
    
    def get_historical_index_price(
        self,
        chain_index: str,
        token_address: str = '',
        limit: int = 100,
        begin: Optional[str] = None,
        period: str = '1m'
    ) -> Dict:
        """
        获取历史指数价格
        
        Args:
            chain_index: 链标识
            token_address: 代币地址
            limit: 返回数量
            begin: 开始时间 (Unix 毫秒时间戳)
            period: 周期 (1m/5m/15m/30m/1H/4H/1D)
        
        Returns:
            历史价格数据
        """
        path = f'/api/v6/dex/index/historical-price?chainIndex={chain_index}&limit={limit}&period={period}'
        if token_address:
            path += f'&tokenContractAddress={token_address}'
        if begin:
            path += f'&begin={begin}'
        return self._get(path)

    # ==================== 代币 API ====================
    
    def search_token(self, chains: str, keyword: str) -> Dict:
        """
        搜索代币
        
        Args:
            chains: 链标识，多个用逗号分隔 (如 "1,10,56")
            keyword: 搜索关键词 (名称/符号/地址)
        
        Returns:
            匹配的代币列表
        """
        path = f'/api/v6/dex/market/token/search?chains={chains}&search={keyword}'
        return self._get(path)
    
    def get_token_basic_info(self, tokens: List[Dict[str, str]]) -> Dict:
        """
        获取代币基本信息
        
        Args:
            tokens: 代币列表，每个元素包含:
                - chainIndex: 链标识
                - tokenContractAddress: 代币合约地址
        
        Returns:
            代币基本信息 (名称、符号、精度、图标等)
        """
        return self._post('/api/v6/dex/market/token/basic-info', tokens)
    
    def get_token_trading_info(self, tokens: List[Dict[str, str]]) -> Dict:
        """
        获取代币交易信息 (价格、交易量、市值、流动性等)
        
        Args:
            tokens: 代币列表 (最多 100 个)，每个元素包含:
                - chainIndex: 链标识
                - tokenContractAddress: 代币合约地址
        
        Returns:
            代币详细交易信息
        """
        return self._post('/api/v6/dex/market/price-info', tokens)


# 常用链标识
CHAIN_INDEX = {
    'BITCOIN': '0',
    'ETHEREUM': '1',
    'OPTIMISM': '10',
    'BSC': '56',
    'OKX': '66',
    'POLYGON': '137',
    'ZKSYNC': '324',
    'SOLANA': '501',
    'ARBITRUM': '42161',
    'AVALANCHE': '43114',
}


def main():
    """使用示例"""
    import os
    
    # 从环境变量获取 API 凭证
    api_key = os.environ.get('OKX_API_KEY', 'your-api-key')
    secret_key = os.environ.get('OKX_SECRET_KEY', 'your-secret-key')
    passphrase = os.environ.get('OKX_PASSPHRASE', 'your-passphrase')
    
    api = OKXMarketAPI(api_key, secret_key, passphrase)
    
    # 示例 1: 搜索 WETH
    print("=== 搜索 WETH ===")
    result = api.search_token("1,10", "weth")
    if result.get('code') == '0':
        for token in result.get('data', [])[:3]:
            print(f"  {token['tokenSymbol']}: ${token.get('price', 'N/A')}")
    
    # 示例 2: 获取 ETH 指数价格
    print("\n=== ETH 指数价格 ===")
    result = api.get_index_price([
        {"chainIndex": "1", "tokenContractAddress": ""}
    ])
    if result.get('code') == 0:
        for item in result.get('data', []):
            print(f"  价格: ${item['price']}")
    
    # 示例 3: 获取代币交易信息
    print("\n=== 代币交易信息 ===")
    result = api.get_token_trading_info([
        {"chainIndex": "501", "tokenContractAddress": "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp"}
    ])
    if result.get('code') == '0':
        for token in result.get('data', []):
            print(f"  价格: ${token['price']}")
            print(f"  24H 涨跌: {token['priceChange24H']}%")
            print(f"  市值: ${token['marketCap']}")


if __name__ == "__main__":
    main()
