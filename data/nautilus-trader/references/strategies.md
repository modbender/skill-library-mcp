# Nautilus_Trader - Strategies

**Pages:** 7

---

## Trading

**URL:** https://nautilustrader.io/docs/latest/api_reference/trading

**Contents:**
- Trading
  - class Controller​
    - create_actor(actor: Actor, start: bool = True) → None​
    - create_actor_from_config(actor_config: ImportableActorConfig, start: bool = True) → None​
    - create_strategy(strategy: Strategy, start: bool = True) → None​
    - create_strategy_from_config(strategy_config: ImportableStrategyConfig, start: bool = True) → None​
    - execute(command: Command) → None​
    - register_base(self, PortfolioFacade portfolio, MessageBus msgbus, CacheFacade cache, Clock clock) → void​
    - WARNING​
    - remove_actor(actor: Actor) → None​

The trading subpackage groups all trading domain specific components and tooling.

This is a top-level package where the majority of users will interface with the framework. Custom trading strategies can be implemented by inheriting from the Strategy base class.

The base class for all trader controllers.

Add the given actor to the controlled trader.

Create the actor corresponding to actor_config.

Add the given strategy to the controlled trader.

Create the strategy corresponding to strategy_config.

Register with a trader.

System method (not intended to be called by user code).

Remove the given actor.

Will stop the actor first if state is RUNNING.

Remove the actor corresponding to actor_id.

Will stop the actor first if state is RUNNING.

Remove the given strategy.

Will stop the strategy first if state is RUNNING.

Remove the strategy corresponding to strategy_id.

Will stop the strategy first if state is RUNNING.

Start the given actor.

Will log a warning if the actor is already RUNNING.

Start the actor corresponding to actor_id.

Will log a warning if the actor is already RUNNING.

Start the given strategy.

Will log a warning if the strategy is already RUNNING.

Start the strategy corresponding to strategy_id.

Will log a warning if the strategy is already RUNNING.

Stop the given actor.

Will log a warning if the actor is not RUNNING.

Stop the actor corresponding to actor_id.

Will log a warning if the actor is not RUNNING.

Stop the given strategy.

Will log a warning if the strategy is not RUNNING.

Stop the strategy corresponding to strategy_id.

Will log a warning if the strategy is not RUNNING.

Strategy(config: StrategyConfig | None = None)

The base class for all trading strategies.

This class allows traders to implement their own customized trading strategies. A trading strategy can configure its own order management system type, which determines how positions are handled by the ExecutionEngine.

Strategy OMS (Order Management System) types: : - UNSPECIFIED: No specific type has been configured, will therefore default to the native OMS type for each venue.

Cancel all orders for this strategy for the given instrument ID.

A CancelAllOrders command will be created and then sent to both the OrderEmulator and the ExecutionEngine.

Cancel the managed GTD expiry for the given order.

If there is no current GTD expiry timer, then an error will be logged.

Cancel the given order with optional routing instructions.

A CancelOrder command will be created and then sent to either the OrderEmulator or the ExecutionEngine (depending on whether the order is emulated).

Batch cancel the given list of orders with optional routing instructions.

For each order in the list, a CancelOrder command will be created and added to a BatchCancelOrders command. This command is then sent to the ExecutionEngine.

Logs an error if the orders list contains local/emulated orders.

Change the strategies identifier to the given strategy_id.

Change the order identifier tag to the given order_id_tag.

Close all positions for the given instrument ID for this strategy.

Close the given position.

A closing MarketOrder for the position will be created, and then sent to the ExecutionEngine via a SubmitOrder command.

The external order claims instrument IDs for the strategy.

Handle the given event.

If state is RUNNING then passes to on_event.

System method (not intended to be called by user code).

If contingent orders should be managed automatically by the strategy.

If all order GTD time in force expirations should be managed automatically by the strategy.

Modify the given order with optional parameters and routing instructions.

An ModifyOrder command will be created and then sent to either the OrderEmulator or the RiskEngine (depending on whether the order is emulated).

At least one value must differ from the original order for the command to be valid.

Will use an Order Cancel/Replace Request (a.k.a Order Modification) for FIX protocols, otherwise if order update is not available for the API, then will cancel and replace with a new order using the original ClientOrderId.

If the order is already closed or at PENDING_CANCEL status then the command will not be generated, and a warning will be logged.

The order management system for the strategy.

Actions to be performed when running and receives an order accepted event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order cancel rejected event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order canceled event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order denied event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order emulated event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order expired event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order filled event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order initialized event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order modify rejected event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order pending cancel event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order pending update event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order rejected event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order released event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order submitted event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order triggered event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order updated event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position changed event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position closed event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position opened event.

System method (not intended to be called by user code).

The order factory for the strategy.

The order ID tag for the strategy.

Query the account with optional routing instructions.

A QueryAccount command will be created and then sent to the ExecutionEngine.

Query the given order with optional routing instructions.

A QueryOrder command will be created and then sent to the ExecutionEngine.

Logs an error if no VenueOrderId has been assigned to the order.

Register the strategy with a trader.

System method (not intended to be called by user code).

Submit the given order with optional position ID, execution algorithm and routing instructions.

A SubmitOrder command will be created and sent to either an ExecAlgorithm, the OrderEmulator or the RiskEngine (depending whether the order is emulated and/or has an exec_algorithm_id specified).

If the client order ID is duplicate, then the order will be denied.

If a position_id is passed and a position does not yet exist, then any position opened by the order will have this position ID assigned. This may not be what you intended.

Submit the given order list with optional position ID, execution algorithm and routing instructions.

A SubmitOrderList command will be created and sent to either the OrderEmulator, or the RiskEngine (depending whether an order is emulated).

If the order list ID is duplicate, or any client order ID is duplicate, then all orders will be denied.

If a position_id is passed and a position does not yet exist, then any position opened by an order will have this position ID assigned. This may not be what you intended.

Returns an importable configuration for this strategy.

If hyphens should be used in generated client order ID values.

If UUID4’s should be used for client order ID values.

Provides a trader for managing a fleet of actors, execution algorithms and trading strategies.

Return the actor IDs loaded in the trader.

Return the traders actor states.

Return the actors loaded in the trader.

Add the given custom component to the trader.

Add the given actors to the trader.

Add the given execution algorithm to the trader.

