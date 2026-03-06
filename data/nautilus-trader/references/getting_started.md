# Nautilus_Trader - Getting Started

**Pages:** 8

---

## Installation

**URL:** https://nautilustrader.io/docs/latest/getting_started/installation

**Contents:**
- Installation
- From PyPI​
- Extras​
- From the Nautech Systems package index​
  - Stable wheels​
  - Development wheels​
  - Installation commands​
  - Available versions​
  - Branch updates​
  - Retention policies​

NautilusTrader is officially supported for Python 3.11-3.13 on the following 64-bit platforms:

NautilusTrader may work on other platforms, but only those listed above are regularly used by developers and tested in CI.

Continuous CI coverage comes from the GitHub Actions runners we build on:

On Linux, confirm your glibc version with ldd --version and ensure it reports 2.35 or newer before proceeding.

We recommend using the latest supported version of Python and installing nautilus_trader inside a virtual environment to isolate dependencies.

There are two supported ways to install:

We highly recommend installing using the uv package manager with a "vanilla" CPython.

Conda and other Python distributions may work but aren’t officially supported.

To install the latest nautilus_trader binary wheel (or sdist package) from PyPI using Python's pip package manager:

Install optional dependencies as 'extras' for specific integrations:

To install with specific extras using pip:

The Nautech Systems package index (packages.nautechsystems.io) complies with PEP-503 and hosts both stable and development binary wheels for nautilus_trader. This enables users to install either the latest stable release or pre-release versions for testing.

Stable wheels correspond to official releases of nautilus_trader on PyPI, and use standard versioning.

To install the latest stable release:

Use --extra-index-url instead of --index-url if you want pip to fall back to PyPI automatically:

Development wheels are published from both the nightly and develop branches, allowing users to test features and fixes ahead of stable releases.

This process also helps preserve compute resources and provides easy access to the exact binaries tested in CI pipelines, while adhering to PEP-440 versioning standards:

Note: Development wheels from the develop branch publish for every supported platform except Linux ARM64. Skipping that target keeps CI feedback fast while avoiding unnecessary build resource usage.

We do not recommend using development wheels in production environments, such as live trading controlling real capital.

By default, pip will install the latest stable release. Adding the --pre flag ensures that pre-release versions, including development wheels, are considered.

To install the latest available pre-release (including development wheels):

To install a specific development wheel (e.g., 1.221.0a20250912 for September 12, 2025):

You can view all available versions of nautilus_trader on the package index.

To programmatically request and list available versions:

It's possible to install from source using pip if you first install the build dependencies as specified in the pyproject.toml.

Start a new PowerShell

Install uv (see the uv installation guide for more details):

The --depth 1 flag fetches just the latest commit for a faster, lightweight clone.

Adjust the Python version and architecture in the LD_LIBRARY_PATH to match your system. Use uv python list to find the exact path for your Python installation.

To install a binary wheel from GitHub, first navigate to the latest release. Download the appropriate .whl for your operating system and Python version, then run:

NautilusTrader is still under active development. Some features may be incomplete, and while the API is becoming more stable, breaking changes can occur between releases. We strive to document these changes in the release notes on a best-effort basis.

We aim to follow a weekly release schedule, though experimental or larger features may cause delays.

Use NautilusTrader only if you are prepared to adapt to these changes.

Using Redis with NautilusTrader is optional and only required if configured as the backend for a cache database or message bus.

The minimum supported Redis version is 6.2 (required for streams functionality).

For a quick setup, we recommend using a Redis Docker container. You can find an example setup in the .docker directory, or run the following command to start a container:

To manage the Redis container:

We recommend using Redis Insight as a GUI to visualize and debug Redis data efficiently.

NautilusTrader supports two precision modes for its core value types (Price, Quantity, Money), which differ in their internal bit-width and maximum decimal precision.

By default, the official Python wheels ship in high-precision (128-bit) mode on Linux and macOS. On Windows, only standard-precision (64-bit) is available due to the lack of native 128-bit integer support.

For the Rust crates, the default is standard-precision unless you explicitly enable the high-precision feature flag.

The performance tradeoff is that standard-precision is ~3–5% faster in typical backtests, but has lower decimal precision and a smaller representable value range.

Performance benchmarks comparing the modes are pending.

The precision mode is determined by:

