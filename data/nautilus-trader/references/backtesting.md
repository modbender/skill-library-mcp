# Nautilus_Trader - Backtesting

**Pages:** 1

---

## Persistence

**URL:** https://nautilustrader.io/docs/latest/api_reference/persistence

**Contents:**
- Persistence
  - class BaseDataCatalog​
    - abstractmethod classmethod from_env() → BaseDataCatalog​
    - abstractmethod classmethod from_uri(uri: str, storage_options: dict[str, str] | None = None) → BaseDataCatalog​
    - instruments(instrument_type: type | None = None, instrument_ids: list[str] | None = None, **kwargs: Any) → list[Instrument]​
    - instrument_status(instrument_ids: list[str] | None = None, **kwargs: Any) → list[InstrumentStatus]​
    - instrument_closes(instrument_ids: list[str] | None = None, **kwargs: Any) → list[InstrumentClose]​
    - order_book_deltas(instrument_ids: list[str] | None = None, batched: bool = False, **kwargs: Any) → list[OrderBookDelta] | list[OrderBookDeltas]​
    - order_book_depth10(instrument_ids: list[str] | None = None, **kwargs: Any) → list[OrderBookDepth10]​
    - quote_ticks(instrument_ids: list[str] | None = None, **kwargs: Any) → list[QuoteTick]​

The persistence subpackage handles data storage and retrieval, mainly to support backtesting.

Provides a abstract base class for a queryable data catalog.

FeatherFile(path, class_name)

Alias for field number 0

Alias for field number 1

Return number of occurrences of value.

Return first index of value.

Raises ValueError if the value is not present.

Bases: BaseDataCatalog

Provides a queryable data catalog persisted to files in Parquet (Arrow) format.

The data catalog is not threadsafe. Using it in a multithreaded environment can lead to unexpected behavior.

Create a data catalog instance by accessing the ‘NAUTILUS_PATH’ environment variable.

Create a data catalog instance from the given uri with optional storage options.

Write the given data to the catalog.

The function categorizes the data based on their class name and, when applicable, their associated instrument ID. It then delegates the actual writing process to the write_chunk method.

Any existing data which already exists under a filename will be overwritten.

Extend the timestamp range of an existing parquet file by renaming it.

This method looks for parquet files that are adjacent to the specified timestamp range and renames them to include the new range. It’s useful for extending existing files without having to rewrite them when a query returns an empty list.

Reset the filenames of all parquet files in the catalog to match their actual content timestamps.

This method identifies all leaf directories in the catalog that contain parquet files and resets their filenames to accurately reflect the minimum and maximum timestamps of the data they contain. It does this by examining the parquet metadata for each file and renaming the file to follow the pattern ‘{first_timestamp}-{last_timestamp}.parquet’.

This is useful when file names may have become inconsistent with their content, for example after manual file operations or data corruption. It ensures that query operations that rely on filename-based filtering will work correctly.

Reset the filenames of parquet files for a specific data class and instrument ID.

This method resets the filenames of parquet files for the specified data class and identifier to accurately reflect the minimum and maximum timestamps of the data they contain. It examines the parquet metadata for each file and renames the file to follow the pattern ‘{first_timestamp}-{last_timestamp}.parquet’.

Consolidate all parquet files across the entire catalog within the specified time range.

This method identifies all leaf directories in the catalog that contain parquet files and consolidates them. A leaf directory is one that contains files but no subdirectories. This is a convenience method that effectively calls consolidate_data for all data types and instrument IDs in the catalog.

Consolidate multiple parquet files for a specific data class and instrument ID into a single file.

This method identifies all parquet files within the specified time range for the given data class and instrument ID, then combines them into a single parquet file. This helps improve query performance and reduces storage overhead by eliminating small fragmented files.

Consolidate all parquet files across the entire catalog by splitting them into fixed time periods.

This method identifies all leaf directories in the catalog that contain parquet files and consolidates them by period. A leaf directory is one that contains files but no subdirectories. This is a convenience method that effectively calls consolidate_data_by_period for all data types and instrument IDs in the catalog.

Consolidate data files by splitting them into fixed time periods.

This method queries data by period and writes consolidated files immediately, using the skip_disjoint_check parameter to avoid interval conflicts during the consolidation process. When start/end boundaries intersect existing files, the function automatically splits those files to preserve all data.

Delete data within a specified time range across the entire catalog.