Add the given execution algorithms to the trader.

Add the given trading strategies to the trader.

Add the given trading strategy to the trader.

Check for residual open state such as open orders or open positions.

Dispose and clear all actors held by the trader.

Dispose and clear all execution algorithms held by the trader.

Dispose and clear all strategies held by the trader.

Return the execution algorithm IDs loaded in the trader.

Return the traders execution algorithm states.

Return the execution algorithms loaded in the trader.

Generate an account report.

Generate a fills report.

Generate an order fills report.

Generate an orders report.

Generate a positions report.

Return the traders instance ID.

Load all actor and strategy states from the cache.

Remove the actor with the given actor_id.

Will stop the actor first if state is RUNNING.

Remove the strategy with the given strategy_id.

Will stop the strategy first if state is RUNNING.

Save all actor and strategy states to the cache.

Start the actor with the given actor_id.

Start the strategy with the given strategy_id.

Stop the actor with the given actor_id.

Stop the strategy with the given strategy_id.

Return the strategies loaded in the trader.

Return the strategy IDs loaded in the trader.

Return the traders strategy states.

Subscribe to the given message topic with the given callback handler.

Unsubscribe the given handler from the given message topic.

The base class for all trader controllers.

Register with a trader.

System method (not intended to be called by user code).

Add the given actor to the controlled trader.

Add the given strategy to the controlled trader.

Start the given actor.

Will log a warning if the actor is already RUNNING.

Start the given strategy.

Will log a warning if the strategy is already RUNNING.

Stop the given actor.

Will log a warning if the actor is not RUNNING.

Stop the given strategy.

Will log a warning if the strategy is not RUNNING.

Remove the given actor.

Will stop the actor first if state is RUNNING.

Remove the given strategy.

Will stop the strategy first if state is RUNNING.

Create the actor corresponding to actor_config.

Create the strategy corresponding to strategy_config.

Start the actor corresponding to actor_id.

Will log a warning if the actor is already RUNNING.

Start the strategy corresponding to strategy_id.

Will log a warning if the strategy is already RUNNING.

Stop the actor corresponding to actor_id.

Will log a warning if the actor is not RUNNING.

Stop the strategy corresponding to strategy_id.

Will log a warning if the strategy is not RUNNING.

Remove the actor corresponding to actor_id.

Will stop the actor first if state is RUNNING.

Remove the strategy corresponding to strategy_id.

Will stop the strategy first if state is RUNNING.

Return the active task identifiers.

Add the created synthetic instrument to the cache.

The read-only cache for the actor.

Cancel all queued and active tasks.

Cancel the task with the given task_id (if queued or active).

If the task is not found then a warning is logged.

The actors configuration.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Deregister the given event type from warning log levels.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

The read-only greeks calculator for the actor.

Handle the given bar data.

If state is RUNNING then passes to on_bar.

System method (not intended to be called by user code).

Handle the given historical bar data by handling each bar individually.

System method (not intended to be called by user code).

Handle the given data.

If state is RUNNING then passes to on_data.

System method (not intended to be called by user code).

Handle the given event.

If state is RUNNING then passes to on_event.

System method (not intended to be called by user code).

Handle the given funding rate update.

If state is RUNNING then passes to on_funding_rate.

System method (not intended to be called by user code).

Handle the given historical data.

System method (not intended to be called by user code).

Handle the given index price update.

If state is RUNNING then passes to on_index_price.

System method (not intended to be called by user code).

Handle the given instrument.

Passes to on_instrument if state is RUNNING.

System method (not intended to be called by user code).

Handle the given instrument close update.

If state is RUNNING then passes to on_instrument_close.

System method (not intended to be called by user code).

Handle the given instrument status update.

If state is RUNNING then passes to on_instrument_status.

System method (not intended to be called by user code).

Handle the given instruments data by handling each instrument individually.

System method (not intended to be called by user code).

Handle the given mark price update.

If state is RUNNING then passes to on_mark_price.

System method (not intended to be called by user code).

Handle the given order book.

Passes to on_order_book if state is RUNNING.

System method (not intended to be called by user code).

Handle the given order book deltas.

Passes to on_order_book_deltas if state is RUNNING. The deltas will be nautilus_pyo3.OrderBookDeltas if the pyo3_conversion flag was set for the subscription.

System method (not intended to be called by user code).

Handle the given order book depth

Passes to on_order_book_depth if state is RUNNING.

System method (not intended to be called by user code).

Handle the given quote tick.

If state is RUNNING then passes to on_quote_tick.

System method (not intended to be called by user code).

Handle the given historical quote tick data by handling each tick individually.

System method (not intended to be called by user code).

Handle the given signal.

If state is RUNNING then passes to on_signal.

System method (not intended to be called by user code).

Handle the given trade tick.

If state is RUNNING then passes to on_trade_tick.

System method (not intended to be called by user code).

Handle the given historical trade tick data by handling each tick individually.

System method (not intended to be called by user code).

Return a value indicating whether there are any active tasks.

Return a value indicating whether there are any queued OR active tasks.

Return whether the actor is pending processing for any requests.

Return a value indicating whether there are any queued tasks.

Return a value indicating whether all indicators are initialized.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the request for the given identifier is pending processing.

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Load the actor/strategy state from the give state dictionary.

Calls on_load and passes the state.

Exceptions raised will be caught, logged, and reraised.

The message bus for the actor (if registered).

Actions to be performed when running and receives a bar.

System method (not intended to be called by user code).

Actions to be performed when running and receives data.

System method (not intended to be called by user code).

Actions to be performed on degrade.

System method (not intended to be called by user code).

Should be overridden in the actor implementation.

Actions to be performed on dispose.

Cleanup/release any resources used here.

System method (not intended to be called by user code).

Actions to be performed running and receives an event.

System method (not intended to be called by user code).

Actions to be performed on fault.

Cleanup any resources used by the actor here.

System method (not intended to be called by user code).

Should be overridden in the actor implementation.

Actions to be performed when running and receives a funding rate update.

System method (not intended to be called by user code).

Actions to be performed when running and receives historical data.

System method (not intended to be called by user code).

Actions to be performed when running and receives an index price update.

System method (not intended to be called by user code).

Actions to be performed when running and receives an instrument.

System method (not intended to be called by user code).

Actions to be performed when running and receives an instrument close update.

