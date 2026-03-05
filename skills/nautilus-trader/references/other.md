# Nautilus_Trader - Other

**Pages:** 15

---

## Release Notes Guide

**URL:** https://nautilustrader.io/docs/latest/developer_guide/releases

**Contents:**
- Release Notes Guide
- Sections​
  - Enhancements​
  - Breaking Changes​
  - Security​
  - Fixes​
  - Internal Improvements​
  - Documentation Updates​
  - Deprecations​
- Attribution​

This guide documents the standards for writing release notes in RELEASES.md.

Use the following sections in this order:

Omit sections that have no items for a given release.

New features and user-visible improvements.

Changes that may break existing code.

Security hardening and fixes that prevent crashes, undefined behavior, or data corruption. Includes significant hardening improvements elevated from Internal Improvements.

Bug fixes that improve correctness but don't qualify as security issues.

Implementation details and infrastructure changes.

Changes to guides and examples.

Features marked for removal.

Include in Security if the change addresses:

Otherwise use Fixes (for logic bugs and panics) or Internal Improvements (for minor hardening).

Note: Plain logic panics belong in Fixes unless they threaten system stability or data corruption.

Security (could cause crashes/corruption):

Fixes (incorrect but safe):

Enhancements (user-facing):

Internal (implementation):

After publishing a release:

**Examples:**

Example 1 (markdown):
```markdown
- Added `subscribe_order_fills(...)` and `unsubscribe_order_fills(...)` for `Actor`- Added BitMEX conditional orders support- Added support for `OrderBookDepth10` requests (#2955), thanks @faysou
```

Example 2 (markdown):
```markdown
- Removed `nautilus_trader.analysis.statistics` subpackage - must import from `nautilus_trader.analysis`- Renamed `BinanceAccountType.USDT_FUTURE` to `USDT_FUTURES`- Changed `start` parameter to required for `Actor` data request methods
```

Example 3 (markdown):
```markdown
- Fixed non-executable stack for Cython extensions to support hardened Linux systems- Fixed divide-by-zero and overflow bugs in model crate that could cause crashes- Fixed core arithmetic operations to reject NaN/Infinity values and improve overflow handling
```

Example 4 (markdown):
```markdown
- Fixed reduce-only order panic when quantity exceeds position- Fixed Binance order status parsing for external orders (#3006), thanks for reporting @bmlquant
```

---

## Rust Style Guide

**URL:** https://nautilustrader.io/docs/latest/developer_guide/rust

**Contents:**
- Rust Style Guide
- Cargo manifest conventions​
- Versioning guidance​
- Feature flag conventions​
- Module organization​
- Code style and conventions​
  - File header requirements​
  - Code formatting​
    - String formatting​
  - Type qualification​

The Rust programming language is an ideal fit for implementing the mission-critical core of the platform and systems. Its strong type system, ownership model, and compile-time checks eliminate memory errors and data races by construction, while zero-cost abstractions and the absence of a garbage collector deliver C-like performance—critical for high-frequency trading workloads.

All Rust files must include the standardized copyright header:

Import formatting is automatically handled by rustfmt when running make format. The tool organizes imports into groups (standard library, external crates, local imports) and sorts them alphabetically within each group.

Within this section, follow these spacing rules:

Prefer inline format strings over positional arguments:

This makes messages more readable and self-documenting, especially when there are multiple variables.

Follow these conventions for qualifying types in code:

Use structured error handling patterns consistently:

Primary Pattern: Use anyhow::Result<T> for fallible functions:

Custom Error Types: Use thiserror for domain-specific errors:

Error Propagation: Use the ? operator for clean error propagation.

Error Creation: Prefer anyhow::bail! for early returns with errors:

Note: Use anyhow::bail! for early returns, but anyhow::anyhow! in closure contexts like ok_or_else() where early returns aren't possible.

Use consistent async/await patterns:

Consistent attribute usage and ordering:

For enums with extensive derive attributes:

Use the new() vs new_checked() convention consistently:

Always use the FAILED constant for .expect() messages related to correctness checks:

Use SCREAMING_SNAKE_CASE for constants with descriptive names:

Prefer AHashMap and AHashSet from the ahash crate over the standard library's HashMap and HashSet:

When to use standard HashMap/HashSet:

Organize re-exports alphabetically and place at the end of lib.rs files:

All modules must have module-level documentation starting with a brief description:

For modules with feature flags, document them clearly:

All struct and enum fields must have documentation with terminating periods:

Document all public functions with:

For single line errors and panics documentation, use sentence case with the following convention:

For multi-line errors and panics documentation, use sentence case with bullets and terminating periods:

For Safety documentation, use the SAFETY: prefix followed by a short description explaining why the unsafe operation is valid:

For inline unsafe blocks, use the SAFETY: comment directly above the unsafe code:

Python bindings are provided via Cython and PyO3, allowing users to import NautilusTrader crates directly in Python without a Rust toolchain.

When exposing Rust functions to Python via PyO3:

Use consistent test module structure with section separators:

Use the rstest attribute consistently, and for parameterized tests:

Use descriptive test names that explain the scenario:

When working with PyO3 bindings, it's critical to understand and avoid reference cycles between Rust's Arc reference counting and Python's garbage collector. This section documents best practices for handling Python objects in Rust callback-holding structures.

Problem: Using Arc<PyObject> in callback-holding structs creates circular references:

Example of problematic pattern:

Solution: Use plain PyObject with proper GIL-based cloning via clone_py_object():

The clone_py_object() function:

This approach allows both Rust and Python garbage collectors to work correctly, eliminating memory leaks from reference cycles.

It will be necessary to write unsafe Rust code to be able to achieve the value of interoperating between Cython and Rust. The ability to step outside the boundaries of safe Rust is what makes it possible to implement many of the most fundamental features of the Rust language itself, just as C and C++ are used to implement their own standard libraries.

Great care will be taken with the use of Rusts unsafe facility - which just enables a small set of additional language features, thereby changing the contract between the interface and caller, shifting some responsibility for guaranteeing correctness from the Rust compiler, and onto us. The goal is to realize the advantages of the unsafe facility, whilst avoiding any undefined behavior. The definition for what the Rust language designers consider undefined behavior can be found in the language reference.

To maintain correctness, any use of unsafe Rust must follow our policy:

Crate-level lint – every crate that exposes FFI symbols enables #![deny(unsafe_op_in_unsafe_fn)]. Even inside an unsafe fn, each pointer dereference or other dangerous operation must be wrapped in its own unsafe { … } block.

