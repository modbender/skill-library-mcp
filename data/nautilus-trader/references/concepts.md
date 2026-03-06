# Nautilus_Trader - Concepts

**Pages:** 19

---

## Strategies

**URL:** https://nautilustrader.io/docs/latest/concepts/strategies

**Contents:**
- Strategies
- Strategy implementation​
  - Handlers​
    - Stateful actions​
    - Data handling​
    - Order management​
    - Position management​
    - Generic event handling​
    - Handler example​
  - Clock and timers​

The heart of the NautilusTrader user experience is in writing and working with trading strategies. Defining a strategy involves inheriting the Strategy class and implementing the methods required by the strategy's logic.

Relationship with actors: The Strategy class inherits from Actor, which means strategies have access to all actor functionality plus order management capabilities.

We recommend reviewing the Actors guide before diving into strategy development.

Strategies can be added to Nautilus systems in any environment contexts and will start sending commands and receiving events based on their logic as soon as the system starts.

Using the basic building blocks of data ingest, event handling, and order management (which we will discuss below), it's possible to implement any type of strategy including directional, momentum, re-balancing, pairs, market making etc.

See the Strategy API Reference for a complete description of all available methods.

There are two main parts of a Nautilus trading strategy:

Once a strategy is defined, the same source code can be used for backtesting and live trading.

The main capabilities of a strategy include:

Since a trading strategy is a class which inherits from Strategy, you must define a constructor where you can handle initialization. Minimally the base/super class needs to be initialized:

From here, you can implement handlers as necessary to perform actions based on state transitions and events.

Do not call components such as clock and logger in the __init__ constructor (which is prior to registration). This is because the systems clock and logging subsystem have not yet been initialized.

Handlers are methods within the Strategy class which may perform actions based on different types of events or on state changes. These methods are named with the prefix on_*. You can choose to implement any or all of these handler methods depending on the specific goals and needs of your strategy.

The purpose of having multiple handlers for similar types of events is to provide flexibility in handling granularity. This means that you can choose to respond to specific events with a dedicated handler, or use a more generic handler to react to a range of related events (using typical switch statement logic). The handlers are called in sequence from the most specific to the most general.

These handlers are triggered by lifecycle state changes of the Strategy. It's recommended to:

These handlers receive data updates, including built-in market data and custom user-defined data. You can use these handlers to define actions upon receiving data object instances.

These handlers receive events related to orders. OrderEvent type messages are passed to handlers in the following sequence:

These handlers receive events related to positions. PositionEvent type messages are passed to handlers in the following sequence:

This handler will eventually receive all event messages which arrive at the strategy, including those for which no other specific handler exists.

The following example shows a typical on_start handler method implementation (taken from the example EMA cross strategy). Here we can see the following:

Strategies have access to a Clock which provides a number of methods for creating different timestamps, as well as setting time alerts or timers to trigger TimeEvents.

See the Clock API reference for a complete list of available methods.

While there are multiple ways to obtain current timestamps, here are two commonly used methods as examples:

To get the current UTC timestamp as a tz-aware pd.Timestamp:

To get the current UTC timestamp as nanoseconds since the UNIX epoch:

Time alerts can be set which will result in a TimeEvent being dispatched to the on_event handler at the specified alert time. In a live context, this might be slightly delayed by a few microseconds.

This example sets a time alert to trigger one minute from the current time:

Continuous timers can be set up which will generate a TimeEvent at regular intervals until the timer expires or is canceled.

This example sets a timer to fire once per minute, starting immediately:

The trader instances central Cache can be accessed to fetch data and execution objects (orders, positions etc). There are many methods available often with filtering functionality, here we go through some basic use cases.

The following example shows how data can be fetched from the cache (assuming some instrument ID attribute is assigned):

The following example shows how individual order and position objects can be fetched from the cache:

See the Cache API Reference for a complete description of all available methods.

The traders central Portfolio can be accessed to fetch account and positional information. The following shows a general outline of available methods.

See the Portfolio API Reference for a complete description of all available methods.

The Portfolio also makes a PortfolioAnalyzer available, which can be fed with a flexible amount of data (to accommodate different lookback windows). The analyzer can provide tracking for and generating of performance metrics and statistics.

See the PortfolioAnalyzer API Reference for a complete description of all available methods.

See the Portfolio statistics guide.

NautilusTrader offers a comprehensive suite of trading commands, enabling granular order management tailored for algorithmic trading. These commands are essential for executing strategies, managing risk, and ensuring seamless interaction with various trading venues. In the following sections, we will delve into the specifics of each command and its use cases.

The Execution guide explains the flow through the system, and can be helpful to read in conjunction with the below.

An OrderFactory is provided on the base class for every Strategy as a convenience, reducing the amount of boilerplate required to create different Order objects (although these objects can still be initialized directly with the Order.__init__(...) constructor if the trader prefers).

The component a SubmitOrder or SubmitOrderList command will flow to for execution depends on the following:

This example submits a LIMIT BUY order for emulation (see Emulated Orders):

You can specify both order emulation and an execution algorithm.

This example submits a MARKET BUY order to a TWAP execution algorithm:

Orders can be canceled individually, as a batch, or all orders for an instrument (with an optional side filter).

If the order is already closed or already pending cancel, then a warning will be logged.

If the order is currently open then the status will become PENDING_CANCEL.

The component a CancelOrder, CancelAllOrders or BatchCancelOrders command will flow to for execution depends on the following:

Any managed GTD timer will also be canceled after the command has left the strategy.

The following shows how to cancel an individual order:

The following shows how to cancel a batch of orders:

The following shows how to cancel all orders:

Orders can be modified individually when emulated, or open on a venue (if supported).

If the order is already closed or already pending cancel, then a warning will be logged. If the order is currently open then the status will become PENDING_UPDATE.

At least one value must differ from the original order for the command to be valid.

The component a ModifyOrder command will flow to for execution depends on the following:

Once an order is under the control of an execution algorithm, it cannot be directly modified by a strategy (only canceled).

The following shows how to modify the size of LIMIT BUY order currently open on a venue:

The price and trigger price can also be modified (when emulated or supported by a venue).

The main purpose of a separate configuration class is to provide total flexibility over where and how a trading strategy can be instantiated. This includes being able to serialize strategies and their configurations over the wire, making distributed backtesting and firing up remote live trading possible.

This configuration flexibility is actually opt-in, in that you can actually choose not to have any strategy configuration beyond the parameters you choose to pass into your strategies' constructor. If you would like to run distributed backtests or launch live trading servers remotely, then you will need to define a configuration.

Here is an example configuration:

When implementing strategies, it's recommended to access configuration values directly through self.config. This provides clear separation between:

Configuration data (accessed via self.config):

Strategy state variables (as direct attributes):

This separation makes code easier to understand and maintain.

Even though it often makes sense to define a strategy which will trade a single instrument. The number of instruments a single strategy can work with is only limited by machine resources.

It's possible for the strategy to manage expiry for orders with a time in force of GTD (Good 'till Date). This may be desirable if the exchange/broker does not support this time in force option, or for any reason you prefer the strategy to manage this.

To use this option, pass manage_gtd_expiry=True to your StrategyConfig. When an order is submitted with a time in force of GTD, the strategy will automatically start an internal time alert. Once the internal GTD time alert is reached, the order will be canceled (if not already closed).

Some venues (such as Binance Futures) support the GTD time in force, so to avoid conflicts when using managed_gtd_expiry you should set use_gtd=False for your execution client config.

If you intend running multiple instances of the same strategy, with different configurations (such as trading different instruments), then you will need to define a unique order_id_tag for each of these strategies (as shown above).

The platform has built-in safety measures in the event that two strategies share a duplicated strategy ID, then an exception will be raised that the strategy ID has already been registered.

The reason for this is that the system must be able to identify which strategy various commands and events belong to. A strategy ID is made up of the strategy class name, and the strategies order_id_tag separated by a hyphen. For example the above config would result in a strategy ID of MyStrategy-001.