System method (not intended to be called by user code).

Actions to be performed when running and receives an instrument status update.

System method (not intended to be called by user code).

Actions to be performed when the actor state is loaded.

Saved state values will be contained in the give state dictionary.

System method (not intended to be called by user code).

Actions to be performed when running and receives a mark price update.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order book.

System method (not intended to be called by user code).

Actions to be performed when running and receives order book deltas.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order book depth.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order filled event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a quote tick.

System method (not intended to be called by user code).

Actions to be performed on reset.

System method (not intended to be called by user code).

Should be overridden in a user implementation.

Actions to be performed on resume.

System method (not intended to be called by user code).

Actions to be performed when the actor state is saved.

Create and return a state dictionary of values to be saved.

System method (not intended to be called by user code).

Actions to be performed when running and receives signal data.

System method (not intended to be called by user code).

Actions to be performed on start.

The intent is that this method is called once per trading ‘run’, when initially starting.

It is recommended to subscribe/request for data here.

System method (not intended to be called by user code).

Should be overridden in a user implementation.

Actions to be performed on stop.

The intent is that this method is called to pause, or when done for day.

System method (not intended to be called by user code).

Should be overridden in a user implementation.

Actions to be performed when running and receives a trade tick.

System method (not intended to be called by user code).

Return the request IDs which are currently pending processing.

The read-only portfolio for the actor.

Publish the given data to the message bus.

Publish the given value as a signal to the message bus.

Queues the callable func to be executed as fn(*args, **kwargs) sequentially.

Return the queued task identifiers.

Register the given Executor for the actor.

Register the given indicator with the actor/strategy to receive bar data for the given bar type.

Register the given indicator with the actor/strategy to receive quote tick data for the given instrument ID.

Register the given indicator with the actor/strategy to receive trade tick data for the given instrument ID.

Register the given event type for warning log levels.

Return the registered indicators for the strategy.

Request historical aggregated Bar data for multiple bar types. The first bar is used to determine which market data type will be queried. This can either be quotes, trades or bars. If bars are queried, the first bar type needs to have a composite bar that is external (i.e. not internal/aggregated). This external bar type will be queried.

If end is None then will request up to the most recent data.

Once the response is received, the bar data is forwarded from the message bus to the on_historical_data handler. Any tick data used for aggregation is also forwarded to the on_historical_data handler.

If the request fails, then an error is logged.

Request historical Bar data.

If end is None then will request up to the most recent data.

Once the response is received, the bar data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request custom data for the given data type from the given data client.

Once the response is received, the data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request Instrument data for the given instrument ID.

If end is None then will request up to the most recent data.

Once the response is received, the instrument data is forwarded from the message bus to the on_instrument handler.

If the request fails, then an error is logged.

Request all Instrument data for the given venue.

If end is None then will request up to the most recent data.

Once the response is received, the instrument data is forwarded from the message bus to the on_instrument handler.

If the request fails, then an error is logged.

Request historical OrderBookDepth10 snapshots.

Once the response is received, the order book depth data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request an order book snapshot.

Once the response is received, the order book data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request historical QuoteTick data.

If end is None then will request up to the most recent data.

Once the response is received, the quote tick data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request historical TradeTick data.

If end is None then will request up to the most recent data.

Once the response is received, the trade tick data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Schedules the callable func to be executed as fn(*args, **kwargs).

Return the actor/strategy state dictionary to be saved.

Exceptions raised will be caught, logged, and reraised.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Subscribe to streaming Bar data for the given bar type.

Once subscribed, any matching bar data published on the message bus is forwarded to the on_bar handler.

Subscribe to data of the given data type.

Once subscribed, any matching data published on the message bus is forwarded to the on_data handler.

Subscribe to streaming FundingRateUpdate data for the given instrument ID.

Once subscribed, any matching funding rate updates published on the message bus are forwarded to the on_funding_rate handler.

Subscribe to streaming IndexPriceUpdate data for the given instrument ID.

Once subscribed, any matching index price updates published on the message bus are forwarded to the on_index_price handler.

Subscribe to update Instrument data for the given instrument ID.

Once subscribed, any matching instrument data published on the message bus is forwarded to the on_instrument handler.

Subscribe to close updates for the given instrument ID.

Once subscribed, any matching instrument close data published on the message bus is forwarded to the on_instrument_close handler.

Subscribe to status updates for the given instrument ID.

Once subscribed, any matching instrument status data published on the message bus is forwarded to the on_instrument_status handler.

Subscribe to update Instrument data for the given venue.

Once subscribed, any matching instrument data published on the message bus is forwarded the on_instrument handler.

Subscribe to streaming MarkPriceUpdate data for the given instrument ID.

Once subscribed, any matching mark price updates published on the message bus are forwarded to the on_mark_price handler.

Subscribe to an OrderBook at a specified interval for the given instrument ID.

Once subscribed, any matching order book updates published on the message bus are forwarded to the on_order_book handler.

The DataEngine will only maintain one order book for each instrument. Because of this - the level, depth and params for the stream will be set as per the last subscription request (this will also affect all subscribers).

Consider subscribing to order book deltas if you need intervals less than 100 milliseconds.

Subscribe to the order book data stream, being a snapshot then deltas for the given instrument ID.

Once subscribed, any matching order book data published on the message bus is forwarded to the on_order_book_deltas handler.

Subscribe to the order book depth stream for the given instrument ID.

Once subscribed, any matching order book data published on the message bus is forwarded to the on_order_book_depth handler.

Subscribe to all order fills for the given instrument ID.

Once subscribed, any matching order fills published on the message bus are forwarded to the on_order_filled handler.

Subscribe to streaming QuoteTick data for the given instrument ID.

Once subscribed, any matching quote tick data published on the message bus is forwarded to the on_quote_tick handler.

Subscribe to a specific signal by name, or to all signals if no name is provided.

Once subscribed, any matching signal data published on the message bus is forwarded to the on_signal handler.

Subscribe to streaming TradeTick data for the given instrument ID.

Once subscribed, any matching trade tick data published on the message bus is forwarded to the on_trade_tick handler.

Returns an importable configuration for this actor.

The trader ID associated with the component.

Unsubscribe from streaming Bar data for the given bar type.

Unsubscribe from data of the given data type.

