# Nautilus_Trader - Data

**Pages:** 12

---

## OKX

**URL:** https://nautilustrader.io/docs/latest/integrations/okx

**Contents:**
- OKX
- Overview​
- Examples​
  - Product support​
- Symbology​
  - Symbol format by instrument type​
    - SPOT​
    - SWAP (Perpetual Futures)​
    - FUTURES (Dated Futures)​
    - OPTIONS​

Founded in 2017, OKX is a leading cryptocurrency exchange offering spot, perpetual swap, futures, and options trading. This integration supports live market data ingest and order execution on OKX.

This adapter is implemented in Rust, with optional Python bindings for ease of use in Python-based workflows. It does not require external OKX client libraries—the core components are compiled as a static library and linked automatically during the build.

You can find live example scripts here.

Options support: While you can subscribe to options market data and receive price updates, order execution for options is not yet implemented. You can use the symbology format shown above to subscribe to options data feeds.

Instrument multipliers: For derivatives (SWAP, FUTURES, OPTIONS), instrument multipliers are calculated as the product of OKX's ctMult (contract multiplier) and ctVal (contract value) fields. This ensures position sizing accurately reflects both the contract size and value.

The OKX adapter includes multiple components, which can be used separately or together depending on your use case.

Most users will simply define a configuration for a live trading node (as shown below), and won’t need to work directly with these lower-level components.

OKX uses specific symbol conventions for different instrument types. All instrument IDs should include the .OKX suffix when referencing them (e.g., BTC-USDT.OKX for spot Bitcoin).

Format: {BaseCurrency}-{QuoteCurrency}

To subscribe to spot Bitcoin USD in your strategy:

Format: {BaseCurrency}-{QuoteCurrency}-SWAP

Linear vs Inverse contracts:

Format: {BaseCurrency}-{QuoteCurrency}-{YYMMDD}

Note: Futures are typically inverse contracts (coin-margined).

Format: {BaseCurrency}-{QuoteCurrency}-{YYMMDD}-{Strike}-{Type}

Q: How do I subscribe to spot Bitcoin USD? A: Use BTC-USDT.OKX for USDT-margined spot or BTC-USDC.OKX for USDC-margined spot.

Q: What's the difference between BTC-USDT-SWAP and BTC-USD-SWAP? A: BTC-USDT-SWAP is a linear perpetual (USDT-margined), while BTC-USD-SWAP is an inverse perpetual (BTC-margined).

Q: How do I know which contract type to use? A: Check the contract_types parameter in the configuration:

Below are the order types, execution instructions, and time-in-force options supported for linear perpetual swap products on OKX.

OKX has specific requirements for client order IDs:

When configuring your strategy, ensure you set:

Conditional orders: STOP_MARKET, STOP_LIMIT, MARKET_IF_TOUCHED, and LIMIT_IF_TOUCHED are implemented as OKX algo orders, providing advanced trigger capabilities with multiple price sources.

When using spot margin trading (use_spot_margin=True), OKX interprets order quantities differently depending on the order side:

When submitting spot margin market BUY orders, you must:

The OKX execution client will deny base-denominated market buy orders for spot margin to prevent unintended fills.

On the first fill, the order quantity will be automatically updated from the quote quantity to the actual base quantity received, reflecting the executed trade.

GTD (Good Till Date) time in force: OKX does not support native GTD functionality through their API.

If you need GTD functionality, you must use Nautilus's strategy-managed GTD feature, which will handle the order expiration by canceling the order at the specified expiry time.

OKX supports two position modes for derivatives trading:

Position mode must be configured via the OKX Web/App interface and applies account-wide. The adapter automatically detects the current position mode and handles position reporting accordingly.

OKX's unified account system supports different trade modes for spot and derivatives trading. The adapter automatically determines the correct trade mode based on your configuration and instrument type.

Important: Account modes must be initially configured via the OKX Web/App interface. The API cannot set the account mode for the first time.

For more details on OKX's account modes and margin system, see the OKX Account Mode documentation.

OKX supports four trade modes, which the adapter selects automatically based on your configuration:

The adapter automatically selects the correct trade mode based on:

When trading both SPOT and derivatives instruments simultaneously, the adapter automatically determines the correct trade mode per-order based on the instrument being traded:

This enables strategies that trade across multiple instrument types with different margin configurations, such as:

Manual trade mode override: While you can still manually override the trade mode per order using params={"td_mode": "..."}, this is not recommended as it bypasses automatic mode selection and can lead to order rejection if the wrong mode is specified for the instrument type (e.g., using isolated for SPOT instruments).

Only use manual override if you have specific requirements that cannot be met through configuration.

Conditional orders (OKX algo orders) use a hybrid architecture for optimal performance and reliability:

Conditional orders support different trigger price sources:

The OKX adapter automatically detects and handles exchange-initiated risk management events:

Liquidation and ADL events are logged at WARNING level with details including order ID, instrument, and state. Monitor your logs for these events as part of your risk management process.

The adapter handles these exchange-generated orders seamlessly, generating appropriate OrderFilled events and updating positions accordingly. No special handling is required in your strategy code.

To use the OKX adapter, you'll need to create API credentials in your OKX account:

You can provide these credentials through environment variables:

Or pass them directly in the configuration (not recommended for production).

OKX provides a demo trading environment for testing strategies without real funds. To use demo mode, set is_demo=True in your client configuration:

When demo mode is enabled:

You must use API keys created specifically for demo trading. Production API keys will not work in demo mode.

The adapter enforces OKX’s per-endpoint quotas while keeping sensible defaults for both REST and WebSocket calls.

OKX enforces per-endpoint and per-account quotas; exceeding them leads to HTTP 429 responses and temporary throttling on that key.

All keys automatically include the okx:global bucket. URLs are normalised (query strings removed) before rate limiting, so requests with different filters share the same quota.

For more details on rate limiting, see the official documentation: https://www.okx.com/docs-v5/en/#rest-api-rate-limit.

The OKX data client provides the following configuration options:

The OKX execution client provides the following configuration options:

Below is an example configuration for a live trading node using OKX data and execution clients:

For additional features or to contribute to the OKX adapter, please see our contributing guide.

**Examples:**

Example 1 (python):
```python
InstrumentId.from_str("BTC-USDT.OKX")  # For USDT-quoted spotInstrumentId.from_str("BTC-USDC.OKX")  # For USDC-quoted spot
```

Example 2 (python):
```python
use_hyphens_in_client_order_ids=False
```

Example 3 (python):
```python
from nautilus_trader.execution.config import ExecEngineConfigfrom nautilus_trader.execution.engine import ExecutionEngine# Disable automatic conversion for quote quantitiesconfig = ExecEngineConfig(convert_quote_qty_to_base=False)engine = ExecutionEngine(msgbus=msgbus, cache=cache, clock=clock, config=config)# Correct: Spot margin market BUY with quote quantity (spend $100 USDT)order = strategy.order_factory.market(    instrument_id=instrument_id,    order_side=OrderSide.BUY,    quantity=instrument.make_qty(100.0),    quote_quantity=True,  # Interpret as USDT notional)strategy.submit_order(order)
```

Example 4 (python):
```python
# Simple SPOT trading without leverage (uses 'cash' mode)exec_clients={    OKX: OKXExecClientConfig(        instrument_types=(OKXInstrumentType.SPOT,),        use_spot_margin=False,  # Default - simple SPOT        # ... other config    ),}# SPOT trading WITH margin/leverage (uses 'spot_isolated' mode)exec_clients={    OKX: OKXExecClientConfig(        instrument_types=(OKXInstrumentType.SPOT,),        use_spot_margin=True,  # Enable margin trading for SPOT        # ... other config    ),}
```

---

## Tardis

**URL:** https://nautilustrader.io/docs/latest/integrations/tardis

**Contents:**
- Tardis
- Overview​
- Tardis documentation​
- Supported formats​
- Bars​
- Symbology and normalization​
  - Common rules​
  - Exchange-specific normalizations​
- Venues​
- Environment variables​

Tardis provides granular data for cryptocurrency markets including tick-by-tick order book snapshots & updates, trades, open interest, funding rates, options chains and liquidations data for leading crypto exchanges.

NautilusTrader provides an integration with the Tardis API and data formats, enabling seamless access. The capabilities of this adapter include:

A Tardis API key is required for the adapter to operate correctly. See also environment variables.

This adapter is implemented in Rust, with optional Python bindings for ease of use in Python-based workflows. It does not require any external Tardis client library dependencies.

There is no need for additional installation steps for tardis. The core components of the adapter are compiled as static libraries and automatically linked during the build process.

Tardis provides extensive user documentation. We recommend also referring to the Tardis documentation in conjunction with this NautilusTrader integration guide.

Tardis provides normalized market data—a unified format consistent across all supported exchanges. This normalization is highly valuable because it allows a single parser to handle data from any Tardis-supported exchange, reducing development time and complexity. As a result, NautilusTrader will not support exchange-native market data formats, as it would be inefficient to implement separate parsers for each exchange at this stage.

The following normalized Tardis formats are supported by NautilusTrader:

See also the Tardis normalized market data APIs.

The adapter will automatically convert Tardis trade bar interval and suffix to Nautilus BarTypes. This includes the following:

The Tardis integration ensures seamless compatibility with NautilusTrader’s crypto exchange adapters by consistently normalizing symbols. Typically, NautilusTrader uses the native exchange naming conventions provided by Tardis. However, for certain exchanges, raw symbols are adjusted to adhere to the Nautilus symbology normalization, as outlined below:

For detailed symbology documentation per exchange:

Some exchanges on Tardis are partitioned into multiple venues. The table below outlines the mappings between Nautilus venues and corresponding Tardis exchanges, as well as the exchanges that Tardis supports:

The following environment variables are used by Tardis and NautilusTrader.

The Tardis Machine Server is a locally runnable server with built-in data caching, providing both tick-level historical and consolidated real-time cryptocurrency market data through HTTP and WebSocket APIs.

You can perform complete Tardis Machine WebSocket replays of historical data and output the results in Nautilus Parquet format, using either Python or Rust. Since the function is implemented in Rust, performance is consistent whether run from Python or Rust, letting you choose based on your preferred workflow.

The end-to-end run_tardis_machine_replay data pipeline function utilizes a specified configuration to execute the following steps:

File Naming Convention

Files are written one per day, per instrument, using ISO 8601 timestamp ranges that clearly indicate the exact time span of data:

This format is fully compatible with the Nautilus data catalog, enabling seamless querying, consolidation, and data management operations.

You can request data for the first day of each month without an API key. For all other dates, a Tardis Machine API key is required.

This process is optimized for direct output to a Nautilus Parquet data catalog. Ensure that the NAUTILUS_PATH environment variable is set to the parent directory containing the catalog/ subdirectory. Parquet files will then be organized under <NAUTILUS_PATH>/catalog/data/ in the expected subdirectories corresponding to data type and instrument.

If no output_path is specified in the configuration file and the NAUTILUS_PATH environment variable is unset, the system will default to the current working directory.

First, ensure the tardis-machine docker container is running. Use the following command:

This command starts the tardis-machine server without a persistent local cache, which may affect performance. For improved performance, consider running the server with a persistent volume. Refer to the Tardis Docker documentation for details.

Next, ensure you have a configuration JSON file available.

Configuration JSON format

An example configuration file, example_config.json, is available here:

To run a replay in Python, create a script similar to the following:

To run a replay in Rust, create a binary similar to the following:

Make sure to enable Rust logging by exporting the following environment variable:

A working example binary can be found here.

This can also be run using cargo:

Tardis-format CSV data can be loaded using either Python or Rust. The loader reads the CSV text data from disk and parses it into Nautilus data. Since the loader is implemented in Rust, performance remains consistent regardless of whether you run it from Python or Rust, allowing you to choose based on your preferred workflow.

You can also optionally specify a limit parameter for the load_* functions/methods to control the maximum number of rows loaded.

Loading mixed-instrument CSV files is challenging due to precision requirements and is not recommended. Use single-instrument CSV files instead (see below).

You can load Tardis-format CSV data in Python using the TardisCSVDataLoader. When loading data, you can optionally specify the instrument ID but must specify both the price precision, and size precision. Providing the instrument ID improves loading performance, while specifying the precisions is required, as they cannot be inferred from the text data alone.

To load the data, create a script similar to the following:

You can load Tardis-format CSV data in Rust using the loading functions found here. When loading data, you can optionally specify the instrument ID but must specify both the price precision and size precision. Providing the instrument ID improves loading performance, while specifying the precisions is required, as they cannot be inferred from the text data alone.

For a complete example, see the example binary here.

To load the data, you can use code similar to the following:

For memory-efficient processing of large CSV files, the Tardis integration provides streaming capabilities that load and process data in configurable chunks rather than loading entire files into memory at once. This is particularly useful for processing multi-gigabyte CSV files without exhausting system memory.

The streaming functionality is available for all supported Tardis data types:

The TardisCSVDataLoader provides streaming methods that yield chunks of data as iterators. Each method accepts a chunk_size parameter that controls how many records are read from the CSV file per chunk:

For order book data, streaming is available for both deltas and depth snapshots:

Quote data can be streamed similarly:

The streaming approach provides significant memory efficiency advantages:

When using streaming with precision inference (not providing explicit precisions), the inferred precision may differ from bulk loading the entire file. This is because precision inference works within chunk boundaries, and different chunks may contain values with different precision requirements. For deterministic precision behavior, provide explicit price_precision and size_precision parameters when calling streaming methods.

The underlying streaming functionality is implemented in Rust and can be used directly:

You can request instrument definitions in both Python and Rust using the TardisHttpClient. This client interacts with the Tardis instruments metadata API to request and parse instrument metadata into Nautilus instruments.

The TardisHttpClient constructor accepts optional parameters for api_key, base_url, and timeout_secs (default is 60 seconds).

The client provides methods to retrieve either a specific instrument, or all instruments available on a particular exchange. Ensure that you use Tardis’s lower-kebab casing convention when referring to a Tardis-supported exchange.

A Tardis API key is required to access the instruments metadata API.

To request instrument definitions in Python, create a script similar to the following:

To request instrument definitions in Rust, use code similar to the following. For a complete example, see the example binary here.

The TardisInstrumentProvider requests and parses instrument definitions from Tardis through the HTTP instrument metadata API. Since there are multiple Tardis-supported exchanges, when loading all instruments, you must filter for the desired venues using an InstrumentProviderConfig:

You can also load specific instrument definitions in the usual way:

The instrument provider automatically filters out option-specific exchanges (such as binance-options, binance-european-options, bybit-options, okex-options, and huobi-dm-options) when the instrument_type filter is not provided or does not include "option".

To explicitly load option instruments, include "option" in the instrument_type filter:

This filtering mechanism prevents unnecessary API calls to option exchanges when they are not needed, improving performance and reducing API usage.

Instruments must be available in the cache for all subscriptions. For simplicity, it's recommended to load all instruments for the venues you intend to subscribe to.

The TardisDataClient enables integration of a Tardis Machine with a running NautilusTrader system. It supports subscriptions to the following data types:

The main TardisMachineClient data WebSocket manages all stream subscriptions received during the initial connection phase, up to the duration specified by ws_connection_delay_secs. For any additional subscriptions made after this period, a new TardisMachineClient is created. This approach optimizes performance by allowing the main WebSocket to handle potentially hundreds of subscriptions in a single stream if they are provided at startup.