See the StrategyId API Reference for further details.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.trading.strategy import Strategyclass MyStrategy(Strategy):    def __init__(self) -> None:        super().__init__()  # <-- the superclass must be called to initialize the strategy
```

Example 2 (python):
```python
def on_start(self) -> None:def on_stop(self) -> None:def on_resume(self) -> None:def on_reset(self) -> None:def on_dispose(self) -> None:def on_degrade(self) -> None:def on_fault(self) -> None:def on_save(self) -> dict[str, bytes]:  # Returns user-defined dictionary of state to be saveddef on_load(self, state: dict[str, bytes]) -> None:
```

Example 3 (python):
```python
from nautilus_trader.core import Datafrom nautilus_trader.model import OrderBookfrom nautilus_trader.model import Barfrom nautilus_trader.model import QuoteTickfrom nautilus_trader.model import TradeTickfrom nautilus_trader.model import OrderBookDeltasfrom nautilus_trader.model import InstrumentClosefrom nautilus_trader.model import InstrumentStatusfrom nautilus_trader.model.instruments import Instrumentdef on_order_book_deltas(self, deltas: OrderBookDeltas) -> None:def on_order_book(self, order_book: OrderBook) -> None:def on_quote_tick(self, tick: QuoteTick) -> None:def on_trade_tick(self, tick: TradeTick) -> None:def on_bar(self, bar: Bar) -> None:def on_instrument(self, instrument: Instrument) -> None:def on_instrument_status(self, data: InstrumentStatus) -> None:def on_instrument_close(self, data: InstrumentClose) -> None:def on_historical_data(self, data: Data) -> None:def on_data(self, data: Data) -> None:  # Custom data passed to this handlerdef on_signal(self, signal: Data) -> None:  # Custom signals passed to this handler
```

Example 4 (python):
```python
from nautilus_trader.model.events import OrderAcceptedfrom nautilus_trader.model.events import OrderCanceledfrom nautilus_trader.model.events import OrderCancelRejectedfrom nautilus_trader.model.events import OrderDeniedfrom nautilus_trader.model.events import OrderEmulatedfrom nautilus_trader.model.events import OrderEventfrom nautilus_trader.model.events import OrderExpiredfrom nautilus_trader.model.events import OrderFilledfrom nautilus_trader.model.events import OrderInitializedfrom nautilus_trader.model.events import OrderModifyRejectedfrom nautilus_trader.model.events import OrderPendingCancelfrom nautilus_trader.model.events import OrderPendingUpdatefrom nautilus_trader.model.events import OrderRejectedfrom nautilus_trader.model.events import OrderReleasedfrom nautilus_trader.model.events import OrderSubmittedfrom nautilus_trader.model.events import OrderTriggeredfrom nautilus_trader.model.events import OrderUpdateddef on_order_initialized(self, event: OrderInitialized) -> None:def on_order_denied(self, event: OrderDenied) -> None:def on_order_emulated(self, event: OrderEmulated) -> None:def on_order_released(self, event: OrderReleased) -> None:def on_order_submitted(self, event: OrderSubmitted) -> None:def on_order_rejected(self, event: OrderRejected) -> None:def on_order_accepted(self, event: OrderAccepted) -> None:def on_order_canceled(self, event: OrderCanceled) -> None:def on_order_expired(self, event: OrderExpired) -> None:def on_order_triggered(self, event: OrderTriggered) -> None:def on_order_pending_update(self, event: OrderPendingUpdate) -> None:def on_order_pending_cancel(self, event: OrderPendingCancel) -> None:def on_order_modify_rejected(self, event: OrderModifyRejected) -> None:def on_order_cancel_rejected(self, event: OrderCancelRejected) -> None:def on_order_updated(self, event: OrderUpdated) -> None:def on_order_filled(self, event: OrderFilled) -> None:def on_order_event(self, event: OrderEvent) -> None:  # All order event messages are eventually passed to this handler
```

---

## Positions

**URL:** https://nautilustrader.io/docs/latest/concepts/positions

**Contents:**
- Positions
- Overview​
- Position lifecycle​
  - Creation​
  - Updates​
  - Closure​
- Order fill aggregation​
  - Buy fills​
  - Sell fills​
  - Net position calculation​

This guide explains how positions work in NautilusTrader, including their lifecycle, aggregation from order fills, profit and loss calculations, and the important concept of position snapshotting for netting OMS configurations.

A position represents an open exposure to a particular instrument in the market. Positions are fundamental to tracking trading performance and risk, as they aggregate all fills for a particular instrument and continuously calculate metrics like unrealized PnL, average entry price, and total exposure.

The system automatically creates positions when orders fill and tracks them from open to close. The platform supports both netting and hedging position management styles through its OMS (Order Management System) configuration.

The system opens a position on the first fill:

You can access positions through the Cache using self.cache.position(position_id) or self.cache.positions(instrument_id=instrument_id) from within your actors/strategies.

As additional fills occur, the position:

A position closes when the net quantity becomes zero (FLAT). At closure:

Positions aggregate order fills to maintain an accurate view of market exposure. The aggregation process handles both sides of trading activity:

When a BUY order fills:

When a SELL order fills:

The position maintains a signed_qty field representing the net exposure:

NautilusTrader supports two primary OMS types that fundamentally affect how positions are tracked and managed. An OmsType.UNSPECIFIED option also exists, which defaults to the component's context. For comprehensive details, see the Execution guide.

In NETTING mode, all fills for an instrument are aggregated into a single position:

In HEDGING mode, multiple positions can exist for the same instrument:

When using HEDGING mode, be aware of increased margin requirements as each position consumes margin independently. Some venues may not support true hedging mode and will net positions automatically.

The platform allows different OMS configurations for strategies and venues:

For most trading scenarios, keeping strategy and venue OMS types aligned simplifies position management. Override configurations are primarily useful for prop trading desks or when interfacing with legacy systems. See the Live guide for venue-specific OMS configuration.

Position snapshotting is an important feature for NETTING OMS configurations that preserves the state of closed positions for accurate PnL tracking and reporting.

In a NETTING system, when a position closes (becomes FLAT) and then reopens with a new trade, the position object is reset to track the new exposure. Without snapshotting, the historical realized PnL from the previous position cycle would be lost.

When a NETTING position closes and then receives a new fill for the same instrument, the execution engine snapshots the closed position state before resetting it, preserving:

This snapshot is stored in the cache indexed by position ID. The position then resets for the new cycle while previous snapshots remain accessible. The Portfolio aggregates PnL across all snapshots for accurate totals.

This historical snapshot mechanism differs from optional position state snapshots (snapshot_positions), which periodically record open-position state for telemetry. See the Live guide for snapshot_positions and snapshot_positions_interval_secs settings.

Without snapshotting, only the most recent cycle's PnL would be available, leading to incorrect reporting and analysis.

NautilusTrader provides comprehensive PnL calculations that account for instrument specifications and market conventions.

Calculated when positions are partially or fully closed:

The engine automatically applies the correct formula based on position side.

Calculated using current market prices for open positions. The price parameter accepts any reference price (bid, ask, mid, last, or mark):

Combines realized and unrealized components:

Positions track all trading costs:

For complete type information and detailed property documentation, see the Position API Reference.

Positions maintain a complete history of events:

This historical data enables:

Use position.events to access the full history of fills for reconciliation. The position.trade_ids property helps match against broker statements. See the Execution guide for reconciliation best practices.

Position calculations use 64-bit floating-point (f64) arithmetic for PnL and average price computations. While fixed-point types (Price, Quantity, Money) preserve exact precision at configured decimal places, internal calculations convert to f64 for performance and overflow safety.

The platform uses f64 for position calculations to balance performance and accuracy:

Testing confirms f64 arithmetic maintains accuracy for typical trading scenarios:

For implementation details, see test_position_pnl_precision_* tests in crates/model/src/position.rs.

For regulatory compliance or audit trails requiring exact decimal arithmetic, consider using Decimal types from external libraries. Very small amounts below f64 epsilon (~1e-15) may round to zero, though this does not affect realistic trading scenarios with standard currency precisions.

Positions interact with several key components:

Positions are not created for spread instruments. While contingent orders can still trigger for spreads, they operate without position linkage. The engine handles spread instruments separately from regular positions.

Positions are central to tracking trading activity and performance in NautilusTrader. Understanding how positions aggregate fills, calculate PnL, and handle different OMS configurations is essential for building robust trading strategies. The position snapshotting mechanism ensures accurate historical tracking in NETTING mode, while the comprehensive event history supports detailed analysis and reconciliation.

**Examples:**

Example 1 (python):
```python
# Example: Position aggregation# Initial BUY 100 units at $50signed_qty = +100  # LONG position# Subsequent SELL 150 units at $55signed_qty = -50   # Now SHORT position# Final BUY 50 units at $52signed_qty = 0     # Position FLAT (closed)
```

Example 2 (python):
```python
# NETTING OMS Example# Cycle 1: Open LONG positionBUY 100 units at $50   # Position opensSELL 100 units at $55  # Position closes, PnL = $500# Snapshot taken preserving $500 realized PnL# Cycle 2: Open SHORT positionSELL 50 units at $54   # Position reopens (SHORT)BUY 50 units at $52    # Position closes, PnL = $100# Snapshot taken preserving $100 realized PnL# Total realized PnL = $500 + $100 = $600 (from snapshots)
```

Example 3 (python):
```python
# For standard instrumentsrealized_pnl = (exit_price - entry_price) * closed_quantity * multiplier# For inverse instruments (side-aware)# LONG: realized_pnl = closed_quantity * multiplier * (1/entry_price - 1/exit_price)# SHORT: realized_pnl = closed_quantity * multiplier * (1/exit_price - 1/entry_price)
```

Example 4 (python):
```python
position.unrealized_pnl(last_price)  # Using last traded priceposition.unrealized_pnl(bid_price)   # Conservative for LONG positionsposition.unrealized_pnl(ask_price)   # Conservative for SHORT positions
```

---

## Concepts

**URL:** https://nautilustrader.io/docs/latest/concepts

**Contents:**
- Concepts
- Overview​
- Architecture​
- Actors​
- Strategies​
- Instruments​
- Data​
- Execution​
- Orders​
- Positions​

Concept guides introduce and explain the foundational ideas, components, and best practices that underpin the NautilusTrader platform. These guides are designed to provide both conceptual and practical insights, helping you navigate the system's architecture, strategies, data management, execution flow, and more. Explore the following guides to deepen your understanding and make the most of NautilusTrader.

The Overview guide covers the main features and intended use cases for the platform.

The Architecture guide dives deep into the foundational principles, structures, and designs that underpin the platform. It is ideal for developers, system architects, or anyone curious about the inner workings of NautilusTrader.

The Actor serves as the foundational component for interacting with the trading system. The Actors guide covers capabilities and implementation specifics.

The Strategy is at the heart of the NautilusTrader user experience when writing and working with trading strategies. The Strategies guide covers how to implement strategies for the platform.

The Instruments guide covers the different instrument definition specifications for tradable assets and contracts.

The NautilusTrader platform defines a range of built-in data types crafted specifically to represent a trading domain. The Data guide covers working with both built-in and custom data.

NautilusTrader can handle trade execution and order management for multiple strategies and venues simultaneously (per instance). The Execution guide covers components involved in execution, as well as the flow of execution messages (commands and events).

The Orders guide provides more details about the available order types for the platform, along with the execution instructions supported for each. Advanced order types and emulated orders are also covered.

The Positions guide explains how positions work in NautilusTrader, including their lifecycle, aggregation from order fills, profit and loss calculations, and the important concept of position snapshotting for netting OMS configurations.

The Cache is a central in-memory data store for managing all trading-related data. The Cache guide covers capabilities and best practices of the cache.

The MessageBus is the core communication system enabling decoupled messaging patterns between components, including point-to-point, publish/subscribe, and request/response. The Message Bus guide covers capabilities and best practices of the MessageBus.

The Portfolio serves as the central hub for managing and tracking all positions across active strategies for the trading node or backtest. It consolidates position data from multiple instruments, providing a unified view of your holdings, risk exposure, and overall performance. Explore this section to understand how NautilusTrader aggregates and updates portfolio state to support effective trading and risk management.

The Reports guide covers the reporting capabilities in NautilusTrader, including execution reports, portfolio analysis reports, PnL accounting considerations, and how reports are used for backtest post-run analysis.

The platform provides logging for both backtesting and live trading using a high-performance logger implemented in Rust.

Backtesting with NautilusTrader is a methodical simulation process that replicates trading activities using a specific system implementation.

Live trading in NautilusTrader enables traders to deploy their backtested strategies in real-time without any code changes. This seamless transition ensures consistency and reliability, though there are key differences between backtesting and live trading.

The NautilusTrader design allows for integrating data providers and/or trading venues through adapter implementations. The Adapters guide covers requirements and best practices for developing new integration adapters for the platform.

The API Reference documentation should be considered the source of truth for the platform. If there are any discrepancies between concepts described here and the API Reference, then the API Reference should be considered the correct information. We are working to ensure that concepts stay up-to-date with the API Reference and will be introducing doc tests in the near future to help with this.

---

## Live Trading

**URL:** https://nautilustrader.io/docs/latest/concepts/live

**Contents:**
- Live Trading
- Configuration​
  - TradingNodeConfig​
    - Core configuration parameters​
    - Cache database configuration​
    - MessageBus configuration​
  - Multi-venue configuration​
  - ExecutionEngine configuration​
    - Reconciliation​
    - Order filtering​

Live trading in NautilusTrader enables traders to deploy their backtested strategies in a real-time trading environment with no code changes. This seamless transition from backtesting to live trading is a core feature of the platform, ensuring consistency and reliability. However, there are key differences to be aware of between backtesting and live trading.

This guide provides an overview of the key aspects of live trading.

Windows signal handling differs from Unix-like systems. If you are running on Windows, please read the note on Windows signal handling for guidance on graceful shutdown behavior and Ctrl+C (SIGINT) support.

When operating a live trading system, configuring your execution engine and strategies properly is essential for ensuring reliability, accuracy, and performance. The following is an overview of the key concepts and settings involved for live configuration.

The main configuration class for live trading systems is TradingNodeConfig, which inherits from NautilusKernelConfig and provides live-specific config options:

Configure data persistence with a backing database:

Configure message routing and external streaming:

Live trading systems often connect to multiple venues. Here's an example of configuring both spot and futures markets for Binance:

The LiveExecEngineConfig sets up the live execution engine, managing order processing, execution events, and reconciliation with trading venues. The following outlines the main configuration options.

By configuring these parameters thoughtfully, you can ensure that your trading system operates efficiently, handles orders correctly, and remains resilient in the face of potential issues, such as lost events or conflicting data/information.

For full details see the LiveExecEngineConfig API Reference.

Purpose: Ensures that the system state remains consistent with the trading venue by recovering any missed events, such as order and position status updates.

See Execution reconciliation for additional background.

Purpose: Manages which order events and reports should be processed by the system to avoid conflicts with other trading nodes and unnecessary data handling.

Purpose: Maintains accurate execution state through a continuous reconciliation loop that runs after startup reconciliation completes, this loop:

Startup sequence: The continuous reconciliation loop waits for startup reconciliation to complete before beginning periodic checks. This prevents race conditions where continuous checks might interfere with the initial state reconciliation. The reconciliation_startup_delay_secs parameter applies an additional delay after startup reconciliation completes.

If an order's status cannot be reconciled after exhausting all retries, the engine resolves the order as follows:

In-flight order timeout resolution (when venue doesn't respond after max retries):

Order consistency checks (when cache state differs from venue state):

Important reconciliation caveats:

The execution engine reuses a single retry counter (_recon_check_retries) for both the inflight loop (bounded by inflight_check_retries) and the open-order loop (bounded by open_check_missing_retries). This shared budget ensures the stricter limit wins and prevents duplicate venue queries for the same order state.

When the open-order loop exhausts its retries, the engine issues one targeted GenerateOrderStatusReport probe before applying a terminal state. If the venue returns the order, reconciliation proceeds and the retry counter resets automatically.

Single-order query protection: To prevent rate limit exhaustion when many orders need individual queries, the engine limits single-order queries per reconciliation cycle via max_single_order_queries_per_cycle (default: 10). When this limit is reached, remaining orders are deferred to the next cycle. Additionally, the engine adds a configurable delay (single_order_query_delay_ms, default: 100ms) between single-order queries to further prevent rate limiting. This ensures the system can handle scenarios where bulk queries fail for hundreds of orders without overwhelming the venue API.

Orders that age beyond open_check_lookback_mins rely on this targeted probe. Keep the lookback generous for venues with short history windows, and consider increasing open_check_threshold_ms if venue timestamps lag the local clock so recently updated orders are not marked missing prematurely.

This ensures the trading node maintains a consistent execution state even under unreliable conditions.

Important configuration guidelines:

The following additional options provide further control over execution behavior:

Purpose: Periodically purges closed orders, closed positions, and account events from the in-memory cache to optimize resource usage and performance during extended / HFT operations.

By configuring these memory management settings appropriately, you can prevent memory usage from growing indefinitely during long-running / HFT sessions while ensuring that recently closed orders, closed positions, and account events remain available in memory for any ongoing operations that might require them. Set an interval to enable the relevant purge loop; leaving it unset disables both scheduling and deletion. Each loop delegates to the cache APIs described in Purging cached state.

Purpose: Handles the internal buffering of order events to ensure smooth processing and to prevent system resource overloads.

The StrategyConfig class outlines the configuration for trading strategies, ensuring that each strategy operates with the correct parameters and manages orders effectively. For a complete parameter list see the StrategyConfig API Reference.

Purpose: Provides unique identifiers for each strategy to prevent conflicts and ensure proper tracking of orders.

Purpose: Controls strategy-level order handling including position-ID processing, claiming relevant external orders, automating contingent order logic (OUO/OCO), and tracking GTD expirations.

Windows: asyncio event loops do not implement loop.add_signal_handler. As a result, the legacy TradingNode does not receive OS signals via asyncio on Windows. Use Ctrl+C (SIGINT) handling or programmatic shutdown; SIGTERM parity is not expected on Windows.

On Windows, asyncio event loops do not implement loop.add_signal_handler, so Unix-style signal integration is unavailable. As a result, TradingNode does not receive OS signals via asyncio on Windows and will not gracefully stop unless you intervene.

Recommended approaches on Windows:

The “inflight check loop task still pending” message is consistent with the lack of asyncio signal handling on Windows, i.e., the normal graceful shutdown path isn’t being triggered.

This is tracked as an enhancement request to support Ctrl+C (SIGINT) for Windows in the legacy path. https://github.com/nautechsystems/nautilus_trader/issues/2785.

For the new v2 system, LiveNode already supports Ctrl+C cleanly via tokio::signal::ctrl_c() and a Python SIGINT bridge, so the runner stops and tasks are shut down cleanly.

Example pattern for Windows:

Execution reconciliation is the process of aligning the external state of reality for orders and positions (both closed and open) with the system's internal state built from events. This process is primarily applicable to live trading, which is why only the LiveExecutionEngine has reconciliation capability.

There are two main scenarios for reconciliation:

Best practice: Persist all execution events to the cache database to minimize reliance on venue history, ensuring full recovery even with short lookback windows.

Unless reconciliation is disabled by setting the reconciliation configuration parameter to false, the execution engine will perform the execution reconciliation procedure for each venue. Additionally, you can specify the lookback window for reconciliation by setting the reconciliation_lookback_mins configuration parameter.

We recommend not setting a specific reconciliation_lookback_mins. This allows the requests made to the venues to utilize the maximum execution history available for reconciliation.

If executions have occurred prior to the lookback window, any necessary events will be generated to align internal and external states. This may result in some information loss that could have been avoided with a longer lookback window.

Additionally, some venues may filter or drop execution information under certain conditions, resulting in further information loss. This would not occur if all events were persisted in the cache database.

Each strategy can also be configured to claim any external orders for an instrument ID generated during reconciliation using the external_order_claims configuration parameter. This is useful in situations where, at system start, there is no cached state or it is desirable for a strategy to resume its operations and continue managing existing open orders for a specific instrument.

Orders generated with strategy ID INTERNAL-DIFF during position reconciliation are internal to the engine and cannot be claimed via external_order_claims. They exist solely to align position discrepancies and should not be managed by user strategies.

For a full list of live trading options see the LiveExecEngineConfig API Reference.

The reconciliation procedure is standardized for all adapter execution clients and uses the following methods to produce an execution mass status:

The system state is then reconciled with the reports, which represent external "reality":

If reconciliation fails, the system will not continue to start, and an error will be logged.

The scenarios below are split between startup reconciliation (mass status) and runtime/continuous checks (in-flight order checks, open-order polls, and own-books audits).

For persistent reconciliation issues, consider dropping cached state or flattening accounts before system restart.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.config import TradingNodeConfigconfig = TradingNodeConfig(    trader_id="MyTrader-001",    # Component configurations    cache: CacheConfig(),    message_bus: MessageBusConfig(),    data_engine=LiveDataEngineConfig(),    risk_engine=LiveRiskEngineConfig(),    exec_engine=LiveExecEngineConfig(),    portfolio=PortfolioConfig(),    # Client configurations    data_clients={        "BINANCE": BinanceDataClientConfig(),    },    exec_clients={        "BINANCE": BinanceExecClientConfig(),    },)
```

Example 2 (python):
```python
from nautilus_trader.config import CacheConfigfrom nautilus_trader.config import DatabaseConfigcache_config = CacheConfig(    database=DatabaseConfig(        host="localhost",        port=6379,        username="nautilus",        password="pass",        timeout=2.0,    ),    encoding="msgpack",  # or "json"    timestamps_as_iso8601=True,    buffer_interval_ms=100,    flush_on_start=False,)
```

Example 3 (python):
```python
from nautilus_trader.config import MessageBusConfigfrom nautilus_trader.config import DatabaseConfigmessage_bus_config = MessageBusConfig(    database=DatabaseConfig(timeout=2),    timestamps_as_iso8601=True,    use_instance_id=False,    types_filter=[QuoteTick, TradeTick],  # Filter specific message types    stream_per_topic=False,    autotrim_mins=30,  # Automatic message trimming    heartbeat_interval_secs=1,)
```

Example 4 (python):
```python
config = TradingNodeConfig(    trader_id="MultiVenue-001",    # Multiple data clients for different market types    data_clients={        "BINANCE_SPOT": BinanceDataClientConfig(            account_type=BinanceAccountType.SPOT,            testnet=False,        ),        "BINANCE_FUTURES": BinanceDataClientConfig(            account_type=BinanceAccountType.USDT_FUTURES,            testnet=False,        ),    },    # Corresponding execution clients    exec_clients={        "BINANCE_SPOT": BinanceExecClientConfig(            account_type=BinanceAccountType.SPOT,            testnet=False,        ),        "BINANCE_FUTURES": BinanceExecClientConfig(            account_type=BinanceAccountType.USDT_FUTURES,            testnet=False,        ),    },)
```

---

## Reports

**URL:** https://nautilustrader.io/docs/latest/concepts/reports

**Contents:**
- Reports
- Overview​
- Available reports​
  - Orders report​
  - Order fills report​
  - Fills report​
  - Positions report​
  - Account report​
- PnL accounting considerations​
  - Position-based PnL​

We are currently working on this concept guide.

This guide explains the portfolio analysis and reporting capabilities provided by the ReportProvider class, and how these reports are used for PnL accounting and backtest post-run analysis.

The ReportProvider class in NautilusTrader generates structured analytical reports from trading data, transforming raw orders, fills, positions, and account states into pandas DataFrames for analysis and visualization. These reports are essential for understanding strategy performance, analyzing execution quality, and ensuring accurate PnL accounting.

Reports can be generated using two approaches:

Reports provide consistent analytics across both backtesting and live trading environments, enabling reliable performance evaluation and strategy comparison.

The ReportProvider class offers several static methods to generate reports from trading data. Each report returns a pandas DataFrame with specific columns and indexing for easy analysis.

Generates a comprehensive view of all orders:

Returns pd.DataFrame with:

Provides a summary of filled orders (one row per order):

This report includes only orders with filled_qty > 0 and contains the same columns as the orders report, but filtered to executed orders only. Note that ts_init and ts_last are converted to datetime objects in this report for easier analysis.

Details individual fill events (one row per fill):

Returns pd.DataFrame with:

Comprehensive position analysis including snapshots:

Returns pd.DataFrame with:

Tracks account balance and margin changes over time:

Returns pd.DataFrame with:

Accurate PnL accounting requires careful consideration of several factors:

PnL calculations depend on the OMS type. In NETTING mode, position snapshots preserve historical PnL when positions reopen. Always include snapshots in reports for accurate total PnL calculation.

When dealing with multiple currencies:

For NETTING OMS configurations:

After a backtest completes, comprehensive analysis is available through various reports and the portfolio analyzer.

The portfolio analyzer provides comprehensive performance metrics:

For detailed information about available statistics and creating custom metrics, see the Portfolio guide. The Portfolio guide covers:

Reports integrate well with visualization tools:

During live trading, generate reports periodically:

For backtest analysis:

Reports are generated from in-memory data structures. For large-scale analysis or long-running systems, consider persisting reports to a database for efficient querying. See the Cache guide for persistence options.

The ReportProvider works with several system components:

The ReportProvider class offers a comprehensive suite of analytical reports for evaluating trading performance. These reports transform raw trading data into structured DataFrames, enabling detailed analysis of orders, fills, positions, and account states. Understanding how to generate and interpret these reports is essential for strategy development, performance evaluation, and accurate PnL accounting, particularly when dealing with position snapshots in NETTING OMS configurations.

**Examples:**

Example 1 (python):
```python
# Using Trader helper method (recommended)orders_report = trader.generate_orders_report()# Or using ReportProvider directlyfrom nautilus_trader.analysis.reporter import ReportProviderorders = cache.orders()orders_report = ReportProvider.generate_orders_report(orders)
```

Example 2 (python):
```python
# Using Trader helper method (recommended)fills_report = trader.generate_order_fills_report()# Or using ReportProvider directlyorders = cache.orders()fills_report = ReportProvider.generate_order_fills_report(orders)
```

Example 3 (python):
```python
# Using Trader helper method (recommended)fills_report = trader.generate_fills_report()# Or using ReportProvider directlyorders = cache.orders()fills_report = ReportProvider.generate_fills_report(orders)
```

Example 4 (python):
```python
# Using Trader helper method (recommended)# Automatically includes snapshots for NETTING OMSpositions_report = trader.generate_positions_report()# Or using ReportProvider directlypositions = cache.positions()snapshots = cache.position_snapshots()  # For NETTING OMSpositions_report = ReportProvider.generate_positions_report(    positions=positions,    snapshots=snapshots)
```