CVec contract – for raw vectors that cross the FFI boundary read the FFI Memory Contract. Foreign code becomes the owner of the allocation and must call the matching vec_drop_* function exactly once.

The project uses several tools for code quality:

The project pins to a specific Rust version via rust-toolchain.toml.

Keep your toolchain synchronized with CI:

If pre-commit passes locally but fails in CI, clear the pre-commit cache and re-run:

This ensures you're using the same Rust and clippy versions as CI.

**Examples:**

Example 1 (rust):
```rust
// -------------------------------------------------------------------------------------------------//  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.//  https://nautechsystems.io////  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");//  You may not use this file except in compliance with the License.//  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html////  Unless required by applicable law or agreed to in writing, software//  distributed under the License is distributed on an "AS IS" BASIS,//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.//  See the License for the specific language governing permissions and//  limitations under the License.// -------------------------------------------------------------------------------------------------
```

Example 2 (rust):
```rust
// Preferred - inline format with variable namesanyhow::bail!("Failed to subtract {n} months from {datetime}");// Instead of - positional argumentsanyhow::bail!("Failed to subtract {} months from {}", n, datetime);
```

Example 3 (rust):
```rust
use nautilus_model::identifiers::Symbol;pub fn process_symbol(symbol: Symbol) -> anyhow::Result<()> {    if !symbol.is_valid() {        anyhow::bail!("Invalid symbol: {symbol}");    }    tokio::spawn(async move {        // Process symbol asynchronously    });    Ok(())}
```

Example 4 (rust):
```rust
pub fn calculate_balance(&mut self) -> anyhow::Result<Money> {    // Implementation}
```

---

## Benchmarking

**URL:** https://nautilustrader.io/docs/latest/developer_guide/benchmarking

**Contents:**
- Benchmarking
- Tooling overview​
- Directory layout​
- Writing Criterion benchmarks​
- Writing iai benchmarks​
- Running benches locally​
  - Generating a flamegraph​
    - Linux​
    - macOS​
- Templates​

This guide explains how NautilusTrader measures Rust performance, when to use each tool and the conventions you should follow when adding new benches.

NautilusTrader relies on two complementary benchmarking frameworks:

Most hot code paths benefit from both kinds of measurements.

Each crate keeps its performance tests in a local benches/ folder:

Cargo.toml must list every benchmark explicitly so cargo bench discovers them:

iai requires functions that take no parameters and return a value (which can be ignored). Keep them as small as possible so the measured instruction count is meaningful.

Criterion writes HTML reports to target/criterion/; open target/criterion/report/index.html in your browser.

cargo-flamegraph lets you see a sampled call-stack profile of a single benchmark. On Linux it uses perf, and on macOS it uses DTrace.

Install cargo-flamegraph once per machine (it installs a cargo flamegraph subcommand automatically).

Run a specific bench with the symbol-rich bench profile.

Open the generated flamegraph.svg in your browser and zoom into hot paths.

On Linux, perf must be available. On Debian/Ubuntu, you can install it with:

If you see an error mentioning perf_event_paranoid you need to relax the kernel’s perf restrictions for the current session (root required):

A value of 1 is typically enough; set it back to 2 (default) or make the change permanent via /etc/sysctl.conf if desired.

On macOS, DTrace requires root permissions, so you must run cargo flamegraph with sudo:

Warning Running with sudo will create files in your target/ directory that are owned by the root user. This can cause permission errors with subsequent cargo commands.

To fix this, you may need to remove the root-owned files manually, or simply run sudo cargo clean to remove the entire target/ directory.

Because [profile.bench] keeps full debug symbols the SVG will show readable function names without bloating production binaries (which still use panic = "abort" and are built via [profile.release]).

Note Benchmark binaries are compiled with the custom [profile.bench] defined in the workspace Cargo.toml. That profile inherits from release-debugging, preserving full optimisation and debug symbols so that tools like cargo flamegraph or perf produce human-readable stack traces.

Ready-to-copy starter files live in docs/dev_templates/.

Copy the template into benches/, adjust imports and names, and start measuring!

**Examples:**

Example 1 (text):
```text
crates/<crate_name>/└── benches/    ├── foo_criterion.rs   # Criterion group(s)    └── foo_iai.rs         # iai micro benches
```

Example 2 (toml):
```toml
[[bench]]name = "foo_criterion"             # file stem in benches/path = "benches/foo_criterion.rs"harness = false                    # disable the default libtest harness
```

Example 3 (rust):
```rust
use std::hint::black_box;use criterion::{Criterion, criterion_group, criterion_main};fn bench_my_algo(c: &mut Criterion) {    let data = prepare_data(); // heavy set-up done once    c.bench_function("my_algo", |b| {        b.iter(|| my_algo(black_box(&data)));    });}criterion_group!(benches, bench_my_algo);criterion_main!(benches);
```

Example 4 (rust):
```rust
use std::hint::black_box;fn bench_add() -> i64 {    let a = black_box(123);    let b = black_box(456);    a + b}iai::main!(bench_add);
```

---

## Cython

**URL:** https://nautilustrader.io/docs/latest/developer_guide/cython

**Contents:**
- Cython
- What is Cython?​
- Function and method signatures​
- Debugging​
  - PyCharm​
  - Cython docs​
  - Tips​

Here you will find guidance and tips for working on NautilusTrader using the Cython language. More information on Cython syntax and conventions can be found by reading the Cython docs.

Cython is a superset of Python that compiles to C extension modules, enabling optional static typing and optimized performance. NautilusTrader relies on Cython for its Python bindings and performance-critical components.

Ensure that all functions and methods returning void or a primitive C type (such as bint, int, double) include the except * keyword in the signature.

This will ensure Python exceptions are not ignored, and instead are “bubbled up” to the caller as expected.

Improved debugging support for Cython has remained a highly up-voted PyCharm feature for many years. Unfortunately, it's safe to assume that PyCharm will not be receiving first class support for Cython debugging https://youtrack.jetbrains.com/issue/PY-9476.

The following recommendations are contained in the Cython docs: https://cython.readthedocs.io/en/latest/src/userguide/debugging.html

The summary is it involves manually running a specialized version of gdb from the command line. We don't recommend this workflow.

When debugging and seeking to understand a complex system such as NautilusTrader, it can be quite helpful to step through the code with a debugger. With this not being available for the Cython part of the codebase, there are a few things which can help:

---

## Interactive Brokers