When an initial subscription delay is set with ws_connection_delay_secs, unsubscribing from any of these streams will not actually remove the subscription from the Tardis Machine stream, as selective unsubscription is not supported by Tardis. However, the component will still unsubscribe from message bus publishing as expected.

All subscriptions made after any initial delay will behave normally, fully unsubscribing from the Tardis Machine stream when requested.

If you anticipate frequent subscription and unsubscription of data, it is recommended to set ws_connection_delay_secs to zero. This will create a new client for each initial subscription, allowing them to be later closed individually upon unsubscription.

The following limitations and considerations are currently known:

For additional features or to contribute to the Tardis adapter, please see our contributing guide.

**Examples:**

Example 1 (bash):
```bash
docker run -p 8000:8000 -p 8001:8001 -e "TM_API_KEY=YOUR_API_KEY" -d tardisdev/tardis-machine
```

Example 2 (json):
```json
{  "tardis_ws_url": "ws://localhost:8001",  "output_path": null,  "options": [    {      "exchange": "bitmex",      "symbols": [        "xbtusd",        "ethusd"      ],      "data_types": [        "trade"      ],      "from": "2019-10-01",      "to": "2019-10-02"    }  ]}
```

Example 3 (python):
```python
import asynciofrom nautilus_trader.core import nautilus_pyo3async def run():    config_filepath = Path("YOUR_CONFIG_FILEPATH")    await nautilus_pyo3.run_tardis_machine_replay(str(config_filepath.resolve()))if __name__ == "__main__":    asyncio.run(run())
```

Example 4 (rust):
```rust
use std::{env, path::PathBuf};use nautilus_adapters::tardis::replay::run_tardis_machine_replay_from_config;#[tokio::main]async fn main() {    tracing_subscriber::fmt()        .with_max_level(tracing::Level::DEBUG)        .init();    let config_filepath = PathBuf::from("YOUR_CONFIG_FILEPATH");    run_tardis_machine_replay_from_config(&config_filepath).await;}
```

---

## Databento

**URL:** https://nautilustrader.io/docs/latest/integrations/databento

**Contents:**
- Databento
- Overview​
- Examples​
- Databento documentation​
- Databento Binary Encoding (DBN)​
- Supported schemas​
  - Schema considerations​
- Schema selection for live subscriptions​
  - Quote subscriptions (MBP / L1)​
  - Trade subscriptions​

NautilusTrader provides an adapter for integrating with the Databento API and Databento Binary Encoding (DBN) format data. As Databento is purely a market data provider, there is no execution client provided - although a sandbox environment with simulated execution could still be set up. It's also possible to match Databento data with Interactive Brokers execution, or to calculate traditional asset class signals for crypto trading.

The capabilities of this adapter include:

Databento currently offers 125 USD in free data credits (historical data only) for new account sign-ups.

With careful requests, this is more than enough for testing and evaluation purposes. We recommend you make use of the /metadata.get_cost endpoint.

The adapter implementation takes the databento-rs crate as a dependency, which is the official Rust client library provided by Databento.

There is no need for an optional extra installation of databento, as the core components of the adapter are compiled as static libraries and linked automatically during the build process.

The following adapter classes are available:

As with the other integration adapters, most users will simply define a configuration for a live trading node (covered below), and won't need to necessarily work with these lower level components directly.

You can find live example scripts here.

Databento provides extensive documentation for new users which can be found in the Databento new users guide. We recommend also referring to the Databento documentation in conjunction with this NautilusTrader integration guide.

Databento Binary Encoding (DBN) is an extremely fast message encoding and storage format for normalized market data. The DBN specification includes a simple, self-describing metadata header and a fixed set of struct definitions, which enforce a standardized way to normalize market data.

The integration provides a decoder which can convert DBN format data to Nautilus objects.

The same Rust implemented Nautilus decoder is used for:

The following Databento schemas are supported by NautilusTrader:

Consolidated schemas (CMBP_1, CBBO_1S, CBBO_1M, TCBBO) aggregate data across multiple venues, providing a unified view of the market. These are particularly useful for cross-venue analysis and when you need a comprehensive market picture.

See also the Databento Schemas and data formats guide.

The following table shows how Nautilus subscription methods map to Databento schemas:

The examples below assume you're within a Strategy or Actor class context where self has access to subscription methods. Remember to import the necessary types:

For specialized Databento data types like imbalance and statistics, use the generic subscribe_data method:

Databento market data includes an instrument_id field which is an integer assigned by either the original source venue, or internally by Databento during normalization.

It's important to realize that this is different to the Nautilus InstrumentId which is a string made up of a symbol + venue with a period separator i.e. "{symbol}.{venue}".

The Nautilus decoder will use the Databento raw_symbol for the Nautilus symbol and an ISO 10383 MIC (Market Identifier Code) from the Databento instrument definition message for the Nautilus venue.

Databento datasets are identified with a dataset ID which is not the same as a venue identifier. You can read more about Databento dataset naming conventions here.

Of particular note is for CME Globex MDP 3.0 data (GLBX.MDP3 dataset ID), the following exchanges are all grouped under the GLBX venue. These mappings can be determined from the instruments exchange field:

Other venue MICs can be found in the venue field of responses from the metadata.list_publishers endpoint.

Databento data includes various timestamp fields including (but not limited to):

Nautilus data includes at least two timestamps (required by the Data contract):

When decoding and normalizing Databento to Nautilus we generally assign the Databento ts_recv value to the Nautilus ts_event field, as this timestamp is much more reliable and consistent, and is guaranteed to be monotonically increasing per instrument. The exception to this are the DatabentoImbalance and DatabentoStatistics data types, which have fields for all timestamps as these types are defined specifically for the adapter.

See the following Databento docs for further information:

The following section discusses Databento schema -> Nautilus data type equivalence and considerations.

See Databento schemas and data formats.

Databento provides a single schema to cover all instrument classes, these are decoded to the appropriate Nautilus Instrument types.

The following Databento instrument classes are supported by NautilusTrader:

This schema is the highest granularity data offered by Databento, and represents full order book depth. Some messages also provide trade information, and so when decoding MBO messages Nautilus will produce an OrderBookDelta and optionally a TradeTick.

The Nautilus live data client will buffer MBO messages until an F_LAST flag is seen. A discrete OrderBookDeltas container object will then be passed to the registered handler.

Order book snapshots are also buffered into a discrete OrderBookDeltas container object, which occurs during the replay startup sequence.

This schema represents the top-of-book only (quotes and trades). Like with MBO messages, some messages carry trade information, and so when decoding MBP-1 messages Nautilus will produce a QuoteTick and also a TradeTick if the message is a trade.

The TBBO (Top Book with Trades) and TCBBO (Top Consolidated Book with Trades) schemas provide both quote and trade data in each message. When subscribing to quotes using these schemas, you'll automatically receive both QuoteTick and TradeTick data, making them more efficient than subscribing to quotes and trades separately. TCBBO provides consolidated data across venues.

The Databento bar aggregation messages are timestamped at the open of the bar interval. The Nautilus decoder will normalize the ts_event timestamps to the close of the bar (original ts_event + bar interval).

The Databento imbalance and statistics schemas cannot be represented as a built-in Nautilus data types, and so they have specific types defined in Rust DatabentoImbalance and DatabentoStatistics. Python bindings are provided via PyO3 (Rust) so the types behave a little differently to built-in Nautilus data types, where all attributes are PyO3 provided objects and not directly compatible with certain methods which may expect a Cython provided type. There are PyO3 -> legacy Cython object conversion methods available, which can be found in the API reference.

Here is a general pattern for converting a PyO3 Price to a Cython Price:

Additionally requesting for and subscribing to these data types requires the use of the lower level generic methods for custom data types. The following example subscribes to the imbalance schema for the AAPL.XNAS instrument (Apple Inc trading on the Nasdaq exchange):

Or requesting the previous days statistics schema for the ES.FUT parent symbol (all active E-mini S&P 500 futures contracts on the CME Globex exchange):

When backtesting with Databento DBN data, there are two options:

Whilst the DBN -> Nautilus decoder is implemented in Rust and has been optimized, the best performance for backtesting will be achieved by writing the Nautilus objects to the data catalog, which performs the decoding step once.

DataFusion provides a query engine backend to efficiently load and stream the Nautilus Parquet data from disk, which achieves extremely high throughput (at least an order of magnitude faster than converting DBN -> Nautilus on the fly for every backtest run).

Performance benchmarks are currently under development.

You can load DBN files and convert the records to Nautilus objects using the DatabentoDataLoader class. There are two main purposes for doing so:

This code snippet demonstrates how to load DBN data and pass to a BacktestEngine. Since the BacktestEngine needs an instrument added, we'll use a test instrument provided by the TestInstrumentProvider (you could also pass an instrument object which was parsed from a DBN file too). The data is a month of TSLA (Tesla Inc) trades on the Nasdaq exchange:

This code snippet demonstrates how to load DBN data and write to a ParquetDataCatalog. We pass a value of false for the as_legacy_cython flag, which will ensure the DBN records are decoded as PyO3 (Rust) objects. It's worth noting that legacy Cython objects can also be passed to write_data, but these need to be converted back to pyo3 objects under the hood (so passing PyO3 objects is an optimization).

Important: When loading market data (MBO, trades, quotes, bars, etc.) into a catalog, you must first load the corresponding instrument definitions from DEFINITION schema files. The catalog needs instruments to be present before it can store market data. Market data files (MBO, TRADES, etc.) do not contain instrument definitions.

When preparing a catalog for backtesting with multiple data types (e.g., MBO order book data), always load instruments first:

You can verify your instruments loaded correctly by calling catalog.instruments() which returns a list of all instruments in the catalog. If this returns an empty list, you need to load DEFINITION files first.

To obtain DEFINITION schema files from Databento, use the Databento API or CLI to download instrument definitions for your symbols and date ranges. See the Databento documentation for details on requesting definition data.

See also the Data concepts guide.

The from_dbn_file method supports several important parameters:

IMBALANCE and STATISTICS schemas require as_legacy_cython=False as these are PyO3-only types. Setting as_legacy_cython=True will raise a ValueError.

Consolidated schemas aggregate data across multiple venues:

Cost optimization: Avoid subscribing to both TBBO/TCBBO and separate trade subscriptions for the same instrument, as these schemas already include trade data. This prevents duplicates and reduces costs.

The DatabentoDataClient is a Python class which contains other Databento adapter classes. There are two DatabentoLiveClients per Databento dataset:

There is currently a limitation that all MBO (order book deltas) subscriptions for a dataset have to be made at node startup, to then be able to replay data from the beginning of the session. If subsequent subscriptions arrive after start, then an error will be logged (and the subscription ignored).

There is no such limitation for any of the other Databento schemas.

A single DatabentoHistoricalClient instance is reused between the DatabentoInstrumentProvider and DatabentoDataClient, which makes historical instrument definitions and data requests.

The most common use case is to configure a live TradingNode to include a Databento data client. To achieve this, add a DATABENTO section to your client configuration(s):

Then, create a TradingNode and add the client factory:

The Databento data client provides the following configuration options:

We recommend using environment variables to manage your credentials.