To enable high-precision (128-bit) mode in Rust, add the high-precision feature to your Cargo.toml:

See the Value Types specifications for more details.

**Examples:**

Example 1 (bash):
```bash
pip install -U nautilus_trader
```

Example 2 (bash):
```bash
pip install -U "nautilus_trader[docker,ib]"
```

Example 3 (bash):
```bash
pip install -U nautilus_trader --index-url=https://packages.nautechsystems.io/simple
```

Example 4 (bash):
```bash
pip install -U nautilus_trader --pre --index-url=https://packages.nautechsystems.io/simple
```

---

## Tutorials

**URL:** https://nautilustrader.io/docs/latest/tutorials/

**Contents:**
- Tutorials
- Running in docker​

The tutorials provide a guided learning experience with a series of comprehensive step-by-step walkthroughs. Each tutorial targets specific features or workflows, enabling hands-on learning. From basic tasks to more advanced operations, these tutorials cater to a wide range of skill levels.

Each tutorial is generated from a Jupyter notebook located in the docs tutorials directory. These notebooks serve as valuable learning aids and let you execute the code interactively.

Alternatively, a self-contained dockerized Jupyter notebook server is available for download, which requires no setup or installation. This is the fastest way to get up and running to try out NautilusTrader. Note that deleting the container will also delete any data.

NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output), therefore we set log_level to ERROR in the examples. Lowering this level to see more logging will cause the notebook to hang during cell execution. We are currently investigating a fix that involves either raising the configured rate limits for Jupyter, or throttling the log flushing from Nautilus.

---

## Backtest (low-level API)

**URL:** https://nautilustrader.io/docs/latest/getting_started/backtest_low_level

**Contents:**
- Backtest (low-level API)
- Overview​
- Prerequisites​
- Imports​
- Loading data​
- Initialize a backtest engine​
- Add venues​
- Add data​
- Add strategies​
- Add execution algorithms​

Tutorial for NautilusTrader a high-performance algorithmic trading platform and event driven backtester.

View source on GitHub.

This tutorial walks through how to use a BacktestEngine to backtest a simple EMA cross strategy with a TWAP execution algorithm on a simulated Binance Spot exchange using historical trade tick data.

The following points will be covered:

We'll start with all of our imports for the remainder of this tutorial.

For this tutorial we use stub test data from the NautilusTrader repository (the automated test suite also uses this data to verify platform correctness).

First, instantiate a data provider to read raw CSV trade tick data into memory as a pd.DataFrame. Next, initialize the instrument that matches the data (in this case the ETHUSDT spot cryptocurrency pair for Binance) and reuse it for the remainder of the backtest run.

Then wrangle the data into a list of Nautilus TradeTick objects so you can add them to the BacktestEngine.

See the Loading External Data guide for a more detailed explanation of the typical data processing components and pipeline.

Create a backtest engine. You can call BacktestEngine() to instantiate an engine with the default configuration.

We also initialize a BacktestEngineConfig (with only a custom trader_id specified) to illustrate the general configuration pattern.

See the Configuration API reference for details of all configuration options available.

Create a venue to trade on that matches the market data you add to the engine.

In this case we set up a simulated Binance Spot exchange.

Add data to the backtest engine. Start by adding the Instrument object we initialized earlier to match the data.

Then add the trades we wrangled earlier.

Machine resources and your imagination limit the amount and variety of data types you can use (custom types are possible). You can also backtest across multiple venues, again constrained only by machine resources.

Add the trading strategies you plan to run as part of the system.

You can backtest multiple strategies and instruments; machine resources remain the only limit.

First, initialize a strategy configuration, then use it to initialize a strategy that you can add to the engine:

You may notice that this strategy config includes parameters related to a TWAP execution algorithm. We can flexibly use different parameters per order submit, but we still need to initialize and add the actual ExecAlgorithm component that executes the algorithm.

NautilusTrader enables you to build complex systems of custom components. Here we highlight one built-in component: a TWAP execution algorithm. Configure it and add it to the engine using the same general pattern as for strategies.

You can backtest multiple execution algorithms; machine resources remain the only limit.

After configuring the data, venues, and trading system, run a backtest. Call the .run(...) method to process all available data by default.

See the BacktestEngineConfig API reference for a complete description of all available methods and options.

After the backtest completes, the engine automatically logs a post-run tearsheet with default statistics (or custom statistics that you load; see the advanced Portfolio statistics guide).