**URL:** https://nautilustrader.io/docs/latest/integrations/ib

**Contents:**
- Interactive Brokers
- Installation​
- Examples​
- Getting started​
  - Connection methods​
  - Default ports​
  - Establish connection to an existing gateway or TWS​
  - Establish connection to Dockerized IB Gateway​
  - Environment variables​
  - Connection management​

Interactive Brokers (IB) is a trading platform providing market access across a wide range of financial instruments, including stocks, options, futures, currencies, bonds, funds, and cryptocurrencies. NautilusTrader offers an adapter to integrate with IB using their Trader Workstation (TWS) API through their Python library, ibapi.

The TWS API serves as an interface to IB's standalone trading applications: TWS and IB Gateway. Both can be downloaded from the IB website. If you haven't installed TWS or IB Gateway yet, refer to the Initial Setup guide. In NautilusTrader, you'll establish a connection to one of these applications via the InteractiveBrokersClient.

Alternatively, you can start with a dockerized version of the IB Gateway, which is particularly useful when deploying trading strategies on a hosted cloud platform. This requires having Docker installed on your machine, along with the docker Python package, which NautilusTrader conveniently includes as an extra package.

The standalone TWS and IB Gateway applications require manually inputting username, password, and trading mode (live or paper) at startup. The dockerized version of the IB Gateway handles these steps programmatically.

To install NautilusTrader with Interactive Brokers (and Docker) support:

To build from source with all extras (including IB and Docker):

Because IB does not provide wheels for ibapi, NautilusTrader repackages it for release on PyPI.

You can find live example scripts here.

Before implementing your trading strategies, make sure that either TWS (Trader Workstation) or IB Gateway is running. You can log in to one of these standalone applications with your credentials, or connect programmatically via DockerizedIBGateway.

There are two primary ways to connect to Interactive Brokers:

Interactive Brokers uses different default ports depending on the application and trading mode:

When connecting to a pre-existing gateway or TWS, specify the ibg_host and ibg_port parameters in both the InteractiveBrokersDataClientConfig and InteractiveBrokersExecClientConfig:

For automated deployments, the dockerized gateway is recommended. Supply dockerized_gateway with an instance of DockerizedIBGatewayConfig in both client configurations. The ibg_host and ibg_port parameters are not needed as they're managed automatically.

To supply credentials to the Interactive Brokers Gateway, either pass the username and password to the DockerizedIBGatewayConfig, or set the following environment variables:

The adapter includes robust connection management features:

The Interactive Brokers adapter provides a comprehensive integration with IB's TWS API. The adapter includes several major components:

The adapter supports trading across all major asset classes available through Interactive Brokers:

The InteractiveBrokersClient serves as the central component of the IB adapter, overseeing a range of critical functions. These include establishing and maintaining connections, handling API errors, executing trades, and gathering various types of data such as market data, contract/instrument data, and account details.

To ensure efficient management of these diverse responsibilities, the InteractiveBrokersClient is divided into several specialized mixin classes. This modular approach enhances manageability and clarity.

The client uses a mixin-based architecture where each mixin handles a specific aspect of the IB API:

To troubleshoot TWS API incoming message issues, consider starting at the InteractiveBrokersClient._process_message method, which acts as the primary gateway for processing all messages received from the API.

The InteractiveBrokersInstrumentProvider supports three methods for constructing InstrumentId instances, which can be configured via the symbology_method enum in InteractiveBrokersInstrumentProviderConfig.

When symbology_method is set to IB_SIMPLIFIED (the default setting), the system uses intuitive, human-readable symbology rules:

Format Rules by Asset Class:

Setting symbology_method to IB_RAW enforces stricter parsing rules that align directly with the fields defined in the IB API. This method provides maximum compatibility across all regions and instrument types:

This configuration ensures explicit instrument identification and supports instruments from any region, especially those with non-standard symbology where simplified parsing may fail.

The adapter supports converting Interactive Brokers exchange codes to Market Identifier Codes (MIC) for standardized venue identification:

When set to True, the adapter automatically converts IB exchange codes to their corresponding MIC codes:

Examples of MIC Conversion:

For custom venue mapping, use the symbol_to_mic_venue dictionary to override default conversions:

The adapter supports various instrument formats based on Interactive Brokers' contract specifications:

Cryptocurrency Exchanges:

CFD/Commodity Exchanges:

In Interactive Brokers, a NautilusTrader Instrument corresponds to an IB Contract. The adapter handles two types of contract representations:

To search for contract information, use the IB Contract Information Center.

There are two primary methods for loading instruments:

Use symbology_method=SymbologyMethod.IB_SIMPLIFIED (default) with load_ids for clean, intuitive instrument identification:

Use load_contracts with IBContract instances for complex scenarios like options/futures chains:

For continuous futures contracts (using secType='CONTFUT'), the adapter creates instrument IDs using just the symbol and venue:

Continuous Futures vs Individual Futures:

When using build_options_chain=True or build_futures_chain=True, the secType and symbol should be specified for the underlying contract. The adapter will automatically discover and load all related derivative contracts within the specified expiry range.

Interactive Brokers supports option spreads through BAG contracts, which combine multiple option legs into a single tradeable instrument. NautilusTrader provides comprehensive support for creating, loading, and trading option spreads.

Option spreads are created using the InstrumentId.new_spread() method, which combines individual option legs with their respective ratios:

Option spreads must be requested before they can be traded or subscribed to for market data. Use the request_instrument() method to dynamically load spread instruments:

The HistoricInteractiveBrokersClient provides comprehensive methods for retrieving historical data from Interactive Brokers for backtesting and research purposes.

You can download entire option chains using request_instruments in your strategy, with the added benefit of saving the data to the catalog using update_catalog=True:

The adapter supports various bar specifications:

Be aware of Interactive Brokers' historical data limitations:

Interactive Brokers enforces pacing limits; excessive historical-data or order requests trigger pacing violations and IB can disable the API session for several minutes.

Live trading with Interactive Brokers requires setting up a TradingNode that incorporates both InteractiveBrokersDataClient and InteractiveBrokersExecutionClient. These clients depend on the InteractiveBrokersInstrumentProvider for instrument management.

The live trading setup consists of three main components:

The InteractiveBrokersInstrumentProvider serves as the bridge for accessing financial instrument data from IB. It supports loading individual instruments, options chains, and futures chains.

The Interactive Brokers adapter can be used alongside other data providers for enhanced market data coverage. When using multiple data sources:

The InteractiveBrokersDataClient interfaces with IB for streaming and retrieving real-time market data. Upon connection, it configures the market data type and loads instruments based on the InteractiveBrokersInstrumentProviderConfig settings.

Interactive Brokers supports several market data types:

The InteractiveBrokersExecutionClient handles trade execution, order management, account information, and position tracking. It provides comprehensive order lifecycle management and real-time account updates.

The adapter supports most Interactive Brokers order types:

The account_id parameter is crucial and must match the account logged into TWS/Gateway:

The adapter supports IB-specific order parameters through order tags:

The adapter provides comprehensive support for OCA orders through explicit configuration using IBOrderTags:

All OCA functionality must be explicitly configured using IBOrderTags:

You can specify different OCA types and behaviors using IBOrderTags:

Interactive Brokers supports three OCA types:

OCA functionality is only available through explicit configuration:

The adapter supports Interactive Brokers conditional orders through the conditions parameter in IBOrderTags. Conditional orders allow you to specify criteria that must be met before an order is transmitted or cancelled.

Percent Change Condition:

Set conditionsCancelOrder to control what happens when conditions are met:

Setting up a complete trading environment involves configuring a TradingNodeConfig with all necessary components. Here are comprehensive examples for different scenarios.

For advanced setups, you can configure multiple clients with different purposes:

Set these environment variables for easier configuration:

You can find additional examples here: https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers

Interactive Brokers uses specific error codes. Common ones include:

**Examples:**

Example 1 (bash):
```bash
pip install --upgrade "nautilus_trader[ib,docker]"
```

Example 2 (bash):
```bash
uv sync --all-extras
```

Example 3 (python):
```python
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersDataClientConfigfrom nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersExecClientConfig# Example for TWS paper trading (default port 7497)data_config = InteractiveBrokersDataClientConfig(    ibg_host="127.0.0.1",    ibg_port=7497,    ibg_client_id=1,)exec_config = InteractiveBrokersExecClientConfig(    ibg_host="127.0.0.1",    ibg_port=7497,    ibg_client_id=1,    account_id="DU123456",  # Your paper trading account ID)
```

Example 4 (python):
```python
from nautilus_trader.adapters.interactive_brokers.config import DockerizedIBGatewayConfigfrom nautilus_trader.adapters.interactive_brokers.gateway import DockerizedIBGatewaygateway_config = DockerizedIBGatewayConfig(    username="your_username",  # Or set TWS_USERNAME env var    password="your_password",  # Or set TWS_PASSWORD env var    trading_mode="paper",      # "paper" or "live"    read_only_api=True,        # Set to False to allow order execution    timeout=300,               # Startup timeout in seconds)# This may take a short while to start up, especially the first timegateway = DockerizedIBGateway(config=gateway_config)gateway.start()# Confirm you are logged inprint(gateway.is_logged_in(gateway.container))# Inspect the logsprint(gateway.container.logs())
```

---

## Developer Guide

**URL:** https://nautilustrader.io/docs/latest/developer_guide/

**Contents:**
- Developer Guide
- Contents​

Welcome to the developer guide for NautilusTrader!

Here you'll find guidance on developing and extending NautilusTrader to meet your trading needs or to contribute improvements back to the project.

This guide is structured so that automated tooling can consume it alongside human readers.

We believe in using the right tool for the job. The overall design philosophy is to fully utilize the high level power of Python, with its rich eco-system of frameworks and libraries, whilst overcoming some of its inherent shortcomings in performance and lack of built-in type safety (with it being an interpreted dynamic language).

One of the advantages of Cython is that allocation and freeing of memory is handled by the C code generator during the ‘cythonization’ step of the build (unless you’re specifically utilizing some of its lower level features).

This approach combines Python’s simplicity with near-native C performance via compiled extensions.

The main development and runtime environment we are working in is Python. With the introduction of Cython throughout the production codebase in .pyx and .pxd files, it's important to be aware of how the CPython implementation of Python interacts with the underlying CPython API, and the NautilusTrader C extension modules which Cython produces.

We recommend a thorough review of the Cython docs to familiarize yourself with some of its core concepts, and where C typing is being used.

It's not necessary to become a C language expert, however it's helpful to understand how Cython C syntax is used in function and method definitions, in local code blocks, and the common primitive C types and how these map to their corresponding PyObject types.

---

## Betfair

**URL:** https://nautilustrader.io/docs/latest/integrations/betfair

**Contents:**
- Betfair
- Installation​
- Examples​
- Betfair documentation​
- Application keys​
- API credentials​
- Overview​
- Orders capability​
  - Order types​
  - Execution instructions​

Founded in 2000, Betfair operates the world’s largest online betting exchange, with its headquarters in London and satellite offices across the globe.

NautilusTrader provides an adapter for integrating with the Betfair REST API and Exchange Streaming API.

Install NautilusTrader with Betfair support via pip:

To build from source with Betfair extras:

You can find live example scripts here.

For API details and troubleshooting, see the official Betfair Developer Documentation.

Betfair requires an Application Key to authenticate API requests. After registering and funding your account, obtain your key using the API-NG Developer AppKeys Tool.

See also the Betfair Getting Started - Application Keys guide.

Supply your Betfair credentials via environment variables or client configuration:

We recommend using environment variables to manage your credentials.

The Betfair adapter provides three primary components:

Betfair operates as a betting exchange with unique characteristics compared to traditional financial exchanges:

Here is a minimal example showing how to configure a live TradingNode with Betfair clients:

For additional features or to contribute to the Betfair adapter, please see our contributing guide.

**Examples:**

Example 1 (bash):
```bash
pip install --upgrade "nautilus_trader[betfair]"
```

Example 2 (bash):
```bash
uv sync --all-extras
```

Example 3 (bash):
```bash
export BETFAIR_USERNAME=<your_username>export BETFAIR_PASSWORD=<your_password>export BETFAIR_APP_KEY=<your_app_key>export BETFAIR_CERTS_DIR=<path_to_certificate_dir>
```

Example 4 (python):
```python
from nautilus_trader.adapters.betfair import BETFAIRfrom nautilus_trader.adapters.betfair import BetfairLiveDataClientFactoryfrom nautilus_trader.adapters.betfair import BetfairLiveExecClientFactoryfrom nautilus_trader.config import TradingNodeConfigfrom nautilus_trader.live.node import TradingNode# Configure Betfair data and execution clients (using AUD account currency)config = TradingNodeConfig(    data_clients={BETFAIR: {"account_currency": "AUD"}},    exec_clients={BETFAIR: {"account_currency": "AUD"}},)# Build the TradingNode with Betfair adapter factoriesnode = TradingNode(config)node.add_data_client_factory(BETFAIR, BetfairLiveDataClientFactory)node.add_exec_client_factory(BETFAIR, BetfairLiveExecClientFactory)node.build()
```