For additional features or to contribute to the Databento adapter, please see our contributing guide.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.adapters.databento import DATABENTO_CLIENT_IDfrom nautilus_trader.model import BarTypefrom nautilus_trader.model.enums import BookTypefrom nautilus_trader.model.identifiers import InstrumentId
```

Example 2 (python):
```python
# Default MBP-1 quotes (may include trades)self.subscribe_quote_ticks(instrument_id, client_id=DATABENTO_CLIENT_ID)# Explicit MBP-1 schemaself.subscribe_quote_ticks(    instrument_id=instrument_id,    params={"schema": "mbp-1"},    client_id=DATABENTO_CLIENT_ID,)# 1-second BBO snapshots (quotes only, no trades)self.subscribe_quote_ticks(    instrument_id=instrument_id,    params={"schema": "bbo-1s"},    client_id=DATABENTO_CLIENT_ID,)# Consolidated quotes across venuesself.subscribe_quote_ticks(    instrument_id=instrument_id,    params={"schema": "cbbo-1s"},  # or "cmbp-1" for consolidated MBP    client_id=DATABENTO_CLIENT_ID,)# Trade-sampled BBO (includes both quotes AND trades)self.subscribe_quote_ticks(    instrument_id=instrument_id,    params={"schema": "tbbo"},  # Will receive both QuoteTick and TradeTick onto the message bus    client_id=DATABENTO_CLIENT_ID,)
```

Example 3 (python):
```python
# Trade ticks onlyself.subscribe_trade_ticks(instrument_id, client_id=DATABENTO_CLIENT_ID)# Trades from MBP-1 feed (only when trade events occur)self.subscribe_trade_ticks(    instrument_id=instrument_id,    params={"schema": "mbp-1"},    client_id=DATABENTO_CLIENT_ID,)# Trade-sampled data (includes quotes at trade time)self.subscribe_trade_ticks(    instrument_id=instrument_id,    params={"schema": "tbbo"},  # Also provides quotes at trade events    client_id=DATABENTO_CLIENT_ID,)
```

Example 4 (python):
```python
# Subscribe to top 10 levels of market depthself.subscribe_order_book_depth(    instrument_id=instrument_id,    depth=10  # MBP-10 schema is automatically selected)# The depth parameter must be 10 for Databento# This will receive OrderBookDepth10 updates
```

---

## Binance

**URL:** https://nautilustrader.io/docs/latest/integrations/binance

**Contents:**
- Binance
- Examples​
- Overview​
  - Product support​
- Data types​
- Symbology​
- Order capability​
  - Order types​
  - Execution instructions​
    - Post-only restrictions​

Founded in 2017, Binance is one of the largest cryptocurrency exchanges in terms of daily trading volume, and open interest of crypto assets and crypto derivative products.

This integration supports live market data ingest and order execution for:

You can find live example scripts here.

This guide assumes a trader is setting up for both live market data feeds, and trade execution. The Binance adapter includes multiple components, which can be used together or separately depending on the use case.

Most users will define a configuration for a live trading node (as below), and won't need to necessarily work with these lower level components directly.

Margin trading (cross & isolated) is not implemented at this time. Contributions via GitHub issue #2631 or pull requests to add margin trading functionality are welcome.

To provide complete API functionality to traders, the integration includes several custom data types:

See the Binance API Reference for full definitions.

As per the Nautilus unification policy for symbols, the native Binance symbols are used where possible including for spot assets and futures contracts. Because NautilusTrader is capable of multi-venue + multi-account trading, it's necessary to explicitly clarify the difference between BTCUSDT as the spot and margin traded pair, and the BTCUSDT perpetual futures contract (this symbol is used for both natively by Binance).

Therefore, Nautilus appends the suffix -PERP to all perpetual symbols. E.g. for Binance Futures, the BTCUSDT perpetual futures contract symbol would be BTCUSDT-PERP within the Nautilus system boundary.

The following tables detail the order types, execution instructions, and time-in-force options supported across different Binance account types:

Only limit order types support post_only.

Binance Futures can trigger exchange-generated orders in response to risk events:

The adapter detects these special order types via their client ID patterns and execution type (CALCULATED), then:

This ensures liquidation and ADL events are properly reflected in portfolio state and PnL calculations.

Customize individual orders by supplying a params dictionary when calling Strategy.submit_order. The Binance execution clients currently recognise:

Binance Futures supports BBO (Best Bid/Offer) price matching via the priceMatch parameter, which delegates price selection to the exchange. This feature allows limit orders to dynamically join the order book at optimal prices without manually specifying the exact price level.

When using price_match, you submit a limit order with a reference price (for local risk checks), but Binance determines the actual working price based on the current market state and the selected price match mode.

Valid priceMatch values for Binance Futures:

For more details, see the official documentation.

When an order is submitted with price_match, the following sequence of events occurs:

This ensures that the order price in your system accurately reflects what Binance has accepted, which is critical for position management, risk calculations, and strategy logic.

After submission, if Binance accepts the order at a different price (e.g., 64,995.50), you will receive both an OrderAccepted event followed by an OrderUpdated event with the new price.

For trailing stop market orders on Binance:

Do not use trigger_price for trailing stop orders - it will fail with an error. Use activation_price instead.

Order books can be maintained at full or partial depths depending on the subscription. WebSocket stream throttling is different between Spot and Futures exchanges, Nautilus will use the highest streaming rate possible:

Order books can be maintained at full or partial depths based on the subscription settings. WebSocket stream update rates differ between Spot and Futures exchanges, with Nautilus using the highest available streaming rate:

There is a limitation of one order book per instrument per trader instance. As stream subscriptions may vary, the latest order book data (deltas or snapshots) subscription will be used by the Binance data client.

Order book snapshot rebuilds will be triggered on:

The sequence of events is as follows:

The ts_event field value for QuoteTick objects will differ between Spot and Futures exchanges, where the former does not provide an event timestamp, so the ts_init is used (which means ts_event and ts_init are identical).

It's possible to subscribe to Binance specific data streams as they become available to the adapter over time.

Bars are not considered 'Binance specific' and can be subscribed to in the normal way. As more adapters are built out which need for example mark price and funding rate updates, then these methods may eventually become first-class (not requiring custom/generic subscriptions as below).

You can subscribe to BinanceFuturesMarkPriceUpdate (including funding rating info) data streams by subscribing in the following way from your actor or strategy:

This will result in your actor/strategy passing these received BinanceFuturesMarkPriceUpdate objects to your on_data method. You will need to check the type, as this method acts as a flexible handler for all custom/generic data.

Binance uses an interval-based rate limiting system where request weight is tracked per fixed time window (e.g., every minute resets at :00 seconds). The adapter uses token bucket rate limiters to approximate this behavior, helping to reduce the risk of quota violations while maintaining high throughput for normal trading operations.

Binance assigns request weight dynamically (e.g. /klines scales with limit). The quotas above mirror the static limits but the client still draws a single token per call, so long history pulls may need manual pacing to respect the live X-MBX-USED-WEIGHT-* headers.

Binance returns HTTP 429 when you exceed the allowed weight and repeated bursts can trigger temporary IP bans, so leave enough headroom between batches.

For more details on rate limiting, see the official documentation: https://binance-docs.github.io/apidocs/futures/en/#limits.

The most common use case is to configure a live TradingNode to include Binance data and execution clients. To achieve this, add a BINANCE section to your client configuration(s):

Then, create a TradingNode and add the client factories:

Binance supports multiple cryptographic key types for API authentication:

You can specify the key type in your configuration:

Ed25519 keys must be provided in base64-encoded ASN.1/DER format. The implementation automatically extracts the 32-byte seed from the DER structure.

There are multiple options for supplying your credentials to the Binance clients. Either pass the corresponding values to the configuration objects, or set the following environment variables:

For Binance live clients (shared between Spot/Margin and Futures), you can set:

For Binance Spot/Margin testnet clients, you can set:

For Binance Futures testnet clients, you can set:

When starting the trading node, you'll receive immediate confirmation of whether your credentials are valid and have trading permissions.

All the Binance account types will be supported for live trading. Set the account_type using the BinanceAccountType enum. The account type options are:

We recommend using environment variables to manage your credentials.

It's possible to override the default base URLs for both HTTP Rest and WebSocket APIs. This is useful for configuring API clusters for performance reasons, or when Binance has provided you with specialized endpoints.

There is support for Binance US accounts by setting the us option in the configs to True (this is False by default). All functionality available to US accounts should behave identically to standard Binance.

It's also possible to configure one or both clients to connect to the Binance testnet. Set the testnet option to True (this is False by default):

Binance provides aggregated trade data endpoints as an alternative source of trades. In comparison to the default trade endpoints, aggregated trade data endpoints can return all ticks between a start_time and end_time.

To use aggregated trades and the endpoint features, set the use_agg_trade_ticks option to True (this is False by default.)

Some Binance instruments are unable to be parsed into Nautilus objects if they contain enormous field values beyond what can be handled by the platform. In these cases, a warn and continue approach is taken (the instrument will not be available).

These warnings may cause unnecessary log noise, and so it's possible to configure the provider to not log the warnings, as per the client configuration example below:

Binance Futures Hedge mode is a position mode where a trader opens positions in both long and short directions to mitigate risk and potentially profit from market volatility.

To use Binance Future Hedge mode, you need to follow the three items below:

For additional features or to contribute to the Binance adapter, please see our contributing guide.

**Examples:**

Example 1 (python):
```python
order = strategy.order_factory.limit(    instrument_id=InstrumentId.from_str("BTCUSDT-PERP.BINANCE"),    order_side=OrderSide.BUY,    quantity=Quantity.from_int(1),    price=Price.from_str("65000"),  # Reference price for local risk checks)strategy.submit_order(    order,    params={"price_match": "QUEUE"},)
```

Example 2 (python):
```python
from nautilus_trader.adapters.binance import BinanceFuturesMarkPriceUpdatefrom nautilus_trader.model import DataTypefrom nautilus_trader.model import ClientId# In your `on_start` methodself.subscribe_data(    data_type=DataType(BinanceFuturesMarkPriceUpdate, metadata={"instrument_id": self.instrument.id}),    client_id=ClientId("BINANCE"),)
```

Example 3 (python):
```python
from nautilus_trader.core import Datadef on_data(self, data: Data):    # First check the type of data    if isinstance(data, BinanceFuturesMarkPriceUpdate):        # Do something with the data
```

Example 4 (python):
```python
from nautilus_trader.adapters.binance import BINANCEfrom nautilus_trader.live.node import TradingNodeconfig = TradingNodeConfig(    ...,  # Omitted    data_clients={        BINANCE: {            "api_key": "YOUR_BINANCE_API_KEY",            "api_secret": "YOUR_BINANCE_API_SECRET",            "account_type": "spot",  # {spot, margin, usdt_future, coin_future}            "base_url_http": None,  # Override with custom endpoint            "base_url_ws": None,  # Override with custom endpoint            "us": False,  # If client is for Binance US        },    },    exec_clients={        BINANCE: {            "api_key": "YOUR_BINANCE_API_KEY",            "api_secret": "YOUR_BINANCE_API_SECRET",            "account_type": "spot",  # {spot, margin, usdt_future, coin_future}            "base_url_http": None,  # Override with custom endpoint            "base_url_ws": None,  # Override with custom endpoint            "us": False,  # If client is for Binance US        },    },)
```

---

## BitMEX

**URL:** https://nautilustrader.io/docs/latest/integrations/bitmex

**Contents:**
- BitMEX
- Overview​
- Examples​
- Components​
- BitMEX documentation​
- Product support​
  - Spot trading​
  - Derivatives​
- Symbology​
  - Symbol format​

Founded in 2014, BitMEX (Bitcoin Mercantile Exchange) is a cryptocurrency derivatives trading platform offering spot, perpetual contracts, traditional futures, prediction markets, and other advanced trading products. This integration supports live market data ingest and order execution with BitMEX.

This adapter is implemented in Rust, with optional Python bindings for ease of use in Python-based workflows. It does not require external BitMEX client libraries—the core components are compiled as a static library and linked automatically during the build.

You can find live example scripts here.

This guide assumes a trader is setting up for both live market data feeds, and trade execution. The BitMEX adapter includes multiple components, which can be used together or separately depending on the use case.

Most users will simply define a configuration for a live trading node (as below), and won't need to necessarily work with these lower level components directly.

BitMEX provides extensive documentation for users:

It's recommended you refer to the BitMEX documentation in conjunction with this NautilusTrader integration guide.

BitMEX has discontinued their options products to focus on their core derivatives and spot offerings.

BitMEX uses a specific naming convention for its trading symbols. Understanding this convention is crucial for correctly identifying and trading instruments.

BitMEX symbols typically follow these patterns:

BitMEX uses XBT as the symbol for Bitcoin instead of BTC. This follows the ISO 4217 currency code standard where "X" denotes non-national currencies. XBT and BTC refer to the same asset - Bitcoin.

Futures contracts use standard futures month codes:

Followed by the year (e.g., 24 for 2024, 25 for 2025).

Within NautilusTrader, BitMEX instruments are identified using the native BitMEX symbol directly, combined with the venue identifier:

BitMEX spot symbols in NautilusTrader don't include the slash (/) that appears in the BitMEX UI. Use XBTUSDT instead of XBT/USDT.

BitMEX reports spot and derivative quantities in contract units. The actual asset size per contract is exchange-specific and published on the instrument definition:

For example, the SOL/USDT spot instrument (SOLUSDT) exposes lotSize = 1000 and underlyingToPositionMultiplier = 10000, meaning one contract represents 1 / 10000 = 0.0001 SOL, and the minimum order (lotSize * contract_size) is 0.1 SOL. The adapter now derives the contract size directly from these fields and scales both inbound market data and outbound orders accordingly, so quantities in Nautilus are always expressed in base units (SOL, ETH, etc.).

See the BitMEX API documentation for details on these fields: https://www.bitmex.com/app/apiOverview#Instrument-Properties.

The BitMEX integration supports the following order types and execution features.

Post-only orders that would cross the spread are canceled by BitMEX rather than rejected. The integration surfaces these as rejections with due_post_only=True so strategies can handle them consistently.

BitMEX supports multiple reference prices to evaluate stop/conditional order triggers for:

Choose the trigger type that matches your strategy and/or risk preferences.

ExecTester example configuration also demonstrates setting stop_trigger_type=TriggerType.MARK_PRICE in examples/live/bitmex/bitmex_exec_tester.py.

DAY orders expire at 12:00am UTC, which marks the BitMEX trading day boundary (end of trading hours for that day). See the BitMEX Exchange Rules and API documentation for complete details.

BitMEX caps each REST response at 1,000 rows and requires manual pagination via start/startTime. The current adapter returns only the first page; wider pagination support is scheduled for a future update.

The BitMEX adapter utilizes HTTP keep-alive for optimal performance:

This configuration ensures low-latency communication with BitMEX servers by maintaining persistent connections and avoiding the overhead of establishing new connections for each request.

BitMEX uses an api-expires header for request authentication to prevent replay attacks:

BitMEX implements a dual-layer rate limiting system:

The adapter enforces these quotas automatically and surfaces the rate-limit headers BitMEX returns with each response.

Exceeding BitMEX rate limits returns HTTP 429 and may trigger temporary IP bans; persistent 4xx/5xx errors can extend the lockout period.

The rate limits can be configured if your account has different limits than the defaults:

For more details on rate limiting, see the BitMEX API documentation on rate limits.

Cancel Broadcaster Rate Limit Considerations

The cancel broadcaster (when canceller_pool_size > 1) fans out each cancel request to multiple independent HTTP clients in parallel. Each client maintains its own rate limiter, which means the effective request rate is multiplied by the pool size.

Example: With canceller_pool_size=3 (default) and max_requests_per_second=10, a single cancel operation consumes 3 requests (one per client), potentially reaching 30 requests/second if canceling rapidly.

Since BitMEX enforces rate limits at the account level (not per connection), the broadcaster can push you over the exchange's default limits of 10 req/s burst and 120 req/min rolling window.

Mitigations: Reduce max_requests_per_second and max_requests_per_minute proportionally (divide by canceller_pool_size), or adjust the pool size itself (see Cancel broadcaster configuration). Future versions may support shared rate limiters across the pool.

BitMEX exposes the current allowance via response headers:

The BitMEX execution client includes a cancel broadcaster that provides fault-tolerant order cancellation through parallel request fanout.

Order cancellations are time-critical operations - when a strategy decides to cancel an order, any delay or failure can result in unintended fills, slippage, or unwanted position exposure. The cancel broadcaster addresses this by:

This architecture ensures that a single network path failure or slow connection doesn't block critical cancel operations, improving the reliability of risk management and position control in live trading.

Each HTTP client in the broadcaster pool maintains health metrics:

The broadcaster exposes metrics including total cancels, successful cancels, failed cancels, expected rejects (already canceled orders), and idempotent successes for operational monitoring and debugging.

These metrics can be accessed programmatically via the get_metrics() and get_metrics_async() methods on the CancelBroadcaster instance.

The cancel broadcaster is configured via the execution client configuration:

Example configuration:

For HFT strategies without higher rate limits, consider reducing canceller_pool_size=1 to minimize rate limit consumption. The default pool size of 3 broadcasts each cancel request to 3 parallel HTTP clients for fault tolerance, which consumes 3× the rate limit quota per cancel operation. Single-client mode still benefits from the broadcaster's idempotent success handling but uses standard rate limits.

The broadcaster is automatically started when the execution client connects and stopped when it disconnects. All cancel operations (cancel_order, cancel_all_orders, batch_cancel_orders) are automatically routed through the broadcaster without requiring any changes to strategy code.

BitMEX API credentials can be provided either directly in the configuration or via environment variables:

To generate API keys:

Testnet API endpoints:

The adapter automatically routes requests to the correct endpoints when testnet=True is configured.

The BitMEX data client provides the following configuration options:

The BitMEX execution client provides the following configuration options:

A typical BitMEX configuration for live trading includes both testnet and mainnet options:

The BitMEX execution adapter now maps Nautilus contingent order lists to the exchange's native clOrdLinkID/contingencyType mechanics. When the engine submits ContingencyType::Oco or ContingencyType::Oto orders the adapter will:

This means common bracket flows (entry + stop + take-profit) and multi-leg stop structures can now be managed directly by BitMEX instead of being emulated client-side. When defining strategies, continue to use Nautilus OrderList/ContingencyType abstractions—the adapter handles the required BitMEX wiring automatically.

For additional features or to contribute to the BitMEX adapter, please see our contributing guide.

**Examples:**

Example 1 (python):
```python
from nautilus_trader.model.identifiers import InstrumentId# Spot pairs (note: no slash in the symbol)spot_id = InstrumentId.from_str("XBTUSDT.BITMEX")  # XBT/USDT spoteth_spot_id = InstrumentId.from_str("ETHUSDT.BITMEX")  # ETH/USDT spot# Perpetual contractsperp_id = InstrumentId.from_str("XBTUSD.BITMEX")  # Bitcoin perpetual (inverse)linear_perp_id = InstrumentId.from_str("ETHUSDT.BITMEX")  # Ethereum perpetual (linear)# Futures contract (June 2024)futures_id = InstrumentId.from_str("XBTM24.BITMEX")  # Bitcoin futures expiring June 2024# Prediction market contractsprediction_id = InstrumentId.from_str("P_XBTETFV23.BITMEX")  # Bitcoin ETF SEC approval prediction expiring October 2023
```

Example 2 (python):
```python
from nautilus_trader.model.enums import TriggerTypeorder = self.order_factory.stop_market(    instrument_id=instrument_id,    order_side=order_side,    quantity=qty,    trigger_price=trigger,    trigger_type=TriggerType.MARK_PRICE,  # Use BitMEX Mark Price as reference)
```

Example 3 (python):
```python
from nautilus_trader.adapters.bitmex.config import BitmexExecClientConfigexec_config = BitmexExecClientConfig(    api_key="YOUR_API_KEY",    api_secret="YOUR_API_SECRET",    canceller_pool_size=3,  # Default pool size)
```

Example 4 (python):
```python
from nautilus_trader.adapters.bitmex.config import BitmexDataClientConfigfrom nautilus_trader.adapters.bitmex.config import BitmexExecClientConfig# Using environment variables (recommended)testnet_data_config = BitmexDataClientConfig(    testnet=True,  # API credentials loaded from BITMEX_API_KEY and BITMEX_API_SECRET)# Using explicit credentialsmainnet_data_config = BitmexDataClientConfig(    api_key="YOUR_API_KEY",  # Or use os.getenv("BITMEX_API_KEY")    api_secret="YOUR_API_SECRET",  # Or use os.getenv("BITMEX_API_SECRET")    testnet=False,)mainnet_exec_config = BitmexExecClientConfig(    api_key="YOUR_API_KEY",    api_secret="YOUR_API_SECRET",    testnet=False,)
```

---

## Polymarket

**URL:** https://nautilustrader.io/docs/latest/integrations/polymarket

**Contents:**
- Polymarket
- Installation​
- Examples​
- Binary options ​
- Polymarket documentation​
- Overview​
- USDC.e (PoS)​
- Wallets and accounts​
  - Signature types​
  - Setting allowances for Polymarket contracts​

Founded in 2020, Polymarket is the world’s largest decentralized prediction market platform, enabling traders to speculate on the outcomes of world events by buying and selling binary option contracts using cryptocurrency.

NautilusTrader provides a venue integration for data and execution via Polymarket's Central Limit Order Book (CLOB) API. The integration leverages the official Python CLOB client library to facilitate interaction with the Polymarket platform.

NautilusTrader supports multiple Polymarket signature types for order signing, providing flexibility for different wallet configurations. This integration ensures that traders can execute orders securely and efficiently across various wallet types, while NautilusTrader abstracts the complexity of signing and preparing orders for seamless execution.

To install NautilusTrader with Polymarket support:

To build from source with all extras (including Polymarket):

You can find live example scripts here.

A binary option is a type of financial exotic option contract in which traders bet on the outcome of a yes-or-no proposition. If the prediction is correct, the trader receives a fixed payout; otherwise, they receive nothing.

All assets traded on Polymarket are quoted and settled in USDC.e (PoS), see below for more information.

Polymarket offers comprehensive resources for different audiences:

This guide assumes a trader is setting up for both live market data feeds and trade execution. The Polymarket integration adapter includes multiple components, which can be used together or separately depending on the use case.

Most users will simply define a configuration for a live trading node (as below), and won't need to necessarily work with these lower level components directly.

USDC.e is a bridged version of USDC from Ethereum to the Polygon network, operating on Polygon's Proof of Stake (PoS) chain. This enables faster, more cost-efficient transactions on Polygon while maintaining backing by USDC on Ethereum.

The contract address is 0x2791bca1f2de4661ed88a30c99a7a9449aa84174 on the Polygon blockchain. More information can be found in this blog.

To interact with Polymarket via NautilusTrader, you'll need a Polygon-compatible wallet (such as MetaMask).

Polymarket supports multiple signature types for order signing and verification:

See also: Proxy wallet in the Polymarket documentation for more details about signature types and proxy wallet infrastructure.

NautilusTrader defaults to signature type 0 (EOA) but can be configured to use any of the supported signature types via the signature_type configuration parameter.

A single wallet address is supported per trader instance when using environment variables, or multiple wallets could be configured with multiple PolymarketExecutionClient instances.

Ensure your wallet is funded with USDC.e, otherwise you will encounter the "not enough balance / allowance" API error when submitting orders.

Before you can start trading, you need to ensure that your wallet has allowances set for Polymarket's smart contracts. You can do this by running the provided script located at /adapters/polymarket/scripts/set_allowances.py.

This script is adapted from a gist created by @poly-rodr.

You only need to run this script once per EOA wallet that you intend to use for trading on Polymarket.

This script automates the process of approving the necessary allowances for the Polymarket contracts. It sets approvals for the USDC token and Conditional Token Framework (CTF) contract to allow the Polymarket CLOB Exchange to interact with your funds.

Before running the script, ensure the following prerequisites are met:

Once you have these in place, the script will:

You can also adjust the approval amount in the script instead of using MAX_INT, with the amount specified in fractional units of USDC.e, though this has not been tested.

Ensure that your private key and public key are correctly stored in the environment variables before running the script. Here's an example of how to set the variables in your terminal session:

Run the script using:

The script performs the following actions:

This allows Polymarket to interact with your funds when executing trades and ensures smooth integration with the CLOB Exchange.

To trade with Polymarket, you'll need to generate API credentials. Follow these steps:

Ensure the following environment variables are set:

Run the script using:

The script will generate and print API credentials, which you should save to the following environment variables:

These can then be used for Polymarket client configurations:

When setting up NautilusTrader to work with Polymarket, it’s crucial to properly configure the necessary parameters, particularly the private key.

We recommend using environment variables to manage your credentials.

Polymarket operates as a prediction market with a more limited set of order types and instructions compared to traditional exchanges.

Polymarket interprets order quantities differently depending on the order type and side:

As a result, a market buy order submitted with a base-denominated quantity will execute far more size than intended.

When submitting market BUY orders, set quote_quantity=True (or pre-compute the quote-denominated amount) and configure the execution engine with convert_quote_qty_to_base=False so the quote amount reaches the adapter unchanged. The Polymarket execution client denies base-denominated market buys to prevent unintended fills.

NautilusTrader now forwards market orders to Polymarket's native market-order endpoint, so the quote amount you specify for a BUY is executed directly (no more synthetic max-price limits).

FAK (Fill and Kill) is Polymarket's terminology for Immediate or Cancel (IOC) semantics.

Polymarket enforces different precision constraints based on tick size and order type.

Binary Option instruments typically support up to 6 decimal places for amounts (with 0.0001 tick size), but market orders have stricter precision requirements:

FOK (Fill-or-Kill) market orders:

Regular GTC orders: More flexible precision based on market tick size.

Trades on Polymarket can have the following statuses:

Once a trade is initially matched, subsequent trade status updates will be received via the WebSocket. NautilusTrader records the initial trade details in the info field of the OrderFilled event, with additional trade events stored in the cache as JSON under a custom key to retain this information.

The Polymarket API returns either all active (open) orders or specific orders when queried by the Polymarket order ID (venue_order_id). The execution reconciliation procedure for Polymarket is as follows:

Note: Polymarket does not directly provide data for orders which are no longer active.

An optional execution client configuration, generate_order_history_from_trades, is currently under development. It is not recommended for production use at this time.

The PolymarketWebSocketClient is built on top of the high-performance Nautilus WebSocketClient base class, written in Rust.

The main data WebSocket handles all market channel subscriptions received during the initial connection sequence, up to ws_connection_delay_secs. For any additional subscriptions, a new PolymarketWebSocketClient is created for each new instrument (asset).

The main execution WebSocket manages all user channel subscriptions based on the Polymarket instruments available in the cache during the initial connection sequence. When trading commands are issued for additional instruments, a separate PolymarketWebSocketClient is created for each new instrument (asset).

Polymarket does not support unsubscribing from channel streams once subscribed.

The following limitations and considerations are currently known:

For additional features or to contribute to the Polymarket adapter, please see our contributing guide.

**Examples:**

Example 1 (bash):
```bash
pip install --upgrade "nautilus_trader[polymarket]"
```

Example 2 (bash):
```bash
uv sync --all-extras
```

Example 3 (bash):
```bash
export POLYGON_PRIVATE_KEY="YOUR_PRIVATE_KEY"export POLYGON_PUBLIC_KEY="YOUR_PUBLIC_KEY"
```

Example 4 (bash):
```bash
python nautilus_trader/adapters/polymarket/scripts/set_allowances.py
```

---

## Cache

**URL:** https://nautilustrader.io/docs/latest/api_reference/cache

**Contents:**
- Cache
  - class Cache​
    - account(self, AccountId account_id) → Account​
    - account_for_venue(self, Venue venue) → Account​
    - account_id(self, Venue venue) → AccountId​
    - accounts(self) → list​
    - actor_ids(self) → set​
    - add(self, str key, bytes value) → void​
    - add_account(self, Account account) → void​
    - add_bar(self, Bar bar) → void​

The cache subpackage provides common caching infrastructure.

A running Nautilus system generally uses a single centralized cache which can be accessed by many components.

Cache(CacheDatabaseFacade database: CacheDatabaseFacade | None = None, config: CacheConfig | None = None) -> None

Provides a common object cache for market and execution related data.

Return the account matching the given ID (if found).

Return the account matching the given client ID (if found).

If unique_venue is set, it will be used instead of the provided venue.

Return the account ID for the given venue (if found).

Return all accounts in the cache.

Return all actor IDs.

Add the given general object value to the cache.

The cache is agnostic to what the object actually is (and how it may be serialized), offering maximum flexibility.

Add the given account to the cache.

Add the given bar to the cache.

Add the given bars to the cache.

Add the given currency to the cache.

Add the given funding rate update to the cache.

Add greeks to the cache.

Add the given index price update to the cache.

Add the given instrument to the cache.

Add the given mark price update to the cache.

Add the given order to the cache indexed with the given position ID.

Add the given order book to the cache.

Add the given order list to the cache.

Add the given own order book to the cache.

Add the given position to the cache.

Index the given position ID with the other given IDs.

Add the given quote tick to the cache.

Add the given quotes to the cache.

Add the given synthetic instrument to the cache.

Add the given trade tick to the cache.

Add the given trades to the cache.

Index the given client order ID with the given venue order ID.

Add a yield curve to the cache.

Audit all own order books against open and inflight order indexes.

Ensures closed orders are removed from own order books. This includes both orders tracked in _index_orders_open (ACCEPTED, TRIGGERED, PENDING_*, PARTIALLY_FILLED) and _index_orders_inflight (INITIALIZED, SUBMITTED) to prevent false positives during venue latency windows.

Logs all failures as errors.

Return the bar for the given bar type at the given index (if found).

Last bar if no index specified.

The caches bar capacity.

The count of bars for the given bar type.

Return all bar types with the given query filters.

If a filter parameter is None, then no filtering occurs for that parameter.

Return bars for the given bar type.

The count of order book updates for the given instrument ID.

Will return zero if there is no book for the instrument ID.

Build the cache index from objects currently held in memory.

Clear the current accounts cache and load accounts from the cache database.

Clears and loads the currencies, instruments, synthetics, accounts, orders, and positions. from the cache database.

Clear the current currencies cache and load currencies from the cache database.

Clear the current general cache and load the general objects from the cache database.

Clear the current instruments cache and load instruments from the cache database.

Clear the current order lists cache and load order lists using cached orders.

Clear the current orders cache and load orders from the cache database.

Clear the current positions cache and load positions from the cache database.

Clear the current synthetic instruments cache and load synthetic instruments from the cache database.

Check integrity of data within the cache.

All data should be loaded from the database prior to this call. If an error is found then a log error message will also be produced.

Check for any residual open state and log warnings if any are found.

‘Open state’ is considered to be open orders and open positions.

Clear the exchange rate based on mark price.

Clear the exchange rates based on mark price.

Return the specific execution client ID matching the given client order ID (if found).

Return the client order ID matching the given venue order ID (if found).

Return all client order IDs with the given query filters.

Return all closed client order IDs with the given query filters.

Return all emulated client order IDs with the given query filters.

Return all in-flight client order IDs with the given query filters.

Return all open client order IDs with the given query filters.

Delete the given actor from the cache.

Delete the given strategy from the cache.

Dispose of the cache which will close any underlying database adapter.

Return all execution algorithm IDs.

Return the total filled quantity for the given execution spawn ID (if found).

If no execution spawn ID matches then returns None.

Return the total leaves quantity for the given execution spawn ID (if found).

If no execution spawn ID matches then returns None.

Return the total quantity for the given execution spawn ID (if found).

If no execution spawn ID matches then returns None.

Flush the caches database which permanently removes all persisted data.

Force removal of an order from own order books and clean up all indexes.

This method is used when order.apply() fails and we need to ensure terminal orders are properly cleaned up from own books and all relevant indexes. Replicates the index cleanup that update_order performs for closed orders.

Return the funding rate for the given instrument ID (if found).

Return the general object for the given key.

The cache is agnostic to what the object actually is (and how it may be serialized), offering maximum flexibility.

Return the exchange rate based on mark price.

Will return None if an exchange rate has not been set.

Return the calculated exchange rate.

If the exchange rate cannot be calculated then returns None.

Return the latest cached greeks for the given instrument ID.

If the cache has a database backing.

Return a value indicating whether the cache has bars for the given bar type.

Return a value indicating whether the cache has index prices for the given instrument ID.

Return a value indicating whether the cache has mark prices for the given instrument ID.

Return a value indicating whether the cache has an order book snapshot for the given instrument ID.

Return a value indicating whether the cache has quotes for the given instrument ID.

Return a value indicating whether the cache has trades for the given instrument ID.

Add a heartbeat at the given timestamp.

Return the index price for the given instrument ID at the given index (if found).

Last index price if no index specified.

The count of index prices for the given instrument ID.

Return index prices for the given instrument ID.

Return the instrument corresponding to the given instrument ID.

Return all instrument IDs held by the cache.

Return all instruments held by the cache.

Return a value indicating whether an order with the given ID is closed.

Return a value indicating whether an order with the given ID is emulated.

Return a value indicating whether an order with the given ID is in-flight.

Return a value indicating whether an order with the given ID is open.

Return a value indicating whether an order with the given ID is pending cancel locally.

Return a value indicating whether a position with the given ID exists and is closed.

Return a value indicating whether a position with the given ID exists and is open.

Load the account associated with the given account_id (if found).

Load the state dictionary into the given actor.

Load the instrument associated with the given instrument ID (if found).

Load the order associated with the given ID (if found).

Load the position associated with the given ID (if found).

Load the state dictionary into the given strategy.

Load the synthetic instrument associated with the given instrument_id (if found).

Return the mark price for the given instrument ID at the given index (if found).

Last mark price if no index specified.

The count of mark prices for the given instrument ID.

Return mark prices for the given instrument ID.

Return the order matching the given client order ID (if found).

Return the order book for the given instrument ID (if found).

Return a value indicating whether an order with the given ID exists.

Return the order list matching the given order list ID (if found).

Return a value indicating whether an order list with the given ID exists.

Return all order list IDs.

Return all order lists matching the given query filters.

No particular order of list elements is guaranteed.

Return all orders matching the given query filters.

No particular order of list elements is guaranteed.

Return all closed orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of closed orders with the given query filters.

Return all emulated orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of emulated orders with the given query filters.

Return all execution algorithm orders for the given query filters.

Return all orders for the given execution spawn ID (if found).

Will also include the primary (original) order.

Return all orders for the given position ID.

Return all in-flight orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of in-flight orders with the given query filters.

Return all open orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of open orders with the given query filters.

Return the total count of orders with the given query filters.

Return own ask orders for the given instrument ID (if found).

Return own bid orders for the given instrument ID (if found).

Return the own order book for the given instrument ID (if found).

If account state events are written to the backing database.

Return the position associated with the given ID (if found).

Return all closed position IDs with the given query filters.

Return a value indicating whether a position with the given ID exists.

Return the position associated with the given client order ID (if found).

Return the position ID associated with the given client order ID (if found).

Return all position IDs with the given query filters.

Return all open position IDs with the given query filters.

Return the raw pickled snapshot bytes for the given position ID.

Return all position IDs for position snapshots with the given instrument filter.

Return all position snapshots with the given optional identifier filter.

Return all positions with the given query filters.

No particular order of list elements is guaranteed.

Return all closed positions with the given query filters.

No particular order of list elements is guaranteed.

Return the count of closed positions with the given query filters.

Return all open positions with the given query filters.

No particular order of list elements is guaranteed.

Return the count of open positions with the given query filters.

Return the total count of positions with the given query filters.

Return the price for the given instrument ID and price type.

Return a map of latest prices per instrument ID for the given price type.

Purge all account state events which are outside the lookback window.

Purge all closed orders from the cache.

Purge all closed positions from the cache.

Purge the order for the given client order ID from the cache (if found).

For safety, an order is prevented from being purged if it’s open.

Purge the position for the given position ID from the cache (if found).

For safety, a position is prevented from being purged if it’s open.

Return the quote tick for the given instrument ID at the given index (if found).

Last quote tick if no index specified.

The count of quotes for the given instrument ID.

Return the quotes for the given instrument ID.

All stateful fields are reset to their initial value.

Set the exchange rate based on mark price.

Will also set the inverse xrate automatically.

Set a specific venue that the cache will use for subsequent account_for_venue calls.

Primarily for Interactive Brokers, a multi-venue brokerage where account updates are not tied to a single venue.

Snapshot the state dictionary for the given order.

This method will persist to the backing cache database.

Snapshot the given position in its current state.

The position ID will be appended with a UUID v4 string.

Snapshot the state dictionary for the given position.

This method will persist to the backing cache database.

Return the strategy ID associated with the given ID (if found).

Return the strategy ID associated with the given ID (if found).

Return all strategy IDs.

Return the synthetic instrument corresponding to the given instrument ID.

Return all synthetic instrument IDs held by the cache.

Return all synthetic instruments held by the cache.

The caches tick capacity.

Return the trade tick for the given instrument ID at the given index (if found).

Last trade tick if no index specified.

The count of trades for the given instrument ID.

Return trades for the given instrument ID.

Update the given account in the cache.

Update the given actor state in the cache.

Update the given order in the cache.

Update the given order as pending cancel locally.

Update the own order book for the given order.

Orders without prices (MARKET, etc.) are skipped as they cannot be represented in own books.

Update the given position in the cache.

Update the given strategy state in the cache.

Return the order ID matching the given client order ID (if found).

Return the latest cached yield curve for the given curve name.

Bases: CacheDatabaseFacade

CacheDatabaseAdapter(TraderId trader_id, UUID4 instance_id, Serializer serializer, config: CacheConfig | None = None) -> None

Provides a generic cache database adapter.

Redis can only accurately store int64 types to 17 digits of precision. Therefore nanosecond timestamp int64’s with 19 digits will lose 2 digits of precision when persisted. One way to solve this is to ensure the serializer converts timestamp int64’s to strings on the way into Redis, and converts timestamp strings back to int64’s on the way out. One way to achieve this is to set the timestamps_as_str flag to true for the MsgSpecSerializer, as per the default implementations for both TradingNode and BacktestEngine.

Add the given general object value to the database.

Add the given account to the database.

Add the given currency to the database.

Add the given instrument to the database.

Add the given order to the database.

Add the given position to the database.

Add the given synthetic instrument to the database.

Close the backing database adapter.

Delete the given account event from the database.

Delete the given actor from the database.

Delete the given order from the database.

Delete the given position from the database.

Delete the given strategy from the database.

Flush the database which clears all data.

Add a heartbeat at the given timestamp.

Add an index entry for the given client_order_id to position_id.

Add an index entry for the given venue_order_id to client_order_id.

Return all keys in the database matching the given pattern.

Using the default ‘*’ pattern string can have serious performance implications and can take a long time to execute if many keys exist in the database. This operation can lead to high memory and CPU usage, and should be used with caution, especially in production environments.

Load all general objects from the database using bulk loading for efficiency.

Load the account associated with the given account ID (if found).

Load all accounts from the database.

Load the state for the given actor.

Load all cache data from the database.

Load all currencies from the database using bulk loading for efficiency.

Load the currency associated with the given currency code (if found).

Load the order to execution client index from the database.

Load the order to position index from the database.

Load the instrument associated with the given instrument ID (if found).

Load all instruments from the database using bulk loading for efficiency.

Load the order associated with the given client order ID (if found).

Load all orders from the database.

Load the position associated with the given ID (if found).

Load all positions from the database.

Load the state for the given strategy.

Load the synthetic instrument associated with the given synthetic instrument ID (if found).

Load all synthetic instruments from the database using bulk loading for efficiency.

Snapshot the state of the given order.

Snapshot the state of the given position.

Update the given account in the database.

Update the given actor state in the database.

Update the given order in the database.

Update the given position in the database.

Update the given strategy state in the database.

Cache(CacheDatabaseFacade database: CacheDatabaseFacade | None = None, config: CacheConfig | None = None) -> None

Provides a common object cache for market and execution related data.

Return the account matching the given ID (if found).

Return the account matching the given client ID (if found).

If unique_venue is set, it will be used instead of the provided venue.

Return the account ID for the given venue (if found).

Return all accounts in the cache.

Return all actor IDs.

Add the given general object value to the cache.

The cache is agnostic to what the object actually is (and how it may be serialized), offering maximum flexibility.

Add the given account to the cache.

Add the given bar to the cache.

Add the given bars to the cache.

Add the given currency to the cache.

Add the given funding rate update to the cache.

Add greeks to the cache.

Add the given index price update to the cache.

Add the given instrument to the cache.

Add the given mark price update to the cache.

Add the given order to the cache indexed with the given position ID.

Add the given order book to the cache.

Add the given order list to the cache.

Add the given own order book to the cache.

Add the given position to the cache.

Index the given position ID with the other given IDs.

Add the given quote tick to the cache.

Add the given quotes to the cache.

Add the given synthetic instrument to the cache.

Add the given trade tick to the cache.

Add the given trades to the cache.

Index the given client order ID with the given venue order ID.

Add a yield curve to the cache.

Audit all own order books against open and inflight order indexes.

Ensures closed orders are removed from own order books. This includes both orders tracked in _index_orders_open (ACCEPTED, TRIGGERED, PENDING_*, PARTIALLY_FILLED) and _index_orders_inflight (INITIALIZED, SUBMITTED) to prevent false positives during venue latency windows.

Logs all failures as errors.

Return the bar for the given bar type at the given index (if found).

Last bar if no index specified.

The caches bar capacity.

The count of bars for the given bar type.

Return all bar types with the given query filters.

If a filter parameter is None, then no filtering occurs for that parameter.

Return bars for the given bar type.

The count of order book updates for the given instrument ID.

Will return zero if there is no book for the instrument ID.

Build the cache index from objects currently held in memory.

Clear the current accounts cache and load accounts from the cache database.

Clears and loads the currencies, instruments, synthetics, accounts, orders, and positions. from the cache database.

Clear the current currencies cache and load currencies from the cache database.

Clear the current general cache and load the general objects from the cache database.

Clear the current instruments cache and load instruments from the cache database.

Clear the current order lists cache and load order lists using cached orders.

Clear the current orders cache and load orders from the cache database.

Clear the current positions cache and load positions from the cache database.

Clear the current synthetic instruments cache and load synthetic instruments from the cache database.

Check integrity of data within the cache.

All data should be loaded from the database prior to this call. If an error is found then a log error message will also be produced.

Check for any residual open state and log warnings if any are found.

‘Open state’ is considered to be open orders and open positions.

Clear the exchange rate based on mark price.

Clear the exchange rates based on mark price.

Return the specific execution client ID matching the given client order ID (if found).

Return the client order ID matching the given venue order ID (if found).

Return all client order IDs with the given query filters.

Return all closed client order IDs with the given query filters.

Return all emulated client order IDs with the given query filters.

Return all in-flight client order IDs with the given query filters.

Return all open client order IDs with the given query filters.

Delete the given actor from the cache.

Delete the given strategy from the cache.

Dispose of the cache which will close any underlying database adapter.

Return all execution algorithm IDs.

Return the total filled quantity for the given execution spawn ID (if found).

If no execution spawn ID matches then returns None.

Return the total leaves quantity for the given execution spawn ID (if found).

If no execution spawn ID matches then returns None.

Return the total quantity for the given execution spawn ID (if found).

If no execution spawn ID matches then returns None.

Flush the caches database which permanently removes all persisted data.

Force removal of an order from own order books and clean up all indexes.

This method is used when order.apply() fails and we need to ensure terminal orders are properly cleaned up from own books and all relevant indexes. Replicates the index cleanup that update_order performs for closed orders.

Return the funding rate for the given instrument ID (if found).

Return the general object for the given key.

The cache is agnostic to what the object actually is (and how it may be serialized), offering maximum flexibility.

Return the exchange rate based on mark price.

Will return None if an exchange rate has not been set.

Return the calculated exchange rate.

If the exchange rate cannot be calculated then returns None.

Return the latest cached greeks for the given instrument ID.

If the cache has a database backing.

Return a value indicating whether the cache has bars for the given bar type.

Return a value indicating whether the cache has index prices for the given instrument ID.

Return a value indicating whether the cache has mark prices for the given instrument ID.

Return a value indicating whether the cache has an order book snapshot for the given instrument ID.

Return a value indicating whether the cache has quotes for the given instrument ID.

Return a value indicating whether the cache has trades for the given instrument ID.

Add a heartbeat at the given timestamp.

Return the index price for the given instrument ID at the given index (if found).

Last index price if no index specified.

The count of index prices for the given instrument ID.

Return index prices for the given instrument ID.

Return the instrument corresponding to the given instrument ID.

Return all instrument IDs held by the cache.

Return all instruments held by the cache.

Return a value indicating whether an order with the given ID is closed.

Return a value indicating whether an order with the given ID is emulated.

Return a value indicating whether an order with the given ID is in-flight.

Return a value indicating whether an order with the given ID is open.

Return a value indicating whether an order with the given ID is pending cancel locally.

Return a value indicating whether a position with the given ID exists and is closed.

Return a value indicating whether a position with the given ID exists and is open.

Load the account associated with the given account_id (if found).

Load the state dictionary into the given actor.

Load the instrument associated with the given instrument ID (if found).

Load the order associated with the given ID (if found).

Load the position associated with the given ID (if found).

Load the state dictionary into the given strategy.

Load the synthetic instrument associated with the given instrument_id (if found).

Return the mark price for the given instrument ID at the given index (if found).

Last mark price if no index specified.

The count of mark prices for the given instrument ID.

Return mark prices for the given instrument ID.

Return the order matching the given client order ID (if found).

Return the order book for the given instrument ID (if found).

Return a value indicating whether an order with the given ID exists.

Return the order list matching the given order list ID (if found).

Return a value indicating whether an order list with the given ID exists.

Return all order list IDs.

Return all order lists matching the given query filters.

No particular order of list elements is guaranteed.

Return all orders matching the given query filters.

No particular order of list elements is guaranteed.

Return all closed orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of closed orders with the given query filters.

Return all emulated orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of emulated orders with the given query filters.

Return all execution algorithm orders for the given query filters.

Return all orders for the given execution spawn ID (if found).

Will also include the primary (original) order.

Return all orders for the given position ID.

Return all in-flight orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of in-flight orders with the given query filters.

Return all open orders with the given query filters.

No particular order of list elements is guaranteed.

Return the count of open orders with the given query filters.

Return the total count of orders with the given query filters.

Return own ask orders for the given instrument ID (if found).

Return own bid orders for the given instrument ID (if found).

Return the own order book for the given instrument ID (if found).

If account state events are written to the backing database.

Return the position associated with the given ID (if found).

Return all closed position IDs with the given query filters.

Return a value indicating whether a position with the given ID exists.

Return the position associated with the given client order ID (if found).

Return the position ID associated with the given client order ID (if found).

Return all position IDs with the given query filters.

Return all open position IDs with the given query filters.

Return the raw pickled snapshot bytes for the given position ID.

Return all position IDs for position snapshots with the given instrument filter.

Return all position snapshots with the given optional identifier filter.

Return all positions with the given query filters.

No particular order of list elements is guaranteed.

Return all closed positions with the given query filters.

No particular order of list elements is guaranteed.

Return the count of closed positions with the given query filters.

Return all open positions with the given query filters.

No particular order of list elements is guaranteed.

Return the count of open positions with the given query filters.

Return the total count of positions with the given query filters.

Return the price for the given instrument ID and price type.

Return a map of latest prices per instrument ID for the given price type.

Purge all account state events which are outside the lookback window.

Purge all closed orders from the cache.

Purge all closed positions from the cache.

Purge the order for the given client order ID from the cache (if found).

For safety, an order is prevented from being purged if it’s open.

Purge the position for the given position ID from the cache (if found).

For safety, a position is prevented from being purged if it’s open.

Return the quote tick for the given instrument ID at the given index (if found).

Last quote tick if no index specified.

The count of quotes for the given instrument ID.

Return the quotes for the given instrument ID.

All stateful fields are reset to their initial value.

Set the exchange rate based on mark price.

Will also set the inverse xrate automatically.

Set a specific venue that the cache will use for subsequent account_for_venue calls.

Primarily for Interactive Brokers, a multi-venue brokerage where account updates are not tied to a single venue.

Snapshot the state dictionary for the given order.

This method will persist to the backing cache database.

Snapshot the given position in its current state.

The position ID will be appended with a UUID v4 string.

Snapshot the state dictionary for the given position.

This method will persist to the backing cache database.

Return the strategy ID associated with the given ID (if found).

Return the strategy ID associated with the given ID (if found).

Return all strategy IDs.

Return the synthetic instrument corresponding to the given instrument ID.

Return all synthetic instrument IDs held by the cache.

Return all synthetic instruments held by the cache.

The caches tick capacity.

Return the trade tick for the given instrument ID at the given index (if found).

Last trade tick if no index specified.

The count of trades for the given instrument ID.

Return trades for the given instrument ID.

Update the given account in the cache.

Update the given actor state in the cache.

Update the given order in the cache.

Update the given order as pending cancel locally.

Update the own order book for the given order.

Orders without prices (MARKET, etc.) are skipped as they cannot be represented in own books.

Update the given position in the cache.

Update the given strategy state in the cache.

Return the order ID matching the given client order ID (if found).

Return the latest cached yield curve for the given curve name.

Bases: CacheDatabaseFacade

CacheDatabaseAdapter(TraderId trader_id, UUID4 instance_id, Serializer serializer, config: CacheConfig | None = None) -> None

Provides a generic cache database adapter.

Redis can only accurately store int64 types to 17 digits of precision. Therefore nanosecond timestamp int64’s with 19 digits will lose 2 digits of precision when persisted. One way to solve this is to ensure the serializer converts timestamp int64’s to strings on the way into Redis, and converts timestamp strings back to int64’s on the way out. One way to achieve this is to set the timestamps_as_str flag to true for the MsgSpecSerializer, as per the default implementations for both TradingNode and BacktestEngine.

Add the given general object value to the database.

Add the given account to the database.

Add the given currency to the database.

Add the given instrument to the database.

Add the given order to the database.

Add the given position to the database.

Add the given synthetic instrument to the database.

Close the backing database adapter.

Delete the given account event from the database.

Delete the given actor from the database.

Delete the given order from the database.

Delete the given position from the database.

Delete the given strategy from the database.

Flush the database which clears all data.

Add a heartbeat at the given timestamp.

Add an index entry for the given client_order_id to position_id.

Add an index entry for the given venue_order_id to client_order_id.

Return all keys in the database matching the given pattern.

Using the default ‘*’ pattern string can have serious performance implications and can take a long time to execute if many keys exist in the database. This operation can lead to high memory and CPU usage, and should be used with caution, especially in production environments.

Load all general objects from the database using bulk loading for efficiency.

Load the account associated with the given account ID (if found).

Load all accounts from the database.

Load the state for the given actor.

Load all cache data from the database.

Load all currencies from the database using bulk loading for efficiency.

Load the currency associated with the given currency code (if found).

Load the order to execution client index from the database.

Load the order to position index from the database.

Load the instrument associated with the given instrument ID (if found).

Load all instruments from the database using bulk loading for efficiency.

Load the order associated with the given client order ID (if found).

Load all orders from the database.

Load the position associated with the given ID (if found).

Load all positions from the database.

Load the state for the given strategy.

Load the synthetic instrument associated with the given synthetic instrument ID (if found).

Load all synthetic instruments from the database using bulk loading for efficiency.

Snapshot the state of the given order.

Snapshot the state of the given position.

Update the given account in the database.

Update the given actor state in the database.

Update the given order in the database.

Update the given position in the database.

Update the given strategy state in the database.

Provides a read-only facade for the common Cache.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

---

## Packaged Data

**URL:** https://nautilustrader.io/docs/latest/developer_guide/packaged_data

**Contents:**
- Packaged Data
- Libor rates​
- Short term interest rates​
- Economic events​

Various data is contained internally in the tests/test_kit/data folder.

The libor rates for 1 month USD can be updated by downloading the CSV data from https://fred.stlouisfed.org/series/USD1MTD156N.

Ensure you select Max for the time window.

The interbank short term interest rates can be updated by downloading the CSV data at https://data.oecd.org/interest/short-term-interest-rates.htm.

The economic events can be updated from downloading the CSV data from fxstreet https://www.fxstreet.com/economic-calendar.

Ensure timezone is set to GMT.

A maximum 3 month range can be filtered and so yearly quarters must be downloaded manually and stitched together into a single CSV. Use the calendar icon to filter the data in the following way;

---

## Data

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/data

**Contents:**
- Data
  - class Bar​
    - bar_type​
    - close​
    - static from_dict(dict values) → Bar​
    - static from_pyo3(pyo3_bar) → Bar​
    - static from_pyo3_list(list pyo3_bars) → list[Bar]​
    - static from_raw(BarType bar_type, PriceRaw open, PriceRaw high, PriceRaw low, PriceRaw close, uint8_t price_prec, QuantityRaw volume, uint8_t size_prec, uint64_t ts_event, uint64_t ts_init) → Bar​
    - static from_raw_arrays_to_list(BarType bar_type, uint8_t price_prec, uint8_t size_prec, double[:] opens, double[:] highs, double[:] lows, double[:] closes, double[:] volumes, uint64_t[:] ts_events, uint64_t[:] ts_inits) → list[Bar]​
    - classmethod fully_qualified_name(cls) → str​

Bar(BarType bar_type, Price open, Price high, Price low, Price close, Quantity volume, uint64_t ts_event, uint64_t ts_init, bool is_revision=False) -> None

Represents an aggregated bar.

Return the bar type of bar.

Return the close price of the bar.

Return a bar parsed from the given values.

Return a legacy Cython bar converted from the given pyo3 Rust object.

Return legacy Cython bars converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

Return the high price of the bar.

If this bar is a revision for a previous bar with the same ts_event.

Determine if the current class is a signal type, optionally checking for a specific signal name.

If the OHLC are all equal to a single price.

Return the low price of the bar.

Return the open price of the bar.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust bars converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the volume of the bar.

Returns self, the complex conjugate of any int.

Number of bits necessary to represent self in binary.

Number of ones in the binary representation of the absolute value of self.

Also known as the population count.

Return an array of bytes representing an integer.

length : Length of bytes object to use. An OverflowError is raised if the integer is not representable with the given number of bytes. Default is length 1.

byteorder : The byte order used to represent the integer. If byteorder is ‘big’, the most significant byte is at the beginning of the byte array. If byteorder is ‘little’, the most significant byte is at the end of the byte array. To request the native byte order of the host system, use sys.byteorder as the byte order value. Default is to use ‘big’.

signed : Determines whether two’s complement is used to represent the integer. If signed is False and a negative integer is given, an OverflowError is raised.

Return the integer represented by the given array of bytes.

bytes : Holds the array of bytes to convert. The argument must either support the buffer protocol or be an iterable object producing bytes. Bytes and bytearray are examples of built-in objects that support the buffer protocol.

byteorder : The byte order used to represent the integer. If byteorder is ‘big’, the most significant byte is at the beginning of the byte array. If byteorder is ‘little’, the most significant byte is at the end of the byte array. To request the native byte order of the host system, use sys.byteorder as the byte order value. Default is to use ‘big’.

signed : Indicates whether two’s complement is used to represent the integer.

Return a pair of integers, whose ratio is equal to the original int.

The ratio is in lowest terms and has a positive denominator.

Returns True. Exists for duck type compatibility with float.is_integer.

the real part of a complex number

the imaginary part of a complex number

the numerator of a rational number in lowest terms

the denominator of a rational number in lowest terms

Returns self, the complex conjugate of any int.

Number of bits necessary to represent self in binary.

Number of ones in the binary representation of the absolute value of self.

Also known as the population count.

Return an array of bytes representing an integer.

length : Length of bytes object to use. An OverflowError is raised if the integer is not representable with the given number of bytes. Default is length 1.

byteorder : The byte order used to represent the integer. If byteorder is ‘big’, the most significant byte is at the beginning of the byte array. If byteorder is ‘little’, the most significant byte is at the end of the byte array. To request the native byte order of the host system, use sys.byteorder as the byte order value. Default is to use ‘big’.

signed : Determines whether two’s complement is used to represent the integer. If signed is False and a negative integer is given, an OverflowError is raised.

Return the integer represented by the given array of bytes.

bytes : Holds the array of bytes to convert. The argument must either support the buffer protocol or be an iterable object producing bytes. Bytes and bytearray are examples of built-in objects that support the buffer protocol.

byteorder : The byte order used to represent the integer. If byteorder is ‘big’, the most significant byte is at the beginning of the byte array. If byteorder is ‘little’, the most significant byte is at the end of the byte array. To request the native byte order of the host system, use sys.byteorder as the byte order value. Default is to use ‘big’.

signed : Indicates whether two’s complement is used to represent the integer.

Return a pair of integers, whose ratio is equal to the original int.

The ratio is in lowest terms and has a positive denominator.

Returns True. Exists for duck type compatibility with float.is_integer.

the real part of a complex number

the imaginary part of a complex number

the numerator of a rational number in lowest terms

the denominator of a rational number in lowest terms

BarSpecification(int step, BarAggregation aggregation, PriceType price_type) -> None

Represents a bar aggregation specification that defines how market data should be aggregated into bars (candlesticks).

A bar specification consists of three main components:

Bar specifications are used to define different types of bars:

Time-based bars: Aggregate data over fixed time intervals

Tick-based bars: Aggregate data after a certain number of ticks

Volume-based bars: Aggregate data after a certain volume threshold

Value-based bars: Aggregate data after a certain dollar value threshold

Information-based bars: Advanced aggregation based on information flow

The specification determines:

Return the aggregation for the specification.

Check if the given aggregation is an information-based aggregation type.

Information-based aggregation creates bars based on market microstructure patterns and sequential runs of similar market events. These bars capture information flow and market efficiency patterns by detecting sequences of directionally similar price movements or trading activity.

Information-based aggregation types include:

Runs are sequences of consecutive events with the same directional property (e.g., consecutive upticks or downticks). This aggregation method is useful for analyzing market microstructure, information flow, and detecting patterns in high-frequency trading activity.

This differs from time-based aggregation (fixed intervals) and threshold-based aggregation (activity levels), focusing instead on sequential patterns and information content of market events.

Check if the given aggregation is a threshold-based aggregation type.

Threshold-based aggregation creates bars when accumulated market activity reaches predefined thresholds, providing activity-driven sampling rather than time-driven sampling. These bars capture market dynamics based on actual trading patterns and volumes.

Threshold-based aggregation types include:

This differs from time-based aggregation which creates bars at fixed time intervals, and information-based aggregation which creates bars based on market microstructure patterns and runs.

Check if the given aggregation is a time-based aggregation type.

Time-based aggregation creates bars at fixed time intervals, where each bar represents market data for a specific time period. These bars are emitted when the time interval expires, regardless of trading activity level.

Time-based aggregation types include:

This is distinct from threshold-based aggregation (TICK, VOLUME, VALUE) which creates bars when activity thresholds are reached, and information-based aggregation (RUNS) which creates bars based on market microstructure patterns.

Return a bar specification parsed from the given string.

Parameters: value (str) – The bar specification string to parse.

Return type: BarSpecification

Raises: ValueError – If value is not a valid string.

Return a bar specification parsed from the given timedelta and price_type.

Return type: BarSpecification

Raises: ValueError – If duration is not rounded step of aggregation.

Return the interval length in nanoseconds for time-based bar specifications.

Converts the bar specification’s time interval to nanoseconds based on its aggregation type and step size. This method is used for time calculations and (TODO: bar alignment).

Return a value indicating whether the aggregation method is information-driven.

Information-based aggregation creates bars based on market microstructure patterns and sequential runs of similar market events. This aggregation method captures information flow, market efficiency patterns, and the sequential nature of trading activity by detecting directional runs.

Information-based aggregation types supported:

A “run” is a sequence of consecutive market events with the same directional or categorical property. For example, a tick run might be 5 consecutive upticks followed by 3 consecutive downticks.

Information-based bars are ideal for:

This differs from time-based aggregation (fixed time intervals) and threshold-based aggregation (activity levels), focusing instead on the sequential information content and patterns within market events.

Get timedelta for time-based bars:

Return a value indicating whether the aggregation method is threshold-based.

Threshold-based aggregation types trigger bar creation when cumulative activity reaches predefined levels, making them ideal for volume and value-driven analysis rather than time-based intervals.

Threshold-Based Aggregation Types

Activity threshold types supported:

Imbalance threshold types supported:

Threshold-based bars are ideal for:

This differs from time-based aggregation (fixed time intervals) and information-based aggregation (information content patterns), focusing instead on measurable activity and participation thresholds.

check_threshold_aggregated : Static method for threshold aggregation checking

is_time_aggregated : Check for time-based aggregation

is_information_aggregated : Check for information-based aggregation

Return a value indicating whether the aggregation method is time-driven.

Time-based aggregation creates bars at fixed time intervals based on calendar or clock time, providing consistent temporal sampling of market data. Each bar covers a specific time period regardless of trading activity level.

Time-based aggregation types supported:

Time-based bars are ideal for:

This differs from threshold aggregation (volume/tick-based) which creates bars when activity levels are reached, and information aggregation which creates bars based on market microstructure patterns.

is_threshold_aggregated : Check for threshold-based aggregation

is_information_aggregated : Check for information-based aggregation

Return the price type for the specification.

Return the step size for the specification.

Return the timedelta for the specification.

BarType(InstrumentId instrument_id, BarSpecification bar_spec, AggregationSource aggregation_source=AggregationSource.EXTERNAL) -> None

Represents a bar type including the instrument ID, bar specification and aggregation source.

Return the aggregation source for the bar type.

Return a bar type parsed from the given string.

Return the instrument ID for the bar type.

Return a value indicating whether the bar type corresponds to BarType::Composite in Rust.

Return a value indicating whether the bar aggregation source is EXTERNAL.

Return a value indicating whether the bar aggregation source is INTERNAL.

Return a value indicating whether the bar type corresponds to BarType::Standard in Rust.

Return the specification for the bar type.

BookOrder(OrderSide side, Price price, Quantity size, uint64_t order_id) -> None

Represents an order in a book.

Return the total exposure for this order (price * size).

Return an order from the given dict values.

Return an book order from the given raw values.

Return the book orders side.

Return the book orders price.

Return the book orders side.

Return the signed size of the order (negative for SELL).

Return the book orders size.

Return a dictionary representation of this object.

CustomData(DataType data_type, Data data) -> None

Provides a wrapper for custom data which includes data type information.

Return the fully qualified name for the Data class.

Determine if the current class is a signal type, optionally checking for a specific signal name.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

DataType(type type, dict metadata=None) -> None

Represents a data type including metadata.

This class may be used as a key in hash maps throughout the system, thus the key and value contents of metadata must themselves be hashable.

The data types metadata.

The data types topic string.

The Data type of the data.

FundingRateUpdate(InstrumentId instrument_id, rate, uint64_t ts_event, uint64_t ts_init, next_funding_ns=None) -> None

Represents a funding rate update for a perpetual swap instrument.

Return a funding rate update from the given dict values.

Return a legacy Cython funding rate update converted from the given pyo3 Rust object.

Return legacy Cython funding rate updates converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

The instrument ID for the funding rate.

Determine if the current class is a signal type, optionally checking for a specific signal name.

UNIX timestamp (nanoseconds) of the next funding payment (if available, otherwise zero).

The current funding rate.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

IndexPriceUpdate(InstrumentId instrument_id, Price value, uint64_t ts_event, uint64_t ts_init) -> None

Represents an index price update.

Return an index price from the given dict values.

Return a legacy Cython index price converted from the given pyo3 Rust object.

Return legacy Cython index prices converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

Return the instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust index prices converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

InstrumentClose(InstrumentId instrument_id, Price close_price, InstrumentCloseType close_type, uint64_t ts_event, uint64_t ts_init) -> None

Represents an instrument close at a venue.

The instrument close price.

The instrument close type.

Return an instrument close price event from the given dict values.

Return a legacy Cython instrument close converted from the given pyo3 Rust object.

Return legacy Cython instrument closes converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

The event instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust index prices converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the instance was created.

InstrumentStatus(InstrumentId instrument_id, MarketStatusAction action, uint64_t ts_event, uint64_t ts_init, str reason=None, str trading_event=None, is_trading: bool | None = None, is_quoting: bool | None = None, is_short_sell_restricted: bool | None = None) -> None

Represents an event that indicates a change in an instrument market status.

The instrument market status action.

Return an instrument status update from the given dict values.

Return a legacy Cython quote tick converted from the given pyo3 Rust object.

Return legacy Cython instrument status converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

Return the state of quoting in the instrument (if known).

Return the state of short sell restrictions for the instrument (if known and applicable).

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return the state of trading in the instrument (if known).

Additional details about the cause of the status change.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Further information about the status change (if provided).

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the instance was created.

MarkPriceUpdate(InstrumentId instrument_id, Price value, uint64_t ts_event, uint64_t ts_init) -> None

Represents a mark price update.

Return a mark price from the given dict values.

Return a legacy Cython mark price converted from the given pyo3 Rust object.

Return legacy Cython trades converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

Return the instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust mark prices converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

OrderBookDelta(InstrumentId instrument_id, BookAction action, BookOrder order: BookOrder | None, uint8_t flags, uint64_t sequence, uint64_t ts_event, uint64_t ts_init) -> None

Represents a single update/difference on an OrderBook.

Return the deltas book action {ADD, UPDATE, DELETE, CLEAR}

Return an order book delta which acts as an initial CLEAR.

Return the flags for the delta.

Return an order book delta from the given dict values.

Return a legacy Cython order book delta converted from the given pyo3 Rust object.

Return legacy Cython order book deltas converted from the given pyo3 Rust objects.

Return an order book delta from the given raw values.

Return the fully qualified name for the Data class.

Return the deltas book instrument ID.

If the deltas book action is an ADD.

If the deltas book action is a CLEAR.

If the deltas book action is a DELETE.

Determine if the current class is a signal type, optionally checking for a specific signal name.

If the deltas book action is an UPDATE.

Return the deltas book order for the action.

Return the sequence number for the delta.

Return a dictionary representation of this object.

Return pyo3 Rust order book deltas converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

OrderBookDeltas(InstrumentId instrument_id, list deltas) -> None

Represents a batch of OrderBookDelta updates for an OrderBook.

Groups the given list of OrderBookDelta records into batches, creating OrderBookDeltas objects when an F_LAST flag is encountered.

The method iterates through the data list and appends each OrderBookDelta to the current batch. When an F_LAST flag is found, it indicates the end of a batch. The batch is then appended to the list of completed batches and a new batch is started.

UserWarning : If there are remaining deltas in the final batch after the last F_LAST flag.

Return the contained deltas.

Return the flags for the last delta.

Return order book deltas from the given dict values.

Return the fully qualified name for the Data class.

Return the deltas book instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

If the deltas is a snapshot.

Return the sequence number for the last delta.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

OrderBookDepth10(InstrumentId instrument_id, list bids, list asks, list bid_counts, list ask_counts, uint8_t flags, uint64_t sequence, uint64_t ts_event, uint64_t ts_init) -> None

Represents a self-contained order book update with a fixed depth of 10 levels per side.

Return the count of ask orders level for the update.

Return the ask orders for the update.

Return the count of bid orders per level for the update.

Return the bid orders for the update.

Return the flags for the depth update.

Return order book depth from the given dict values.

Return a legacy Cython order book depth converted from the given pyo3 Rust object.

Return legacy Cython order book depths converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

Return the depth updates book instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return the sequence number for the depth update.

Return a dictionary representation of this object.

Return a QuoteTick created from the top of book levels.

Returns None when the top-of-book bid or ask is missing or invalid (NULL order or zero size).

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

QuoteTick(InstrumentId instrument_id, Price bid_price, Price ask_price, Quantity bid_size, Quantity ask_size, uint64_t ts_event, uint64_t ts_init) -> None

Represents a single quote tick in a market.

Contains information about the best top-of-book bid and ask.

Return the top-of-book ask price.

Return the top-of-book ask size.

Return the top-of-book bid price.

Return the top-of-book bid size.

Extract the price for the given price type.

Extract the size for the given price type.

Return a quote tick parsed from the given values.

Return a legacy Cython quote tick converted from the given pyo3 Rust object.

Return legacy Cython quotes converted from the given pyo3 Rust objects.

Return a quote tick from the given raw values.

Return the fully qualified name for the Data class.

Return the tick instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust quotes converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

TradeTick(InstrumentId instrument_id, Price price, Quantity size, AggressorSide aggressor_side, TradeId trade_id, uint64_t ts_event, uint64_t ts_init) -> None

Represents a single trade tick in a market.

Contains information about a single unique trade which matched buyer and seller counterparties.

Return the ticks aggressor side.

Return a trade tick from the given dict values.

Return a legacy Cython trade tick converted from the given pyo3 Rust object.

Return legacy Cython trades converted from the given pyo3 Rust objects.

Return a trade tick from the given raw values.

Return the fully qualified name for the Data class.

Return the ticks instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return the ticks price.

Return the ticks size.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust trades converted from the given legacy Cython objects.

Return the ticks trade match ID.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

**Examples:**

Example 1 (pycon):
```pycon
>>> bin(37)'0b100101'>>> (37).bit_length()6
```

Example 2 (pycon):
```pycon
>>> bin(13)'0b1101'>>> (13).bit_count()3
```

Example 3 (pycon):
```pycon
>>> (10).as_integer_ratio()(10, 1)>>> (-10).as_integer_ratio()(-10, 1)>>> (0).as_integer_ratio()(0, 1)
```

Example 4 (pycon):
```pycon
>>> bin(37)'0b100101'>>> (37).bit_length()6
```

---

## dYdX

**URL:** https://nautilustrader.io/docs/latest/integrations/dydx

**Contents:**
- dYdX
- Installation​
- Examples​
- Overview​
- Troubleshooting​
  - StatusCode.NOT_FOUND — account … /0 not found​
- Symbology​
- Short-term and long-term orders​
- Market orders​
- Stop limit and stop market orders​

dYdX is one of the largest decentralized cryptocurrency exchanges in terms of daily trading volume for crypto derivative products. dYdX runs on smart contracts on the Ethereum blockchain, and allows users to trade with no intermediaries. This integration supports live market data ingestion and order execution with dYdX v4, which is the first version of the protocol to be fully decentralized with no central components.

To install NautilusTrader with dYdX support:

To build from source with all extras (including dYdX):

You can find live example scripts here.

This guide assumes a trader is setting up for both live market data feeds, and trade execution. The dYdX adapter includes multiple components, which can be used together or separately depending on the use case.

Most users will simply define a configuration for a live trading node (as below), and won't need to necessarily work with these lower level components directly.

A dYdX v4 trading account (sub-account 0) is created only after the wallet’s first deposit or trade. Until then, every gRPC/Indexer query returns NOT_FOUND, so DYDXExecutionClient.connect() fails.

Action → Before starting a live TradingNode, send any positive amount of USDC (≥ 1 wei) or other supported collateral from the same wallet on the same network (mainnet / testnet). Once the transaction has finalised (a few blocks) restart the node; the client will connect cleanly.

Cause The wallet/sub-account has never been funded and therefore does not yet exist on-chain.

In unattended deployments, wrap the connect() call in an exponential-backoff loop so the client retries until the deposit appears.

Only perpetual contracts are available on dYdX. To be consistent with other adapters and to be futureproof in case other products become available on dYdX, NautilusTrader appends -PERP for all available perpetual symbols. For example, the Bitcoin/USD-C perpetual futures contract is identified as BTC-USD-PERP. The quote currency for all markets is USD-C. Therefore, dYdX abbreviates it to USD.

dYdX makes a distinction between short-term orders and long-term orders (or stateful orders). Short-term orders are meant to be placed immediately and belongs in the same block the order was received. These orders stay in-memory up to 20 blocks, with only their fill amount and expiry block height being committed to state. Short-term orders are mainly intended for use by market makers with high throughput or for market orders.

By default, all orders are sent as short-term orders. To construct long-term orders, you can attach a tag to an order like this:

To specify the number of blocks that an order is active:

Market orders require specifying a price to for price slippage protection and use hidden orders. By setting a price for a market order, you can limit the potential price slippage. For example, if you set the price of $100 for a market buy order, the order will only be executed if the market price is at or below $100. If the market price is above $100, the order will not be executed.

Some exchanges, including dYdX, support hidden orders. A hidden order is an order that is not visible to other market participants, but is still executable. By setting a price for a market order, you can create a hidden order that will only be executed if the market price reaches the specified price.

If the market price is not specified, a default value of 0 is used.

To specify the price when creating a market order:

Both stop limit and stop market conditional orders can be submitted. dYdX only supports long-term orders for conditional orders.

dYdX supports perpetual futures trading with a comprehensive set of order types and execution features.

dYdX classifies orders as either short-term or long-term orders:

The product types for each client must be specified in the configurations.

The account type must be a margin account to trade the perpetual futures contracts.

The most common use case is to configure a live TradingNode to include dYdX data and execution clients. To achieve this, add a DYDX section to your client configuration(s):

Then, create a TradingNode and add the client factories:

There are two options for supplying your credentials to the dYdX clients. Either pass the corresponding wallet_address and mnemonic values to the configuration objects, or set the following environment variables:

For dYdX live clients, you can set:

For dYdX testnet clients, you can set:

We recommend using environment variables to manage your credentials.

The data client is using the wallet address to determine the trading fees. The trading fees are used during back tests only.

It's also possible to configure one or both clients to connect to the dYdX testnet. Simply set the is_testnet option to True (this is False by default):

Some dYdX instruments are unable to be parsed into Nautilus objects if they contain enormous field values beyond what can be handled by the platform. In these cases, a warn and continue approach is taken (the instrument will not be available).

Order books can be maintained at full depth or top-of-book quotes depending on the subscription. The venue does not provide quotes, but the adapter subscribes to order book deltas and sends new quotes to the DataEngine when there is a top-of-book price or size change.

For additional features or to contribute to the dYdX adapter, please see our contributing guide.

**Examples:**

Example 1 (bash):
```bash
pip install --upgrade "nautilus_trader[dydx]"
```

Example 2 (bash):
```bash
uv sync --all-extras
```

Example 3 (python):
```python
from nautilus_trader.adapters.dydx import DYDXOrderTagsorder: LimitOrder = self.order_factory.limit(    instrument_id=self.instrument_id,    order_side=OrderSide.BUY,    quantity=self.instrument.make_qty(self.trade_size),    price=self.instrument.make_price(price),    time_in_force=TimeInForce.GTD,    expire_time=self.clock.utc_now() + pd.Timedelta(minutes=10),    post_only=True,    emulation_trigger=self.emulation_trigger,    tags=[DYDXOrderTags(is_short_term_order=False).value],)
```

Example 4 (python):
```python
from nautilus_trader.adapters.dydx import DYDXOrderTagsorder: LimitOrder = self.order_factory.limit(    instrument_id=self.instrument_id,    order_side=OrderSide.BUY,    quantity=self.instrument.make_qty(self.trade_size),    price=self.instrument.make_price(price),    time_in_force=TimeInForce.GTD,    expire_time=self.clock.utc_now() + pd.Timedelta(seconds=5),    post_only=True,    emulation_trigger=self.emulation_trigger,    tags=[DYDXOrderTags(is_short_term_order=True, num_blocks_open=5).value],)
```

---

## Data

**URL:** https://nautilustrader.io/docs/latest/api_reference/data

**Contents:**
- Data
- Aggregation​
  - class BarAggregator​
    - bar_type​
    - handle_bar(self, Bar bar) → void​
    - handle_quote_tick(self, QuoteTick tick) → void​
    - handle_trade_tick(self, TradeTick tick) → void​
    - is_running​
    - start_batch_update(self, handler: Callable[[Bar], None], uint64_t time_ns) → None​
    - stop_batch_update(self) → None​

The data subpackage groups components relating to the data stack and data tooling for the platform.

The layered architecture of the data stack somewhat mirrors the execution stack with a central engine, cache layer beneath, database layer beneath, with alternative implementations able to be written on top.

Due to the high-performance, the core components are reusable between both backtest and live implementations - helping to ensure consistent logic for trading operations.

BarAggregator(Instrument instrument, BarType bar_type, handler: Callable[[Bar], None]) -> None

Provides a means of aggregating specified bars and sending to a registered handler.

The aggregators bar type.

Update the aggregator with the given bar.

Update the aggregator with the given tick.

Update the aggregator with the given tick.

BarBuilder(Instrument instrument, BarType bar_type) -> None

Provides a generic bar builder for aggregation.

Return the aggregated bar with the given closing timestamp, and reset.

Return the aggregated bar and reset.

The builders current update count.

If the builder is initialized.

The price precision for the builders instrument.

Reset the bar builder.

All stateful fields are reset to their initial value.

The size precision for the builders instrument.

UNIX timestamp (nanoseconds) when the builder last updated.

Update the bar builder.

Update the bar builder.

RenkoBarAggregator(Instrument instrument, BarType bar_type, handler: Callable[[Bar], None]) -> None

Provides a means of building Renko bars from ticks.

Renko bars are created when the price moves by a fixed amount (brick size) regardless of time or volume. Each bar represents a price movement equal to the step size in the bar specification.

The aggregators bar type.

Update the aggregator with the given bar.

Update the aggregator with the given tick.

Update the aggregator with the given tick.

TickBarAggregator(Instrument instrument, BarType bar_type, handler: Callable[[Bar], None]) -> None

Provides a means of building tick bars from ticks.

When received tick count reaches the step threshold of the bar specification, then a bar is created and sent to the handler.

The aggregators bar type.

Update the aggregator with the given bar.

Update the aggregator with the given tick.

Update the aggregator with the given tick.

TimeBarAggregator(Instrument instrument, BarType bar_type, handler: Callable[[Bar], None], Clock clock, str interval_type=’left-open’, bool timestamp_on_close=True, bool skip_first_non_full_bar=False, bool build_with_no_updates=True, time_bars_origin_offset: pd.Timedelta | pd.DateOffset = None, int bar_build_delay=0) -> None

Provides a means of building time bars from ticks with an internal timer.

When the time reaches the next time interval of the bar specification, then a bar is created and sent to the handler.

The aggregators bar type.

Return the start time for the aggregators next bar.

Update the aggregator with the given bar.

Update the aggregator with the given tick.

Update the aggregator with the given tick.

The aggregators time interval.

The aggregators time interval.

The aggregators next closing time.

Stop the bar aggregator.

ValueBarAggregator(Instrument instrument, BarType bar_type, handler: Callable[[Bar], None]) -> None

Provides a means of building value bars from ticks.

When received value reaches the step threshold of the bar specification, then a bar is created and sent to the handler.

The aggregators bar type.

Return the current cumulative value of the aggregator.

Update the aggregator with the given bar.

Update the aggregator with the given tick.

Update the aggregator with the given tick.

VolumeBarAggregator(Instrument instrument, BarType bar_type, handler: Callable[[Bar], None]) -> None

Provides a means of building volume bars from ticks.

When received volume reaches the step threshold of the bar specification, then a bar is created and sent to the handler.

The aggregators bar type.

Update the aggregator with the given bar.

Update the aggregator with the given tick.

Update the aggregator with the given tick.

DataClient(ClientId client_id, MessageBus msgbus, Cache cache, Clock clock, Venue venue: Venue | None = None, config: NautilusConfig | None = None)

The base class for all data clients.

This class should not be used directly, but through a concrete subclass.

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

If the client is connected.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Request data for the given data type.

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

Subscribe to data for the given data type.

Return the custom data types subscribed to.

The trader ID associated with the component.

Unsubscribe from data for the given data type.

The clients venue ID (if applicable).

MarketDataClient(ClientId client_id, MessageBus msgbus, Cache cache, Clock clock, Venue venue: Venue | None = None, config: NautilusConfig | None = None)

The base class for all market data clients.

This class should not be used directly, but through a concrete subclass.

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

If the client is connected.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Request data for the given data type.

Request historical Bar data. To load historical data from a catalog, you can pass a list[DataCatalogConfig] to the TradingNodeConfig or the BacktestEngineConfig.

Request Instrument data for the given instrument ID.

Request all Instrument data for the given venue.

Request order book snapshot data.

Request historical QuoteTick data.

Request historical TradeTick data.

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

Subscribe to data for the given data type.

Subscribe to Bar data for the given bar type.

Subscribe to FundingRateUpdate data for the given instrument ID.

Subscribe to IndexPriceUpdate data for the given instrument ID.

Subscribe to the Instrument with the given instrument ID.

Subscribe to InstrumentClose updates for the given instrument ID.

Subscribe to InstrumentStatus data for the given instrument ID.

Subscribe to all Instrument data.

Subscribe to MarkPriceUpdate data for the given instrument ID.

Subscribe to OrderBookDeltas data for the given instrument ID.

Subscribe to OrderBookDepth10 data for the given instrument ID.

Subscribe to OrderBook snapshots data for the given instrument ID.

Subscribe to QuoteTick data for the given instrument ID.

Subscribe to TradeTick data for the given instrument ID.

Return the bar types subscribed to.

Return the custom data types subscribed to.

Return the funding rate update instruments subscribed to.

Return the index price update instruments subscribed to.

Return the instrument closes subscribed to.

Return the status update instruments subscribed to.

Return the instruments subscribed to.

Return the mark price update instruments subscribed to.

Return the order book delta instruments subscribed to.

Return the order book snapshot instruments subscribed to.

Return the quote tick instruments subscribed to.

Return the trade tick instruments subscribed to.

The trader ID associated with the component.

Unsubscribe from data for the given data type.

Unsubscribe from Bar data for the given bar type.

Unsubscribe from FundingRateUpdate data for the given instrument ID.

Unsubscribe from IndexPriceUpdate data for the given instrument ID.

Unsubscribe from Instrument data for the given instrument ID.

Unsubscribe from InstrumentClose data for the given instrument ID.

Unsubscribe from InstrumentStatus data for the given instrument ID.

Unsubscribe from all Instrument data.

Unsubscribe from MarkPriceUpdate data for the given instrument ID.

Unsubscribe from OrderBookDeltas data for the given instrument ID.

Unsubscribe from OrderBookDepth10 data for the given instrument ID.

Unsubscribe from OrderBook snapshots data for the given instrument ID.

Unsubscribe from QuoteTick data for the given instrument ID.

Unsubscribe from TradeTick data for the given instrument ID.

The clients venue ID (if applicable).

The DataEngine is the central component of the entire data stack.

The data engines primary responsibility is to orchestrate interactions between the DataClient instances, and the rest of the platform. This includes sending requests to, and receiving responses from, data endpoints via its registered data clients.

The engine employs a simple fan-in fan-out messaging pattern to execute DataCommand type messages, and process DataResponse messages or market data objects.

Alternative implementations can be written on top of the generic engine - which just need to override the execute, process, send and receive methods.

DataEngine(MessageBus msgbus, Cache cache, Clock clock, config: DataEngineConfig | None = None) -> None

Provides a high-performance data engine for managing many DataClient instances, for the asynchronous ingest of data.

Check all of the engines clients are connected.

Check all of the engines clients are disconnected.

The total count of data commands received by the engine.

Connect the engine by calling connect on all registered clients.

The total count of data stream objects received by the engine.

If debug mode is active (will provide extra debug logging).

Return the default data client registered with the engine.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Deregister the given data client from the data engine.

Disconnect the engine by calling disconnect on all registered clients.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Execute the given data command.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

Returns the configured external client order IDs.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Process the given data.

Register the given data catalog with the engine.

Register the given data client with the data engine.

Register the given client as the default routing client (when a specific venue routing cannot be found).

Any existing default routing client will be overwritten.

Register the given client to route messages to the given venue.

Any existing client in the routing map for the given venue will be overwritten.

Return the execution clients registered with the engine.

Handle the given request.

The total count of data requests received by the engine.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Handle the given response.

The total count of data responses received by the engine.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

dict[Venue, DataClient]

Return the default data client registered with the engine.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Stop the registered clients.

Return the bar types subscribed to.

Return the custom data types subscribed to.

Return the funding rate update instruments subscribed to.

Return the index price update instruments subscribed to.

Return the close price instruments subscribed to.

Return the status update instruments subscribed to.

Return the instruments subscribed to.

Return the mark price update instruments subscribed to.

Return the order book delta instruments subscribed to.

Return the order book snapshot instruments subscribed to.

Return the quote tick instruments subscribed to.

Return the synthetic instrument quotes subscribed to.

Return the synthetic instrument trades subscribed to.

Return the trade tick instruments subscribed to.

The trader ID associated with the component.

DataCommand(DataType data_type, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

The base class for all data commands.

This class should not be used directly, but through a concrete subclass.

The data client ID for the command.

The command data type.

The command message ID.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

DataResponse(ClientId client_id: ClientId | None, Venue venue: Venue | None, DataType data_type, data, UUID4 correlation_id, UUID4 response_id, uint64_t ts_init, datetime start, datetime end, dict params: dict | None = None) -> None

Represents a response with data.

The data client ID for the response.

The response correlation ID.

The response data type.

The end datetime (UTC) of response time range.

The response message ID.

Additional specific parameters for the response.

The start datetime (UTC) of response time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the response.

RequestBars(BarType bar_type, datetime start: datetime | None, datetime end: datetime | None, int limit, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for bars.

The bar type for the request.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestData(DataType data_type, InstrumentId instrument_id: InstrumentId | None, datetime start: datetime | None, datetime end: datetime | None, int limit, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for data.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestInstrument(InstrumentId instrument_id, datetime start: datetime | None, datetime end: datetime | None, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for an instrument.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestInstruments(datetime start: datetime | None, datetime end: datetime | None, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for instruments.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestOrderBookDepth(InstrumentId instrument_id, datetime start: datetime | None, datetime end: datetime | None, int limit, int depth, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for historical OrderBookDepth10 data.

The callback for the response.

The data client ID for the request.

The request data type.

The maximum depth for the order book depths.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestOrderBookSnapshot(InstrumentId instrument_id, int limit, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for an order book snapshot.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestQuoteTicks(InstrumentId instrument_id, datetime start: datetime | None, datetime end: datetime | None, int limit, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for quote ticks.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

RequestTradeTicks(InstrumentId instrument_id, datetime start: datetime | None, datetime end: datetime | None, int limit, ClientId client_id: ClientId | None, Venue venue: Venue | None, callback: Callable[[Any], None], UUID4 request_id, uint64_t ts_init, dict params: dict | None) -> None

Represents a request for trade ticks.

The callback for the response.

The data client ID for the request.

The request data type.

The end datetime (UTC) of request time range.

The request message ID.

The instrument ID for the request.

The limit on the amount of data to return for the request.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the request.

SubscribeBars(BarType bar_type, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to bars for an instrument.

The bar type for the subscription.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeData(DataType data_type, InstrumentId instrument_id: InstrumentId | None, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to data.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeFundingRates(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to funding rates.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeIndexPrices(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to index prices.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeInstrument(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeInstrumentClose(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to the close of an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeInstrumentStatus(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to the status of an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeInstruments(ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to all instruments of a venue.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeMarkPrices(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to mark prices.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeOrderBook(InstrumentId instrument_id, type book_data_type, BookType book_type, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, int depth=0, bool managed=True, int interval_ms=0, dict params: dict | None = None) -> None

Represents a command to subscribe to order book deltas for an instrument.

The data client ID for the command.

The command data type.

The maximum depth for the subscription.

The command message ID.

The instrument ID for the subscription.

The order book snapshot interval in milliseconds (must be positive for snapshots).

If an order book should be managed by the data engine based on the subscribed feed.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeQuoteTicks(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to quote ticks.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

SubscribeTradeTicks(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to subscribe to trade ticks.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

Convert this subscribe message to a request message.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeBars(BarType bar_type, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from bars for an instrument.

The bar type for the subscription.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

UnsubscribeData(DataType data_type, InstrumentId instrument_id: InstrumentId | None, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe to data.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeFundingRates(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from funding rates for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeIndexPrices(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from index prices for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeInstrument(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe to an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeInstrumentClose(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from instrument close for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeInstrumentStatus(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from instrument status.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeInstruments(ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe to all instruments.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeMarkPrices(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from mark prices for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeOrderBook(InstrumentId instrument_id, type book_data_type, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from order book updates for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeQuoteTicks(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from quote ticks for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

Bases: UnsubscribeData

UnsubscribeTradeTicks(InstrumentId instrument_id, ClientId client_id: ClientId | None, Venue venue: Venue | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Represents a command to unsubscribe from trade ticks for an instrument.

The data client ID for the command.

The command data type.

The command message ID.

The instrument ID for the subscription.

Additional specific parameters for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue for the command.

---

## Bybit

**URL:** https://nautilustrader.io/docs/latest/integrations/bybit

**Contents:**
- Bybit
- Examples​
- Overview​
- Bybit documentation​
- Products​
- Symbology​
- Orders capability​
  - Order types​
  - Execution instructions​
  - Time in force​

Founded in 2018, Bybit is one of the largest cryptocurrency exchanges in terms of daily trading volume, and open interest of crypto assets and crypto derivative products. This integration supports live market data ingest and order execution with Bybit.

You can find live example scripts here.

This guide assumes a trader is setting up for both live market data feeds, and trade execution. The Bybit adapter includes multiple components, which can be used together or separately depending on the use case.

Most users will simply define a configuration for a live trading node (as below), and won't need to necessarily work with these lower level components directly.

Bybit provides extensive documentation for users which can be found in the Bybit help center. It’s recommended you also refer to the Bybit documentation in conjunction with this NautilusTrader integration guide.

A product is an umbrella term for a group of related instrument types.

Product is also referred to as category in the Bybit v5 API.

The following product types are supported on Bybit:

To distinguish between different product types on Bybit, Nautilus uses specific product category suffixes for symbols:

These suffixes must be appended to the Bybit raw symbol string to identify the specific product type for the instrument ID. For example:

Bybit offers a flexible combination of trigger types, enabling a broader range of Nautilus orders. All the order types listed below can be used as either entries or exits, except for trailing stops (which utilize a position-related API).

Individual orders can be customized using the params dictionary when submitting orders:

Without is_leverage=True in the params, SPOT orders will only use your available balance and won't borrow funds, even if you have auto-borrow enabled on your Bybit account.

For a complete example of using order parameters including is_leverage, see the bybit_exec_tester.py example.

The following limitations apply to SPOT products, as positions are not tracked on the venue side:

Trailing stops on Bybit do not have a client order ID on the venue side (though there is a venue_order_id). This is because trailing stops are associated with a netted position for an instrument. Consider the following points when using trailing stops on Bybit:

Every HTTP call consumes the global token bucket as well as any keyed quota(s). When usage exceeds a bucket, requests are queued automatically, so manual throttling is rarely required.

Bybit responds with error code 10016 when the rate limit is exceeded and may temporarily block the IP if requests continue without back-off.

For more details on rate limiting, see the official documentation: https://bybit-exchange.github.io/docs/v5/rate-limit.

If no product types are specified then all product types will be loaded and available.

The adapter automatically determines the account type based on configured product types:

This allows you to trade SPOT alongside derivatives in a single Unified Trading Account, which is the standard account type for most Bybit users.

Unified Trading Accounts (UTA) and SPOT margin trading

Most Bybit users now have Unified Trading Accounts (UTA) as Bybit steers new users to this account type. Classic accounts are considered legacy.

For SPOT margin trading on UTA accounts:

Important: The Nautilus Bybit adapter defaults to is_leverage=False for SPOT orders, meaning they won't use margin unless you explicitly enable it.

Understanding how Bybit determines the currency for trading fees is important for accurate accounting and position tracking. The fee currency rules vary between SPOT and derivatives products.

For SPOT trading, the fee currency depends on the order side and whether the fee is a rebate (negative fee for maker orders):

When maker fees are negative (rebates), the currency logic is inverted:

Taker orders never have inverted logic, even if the maker fee rate is negative. Taker fees always follow the normal fee currency rules.

For all derivatives products (LINEAR, INVERSE, OPTION), fees are always charged in the settlement currency:

When the WebSocket execution message doesn't provide the exact fee amount (execFee), the adapter calculates fees as follows:

For complete details on Bybit's fee structure and currency rules, refer to:

The product types for each client must be specified in the configurations.

The most common use case is to configure a live TradingNode to include Bybit data and execution clients. To achieve this, add a BYBIT section to your client configuration(s):

Then, create a TradingNode and add the client factories:

There are two options for supplying your credentials to the Bybit clients. Either pass the corresponding api_key and api_secret values to the configuration objects, or set the following environment variables:

For Bybit live clients, you can set:

For Bybit demo clients, you can set:

For Bybit testnet clients, you can set:

We recommend using environment variables to manage your credentials.

When starting the trading node, you'll receive immediate confirmation of whether your credentials are valid and have trading permissions.

For additional features or to contribute to the Bybit adapter, please see our contributing guide.

**Examples:**

Example 1 (python):
```python
# Submit a SPOT order with margin enabledorder = strategy.order_factory.market(    instrument_id=InstrumentId.from_str("BTCUSDT-SPOT.BYBIT"),    order_side=OrderSide.BUY,    quantity=Quantity.from_str("0.1"),    params={"is_leverage": True}  # Enable margin for this order)strategy.submit_order(order)
```

Example 2 (python):
```python
from nautilus_trader.adapters.bybit import BYBITfrom nautilus_trader.adapters.bybit import BybitProductTypefrom nautilus_trader.live.node import TradingNodeconfig = TradingNodeConfig(    ...,  # Omitted    data_clients={        BYBIT: {            "api_key": "YOUR_BYBIT_API_KEY",            "api_secret": "YOUR_BYBIT_API_SECRET",            "base_url_http": None,  # Override with custom endpoint            "product_types": [BybitProductType.LINEAR]            "testnet": False,        },    },    exec_clients={        BYBIT: {            "api_key": "YOUR_BYBIT_API_KEY",            "api_secret": "YOUR_BYBIT_API_SECRET",            "base_url_http": None,  # Override with custom endpoint            "product_types": [BybitProductType.LINEAR]            "testnet": False,        },    },)
```

Example 3 (python):
```python
from nautilus_trader.adapters.bybit import BYBITfrom nautilus_trader.adapters.bybit import BybitLiveDataClientFactoryfrom nautilus_trader.adapters.bybit import BybitLiveExecClientFactoryfrom nautilus_trader.live.node import TradingNode# Instantiate the live trading node with a configurationnode = TradingNode(config=config)# Register the client factories with the nodenode.add_data_client_factory(BYBIT, BybitLiveDataClientFactory)node.add_exec_client_factory(BYBIT, BybitLiveExecClientFactory)# Finally build the nodenode.build()
```

---