---

## Adapters

**URL:** https://nautilustrader.io/docs/latest/concepts/adapters

**Contents:**
- Adapters
- Instrument providers​
  - Research and backtesting​
  - Live trading​
- Data clients​
  - Requests​
    - Example​

The NautilusTrader design integrates data providers and/or trading venues through adapter implementations. These can be found in the top-level adapters subpackage.

An integration adapter is typically comprised of the following main components:

Instrument providers do as their name suggests - instantiating Nautilus Instrument objects by parsing the raw API of the publisher or venue.

The use cases for the instruments available from an InstrumentProvider are either:

Here is an example of discovering the current instruments for the Binance Futures testnet:

Each integration is implementation specific, and there are generally two options for the behavior of an InstrumentProvider within a TradingNode for live trading, as configured:

An Actor or Strategy can request custom data from a DataClient by sending a DataRequest. If the client that receives the DataRequest implements a handler for the request, data will be returned to the Actor or Strategy.

An example of this is a DataRequest for an Instrument, which the Actor class implements (copied below). Any Actor or Strategy can call a request_instrument method with an InstrumentId to request the instrument from a DataClient.

In this particular case, the Actor implements a separate method request_instrument. A similar type of DataRequest could be instantiated and called from anywhere and/or anytime in the actor/strategy code.

A simplified version of request_instrument for an actor/strategy is:

A simplified version of the request handler implemented in a LiveMarketDataClient that will retrieve the data and send it back to actors/strategies is for example:

The DataEngine which is an important component in Nautilus links a request with a DataClient. For example a simplified version of handling an instrument request is:

**Examples:**

Example 1 (python):
```python
import asyncioimport osfrom nautilus_trader.adapters.binance.common.enums import BinanceAccountTypefrom nautilus_trader.adapters.binance import get_cached_binance_http_clientfrom nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProviderfrom nautilus_trader.common.component import LiveClockclock = LiveClock()account_type = BinanceAccountType.USDT_FUTURESclient = get_cached_binance_http_client(    loop=asyncio.get_event_loop(),    clock=clock,    account_type=account_type,    key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),    secret=os.getenv("BINANCE_FUTURES_TESTNET_API_SECRET"),    is_testnet=True,)await client.connect()provider = BinanceFuturesInstrumentProvider(    client=client,    account_type=BinanceAccountType.USDT_FUTURES,)await provider.load_all_async()
```

Example 2 (python):
```python
from nautilus_trader.config import InstrumentProviderConfigInstrumentProviderConfig(load_all=True)
```

Example 3 (python):
```python
InstrumentProviderConfig(load_ids=["BTCUSDT-PERP.BINANCE", "ETHUSDT-PERP.BINANCE"])
```

Example 4 (python):
```python
# nautilus_trader/common/actor.pyxcpdef void request_instrument(self, InstrumentId instrument_id, ClientId client_id=None):    """    Request `Instrument` data for the given instrument ID.    Parameters    ----------    instrument_id : InstrumentId        The instrument ID for the request.    client_id : ClientId, optional        The specific client ID for the command.        If ``None`` then will be inferred from the venue in the instrument ID.    """    Condition.not_none(instrument_id, "instrument_id")    cdef RequestInstrument request = RequestInstrument(        instrument_id=instrument_id,        start=None,        end=None,        client_id=client_id,        venue=instrument_id.venue,        callback=self._handle_instrument_response,        request_id=UUID4(),        ts_init=self._clock.timestamp_ns(),        params=None,    )    self._send_data_req(request)
```

---

## Message Bus

**URL:** https://nautilustrader.io/docs/latest/concepts/message_bus

**Contents:**
- Message Bus
- Data and signal publishing​
- Direct access​
- Messaging styles​
  - MessageBus publish/subscribe to topics​
    - Concept​
    - Key benefits and use cases​
    - Considerations​
    - Quick overview code​
    - Full example​

The MessageBus is a fundamental part of the platform, enabling communication between system components through message passing. This design creates a loosely coupled architecture where components can interact without direct dependencies.

The messaging patterns include:

Messages exchanged via the MessageBus fall into three categories:

While the MessageBus is a lower-level component that users typically interact with indirectly, Actor and Strategy classes provide convenient methods built on top of it:

These methods allow you to publish custom data and signals efficiently without needing to work directly with the MessageBus interface.

For advanced users or specialized use cases, direct access to the message bus is available within Actor and Strategy classes through the self.msgbus reference, which provides the full message bus interface.

To publish a custom message directly, you can specify a topic as a str and any Python object as the message payload, for example:

NautilusTrader is an event-driven framework where components communicate by sending and receiving messages. Understanding the different messaging styles is crucial for building effective trading systems.

This guide explains the three primary messaging patterns available in NautilusTrader:

Each approach serves different purposes and offers unique advantages. This guide will help you decide which messaging pattern to use in your NautilusTrader applications.

The MessageBus is the central hub for all messages in NautilusTrader. It enables a publish/subscribe pattern where components can publish events to named topics, and other components can subscribe to receive those messages. This decouples components, allowing them to interact indirectly via the message bus.

The message bus approach is ideal when you need:

This approach provides a way to exchange trading specific data between Actors in the system. (note: each Strategy inherits from Actor). It inherits from Data, which ensures proper timestamping and ordering of events - crucial for correct backtest processing.

The Data publish/subscribe approach excels when you need:

Inheriting from Data class:

The @customdataclass decorator:

Actor-Based Data Example

Signals are a lightweight way to publish and subscribe to simple notifications within the actor framework. This is the simplest messaging approach, requiring no custom class definitions.

The Signal messaging approach shines when you need:

Actor-Based Signal Example

Here's a quick reference to help you decide which messaging style to use:

The MessageBus can be backed with any database or message broker technology which has an integration written for it, this then enables external publishing of messages.

Redis is currently supported for all serializable messages which are published externally. The minimum supported Redis version is 6.2 (required for streams functionality).

Under the hood, when a backing database (or any other compatible technology) is configured, all outgoing messages are first serialized, then transmitted via a Multiple-Producer Single-Consumer (MPSC) channel to a separate thread (implemented in Rust). In this separate thread, the message is written to its final destination, which is presently Redis streams.

This design is primarily driven by performance considerations. By offloading the I/O operations to a separate thread, we ensure that the main thread remains unblocked and can continue its tasks without being hindered by the potentially time-consuming operations involved in interacting with a database or client.

Nautilus supports serialization for:

You can add serialization support for custom types by registering them through the serialization subpackage.

The message bus external backing technology can be configured by importing the MessageBusConfig object and passing this to your TradingNodeConfig. Each of these config options will be described below.

A DatabaseConfig must be provided, for a default Redis setup on the local loopback you can pass a DatabaseConfig(), which will use defaults to match.

Two encodings are currently supported by the built-in Serializer used by the MessageBus:

Use the encoding config option to control the message writing encoding.

The msgpack encoding is used by default as it offers the most optimal serialization and memory performance. We recommend using json encoding for human readability when performance is not a primary concern.

By default timestamps are formatted as UNIX epoch nanosecond integers. Alternatively you can configure ISO 8601 string formatting by setting the timestamps_as_iso8601 to True.

Message stream keys are essential for identifying individual trader nodes and organizing messages within streams. They can be tailored to meet your specific requirements and use cases. In the context of message bus streams, a trader key is typically structured as follows:

The following options are available for configuring message stream keys:

If the key should begin with the trader string.

If the key should include the trader ID for the node.

Each trader node is assigned a unique 'instance ID,' which is a UUIDv4. This instance ID helps distinguish individual traders when messages are distributed across multiple streams. You can include the instance ID in the trader key by setting the use_instance_id configuration option to True. This is particularly useful when you need to track and identify traders across various streams in a multi-node trading system.

The streams_prefix string enables you to group all streams for a single trader instance or organize messages for multiple instances. Configure this by passing a string to the streams_prefix configuration option, ensuring other prefixes are set to false.

Indicates whether the producer will write a separate stream for each topic. This is particularly useful for Redis backings, which do not support wildcard topics when listening to streams. If set to False, all messages will be written to the same stream.

Redis does not support wildcard stream topics. For better compatibility with Redis, it is recommended to set this option to False.

When messages are published on the message bus, they are serialized and written to a stream if a backing for the message bus is configured and enabled. To prevent flooding the stream with data like high-frequency quotes, you may filter out certain types of messages from external publication.

To enable this filtering mechanism, pass a list of type objects to the types_filter parameter in the message bus configuration, specifying which types of messages should be excluded from external publication.

The autotrim_mins configuration parameter allows you to specify the lookback window in minutes for automatic stream trimming in your message streams. Automatic stream trimming helps manage the size of your message streams by removing older messages, ensuring that the streams remain manageable in terms of storage and performance.

The current Redis implementation will maintain the autotrim_mins as a maximum width (plus roughly a minute, as streams are trimmed no more than once per minute). Rather than a maximum lookback window based on the current wall clock time.

The message bus within a TradingNode (node) is referred to as the "internal message bus". A producer node is one which publishes messages onto an external stream (see external publishing). The consumer node listens to external streams to receive and publish deserialized message payloads on its internal message bus.

Set the LiveDataEngineConfig.external_clients with the list of client_ids intended to represent the external streaming clients. The DataEngine will filter out subscription commands for these clients, ensuring that the external streaming provides the necessary data for any subscriptions to these clients.

The following example details a streaming setup where a producer node publishes Binance data externally, and a downstream consumer node publishes these data messages onto its internal message bus.

We configure the MessageBus of the producer node to publish to a "binance" stream. The settings use_trader_id, use_trader_prefix, and use_instance_id are all set to False to ensure a simple and predictable stream key that the consumer nodes can register for.

We configure the MessageBus of the consumer node to receive messages from the same "binance" stream. The node will listen to the external stream keys to publish these messages onto its internal message bus. Additionally, we declare the client ID "BINANCE_EXT" as an external client. This ensures that the DataEngine does not attempt to send data commands to this client ID, as we expect these messages to be published onto the internal message bus from the external stream, to which the node has subscribed to the relevant topics.

**Examples:**

Example 1 (python):
```python
def publish_data(self, data_type: DataType, data: Data) -> None:def publish_signal(self, name: str, value, ts_event: int | None = None) -> None:
```

Example 2 (python):
```python
self.msgbus.publish("MyTopic", "MyMessage")
```

Example 3 (python):
```python
from nautilus_trader.core.message import Event# Define a custom eventclass Each10thBarEvent(Event):    TOPIC = "each_10th_bar"  # Topic name    def __init__(self, bar):        self.bar = bar# Subscribe in a component (in Strategy)self.msgbus.subscribe(Each10thBarEvent.TOPIC, self.on_each_10th_bar)# Publish an event (in Strategy)event = Each10thBarEvent(bar)self.msgbus.publish(Each10thBarEvent.TOPIC, event)# Handler (in Strategy)def on_each_10th_bar(self, event: Each10thBarEvent):    self.log.info(f"Received 10th bar: {event.bar}")
```

Example 4 (python):
```python
from nautilus_trader.core.data import Datafrom nautilus_trader.model.custom import customdataclass@customdataclassclass GreeksData(Data):    delta: float    gamma: float# Publish data (in Actor / Strategy)data = GreeksData(delta=0.75, gamma=0.1, ts_event=1_630_000_000_000_000_000, ts_init=1_630_000_000_000_000_000)self.publish_data(GreeksData, data)# Subscribe to receiving data  (in Actor / Strategy)self.subscribe_data(GreeksData)# Handler (this is static callback function with fixed name)def on_data(self, data: Data):    if isinstance(data, GreeksData):        self.log.info(f"Delta: {data.delta}, Gamma: {data.gamma}")
```

---

## Cache

**URL:** https://nautilustrader.io/docs/latest/concepts/cache

**Contents:**
- Cache
- How caching works​
  - Basic example​
- Configuration​
  - Configuration options​
  - Database configuration​
- Using the cache​
  - Accessing market data​
    - Bar access​
    - Quote ticks​

The Cache is a central in-memory database that automatically stores and manages all trading-related data. Think of it as your trading system’s memory – storing everything from market data to order history to custom calculations.

The Cache serves multiple key purposes:

Within a strategy, you can access the Cache through self.cache. Here’s a typical example:

Anywhere you find self, it refers mostly to the Strategy itself.

Use the CacheConfig class to configure the Cache behavior and capacity. You can provide this configuration either to a BacktestEngine or a TradingNode, depending on your environment context.

Here's a basic example of configuring the Cache:

By default, the Cache keeps the last 10,000 bars for each bar type and 10,000 trade ticks per instrument. These limits provide a good balance between memory usage and data availability. Increase them if your strategy needs more historical data.

The CacheConfig class supports these parameters:

Each bar type maintains its own separate capacity. For example, if you're using both 1-minute and 5-minute bars, each stores up to bar_capacity bars. When bar_capacity is reached, the Cache automatically removes the oldest data.

For persistence between system restarts, you can configure a database backend.

When is it useful to use persistence?

The Cache provides a comprehensive interface for accessing order books, quotes, trades, and bars. All market data in the cache uses reverse indexing, so the most recent entry sits at index 0.

The Cache provides comprehensive access to all trading objects within the system, including:

You can access and query orders through multiple methods, with flexible filtering options by venue, strategy, instrument, and order side.

The Cache maintains a record of all positions and offers several ways to query them.

The cache exposes explicit maintenance hooks that remove closed or stale objects while preserving safety checks:

Use the trading clock (for example, self.clock.timestamp_ns()) when supplying ts_now. Set purge_from_database=True only when you intend to delete persisted records from Redis or PostgreSQL as well. In live trading these methods run automatically when the execution engine is configured with purge intervals; see Memory management for the scheduler settings.

The Cache can also store and retrieve custom data types in addition to built-in market data and trading objects. Use it to share any user-defined data between system components, primarily actors and strategies.

For more complex use cases, the Cache can store custom data objects that inherit from the nautilus_trader.core.Data base class.

The Cache is not designed to be a full database replacement. For large datasets or complex querying needs, consider using a dedicated database system.

The Cache and Portfolio components serve different but complementary purposes in NautilusTrader:

Choosing between storing data in the Cache versus strategy variables depends on your specific needs:

The following example shows how you might store data in the Cache so multiple strategies can access the same information.

Another strategy can retrieve the cached data as follows:

**Examples:**

Example 1 (text):
```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌───────────────────────┐│                 │     │                 │     │                 │     │                       ││                 │     │                 │     │                 │     │   Strategy callback:  ││      Data       ├─────►   DataEngine    ├─────►     Cache       ├─────►                       ││                 │     │                 │     │                 │     │   on_data(...)        ││                 │     │                 │     │                 │     │                       │└─────────────────┘     └─────────────────┘     └───────── ────────┘     └───────────────────────┘
```

Example 2 (python):
```python
def on_bar(self, bar: Bar) -> None:    # Current bar is provided in the parameter 'bar'    # Get historical bars from Cache    last_bar = self.cache.bar(self.bar_type, index=0)        # Last bar (practically the same as the 'bar' parameter)    previous_bar = self.cache.bar(self.bar_type, index=1)    # Previous bar    third_last_bar = self.cache.bar(self.bar_type, index=2)  # Third last bar    # Get current position information    if self.last_position_opened_id is not None:        position = self.cache.position(self.last_position_opened_id)        if position.is_open:            # Check position details            current_pnl = position.unrealized_pnl    # Get all open orders for our instrument    open_orders = self.cache.orders_open(instrument_id=self.instrument_id)
```

Example 3 (python):
```python
from nautilus_trader.config import CacheConfig, BacktestEngineConfig, TradingNodeConfig# For backtestingengine_config = BacktestEngineConfig(    cache=CacheConfig(        tick_capacity=10_000,  # Store last 10,000 ticks per instrument        bar_capacity=5_000,    # Store last 5,000 bars per bar type    ),)# For live tradingnode_config = TradingNodeConfig(    cache=CacheConfig(        tick_capacity=10_000,        bar_capacity=5_000,    ),)
```

Example 4 (python):
```python
from nautilus_trader.config import CacheConfigcache_config = CacheConfig(    database: DatabaseConfig | None = None,  # Database configuration for persistence    encoding: str = "msgpack",               # Data encoding format ('msgpack' or 'json')    timestamps_as_iso8601: bool = False,     # Store timestamps as ISO8601 strings    buffer_interval_ms: int | None = None,   # Buffer interval for batch operations    use_trader_prefix: bool = True,          # Use trader prefix in keys    use_instance_id: bool = False,           # Include instance ID in keys    flush_on_start: bool = False,            # Clear database on startup    drop_instruments_on_reset: bool = True,  # Clear instruments on reset    tick_capacity: int = 10_000,             # Maximum ticks stored per instrument    bar_capacity: int = 10_000,              # Maximum bars stored per each bar-type)
```

---

## Execution

**URL:** https://nautilustrader.io/docs/latest/concepts/execution

**Contents:**
- Execution
- Execution flow​
- Order Management System (OMS)​
  - OMS configuration​
- Risk engine​
  - Trading state​
- Execution algorithms​
  - TWAP (Time-Weighted Average Price)​
  - Writing execution algorithms​
  - Spawned orders​

NautilusTrader can handle trade execution and order management for multiple strategies and venues simultaneously (per instance). Several interacting components are involved in execution, making it crucial to understand the possible flows of execution messages (commands and events).