This method identifies all leaf directories in the catalog that contain parquet files and deletes data within the specified time range from each directory. A leaf directory is one that contains files but no subdirectories. This is a convenience method that effectively calls delete_data_range for all data types and instrument IDs in the catalog.

Delete data within a specified time range for a specific data class and instrument.

This method identifies all parquet files that intersect with the specified time range and handles them appropriately:

Query the catalog for data matching the specified criteria.

This method retrieves data from the catalog based on the provided filters. It automatically selects the appropriate query implementation (Rust or PyArrow) based on the data class and filesystem protocol.

Create or update a DataBackendSession for querying data using the Rust backend.

This method is used internally by the query_rust method to set up the query session. It identifies the relevant parquet files and adds them to the session with appropriate SQL queries.

Returns: The updated or newly created session.

Return type: DataBackendSession

Raises: RuntimeError – If the data class is not supported by the Rust backend.

Find the missing time intervals for a specific data class and instrument ID.

This method identifies the gaps in the data between the specified start and end timestamps. It’s useful for determining what data needs to be fetched or generated to complete a time series.

Get the time intervals covered by parquet files for a specific data class and instrument ID.

This method retrieves the timestamp ranges of all parquet files for the specified data class and instrument ID. Each parquet file in the catalog follows a naming convention of ‘{start_timestamp}-{end_timestamp}.parquet’, which this method parses to determine the available data intervals.

List all data types available in the catalog.

List all backtest run IDs available in the catalog.

List all live run IDs available in the catalog.

Read data from a live run.

This method reads all data associated with a specific live run instance from feather files.

Read data from a backtest run.

This method reads all data associated with a specific backtest run instance from feather files.

Convert stream data from feather files to parquet files.

This method reads data from feather files generated during a backtest or live run and writes it to the catalog in parquet format. It’s useful for converting temporary stream data into a more permanent and queryable format.

BarDataWrangler(BarType bar_type, Instrument instrument)

Provides a means of building lists of Nautilus Bar objects.

Process the given bar dataset into Nautilus Bar objects.

Expects columns [‘open’, ‘high’, ‘low’, ‘close’, ‘volume’] with ‘timestamp’ index. Note: The ‘volume’ column is optional, if one does not exist then will use the default_volume.

OrderBookDeltaDataWrangler(Instrument instrument)

Provides a means of building lists of Nautilus OrderBookDelta objects.

Process the given order book dataset into Nautilus OrderBookDelta objects.

QuoteTickDataWrangler(Instrument instrument)

Provides a means of building lists of Nautilus QuoteTick objects.

Process the given tick dataset into Nautilus QuoteTick objects.

Expects columns [‘bid_price’, ‘ask_price’] with ‘timestamp’ index. Note: The ‘bid_size’ and ‘ask_size’ columns are optional, will then use the default_volume.

Process the given bar datasets into Nautilus QuoteTick objects.

Expects columns [‘open’, ‘high’, ‘low’, ‘close’, ‘volume’] with ‘timestamp’ index. Note: The ‘volume’ column is optional, will then use the default_volume.

TradeTickDataWrangler(Instrument instrument)

Provides a means of building lists of Nautilus TradeTick objects.

Process the given trade tick dataset into Nautilus TradeTick objects.

Process the given bar datasets into Nautilus TradeTick objects.

Expects columns [‘open’, ‘high’, ‘low’, ‘close’, ‘volume’] with ‘timestamp’ index. Note: The ‘volume’ column is optional, will then use the default_volume.

Merge bid and ask data into a single DataFrame with prefixed column names.

bid_data (pd.DataFrame) – The DataFrame containing bid data.

ask_data (pd.DataFrame) – The DataFrame containing ask data.

pd.DataFrame – A merged DataFrame with columns prefixed by ‘

’ for ask data, joined on their indexes.

Calculate and potentially randomize the time offsets for bar prices based on the closeness of the timestamp.

Convert raw volume data to quarter precision.

Preprocess financial bar data to a standardized format.

Ensures the DataFrame index is labeled as “timestamp”, converts the index to UTC, removes time zone awareness, drops rows with NaN values in critical columns, and optionally scales the data.

Provides a stream writer of Nautilus objects into feather files with rotation capabilities.

Write the object to the stream.

Flush all stream writers if current time greater than the next flush interval.

Flush all stream writers.

Flush and close all stream writers.

Get information about the current files being written.

Get the expected time for the next file rotation.

Return whether all file streams are closed.

---