---

## Docs Style Guide

**URL:** https://nautilustrader.io/docs/latest/developer_guide/docs

**Contents:**
- Docs Style Guide
- General principles​
- Language and tone​
- Markdown tables​
  - Column alignment and spacing​
  - Notes and descriptions​
  - Example​
  - Support indicators​
- Code references​
- Headings​

This guide outlines the style conventions and best practices for writing documentation for NautilusTrader.

We follow modern documentation conventions that prioritize readability and accessibility:

This convention aligns with industry standards used by major technology companies including Google Developer Documentation, Microsoft Docs, and Anthropic's documentation. It improves readability, reduces cognitive load, and is more accessible for international users and screen readers.

**Examples:**

Example 1 (markdown):
```markdown
| Order Type             | Spot | Margin | USDT Futures | Coin Futures | Notes                   ||------------------------|------|--------|--------------|--------------|-------------------------|| `MARKET`               | ✓    | ✓      | ✓            | ✓            |                         || `STOP_MARKET`          | -    | ✓      | ✓            | ✓            | Not supported for Spot. || `MARKET_IF_TOUCHED`    | -    | -      | ✓            | ✓            | Futures only.           |
```

Example 2 (markdown):
```markdown
# NautilusTrader Developer Guide## Getting started with Python## Using the Binance adapter## REST API implementation## WebSocket data streaming## Testing with pytest
```

---

## Hyperliquid

**URL:** https://nautilustrader.io/docs/latest/integrations/hyperliquid

**Contents:**
- Hyperliquid
- Configuration​
  - Data client configuration options​
  - Execution client configuration options​

The Hyperliquid integration is still under active development.

---

## Coding Standards

**URL:** https://nautilustrader.io/docs/latest/developer_guide/coding_standards

**Contents:**
- Coding Standards
- Code Style​
  - Universal formatting rules​
  - Comment conventions​
  - Doc comment / docstring mood​
  - Terminology and phrasing​
  - Formatting​
  - PEP-8​
- Python style guide​
  - Type hints​

The current codebase can be used as a guide for formatting conventions. Additional guidelines are provided below.

The following applies to all source files (Rust, Python, Cython, shell, etc.):

These conventions align with the prevailing styles of each language ecosystem and make generated documentation feel natural to end-users.

Error messages: Avoid using ", got" in error messages. Use more descriptive alternatives like ", was", ", received", or ", found" depending on context.

Spelling: Use "hardcoded" (single word) rather than "hard-coded" or "hard coded" – this is the more modern and accepted spelling.

For longer lines of code, and when passing more than a couple of arguments, you should take a new line which aligns at the next logical indent (rather than attempting a hanging 'vanity' alignment off an opening parenthesis). This practice conserves space to the right, ensures important code is more central in view, and is also robust to function/method name changes.

The closing parenthesis should be located on a new line, aligned at the logical indent.

Also ensure multiple hanging parameters or arguments end with a trailing comma:

The codebase generally follows the PEP-8 style guide. Even though C typing is taken advantage of in the Cython parts of the codebase, we still aim to be idiomatic of Python where possible. One notable departure is that Python truthiness is not always taken advantage of to check if an argument is None for everything other than collections.

There are two reasons for this;

Cython can generate more efficient C code from is None and is not None, rather than entering the Python runtime to check the PyObject truthiness.

As per the Google Python Style Guide - it’s discouraged to use truthiness to check if an argument is/is not None, when there is a chance an unexpected object could be passed into the function or method which will yield an unexpected truthiness evaluation (which could result in a logical error type bug).

“Always use if foo is None: (or is not None) to check for a None value. E.g., when testing whether a variable or argument that defaults to None was set to some other value. The other value might be a value that’s false in a boolean context!”

There are still areas that aren’t performance-critical where truthiness checks for None (if foo is None: vs if not foo:) will be acceptable for clarity.

Use truthiness to check for empty collections (e.g., if not my_list:) rather than comparing explicitly to None or empty.

We welcome all feedback on where the codebase departs from PEP-8 for no apparent reason.

All function and method signatures must include comprehensive type annotations:

Generic Types: Use TypeVar for reusable components

The NumPy docstring spec is used throughout the codebase. This needs to be adhered to consistently to ensure the docs build correctly.

Test method naming: Descriptive names explaining the scenario:

ruff is utilized to lint the codebase. Ruff rules can be found in the top-level pyproject.toml, with ignore justifications typically commented.

Here are some guidelines for the style of your commit messages:

Limit subject titles to 60 characters or fewer. Capitalize subject line and do not end with period.

Use 'imperative voice', i.e. the message should describe what the commit will do if applied.

Optional: Use the body to explain change. Separate from subject with a blank line. Keep under 100 character width. You can use bullet points with or without terminating periods.

Optional: Provide # references to relevant issues or tickets.

Optional: Provide any hyperlinks which are informative.

Gitlint is available to help enforce commit message standards automatically. It checks that commit messages follow the guidelines above (character limits, formatting, etc.). This is opt-in and not enforced in CI.

Benefits: Encourages concise yet expressive commit messages, helps develop clear explanations of changes.

Installation: First install gitlint to run it locally:

To enable gitlint as an automatic commit-msg hook:

Manual usage: Check your last commit message:

Configuration is in .gitlint at the repository root:

Gitlint may be enforced in CI in the future, so adopting these practices early helps ensure a smooth transition.

**Examples:**

Example 1 (python):
```python
long_method_with_many_params(    some_arg1,    some_arg2,    some_arg3,  # <-- trailing comma)
```

Example 2 (python):
```python
def __init__(self, config: EMACrossConfig) -> None:def on_bar(self, bar: Bar) -> None:def on_save(self) -> dict[str, bytes]:def on_load(self, state: dict[str, bytes]) -> None:
```

Example 3 (python):
```python
T = TypeVar("T")class ThrottledEnqueuer(Generic[T]):
```

Example 4 (python):
```python
def test_currency_with_negative_precision_raises_overflow_error(self):def test_sma_with_no_inputs_returns_zero_count(self):def test_sma_with_single_input_returns_expected_value(self):
```