The main execution-related components include:

The Strategy base class inherits from Actor and so contains all of the common data related methods. It also provides methods for managing orders and trade execution:

These methods create the necessary execution commands under the hood and send them on the message bus to the relevant components (point-to-point), as well as publishing any events (such as the initialization of new orders i.e. OrderInitialized events).

The general execution flow looks like the following (each arrow indicates movement across the message bus):

Strategy -> OrderEmulator -> ExecAlgorithm -> RiskEngine -> ExecutionEngine -> ExecutionClient

The OrderEmulator and ExecAlgorithm(s) components are optional in the flow, depending on individual order parameters (as explained below).

This diagram illustrates message flow (commands and events) across the Nautilus execution components.

An order management system (OMS) type refers to the method used for assigning orders to positions and tracking those positions for an instrument. OMS types apply to both strategies and venues (simulated and real). Even if a venue doesn't explicitly state the method in use, an OMS type is always in effect. The OMS type for a component can be specified using the OmsType enum.

The OmsType enum has three variants:

The table below describes different configuration combinations and their applicable scenarios. When the strategy and venue OMS types differ, the ExecutionEngine handles this by overriding or assigning position_id values for received OrderFilled events. A "virtual position" refers to a position ID that exists within the Nautilus system but not on the venue in reality.

Configuring OMS types separately for strategies and venues increases platform complexity but allows for a wide range of trading styles and preferences (see below).

Nautilus does not yet support venue-side hedging modes such as Binance BOTH vs. LONG/SHORT where the venue nets per direction. It is advised to keep Binance account configurations as BOTH so that a single position is netted.

If a strategy OMS type is not explicitly set using the oms_type configuration option, it will default to UNSPECIFIED. This means the ExecutionEngine will not override any venue position_ids, and the OMS type will follow the venue's OMS type.

When configuring a backtest, you can specify the oms_type for the venue. To enhance backtest accuracy, it is recommended to match this with the actual OMS type used by the venue in practice.

The RiskEngine is a core component of every Nautilus system, including backtest, sandbox, and live environments. Every order command and event passes through the RiskEngine unless specifically bypassed in the RiskEngineConfig.

The RiskEngine includes several built-in pre-trade risk checks, including:

If any risk check fails, the system generates an OrderDenied event, effectively closing the order and preventing it from progressing further. This event includes a human-readable reason for the denial.

Additionally, the current trading state of a Nautilus system affects order flow.

The TradingState enum has three variants:

See the RiskEngineConfig API Reference for further details.

The platform supports customized execution algorithm components and provides some built-in algorithms, such as the Time-Weighted Average Price (TWAP) algorithm.

The TWAP execution algorithm aims to execute orders by evenly spreading them over a specified time horizon. The algorithm receives a primary order representing the total size and direction then splits this by spawning smaller child orders, which are then executed at regular intervals throughout the time horizon.

This helps to reduce the impact of the full size of the primary order on the market, by minimizing the concentration of trade size at any given time.

The algorithm will immediately submit the first order, with the final order submitted being the primary order at the end of the horizon period.

Using the TWAP algorithm as an example (found in /examples/algorithms/twap.py), this example demonstrates how to initialize and register a TWAP execution algorithm directly with a BacktestEngine (assuming an engine is already initialized):

For this particular algorithm, two parameters must be specified:

The horizon_secs parameter determines the time period over which the algorithm will execute, while the interval_secs parameter sets the time between individual order executions. These parameters determine how a primary order is split into a series of spawned orders.

Alternatively, you can specify these parameters dynamically per order, determining them based on actual market conditions. In this case, the strategy configuration parameters could be provided to an execution model which determines the horizon and interval.

There is no limit to the number of execution algorithm parameters you can create. The parameters just need to be a dictionary with string keys and primitive values (values that can be serialized over the wire, such as ints, floats, and strings).

To implement a custom execution algorithm you must define a class which inherits from ExecAlgorithm.

An execution algorithm is a type of Actor, so it's capable of the following:

Once an execution algorithm is registered, and the system is running, it will receive orders off the messages bus which are addressed to its ExecAlgorithmId via the exec_algorithm_id order parameter. The order may also carry the exec_algorithm_params being a dict[str, Any].

Because of the flexibility of the exec_algorithm_params dictionary. It's important to thoroughly validate all of the key value pairs for correct operation of the algorithm (for starters that the dictionary is not None and all necessary parameters actually exist).

Received orders will arrive via the following on_order(...) method. These received orders are know as "primary" (original) orders when being handled by an execution algorithm.

When the algorithm is ready to spawn a secondary order, it can use one of the following methods:

Additional order types will be implemented in future versions, as the need arises.

Each of these methods takes the primary (original) Order as the first argument. The primary order quantity will be reduced by the quantity passed in (becoming the spawned orders quantity).

There must be enough primary order quantity remaining (this is validated).

Once the desired number of secondary orders have been spawned, and the execution routine is over, the intention is that the algorithm will then finally send the primary (original) order.

All secondary orders spawned from an execution algorithm will carry a exec_spawn_id which is simply the ClientOrderId of the primary (original) order, and whose client_order_id derives from this original identifier with the following convention:

e.g. O-20230404-001-000-E1 (for the first spawned order)

The "primary" and "secondary" / "spawn" terminology was specifically chosen to avoid conflict or confusion with the "parent" and "child" contingent orders terminology (an execution algorithm may also deal with contingent orders).

The Cache provides several methods to aid in managing (keeping track of) the activity of an execution algorithm. Calling the below method will return all execution algorithm orders for the given query filters.

As well as more specifically querying the orders for a certain execution series/spawn. Calling the below method will return all orders for the given exec_spawn_id (if found).

This also includes the primary (original) order.

Own order books are L3 order books that track only your own (user) orders organized by price level, maintained separately from the venue's public order books.

Own order books serve several purposes:

Own order books are maintained per instrument and automatically updated as orders transition through their lifecycle. Orders are added when submitted or accepted, updated when modified, and removed when filled, canceled, rejected, or expired.

Only orders with prices can be represented in own order books. Market orders and other order types without explicit prices are excluded since they cannot be positioned at specific price levels.

When querying own order books for orders to cancel, use a status filter that excludes PENDING_CANCEL to avoid processing orders already being cancelled.

Including PENDING_CANCEL in status filters can cause:

The optional accepted_buffer_ns many methods expose is a time-based guard that only returns orders whose ts_accepted is at least that many nanoseconds in the past. Orders that have not yet been accepted by the venue still have ts_accepted = 0, so they are included once the buffer window elapses. To exclude those inflight orders you must pair the buffer with an explicit status filter (for example, restrict to ACCEPTED / PARTIALLY_FILLED).

During live trading, own order books can be periodically audited against the cache's order indexes to ensure consistency. The audit mechanism verifies that closed orders are properly removed and that inflight orders (submitted but not yet accepted) remain tracked during venue latency windows.

The audit interval can be configured using the own_books_audit_interval_secs parameter in live trading configurations.

**Examples:**

Example 1 (text):
```text
┌───────────────────┐                  │                   │                  │                   │                  │                   │          ┌───────►   OrderEmulator   ├────────────┐          │       │                   │            │          │       │                   │            │          │       │                   │            │┌─────────┴──┐    └─────▲──────┬──────┘            ││            │          │      │           ┌───────▼────────┐   ┌─────────────────────┐   ┌─────────────────────┐│            │          │      │           │                │   │                     │   │                     ││            ├──────────┼──────┼───────────►                ├───►                     ├───►                     ││  Strategy  │          │      │           │                │   │                     │   │                     ││            │          │      │           │   RiskEngine   │   │   ExecutionEngine   │   │   ExecutionClient   ││            ◄──────────┼──────┼───────────┤                ◄───┤                     ◄───┤                     ││            │          │      │           │                │   │                     │   │                     ││            │          │      │           │                │   │                     │   │                     │└─────────┬──┘    ┌─────┴──────▼──────┐    └───────▲────────┘   └─────────────────────┘   └─────────────────────┘          │       │                   │            │          │       │                   │            │          │       │                   │            │          └───────►   ExecAlgorithm   ├────────────┘                  │                   │                  │                   │                  │                   │                  └──────────────  ─────┘
```

Example 2 (python):
```python
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm# `engine` is an initialized BacktestEngine instanceexec_algorithm = TWAPExecAlgorithm()engine.add_exec_algorithm(exec_algorithm)
```

Example 3 (python):
```python
from decimal import Decimalfrom nautilus_trader.model.data import BarTypefrom nautilus_trader.test_kit.providers import TestInstrumentProviderfrom nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAP, EMACrossTWAPConfig# Configure your strategyconfig = EMACrossTWAPConfig(    instrument_id=TestInstrumentProvider.ethusdt_binance().id,    bar_type=BarType.from_str("ETHUSDT.BINANCE-250-TICK-LAST-INTERNAL"),    trade_size=Decimal("0.05"),    fast_ema_period=10,    slow_ema_period=20,    twap_horizon_secs=10.0,   # execution algorithm parameter (total horizon in seconds)    twap_interval_secs=2.5,    # execution algorithm parameter (seconds between orders))# Instantiate your strategystrategy = EMACrossTWAP(config=config)
```

Example 4 (python):
```python
from nautilus_trader.model.orders.base import Orderdef on_order(self, order: Order) -> None:    # Handle the order here
```

---

## Instruments

**URL:** https://nautilustrader.io/docs/latest/concepts/instruments

**Contents:**
- Instruments
- Symbology​
- Backtesting​
- Live trading​
- Finding instruments​
- Precisions and increments​
- Limits​
- Prices and quantities​
- Margins and fees​
  - When margins apply?​

The Instrument base class represents the core specification for any tradable asset/contract. There are currently a number of subclasses representing a range of asset classes and instrument classes which are supported by the platform:

All instruments should have a unique InstrumentId, which is made up of both the native symbol, and venue ID, separated by a period. For example, on the Binance Futures crypto exchange, the Ethereum Perpetual Futures Contract has the instrument ID ETHUSDT-PERP.BINANCE.

All native symbols should be unique for a venue (this is not always the case e.g. Binance share native symbols between spot and futures markets), and the {symbol.venue} combination must be unique for a Nautilus system.

The correct instrument must be matched to a market dataset such as ticks or order book data for logically sound operation. An incorrectly specified instrument may truncate data or otherwise produce surprising results.

Generic test instruments can be instantiated through the TestInstrumentProvider:

Exchange specific instruments can be discovered from live exchange data using an adapters InstrumentProvider:

Or flexibly defined by the user through an Instrument constructor, or one of its more specific subclasses:

See the full instrument API Reference.

Live integration adapters have defined InstrumentProvider classes which work in an automated way to cache the latest instrument definitions for the exchange. Refer to a particular Instrument object by passing the matching InstrumentId to data and execution related methods and classes that require one.

Since the same actor/strategy classes can be used for both backtest and live trading, you can get instruments in exactly the same way through the central cache:

It's also possible to subscribe to any changes to a particular instrument:

Or subscribe to all instrument changes for an entire venue:

When an update to the instrument(s) is received by the DataEngine, the object(s) will be passed to the actors/strategies on_instrument() method. A user can override this method with actions to take upon receiving an instrument update:

The instrument objects are a convenient way to organize the specification of an instrument through read-only properties. Correct price and quantity precisions, as well as minimum price and size increments, multipliers and standard lot sizes, are available.

Most of these limits are checked by the Nautilus RiskEngine, otherwise invalid values for prices and quantities can result in the exchange rejecting orders.

Certain value limits are optional for instruments and can be None, these are exchange dependent and can include:

Most of these limits are checked by the Nautilus RiskEngine, otherwise exceeding published limits can result in the exchange rejecting orders.

Instrument objects also offer a convenient way to create correct prices and quantities based on given values.

The above is the recommended method for creating valid prices and quantities, such as when passing them to the order factory to create an order.

Margin calculations are handled by the MarginAccount class. This section explains how margins work and introduces key concepts you need to know.

Each exchange (e.g., CME or Binance) operates with a specific account type that determines whether margin calculations are applicable. When setting up an exchange venue, you'll specify one of these account types:

To understand trading on margin, let’s start with some key terms:

Notional Value: The total contract value in the quote currency. It represents the full market value of your position. For example, with EUR/USD futures on CME (symbol 6E).

Leverage (leverage): The ratio that determines how much market exposure you can control relative to your account deposit. For example, with 10× leverage, you can control 10,000 USD worth of positions with just 1,000 USD in your account.

Initial Margin (margin_init): The margin rate required to open a position. It represents the minimum amount of funds that must be available in your account to open new positions. This is only a pre-check — no funds are actually locked.

Maintenance Margin (margin_maint): The margin rate required to keep a position open. This amount is locked in your account to maintain the position. It is always lower than the initial margin. You can view the total blocked funds (sum of maintenance margins for open positions) using the following in your strategy:

Maker/Taker Fees: The fees charged by exchanges based on your order's interaction with the market:

Not all exchanges or instruments implement maker/taker fees. If absent, set both maker_fee and taker_fee to 0 for the Instrument (e.g., FuturesContract, Equity, CurrencyPair, Commodity, Cfd, BinaryOption, BettingInstrument).

The MarginAccount class calculates margins using the following formulas:

For those interested in exploring the technical implementation:

Trading commissions represent the fees charged by exchanges or brokers for executing trades. While maker/taker fees are common in cryptocurrency markets, traditional exchanges like CME often employ other fee structures, such as per-contract commissions. NautilusTrader supports multiple commission models to accommodate diverse fee structures across different markets.

The framework provides two built-in fee model implementations:

While the built-in fee models cover common scenarios, you might encounter situations requiring specific commission structures. NautilusTrader's flexible architecture allows you to implement custom fee models by inheriting from the base FeeModel class.

For example, if you're trading futures on exchanges that charge per-contract commissions (like CME), you can implement a custom fee model. When creating custom fee models, we inherit from the FeeModel base class, which is implemented in Cython for performance reasons. This Cython implementation is reflected in the parameter naming convention, where type information is incorporated into parameter names using underscores (like Order_order or Quantity_fill_qty).

While these parameter names might look unusual to Python developers, they're a result of Cython's type system and help maintain consistency with the framework's core components. Here's how you could create a per-contract commission model:

This custom implementation calculates the total commission by multiplying a fixed per-contract fee by the number of contracts traded. The get_commission(...) method receives information about the order, fill quantity, fill price and instrument, allowing for flexible commission calculations based on these parameters.

Our new class PerContractFeeModel inherits class FeeModel, which is implemented in Cython, so notice the Cython-style parameter names in the method signature:

These parameter names follow NautilusTrader's Cython naming conventions, where the prefix indicates the expected type. While this might seem verbose compared to typical Python naming conventions, it ensures type safety and consistency with the framework's Cython codebase.

To use any fee model in your trading system, whether built-in or custom, you specify it when setting up the venue. Here's an example using the custom per-contract fee model:

When implementing custom fee models, ensure they accurately reflect the fee structure of your target exchange. Even small discrepancies in commission calculations can significantly impact strategy performance metrics during backtesting.

The raw instrument definition as provided by the exchange (typically from JSON serialized data) is also included as a generic Python dictionary. This is to retain all information which is not necessarily part of the unified Nautilus API, and is available to the user at runtime by calling the .info property.

The platform supports creating customized synthetic instruments, which can generate synthetic quote and trades. These are useful for:

Synthetic instruments cannot be traded directly, as they are constructs that only exist locally within the platform. They serve as analytical tools, providing useful metrics based on their component instruments.

In the future, we plan to support order management for synthetic instruments, enabling trading of their component instruments based on the synthetic instrument's behavior.

The venue for a synthetic instrument is always designated as 'SYNTH'.

A synthetic instrument is composed of a combination of two or more component instruments (which can include instruments from multiple venues), as well as a "derivation formula". Utilizing the dynamic expression engine powered by the evalexpr Rust crate, the platform can evaluate the formula to calculate the latest synthetic price tick from the incoming component instrument prices.

See the evalexpr documentation for a full description of available features, operators and precedence.

Before defining a new synthetic instrument, ensure that all component instruments are already defined and exist in the cache.

The following example demonstrates the creation of a new synthetic instrument with an actor/strategy. This synthetic instrument will represent a simple spread between Bitcoin and Ethereum spot prices on Binance. For this example, it is assumed that spot instruments for BTCUSDT.BINANCE and ETHUSDT.BINANCE are already present in the cache.

The instrument_id for the synthetic instrument in the above example will be structured as {symbol}.{SYNTH}, resulting in 'BTC-ETH:BINANCE.SYNTH'.

It's also possible to update a synthetic instrument formulas at any time. The following example shows how to achieve this with an actor/strategy.

The platform allows for emulated orders to be triggered based on synthetic instrument prices. In the following example, we build upon the previous one to submit a new emulated order. This order will be retained in the emulator until a trigger from synthetic quotes releases it. It will then be submitted to Binance as a MARKET order:

Considerable effort has been made to validate inputs, including the derivation formula for synthetic instruments. Despite this, caution is advised as invalid or erroneous inputs may lead to undefined behavior.

