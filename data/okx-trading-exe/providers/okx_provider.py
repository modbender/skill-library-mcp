import hmac
import hashlib
import base64
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .base_provider import BaseProvider

class OKXClient:
    """内部轻量级的 OKX API 客户端 (无行情与复杂依赖)"""
    def __init__(self, api_key: str, api_secret: str, passphrase: str, is_demo: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.is_demo = is_demo
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()

    def _get_timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _sign(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        message = timestamp + method.upper() + request_path + body
        mac = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')
    
    def request(self, method: str, path: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Optional[Dict]:
        url = self.base_url + path
        request_path = path
        
        if method == 'GET' and params:
            from urllib.parse import urlencode
            query = urlencode(params)
            request_path += f"?{query}"
            
        body_str = json.dumps(body) if body else ""
        timestamp = self._get_timestamp()
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': self._sign(timestamp, method, request_path, body_str),
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        if self.is_demo:
            headers['x-simulated-trading'] = '1'
            
        try:
            if method == 'GET':
                resp = self.session.get(url, headers=headers, params=params, timeout=10)
            else:
                resp = self.session.post(url, headers=headers, data=body_str, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[OKX API Error] {e}")
            return None


class OKXProvider(BaseProvider):
    """
    OKX 执行提供者。实现了 BaseProvider 接口。
    """
    def __init__(self, api_key: str, api_secret: str, passphrase: str, is_demo: bool = True):
        self.client = OKXClient(api_key, api_secret, passphrase, is_demo)
        
    def _normalize_symbol(self, symbol: str) -> str:
        """统一交易对格式 (输入如 BTC/USDT 或 BTC-USDT，输出 BTC-USDT)"""
        return symbol.replace('/', '-')

    def get_cash(self) -> float:
        result = self.client.request('GET', '/api/v5/account/balance', {'ccy': 'USDT'})
        if result and result.get('code') == '0':
            for asset in result['data'][0].get('details', []):
                if asset['ccy'] == 'USDT':
                    return float(asset['availBal'])
        return 0.0

    def get_positions(self) -> List[Dict[str, Any]]:
        result = self.client.request('GET', '/api/v5/account/positions')
        positions = []
        if result and result.get('code') == '0':
            for pos in result.get('data', []):
                size = float(pos.get('pos', 0) or 0)
                if abs(size) < 1e-12: continue
                positions.append({
                    "symbol": pos.get('instId', ''),
                    "size": size,
                    "avg_price": float(pos.get('avgPx', 0) or 0),
                    "unrealized_pnl": float(pos.get('upl', 0) or 0),
                })
        return positions

    def place_market_order(self, symbol: str, side: str, size: float) -> Dict[str, Any]:
        """
        OKX 市价单：
        - side = 'buy' 时，如果 ccy='USDT'，sz 代表购买用的 USDT 金额
        - side = 'sell' 时，sz 代表卖出的基础货币数量
        """
        inst_id = self._normalize_symbol(symbol)
        side = side.lower()
        
        body = {
            'instId': inst_id,
            'tdMode': 'cash',
            'side': side,
            'ordType': 'market',
        }
        
        if side == 'buy':
            # 默认传入的 size 为报价币 USDT 的金额
            body['ccy'] = 'USDT'
            body['sz'] = f"{size:.2f}"
            if float(body['sz']) < 10:
                body['sz'] = "10.00"
        else:
            body['sz'] = f"{size:.8f}".rstrip('0').rstrip('.')
            if not body['sz'] or float(body['sz']) < 0.00001:
                body['sz'] = "0.00001"
                
        resp = self.client.request('POST', '/api/v5/trade/order', body=body)
        
        if resp and resp.get('code') == '0':
            return {"order_id": resp['data'][0]['ordId'], "status": "submitted"}
        
        reject_reason = resp.get('msg', 'Unknown Error') if resp else "Request Failed"
        return {"order_id": "", "status": "rejected", "reason": reject_reason}

    def place_limit_order(self, symbol: str, side: str, size: float, price: float) -> Dict[str, Any]:
        inst_id = self._normalize_symbol(symbol)
        side = side.lower()
        
        sz = f"{size:.8f}".rstrip('0').rstrip('.')
        if not sz or float(sz) < 0.00001:
            sz = "0.00001"
            
        body = {
            'instId': inst_id,
            'tdMode': 'cash',
            'side': side,
            'ordType': 'limit',
            'sz': sz,
            'px': str(price)
        }
        
        resp = self.client.request('POST', '/api/v5/trade/order', body=body)
        
        if resp and resp.get('code') == '0':
            return {"order_id": resp['data'][0]['ordId'], "status": "submitted"}
            
        reject_reason = resp.get('msg', 'Unknown Error') if resp else "Request Failed"
        return {"order_id": "", "status": "rejected", "reason": reject_reason}

    def get_recent_trades(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        inst_id = self._normalize_symbol(symbol)
        params = {
            'instType': 'SPOT',
            'instId': inst_id,
            'limit': str(limit)
        }
        resp = self.client.request('GET', '/api/v5/trade/orders-history', params)
        trades = []
        if resp and resp.get('code') == '0':
            for o in resp.get('data', []):
                side_val = (o.get('side') or '').upper()
                avg_px = float(o.get('avgPx') or o.get('px') or 0)
                fill_sz = float(o.get('fillSz', 0) or o.get('sz', 0) or 0)
                
                # 时间格式化
                c_time = int(o.get('cTime', 0))
                dt = datetime.fromtimestamp(c_time / 1000).isoformat() if c_time else datetime.now().isoformat()
                
                trades.append({
                    "order_id": o.get('ordId', ''),
                    "symbol": inst_id,
                    "side": side_val,
                    "price": avg_px,
                    "filled_size": fill_sz,
                    "state": o.get('state', ''),
                    "time": dt
                })
        return trades