---

## FFI Memory Contract

**URL:** https://nautilustrader.io/docs/latest/developer_guide/ffi

**Contents:**
- FFI Memory Contract
- Fail-fast panics at the FFI boundary​
- CVec lifecycle​
- Capsules created on the Python side​
- Capsules created on the Rust side (PyO3 bindings)​
- Why there is no generic cvec_drop anymore​
- Box-backed *_API wrappers (owned Rust objects)​

NautilusTrader exposes several C-compatible types so that compiled Rust code can be consumed from C-extensions generated by Cython or by other native languages. The most important of these is CVec – a thin wrapper around a Rust Vec<T> that is passed across the FFI boundary by value.

The rules below are strict; violating them results in undefined behaviour (usually a double-free or a memory leak).

Rust panics must never unwind across extern "C" functions. Unwinding into C or Python is undefined behaviour and can corrupt the foreign stack or leave partially-dropped resources behind. To enforce the fail-fast architecture we wrap every exported symbol in crate::ffi::abort_on_panic, which executes the body and calls process::abort() if a panic occurs. The panic message is still logged before the abort, so debugging output is preserved while avoiding undefined behaviour.

When adding new FFI functions, call abort_on_panic(|| { … }) around the implementation (or use a helper that does so) to maintain this guarantee.

If step 3 is forgotten the allocation is leaked for the remainder of the process; if it is performed twice the program will double-free and likely crash.

Several Cython helpers allocate temporary C buffers with PyMem_Malloc, wrap them into a CVec, and return the address inside a PyCapsule. Every such capsule is created with a destructor (capsule_destructor or capsule_destructor_deltas) that frees both the buffer and the CVec. Callers must therefore not free the memory manually – doing so would double free.

When Rust code pushes a heap-allocated value into Python it must use PyCapsule::new_with_destructor so that Python knows how to free the allocation once the capsule becomes unreachable. The closure/destructor is responsible for reconstructing the original Box<T> or Vec<T> and letting it drop.

Do not use PyCapsule::new(…, None); that variant registers no destructor and will leak memory unless the recipient manually extracts and frees the pointer (something we never rely on). The codebase has been updated to follow this rule everywhere – adding new FFI modules must follow the same pattern.

Earlier versions of the codebase shipped a generic cvec_drop function that always treated the buffer as Vec<u8>. Using it with any other element type causes a size-mismatch during deallocation and corrupts the allocator’s bookkeeping. Because the helper was not referenced anywhere inside the project it has been removed to avoid accidental misuse.

When the Rust core needs to hand a complex value (for example an OrderBook, SyntheticInstrument, or TimeEventAccumulator) to foreign code it allocates the value on the heap with Box::new and returns a small repr(C) wrapper whose only field is that Box.

Memory-safety requirements are therefore:

Every constructor (*_new) must have a matching *_drop exported next to it.

The Python/Cython binding must guarantee that *_drop is invoked exactly once. Two approaches are accepted:

• Wrap the pointer in a PyCapsule created with PyCapsule::new_with_destructor, passing a destructor that calls the drop helper.

• Call the helper explicitly in __del__/__dealloc__ on the Python side. This is the historical pattern for most v1 Cython modules:

Whichever style is used, remember: forgetting the drop call leaks the entire structure, while calling it twice will double-free and crash.

New FFI code must follow this template before it can be merged.

**Examples:**

Example 1 (rust):
```rust
Python::attach(|py| {    // allocate the value on the heap    let my_data = MyStruct::new();    // move it into the capsule and register a destructor    let capsule = pyo3::types::PyCapsule::new_with_destructor(py, my_data, None, |_, _| {})        .expect("capsule creation failed");    // ... pass `capsule` back to Python ...});
```

Example 2 (rust):
```rust
#[repr(C)]pub struct OrderBook_API(Box<OrderBook>);#[unsafe(no_mangle)]pub extern "C" fn orderbook_new(id: InstrumentId, book_type: BookType) -> OrderBook_API {    OrderBook_API(Box::new(OrderBook::new(id, book_type)))}#[unsafe(no_mangle)]pub extern "C" fn orderbook_drop(book: OrderBook_API) {    drop(book); // frees the heap allocation}
```

Example 3 (python):
```python
cdef class OrderBook:    cdef OrderBook_API _mem    def __cinit__(self, ...):        self._mem = orderbook_new(...)    def __del__(self):        if self._mem._0 != NULL:            orderbook_drop(self._mem)
```

---

## Coinbase International

**URL:** https://nautilustrader.io/docs/latest/integrations/coinbase_intx

**Contents:**
- Coinbase International
- Installation​
- Examples​
- Overview​
- Coinbase documentation​
- Data​
  - Instruments​
  - WebSocket market data​
- Execution​
  - Selecting a Portfolio​

Coinbase International Exchange provides non-US institutional clients with access to cryptocurrency perpetual futures and spot markets. The exchange serves European and international traders by providing leveraged crypto derivatives, often restricted or unavailable in these regions.

Coinbase International brings a high standard of customer protection, a robust risk management framework and high-performance trading technology, including:

See the Introducing Coinbase International Exchange blog article for more details.

No additional coinbase_intx installation is required; the adapter’s core components, written in Rust, are automatically compiled and linked during the build.

You can find live example scripts here. These examples demonstrate how to set up live market data feeds and execution clients for trading on Coinbase International.

The following products are supported on the Coinbase International exchange:

This guide assumes a trader is setting up for both live market data feeds, and trade execution. The Coinbase International adapter includes multiple components, which can be used together or separately depending on the use case. These components work together to connect to Coinbase International’s APIs for market data and execution.

Most users will simply define a configuration for a live trading node (described below), and won't necessarily need to work with the above components directly.

Coinbase International provides extensive API documentation for users which can be found in the Coinbase Developer Platform. We recommend also referring to the Coinbase International documentation in conjunction with this NautilusTrader integration guide.

On startup, the adapter automatically loads all available instruments from the Coinbase International REST API and subscribes to the INSTRUMENTS WebSocket channel for updates. This ensures that the cache and clients requiring up-to-date definitions for parsing always have the latest instrument data.

Available instrument types include:

Index products have not yet been implemented.

The following data types are available:

Historical data requests have not yet been implemented.

The data client connects to Coinbase International's WebSocket feed to stream real-time market data. The WebSocket client handles automatic reconnection and re-subscribes to active subscriptions upon reconnecting.

The adapter is designed to trade one Coinbase International portfolio per execution client.