See the SyntheticInstrument API reference for a detailed understanding of input requirements and potential exceptions.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.test_kit.providers import TestInstrumentProvideraudusd = TestInstrumentProvider.default_fx_ccy("AUD/USD")
```

Example 2 (python):
```python
from nautilus_trader.adapters.binance.spot.providers import BinanceSpotInstrumentProviderfrom nautilus_trader.model import InstrumentIdprovider = BinanceSpotInstrumentProvider(client=binance_http_client)await provider.load_all_async()btcusdt = InstrumentId.from_str("BTCUSDT.BINANCE")instrument = provider.find(btcusdt)
```

Example 3 (python):
```python
from nautilus_trader.model.instruments import Instrumentinstrument = Instrument(...)  # <-- provide all necessary parameters
```

Example 4 (python):
```python
from nautilus_trader.model import InstrumentIdinstrument_id = InstrumentId.from_str("ETHUSDT-PERP.BINANCE")instrument = self.cache.instrument(instrument_id)
```

---

## Orders

**URL:** https://nautilustrader.io/docs/latest/concepts/orders

**Contents:**
- Orders
- Overview​
  - Terminology​
- Execution instructions​
  - Time in force​
  - Expire time​
  - Post-only​
  - Reduce-only​
  - Display quantity​
  - Trigger type​

This guide provides further details about the available order types for the platform, along with the execution instructions supported for each.

Orders are one of the fundamental building blocks of any algorithmic trading strategy. NautilusTrader supports a broad set of order types and execution instructions, from standard to advanced, exposing as much of a trading venue's functionality as possible. This enables traders to define instructions and contingencies for order execution and management, facilitating the creation of virtually any trading strategy.

All order types are derived from two fundamentals: Market and Limit orders. In terms of liquidity, they are opposites. Market orders consume liquidity by executing immediately at the best available price, whereas Limit orders provide liquidity by resting in the order book at a specified price until matched.

The order types available for the platform are (using the enum values):

NautilusTrader provides a unified API for many order types and execution instructions, but not all venues support every option. If an order includes an instruction or option the target venue does not support, the system does not submit it. Instead, it logs a clear, explanatory error.

Certain venues allow a trader to specify conditions and restrictions on how an order will be processed and executed. The following is a brief summary of the different execution instructions available.

The order's time in force specifies how long the order will remain open or active before any remaining quantity is canceled.

This instruction is to be used in conjunction with the GTD time in force to specify the time at which the order will expire and be removed from the venue's order book (or order management system).

An order which is marked as post_only will only ever participate in providing liquidity to the limit order book, and never initiating a trade which takes liquidity as an aggressor. This option is important for market makers, or traders seeking to restrict the order to a liquidity maker fee tier.

An order which is set as reduce_only will only ever reduce an existing position on an instrument and never open a new position (if already flat). The exact behavior of this instruction can vary between venues.

However, the behavior in the Nautilus SimulatedExchange is typical of a real venue.

The display_qty specifies the portion of a Limit order which is displayed on the limit order book. These are also known as iceberg orders as there is a visible portion to be displayed, with more quantity which is hidden. Specifying a display quantity of zero is also equivalent to setting an order as hidden.

Also known as trigger method which is applicable to conditional trigger orders, specifying the method of triggering the stop price.

Applicable to conditional trailing-stop trigger orders, specifies the method of triggering modification of the stop price based on the offset from the market (bid, ask or last price as applicable).

More advanced relationships can be specified between orders. For example, child orders can be assigned to trigger only when the parent is activated or filled, or orders can be linked so that one cancels or reduces the quantity of another. See the Advanced Orders section for more details.

The easiest way to create new orders is by using the built-in OrderFactory, which is automatically attached to every Strategy class. This factory will take care of lower level details - such as ensuring the correct trader ID and strategy ID are assigned, generation of a necessary initialization ID and timestamp, and abstracts away parameters which don't necessarily apply to the order type being created, or are only needed to specify more advanced execution instructions.

This leaves the factory with simpler order creation methods to work with, all the examples will leverage an OrderFactory from within a Strategy context.

See the OrderFactory API Reference for further details.

The following describes the order types which are available for the platform with a code example. Any optional parameters will be clearly marked with a comment which includes the default value.

A Market order is an instruction by the trader to immediately trade the given quantity at the best price available. You can also specify several time in force options, and indicate whether this order is only intended to reduce a position.

In the following example we create a Market order on the Interactive Brokers IdealPro Forex ECN to BUY 100,000 AUD using USD:

See the MarketOrder API Reference for further details.

A Limit order is placed on the limit order book at a specific price, and will only execute at that price (or better).

In the following example we create a Limit order on the Binance Futures Crypto exchange to SELL 20 ETHUSDT-PERP Perpetual Futures contracts at a limit price of 5000 USDT, as a market maker.

See the LimitOrder API Reference for further details.

A Stop-Market order is a conditional order which once triggered, will immediately place a Market order. This order type is often used as a stop-loss to limit losses, either as a SELL order against LONG positions, or as a BUY order against SHORT positions.

In the following example we create a Stop-Market order on the Binance Spot/Margin exchange to SELL 1 BTC at a trigger price of 100,000 USDT, active until further notice:

See the StopMarketOrder API Reference for further details.

A Stop-Limit order is a conditional order which once triggered will immediately place a Limit order at the specified price.

In the following example we create a Stop-Limit order on the Currenex FX ECN to BUY 50,000 GBP at a limit price of 1.3000 USD once the market hits the trigger price of 1.30010 USD, active until midday 6th June, 2022 (UTC):

See the StopLimitOrder API Reference for further details.

A Market-To-Limit order submits as a market order at the current best price. If the order partially fills, the system cancels the remainder and resubmits it as a Limit order at the executed price.

In the following example we create a Market-To-Limit order on the Interactive Brokers IdealPro Forex ECN to BUY 200,000 USD using JPY:

See the MarketToLimitOrder API Reference for further details.

A Market-If-Touched order is a conditional order which once triggered will immediately place a Market order. This order type is often used to enter a new position on a stop price, or to take profits for an existing position, either as a SELL order against LONG positions, or as a BUY order against SHORT positions.

In the following example we create a Market-If-Touched order on the Binance Futures exchange to SELL 10 ETHUSDT-PERP Perpetual Futures contracts at a trigger price of 10,000 USDT, active until further notice:

See the MarketIfTouchedOrder API Reference for further details.

A Limit-If-Touched order is a conditional order which once triggered will immediately place a Limit order at the specified price.

In the following example we create a Limit-If-Touched order to BUY 5 BTCUSDT-PERP Perpetual Futures contracts on the Binance Futures exchange at a limit price of 30,100 USDT (once the market hits the trigger price of 30,150 USDT), active until midday 6th June, 2022 (UTC):

See the LimitIfTouched API Reference for further details.

A Trailing-Stop-Market order is a conditional order which trails a stop trigger price a fixed offset away from the defined market price. Once triggered a Market order will immediately be placed.

In the following example we create a Trailing-Stop-Market order on the Binance Futures exchange to SELL 10 ETHUSD-PERP COIN_M margined Perpetual Futures Contracts activating at a price of 5,000 USD, then trailing at an offset of 1% (in basis points) away from the current last traded price:

See the TrailingStopMarketOrder API Reference for further details.

A Trailing-Stop-Limit order is a conditional order which trails a stop trigger price a fixed offset away from the defined market price. Once triggered a Limit order will immediately be placed at the defined price (which is also updated as the market moves until triggered).

In the following example we create a Trailing-Stop-Limit order on the Currenex FX ECN to BUY 1,250,000 AUD using USD at a limit price of 0.71000 USD, activating at 0.72000 USD then trailing at a stop offset of 0.00100 USD away from the current ask price, active until further notice:

See the TrailingStopLimitOrder API Reference for further details.

The following guide should be read in conjunction with the specific documentation from the broker or venue involving these order types, lists/groups and execution instructions (such as for Interactive Brokers).

Combinations of contingent orders, or larger order bulks can be grouped together into a list with a common order_list_id. The orders contained in this list may or may not have a contingent relationship with each other, as this is specific to how the orders themselves are constructed, and the specific venue they are being routed to.

OTO (One-Triggers-Other) – a parent order that, once executed, automatically places one or more child orders.

OCO (One-Cancels-Other) – two (or more) linked live orders where executing one cancels the remainder.

OUO (One-Updates-Other) – two (or more) linked live orders where executing one reduces the open quantity of the remainder.

These contingency types relate to ContingencyType FIX tag <1385> https://www.onixs.biz/fix-dictionary/5.0.sp2/tagnum_1385.html.

An OTO order involves two parts:

The default backtest venue for NautilusTrader uses a partial-trigger model for OTO orders. A future update will add configuration to opt-in to a full-trigger model.

Why the distinction matters Full trigger leaves a risk window: any partially filled position is live without its protective exit until the remaining quantity fills. Partial trigger mitigates that risk by ensuring every executed lot instantly has its linked stop/limit, at the cost of creating more order traffic and updates.

An OTO order can use any supported asset type on the venue (e.g. stock entry with option hedge, futures entry with OCO bracket, crypto spot entry with TP/SL).

An OCO order is a set of linked orders where the execution of any order (full or partial) triggers a best-efforts cancellation of the others. Both orders are live simultaneously; once one starts filling, the venue attempts to cancel the unexecuted portion of the remainder.

An OUO order is a set of linked orders where execution of one order causes an immediate reduction of open quantity in the other order(s). Both orders are live concurrently, and each partial execution proportionally updates the remaining quantity of its peer order on a best-effort basis.

Bracket orders are an advanced order type that allows traders to set both take-profit and stop-loss levels for a position simultaneously. This involves placing a parent order (entry order) and two child orders: a take-profit LIMIT order and a stop-loss STOP_MARKET order. When the parent order executes, the system places the child orders. The take-profit closes the position if the market moves favorably, and the stop-loss limits losses if it moves unfavorably.

Bracket orders can be easily created using the OrderFactory, which supports various order types, parameters, and instructions.

You should be aware of the margin requirements of positions, as bracketing a position will consume more order margin.

Before diving into the technical details, it's important to understand the fundamental purpose of emulated orders in NautilusTrader. At its core, emulation allows you to use certain order types even when your trading venue doesn't natively support them.

This works by having Nautilus locally mimic the behavior of these order types (such as STOP_LIMIT or TRAILING_STOP orders) locally, while using only simple MARKET and LIMIT orders for actual execution on the venue.

When you create an emulated order, Nautilus continuously tracks a specific type of market price (specified by the emulation_trigger parameter) and based on the order type and conditions you've set, will automatically submit the appropriate fundamental order (MARKET / LIMIT) when the triggering condition is met.

For example, if you create an emulated STOP_LIMIT order, Nautilus will monitor the market price until your stop price is reached, and then automatically submits a LIMIT order to the venue.

To perform emulation, Nautilus needs to know which type of market price it should monitor. By default, it uses bid and ask prices (quotes), which is why you'll often see emulation_trigger=TriggerType.DEFAULT in examples (this is equivalent to using TriggerType.BID_ASK). However, Nautilus supports various other price types, that can guide the emulation process.

The only requirement to emulate an order is to pass a TriggerType to the emulation_trigger parameter of an Order constructor, or OrderFactory creation method. The following emulation trigger types are currently supported:

The choice of trigger type determines how the order emulation will behave:

Here are all the available values you can set into emulation_trigger parameter and their purposes:

The platform makes it possible to emulate most order types locally, regardless of whether the type is supported on a trading venue. The logic and code paths for order emulation are exactly the same for all environment contexts and utilize a common OrderEmulator component.

There is no limitation on the number of emulated orders you can have per running instance.

An emulated order will progress through the following stages:

Emulated orders are subject to the same risk controls as regular orders, and can be modified and canceled by a trading strategy in the normal way. They will also be included when canceling all orders.

An emulated order will retain its original client order ID throughout its entire life cycle, making it easy to query through the cache.

The following will occur for an emulated order now held by the OrderEmulator component:

Once data arrival triggers / matches an emulated order locally, the following release actions will occur:

The following table lists which order types are possible to emulate, and which order type they transform to when being released for submission to the trading venue.

The following table lists which order types are possible to emulate, and which order type they transform to when being released for submission to the trading venue.

When writing trading strategies, it may be necessary to know the state of emulated orders in the system. There are several ways to query emulation status:

The following Cache methods are available:

See the full API reference for additional details.

You can query order objects directly using:

If either of these return False, then the order has been released from the OrderEmulator, and so is no longer considered an emulated order (or was never an emulated order).

It's not advised to hold a local reference to an emulated order, as the order object will be transformed when/if the emulated order is released. You should rely on the Cache which is made for the job.

If a running system either crashes or shuts down with active emulated orders, then they will be reloaded inside the OrderEmulator from any configured cache database. This ensures order state persistence across system restarts and recoveries.

When working with emulated orders, consider the following best practices:

Order emulation allows you to use advanced order types even on venues that don't natively support them, making your trading strategies more portable across different venues.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.model.enums import OrderSidefrom nautilus_trader.model.enums import TimeInForcefrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model import Quantityfrom nautilus_trader.model.orders import MarketOrderorder: MarketOrder = self.order_factory.market(    instrument_id=InstrumentId.from_str("AUD/USD.IDEALPRO"),    order_side=OrderSide.BUY,    quantity=Quantity.from_int(100_000),    time_in_force=TimeInForce.IOC,  # <-- optional (default GTC)    reduce_only=False,  # <-- optional (default False)    tags=["ENTRY"],  # <-- optional (default None))
```

Example 2 (python):
```python
from nautilus_trader.model.enums import OrderSidefrom nautilus_trader.model.enums import TimeInForcefrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model import Pricefrom nautilus_trader.model import Quantityfrom nautilus_trader.model.orders import LimitOrderorder: LimitOrder = self.order_factory.limit(    instrument_id=InstrumentId.from_str("ETHUSDT-PERP.BINANCE"),    order_side=OrderSide.SELL,    quantity=Quantity.from_int(20),    price=Price.from_str("5_000.00"),    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)    expire_time=None,  # <-- optional (default None)    post_only=True,  # <-- optional (default False)    reduce_only=False,  # <-- optional (default False)    display_qty=None,  # <-- optional (default None which indicates full display)    tags=None,  # <-- optional (default None))
```

Example 3 (python):
```python
from nautilus_trader.model.enums import OrderSidefrom nautilus_trader.model.enums import TimeInForcefrom nautilus_trader.model.enums import TriggerTypefrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model import Pricefrom nautilus_trader.model import Quantityfrom nautilus_trader.model.orders import StopMarketOrderorder: StopMarketOrder = self.order_factory.stop_market(    instrument_id=InstrumentId.from_str("BTCUSDT.BINANCE"),    order_side=OrderSide.SELL,    quantity=Quantity.from_int(1),    trigger_price=Price.from_int(100_000),    trigger_type=TriggerType.LAST_PRICE,  # <-- optional (default DEFAULT)    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)    expire_time=None,  # <-- optional (default None)    reduce_only=False,  # <-- optional (default False)    tags=None,  # <-- optional (default None))
```

Example 4 (python):
```python
import pandas as pdfrom nautilus_trader.model.enums import OrderSidefrom nautilus_trader.model.enums import TimeInForcefrom nautilus_trader.model.enums import TriggerTypefrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model import Pricefrom nautilus_trader.model import Quantityfrom nautilus_trader.model.orders import StopLimitOrderorder: StopLimitOrder = self.order_factory.stop_limit(    instrument_id=InstrumentId.from_str("GBP/USD.CURRENEX"),    order_side=OrderSide.BUY,    quantity=Quantity.from_int(50_000),    price=Price.from_str("1.30000"),    trigger_price=Price.from_str("1.30010"),    trigger_type=TriggerType.BID_ASK,  # <-- optional (default DEFAULT)    time_in_force=TimeInForce.GTD,  # <-- optional (default GTC)    expire_time=pd.Timestamp("2022-06-06T12:00"),    post_only=True,  # <-- optional (default False)    reduce_only=False,  # <-- optional (default False)    tags=None,  # <-- optional (default None))
```

---

## Data

**URL:** https://nautilustrader.io/docs/latest/concepts/data

**Contents:**
- Data
- Order books​
- Instruments​
- Bars and aggregation​
  - Introduction to bars​
  - Purpose of data aggregation​
  - Aggregation methods​
  - Types of aggregation​
  - Bar types​
  - Aggregation sources​

NautilusTrader provides a set of built-in data types specifically designed to represent a trading domain. These data types include:

NautilusTrader is designed primarily to operate on granular order book data, providing the highest realism for execution simulations in backtesting. However, backtests can also be conducted on any of the supported market data types, depending on the desired simulation fidelity.

A high-performance order book implemented in Rust is available to maintain order book state based on provided data.

OrderBook instances are maintained per instrument for both backtesting and live trading, with the following book types available:

Top-of-book data, such as QuoteTick, TradeTick and Bar, can also be used for backtesting, with markets operating on L1_MBP book types.

The following instrument definitions are available:

A bar (also known as a candle, candlestick or kline) is a data structure that represents price and volume information over a specific period, including:

The system generates bars using an aggregation method that groups data by specific criteria.

Data aggregation in NautilusTrader transforms granular market data into structured bars or candles for several reasons:

The platform implements various aggregation methods:

The following bar aggregations are not currently implemented:

NautilusTrader implements three distinct data aggregation methods:

Trade-to-bar aggregation: Creates bars from TradeTick objects (executed trades)

Quote-to-bar aggregation: Creates bars from QuoteTick objects (bid/ask prices)

Bar-to-bar aggregation: Creates larger-timeframe Bar objects from smaller-timeframe Bar objects