The engine also keeps many data and execution objects in memory, which you can use to generate additional reports for performance analysis.

You can reset the engine for repeated runs with different strategy and component configurations.

Instruments and data persist across resets by default, so you don't need to reload them.

Remove and add individual components (actors, strategies, execution algorithms) as required.

See the Trader API reference for a description of all methods available to achieve this.

**Examples:**

Example 1 (python):
```python
from decimal import Decimalfrom nautilus_trader.backtest.config import BacktestEngineConfigfrom nautilus_trader.backtest.engine import BacktestEnginefrom nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithmfrom nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAPfrom nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAPConfigfrom nautilus_trader.model import BarTypefrom nautilus_trader.model import Moneyfrom nautilus_trader.model import TraderIdfrom nautilus_trader.model import Venuefrom nautilus_trader.model.currencies import ETHfrom nautilus_trader.model.currencies import USDTfrom nautilus_trader.model.enums import AccountTypefrom nautilus_trader.model.enums import OmsTypefrom nautilus_trader.persistence.wranglers import TradeTickDataWranglerfrom nautilus_trader.test_kit.providers import TestDataProviderfrom nautilus_trader.test_kit.providers import TestInstrumentProvider
```

Example 2 (python):
```python
# Load stub test dataprovider = TestDataProvider()trades_df = provider.read_csv_ticks("binance/ethusdt-trades.csv")# Initialize the instrument which matches the dataETHUSDT_BINANCE = TestInstrumentProvider.ethusdt_binance()# Process into Nautilus objectswrangler = TradeTickDataWrangler(instrument=ETHUSDT_BINANCE)ticks = wrangler.process(trades_df)
```

Example 3 (python):
```python
# Configure backtest engineconfig = BacktestEngineConfig(trader_id=TraderId("BACKTESTER-001"))# Build the backtest engineengine = BacktestEngine(config=config)
```

Example 4 (python):
```python
# Add a trading venue (multiple venues possible)BINANCE = Venue("BINANCE")engine.add_venue(    venue=BINANCE,    oms_type=OmsType.NETTING,    account_type=AccountType.CASH,  # Spot CASH account (not for perpetuals or futures)    base_currency=None,  # Multi-currency account    starting_balances=[Money(1_000_000.0, USDT), Money(10.0, ETH)],)
```

---

## Tutorials

**URL:** https://nautilustrader.io/docs/latest/tutorials

**Contents:**
- Tutorials
- Running in docker​

The tutorials provide a guided learning experience with a series of comprehensive step-by-step walkthroughs. Each tutorial targets specific features or workflows, enabling hands-on learning. From basic tasks to more advanced operations, these tutorials cater to a wide range of skill levels.

Each tutorial is generated from a Jupyter notebook located in the docs tutorials directory. These notebooks serve as valuable learning aids and let you execute the code interactively.

Alternatively, a self-contained dockerized Jupyter notebook server is available for download, which requires no setup or installation. This is the fastest way to get up and running to try out NautilusTrader. Note that deleting the container will also delete any data.

NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output), therefore we set log_level to ERROR in the examples. Lowering this level to see more logging will cause the notebook to hang during cell execution. We are currently investigating a fix that involves either raising the configured rate limits for Jupyter, or throttling the log flushing from Nautilus.

---

## Quickstart

**URL:** https://nautilustrader.io/docs/latest/getting_started/quickstart

**Contents:**
- Quickstart
- Overview​
- Prerequisites​
- 1. Get sample data​
- 2. Set up a Parquet data catalog​
- 3. Write a trading strategy​
  - Enhanced Strategy with Stop-Loss and Take-Profit​
- Configuring backtests​
- 5. Configure data​
- 6. Configure engine​

Tutorial for NautilusTrader a high-performance algorithmic trading platform and event driven backtester.

View source on GitHub.

This quickstart tutorial shows you how to get up and running with NautilusTrader backtesting using FX data. To support this, we provide pre-loaded test data in the standard Nautilus persistence format (Parquet).

To save time, we have prepared sample data in the Nautilus format for use with this example. Run the next cell to download and set up the data (this should take ~ 1-2 mins).

For further details on how to load data into Nautilus, see Loading External Data guide.

If everything worked correctly, you should be able to see a single EUR/USD instrument in the catalog.