To identify your available portfolios and their IDs, use the REST client by running the following script:

This will output a list of portfolio details, similar to the example below:

To specify a portfolio for trading, set the COINBASE_INTX_PORTFOLIO_ID environment variable to the desired portfolio_id. If you're using multiple execution clients, you can alternatively define the portfolio_id in the execution configuration for each client.

Coinbase International offers market, limit, and stop order types, enabling a broad range of strategies.

The Coinbase International adapter includes a FIX (Financial Information eXchange) drop copy client. This provides reliable, low-latency execution updates directly from Coinbase's matching engine.

This approach is necessary because execution messages are not provided over the WebSocket feed, and delivers faster and more reliable order execution updates than polling the REST API.

The client processes several types of execution messages:

The FIX credentials are automatically managed using the same API credentials as the REST and WebSocket clients. No additional configuration is required beyond providing valid API credentials.

The REST client handles processing REJECTED and ACCEPTED status execution messages on order submission.

On startup, the execution client requests and loads your current account and execution state including:

This provides your trading strategies with a complete picture of your account before placing new orders.

Coinbase International has a strict specification for client order IDs. Nautilus can meet the spec by using UUID4 values for client order IDs. To comply, set the use_uuid_client_order_ids=True config option in your strategy configuration (otherwise, order submission will trigger an API error).

See the Coinbase International Create order REST API documentation for further details.

An example configuration could be:

Then, create a TradingNode and add the client factories:

Provide credentials to the clients using one of the following methods.

Either pass values for the following configuration options:

Or, set the following environment variables:

We recommend using environment variables to manage your credentials.

When starting the trading node, you'll receive immediate confirmation of whether your credentials are valid and have trading permissions.

Coinbase International returns HTTP 429 when you exceed the 100 requests/sec allowance and can throttle the API key for several seconds, so keep bursts below the documented ceiling.

**Examples:**

Example 1 (bash):
```bash
python nautilus_trader/adapters/coinbase_intx/scripts/list_portfolios.py
```

Example 2 (bash):
```bash
[{'borrow_disabled': False,  'cross_collateral_enabled': False,  'is_default': False,  'is_lsp': False,  'maker_fee_rate': '-0.00008',  'name': 'hrp5587988499',  'portfolio_id': '3mnk59ap-1-22',  # Your portfolio ID  'portfolio_uuid': 'dd0958ad-0c9d-4445-a812-1870fe40d0e1',  'pre_launch_trading_enabled': False,  'taker_fee_rate': '0.00012',  'trading_lock': False,  'user_uuid': 'd4fbf7ea-9515-1068-8d60-4de91702c108'}]
```

Example 3 (python):
```python
from nautilus_trader.adapters.coinbase_intx import COINBASE_INTX, CoinbaseIntxDataClientConfig, CoinbaseIntxExecClientConfigfrom nautilus_trader.live.node import TradingNodeconfig = TradingNodeConfig(    ...,  # Further config omitted    data_clients={        COINBASE_INTX: CoinbaseIntxDataClientConfig(            instrument_provider=InstrumentProviderConfig(load_all=True),        ),    },    exec_clients={        COINBASE_INTX: CoinbaseIntxExecClientConfig(            instrument_provider=InstrumentProviderConfig(load_all=True),        ),    },)strat_config = TOBQuoterConfig(    use_uuid_client_order_ids=True,  # <-- Necessary for Coinbase Intx    instrument_id=instrument_id,    external_order_claims=[instrument_id],    ...,  # Further config omitted)
```

Example 4 (python):
```python
from nautilus_trader.adapters.coinbase_intx import COINBASE_INTX, CoinbaseIntxLiveDataClientFactory, CoinbaseIntxLiveExecClientFactoryfrom nautilus_trader.live.node import TradingNode# Instantiate the live trading node with a configurationnode = TradingNode(config=config)# Register the client factories with the nodenode.add_data_client_factory(COINBASE_INTX, CoinbaseIntxLiveDataClientFactory)node.add_exec_client_factory(COINBASE_INTX, CoinbaseIntxLiveExecClientFactory)# Finally build the nodenode.build()
```

---

## Environment Setup

**URL:** https://nautilustrader.io/docs/latest/developer_guide/environment_setup

**Contents:**
- Environment Setup
- Setup​
- Builds​
- Faster builds​
- Services​
- Nautilus CLI developer guide​
- Introduction​
- Install​
- Commands​
  - Database​

For development we recommend using the PyCharm Professional edition IDE, as it interprets Cython syntax. Alternatively, you could use Visual Studio Code with a Cython extension.

uv is the preferred tool for handling all Python virtual environments and dependencies.

pre-commit is used to automatically run various checks, auto-formatters and linting tools at commit.

NautilusTrader uses increasingly more Rust, so Rust should be installed on your system as well (installation guide).

NautilusTrader must compile and run on Linux, macOS, and Windows. Please keep portability in mind (use std::path::Path, avoid Bash-isms in shell scripts, etc.).

The following steps are for UNIX-like systems, and only need to be completed once.

If you're developing and iterating frequently, then compiling in debug mode is often sufficient and significantly faster than a fully optimized build. To install in debug mode, use:

Before opening a pull-request run the formatting and lint suite locally so that CI passes on the first attempt:

Make sure the Rust compiler reports zero errors – broken builds slow everyone down.

Since .cargo/config.toml is tracked, configure git to skip any local modifications:

To restore tracking: git update-index --no-skip-worktree .cargo/config.toml

Following any changes to .rs, .pyx or .pxd files, you can re-compile by running:

If you're developing and iterating frequently, then compiling in debug mode is often sufficient and significantly faster than a fully optimized build. To compile in debug mode, use:

The cranelift backends reduces build time significantly for dev, testing and IDE checks. However, cranelift is available on the nightly toolchain and needs extra configuration. Install the nightly toolchain

Activate the nightly feature and use "cranelift" backend for dev and testing profiles in workspace Cargo.toml. You can apply the below patch using git apply <patch>. You can remove it using git apply -R <patch> before pushing changes.

Pass RUSTUP_TOOLCHAIN=nightly when running make build-debug like commands and include it in all rust analyzer settings for faster builds and IDE checks.

You can use docker-compose.yml file located in .docker directory to bootstrap the Nautilus working environment. This will start the following services:

If you only want specific services running (like postgres for example), you can start them with command:

Please use this as development environment only. For production, use a proper and more secure setup.