Unsubscribe from streaming FundingRateUpdate data for the given instrument ID.

Unsubscribe from streaming IndexPriceUpdate data for the given instrument ID.

Unsubscribe from update Instrument data for the given instrument ID.

Unsubscribe from close updates for the given instrument ID.

Unsubscribe from status updates for the given instrument ID.

Unsubscribe from update Instrument data for the given venue.

Unsubscribe from streaming MarkPriceUpdate data for the given instrument ID.

Unsubscribe from an OrderBook at a specified interval for the given instrument ID.

The interval must match the previously subscribed interval.

Unsubscribe the order book deltas stream for the given instrument ID.

Unsubscribe the order book depth stream for the given instrument ID.

Unsubscribe from all order fills for the given instrument ID.

Unsubscribe from streaming QuoteTick data for the given instrument ID.

Unsubscribe from streaming TradeTick data for the given instrument ID.

Update the synthetic instrument in the cache.

Represents an economic news event.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the instance was created.

Return the fully qualified name for the Data class.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Provides methods to help filter trading strategy rules based on economic news events.

Return the start of the raw data.

Return the end of the raw data.

Return the currencies the data is filtered on.

Return the news impacts the data is filtered on.

Return the next news event matching the filter conditions. Will return None if no news events match the filter conditions.

Return the previous news event matching the initial filter conditions. Will return None if no news events match the filter conditions.

This module defines a trading strategy class which allows users to implement their own customized trading strategies

A user can inherit from Strategy and optionally override any of the “on” named event methods. The class is not entirely initialized in a stand-alone way, the intended usage is to pass strategies to a Trader so that they can be fully “wired” into the platform. Exceptions will be raised if a Strategy attempts to operate without a managing Trader instance.

Strategy(config: StrategyConfig | None = None)

The base class for all trading strategies.

This class allows traders to implement their own customized trading strategies. A trading strategy can configure its own order management system type, which determines how positions are handled by the ExecutionEngine.

Strategy OMS (Order Management System) types: : - UNSPECIFIED: No specific type has been configured, will therefore default to the native OMS type for each venue.

Return the active task identifiers.

Add the created synthetic instrument to the cache.

The read-only cache for the actor.

Cancel all orders for this strategy for the given instrument ID.

A CancelAllOrders command will be created and then sent to both the OrderEmulator and the ExecutionEngine.

Cancel all queued and active tasks.

Cancel the managed GTD expiry for the given order.

If there is no current GTD expiry timer, then an error will be logged.

Cancel the given order with optional routing instructions.

A CancelOrder command will be created and then sent to either the OrderEmulator or the ExecutionEngine (depending on whether the order is emulated).

Batch cancel the given list of orders with optional routing instructions.

For each order in the list, a CancelOrder command will be created and added to a BatchCancelOrders command. This command is then sent to the ExecutionEngine.

Logs an error if the orders list contains local/emulated orders.

Cancel the task with the given task_id (if queued or active).

If the task is not found then a warning is logged.

Change the strategies identifier to the given strategy_id.

Change the order identifier tag to the given order_id_tag.

Close all positions for the given instrument ID for this strategy.

Close the given position.

A closing MarketOrder for the position will be created, and then sent to the ExecutionEngine via a SubmitOrder command.

The actors configuration.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Deregister the given event type from warning log levels.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

The external order claims instrument IDs for the strategy.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

The read-only greeks calculator for the actor.

Handle the given bar data.

If state is RUNNING then passes to on_bar.

System method (not intended to be called by user code).

Handle the given historical bar data by handling each bar individually.

System method (not intended to be called by user code).

Handle the given data.

If state is RUNNING then passes to on_data.

System method (not intended to be called by user code).

Handle the given event.

If state is RUNNING then passes to on_event.

System method (not intended to be called by user code).

Handle the given funding rate update.

If state is RUNNING then passes to on_funding_rate.

System method (not intended to be called by user code).

Handle the given historical data.

System method (not intended to be called by user code).

Handle the given index price update.

If state is RUNNING then passes to on_index_price.

System method (not intended to be called by user code).

Handle the given instrument.

Passes to on_instrument if state is RUNNING.

System method (not intended to be called by user code).

Handle the given instrument close update.

If state is RUNNING then passes to on_instrument_close.

System method (not intended to be called by user code).

Handle the given instrument status update.

If state is RUNNING then passes to on_instrument_status.

System method (not intended to be called by user code).

Handle the given instruments data by handling each instrument individually.

System method (not intended to be called by user code).

Handle the given mark price update.

If state is RUNNING then passes to on_mark_price.

System method (not intended to be called by user code).

Handle the given order book.

Passes to on_order_book if state is RUNNING.

System method (not intended to be called by user code).

Handle the given order book deltas.

Passes to on_order_book_deltas if state is RUNNING. The deltas will be nautilus_pyo3.OrderBookDeltas if the pyo3_conversion flag was set for the subscription.

System method (not intended to be called by user code).

Handle the given order book depth

Passes to on_order_book_depth if state is RUNNING.

System method (not intended to be called by user code).

Handle the given quote tick.

If state is RUNNING then passes to on_quote_tick.

System method (not intended to be called by user code).

Handle the given historical quote tick data by handling each tick individually.

System method (not intended to be called by user code).

Handle the given signal.

If state is RUNNING then passes to on_signal.

System method (not intended to be called by user code).

Handle the given trade tick.

If state is RUNNING then passes to on_trade_tick.

System method (not intended to be called by user code).

Handle the given historical trade tick data by handling each tick individually.

System method (not intended to be called by user code).

Return a value indicating whether there are any active tasks.

Return a value indicating whether there are any queued OR active tasks.

Return whether the actor is pending processing for any requests.

Return a value indicating whether there are any queued tasks.

Return a value indicating whether all indicators are initialized.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the request for the given identifier is pending processing.

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Load the actor/strategy state from the give state dictionary.

Calls on_load and passes the state.

Exceptions raised will be caught, logged, and reraised.

If contingent orders should be managed automatically by the strategy.

If all order GTD time in force expirations should be managed automatically by the strategy.

Modify the given order with optional parameters and routing instructions.

An ModifyOrder command will be created and then sent to either the OrderEmulator or the RiskEngine (depending on whether the order is emulated).

At least one value must differ from the original order for the command to be valid.