NautilusTrader includes many built-in indicators. In this example we use the MACD indicator to build a simple trading strategy.

You can read more about MACD here; this indicator merely serves as an example without any expected alpha. You can also register indicators to receive certain data types; however, in this example we manually pass the received QuoteTick to the indicator in the on_quote_tick method.

The basic MACD strategy above will now generate trades. For better risk management, here's an enhanced version with stop-loss and take-profit orders:

Now that we have a trading strategy and data, we can begin to configure a backtest run. Nautilus uses a BacktestNode to orchestrate backtest runs, which requires some setup. This may seem a little complex at first, however this is necessary for the capabilities that Nautilus strives for.

To configure a BacktestNode, we first need to create an instance of a BacktestRunConfig, configuring the following (minimal) aspects of the backtest:

There are many more configurable features described later in the docs; for now this will get us up and running.

We need to know about the instruments that we would like to load data for, we can use the ParquetDataCatalog for this.

Next, configure the data for the backtest. Nautilus provides a flexible data-loading system for backtests, but that flexibility requires some configuration.

For each tick type (and instrument), we add a BacktestDataConfig. In this instance we are simply adding the QuoteTick(s) for our EUR/USD instrument:

Create a BacktestEngineConfig to represent the configuration of our core trading system. Pass in your trading strategies, adjust the log level as needed, and configure any other components (the defaults are fine too).

Add strategies via the ImportableStrategyConfig, which enables importing strategies from arbitrary files or user packages. In this instance our MACDStrategy lives in the current module, which Python refers to as __main__.

We can now pass our various config pieces to the BacktestRunConfig. This object now contains the full configuration for our backtest.

The BacktestNode class orchestrates the backtest run. This separation between configuration and execution enables the BacktestNode to run multiple configurations (different parameters or batches of data). We are now ready to run some backtests.

When you run the backtest with the improved MACD strategy, you should see:

If you're not seeing any trades, check:

Now that the run is complete, we can also directly query for the BacktestEngine(s) used internally by the BacktestNode by using the run configs ID.

The engine(s) can provide additional reports and information.

Let's add some additional performance metrics to better understand how our strategy performed:

**Examples:**

Example 1 (python):
```python
import osimport urllib.requestfrom pathlib import Pathfrom nautilus_trader.persistence.catalog import ParquetDataCatalogfrom nautilus_trader.persistence.wranglers import QuoteTickDataWranglerfrom nautilus_trader.test_kit.providers import CSVTickDataLoaderfrom nautilus_trader.test_kit.providers import TestInstrumentProvider# Change to project root directoryoriginal_cwd = os.getcwd()project_root = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))os.chdir(project_root)print(f"Working directory: {os.getcwd()}")# Create catalog directorycatalog_path = Path("catalog")catalog_path.mkdir(exist_ok=True)print(f"Catalog directory: {catalog_path.absolute()}")try:    # Download EUR/USD sample data    print("Downloading EUR/USD sample data...")    url = "https://raw.githubusercontent.com/nautechsystems/nautilus_data/main/raw_data/fx_hist_data/DAT_ASCII_EURUSD_T_202001.csv.gz"    filename = "EURUSD_202001.csv.gz"    print(f"Downloading from: {url}")    urllib.request.urlretrieve(url, filename)  # noqa: S310    print("Download complete")    # Create the instrument using the current schema (includes multiplier)    print("Creating EUR/USD instrument...")    instrument = TestInstrumentProvider.default_fx_ccy("EUR/USD")    # Load and process the tick data    print("Loading tick data...")    wrangler = QuoteTickDataWrangler(instrument)    df = CSVTickDataLoader.load(        filename,        index_col=0,        datetime_format="%Y%m%d %H%M%S%f",    )    df.columns = ["bid_price", "ask_price", "size"]    print(f"Loaded {len(df)} ticks")    # Process ticks    print("Processing ticks...")    ticks = wrangler.process(df)    # Write to catalog    print("Writing data to catalog...")    catalog = ParquetDataCatalog(str(catalog_path))    # Write instrument first    catalog.write_data([instrument])    print("Instrument written to catalog")    # Write tick data    catalog.write_data(ticks)    print("Tick data written to catalog")    # Verify what was written    print("\nVerifying catalog contents...")    test_catalog = ParquetDataCatalog(str(catalog_path))    loaded_instruments = test_catalog.instruments()    print(f"Instruments in catalog: {[str(i.id) for i in loaded_instruments]}")    # Clean up downloaded file    os.unlink(filename)    print("\nData setup complete!")except Exception as e:    print(f"Error: {e}")    import traceback    traceback.print_exc()finally:    os.chdir(original_cwd)    print(f"Changed back to: {os.getcwd()}")
```