After the services has been started, you must log in with psql cli to create nautilus Postgres database. To do that you can run, and type POSTGRES_PASSWORD from docker service setup

After you have logged in as postgres administrator, run CREATE DATABASE command with target db name (we use nautilus):

The Nautilus CLI is a command-line interface tool for interacting with the NautilusTrader ecosystem. It offers commands for managing the PostgreSQL database and handling various trading operations.

The Nautilus CLI command is only supported on UNIX-like systems.

You can install the Nautilus CLI using the below Makefile target, which leverages cargo install under the hood. This will place the nautilus binary in your system's PATH, assuming Rust's cargo is properly configured.

You can run nautilus --help to view the CLI structure and available command groups:

These commands handle bootstrapping the PostgreSQL database. To use them, you need to provide the correct connection configuration, either through command-line arguments or a .env file located in the root directory or the current working directory.

List of commands are:

Rust analyzer is a popular language server for Rust and has integrations for many IDEs. It is recommended to configure rust analyzer to have same environment variables as make build-debug for faster compile times. Below tested configurations for VSCode and Astro Nvim are provided. For more information see PR or rust analyzer config docs.

You can add the following settings to your VSCode settings.json file:

You can add the following to your astro lsp config file:

**Examples:**

Example 1 (bash):
```bash
uv sync --active --all-groups --all-extras
```

Example 2 (bash):
```bash
make install
```

Example 3 (bash):
```bash
make install-debug
```

Example 4 (bash):
```bash
pre-commit install
```

---

## Testing

**URL:** https://nautilustrader.io/docs/latest/developer_guide/testing

**Contents:**
- Testing
- Running tests​
  - Python tests​
  - Rust tests​
  - IDE integration​
- Test style​
- Waiting for asynchronous effects​
- Mocks​
- Code coverage​
- Excluded code coverage​

Our automated tests serve as executable specifications for the trading platform. A healthy suite documents intended behaviour, gives contributors confidence to refactor, and catches regressions before they reach production. Tests also double as living examples that clarify complex flows and provide rapid CI feedback so issues surface early.

The suite covers these categories:

Performance tests help evolve performance-critical components.

Run tests with pytest, our primary test runner. Use parametrized tests and fixtures (e.g., @pytest.mark.parametrize) to avoid repetitive code and improve clarity.

From the repository root:

For performance tests:

When waiting for background work to complete, prefer the polling helpers await eventually(...) from nautilus_trader.test_kit.functions and wait_until_async(...) from nautilus_common::testing instead of arbitrary sleeps. They surface failures faster and reduce flakiness in CI because they stop as soon as the condition is satisfied or time out with a useful error.

Use lightweight collaborators as mocks to keep the suite simple and avoid heavy mocking frameworks. We still rely on MagicMock in specific cases where it provides the most convenient tooling.

We generate coverage reports with coverage and publish them to codecov.

Aim for high coverage without sacrificing appropriate error handling or causing "test induced damage" to the architecture.

Some branches remain untestable without modifying production behaviour. For example, a final condition in a defensive if-else block may only trigger for unexpected values; leave these checks in place so future changes can exercise them if needed.

Design-time exceptions can also be impractical to test, so 100% coverage is not the target.

We use pragma: no cover comments to exclude code from coverage when tests would be redundant. Typical examples include:

Such tests are expensive to maintain because they must track refactors while providing little value. Ensure concrete implementations of abstract methods remain fully covered. Remove pragma: no cover when it no longer applies and restrict its use to the cases above.

Use the default test configuration to debug Rust tests.

To run the full suite with debug symbols for later, run make cargo-test-debug instead of make cargo-test.

In IntelliJ IDEA, adjust the run configuration for parametrised #[rstest] cases so it reads test --package nautilus-model --lib data::bar::tests::test_get_time_bar_start::case_1 (remove -- --exact and append ::case_n where n starts at 1). This workaround matches the behaviour explained here.

In VS Code you can pick the specific test case to debug directly.

This workflow lets you debug Python and Rust code simultaneously from a Jupyter notebook inside VS Code.

Install these VS Code extensions: Rust Analyzer, CodeLLDB, Python, Jupyter.

This command creates the required VS Code debugging configurations and starts a debugpy server for the Python debugger.

By default setup_debugging() expects the .vscode folder one level above the nautilus_trader root directory. Adjust the target location if your workspace layout differs.

Run Jupyter notebook cells that call Rust functions. The debugger stops at breakpoints in both Python and Rust code.

setup_debugging() creates these VS Code configurations:

Open and run the example notebook: debug_mixed_jupyter.ipynb.

**Examples:**

Example 1 (bash):
```bash
make pytest# oruv run --active --no-sync pytest --new-first --failed-first# or simplypytest
```

Example 2 (bash):
```bash
make test-performance# oruv run --active --no-sync pytest tests/performance_tests --benchmark-disable-gc --codspeed
```

Example 3 (bash):
```bash
make cargo-test# orcargo nextest run --workspace --features "python,ffi,high-precision,defi" --cargo-profile nextest
```

Example 4 (bash):
```bash
cd nautilus_trader && make build-debug-pyo3
```

---

## Developer Guide

**URL:** https://nautilustrader.io/docs/latest/developer_guide

**Contents:**
- Developer Guide
- Contents​

Welcome to the developer guide for NautilusTrader!

Here you'll find guidance on developing and extending NautilusTrader to meet your trading needs or to contribute improvements back to the project.

This guide is structured so that automated tooling can consume it alongside human readers.

We believe in using the right tool for the job. The overall design philosophy is to fully utilize the high level power of Python, with its rich eco-system of frameworks and libraries, whilst overcoming some of its inherent shortcomings in performance and lack of built-in type safety (with it being an interpreted dynamic language).

One of the advantages of Cython is that allocation and freeing of memory is handled by the C code generator during the ‘cythonization’ step of the build (unless you’re specifically utilizing some of its lower level features).

This approach combines Python’s simplicity with near-native C performance via compiled extensions.

The main development and runtime environment we are working in is Python. With the introduction of Cython throughout the production codebase in .pyx and .pxd files, it's important to be aware of how the CPython implementation of Python interacts with the underlying CPython API, and the NautilusTrader C extension modules which Cython produces.

We recommend a thorough review of the Cython docs to familiarize yourself with some of its core concepts, and where C typing is being used.

It's not necessary to become a C language expert, however it's helpful to understand how Cython C syntax is used in function and method definitions, in local code blocks, and the common primitive C types and how these map to their corresponding PyObject types.

---