Will use an Order Cancel/Replace Request (a.k.a Order Modification) for FIX protocols, otherwise if order update is not available for the API, then will cancel and replace with a new order using the original ClientOrderId.

If the order is already closed or at PENDING_CANCEL status then the command will not be generated, and a warning will be logged.

The message bus for the actor (if registered).

The order management system for the strategy.

Actions to be performed when running and receives a bar.

System method (not intended to be called by user code).

Actions to be performed when running and receives data.

System method (not intended to be called by user code).

Actions to be performed on degrade.

System method (not intended to be called by user code).

Should be overridden in the actor implementation.

Actions to be performed on dispose.

Cleanup/release any resources used here.

System method (not intended to be called by user code).

Actions to be performed running and receives an event.

System method (not intended to be called by user code).

Actions to be performed on fault.

Cleanup any resources used by the actor here.

System method (not intended to be called by user code).

Should be overridden in the actor implementation.

Actions to be performed when running and receives a funding rate update.

System method (not intended to be called by user code).

Actions to be performed when running and receives historical data.

System method (not intended to be called by user code).

Actions to be performed when running and receives an index price update.

System method (not intended to be called by user code).

Actions to be performed when running and receives an instrument.

System method (not intended to be called by user code).

Actions to be performed when running and receives an instrument close update.

System method (not intended to be called by user code).

Actions to be performed when running and receives an instrument status update.

System method (not intended to be called by user code).

Actions to be performed when the actor state is loaded.

Saved state values will be contained in the give state dictionary.

System method (not intended to be called by user code).

Actions to be performed when running and receives a mark price update.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order accepted event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order book.

System method (not intended to be called by user code).

Actions to be performed when running and receives order book deltas.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order book depth.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order cancel rejected event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order canceled event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order denied event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order emulated event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order expired event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order filled event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order initialized event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order modify rejected event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order pending cancel event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order pending update event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order rejected event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order released event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order submitted event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order triggered event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order updated event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position changed event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position closed event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a position opened event.

System method (not intended to be called by user code).

Actions to be performed when running and receives a quote tick.

System method (not intended to be called by user code).

Actions to be performed when the actor state is saved.

Create and return a state dictionary of values to be saved.

System method (not intended to be called by user code).

Actions to be performed when running and receives signal data.

System method (not intended to be called by user code).

Actions to be performed when running and receives a trade tick.

System method (not intended to be called by user code).

The order factory for the strategy.

The order ID tag for the strategy.

Return the request IDs which are currently pending processing.

The read-only portfolio for the actor.

Publish the given data to the message bus.

Publish the given value as a signal to the message bus.

Query the account with optional routing instructions.

A QueryAccount command will be created and then sent to the ExecutionEngine.

Query the given order with optional routing instructions.

A QueryOrder command will be created and then sent to the ExecutionEngine.

Logs an error if no VenueOrderId has been assigned to the order.

Queues the callable func to be executed as fn(*args, **kwargs) sequentially.

Return the queued task identifiers.

Register the strategy with a trader.

System method (not intended to be called by user code).

Register with a trader.

System method (not intended to be called by user code).

Register the given Executor for the actor.

Register the given indicator with the actor/strategy to receive bar data for the given bar type.

Register the given indicator with the actor/strategy to receive quote tick data for the given instrument ID.

Register the given indicator with the actor/strategy to receive trade tick data for the given instrument ID.

Register the given event type for warning log levels.

Return the registered indicators for the strategy.

Request historical aggregated Bar data for multiple bar types. The first bar is used to determine which market data type will be queried. This can either be quotes, trades or bars. If bars are queried, the first bar type needs to have a composite bar that is external (i.e. not internal/aggregated). This external bar type will be queried.

If end is None then will request up to the most recent data.

Once the response is received, the bar data is forwarded from the message bus to the on_historical_data handler. Any tick data used for aggregation is also forwarded to the on_historical_data handler.

If the request fails, then an error is logged.

Request historical Bar data.

If end is None then will request up to the most recent data.

Once the response is received, the bar data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request custom data for the given data type from the given data client.

Once the response is received, the data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request Instrument data for the given instrument ID.

If end is None then will request up to the most recent data.

Once the response is received, the instrument data is forwarded from the message bus to the on_instrument handler.

If the request fails, then an error is logged.

Request all Instrument data for the given venue.

If end is None then will request up to the most recent data.

Once the response is received, the instrument data is forwarded from the message bus to the on_instrument handler.

If the request fails, then an error is logged.

Request historical OrderBookDepth10 snapshots.

Once the response is received, the order book depth data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request an order book snapshot.

Once the response is received, the order book data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request historical QuoteTick data.

If end is None then will request up to the most recent data.

Once the response is received, the quote tick data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

Request historical TradeTick data.

If end is None then will request up to the most recent data.

Once the response is received, the trade tick data is forwarded from the message bus to the on_historical_data handler.

If the request fails, then an error is logged.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Schedules the callable func to be executed as fn(*args, **kwargs).

Return the actor/strategy state dictionary to be saved.

Exceptions raised will be caught, logged, and reraised.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Submit the given order with optional position ID, execution algorithm and routing instructions.

A SubmitOrder command will be created and sent to either an ExecAlgorithm, the OrderEmulator or the RiskEngine (depending whether the order is emulated and/or has an exec_algorithm_id specified).

If the client order ID is duplicate, then the order will be denied.

If a position_id is passed and a position does not yet exist, then any position opened by the order will have this position ID assigned. This may not be what you intended.

Submit the given order list with optional position ID, execution algorithm and routing instructions.

A SubmitOrderList command will be created and sent to either the OrderEmulator, or the RiskEngine (depending whether an order is emulated).

If the order list ID is duplicate, or any client order ID is duplicate, then all orders will be denied.

If a position_id is passed and a position does not yet exist, then any position opened by an order will have this position ID assigned. This may not be what you intended.

Subscribe to streaming Bar data for the given bar type.

Once subscribed, any matching bar data published on the message bus is forwarded to the on_bar handler.

Subscribe to data of the given data type.

Once subscribed, any matching data published on the message bus is forwarded to the on_data handler.

Subscribe to streaming FundingRateUpdate data for the given instrument ID.

Once subscribed, any matching funding rate updates published on the message bus are forwarded to the on_funding_rate handler.