Example 2 (python):
```python
from nautilus_trader.backtest.node import BacktestDataConfigfrom nautilus_trader.backtest.node import BacktestEngineConfigfrom nautilus_trader.backtest.node import BacktestNodefrom nautilus_trader.backtest.node import BacktestRunConfigfrom nautilus_trader.backtest.node import BacktestVenueConfigfrom nautilus_trader.config import ImportableStrategyConfigfrom nautilus_trader.config import LoggingConfigfrom nautilus_trader.model import Quantityfrom nautilus_trader.model import QuoteTickfrom nautilus_trader.persistence.catalog import ParquetDataCatalog
```

Example 3 (python):
```python
# Load the catalog from the project root directoryproject_root = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))catalog_path = os.path.join(project_root, "catalog")catalog = ParquetDataCatalog(catalog_path)instruments = catalog.instruments()print(f"Loaded catalog from: {catalog_path}")print(f"Available instruments: {[str(i.id) for i in instruments]}")if instruments:    print(f"\nUsing instrument: {instruments[0].id}")else:    print("\nNo instruments found. Please run the data download cell first.")
```

Example 4 (python):
```python
from nautilus_trader.core.message import Eventfrom nautilus_trader.indicators import MovingAverageConvergenceDivergencefrom nautilus_trader.model import InstrumentIdfrom nautilus_trader.model import Positionfrom nautilus_trader.model.enums import OrderSidefrom nautilus_trader.model.enums import PositionSidefrom nautilus_trader.model.enums import PriceTypefrom nautilus_trader.model.events import PositionClosedfrom nautilus_trader.model.events import PositionOpenedfrom nautilus_trader.trading.strategy import Strategyfrom nautilus_trader.trading.strategy import StrategyConfigclass MACDConfig(StrategyConfig):    instrument_id: InstrumentId    fast_period: int = 12    slow_period: int = 26    trade_size: int = 1_000_000class MACDStrategy(Strategy):    """A MACD-based strategy that only trades on zero-line crossovers."""    def __init__(self, config: MACDConfig):        super().__init__(config=config)        # Our "trading signal"        self.macd = MovingAverageConvergenceDivergence(            fast_period=config.fast_period, slow_period=config.slow_period, price_type=PriceType.MID        )        self.trade_size = Quantity.from_int(config.trade_size)        # Track our position and MACD state        self.position: Position | None = None        self.last_macd_above_zero = None  # Track if MACD was above zero on last check    def on_start(self):        """Subscribe to market data on strategy start."""        self.subscribe_quote_ticks(instrument_id=self.config.instrument_id)    def on_stop(self):        """Clean up on strategy stop."""        self.close_all_positions(self.config.instrument_id)        self.unsubscribe_quote_ticks(instrument_id=self.config.instrument_id)    def on_quote_tick(self, tick: QuoteTick):        """Process incoming quote ticks."""        # Update indicator        self.macd.handle_quote_tick(tick)        if not self.macd.initialized:            return  # Wait for indicator to warm up        # Check for trading opportunities        self.check_signals()    def on_event(self, event: Event):        """Handle position events."""        if isinstance(event, PositionOpened):            self.position = self.cache.position(event.position_id)            self._log.info(f"Position opened: {self.position.side} @ {self.position.avg_px_open}")        elif isinstance(event, PositionClosed):            if self.position and self.position.id == event.position_id:                self._log.info(f"Position closed with PnL: {self.position.realized_pnl}")                self.position = None    def check_signals(self):        """Check MACD signals - only act on actual crossovers."""        current_macd = self.macd.value        current_above_zero = current_macd > 0        # Skip if this is the first reading        if self.last_macd_above_zero is None:            self.last_macd_above_zero = current_above_zero            return        # Only act on actual crossovers        if self.last_macd_above_zero != current_above_zero:            if current_above_zero:  # Just crossed above zero                # Only go long if we're not already long                if not self.is_long:                    # Close any short position first                    if self.is_short:                        self.close_position(self.position)                    # Then go long (but only when flat)                    self.go_long()            else:  # Just crossed below zero                # Only go short if we're not already short                if not self.is_short:                    # Close any long position first                    if self.is_long:                        self.close_position(self.position)                    # Then go short (but only when flat)                    self.go_short()        self.last_macd_above_zero = current_above_zero    def go_long(self):        """Enter long position only if flat."""        if self.is_flat:            order = self.order_factory.market(                instrument_id=self.config.instrument_id,                order_side=OrderSide.BUY,                quantity=self.trade_size,            )            self.submit_order(order)            self._log.info(f"Going LONG - MACD crossed above zero: {self.macd.value:.6f}")    def go_short(self):        """Enter short position only if flat."""        if self.is_flat:            order = self.order_factory.market(                instrument_id=self.config.instrument_id,                order_side=OrderSide.SELL,                quantity=self.trade_size,            )            self.submit_order(order)            self._log.info(f"Going SHORT - MACD crossed below zero: {self.macd.value:.6f}")    @property    def is_flat(self) -> bool:        """Check if we have no position."""        return self.position is None    @property    def is_long(self) -> bool:        """Check if we have a long position."""        return self.position and self.position.side == PositionSide.LONG    @property    def is_short(self) -> bool:        """Check if we have a short position."""        return self.position and self.position.side == PositionSide.SHORT    def on_dispose(self):        """Clean up on strategy disposal."""
```

