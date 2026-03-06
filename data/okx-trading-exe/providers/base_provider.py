from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseProvider(ABC):
    """
    TAS-20 标准: 执行手柄抽象层 (Executor Interface)
    所有具体的交易所/回测引擎插件都必须继承并实现此接口。
    这保证了外层在使用 trading_exe 时，无论底层连向哪，API 始终一致。
    """
    
    @abstractmethod
    def get_cash(self) -> float:
        """获取当前账户可用资金 (如可用 USDT 余额)"""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        获取当前账户所有的持有仓位。
        返回的数据结构示例:
        [
            {"symbol": "BTC-USDT", "size": 1.5, "avg_price": 50000, "unrealized_pnl": 1500},
            ...
        ]
        """
        pass

    @abstractmethod
    def place_market_order(self, symbol: str, side: str, size: float) -> Dict[str, Any]:
        """
        下达市价单。
        对于 BUY 操作，size 可能代表花费的 USDT。
        对于 SELL 操作，size 通常代表卖出的基础币种数量。
        
        Args:
            symbol: 交易对 (e.g., 'BTC-USDT')
            side: 方向 ('buy' 或 'sell')
            size: 下单数量或金额
            
        Returns:
            Dict: 必须包含 'order_id' 以及 'status' ('submitted', 'rejected' 等)
        """
        pass

    @abstractmethod
    def place_limit_order(self, symbol: str, side: str, size: float, price: float) -> Dict[str, Any]:
        """
        下达限价单。
        """
        pass

    @abstractmethod
    def get_recent_trades(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取最近在该交易对的历史成交记录。
        """
        pass