Subscribe to streaming IndexPriceUpdate data for the given instrument ID.

Once subscribed, any matching index price updates published on the message bus are forwarded to the on_index_price handler.

Subscribe to update Instrument data for the given instrument ID.

Once subscribed, any matching instrument data published on the message bus is forwarded to the on_instrument handler.

Subscribe to close updates for the given instrument ID.

Once subscribed, any matching instrument close data published on the message bus is forwarded to the on_instrument_close handler.

Subscribe to status updates for the given instrument ID.

Once subscribed, any matching instrument status data published on the message bus is forwarded to the on_instrument_status handler.

Subscribe to update Instrument data for the given venue.

Once subscribed, any matching instrument data published on the message bus is forwarded the on_instrument handler.

Subscribe to streaming MarkPriceUpdate data for the given instrument ID.

Once subscribed, any matching mark price updates published on the message bus are forwarded to the on_mark_price handler.

Subscribe to an OrderBook at a specified interval for the given instrument ID.

Once subscribed, any matching order book updates published on the message bus are forwarded to the on_order_book handler.

The DataEngine will only maintain one order book for each instrument. Because of this - the level, depth and params for the stream will be set as per the last subscription request (this will also affect all subscribers).

Consider subscribing to order book deltas if you need intervals less than 100 milliseconds.

Subscribe to the order book data stream, being a snapshot then deltas for the given instrument ID.

Once subscribed, any matching order book data published on the message bus is forwarded to the on_order_book_deltas handler.

Subscribe to the order book depth stream for the given instrument ID.

Once subscribed, any matching order book data published on the message bus is forwarded to the on_order_book_depth handler.

Subscribe to all order fills for the given instrument ID.

Once subscribed, any matching order fills published on the message bus are forwarded to the on_order_filled handler.

Subscribe to streaming QuoteTick data for the given instrument ID.

Once subscribed, any matching quote tick data published on the message bus is forwarded to the on_quote_tick handler.

Subscribe to a specific signal by name, or to all signals if no name is provided.

Once subscribed, any matching signal data published on the message bus is forwarded to the on_signal handler.

Subscribe to streaming TradeTick data for the given instrument ID.

Once subscribed, any matching trade tick data published on the message bus is forwarded to the on_trade_tick handler.

Returns an importable configuration for this strategy.

The trader ID associated with the component.

Unsubscribe from streaming Bar data for the given bar type.

Unsubscribe from data of the given data type.

Unsubscribe from streaming FundingRateUpdate data for the given instrument ID.

Unsubscribe from streaming IndexPriceUpdate data for the given instrument ID.

Unsubscribe from update Instrument data for the given instrument ID.

Unsubscribe from close updates for the given instrument ID.

Unsubscribe from status updates for the given instrument ID.

Unsubscribe from update Instrument data for the given venue.

Unsubscribe from streaming MarkPriceUpdate data for the given instrument ID.

Unsubscribe from an OrderBook at a specified interval for the given instrument ID.

The interval must match the previously subscribed interval.

Unsubscribe the order book deltas stream for the given instrument ID.

Unsubscribe the order book depth stream for the given instrument ID.

Unsubscribe from all order fills for the given instrument ID.

Unsubscribe from streaming QuoteTick data for the given instrument ID.

Unsubscribe from streaming TradeTick data for the given instrument ID.

Update the synthetic instrument in the cache.

If hyphens should be used in generated client order ID values.

If UUID4’s should be used for client order ID values.

The Trader class is intended to manage a fleet of trading strategies within a running instance of the platform.

A running instance could be either a test/backtest or live implementation - the Trader will operate in the same way.

Provides a trader for managing a fleet of actors, execution algorithms and trading strategies.

Return the traders instance ID.

Return the actors loaded in the trader.

Return the strategies loaded in the trader.

Return the execution algorithms loaded in the trader.

Return the actor IDs loaded in the trader.

Return the strategy IDs loaded in the trader.

Return the execution algorithm IDs loaded in the trader.

Return the traders actor states.

Return the traders strategy states.

Return the traders execution algorithm states.

Add the given custom component to the trader.

Add the given actors to the trader.

Add the given trading strategy to the trader.

Add the given trading strategies to the trader.

Add the given execution algorithm to the trader.

Add the given execution algorithms to the trader.

Start the actor with the given actor_id.

Start the strategy with the given strategy_id.

Stop the actor with the given actor_id.

Stop the strategy with the given strategy_id.

Remove the actor with the given actor_id.

Will stop the actor first if state is RUNNING.

Remove the strategy with the given strategy_id.

Will stop the strategy first if state is RUNNING.

Dispose and clear all actors held by the trader.

Dispose and clear all strategies held by the trader.

Dispose and clear all execution algorithms held by the trader.

Subscribe to the given message topic with the given callback handler.

Unsubscribe the given handler from the given message topic.

Save all actor and strategy states to the cache.

Load all actor and strategy states from the cache.

Check for residual open state such as open orders or open positions.

Generate an orders report.

Generate an order fills report.

Generate a fills report.

Generate a positions report.

Generate an account report.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

The trader ID associated with the component.

---

## Analysis

**URL:** https://nautilustrader.io/docs/latest/api_reference/analysis

**Contents:**
- Analysis
  - class AvgLoser​
    - calculate_from_positions(_positions)​
    - calculate_from_realized_pnls(realized_pnls)​
    - calculate_from_returns(_returns)​
    - name​
  - class AvgWinner​
    - calculate_from_positions(_positions)​
    - calculate_from_realized_pnls(realized_pnls)​
    - calculate_from_returns(_returns)​

The analysis subpackage groups components relating to trading performance statistics and analysis.

Calculates the expectancy of a trading strategy based on realized PnLs.

Expectancy is defined as: (Average Win × Win Rate) + (Average Loss × Loss Rate) This metric provides insight into the expected profitability per trade and helps evaluate the overall edge of a trading strategy.

A positive expectancy indicates a profitable system over time, while a negative expectancy suggests losses.

Provides a portfolio performance analyzer for tracking and generating performance metrics and statistics.

Add positions data to the analyzer.

Add return data to the analyzer.

Add trade data to the analyzer.

Calculate performance metrics from the given data.

Return the analyzed currencies.

Deregister a statistic from the analyzer.

Deregister all statistics from the analyzer.