---

## Backtest (high-level API)

**URL:** https://nautilustrader.io/docs/latest/getting_started/backtest_high_level

**Contents:**
- Backtest (high-level API)
- Overview​
- Prerequisites​
- Imports​
- Loading data into the Parquet data catalog​
- Using the Data Catalog​
- Add venues​
- Add data​
- Add strategies​
- Configure backtest​

Tutorial for NautilusTrader a high-performance algorithmic trading platform and event driven backtester.

View source on GitHub.

This tutorial walks through how to use a BacktestNode to backtest a simple EMA cross strategy on a simulated FX ECN venue using historical quote tick data.

The following points will be covered:

We'll start with all of our imports for the remainder of this tutorial.

As a one-off before we start the notebook, we need to download some sample data for backtesting.

For this example we will use FX data from histdata.com. Simply go to https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/ and select an FX pair, then select one or more months of data to download.

Examples of downloaded files:

Once you have downloaded the data:

Histdata stores the FX data in CSV/text format with fields timestamp, bid_price, ask_price. First, load this raw data into a pandas.DataFrame with a schema compatible with Nautilus quotes.

Then create Nautilus QuoteTick objects by processing the DataFrame with a QuoteTickDataWrangler.

See the Loading data guide for further details.

Next, instantiate a ParquetDataCatalog (pass in a directory to store the data; by default we use the current directory). Write the instrument and tick data to the catalog. Loading the data should only take a couple of minutes, depending on how many months you include.

After you load data into the catalog, use the catalog instance to load data for backtests or research. It contains various methods to pull data from the catalog, such as .instruments(...) and quote_ticks(...) (shown below).

Nautilus uses a BacktestRunConfig object to centralize backtest configuration. The BacktestRunConfig is Partialable, so you can configure it in stages. This design reduces boilerplate when you create multiple backtest runs (for example when performing a parameter grid search).

Now we can run the backtest node, which will simulate trading across the entire data stream.

**Examples:**

Example 1 (python):
```python
import shutilfrom decimal import Decimalfrom pathlib import Pathimport pandas as pdfrom nautilus_trader.backtest.node import BacktestDataConfigfrom nautilus_trader.backtest.node import BacktestEngineConfigfrom nautilus_trader.backtest.node import BacktestNodefrom nautilus_trader.backtest.node import BacktestRunConfigfrom nautilus_trader.backtest.node import BacktestVenueConfigfrom nautilus_trader.config import ImportableStrategyConfigfrom nautilus_trader.core.datetime import dt_to_unix_nanosfrom nautilus_trader.model import QuoteTickfrom nautilus_trader.persistence.catalog import ParquetDataCatalogfrom nautilus_trader.persistence.wranglers import QuoteTickDataWranglerfrom nautilus_trader.test_kit.providers import CSVTickDataLoaderfrom nautilus_trader.test_kit.providers import TestInstrumentProvider
```

