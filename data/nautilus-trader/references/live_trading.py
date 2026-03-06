#!/usr/bin/env python3
"""
Minimal live trading example with Nautilus Trader + Hyperliquid.
"""

import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# CRITICAL: Import patch BEFORE Nautilus
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hyperliquid_patch

from nautilus_trader.adapters.hyperliquid import (
    HYPERLIQUID,
    HyperliquidDataClientConfig,
    HyperliquidExecClientConfig,
    HyperliquidLiveDataClientFactory,
    HyperliquidLiveExecClientFactory,
)
from nautilus_trader.live.node import TradingNode, TradingNodeConfig
from nautilus_trader.config import LiveDataEngineConfig, LiveExecEngineConfig
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.enums import OrderSide, TimeInForce


class SimpleStrategyConfig(StrategyConfig):
    instrument_id: str
    trade_size: Decimal = Decimal("0.1")


class SimpleStrategy(Strategy):
    """Minimal strategy that places a single order on start."""

    def __init__(self, config: SimpleStrategyConfig):
        super().__init__(config)
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.trade_size = config.trade_size
        self.order_placed = False

    def on_start(self):
        self.instrument = self.cache.instrument(self.instrument_id)
        self.log.info(f"Strategy started for {self.instrument_id}")

    def on_bar(self, bar: Bar):
        if not self.order_placed:
            self._place_test_order()
            self.order_placed = True

    def _place_test_order(self):
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.trade_size),
            time_in_force=TimeInForce.IOC,
        )
        self.submit_order(order)
        self.log.info(f"Submitted: {order}")


def main():
    vault = os.getenv("HYPERLIQUID_VAULT")
    pk = os.getenv("HYPERLIQUID_PK")

    if not vault or not pk:
        print("Set HYPERLIQUID_VAULT and HYPERLIQUID_PK")
        return

    node_config = TradingNodeConfig(
        trader_id="LIVE-001",
        data_engine=LiveDataEngineConfig(),
        exec_engine=LiveExecEngineConfig(),
    )

    node = TradingNode(config=node_config)

    data_config = HyperliquidDataClientConfig(
        wallet_address=vault,
        is_testnet=False,
    )

    exec_config = HyperliquidExecClientConfig(
        wallet_address=vault,
        private_key=pk,
        is_testnet=False,
    )

    node.add_data_client_factory(HYPERLIQUID, HyperliquidLiveDataClientFactory)
    node.add_exec_client_factory(HYPERLIQUID, HyperliquidLiveExecClientFactory)
    node.build()

    strategy_config = SimpleStrategyConfig(
        instrument_id="SOL-USD.HYPERLIQUID",
        trade_size=Decimal("0.1"),
    )

    strategy = SimpleStrategy(config=strategy_config)
    node.trader.add_strategy(strategy)

    try:
        node.run()
    except KeyboardInterrupt:
        node.dispose()


if __name__ == "__main__":
    main()