Return the general performance statistics.

Return the ‘PnL’ (profit and loss) performance statistics, optionally includes the unrealized PnL.

Money objects are converted to floats.

Return the return performance statistics values.

Return the performance statistics for returns from the last backtest run formatted for printing in the backtest run footer.

Return the performance statistics from the last backtest run formatted for printing in the backtest run footer.

Return the performance statistics for returns from the last backtest run formatted for printing in the backtest run footer.

Return the realized PnL for the portfolio.

For multi-currency portfolios, specify the currency for the result.

Register the given statistic with the analyzer.

All stateful fields are reset to their initial value.

Return raw the returns data.

Return the statistic with the given name (if found).

Return the total PnL for the portfolio.

For multi-currency portfolios, specify the currency for the result.

Return the percentage change of the total PnL for the portfolio.

For multi-currency accounts, specify the currency for the result.

The base class for all portfolio performance statistics.

Calculate the statistic value from the given orders.

Calculate the statistic value from the given positions.

Calculate the statistic value from the given raw realized PnLs.

Calculate the statistic value from the given raw returns.

Return the fully qualified name for the PortfolioStatistic class.

Return the name for the statistic.

Calculates the profit factor based on portfolio returns.

Profit factor is defined as the ratio of gross profits to gross losses: Sum(Positive Returns) / Abs(Sum(Negative Returns))

A profit factor greater than 1.0 indicates a profitable strategy, while a factor less than 1.0 indicates losses exceed gains.

2.0: Excellent profitability

Provides various portfolio analysis reports.

Generate an account report for the given optional time range.

Generate a fills report.

This report provides a row per individual fill event.

Generate an order fills report.

This report provides a row per order.

Generate an orders report.

Generate a positions report.

Calculates the annualized volatility (standard deviation) of portfolio returns.

Volatility is calculated as the standard deviation of returns, annualized by multiplying the daily standard deviation by the square root of the period: Standard Deviation * sqrt(period)

Uses Bessel’s correction (ddof=1) for sample standard deviation. This provides a measure of the portfolio’s risk or uncertainty of returns.

Calculates the Sharpe ratio for portfolio returns.

The Sharpe ratio measures risk-adjusted return and is calculated as: (Mean Return - Risk-free Rate) / Standard Deviation of Returns * sqrt(period)

This implementation assumes a risk-free rate of 0 and annualizes the ratio using the square root of the specified period (default: 252 trading days).

Calculates the Sortino ratio for portfolio returns.

The Sortino ratio is a variation of the Sharpe ratio that only penalizes downside volatility, making it more appropriate for strategies with asymmetric return distributions.

Formula: Mean Return / Downside Deviation * sqrt(period)

Where downside deviation is calculated as: sqrt(sum(negative_returns^2) / total_observations)

Note: Uses total observations count (not just negative returns) as per Sortino’s methodology.

Calculates the win rate of a trading strategy based on realized PnLs.

Win rate is the percentage of profitable trades out of total trades: Count(Trades with PnL > 0) / Total Trades

Returns a value between 0.0 and 1.0, where 1.0 represents 100% winning trades.

Note: While a high win rate is desirable, it should be considered alongside average win/loss sizes and profit factor for complete system evaluation.

Provides a portfolio performance analyzer for tracking and generating performance metrics and statistics.

Register the given statistic with the analyzer.

Deregister a statistic from the analyzer.

Deregister all statistics from the analyzer.

All stateful fields are reset to their initial value.

Return the analyzed currencies.

Return the statistic with the given name (if found).

Return raw the returns data.

Calculate performance metrics from the given data.

Add positions data to the analyzer.

Add trade data to the analyzer.

Add return data to the analyzer.

Return the realized PnL for the portfolio.

For multi-currency portfolios, specify the currency for the result.

Return the total PnL for the portfolio.

For multi-currency portfolios, specify the currency for the result.

Return the percentage change of the total PnL for the portfolio.

For multi-currency accounts, specify the currency for the result.

Return the ‘PnL’ (profit and loss) performance statistics, optionally includes the unrealized PnL.

Money objects are converted to floats.

Return the return performance statistics values.

Return the general performance statistics.

Return the performance statistics from the last backtest run formatted for printing in the backtest run footer.

Return the performance statistics for returns from the last backtest run formatted for printing in the backtest run footer.

Return the performance statistics for returns from the last backtest run formatted for printing in the backtest run footer.

Provides various portfolio analysis reports.

Generate an orders report.

Generate an order fills report.

This report provides a row per order.

Generate a fills report.

This report provides a row per individual fill event.

Generate a positions report.

Generate an account report for the given optional time range.

The base class for all portfolio performance statistics.

Return the fully qualified name for the PortfolioStatistic class.

Return the name for the statistic.

Calculate the statistic value from the given raw returns.

Calculate the statistic value from the given raw realized PnLs.

Calculate the statistic value from the given orders.

Calculate the statistic value from the given positions.

---

## Position

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/position

**Contents:**
- Position
  - class Position​
    - account_id​
    - apply(self, OrderFilled fill) → void​
    - avg_px_close​
    - avg_px_open​
    - base_currency​
    - calculate_pnl(self, double avg_px_open, double avg_px_close, Quantity quantity) → Money​
    - client_order_ids​
    - closing_order_id​

Position(Instrument instrument, OrderFilled fill) -> None

Represents a position in a market.

The position ID may be assigned at the trading venue, or can be system generated depending on a strategies OMS (Order Management System) settings.

The account ID associated with the position.

Applies the given order fill event to the position.

If the position is FLAT prior to applying fill, the position state is reset (clearing existing events, commissions, etc.) before processing the new fill.

The average close price.

The average open price.

The position base currency (if applicable).

Return a calculated PnL in the instrument’s settlement currency.

Return the client order IDs associated with the position.

The client order ID for the order which closed the position.

Return the closing order side for the position.

If the position is FLAT then will return NO_ORDER_SIDE.

Return the total commissions generated by the position.

The total open duration in nanoseconds (zero unless closed).

The position entry order side.

Return the count of order fill events applied to the position.

Return the order fill events for the position.

Return a summary description of the position.

The position instrument ID.

Return whether the position side is FLAT.

If the quantity is expressed in quote currency.

Return whether the position side is LONG.

Return whether the position side is not FLAT.