Example 2 (python):
```python
DATA_DIR = "~/Downloads/Data/"
```

Example 3 (python):
```python
path = Path(DATA_DIR).expanduser()raw_files = list(path.iterdir())assert raw_files, f"Unable to find any histdata files in directory {path}"raw_files
```

Example 4 (python):
```python
# Here we just take the first data file found and load into a pandas DataFramedf = CSVTickDataLoader.load(    file_path=raw_files[0],                                   # Input 1st CSV file    index_col=0,                                              # Use 1st column in data as index for dataframe    header=None,                                              # There are no column names in CSV files    names=["timestamp", "bid_price", "ask_price", "volume"],  # Specify names to individual columns    usecols=["timestamp", "bid_price", "ask_price"],          # Read only these columns from CSV file into dataframe    parse_dates=["timestamp"],                                # Specify columns containing date/time    date_format="%Y%m%d %H%M%S%f",                            # Format for parsing datetime)# Let's make sure data are sorted by timestampdf = df.sort_index()# Preview of loaded dataframedf.head(2)
```

---

## Getting Started

**URL:** https://nautilustrader.io/docs/latest/getting_started

**Contents:**
- Getting Started
- Installation​
- Quickstart​
- Examples in repository​
- Backtesting API levels​
  - Backtest (low-level API)​
  - Backtest (high-level API)​
- Running in docker​

To get started with NautilusTrader, you will need:

The Installation guide will help to ensure that NautilusTrader is properly installed on your machine.

The Quickstart provides a step-by-step walk through for setting up your first backtest.

The online documentation shows just a subset of examples. For the full set, see this repository on GitHub.

The following table lists example locations ordered by recommended learning progression:

NautilusTrader provides two different API levels for backtesting:

Backtesting involves running simulated trading systems on historical data.

To get started backtesting with NautilusTrader you need to first understand the two different API levels which are provided, and which one may be more suitable for your intended use case.

For more information on which API level to choose, refer to the Backtesting guide.

This tutorial runs through how to load raw data (external to Nautilus) using data loaders and wranglers, and then use this data with a BacktestEngine to run a single backtest.

This tutorial runs through how to load raw data (external to Nautilus) into the data catalog, and then use this data with a BacktestNode to run a single backtest.

Alternatively, you can download a self-contained dockerized Jupyter notebook server, which requires no setup or installation. This is the fastest way to get up and running to try out NautilusTrader. Note that deleting the container will also delete any data.

NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output), therefore we set log_level to ERROR in the examples. Lowering this level to see more logging will cause the notebook to hang during cell execution. We are currently investigating a fix that involves either raising the configured rate limits for Jupyter, or throttling the log flushing from Nautilus.

---

## Getting Started

**URL:** https://nautilustrader.io/docs/latest/getting_started/

**Contents:**
- Getting Started
- Installation​
- Quickstart​
- Examples in repository​
- Backtesting API levels​
  - Backtest (low-level API)​
  - Backtest (high-level API)​
- Running in docker​

To get started with NautilusTrader, you will need:

The Installation guide will help to ensure that NautilusTrader is properly installed on your machine.

The Quickstart provides a step-by-step walk through for setting up your first backtest.

The online documentation shows just a subset of examples. For the full set, see this repository on GitHub.

The following table lists example locations ordered by recommended learning progression:

NautilusTrader provides two different API levels for backtesting:

Backtesting involves running simulated trading systems on historical data.

To get started backtesting with NautilusTrader you need to first understand the two different API levels which are provided, and which one may be more suitable for your intended use case.

For more information on which API level to choose, refer to the Backtesting guide.

This tutorial runs through how to load raw data (external to Nautilus) using data loaders and wranglers, and then use this data with a BacktestEngine to run a single backtest.

This tutorial runs through how to load raw data (external to Nautilus) into the data catalog, and then use this data with a BacktestNode to run a single backtest.

Alternatively, you can download a self-contained dockerized Jupyter notebook server, which requires no setup or installation. This is the fastest way to get up and running to try out NautilusTrader. Note that deleting the container will also delete any data.

NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output), therefore we set log_level to ERROR in the examples. Lowering this level to see more logging will cause the notebook to hang during cell execution. We are currently investigating a fix that involves either raising the configured rate limits for Jupyter, or throttling the log flushing from Nautilus.

---