NautilusTrader defines a unique bar type (BarType class) based on the following components:

Bar types can also be classified as either standard or composite:

Bar data aggregation can be either internal or external:

For bar-to-bar aggregation, the target bar type is always INTERNAL (since you're doing the aggregation within NautilusTrader), but the source bars can be either INTERNAL or EXTERNAL, i.e., you can aggregate externally provided bars or already aggregated internal bars.

You can define standard bar types from strings using the following convention:

{instrument_id}-{step}-{aggregation}-{price_type}-{INTERNAL | EXTERNAL}

For example, to define a BarType for AAPL trades (last price) on Nasdaq (XNAS) using a 5-minute interval aggregated from trades locally by Nautilus:

Composite bars are derived by aggregating higher-granularity bars into the desired bar type. To define a composite bar, use this convention:

{instrument_id}-{step}-{aggregation}-{price_type}-INTERNAL@{step}-{aggregation}-{INTERNAL | EXTERNAL}

For example, to define a BarType for AAPL trades (last price) on Nasdaq (XNAS) using a 5-minute interval aggregated locally by Nautilus, from 1-minute interval bars aggregated externally:

The BarType string format encodes both the target bar type and, optionally, the source data type:

The part after the @ symbol is optional and only used for bar-to-bar aggregation:

You can create complex aggregation chains where you aggregate from already aggregated bars:

NautilusTrader provides two distinct operations for working with bars:

These methods work together in a typical workflow:

Example usage in on_start():

Required handlers in your strategy to receive the data:

When requesting historical bars for backtesting or initializing indicators, you can use the request_bars() method, which supports both direct requests and aggregation:

If historical aggregated bars are needed, you can use specialized request request_aggregated_bars() method:

Register indicators before requesting data: Ensure indicators are registered before requesting historical data so they get updated properly.

The platform uses two fundamental timestamp fields that appear across many objects, including market data, orders, and events. These timestamps serve distinct purposes and help maintain precise timing information throughout the system:

The ts_init field represents a more general concept than just the "time of reception" for events. It denotes the timestamp when an object, such as a data point or command, was initialized within Nautilus. This distinction is important because ts_init is not exclusive to "received events" — it applies to any internal initialization process.

For example, the ts_init field is also used for commands, where the concept of reception does not apply. This broader definition ensures consistent handling of initialization timestamps across various object types in the system.

The dual timestamp system enables latency analysis within the platform:

The ts_init field indicates when the message was originally received.

The platform ensures consistency by flowing data through the same pathways across all system environment contexts (e.g., backtest, sandbox, live). Data is primarily transported via the MessageBus to the DataEngine and then distributed to subscribed or registered handlers.

For users who need more flexibility, the platform also supports the creation of custom data types. For details on how to implement user-defined data types, see the Custom Data section below.

NautilusTrader facilitates data loading and conversion for three main use cases:

Regardless of the destination, the process remains the same: converting diverse external data formats into Nautilus data structures.

To achieve this, two main components are necessary:

Data loader components are typically specific for the raw source/format and per integration. For instance, Binance order book data is stored in its raw CSV file form with an entirely different format to Databento Binary Encoding (DBN) files.

Data wranglers are implemented per specific Nautilus data type, and can be found in the nautilus_trader.persistence.wranglers module. Currently there exists:

There are a number of DataWrangler v2 components, which will take a pd.DataFrame typically with a different fixed width Nautilus Arrow v2 schema, and output PyO3 Nautilus objects which are only compatible with the new version of the Nautilus core, currently in development.

These PyO3 provided data objects are not compatible where the legacy Cython objects are currently used (e.g., adding directly to a BacktestEngine).

The following diagram illustrates how raw data is transformed into Nautilus data structures:

Concretely, this would involve:

The following example shows how to accomplish the above in Python:

The data catalog is a central store for Nautilus data, persisted in the Parquet file format. It serves as the primary data management system for both backtesting and live trading scenarios, providing efficient storage, retrieval, and streaming capabilities for market data.

The NautilusTrader data catalog is built on a dual-backend architecture that combines the performance of Rust with the flexibility of Python:

Storage format advantages:

The Arrow schemas used for the Parquet format are primarily single-sourced in the core persistence Rust crate, with some legacy schemas available from the /serialization/arrow/schema.py module.

The current plan is to eventually phase out the Python schemas module, so that all schemas are single sourced in the Rust core for consistency and performance.

The data catalog can be initialized from a NAUTILUS_PATH environment variable, or by explicitly passing in a path like object.

The NAUTILUS_PATH environment variable should point to the root directory containing your Nautilus data. The catalog will automatically append /catalog to this path.

This is a common pattern when using ParquetDataCatalog.from_env() - make sure your NAUTILUS_PATH points to the parent directory, not the catalog directory itself.

The following example shows how to initialize a data catalog where there is pre-existing data already written to disk at the given path.

The catalog supports multiple filesystem protocols through fsspec integration, enabling seamless operation across local and cloud storage systems.

Local filesystem (file):

Google Cloud Storage (gcs):

For convenience, you can use URI strings that automatically parse protocol and storage options:

Store data in the catalog using the write_data() method. All Nautilus built-in Data objects are supported, and any data which inherits from Data can be written.

The catalog automatically generates filenames based on the timestamp range of the data being written. Files are named using the pattern {start_timestamp}_{end_timestamp}.parquet where timestamps are in ISO format.

Data is organized in directories by data type and instrument ID:

Rust backend data types (enhanced performance):

The following data types use optimized Rust implementations:

By default, data that overlaps with existing files will cause an assertion error to maintain data integrity. Use skip_disjoint_check=True in write_data() to bypass this check when needed.

Use the query() method to read data back from the catalog:

The BacktestDataConfig class is the primary mechanism for specifying data requirements before a backtest starts. It defines what data should be loaded from the catalog and how it should be filtered and processed during the backtest execution.

Loading multiple instruments:

Cloud Storage with Custom Filtering:

Custom Data with Client ID:

The BacktestDataConfig objects are integrated into the backtesting framework through BacktestRunConfig:

When a backtest runs, the BacktestNode processes each BacktestDataConfig:

The system automatically handles:

The DataCatalogConfig class provides configuration for on-the-fly data loading scenarios, particularly useful for backtests where the number of possible instruments is vast, Unlike BacktestDataConfig which pre-specifies data for backtests, DataCatalogConfig enables flexible catalog access during runtime. Catalogs defined this way can also be used for requesting historical data.

Local Catalog Configuration:

Cloud storage configuration:

DataCatalogConfig is commonly used in live trading configurations for historical data access:

For streaming data to catalogs during live trading or backtesting, use StreamingConfig:

Historical Data Analysis:

Dynamic data loading:

Research and development:

The catalog's query system leverages a sophisticated dual-backend architecture that automatically selects the optimal query engine based on data type and query parameters.

Rust backend (high performance):

PyArrow backend (flexible):

Core query parameters:

Advanced filtering examples:

The catalog provides several operation functions for maintaining and organizing data files. These operations help optimize storage, improve query performance, and ensure data integrity.

Reset parquet file names to match their actual content timestamps. This ensures filename-based filtering works correctly.

Reset all files in catalog:

Reset specific data type:

Combine multiple small parquet files into larger files to improve query performance and reduce storage overhead.

Consolidate entire catalog:

Consolidate specific data type:

Split data files into fixed time periods for standardized file organization.

Consolidate entire catalog by period:

Consolidate specific data by period:

Remove data within a specified time range for specific data types and instruments. This operation permanently deletes data and handles file intersections intelligently.

Delete entire catalog range:

Delete specific data type:

Delete operations permanently remove data and cannot be undone. Files that partially overlap the deletion range are split to preserve data outside the range.

The catalog supports streaming data to temporary feather files during backtests, which can then be converted to permanent parquet format for efficient querying.

Example: option greeks streaming

The NautilusTrader data catalog provides comprehensive market data management:

NautilusTrader defines an internal data format specified in the nautilus_model crate. These models are serialized into Arrow record batches and written to Parquet files. Nautilus backtesting is most efficient when using these Nautilus-format Parquet files.

However, migrating the data model between precision modes and schema changes can be challenging. This guide explains how to handle data migrations using our utility tools.

The nautilus_persistence crate provides two key utilities:

Converts Parquet files to JSON while preserving metadata:

Automatically detects data type from filename:

Converts JSON back to Parquet format:

The following migration examples both use trades data (you can also migrate the other data types in the same way). All commands should be run from the root of the persistence crate directory.

This example describes a scenario where you want to migrate from standard-precision schema to high-precision schema.

If you're migrating from a catalog that used the Int64 and UInt64 Arrow data types for prices and sizes, be sure to check out commit e284162 before compiling the code that writes the initial JSON.

1. Convert from standard-precision Parquet to JSON:

This will create trades.json and trades.metadata.json files.

2. Convert from JSON to high-precision Parquet:

Add the --features high-precision flag to write data as high-precision (128-bit) schema Parquet.

This will create a trades.parquet file with high-precision schema data.

This example describes a scenario where you want to migrate from one schema version to another.

1. Convert from old schema Parquet to JSON:

Add the --features high-precision flag if the source data uses a high-precision (128-bit) schema.

This will create trades.json and trades.metadata.json files.

2. Switch to new schema version:

3. Convert from JSON back to new schema Parquet:

This will create a trades.parquet file with the new schema.

Due to the modular nature of the Nautilus design, it is possible to set up systems with very flexible data streams, including custom user-defined data types. This guide covers some possible use cases for this functionality.

It's possible to create custom data types within the Nautilus system. First you will need to define your data by subclassing from Data.

As Data holds no state, it is not strictly necessary to call super().__init__().

The Data abstract base class acts as a contract within the system and requires two properties for all types of data: ts_event and ts_init. These represent the UNIX nanosecond timestamps for when the event occurred and when the object was initialized, respectively.

The recommended approach to satisfy the contract is to assign ts_event and ts_init to backing fields, and then implement the @property for each as shown above (for completeness, the docstrings are copied from the Data base class).

These timestamps enable Nautilus to correctly order data streams for backtests using monotonically increasing ts_init UNIX nanoseconds.

We can now work with this data type for backtesting and live trading. For instance, we could now create an adapter which is able to parse and create objects of this type - and send them back to the DataEngine for consumption by subscribers.

You can publish a custom data type within your actor/strategy using the message bus in the following way:

The metadata dictionary optionally adds more granular information that is used in the topic name to publish data with the message bus.

Extra metadata information can also be passed to a BacktestDataConfig configuration object in order to enrich and describe custom data objects used in a backtesting context:

You can subscribe to custom data types within your actor/strategy in the following way:

The client_id provides an identifier to route the data subscription to a specific client.

This will result in your actor/strategy passing these received MyDataPoint objects to your on_data method. You will need to check the type, as this method acts as a flexible handler for all custom data.

Here is an example of publishing and receiving signal data using the MessageBus from an actor or strategy. A signal is an automatically generated custom data identified by a name containing only one value of a basic type (str, float, int, bool or bytes).

This example demonstrates how to create a custom data type for option Greeks, specifically the delta. By following these steps, you can create custom data types, subscribe to them, publish them, and store them in the Cache or ParquetDataCatalog for efficient retrieval.

Here is an example of publishing and receiving data using the MessageBus from an actor or strategy:

Here is an example of writing and reading data using the Cache from an actor or strategy:

For streaming custom data to feather files or writing it to parquet files in a catalog (register_arrow needs to be used):

The @customdataclass decorator enables the creation of a custom data class with default implementations for all the features described above.

Each method can also be overridden if needed. Here is an example of its usage:

To enhance development convenience and improve code suggestions in your IDE, you can create a .pyi stub file with the proper constructor signature for your custom data types as well as type hints for attributes. This is particularly useful when the constructor is dynamically generated at runtime, as it allows the IDE to recognize and provide suggestions for the class's methods and attributes.

For instance, if you have a custom data class defined in greeks.py, you can create a corresponding greeks.pyi file with the following constructor signature:

**Examples:**

Example 1 (python):
```python
bar_type = BarType.from_str("AAPL.XNAS-5-MINUTE-LAST-INTERNAL")
```

Example 2 (python):
```python
bar_type = BarType.from_str("AAPL.XNAS-5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL")
```

Example 3 (text):
```text
{instrument_id}-{step}-{aggregation}-{price_type}-{source}@{step}-{aggregation}-{source}
```

Example 4 (python):
```python
def on_start(self) -> None:    # Define a bar type for aggregating from TradeTick objects    # Uses price_type=LAST which indicates TradeTick data as source    bar_type = BarType.from_str("6EH4.XCME-50-VOLUME-LAST-INTERNAL")    # Request historical data (will receive bars in on_historical_data handler)    self.request_bars(bar_type)    # Subscribe to live data (will receive bars in on_bar handler)    self.subscribe_bars(bar_type)
```

---

## Concepts

**URL:** https://nautilustrader.io/docs/latest/concepts/

**Contents:**
- Concepts
- Overview​
- Architecture​
- Actors​
- Strategies​
- Instruments​
- Data​
- Execution​
- Orders​
- Positions​

Concept guides introduce and explain the foundational ideas, components, and best practices that underpin the NautilusTrader platform. These guides are designed to provide both conceptual and practical insights, helping you navigate the system's architecture, strategies, data management, execution flow, and more. Explore the following guides to deepen your understanding and make the most of NautilusTrader.

The Overview guide covers the main features and intended use cases for the platform.

The Architecture guide dives deep into the foundational principles, structures, and designs that underpin the platform. It is ideal for developers, system architects, or anyone curious about the inner workings of NautilusTrader.

The Actor serves as the foundational component for interacting with the trading system. The Actors guide covers capabilities and implementation specifics.

The Strategy is at the heart of the NautilusTrader user experience when writing and working with trading strategies. The Strategies guide covers how to implement strategies for the platform.

The Instruments guide covers the different instrument definition specifications for tradable assets and contracts.

The NautilusTrader platform defines a range of built-in data types crafted specifically to represent a trading domain. The Data guide covers working with both built-in and custom data.

NautilusTrader can handle trade execution and order management for multiple strategies and venues simultaneously (per instance). The Execution guide covers components involved in execution, as well as the flow of execution messages (commands and events).

The Orders guide provides more details about the available order types for the platform, along with the execution instructions supported for each. Advanced order types and emulated orders are also covered.

The Positions guide explains how positions work in NautilusTrader, including their lifecycle, aggregation from order fills, profit and loss calculations, and the important concept of position snapshotting for netting OMS configurations.

The Cache is a central in-memory data store for managing all trading-related data. The Cache guide covers capabilities and best practices of the cache.

The MessageBus is the core communication system enabling decoupled messaging patterns between components, including point-to-point, publish/subscribe, and request/response. The Message Bus guide covers capabilities and best practices of the MessageBus.

The Portfolio serves as the central hub for managing and tracking all positions across active strategies for the trading node or backtest. It consolidates position data from multiple instruments, providing a unified view of your holdings, risk exposure, and overall performance. Explore this section to understand how NautilusTrader aggregates and updates portfolio state to support effective trading and risk management.

The Reports guide covers the reporting capabilities in NautilusTrader, including execution reports, portfolio analysis reports, PnL accounting considerations, and how reports are used for backtest post-run analysis.

The platform provides logging for both backtesting and live trading using a high-performance logger implemented in Rust.

Backtesting with NautilusTrader is a methodical simulation process that replicates trading activities using a specific system implementation.

Live trading in NautilusTrader enables traders to deploy their backtested strategies in real-time without any code changes. This seamless transition ensures consistency and reliability, though there are key differences between backtesting and live trading.

The NautilusTrader design allows for integrating data providers and/or trading venues through adapter implementations. The Adapters guide covers requirements and best practices for developing new integration adapters for the platform.

The API Reference documentation should be considered the source of truth for the platform. If there are any discrepancies between concepts described here and the API Reference, then the API Reference should be considered the correct information. We are working to ensure that concepts stay up-to-date with the API Reference and will be introducing doc tests in the near future to help with this.

---

## Overview

**URL:** https://nautilustrader.io/docs/latest/concepts/overview

**Contents:**
- Overview
- Introduction​
- Features​
- Why NautilusTrader?​
- Use cases​
- Distributed​
- Common core​
- Backtesting​
- Live trading​
- Domain model​

NautilusTrader is an open-source, high-performance, production-grade algorithmic trading platform, providing quantitative traders with the ability to backtest portfolios of automated trading strategies on historical data with an event-driven engine, and also deploy those same strategies live, with no code changes.

The platform is AI-first, designed to develop and deploy algorithmic trading strategies within a highly performant and robust Python-native environment. This helps to address the parity challenge of keeping the Python research/backtest environment consistent with the production live trading environment.

NautilusTrader's design, architecture, and implementation philosophy prioritizes software correctness and safety at the highest level, with the aim of supporting Python-native, mission-critical, trading system backtesting and live deployment workloads.

The platform is also universal and asset-class-agnostic — with any REST API or WebSocket stream able to be integrated via modular adapters. It supports high-frequency trading across a wide range of asset classes and instrument types including FX, Equities, Futures, Options, Crypto, DeFi, and Betting — enabling seamless operations across multiple venues simultaneously.

nautilus - from ancient Greek 'sailor' and naus 'ship'.

The nautilus shell consists of modular chambers with a growth factor which approximates a logarithmic spiral. The idea is that this can be translated to the aesthetics of design and architecture.

Traditionally, trading strategy research and backtesting might be conducted in Python using vectorized methods, with the strategy then needing to be reimplemented in a more event-driven way using C++, C#, Java or other statically typed language(s). The reasoning here is that vectorized backtesting code cannot express the granular time and event dependent complexity of real-time trading, where compiled languages have proven to be more suitable due to their inherently higher performance, and type safety.

One of the key advantages of NautilusTrader here, is that this reimplementation step is now circumvented - as the critical core components of the platform have all been written entirely in Rust or Cython. This means we're using the right tools for the job, where systems programming languages compile performant binaries, with CPython C extension modules then able to offer a Python-native environment, suitable for professional quantitative traders and trading firms.

There are three main use cases for this software package:

The project's codebase provides a framework for implementing the software layer of systems which achieve the above. You will find the default backtest and live system implementations in their respectively named subpackages. A sandbox environment can be built using the sandbox adapter.

The platform is designed to be easily integrated into a larger distributed system. To facilitate this, nearly all configuration and domain objects can be serialized using JSON, MessagePack or Apache Arrow (Feather) for communication over the network.

The common system core is utilized by all node environment contexts (backtest, sandbox, and live). User-defined Actor, Strategy and ExecAlgorithm components are managed consistently across these environment contexts.

Backtesting can be achieved by first making data available to a BacktestEngine either directly or via a higher level BacktestNode and ParquetDataCatalog, and then running the data through the system with nanosecond resolution.

A TradingNode can ingest data and events from multiple data and execution clients. Live deployments can use both demo/paper trading accounts, or real accounts.

For live trading, a TradingNode can ingest data and events from multiple data and execution clients. The platform supports both demo/paper trading accounts and real accounts. High performance can be achieved by running asynchronously on a single event loop, with the potential to further boost performance by leveraging the uvloop implementation (available for Linux and macOS).

The platform features a comprehensive trading domain model that includes various value types such as Price and Quantity, as well as more complex entities such as Order and Position objects, which are used to aggregate multiple events to determine state.

All timestamps within the platform are recorded at nanosecond precision in UTC.

Timestamp strings follow ISO 8601 (RFC 3339) format with either 9 digits (nanoseconds) or 3 digits (milliseconds) of decimal precision, (but mostly nanoseconds) always maintaining all digits including trailing zeros. These can be seen in log messages, and debug/display outputs for objects.

A timestamp string consists of:

Example: 2024-01-05T15:30:45.123456789Z

For the complete specification, refer to RFC 3339: Date and Time on the Internet.

The platform uses Universally Unique Identifiers (UUID) version 4 (RFC 4122) for unique identifiers. Our high-performance implementation leverages the uuid crate for correctness validation when parsing from strings, ensuring input UUIDs comply with the specification.

A valid UUID v4 consists of:

Example: 2d89666b-1a1e-4a75-b193-4eb3b454c757

For the complete specification, refer to RFC 4122: A Universally Unique IIdentifier (UUID) URN Namespace.

The following market data types can be requested historically, and also subscribed to as live streams when available from a venue / data provider, and implemented in an integrations adapter.

The following PriceType options can be used for bar aggregations:

The following BarAggregation methods are available:

Currently implemented aggregations:

Aggregations listed above that are not repeated in the implemented list are planned but not yet available.

The price types and bar aggregations can be combined with step sizes >= 1 in any way through a BarSpecification. This enables maximum flexibility and now allows alternative bars to be aggregated for live trading.

The following account types are available for both live and backtest environments:

The following order types are available (when possible on a venue):

The following value types are backed by either 128-bit or 64-bit raw integer values, depending on the precision mode used during compilation.

When the high-precision feature flag is enabled (default), values use the specification:

When the high-precision feature flag is disabled, values use the specification:

---

## Logging

**URL:** https://nautilustrader.io/docs/latest/concepts/logging

**Contents:**
- Logging
- Configuration​
  - Standard output logging​
  - File logging​
    - Log file rotation​
    - Log file naming convention​
  - Component log filtering​
  - Components-only logging​
  - Log Colors​
- Using a logger directly​

The platform provides logging for both backtesting and live trading using a high-performance logging subsystem implemented in Rust with a standardized facade from the log crate.

The core logger operates in a separate thread and uses a multi-producer single-consumer (MPSC) channel to receive log messages. This design ensures that the main thread remains performant, avoiding potential bottlenecks caused by log string formatting or file I/O operations.

Logging output is configurable and supports:

Infrastructure such as Vector can be integrated to collect and aggregate events within your system.

Logging can be configured by importing the LoggingConfig object. By default, log events with an 'INFO' LogLevel and higher are written to stdout/stderr.

Log level (LogLevel) values include (and generally match Rust's tracing level filters).

Python loggers expose the following levels:

The Python Logger does not provide a trace() method; TRACE level logs are only emitted by the underlying Rust components and cannot be generated directly from Python code. However, you can set TRACE as a logging level filter to see trace logs from Rust components.

See the LoggingConfig API Reference for further details.

Logging can be configured in the following ways:

Log messages are written to the console via stdout/stderr writers. The minimum log level can be configured using the log_level parameter.

Log files are written to the current working directory by default. The naming convention and rotation behavior are configurable and follow specific patterns based on your settings.

You can specify a custom log directory using log_directory and/or a custom file basename using log_file_name. Log files are always suffixed with .log (plain text) or .json (JSON).

For detailed information about log file naming conventions and rotation behavior, see the Log file rotation and Log file naming convention sections below.

Rotation behavior depends on both the presence of a size limit and whether a custom file name is provided:

The default naming convention ensures log files are uniquely identifiable and timestamped. The format depends on whether file rotation is enabled:

With file rotation enabled:

Without size-based rotation (default naming):

If log_file_name is set (e.g., my_custom_log):

The log_component_levels parameter can be used to set log levels for each component individually. The input value should be a dictionary of component ID strings to log level strings: dict[str, str].

Below is an example of a trading node logging configuration that includes some of the options mentioned above:

For backtesting, the BacktestEngineConfig class can be used instead of TradingNodeConfig, as the same options are available.

When focusing on a subset of noisy systems, enable log_components_only to log messages only from components explicitly listed in log_component_levels. All other components are suppressed regardless of the global log_level or file level.

Example (Python configuration):

If configuring via the environment using the Rust spec string, include log_components_only alongside component filters, for example:

If log_components_only=True (or log_components_only is present in the spec string) and log_component_levels is empty, no log messages will be emitted to stdout/stderr or files. Add at least one component filter or disable components-only logging.

ANSI color codes are utilized to enhance the readability of logs when viewed in a terminal. These color codes can make it easier to distinguish different parts of log messages. In environments that do not support ANSI color rendering (such as some cloud environments or text editors), these color codes may not be appropriate as they can appear as raw text.

To accommodate for such scenarios, the LoggingConfig.log_colors option can be set to false. Disabling log_colors will prevent the addition of ANSI color codes to the log messages, ensuring compatibility across different environments where color rendering is not supported.

It's possible to use Logger objects directly, and these can be initialized anywhere (very similar to the Python built-in logging API).

If you aren't using an object which already initializes a NautilusKernel (and logging) such as BacktestEngine or TradingNode, then you can activate logging in the following way:

See the init_logging API Reference for further details.

Only one logging subsystem can be initialized per process with an init_logging call. Multiple LogGuard instances (up to 255) can exist concurrently, and the logging thread will remain active until all guards are dropped.

The LogGuard ensures that the logging subsystem remains active and operational throughout the lifecycle of a process. It prevents premature shutdown of the logging subsystem when running multiple engines in the same process.

The logging system uses reference counting to track active LogGuard instances:

This mechanism ensures that:

Without a LogGuard, any attempt to run sequential engines in the same process may result in errors such as:

This occurs because the logging subsystem's underlying channel and Rust Logger are closed when the first engine is disposed. As a result, subsequent engines lose access to the logging subsystem, leading to these errors.

By leveraging a LogGuard, you can ensure robust logging behavior across multiple backtests or engine runs in the same process. The LogGuard retains the resources of the logging subsystem and ensures that logs continue to function correctly, even as engines are disposed and initialized.

Using LogGuard is critical to maintain consistent logging behavior throughout a process with multiple engines.

The following example demonstrates how to use a LogGuard when running multiple engines sequentially in the same process:

On Windows, non-deterministic garbage collection during interpreter shutdown can occasionally prevent the logging thread from joining properly. When the last LogGuard is dropped, the logging subsystem signals the background thread to close and joins it to ensure all pending messages are written. If Python's garbage collector delays dropping the guard until after interpreter shutdown has begun, this join may not complete, resulting in truncated logs.

This issue is tracked in GitHub issue #3027. A more deterministic shutdown mechanism is under consideration.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.config import LoggingConfigfrom nautilus_trader.config import TradingNodeConfigconfig_node = TradingNodeConfig(    trader_id="TESTER-001",    logging=LoggingConfig(        log_level="INFO",        log_level_file="DEBUG",        log_file_format="json",        log_component_levels={ "Portfolio": "INFO" },    ),    ... # Omitted)
```

Example 2 (python):
```python
logging = LoggingConfig(    log_level="INFO",    log_component_levels={        "RiskEngine": "DEBUG",        "Portfolio": "INFO",    },    log_components_only=True,)
```

Example 3 (bash):
```bash
export NAUTILUS_LOG="stdout=Info;log_components_only;RiskEngine=Debug;Portfolio=Info"
```

Example 4 (python):
```python
from nautilus_trader.common.component import init_loggingfrom nautilus_trader.common.component import Loggerlog_guard = init_logging()logger = Logger("MyLogger")
```

---

## Portfolio

**URL:** https://nautilustrader.io/docs/latest/concepts/portfolio

**Contents:**
- Portfolio
- Portfolio statistics​
- Custom statistics​
- Backtest analysis​

We are currently working on this concept guide.

The Portfolio serves as the central hub for managing and tracking all positions across active strategies for the trading node or backtest. It consolidates position data from multiple instruments, providing a unified view of your holdings, risk exposure, and overall performance. Explore this section to understand how NautilusTrader aggregates and updates portfolio state to support effective trading and risk management.

There are a variety of built-in portfolio statistics which are used to analyse a trading portfolios performance for both backtests and live trading.

The statistics are generally categorized as follows.

It's also possible to call a traders PortfolioAnalyzer and calculate statistics at any arbitrary time, including during a backtest, or live trading session.

Custom portfolio statistics can be defined by inheriting from the PortfolioStatistic base class, and implementing any of the calculate_ methods.

For example, the following is the implementation for the built-in WinRate statistic:

These statistics can then be registered with a traders PortfolioAnalyzer.

Ensure your statistic is robust to degenerate inputs such as None, empty series, or insufficient data.

The expectation is that you would then return None, NaN or a reasonable default.

Following a backtest run, a performance analysis will be carried out by passing realized PnLs, returns, positions and orders data to each registered statistic in turn, calculating their values (with a default configuration). Any output is then displayed in the tear sheet under the Portfolio Performance heading, grouped as.

**Examples:**

Example 1 (python):
```python
import pandas as pdfrom typing import Anyfrom nautilus_trader.analysis.statistic import PortfolioStatisticclass WinRate(PortfolioStatistic):    """    Calculates the win rate from a realized PnLs series.    """    def calculate_from_realized_pnls(self, realized_pnls: pd.Series) -> Any | None:        # Preconditions        if realized_pnls is None or realized_pnls.empty:            return 0.0        # Calculate statistic        winners = [x for x in realized_pnls if x > 0.0]        losers = [x for x in realized_pnls if x <= 0.0]        return len(winners) / float(max(1, (len(winners) + len(losers))))
```

Example 2 (python):
```python
stat = WinRate()# Register with the portfolio analyzerengine.portfolio.analyzer.register_statistic(stat):::infoSee the `PortfolioAnalyzer` [API Reference](../api_reference/analysis.md#class-portfolioanalyzer) for details on available methods.:::
```

---

## Backtesting

**URL:** https://nautilustrader.io/docs/latest/concepts/backtesting

**Contents:**
- Backtesting
- Choosing an API level​
- Low-level API​
- High-level API​
- Repeated runs​
  - BacktestEngine.reset()​
  - Approaches for multiple backtest runs​
    - 1. Use BacktestNode (recommended for production)​
    - 2. Use BacktestEngine.reset()​
- Data​

Backtesting with NautilusTrader is a methodical simulation process that replicates trading activities using a specific system implementation. This system is composed of various components including the built-in engines, Cache, MessageBus, Portfolio, Actors, Strategies, Execution Algorithms, and other user-defined modules. The entire trading simulation is predicated on a stream of historical data processed by a BacktestEngine. Once this data stream is exhausted, the engine concludes its operation, producing detailed results and performance metrics for in-depth analysis.

It's important to recognize that NautilusTrader offers two distinct API levels for setting up and conducting backtests:

Consider using the low-level API when:

Consider using the high-level API when:

The low-level API centers around a BacktestEngine, where inputs are initialized and added manually via a Python script. An instantiated BacktestEngine can accept the following:

This approach offers detailed control over the backtesting process, allowing you to manually configure each component.

The high-level API centers around a BacktestNode, which orchestrates the management of multiple BacktestEngine instances, each defined by a BacktestRunConfig. Multiple configurations can be bundled into a list and processed by the node in one run.

Each BacktestRunConfig object consists of the following:

When conducting multiple backtest runs, it's important to understand how components reset to avoid unexpected behavior.

The .reset() method returns all stateful fields to their initial value, except for data and instruments which persist.

For BacktestEngine, instruments persist across resets by default (because data persists and instruments must match data). This is configured via CacheConfig.drop_instruments_on_reset=False in the default BacktestEngineConfig.

There are two main approaches for running multiple backtests:

The high-level API is designed for multiple backtest runs with different configurations:

Each run gets a fresh engine with clean state - no reset() needed.

For fine-grained control with the low-level API:

Instruments and data persist across resets by default for BacktestEngine, making parameter optimizations straightforward.

Data provided for backtesting drives the execution flow. Since a variety of data types can be used, it's crucial that your venue configurations align with the data being provided for backtesting. Mismatches between data and configuration can lead to unexpected behavior during execution.

NautilusTrader is primarily designed and optimized for order book data, which provides a complete representation of every price level or order in the market, reflecting the real-time behavior of a trading venue. This ensures the highest level of execution granularity and realism. However, if granular order book data is either not available or necessary, then the platform has the capability of processing market data in the following descending order of detail:

Order Book Data/Deltas (L3 market-by-order):

Order Book Data/Deltas (L2 market-by-price):

Quote Ticks (L1 market-by-price):

For many trading strategies, bar data (e.g., 1-minute) can be sufficient for backtesting and strategy development. This is particularly important because bar data is typically much more accessible and cost-effective compared to tick or order book data.

Given this practical reality, Nautilus is designed to support bar-based backtesting with advanced features that maximize simulation accuracy, even when working with lower granularity data.

For some trading strategies, it can be practical to start development with bar data to validate core trading ideas. If the strategy looks promising, but is more sensitive to precise execution timing (e.g., requires fills at specific prices between OHLC levels, or uses tight take-profit/stop-loss levels), you can then invest in higher granularity data for more accurate validation.

When initializing a venue for backtesting, you must specify its internal order book_type for execution processing from the following options:

The granularity of the data must match the specified order book_type. Nautilus cannot generate higher granularity data (L2 or L3) from lower-level data such as quotes, trades, or bars.

If you specify L2_MBP or L3_MBO as the venue’s book_type, all non-order book data (such as quotes, trades, and bars) will be ignored for execution processing. This may cause orders to appear as though they are never filled. We are actively working on improved validation logic to prevent configuration and data mismatches.

When providing L2 or higher order book data, ensure that the book_type is updated to reflect the data's granularity. Failing to do so will result in data aggregation: L2 data will be reduced to a single order per level, and L1 data will reflect only top-of-book levels.

In the main backtesting loop, new market data is first processed for the execution of existing orders before being processed by the data engine that will then send data to strategies.

Bar data provides a summary of market activity with four key prices for each time period (assuming bars are aggregated by trades):

While this gives us an overview of price movement, we lose some important information that we'd have with more granular data:

This is why Nautilus processes bar data through a system that attempts to maintain the most realistic yet conservative market behavior possible, despite these limitations. At its core, the platform always maintains an order book simulation - even when you provide less granular data such as quotes, trades, or bars (although the simulation will only have a top level book).

When using bars for execution simulation (enabled by default with bar_execution=True in venue configurations), Nautilus strictly expects the timestamp (ts_init) of each bar to represent its closing time. This ensures accurate chronological processing, prevents look-ahead bias, and aligns market updates (Open → High → Low → Close) with the moment the bar is complete.

If your data source provides bars timestamped at the opening time (common in some providers), you must adjust them to the closing time before loading into Nautilus. Failure to do so can lead to incorrect order fills, event sequencing errors, or unrealistic backtest results.

Even when you provide bar data, Nautilus maintains an internal order book for each instrument - just like a real venue would.

During backtest execution, each bar is converted into a sequence of four price points:

The trading volume for that bar is split evenly among these four points (25% each). In marginal cases, if the original bar's volume divided by 4 is less than the instrument's minimum size_increment, we still use the minimum size_increment per price point to ensure valid market activity (e.g., 1 contract for CME group exchanges).

How these price points are sequenced can be controlled via the bar_adaptive_high_low_ordering parameter when configuring a venue.

Nautilus supports two modes of bar processing:

Fixed ordering (bar_adaptive_high_low_ordering=False, default)

Adaptive ordering (bar_adaptive_high_low_ordering=True)

Here's how to configure adaptive bar ordering for a venue, including account setup:

When backtesting with different types of data, Nautilus implements specific handling for slippage and spread simulation:

For L2 (market-by-price) or L3 (market-by-order) data, slippage is simulated with high accuracy by:

For L1 data types (e.g., L1 order book, trades, quotes, bars), slippage is handled through:

Initial fill slippage (prob_slippage):

When backtesting with bar data, be aware that the reduced granularity of price information affects the slippage mechanism. For the most realistic backtesting results, consider using higher granularity data sources such as L2 or L3 order book data when available.

The FillModel helps simulate order queue position and execution in a simple probabilistic way during backtesting. It addresses a fundamental challenge: even with perfect historical market data, we can't fully simulate how orders may have interacted with other market participants in real-time.

The FillModel simulates two key aspects of trading that exist in real markets regardless of data quality:

Queue position for limit orders:

Market impact and competition:

prob_fill_on_limit (default: 1.0)

prob_slippage (default: 0.0)

prob_fill_on_stop (default: 1.0)

The prob_fill_on_stop parameter is deprecated and will be removed in a future version (use prob_slippage instead).

The behavior of the FillModel adapts based on the order book type being used:

L2/L3 order book data

With full order book depth, the FillModel focuses purely on simulating queue position for limit orders through prob_fill_on_limit. The order book itself handles slippage naturally based on available liquidity at each price level.

With only best bid/ask prices available, the FillModel provides additional simulation:

When using less granular data, the same behaviors apply as L1:

The FillModel has certain limitations to keep in mind:

As the FillModel continues to evolve, future versions may introduce more sophisticated simulation of order execution dynamics, including:

When you attach a venue to the engine—either for live trading or a back‑test—you must pick one of three accounting modes by passing the account_type parameter:

Example of adding a CASH account for a backtest venue:

Cash accounts settle trades in full; there is no leverage and therefore no concept of margin.

A margin account facilitates trading of instruments requiring margin, such as futures or leveraged products. It tracks account balances, calculates required margins, and manages leverage to ensure sufficient collateral for positions and orders.

Reduce-only orders do not contribute to balance_locked in cash accounts, nor do they add to initial margin in margin accounts—as they can only reduce existing exposure.

Betting accounts are specialised for venues where you stake an amount to win or lose a fixed payout (some prediction markets, sports books, etc.). The engine locks only the stake required by the venue; leverage and margin are not applicable.

NautilusTrader provides flexible margin calculation models to accommodate different venue types and trading scenarios.

Different venues and brokers have varying approaches to calculating margin requirements:

Uses fixed percentages without leverage division, matching traditional broker behavior.

Divides margin requirements by leverage.

By default, MarginAccount uses LeveragedMarginModel.

EUR/USD Trading Scenario:

Account balance impact:

The default LeveragedMarginModel works out of the box:

For traditional broker behavior:

You can create custom margin models by inheriting from MarginModel. Custom models receive configuration through the MarginModelConfig:

When using the high-level backtest API, you can specify margin models in your venue configuration using MarginModelConfig:

Standard model (traditional brokers):

Leveraged model (default):

Custom model with configuration:

The margin model will be automatically applied to the simulated exchange during backtest execution.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.backtest.node import BacktestNodefrom nautilus_trader.config import BacktestRunConfig# Define multiple run configurationsconfigs = [    BacktestRunConfig(...),  # Run 1    BacktestRunConfig(...),  # Run 2    BacktestRunConfig(...),  # Run 3]# Execute all runsnode = BacktestNode(configs=configs)results = node.run()
```

Example 2 (python):
```python
from nautilus_trader.backtest.engine import BacktestEngineengine = BacktestEngine()# Setup onceengine.add_venue(...)engine.add_instrument(ETHUSDT)engine.add_data(data)# Run 1engine.add_strategy(strategy1)engine.run()# Reset and run 2 - instruments and data persistengine.reset()engine.add_strategy(strategy2)engine.run()# Reset and run 3engine.reset()engine.add_strategy(strategy3)engine.run()
```

Example 3 (python):
```python
from nautilus_trader.backtest.engine import BacktestEnginefrom nautilus_trader.model.enums import OmsType, AccountTypefrom nautilus_trader.model import Money, Currency# Initialize the backtest engineengine = BacktestEngine()# Add a venue with adaptive bar ordering and required account settingsengine.add_venue(    venue=venue,  # Your Venue identifier, e.g., Venue("BINANCE")    oms_type=OmsType.NETTING,    account_type=AccountType.CASH,    starting_balances=[Money(10_000, Currency.from_str("USDT"))],    bar_adaptive_high_low_ordering=True,  # Enable adaptive ordering of High/Low bar prices)
```

Example 4 (python):
```python
from nautilus_trader.backtest.models import FillModelfrom nautilus_trader.backtest.config import BacktestEngineConfigfrom nautilus_trader.backtest.engine import BacktestEngine# Create a custom fill model with your desired probabilitiesfill_model = FillModel(    prob_fill_on_limit=0.2,    # Chance a limit order fills when price matches (applied to bars/trades/quotes + L1/L2/L3 order book)    prob_fill_on_stop=0.95,    # [DEPRECATED] Will be removed in a future version, use `prob_slippage` instead    prob_slippage=0.5,         # Chance of 1-tick slippage (applied to bars/trades/quotes + L1 order book only)    random_seed=None,          # Optional: Set for reproducible results)# Add the fill model to your engine configurationengine = BacktestEngine(    config=BacktestEngineConfig(        trader_id="TESTER-001",        fill_model=fill_model,  # Inject your custom fill model here    ))
```

---

## Actors

**URL:** https://nautilustrader.io/docs/latest/concepts/actors

**Contents:**
- Actors
- Basic example​
- Data handling and callbacks​
  - Historical vs real-time data​
  - Callback handlers​
  - Example​
- Order fill subscriptions​
  - Example​

We are currently working on this concept guide.

The Actor serves as the foundational component for interacting with the trading system. It provides core functionality for receiving market data, handling events, and managing state within the trading environment. The Strategy class inherits from Actor and extends its capabilities with order management methods.

Just like strategies, actors support configuration through a very similar pattern.

When working with data in Nautilus, it's important to understand the relationship between data requests/subscriptions and their corresponding callback handlers. The system uses different handlers depending on whether the data is historical or real-time.

The system distinguishes between two types of data flow:

Historical data (from requests):

Real-time data (from subscriptions):

Here's how different data operations map to their handlers:

Here's an example demonstrating both historical and real-time data handling:

This separation between historical and real-time data handlers allows for different processing logic based on the data context. For example, you might want to:

When debugging data flow issues, check that you're looking at the correct handler for your data source. If you're not seeing data in on_bar() but see log messages about receiving bars, check on_historical_data() as the data might be coming from a request rather than a subscription.

Actors can subscribe to order fill events for specific instruments using subscribe_order_fills(). This is useful for monitoring trading activity, implementing custom fill analysis, or tracking execution quality.

When subscribed, all order fills for the specified instrument are forwarded to the on_order_filled() handler, regardless of which strategy or component generated the original order.

Order fill subscriptions are message bus-only subscriptions and do not involve the data engine. The on_order_filled() handler will only receive events while the actor is in a running state.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.config import ActorConfigfrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model import Bar, BarTypefrom nautilus_trader.common.actor import Actorclass MyActorConfig(ActorConfig):    instrument_id: InstrumentId   # example value: "ETHUSDT-PERP.BINANCE"    bar_type: BarType             # example value: "ETHUSDT-PERP.BINANCE-15-MINUTE[LAST]-INTERNAL"    lookback_period: int = 10class MyActor(Actor):    def __init__(self, config: MyActorConfig) -> None:        super().__init__(config)        # Custom state variables        self.count_of_processed_bars: int = 0    def on_start(self) -> None:        # Subscribe to all incoming bars        self.subscribe_bars(self.config.bar_type)   # You can access configuration directly via `self.config`    def on_bar(self, bar: Bar):        self.count_of_processed_bars += 1
```

Example 2 (python):
```python
from nautilus_trader.common.actor import Actorfrom nautilus_trader.config import ActorConfigfrom nautilus_trader.core.data import Datafrom nautilus_trader.model import Bar, BarTypefrom nautilus_trader.model import ClientId, InstrumentIdclass MyActorConfig(ActorConfig):    instrument_id: InstrumentId  # example value: "AAPL.XNAS"    bar_type: BarType            # example value: "AAPL.XNAS-1-MINUTE-LAST-EXTERNAL"class MyActor(Actor):    def __init__(self, config: MyActorConfig) -> None:        super().__init__(config)        self.bar_type = config.bar_type    def on_start(self) -> None:        # Request historical data - will be processed by on_historical_data() handler        self.request_bars(            bar_type=self.bar_type,            # Many optional parameters            start=None,                # datetime, optional            end=None,                  # datetime, optional            callback=None,             # called with the request ID when completed            update_catalog_mode=None,  # UpdateCatalogMode | None, default None            params=None,               # dict[str, Any], optional        )        # Subscribe to real-time data - will be processed by on_bar() handler        self.subscribe_bars(            bar_type=self.bar_type,            # Many optional parameters            client_id=None,  # ClientId, optional            params=None,     # dict[str, Any], optional        )    def on_historical_data(self, data: Data) -> None:        # Handle historical data (from requests)        if isinstance(data, Bar):            self.log.info(f"Received historical bar: {data}")    def on_bar(self, bar: Bar) -> None:        # Handle real-time bar updates (from subscriptions)        self.log.info(f"Received real-time bar: {bar}")
```

Example 3 (python):
```python
from nautilus_trader.common.actor import Actorfrom nautilus_trader.config import ActorConfigfrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model.events import OrderFilledclass MyActorConfig(ActorConfig):    instrument_id: InstrumentId  # example value: "ETHUSDT-PERP.BINANCE"class FillMonitorActor(Actor):    def __init__(self, config: MyActorConfig) -> None:        super().__init__(config)        self.fill_count = 0        self.total_volume = 0.0    def on_start(self) -> None:        # Subscribe to all fills for the instrument        self.subscribe_order_fills(self.config.instrument_id)    def on_order_filled(self, event: OrderFilled) -> None:        # Handle order fill events        self.fill_count += 1        self.total_volume += float(event.last_qty)        self.log.info(            f"Fill received: {event.order_side} {event.last_qty} @ {event.last_px}, "            f"Total fills: {self.fill_count}, Volume: {self.total_volume}"        )    def on_stop(self) -> None:        # Unsubscribe from fills        self.unsubscribe_order_fills(self.config.instrument_id)
```

---

## Architecture

**URL:** https://nautilustrader.io/docs/latest/concepts/architecture

**Contents:**
- Architecture
- Design philosophy​
  - Quality attributes​
  - Assurance-driven engineering​
  - Crash-only design​
  - Data integrity and fail-fast policy​
    - Fail-fast principles​
    - When fail-fast applies​
    - Example scenarios​
- System architecture​

Welcome to the architectural overview of NautilusTrader.

This guide dives deep into the foundational principles, structures, and designs that underpin the platform. Whether you're a developer, system architect, or just curious about the inner workings of NautilusTrader, this section covers:

Throughout the documentation, the term "Nautilus system boundary" refers to operations within the runtime of a single Nautilus node (also known as a "trader instance").

The major architectural techniques and design patterns employed by NautilusTrader are:

These techniques have been utilized to assist in achieving certain architectural quality attributes.

Architectural decisions are often a trade-off between competing priorities. The below is a list of some of the most important quality attributes which are considered when making design and architectural decisions, roughly in order of 'weighting'.

NautilusTrader is incrementally adopting a high-assurance mindset: critical code paths should carry executable invariants that verify behaviour matches the business requirements. Practically this means we:

This approach preserves the platform’s delivery cadence while giving mission critical flows the additional scrutiny they need.

Further reading: High Assurance Rust.

NautilusTrader embraces crash-only design, a philosophy where "the only way to stop the system is to crash it", and "the only way to bring it up is to recover from a crash". This approach simplifies state management and improves reliability by eliminating the complexity of graceful shutdown code paths that are rarely tested.

This design complements the fail-fast policy, where unrecoverable errors (data corruption, invariant violations) result in immediate process termination rather than attempting to continue in a compromised state.

NautilusTrader prioritizes data integrity over availability for trading operations. The system employs a strict fail-fast policy for arithmetic operations and data handling to prevent silent data corruption that could lead to incorrect trading decisions.

The system will fail fast (panic or return an error) when encountering:

In trading systems, corrupt data is worse than no data. A single incorrect price, timestamp, or quantity can cascade through the system, resulting in:

By crashing immediately on invalid data, NautilusTrader ensures:

Results or Options are used for:

This policy is implemented throughout the core types (UnixNanos, Price, Quantity, etc.) and ensures that NautilusTrader maintains the highest standards of data correctness for production trading.

In production deployments, the system is typically configured with panic = abort in release builds, ensuring that any panic results in a clean process termination that can be handled by process supervisors or orchestration systems. This aligns with the crash-only design principle, where unrecoverable errors lead to immediate restart rather than attempting to continue in a potentially corrupted state.

The NautilusTrader codebase is actually both a framework for composing trading systems, and a set of default system implementations which can operate in various environment contexts.

The platform is built around several key components that work together to provide a comprehensive trading system:

The central orchestration component responsible for:

The backbone of inter-component communication, implementing:

High-performance in-memory storage system that:

Processes and routes market data throughout the system:

Manages order lifecycle and execution:

Provides comprehensive risk management:

An environment context in NautilusTrader defines the type of data and trading venue you are working with. Understanding these contexts is crucial for effective backtesting, development, and live trading.

Here are the available environments you can work with:

The platform has been designed to share as much common code between backtest, sandbox and live trading systems as possible. This is formalized in the system subpackage, where you will find the NautilusKernel class, providing a common core system 'kernel'.

The ports and adapters architectural style enables modular components to be integrated into the core system, providing various hooks for user-defined or custom component implementations.

Understanding how data and execution flow through the system is crucial for effective use of the platform:

All components follow a finite state machine pattern with well-defined states:

To facilitate modularity and loose coupling, an extremely efficient MessageBus passes messages (data, commands and events) between components.

From a high level architectural view, it's important to understand that the platform has been designed to run efficiently on a single thread, for both backtesting and live trading. Much research and testing resulted in arriving at this design, as it was found the overhead of context switching between threads didn't actually result in improved performance.

When considering the logic of how your algo trading will work within the system boundary, you can expect each component to consume messages in a deterministic synchronous way (similar to the actor model).

Of interest is the LMAX exchange architecture, which achieves award winning performance running on a single thread. You can read about their disruptor pattern based architecture in this interesting article by Martin Fowler.

The codebase is organized with a layering of abstraction levels, and generally grouped into logical subpackages of cohesive concepts. You can navigate to the documentation for each of these subpackages from the left nav menu.

The foundation of the codebase is the crates directory, containing a collection of Rust crates including a C foreign function interface (FFI) generated by cbindgen.

The bulk of the production code resides in the nautilus_trader directory, which contains a collection of Python/Cython subpackages and modules.

Python bindings for the Rust core are provided by statically linking the Rust libraries to the C extension modules generated by Cython at compile time (effectively extending the CPython API).

Both Rust and Cython are build dependencies. The binary wheels produced from a build do not require Rust or Cython to be installed at runtime.

The design of the platform prioritizes software correctness and safety at the highest level.

The Rust codebase in nautilus_core is always type safe and memory safe as guaranteed by the rustc compiler, and so is correct by construction (unless explicitly marked unsafe, see the Rust section of the Developer Guide).

Cython provides type safety at the C level at both compile time, and runtime:

If you pass an argument with an invalid type to a Cython implemented module with typed parameters, then you will receive a TypeError at runtime.

If a function or method's parameter is not explicitly typed to accept None, passing None as an argument will result in a ValueError at runtime.

The above exceptions are not explicitly documented to prevent excessive bloating of the docstrings.

Every attempt has been made to accurately document the possible exceptions which can be raised from NautilusTrader code, and the conditions which will trigger them.

There may be other undocumented exceptions which can be raised by Python's standard library, or from third party library dependencies.

For optimal performance and to prevent potential issues related to Python's memory model and equality, it is highly recommended to run each trader instance in a separate process.

**Examples:**

Example 1 (rust):
```rust
// CORRECT: Panics on overflow - prevents data corruptionlet total_ns = timestamp1 + timestamp2; // Panics if result > u64::MAX// CORRECT: Rejects NaN during deserializationlet price = serde_json::from_str("NaN"); // Error: "must be finite"// CORRECT: Explicit overflow handling when neededlet total_ns = timestamp1.checked_add(timestamp2)?; // Returns Option<UnixNanos>
```

Example 2 (text):
```text
┌─────────────────────────┐│                         ││                         ││     nautilus_trader     ││                         ││     Python / Cython     ││                         ││                         │└────────────┬────────────┘ C API       │             │             │             │ C API       ▼┌─────────────────────────┐│                         ││                         ││      nautilus_core      ││                         ││          Rust           ││                         ││                         │└─────────────────────────┘
```

---