Return a value indicating whether the given order side is opposite to the current position side.

Return whether the position side is SHORT.

Return the last order fill event (if any after purging).

Return the last trade match ID for the position (if any after purging).

The multiplier for the positions instrument.

Return the current notional value of the position, using a reference price for the calculation (e.g., bid, ask, mid, last, or mark).

The client order ID for the order which opened the position.

The peak directional quantity reached by the position.

The price precision for the position.

Purge all order events for the given client order ID.

After purging, the position is rebuilt from remaining fills. If no fills remain, the position is reset to an empty shell with all history cleared (including timestamps), making it eligible for immediate cache cleanup.

The current open quantity.

The position quote currency.

The current realized PnL for the position (including commissions).

The current realized return for the position.

The position settlement currency (for PnL).

The current position side.

Return the position side resulting from the given order side (from FLAT).

Return a signed decimal representation of the position quantity.

The current signed quantity (positive for position side LONG, negative for SHORT).

The size precision for the position.

The strategy ID associated with the position.

Return the positions ticker symbol.

Return a dictionary representation of this object.

Return the total PnL for the position, using a reference price for the calculation (e.g., bid, ask, mid, last, or mark).

Return the trade match IDs associated with the position.

The trader ID associated with the position.

UNIX timestamp (nanoseconds) when the position was closed (zero unless closed).

UNIX timestamp (nanoseconds) when the object was initialized.

UNIX timestamp (nanoseconds) when the last event occurred.

UNIX timestamp (nanoseconds) when the position was opened.

Return the unrealized PnL for the position, using a reference price for the calculation (e.g., bid, ask, mid, last, or mark).

Return the positions trading venue.

Return the venue order IDs associated with the position.

---

## Risk

**URL:** https://nautilustrader.io/docs/latest/api_reference/risk

**Contents:**
- Risk
  - class RiskEngine​
    - command_count​
    - debug​
    - degrade(self) → void​
    - WARNING​
    - dispose(self) → void​
    - WARNING​
    - event_count​
    - execute(self, Command command) → void​

The risk subpackage groups all risk specific components and tooling.

Included is a PositionSizer component which can be used by trading strategies to help with risk management through position sizing.

RiskEngine(PortfolioFacade portfolio, MessageBus msgbus, Cache cache, Clock clock, config: RiskEngineConfig | None = None) -> None

Provides a high-performance risk engine.

The RiskEngine is responsible for global strategy and portfolio risk within the platform. This includes both pre-trade risk checks and post-trade risk monitoring.

Possible trading states: : - ACTIVE (trading is enabled).

The total count of commands received by the engine.

If debug mode is active (will provide extra debug logging).

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

The total count of events received by the engine.

Execute the given command.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

If the risk engine is completely bypassed.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Return the current maximum notional per order for the given instrument ID.

Return the current maximum notionals per order settings.

Return the current maximum order modify rate limit setting.

Return the current maximum order submit rate limit setting.

Process the given event.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Set the maximum notional value per order for the given instrument ID.

Passing a new_value of None will disable the pre-trade risk max notional check.

Set the trading state for the engine.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

The trader ID associated with the component.

The current trading state for the engine.

FixedRiskSizer(Instrument instrument)

Provides position sizing calculations based on a given risk.

Calculate the position size quantity.

The instrument for position sizing.

Update the internal instrument with the given instrument.

PositionSizer(Instrument instrument)

The base class for all position sizers.

This class should not be used directly, but through a concrete subclass.

Abstract method (implement in subclass).

The instrument for position sizing.

Update the internal instrument with the given instrument.

---

## Integrations

**URL:** https://nautilustrader.io/docs/latest/integrations

**Contents:**
- Integrations
- Status​
- Implementation goals​
- API unification​

NautilusTrader uses modular adapters to connect to trading venues and data providers, translating raw APIs into a unified interface and normalized domain model.

The following integrations are currently supported:

The primary goal of NautilusTrader is to provide a unified trading system for use with a variety of integrations. To support the widest range of trading strategies, priority will be given to standard functionality:

The implementation of each integration aims to meet the following criteria:

All integrations must conform to NautilusTrader’s system API, requiring normalization and standardization:

---

## NautilusTrader Documentation

**URL:** https://nautilustrader.io/docs/latest/

**Contents:**
- NautilusTrader Documentation
  - Popular topics
    - Getting Started
    - Concepts
    - Tutorials
    - Integrations
    - Developer Guide

Welcome to the official documentation for NautilusTrader!

NautilusTrader is an open-source, high-performance, production-grade algorithmic trading platform, providing quantitative traders with the ability to backtest portfolios of automated trading strategies on historical data with an event-driven engine, and also deploy those same strategies live, with no code changes.

The platform provides an extensive array of features and capabilities, coupled with open-ended flexibility for assembling trading systems using the framework. Given the breadth of information, and required pre-requisite knowledge, both beginners and experts alike may find the learning curve steep. However, this documentation aims to assist you in learning and understanding NautilusTrader, so that you can then leverage it to achieve your algorithmic trading goals.

If you have any questions or need further assistance, please reach out to the NautilusTrader community for support.

Provides an overview, installation guide, and tutorials for setting up and running your first backtests.

Understand key concepts, essential terminologies, core architecture, and algorithmic trading principles within NautilusTrader.

Guided learning experience with a series of comprehensive step-by-step walkthroughs. Each tutorial targets specific features or workflows, enabling hands-on learning.

Details adapter integrations for connecting with trading venues and data providers, unifying their raw APIs into a single interface.

These guides will help you add functionality to your trading operation and/or provide valuable contributions.

The terms "NautilusTrader", "Nautilus" and "platform" are used interchageably throughout the documentation.

---

## Integrations

**URL:** https://nautilustrader.io/docs/latest/integrations/

**Contents:**
- Integrations
- Status​
- Implementation goals​
- API unification​

NautilusTrader uses modular adapters to connect to trading venues and data providers, translating raw APIs into a unified interface and normalized domain model.

The following integrations are currently supported:

The primary goal of NautilusTrader is to provide a unified trading system for use with a variety of integrations. To support the widest range of trading strategies, priority will be given to standard functionality:

The implementation of each integration aims to meet the following criteria:

All integrations must conform to NautilusTrader’s system API, requiring normalization and standardization:

---
