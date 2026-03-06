# Nautilus_Trader - Api

**Pages:** 17

---

## Serialization

**URL:** https://nautilustrader.io/docs/latest/api_reference/serialization

**Contents:**
- Serialization
  - register_serializable_type(type cls: type, to_dict: Callable[[Any], dict[str, Any]], from_dict: Callable[[dict[str, Any]], Any]) → void​
  - class MsgSpecSerializer​
    - deserialize(self, bytes obj_bytes)​
    - serialize(self, obj) → bytes​
    - timestamps_as_iso8601​
    - timestamps_as_str​
  - class Serializer​
    - WARNING​
    - deserialize(self, bytes obj_bytes)​

The serialization subpackage groups all serialization components and serializer implementations.

Base classes are defined which can allow for other serialization implementations beside the built-in specification serializers.

Register the given type with the global serialization type maps.

The type will also be registered as an external publishable type and will be published externally on the message bus unless also added to the MessageBusConfig.types_filter.

MsgSpecSerializer(encoding, bool timestamps_as_str=False, bool timestamps_as_iso8601=False)

Provides a serializer for either the ‘MessagePack’ or ‘JSON’ specifications.

Deserialize the given MessagePack specification bytes to an object.

Serialize the given object to MessagePack specification bytes.

If the serializer converts timestamp int64_t to ISO 8601 strings.

If the serializer converts timestamp int64_t to integer strings.

The base class for all serializers.

This class should not be used directly, but through a concrete subclass.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Register the given type with the global serialization type maps.

The type will also be registered as an external publishable type and will be published externally on the message bus unless also added to the MessageBusConfig.types_filter.

---

## Instruments

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/instruments

**Contents:**
- Instruments
  - class BettingInstrument​
    - betting_type​
    - competition_id​
    - competition_name​
    - event_country_code​
    - event_id​
    - event_name​
    - event_open_date​
    - event_type_id​

Defines tradable asset/contract instruments with specific properties dependent on the asset class and instrument class.

BettingInstrument(str venue_name, int event_type_id, str event_type_name, int competition_id, str competition_name, int event_id, str event_name, str event_country_code, datetime event_open_date, str betting_type, str market_id, str market_name, datetime market_start_time, str market_type, int selection_id, str selection_name, str currency, float selection_handicap, int8_t price_precision, int8_t size_precision, uint64_t ts_event, uint64_t ts_init, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents an instrument in a betting market.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

BinaryOption(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str outcome=None, str description=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic binary option instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The market description.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

values : The values to initialize the instrument with.

The binary outcome of the market.

Return a dictionary representation of this object.

Cfd(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency quote_currency, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, Currency base_currency: Currency | None = None, Quantity lot_size: Quantity | None = None, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a Contract for Difference (CFD) instrument.

Can represent both Fiat FX and Cryptocurrency pairs.

The base currency for the instrument.

Return an instrument from the given initialization values.

The instruments International Securities Identification Number (ISIN).

Return a dictionary representation of this object.

Commodity(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency quote_currency, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, Currency base_currency: Currency | None = None, Quantity lot_size: Quantity | None = None, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a commodity instrument in a spot/cash market.

Return an instrument from the given initialization values.

The instruments International Securities Identification Number (ISIN).

Return a dictionary representation of this object.

CryptoFuture(InstrumentId instrument_id, Symbol raw_symbol, Currency underlying, Currency quote_currency, Currency settlement_currency, bool is_inverse, uint64_t activation_ns, uint64_t expiration_ns, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, multiplier=Quantity.from_int_c(1), lot_size=Quantity.from_int_c(1), Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a deliverable futures contract instrument, with crypto assets as underlying and for settlement.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython crypto future instrument converted from the given pyo3 Rust object.

Return the instruments base currency (underlying).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

If the instrument is quanto.

Calculate the notional value.

Result will be in quote currency for standard instruments, underlying currency for inverse instruments, or settlement currency for quanto instruments.

The settlement currency for the contract.

Return a dictionary representation of this object.

The underlying asset for the contract.

CryptoOption(InstrumentId instrument_id, Symbol raw_symbol, Currency underlying, Currency quote_currency, Currency settlement_currency, bool is_inverse, OptionKind option_kind, Price strike_price, uint64_t activation_ns, uint64_t expiration_ns, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, Quantity multiplier=Quantity.from_int_c(1), Quantity lot_size=Quantity.from_int_c(1), Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents an option instrument with crypto assets as underlying and for settlement.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython option contract instrument converted from the given pyo3 Rust object.

Return the instruments base currency (underlying).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

Calculate the notional value.

Result will be in quote currency for standard instruments, or underlying currency for inverse instruments.

The option kind (PUT | CALL) for the contract.

The settlement currency for the instrument.

The strike price for the contract.

Return a dictionary representation of this object.

The underlying asset for the contract.

CryptoPerpetual(InstrumentId instrument_id, Symbol raw_symbol, Currency base_currency, Currency quote_currency, Currency settlement_currency, bool is_inverse, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, multiplier=Quantity.from_int_c(1), lot_size=Quantity.from_int_c(1), Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a crypto perpetual futures contract instrument (a.k.a. perpetual swap).

The base currency for the instrument.

Return an instrument from the given initialization values.

Return the instruments base currency.

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

If the instrument is quanto.

Calculate the notional value.

Result will be in quote currency for standard instruments, base currency for inverse instruments, or settlement currency for quanto instruments.

The settlement currency for the instrument.

Return a dictionary representation of this object.

CurrencyPair(InstrumentId instrument_id, Symbol raw_symbol, Currency base_currency, Currency quote_currency, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, multiplier=Quantity.from_int_c(1), Quantity lot_size: Quantity | None = None, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic currency pair instrument in a spot/cash market.

Can represent both Fiat FX and Cryptocurrency pairs.

The base currency for the instrument.

Return an instrument from the given initialization values.

Return the instruments base currency.

Return a dictionary representation of this object.

Equity(InstrumentId instrument_id, Symbol raw_symbol, Currency currency, int price_precision, Price price_increment, Quantity lot_size, uint64_t ts_event, uint64_t ts_init, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str isin: str | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic equity instrument.

Return an instrument from the given initialization values.

Return legacy Cython equity instrument converted from the given pyo3 Rust object.

The instruments International Securities Identification Number (ISIN).

Return a dictionary representation of this object.

FuturesContract(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, Price price_increment, Quantity multiplier, Quantity lot_size, str underlying, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str exchange=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic deliverable futures contract instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The exchange ISO 10383 Market Identifier Code (MIC) where the instrument trades.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython futures contract instrument converted from the given pyo3 Rust object.

Return a dictionary representation of this object.

The underlying asset for the contract.

FuturesSpread(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, Price price_increment, Quantity multiplier, Quantity lot_size, str underlying, str strategy_type, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str exchange=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic deliverable futures spread instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The exchange ISO 10383 Market Identifier Code (MIC) where the instrument trades.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython futures spread instrument converted from the given pyo3 Rust object.

The strategy type of the spread.

Return a dictionary representation of this object.

The underlying asset for the spread.

IndexInstrument(InstrumentId instrument_id, Symbol raw_symbol, Currency currency, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, str tick_scheme_name=None, dict info=None) -> None

Represents a spot index instrument (also known as a cash index).

A spot index is calculated from its underlying constituents. It is not directly tradable. To gain exposure you would typically use index futures, ETFs, or CFDs.

Return an instrument from the given initialization values.

Return legacy Cython index instrument converted from the given pyo3 Rust object.

Return a dictionary representation of this object.

Instrument(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, InstrumentClass instrument_class, Currency quote_currency, bool is_inverse, int price_precision, int size_precision, Quantity size_increment, Quantity multiplier, margin_init: Decimal, margin_maint: Decimal, maker_fee: Decimal, taker_fee: Decimal, uint64_t ts_event, uint64_t ts_init, Price price_increment: Price | None = None, Quantity lot_size: Quantity | None = None, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, str tick_scheme_name=None, dict info=None) -> None

The base class for all instruments.

Represents a tradable instrument. This class can be used to define an instrument, or act as a parent class for more specific instruments.

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

Return the instruments base currency (if applicable).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, or base currency for inverse instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the instruments trading venue.

OptionContract(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, Price price_increment, Quantity multiplier, Quantity lot_size, str underlying, OptionKind option_kind, Price strike_price, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str exchange=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic option contract instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The exchange ISO 10383 Market Identifier Code (MIC) where the instrument trades.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython option contract instrument converted from the given pyo3 Rust object.

The option kind (PUT | CALL) for the contract.

The strike price for the contract.

Return a dictionary representation of this object.

The underlying asset for the contract.

OptionSpread(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, Price price_increment, Quantity multiplier, Quantity lot_size, str underlying, str strategy_type, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str exchange=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic option spread instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The exchang ISO 10383 Market Identifier Code (MIC) where the instrument trades.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython option spread instrument converted from the given pyo3 Rust object.

The strategy type of the spread.

Return a dictionary representation of this object.

The underlying asset for the contract.

SyntheticInstrument(Symbol symbol, uint8_t price_precision, list components, str formula, uint64_t ts_event, uint64_t ts_init) -> None

Represents a synthetic instrument with prices derived from component instruments using a formula.

The id for the synthetic will become {symbol}.{SYNTH}.

All component instruments should already be defined and exist in the cache prior to defining a new synthetic instrument.

Calculate the price of the synthetic instrument from the given inputs.

Change the internal derivation formula for the synthetic instrument.

Return the components of the synthetic instrument.

Return the synthetic instrument internal derivation formula.

Return an instrument from the given initialization values.

Return the minimum price increment (tick size) for the synthetic instrument.

Return the precision for the synthetic instrument.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

BettingInstrument(str venue_name, int event_type_id, str event_type_name, int competition_id, str competition_name, int event_id, str event_name, str event_country_code, datetime event_open_date, str betting_type, str market_id, str market_name, datetime market_start_time, str market_type, int selection_id, str selection_name, str currency, float selection_handicap, int8_t price_precision, int8_t size_precision, uint64_t ts_event, uint64_t ts_init, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents an instrument in a betting market.

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

Return an instrument from the given initialization values.

Return the fully qualified name for the Data class.

Return the instruments base currency (if applicable).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the instruments trading venue.

CryptoPerpetual(InstrumentId instrument_id, Symbol raw_symbol, Currency base_currency, Currency quote_currency, Currency settlement_currency, bool is_inverse, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, multiplier=Quantity.from_int_c(1), lot_size=Quantity.from_int_c(1), Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a crypto perpetual futures contract instrument (a.k.a. perpetual swap).

The asset class of the instrument.

The base currency for the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

Return an instrument from the given initialization values.

Return the fully qualified name for the Data class.

Return the instruments base currency.

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

If the instrument is quanto.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, base currency for inverse instruments, or settlement currency for quanto instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The settlement currency for the instrument.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the instruments trading venue.

CryptoFuture(InstrumentId instrument_id, Symbol raw_symbol, Currency underlying, Currency quote_currency, Currency settlement_currency, bool is_inverse, uint64_t activation_ns, uint64_t expiration_ns, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, multiplier=Quantity.from_int_c(1), lot_size=Quantity.from_int_c(1), Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a deliverable futures contract instrument, with crypto assets as underlying and for settlement.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython crypto future instrument converted from the given pyo3 Rust object.

Return the fully qualified name for the Data class.

Return the instruments base currency (underlying).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

If the instrument is quanto.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, underlying currency for inverse instruments, or settlement currency for quanto instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The settlement currency for the contract.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The underlying asset for the contract.

Return the instruments trading venue.

CurrencyPair(InstrumentId instrument_id, Symbol raw_symbol, Currency base_currency, Currency quote_currency, int price_precision, int size_precision, Price price_increment, Quantity size_increment, uint64_t ts_event, uint64_t ts_init, multiplier=Quantity.from_int_c(1), Quantity lot_size: Quantity | None = None, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic currency pair instrument in a spot/cash market.

Can represent both Fiat FX and Cryptocurrency pairs.

The asset class of the instrument.

The base currency for the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

Return an instrument from the given initialization values.

Return the fully qualified name for the Data class.

Return the instruments base currency.

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, or base currency for inverse instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the instruments trading venue.

Equity(InstrumentId instrument_id, Symbol raw_symbol, Currency currency, int price_precision, Price price_increment, Quantity lot_size, uint64_t ts_event, uint64_t ts_init, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str isin: str | None = None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic equity instrument.

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

Return an instrument from the given initialization values.

Return legacy Cython equity instrument converted from the given pyo3 Rust object.

Return the fully qualified name for the Data class.

Return the instruments base currency (if applicable).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The instruments International Securities Identification Number (ISIN).

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, or base currency for inverse instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the instruments trading venue.

FuturesContract(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, Price price_increment, Quantity multiplier, Quantity lot_size, str underlying, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str exchange=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic deliverable futures contract instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

The exchange ISO 10383 Market Identifier Code (MIC) where the instrument trades.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython futures contract instrument converted from the given pyo3 Rust object.

Return the fully qualified name for the Data class.

Return the instruments base currency (if applicable).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, or base currency for inverse instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The underlying asset for the contract.

Return the instruments trading venue.

OptionContract(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, Currency currency, int price_precision, Price price_increment, Quantity multiplier, Quantity lot_size, str underlying, OptionKind option_kind, Price strike_price, uint64_t activation_ns, uint64_t expiration_ns, uint64_t ts_event, uint64_t ts_init, margin_init: Decimal | None = None, margin_maint: Decimal | None = None, maker_fee: Decimal | None = None, taker_fee: Decimal | None = None, str exchange=None, str tick_scheme_name=None, dict info=None) -> None

Represents a generic option contract instrument.

UNIX timestamp (nanoseconds) for contract activation.

Return the contract activation timestamp (UTC).

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

The exchange ISO 10383 Market Identifier Code (MIC) where the instrument trades.

UNIX timestamp (nanoseconds) for contract expiration.

Return the contract expiration timestamp (UTC).

Return an instrument from the given initialization values.

Return legacy Cython option contract instrument converted from the given pyo3 Rust object.

Return the fully qualified name for the Data class.

Return the instruments base currency (if applicable).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, or base currency for inverse instruments.

The option kind (PUT | CALL) for the contract.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

The strike price for the contract.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The underlying asset for the contract.

Return the instruments trading venue.

SyntheticInstrument(Symbol symbol, uint8_t price_precision, list components, str formula, uint64_t ts_event, uint64_t ts_init) -> None

Represents a synthetic instrument with prices derived from component instruments using a formula.

The id for the synthetic will become {symbol}.{SYNTH}.

All component instruments should already be defined and exist in the cache prior to defining a new synthetic instrument.

Calculate the price of the synthetic instrument from the given inputs.

Change the internal derivation formula for the synthetic instrument.

Return the components of the synthetic instrument.

Return the synthetic instrument internal derivation formula.

Return an instrument from the given initialization values.

Return the fully qualified name for the Data class.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return the minimum price increment (tick size) for the synthetic instrument.

Return the precision for the synthetic instrument.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Instrument(InstrumentId instrument_id, Symbol raw_symbol, AssetClass asset_class, InstrumentClass instrument_class, Currency quote_currency, bool is_inverse, int price_precision, int size_precision, Quantity size_increment, Quantity multiplier, margin_init: Decimal, margin_maint: Decimal, maker_fee: Decimal, taker_fee: Decimal, uint64_t ts_event, uint64_t ts_init, Price price_increment: Price | None = None, Quantity lot_size: Quantity | None = None, Quantity max_quantity: Quantity | None = None, Quantity min_quantity: Quantity | None = None, Money max_notional: Money | None = None, Money min_notional: Money | None = None, Price max_price: Price | None = None, Price min_price: Price | None = None, str tick_scheme_name=None, dict info=None) -> None

The base class for all instruments.

Represents a tradable instrument. This class can be used to define an instrument, or act as a parent class for more specific instruments.

The asset class of the instrument.

Return an instrument from the given initialization values.

Return a dictionary representation of this object.

Calculate the base asset quantity from the given quote asset quantity and last price.

Return the fully qualified name for the Data class.

Return the instruments base currency (if applicable).

Return the currency used for PnL calculations for the instrument.

Return the currency used to settle a trade of the instrument.

The raw info for the instrument.

The class of the instrument.

If the quantity is expressed in quote currency.

Determine if the current class is a signal type, optionally checking for a specific signal name.

The rounded lot unit size (standard/board) for the instrument.

Return a new price from the given value using the instruments price precision.

Return a new quantity from the given value using the instruments size precision.

The fee rate for liquidity makers as a percentage of order value (where 1.0 is 100%).

The initial (order) margin rate for the instrument.

The maintenance (position) margin rate for the instrument.

The maximum notional order value for the instrument.

The maximum printable price for the instrument.

The maximum order quantity for the instrument.

The minimum notional order value for the instrument.

The minimum printable price for the instrument.

The minimum order quantity for the instrument.

The contract multiplier for the instrument (determines tick value).

Return the price n ask ticks away from value.

If a given price is between two ticks, n=0 will find the nearest ask tick.

Return a list of prices up to num_ticks ask ticks away from value.

If a given price is between two ticks, the first price will be the nearest ask tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Return the price n bid ticks away from value.

If a given price is between two ticks, n=0 will find the nearest bid tick.

Return a list of prices up to num_ticks bid ticks away from value.

If a given price is between two ticks, the first price will be the nearest bid tick. Returns as many valid ticks as possible up to num_ticks. Will return an empty list if no valid ticks can be generated.

Calculate the notional value.

Result will be in quote currency for standard instruments, or base currency for inverse instruments.

The minimum price increment or tick size for the instrument.

The price precision of the instrument.

The quote currency for the instrument.

The raw/local/native symbol for the instrument, assigned by the venue.

Set the tick scheme for the instrument.

Sets both the tick_scheme_name and the corresponding tick scheme implementation used for price rounding and tick calculations.

This will override any previously set tick scheme, including the tick_scheme_name field.

The minimum size increment for the instrument.

The size precision of the instrument.

Return the instruments ticker symbol.

The fee rate for liquidity takers as a percentage of order value (where 1.0 is 100%).

The tick scheme name.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the instruments trading venue.

**Examples:**

Example 1 (pycon):
```pycon
>>> make_symbol(market_id="1.201070830", selection_id=123456, selection_handicap=null_handicap())Symbol('1-201070830-123456-None')
```

---

## Common

**URL:** https://nautilustrader.io/docs/latest/api_reference/common

**Contents:**
- Common
  - class Environment​
    - BACKTEST = 'backtest'​
    - SANDBOX = 'sandbox'​
    - LIVE = 'live'​
  - class Actor​
    - WARNING​
    - active_task_ids(self) → list​
    - add_synthetic(self, SyntheticInstrument synthetic) → void​
    - cache​

The common subpackage provides generic/common parts for assembling the frameworks various components.

More domain specific concepts are introduced above the core base layer. The ID cache is implemented, a base Clock with Test and Live implementations which can control many Timer instances.

Trading domain specific components for generating Order and Identifier objects, common logging components, a high performance Queue and UUID4 factory.

Represents the environment context for a Nautilus system.

The Actor class allows traders to implement their own customized components.

A user can inherit from Actor and optionally override any of the “on” named event handler methods. The class is not entirely initialized in a stand-alone way, the intended usage is to pass actors to a Trader so that they can be fully “wired” into the platform. Exceptions will be raised if an Actor attempts to operate without a managing Trader instance.

Actor(config: ActorConfig | None = None) -> None

The base class for all actor components.

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

OrderFactory(TraderId trader_id, StrategyId strategy_id, Clock clock, CacheFacade cache: CacheFacade | None = None, bool use_uuid_client_order_ids=False, bool use_hyphens_in_client_order_ids=True) -> None

A factory class which provides different order types.

The TraderId tag and StrategyId tag will be inserted into all IDs generated.

Create a bracket order with optional entry of take-profit order types.

The stop-loss order will always be STOP_MARKET.

Return a new order list containing the given orders.

Generate and return a new client order ID.

The identifier will be the next in the logical sequence.

Generate and return a new order list ID.

The identifier will be the next in the logical sequence.

Return the client order ID count for the factory.

Return the order list ID count for the factory.

Create a new LIMIT order.

Create a new LIMIT_IF_TOUCHED (LIT) conditional order.

Create a new MARKET order.

Create a new MARKET_IF_TOUCHED (MIT) conditional order.

Create a new MARKET order.

Reset the order factory.

All stateful fields are reset to their initial value.

Set the internal order ID generator count to the given count.

System method (not intended to be called by user code).

Set the internal order list ID generator count to the given count.

System method (not intended to be called by user code).

Create a new STOP_LIMIT conditional order.

Create a new STOP_MARKET conditional order.

The order factories trading strategy ID.

The order factories trader ID.

Create a new TRAILING_STOP_LIMIT conditional order.

Create a new TRAILING_STOP_MARKET conditional order.

If hyphens should be used in generated client order ID values.

If UUID4’s should be used for client order ID values.

The base class for all clocks.

This class should not be used directly, but through a concrete subclass.

Cancel the timer corresponding to the given label.

Return the current datetime of the clock in the given local timezone.

Find a particular timer.

Register the given handler as the clocks default handler.

Set a time alert for the given time.

When the time is reached the handler will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

If alert_time is in the past or at current time, then an immediate time event will be generated (rather than being invalid and failing a condition check).

Set a time alert for the given time.

When the time is reached the handler will be passed the TimeEvent containing the timers unique name. If no callback is passed then the default handler (if registered) will receive the TimeEvent.

If alert_time_ns is in the past or at current time, then an immediate time event will be generated (rather than being invalid and failing a condition check).

The timer will run from the start time (optionally until the stop time). When the intervals are reached the handlers will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

The timer will run from the start time until the stop time. When the intervals are reached the handlers will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

Return the count of active timers running in the clock.

Return the names of active timers running in the clock.

Return the current UNIX timestamp in seconds.

Return the current UNIX timestamp in milliseconds (ms).

Return the current UNIX timestamp in nanoseconds (ns).

Return the current UNIX timestamp in microseconds (μs).

Return the current time (UTC).

Component(Clock clock, TraderId trader_id=None, Identifier component_id=None, str component_name=None, MessageBus msgbus=None, config: NautilusConfig | None = None)

The base class for all system components.

A component is not considered initialized until a message bus is registered (this either happens when one is passed to the constructor, or when registered with a trader).

Thus, if the component does not receive a message bus through the constructor, then it will be in a PRE_INITIALIZED state, otherwise if one is passed then it will be in an INITIALIZED state.

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

Provides a generic component Finite-State Machine.

The default state transition table.

Provides a monotonic clock for live trading.

All times are tz-aware UTC.

Return the current datetime of the clock in the given local timezone.

Set a time alert for the given time.

When the time is reached the handler will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

If alert_time is in the past or at current time, then an immediate time event will be generated (rather than being invalid and failing a condition check).

The timer will run from the start time (optionally until the stop time). When the intervals are reached the handlers will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

Return the current time (UTC).

Provides a LogGuard which serves as a token to signal the initialization of the logging subsystem. It also ensures that the global logger is flushed of any buffered records when the instance is destroyed.

Logger(str name) -> None

Provides a logger adapter into the logging subsystem.

Log the given DEBUG level message.

Log the given ERROR level message.

Log the given exception including stack trace information.

Log the given INFO level message.

Return the name of the logger.

Log the given WARNING level message.

MessageBus(TraderId trader_id, Clock clock, UUID4 instance_id=None, str name=None, Serializer serializer=None, database: nautilus_pyo3.RedisMessageBusDatabase | None = None, config: Any | None = None) -> None

Provides a generic message bus to facilitate various messaging patterns.

The bus provides both a producer and consumer API for Pub/Sub, Req/Rep, as well as direct point-to-point messaging to registered endpoints.

Pub/Sub wildcard patterns for hierarchical topics are possible: : - * asterisk represents one or more characters in a pattern.

Given a topic and pattern potentially containing wildcard characters, i.e. * and ?, where ? can match any single character in the topic, and * can match any number of characters including zero characters.

The asterisk in a wildcard matches any character zero or more times. For example, comp* matches anything beginning with comp which means comp, complete, and computer are all matched.

A question mark matches a single character once. For example, c?mp matches camp and comp. The question mark can also be used more than once. For example, c??p would match both of the above examples and coop.

This message bus is not thread-safe and must be called from the same thread as the event loop.

Adds the given listener to the message bus.

Register the given type for external->internal message bus streaming.

Deregister the given handler from the endpoint address.

Dispose of the message bus which will close the internal channel and thread.

Return all endpoint addresses registered with the message bus.

If the message bus has a database backing.

If the message bus has subscribers for the give topic pattern.

Return if the given request_id is still pending a response.

Return whether the given type has been registered for external message streaming.

Return if topic and handler is subscribed to the message bus.

Does not consider any previous priority.

The count of messages published by the bus.

Publish the given message for the given topic.

Subscription handlers will receive the message in priority order (highest first).

Register the given handler to receive messages at the endpoint address.

The count of requests processed by the bus.

Handle the given request.

Will log an error if the correlation ID already exists.

The count of responses processed by the bus.

Handle the given response.

Will log an error if the correlation ID is not found.

Send the given message to the given endpoint address.

The count of messages sent through the bus.

The serializer for the bus.

Return all types registered for external streaming -> internal publishing.

Subscribe to the given message topic with the given callback handler.

Assigning priority handling is an advanced feature which shouldn’t normally be needed by most users. Only assign a higher priority to the subscription if you are certain of what you’re doing. If an inappropriate priority is assigned then the handler may receive messages before core system components have been able to process necessary calculations and produce potential side effects for logically sound behavior.

Return all subscriptions matching the given topic pattern.

Return all topics with active subscribers.

The trader ID associated with the bus.

Unsubscribe the given callback handler from the given message topic.

Subscription(str topic, handler: Callable[[Any], None], int priority=0)

Represents a subscription to a particular topic.

This is an internal class intended to be used by the message bus to organize topics and their subscribers.

The handler for the subscription.

The priority for the subscription.

The topic for the subscription.

Provides a monotonic clock for backtesting and unit testing.

Advance the clocks time to the given to_time_ns.

Return the current datetime of the clock in the given local timezone.

Set the clocks datetime to the given time (UTC).

Set a time alert for the given time.

When the time is reached the handler will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

If alert_time is in the past or at current time, then an immediate time event will be generated (rather than being invalid and failing a condition check).

The timer will run from the start time (optionally until the stop time). When the intervals are reached the handlers will be passed the TimeEvent containing the timers unique name. If no handler is passed then the default handler (if registered) will receive the TimeEvent.

Return the current time (UTC).

Throttler(str name, int limit, timedelta interval, Clock clock, output_send: Callable[[Any], None], output_drop: Callable[[Any], None] | None = None) -> None

Provides a generic throttler which can either buffer or drop messages.

Will throttle messages to the given maximum limit-interval rate. If an output_drop handler is provided, then will drop messages which would exceed the rate limit. Otherwise will buffer messages until within the rate limit, then send.

This throttler is not thread-safe and must be called from the same thread as the event loop.

The internal buffer queue is unbounded and so a bounded queue should be upstream.

The interval for the throttler rate.

If the throttler is currently limiting messages (buffering or dropping).

The limit for the throttler rate.

The name of the throttler.

Return the qsize of the internal buffer.

If count of messages received by the throttler.

Reset the state of the throttler.

Send the given message through the throttler.

If count of messages sent from the throttler.

Return the percentage of maximum rate currently used.

TimeEvent(str name, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents a time event occurring at the event timestamp.

The event message identifier.

Return the name of the time event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

TimeEventHandler(TimeEvent event, handler: Callable[[TimeEvent], None]) -> None

Represents a time event with its associated handler.

Call the handler with the contained time event.

Initialize the logging subsystem.

Provides an interface into the logging subsystem implemented in Rust.

This function should only be called once per process, at the beginning of the application run. Subsequent calls will raise a RuntimeError, as there can only be one LogGuard per initialized system.

Represents a unique identifier for a task managed by the ActorExecutor.

This ID can be associated with a task that is either queued for execution or actively executing as an asyncio.Future.

Create and return a new task identifier with a UUID v4 value.

Provides an executor for Actor and Strategy classes.

The executor is designed to handle asynchronous tasks for Actor and Strategy classes. This custom executor queues and executes tasks within a given event loop and is tailored for single-threaded applications.

The ActorExecutor maintains its internal state to manage both queued and active tasks, providing facilities for scheduling, cancellation, and monitoring. It can be used to create more controlled execution flows within complex asynchronous systems.

This executor is not fully thread-safe. Only queue_for_executor can be safely called from other threads. All other methods (cancel_task, get_future, reset, etc.) must be invoked from the same thread in which the executor was created (the event loop thread).

This will cancel all queued and active tasks, and drain the internal queue without executing those tasks.

Return the executing Future with the given task_id (if found).

Shutdown the executor in an async context.

This will cancel the inner worker task and shutdown the underlying executor.

Enqueue the given func to be executed sequentially.

Arrange for the given func to be called in the executor.

Return the queued task identifiers.

Return the active task identifiers.

Return a value indicating whether there are any queued tasks.

Return a value indicating whether there are any active tasks.

Cancel the task with the given task_id (if queued or active).

If the task is not found then a warning is logged.

Cancel all active and queued tasks.

Bases: IdentifierGenerator

ClientOrderIdGenerator(TraderId trader_id, StrategyId strategy_id, Clock clock, int initial_count=0, bool use_uuids=False, bool use_hyphens=True)

Provides a generator for unique

The count of IDs generated.

Return a unique client order ID.

Reset the ID generator.

All stateful fields are reset to their initial value.

Set the internal counter to the given count.

If hyphens should be used in generated client order ID values.

If UUID4’s should be used for client order ID values.

IdentifierGenerator(TraderId trader_id, Clock clock)

Provides a generator for unique ID strings.

Bases: IdentifierGenerator

OrderListIdGenerator(TraderId trader_id, StrategyId strategy_id, Clock clock, int initial_count=0)

Provides a generator for unique

The count of IDs generated.

Return a unique order list ID.

Reset the ID generator.

All stateful fields are reset to their initial value.

Set the internal counter to the given count.

Bases: IdentifierGenerator

PositionIdGenerator(TraderId trader_id, Clock clock)

Provides a generator for unique PositionId(s).

Return a unique position ID.

Return the internal position count for the given strategy ID.

Reset the ID generator.

All stateful fields are reset to their initial value.

Set the internal position count for the given strategy ID.

The base class for all instrument providers.

This class should not be used directly, but through a concrete subclass.

Return the count of instruments held by the provider.

Load the latest instruments into the provider asynchronously, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Load the instrument for the given ID into the provider asynchronously, optionally applying the given filters.

Initialize the instrument provider.

Load the latest instruments into the provider, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Load the instrument for the given ID into the provider, optionally applying the given filters.

Add the given currency to the provider.

Add the given instrument to the provider.

Add the given instruments bulk to the provider.

Return all loaded instruments.

Return all loaded instruments as a map keyed by instrument ID.

If no instruments loaded, will return an empty dict.

Return all currencies held by the instrument provider.

Return the currency with the given code (if found).

Return the instrument for the given instrument ID (if found).

---

## Adapters

**URL:** https://nautilustrader.io/docs/latest/developer_guide/adapters

**Contents:**
- Adapters
- Introduction​
- Structure of an adapter​
  - Rust core (crates/adapters/your_adapter/)​
  - Python layer (nautilus_trader/adapters/your_adapter)​
- Adapter implementation steps​
- Rust adapter patterns​
- HTTP client patterns​
  - Client structure​
  - Parser functions​

This developer guide provides specifications and instructions on how to develop an integration adapter for the NautilusTrader platform. Adapters provide connectivity to trading venues and data providers—translating raw venue APIs into Nautilus’s unified interface and normalized domain model.

NautilusTrader adapters follow a layered architecture pattern with:

Good references for consistent patterns are currently:

The Rust layer handles:

Typical Rust structure:

The Python layer provides the integration interface through these components:

Typical Python structure:

Adapters use a two-layer HTTP client structure to enable efficient cloning for Python bindings while keeping the actual HTTP logic in a single place.

Use an inner/outer client pattern with Arc wrapping:

Parser functions convert venue-specific data structures into Nautilus domain objects. These belong in common/parse.rs for cross-cutting conversions (instruments, trades, bars) or http/parse.rs for REST-specific transformations. Each parser takes venue data plus context (account IDs, timestamps, instrument references) and returns a Nautilus domain type wrapped in Result.

Place parsing helpers (parse_price_with_precision, parse_timestamp) in the same module as private functions when they're reused across multiple parsers.

Organize HTTP methods into two distinct sections:

High-level method flow:

High-level domain methods in the inner client follow a three-step pattern: build venue-specific parameters from Nautilus types, call the corresponding http_* method, then parse or extract the response. For endpoints returning domain objects (positions, orders, trades), call parser functions from common/parse. For endpoints returning raw venue data (fee rates, balances), extract the result directly from the response envelope. Methods prefixed with request_* indicate they return domain data, while methods like submit_*, cancel_*, or modify_* perform actions and return acknowledgments.

The outer client delegates all methods directly to the inner client without additional logic - this separation exists solely to enable cheap cloning for Python bindings via Arc.

Use the derive_builder crate with proper defaults and ergonomic Option handling:

Keep signing logic in the inner client.

Use the RetryManager from nautilus_network for consistent retry behavior.

Configure rate limiting through HttpClient.

WebSocket clients handle real-time streaming data and require careful management of connection state, authentication, subscriptions, and reconnection logic.

WebSocket clients typically don't need the inner/outer pattern since they're not frequently cloned. Use a single struct with clear state management.

Handle authentication separately from subscriptions.

A subscription represents any topic in one of two states:

State transitions follow this lifecycle:

Adapters use venue-specific delimiters to structure subscription topics:

Parse topics using split_once() with the appropriate delimiter to extract channel and symbol components.

On reconnection, restore authentication and public subscriptions, but skip private channels that were explicitly unsubscribed.

Support both control frame pings and application-level pings.

Route different message types to appropriate handlers.

Classify errors to determine retry behavior:

Use the following conventions when mirroring upstream schemas in Rust.

Adapters should ship two layers of coverage: the Rust crate that talks to the venue and the Python glue that exposes it to the wider platform. Keep the suites deterministic and colocated with the production code they protect.

Exercise the public API against Axum mock servers. At a minimum, mirror the BitMEX test surface (see crates/adapters/bitmex/tests/) so every adapter proves the same behaviours.

Login handshake – confirm a successful login flips the internal auth state and test failure cases where the server returns a non-zero code; the client should surface an error and avoid marking itself as authenticated.

Ping/Pong – prove both text-based and control-frame pings trigger immediate pong responses.

Subscription lifecycle – assert subscription requests/acks are emitted for public and private channels, and that unsubscribe calls remove entries from the cached subscription sets.

Reconnect behaviour – simulate a disconnect and ensure the client re-authenticates, restores public channels, and skips private channels that were explicitly unsubscribed pre-disconnect.

Message routing – feed representative data/ack/error payloads through the socket and assert they arrive on the public stream as the correct NautilusWsMessage variant.

Quota tagging – (optional but recommended) validate that order/cancel/amend operations are tagged with the appropriate quota label so rate limiting can be enforced independently of subscription traffic.

Prefer event-driven assertions with shared state (for example, collect subscription_events, track pending/confirmed topics, wait for connection_count transitions) instead of arbitrary sleep calls.

Use adapter-specific helpers to gate on explicit signals such as "auth confirmed" or "reconnection finished" so suites remain deterministic under load.

Below is a step-by-step guide to building an adapter for a new data provider using the provided template.

The InstrumentProvider supplies instrument definitions available on the venue. This includes loading all available instruments, specific instruments by ID, and applying filters to the instrument list.

The LiveDataClient handles the subscription and management of data feeds that are not specifically related to market data. This might include news feeds, custom data streams, or other data sources that enhance trading strategies but do not directly represent market activity.

The MarketDataClient handles market-specific data such as order books, top-of-book quotes and trades, and instrument status updates. It focuses on providing historical and real-time market data that is essential for trading operations.

The ExecutionClient is responsible for order management, including submission, modification, and cancellation of orders. It is a crucial component of the adapter that interacts with the venue trading system to manage and execute trades.

The configuration file defines settings specific to the adapter, such as API keys and connection details. These settings are essential for initializing and managing the adapter’s connection to the data provider.

Exercise adapters across every venue behaviour they claim to support. Incorporate these scenarios into the Rust and Python suites.

Ensure each supported product family is tested.

**Examples:**

Example 1 (text):
```text
crates/adapters/your_adapter/├── src/│   ├── common/           # Shared types and utilities│   │   ├── consts.rs     # Venue constants / broker IDs│   │   ├── credential.rs # API key storage and signing helpers│   │   ├── enums.rs      # Venue enums mirrored in REST/WS payloads│   │   ├── urls.rs       # Environment & product aware base-url resolvers│   │   ├── parse.rs      # Shared parsing helpers│   │   └── testing.rs    # Fixtures reused across unit tests│   ├── http/             # HTTP client implementation│   │   ├── client.rs     # HTTP client with authentication│   │   ├── models.rs     # Structs for REST payloads│   │   ├── query.rs      # Request and query builders│   │   └── parse.rs      # Response parsing functions│   ├── websocket/        # WebSocket implementation│   │   ├── client.rs     # WebSocket client│   │   ├── messages.rs   # Structs for stream payloads│   │   └── parse.rs      # Message parsing functions│   ├── python/           # PyO3 Python bindings│   ├── config.rs         # Configuration structures│   └── lib.rs            # Library entry point└── tests/                # Integration tests with mock servers
```

Example 2 (text):
```text
nautilus_trader/adapters/your_adapter/├── config.py     # Configuration classes├── constants.py  # Adapter constants├── data.py       # LiveDataClient/LiveMarketDataClient├── execution.py  # LiveExecutionClient├── factories.py  # Instrument factories├── providers.py  # InstrumentProvider└── __init__.py   # Package initialization
```

Example 3 (rust):
```rust
use std::sync::Arc;use nautilus_network::http::HttpClient;// Inner client - contains actual HTTP logicpub struct MyHttpInnerClient {    base_url: String,    client: HttpClient,  // Use nautilus_network::http::HttpClient, not reqwest directly    credential: Option<Credential>,    retry_manager: RetryManager<MyHttpError>,    cancellation_token: CancellationToken,}// Outer client - wraps inner with Arc for cheap cloning (needed for Python)pub struct MyHttpClient {    pub(crate) inner: Arc<MyHttpInnerClient>,}
```

Example 4 (rust):
```rust
use derive_builder::Builder;#[derive(Clone, Debug, Deserialize, Serialize, Builder)]#[serde(rename_all = "camelCase")]#[builder(setter(into, strip_option), default)]pub struct InstrumentsInfoParams {    pub category: ProductType,    #[serde(skip_serializing_if = "Option::is_none")]    pub symbol: Option<String>,    #[serde(skip_serializing_if = "Option::is_none")]    pub limit: Option<u32>,}impl Default for InstrumentsInfoParams {    fn default() -> Self {        Self {            category: ProductType::Linear,            symbol: None,            limit: None,        }    }}
```

---

## Objects

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/objects

**Contents:**
- Objects
  - class AccountBalance​
    - copy(self) → AccountBalance​
    - currency​
    - free​
    - static from_dict(dict values) → AccountBalance​
    - locked​
    - to_dict(self) → dict​
    - total​
  - class Currency​

Defines fundamental value objects for the trading domain.

AccountBalance(Money total, Money locked, Money free) -> None

Represents an account balance denominated in a particular currency.

Return a copy of this account balance.

The currency of the account.

The account balance free for trading.

Return an account balance from the given dict values.

The account balance locked (assigned to pending orders).

Return a dictionary representation of this object.

The total account balance.

Currency(str code, uint8_t precision, uint16_t iso4217, str name, CurrencyType currency_type) -> None

Represents a medium of exchange in a specified denomination with a fixed decimal precision.

Handles up to 16 decimals of precision (in high-precision mode).

Return the currency code.

Return the currency type.

Return the currency with the given code from the built-in internal map (if found).

Parse a currency from the given string (if found).

Return whether a currency with the given code is CRYPTO.

Return whether a currency with the given code is FIAT.

Return the currency ISO 4217 code.

Return the currency name.

Return the currency decimal precision.

Register the given currency.

Will override the internal currency map.

MarginBalance(Money initial, Money maintenance, InstrumentId instrument_id=None) -> None

Represents a margin balance optionally associated with a particular instrument.

Return a copy of this margin balance.

The currency of the margin.

Return a margin balance from the given dict values.

The initial margin requirement.

The instrument ID associated with the margin.

The maintenance margin requirement.

Return a dictionary representation of this object.

Money(value, Currency currency) -> None

Represents an amount of money in a specified currency denomination.

Return the value as a built-in Decimal.

Return the value as a double.

Return the currency for the money.

Return money from the given raw fixed-point integer and currency.

Small raw values can produce a zero money amount depending on the precision of the currency.

Return money parsed from the given string.

Must be correctly formatted with a value and currency separated by a whitespace delimiter.

Example: “1000000.00 USD”.

Return the raw memory representation of the money amount.

Return the formatted string representation of the money.

Price(double value, uint8_t precision) -> None

Represents a price in a market.

The number of decimal places may vary. For certain asset classes, prices may have negative values. For example, prices for options instruments can be negative under certain conditions.

Handles up to 16 decimals of precision (in high-precision mode).

Return the value as a built-in Decimal.

Return the value as a double.

Return a price from the given integer value.

A precision of zero will be inferred.

Return a price from the given raw fixed-point integer and precision.

Handles up to 16 decimals of precision (in high-precision mode).

Small raw values can produce a zero price depending on the precision.

Return a price parsed from the given string.

Handles up to 16 decimals of precision (in high-precision mode).

The decimal precision will be inferred from the number of digits following the ‘.’ point (if no point then precision zero).

Return the precision for the price.

Return the raw memory representation of the price value.

Return the formatted string representation of the price.

Quantity(double value, uint8_t precision) -> None

Represents a quantity with a non-negative value.

Capable of storing either a whole number (no decimal places) of ‘contracts’ or ‘shares’ (instruments denominated in whole units) or a decimal value containing decimal places for instruments denominated in fractional units.

Handles up to 16 decimals of precision (in high-precision mode).

Return the value as a built-in Decimal.

Return the value as a double.

Return a quantity from the given integer value.

A precision of zero will be inferred.

Return a quantity from the given raw fixed-point integer and precision.

Handles up to 16 decimals of precision (in high-precision mode).

Small raw values can produce a zero quantity depending on the precision.

Return a quantity parsed from the given string.

Handles up to 16 decimals of precision (in high-precision mode).

The decimal precision will be inferred from the number of digits following the ‘.’ point (if no point then precision zero).

Return the precision for the quantity.

Return the raw memory representation of the quantity value.

Return the formatted string representation of the quantity.

Return a quantity with a value of zero.

precision : The precision for the quantity.

The default precision is zero.

---

## Adapters

**URL:** https://nautilustrader.io/docs/latest/api_reference/adapters/

**Contents:**
- Adapters

The adapters subpackage provides integrations for data providers, brokerages, and exchanges.

Generally each integration will implement lower level HTTP REST and/or WebSocket clients for the exchange/venue API, which the rest of the components can then be built on top of.

---

## Identifiers

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/identifiers

**Contents:**
- Identifiers
  - class AccountId​
    - WARNING​
    - get_id(self) → str​
    - get_issuer(self) → str​
    - value​
  - class ClientId​
    - WARNING​
    - value​
  - class ClientOrderId​

AccountId(str value) -> None

Represents a valid account ID.

Must be correctly formatted with two valid strings either side of a hyphen. It is expected an account ID is the name of the issuer with an account number separated by a hyphen.

Example: “IB-D02851908”.

The issuer and number ID combination must be unique at the firm level.

Return the account ID without issuer name.

Return the account issuer for this ID.

Return the identifier (ID) value.

ClientId(str value) -> None

Represents a system client ID.

The ID value must be unique at the trader level.

Return the identifier (ID) value.

ClientOrderId(str value) -> None

Represents a valid client order ID (assigned by the Nautilus system).

The ID value must be unique at the firm level.

Return the identifier (ID) value.

ComponentId(str value) -> None

Represents a valid component ID.

The ID value must be unique at the trader level.

Return the identifier (ID) value.

ExecAlgorithmId(str value) -> None

Represents a valid execution algorithm ID.

Return the identifier (ID) value.

The abstract base class for all identifiers.

Return the identifier (ID) value.

InstrumentId(Symbol symbol, Venue venue) -> None

Represents a valid instrument ID.

The symbol and venue combination should uniquely identify the instrument.

Return an instrument ID from the given PyO3 instance.

Return an instrument ID parsed from the given string value. Must be correctly formatted including symbol and venue components either side of a single period.

Examples: ‘AUD/USD.IDEALPRO’, ‘BTCUSDT.BINANCE’

Return whether the instrument ID is a spread instrument (symbol contains ‘_’ separator).

Return whether the instrument ID is a synthetic instrument (with venue of ‘SYNTH’).

Create a spread InstrumentId from a list of (instrument_id, ratio) tuples.

The resulting symbol will be in the format: (ratio1)symbol1_(ratio2)symbol2_… where positive ratios are shown as (ratio) and negative ratios as ((ratio)). All instrument IDs must have the same venue. The instrument IDs are sorted alphabetically by symbol before creating the spread symbol.

Returns the instrument ticker symbol.

Parse this InstrumentId back into a list of (instrument_id, ratio) tuples.

This is the inverse operation of new_spread(). The symbol must be in the format created by new_spread(): (ratio1)symbol1_(ratio2)symbol2_… The returned list is sorted alphabetically by symbol.

Return a pyo3 object from this legacy Cython instance.

Return the identifier (ID) value.

Returns the instrument trading venue.

OrderListId(str value) -> None

Represents a valid order list ID (assigned by the Nautilus system).

Return the identifier (ID) value.

PositionId(str value) -> None

Represents a valid position ID.

Return the identifier (ID) value.

StrategyId(str value) -> None

Represents a valid strategy ID.

Must be correctly formatted with two valid strings either side of a hyphen. It is expected a strategy ID is the class name of the strategy, with an order ID tag number separated by a hyphen.

Example: “EMACross-001”.

The reason for the numerical component of the ID is so that order and position IDs do not collide with those from another strategy within the node instance.

The name and tag combination must be unique at the trader level.

Return the order ID tag value for this ID.

If the strategy ID is the global ‘external’ strategy. This represents the strategy for all orders interacting with this instance of the system which did not originate from any strategy being managed by the system.

Return the identifier (ID) value.

Symbol(str value) -> None

Represents a valid ticker symbol ID for a tradable instrument.

The ID value must be unique for a trading venue.

Returns true if the symbol string contains a period (‘.’).

Return the symbol root.

The symbol root is the substring that appears before the first period (‘.’) in the full symbol string. It typically represents the underlying asset for futures and options contracts. If no period is found, the entire symbol string is considered the root.

Return the symbol topic.

The symbol topic is the root symbol with a wildcard ‘*’ appended if the symbol has a root, otherwise returns the full symbol string.

Return the identifier (ID) value.

TradeId(str value) -> None

Represents a valid trade match ID (assigned by a trading venue).

Maximum length is 36 characters. Can correspond to the TradeID <1003> field of the FIX protocol.

The unique ID assigned to the trade entity once it is received or matched by the exchange or central counterparty.

Return the identifier (ID) value.

TraderId(str value) -> None

Represents a valid trader ID.

Must be correctly formatted with two valid strings either side of a hyphen. It is expected a trader ID is the abbreviated name of the trader with an order ID tag number separated by a hyphen.

Example: “TESTER-001”.

The reason for the numerical component of the ID is so that order and position IDs do not collide with those from another node instance.

The name and tag combination ID value must be unique at the firm level.

Return the order ID tag value for this ID.

Return the identifier (ID) value.

Venue(str name) -> None

Represents a valid trading venue ID.

Return the venue with the given code from the built-in internal map (if found).

Currency only supports CME Globex exchange ISO 10383 MIC codes.

Return whether the venue is synthetic (‘SYNTH’).

Return the identifier (ID) value.

VenueOrderId(str value) -> None

Represents a valid venue order ID (assigned by a trading venue).

Return the identifier (ID) value.

---

## Order Book

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/book

**Contents:**
- Order Book
  - class BookLevel​
    - exposure(self) → double​
    - orders(self) → list​
    - price​
    - side​
    - size(self) → double​
  - class OrderBook​
    - add(self, BookOrder order, uint64_t ts_event, uint8_t flags=0, uint64_t sequence=0) → void​
    - apply(self, Data data) → void​

Represents an order book price level.

A price level on one side of the order book with one or more individual orders.

This class is read-only and cannot be initialized from Python.

Return the exposure at this level (price * volume).

Return the orders for the level.

Return the price for the level.

Return the side for the level.

Return the size at this level.

OrderBook(InstrumentId instrument_id, BookType book_type) -> None

Provides an order book which can handle L1/L2/L3 granularity data.

Add the given order to the book.

Apply the given data to the order book.

Apply the order book delta.

Apply the bulk deltas to the order book.

Apply the depth update to the order book.

Return the bid levels for the order book.

Return the best ask price in the book (if no asks then returns None).

Return the best ask size in the book (if no asks then returns None).

Return the best bid price in the book (if no bids then returns None).

Return the best bid size in the book (if no bids then returns None).

Return the bid levels for the order book.

Return the order book type.

Check book integrity.

Clear the entire order book.

Clear the asks from the order book.

Clear the bids from the order book.

Cancel the given order in the book.

Return the fully qualified name for the Data class.

Return the average price expected for the given quantity based on the current state of the order book.

If no average price can be calculated then will return 0.0 (zero).

Return the current total quantity for the given price based on the current state of the order book.

Return the books instrument ID.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return the mid point (if no market exists then returns None).

Return a string representation of the order book in a human-readable table format.

Reset the order book (clear all stateful values).

Return the last sequence number for the book.

Simulate filling the book with the given order.

Return the top-of-book spread (if no bids or asks then returns None).

Return a QuoteTick created from the top of book levels.

Returns None when the top-of-book bid or ask is missing or invalid (zero size).

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the UNIX timestamp (nanoseconds) when the order book was last updated.

Update the given order in the book.

Return the books update count.

Update the order book with the given quote tick.

This operation is only valid for L1_MBP books maintaining a top level.

Update the order book with the given trade tick.

---

## Orders

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/orders

**Contents:**
- Orders
  - class LimitIfTouchedOrder​
    - static create(init)​
    - display_qty​
    - expire_time​
    - expire_time_ns​
    - info(self) → str​
    - is_triggered​
    - price​
    - to_dict(self) → dict​

Provides a full range of standard order types, as well as more advanced types and order lists.

LimitIfTouchedOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Limit-If-Touched (LIT) conditional order.

A Limit-If-Touched (LIT) is an order to BUY (or SELL) an instrument at a specified price or better, below (or above) the market. This order is held in the system until the trigger price is touched. A LIT order is similar to a Stop-Limit order, except that a LIT SELL order is placed above the current market price, and a Stop-Limit SELL order is placed below.

Using a LIT order helps to ensure that, if the order does execute, the order will not execute at a price less favorable than the limit price.

The quantity of the LIMIT order to display on the public book (iceberg).

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

If the order has been triggered.

The order price (LIMIT).

Return a dictionary representation of this object.

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was triggered (0 if not triggered).

LimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Limit order.

A Limit order is an order to BUY (or SELL) at a specified price or better. The Limit order ensures that if the order fills, it will not fill at a price less favorable than your limit price, but it does not guarantee a fill.

The quantity of the order to display on the public book (iceberg).

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

The order price (LIMIT).

Return a dictionary representation of this object.

MarketIfTouchedOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Market-If-Touched (MIT) conditional order.

A Market-If-Touched (MIT) is an order to BUY (or SELL) an instrument below (or above) the market. This order is held in the system until the trigger price is touched, and is then submitted as a market order. An MIT order is similar to a Stop-Order, except that an MIT SELL order is placed above the current market price, and a stop SELL order is placed below.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

Return a dictionary representation of this object.

The order trigger price (STOP).

The trigger type for the order.

MarketOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, bool reduce_only=False, bool quote_quantity=False, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Market order.

A Market order is an order to BUY (or SELL) at the market bid or offer price. A market order may increase the likelihood of a fill and the speed of execution, but unlike the Limit order - a Market order provides no price protection and may fill at a price far lower/higher than the top-of-book bid/ask.

Return a summary description of the order.

Return a dictionary representation of this object.

MarketToLimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Market-To-Limit (MTL) order.

A Market-to-Limit (MTL) order is submitted as a market order to execute at the current best market price. If the order is only partially filled, the remainder of the order is canceled and re-submitted as a Limit order with the limit price equal to the price at which the filled portion of the order executed.

The quantity of the limit order to display on the public book (iceberg).

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

The order price (LIMIT).

Return a dictionary representation of this object.

Order(OrderInitialized init)

The base class for all orders.

This class should not be used directly, but through a concrete subclass.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

OrderList(OrderListId order_list_id, list orders) -> None

Represents a list of bulk or related contingent orders.

All orders must be for the same instrument ID.

The first order in the list (typically the parent).

The instrument ID associated with the list.

The contained orders list.

The strategy ID associated with the list.

UNIX timestamp (nanoseconds) when the object was initialized.

Provides a means of unpacking orders from value dictionaries.

Return an order initialized from the given event.

Return an order unpacked from the given values.

StopLimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Stop-Limit conditional order.

A Stop-Limit order is an instruction to submit a BUY (or SELL) limit order when the specified stop trigger price is attained or penetrated. The order has two basic components: the stop price and the limit price. When a trade has occurred at or through the stop price, the order becomes executable and enters the market as a limit order, which is an order to BUY (or SELL) at a specified price or better.

A Stop-Limit eliminates the price risk associated with a stop order where the execution price cannot be guaranteed, but exposes the trader to the risk that the order may never fill, even if the stop price is reached.

The quantity of the LIMIT order to display on the public book (iceberg).

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

If the order has been triggered.

The order price (LIMIT).

Return a dictionary representation of this object.

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was triggered (0 if not triggered).

StopMarketOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Stop-Market conditional order.

A Stop-Market order is an instruction to submit a BUY (or SELL) market order if and when the specified stop trigger price is attained or penetrated. A Stop-Market order is not guaranteed a specific execution price and may execute significantly away from its stop price.

A SELL Stop-Market order is always placed below the current market price, and is typically used to limit a loss or protect a profit on a long position.

A BUY Stop-Market order is always placed above the current market price, and is typically used to limit a loss or protect a profit on a short position.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

Return a dictionary representation of this object.

The order trigger price (STOP).

The trigger type for the order.

TrailingStopLimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price: Price | None, Price trigger_price: Price | None, TriggerType trigger_type, limit_offset: Decimal, trailing_offset: Decimal, TrailingOffsetType trailing_offset_type, UUID4 init_id, uint64_t ts_init, Price activation_price: Price | None = None, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Trailing-Stop-Limit conditional order.

The order activation price (STOP).

The quantity of the LIMIT order to display on the public book (iceberg).

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

If the order has been activated.

If the order has been triggered.

The trailing offset for the orders limit price.

The order price (LIMIT).

Return a dictionary representation of this object.

The trailing offset for the orders trigger price (STOP).

The trailing offset type.

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was triggered (0 if not triggered).

TrailingStopMarketOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price trigger_price: Price | None, TriggerType trigger_type, trailing_offset: Decimal, TrailingOffsetType trailing_offset_type, UUID4 init_id, uint64_t ts_init, Price activation_price: Price | None = None, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Trailing-Stop-Market conditional order.

The order activation price (STOP).

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

Return a summary description of the order.

If the order has been activated.

Return a dictionary representation of this object.

The trailing offset for the orders trigger price (STOP).

The trailing offset type.

The order trigger price (STOP).

The trigger type for the order.

MarketOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, bool reduce_only=False, bool quote_quantity=False, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Market order.

A Market order is an order to BUY (or SELL) at the market bid or offer price. A market order may increase the likelihood of a fill and the speed of execution, but unlike the Limit order - a Market order provides no price protection and may fill at a price far lower/higher than the top-of-book bid/ask.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

LimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Limit order.

A Limit order is an order to BUY (or SELL) at a specified price or better. The Limit order ensures that if the order fills, it will not fill at a price less favorable than your limit price, but it does not guarantee a fill.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The quantity of the order to display on the public book (iceberg).

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

The order price (LIMIT).

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

StopMarketOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Stop-Market conditional order.

A Stop-Market order is an instruction to submit a BUY (or SELL) market order if and when the specified stop trigger price is attained or penetrated. A Stop-Market order is not guaranteed a specific execution price and may execute significantly away from its stop price.

A SELL Stop-Market order is always placed below the current market price, and is typically used to limit a loss or protect a profit on a long position.

A BUY Stop-Market order is always placed above the current market price, and is typically used to limit a loss or protect a profit on a short position.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

StopLimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Stop-Limit conditional order.

A Stop-Limit order is an instruction to submit a BUY (or SELL) limit order when the specified stop trigger price is attained or penetrated. The order has two basic components: the stop price and the limit price. When a trade has occurred at or through the stop price, the order becomes executable and enters the market as a limit order, which is an order to BUY (or SELL) at a specified price or better.

A Stop-Limit eliminates the price risk associated with a stop order where the execution price cannot be guaranteed, but exposes the trader to the risk that the order may never fill, even if the stop price is reached.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The quantity of the LIMIT order to display on the public book (iceberg).

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

If the order has been triggered.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

The order price (LIMIT).

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

UNIX timestamp (nanoseconds) when the order was triggered (0 if not triggered).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

MarketToLimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Market-To-Limit (MTL) order.

A Market-to-Limit (MTL) order is submitted as a market order to execute at the current best market price. If the order is only partially filled, the remainder of the order is canceled and re-submitted as a Limit order with the limit price equal to the price at which the filled portion of the order executed.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The quantity of the limit order to display on the public book (iceberg).

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

The order price (LIMIT).

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

MarketIfTouchedOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Market-If-Touched (MIT) conditional order.

A Market-If-Touched (MIT) is an order to BUY (or SELL) an instrument below (or above) the market. This order is held in the system until the trigger price is touched, and is then submitted as a market order. An MIT order is similar to a Stop-Order, except that an MIT SELL order is placed above the current market price, and a stop SELL order is placed below.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

LimitIfTouchedOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price, Price trigger_price, TriggerType trigger_type, UUID4 init_id, uint64_t ts_init, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Limit-If-Touched (LIT) conditional order.

A Limit-If-Touched (LIT) is an order to BUY (or SELL) an instrument at a specified price or better, below (or above) the market. This order is held in the system until the trigger price is touched. A LIT order is similar to a Stop-Limit order, except that a LIT SELL order is placed above the current market price, and a Stop-Limit SELL order is placed below.

Using a LIT order helps to ensure that, if the order does execute, the order will not execute at a price less favorable than the limit price.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The quantity of the LIMIT order to display on the public book (iceberg).

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

If the order has been triggered.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

The order price (LIMIT).

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

UNIX timestamp (nanoseconds) when the order was triggered (0 if not triggered).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

TrailingStopMarketOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price trigger_price: Price | None, TriggerType trigger_type, trailing_offset: Decimal, TrailingOffsetType trailing_offset_type, UUID4 init_id, uint64_t ts_init, Price activation_price: Price | None = None, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool reduce_only=False, bool quote_quantity=False, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Trailing-Stop-Market conditional order.

The account ID associated with the order.

The order activation price (STOP).

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

If the order has been activated.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The trailing offset for the orders trigger price (STOP).

The trailing offset type.

The order emulation trigger instrument ID (will be instrument_id if None).

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

TrailingStopLimitOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, Quantity quantity, Price price: Price | None, Price trigger_price: Price | None, TriggerType trigger_type, limit_offset: Decimal, trailing_offset: Decimal, TrailingOffsetType trailing_offset_type, UUID4 init_id, uint64_t ts_init, Price activation_price: Price | None = None, TimeInForce time_in_force=TimeInForce.GTC, uint64_t expire_time_ns=0, bool post_only=False, bool reduce_only=False, bool quote_quantity=False, Quantity display_qty=None, TriggerType emulation_trigger=TriggerType.NO_TRIGGER, InstrumentId trigger_instrument_id=None, ContingencyType contingency_type=ContingencyType.NO_CONTINGENCY, OrderListId order_list_id=None, list linked_order_ids=None, ClientOrderId parent_order_id=None, ExecAlgorithmId exec_algorithm_id=None, dict exec_algorithm_params=None, ClientOrderId exec_spawn_id=None, list tags=None)

Represents a Trailing-Stop-Limit conditional order.

The account ID associated with the order.

The order activation price (STOP).

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The quantity of the LIMIT order to display on the public book (iceberg).

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return the expire time for the order (UTC).

The order expiration (UNIX epoch nanoseconds), zero for no expiration.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

If the order has been activated.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

If the order has been triggered.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The trailing offset for the orders limit price.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

The order price (LIMIT).

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The trailing offset for the orders trigger price (STOP).

The trailing offset type.

The order emulation trigger instrument ID (will be instrument_id if None).

The order trigger price (STOP).

The trigger type for the order.

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

UNIX timestamp (nanoseconds) when the order was triggered (0 if not triggered).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

OrderList(OrderListId order_list_id, list orders) -> None

Represents a list of bulk or related contingent orders.

All orders must be for the same instrument ID.

The first order in the list (typically the parent).

The instrument ID associated with the list.

The contained orders list.

The strategy ID associated with the list.

UNIX timestamp (nanoseconds) when the object was initialized.

Order(OrderInitialized init)

The base class for all orders.

This class should not be used directly, but through a concrete subclass.

The account ID associated with the order.

Apply the given order event to the order.

The order average fill price.

Return the order side needed to close a position with the given side.

Return the total commissions generated by the order.

The orders contingency type.

The order emulation trigger type.

Return the count of events applied to the order.

Return the order events.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

The order total filled quantity.

Return whether the order has a activation_price property.

Return whether the order has a price property.

Return whether the order has a trigger_price property.

Return a summary description of the order.

Return the initialization event for the order.

The event ID of the OrderInitialized event.

The order instrument ID.

Return whether the order is active and held in the local system.

An order is considered active local when its status is any of:

Return whether the order is aggressive (order_type is MARKET).

Return whether the order side is BUY.

Return whether current status is CANCELED.

Return whether the order has a parent order.

Return whether the order is closed (lifecycle completed).

An order is considered closed when its status can no longer change. The possible statuses of closed orders include;

Return whether the order has a contingency (contingency_type is not NO_CONTINGENCY).

Return whether the order is emulated and held in the local system.

Return whether the order is in-flight (order request sent to the trading venue).

An order is considered in-flight when its status is any of:

An emulated order is never considered in-flight.

Return whether the order is open at the trading venue.

An order is considered open when its status is any of:

An emulated order is never considered open.

Return whether the order has at least one child order.

Return whether the order is passive (order_type not MARKET).

Return whether the current status is PENDING_CANCEL.

Return whether the current status is PENDING_UPDATE.

If the order will only provide liquidity (make a market).

Return whether the order is the primary for an execution algorithm sequence.

If the order quantity is denominated in the quote currency.

If the order carries the ‘reduce-only’ execution instruction.

Return whether the order side is SELL.

Return whether the order was spawned as part of an execution algorithm sequence.

Return the last event applied to the order.

The orders last trade match ID.

The order total leaves quantity.

The orders linked client order ID(s).

The order liquidity side.

Return the opposite order side from the given side.

The order list ID associated with the order.

The parent client order ID.

The position ID associated with the order.

Return the orders side as a string.

Return a signed decimal representation of the remaining quantity.

The order total price slippage.

Return the orders current status.

Return the orders current status as a string.

The strategy ID associated with the order.

Return the orders ticker symbol.

The order custom user tags.

Return the orders time in force as a string.

The order time in force.

Return a dictionary representation of this object.

Returns an own/user order representation of this order.

Return the trade match IDs.

The trader ID associated with the position.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the order was accepted or first filled (zero unless accepted or filled).

UNIX timestamp (nanoseconds) when the order closed / lifecycle completed (zero unless closed).

UNIX timestamp (nanoseconds) when the order was initialized.

UNIX timestamp (nanoseconds) when the last order event occurred.

UNIX timestamp (nanoseconds) when the order was submitted (zero unless submitted).

Return the orders type as a string.

Return the orders trading venue.

The venue assigned order ID.

Return the venue order IDs.

Whether the current order would only reduce the given position if applied in full.

---

## Python API

**URL:** https://nautilustrader.io/docs/latest/api_reference/

**Contents:**
- Python API
- Why Python?​

Welcome to the Python API reference for NautilusTrader!

The API reference provides detailed technical documentation for the NautilusTrader framework, including its modules, classes, methods, and functions. The reference is automatically generated from the latest NautilusTrader source code using Sphinx.

Please note that there are separate references for different versions of NautilusTrader:

You can select the desired API reference from the Versions top left drop down menu.

Use the right navigation sidebar to explore the available modules and their contents. You can click on any item to view its detailed documentation, including parameter descriptions, and return value explanations.

Python was originally created decades ago as a simple scripting language with a clean straight forward syntax. It has since evolved into a fully fledged general purpose object-oriented programming language. Based on the TIOBE index, Python is currently the most popular programming language in the world. Not only that, Python has become the de facto lingua franca of data science, machine learning, and artificial intelligence.

---

## Config

**URL:** https://nautilustrader.io/docs/latest/api_reference/config

**Contents:**
- Config
- Backtest​
  - parse_filters_expr(s: str | None)​
  - class BacktestVenueConfig​
    - name : str​
    - oms_type : OmsType | str​
    - account_type : AccountType | str​
    - starting_balances : list[str]​
    - base_currency : str | None​
    - default_leverage : float​

Parse a pyarrow.dataset filter expression from a string.

Bases: NautilusConfig

Represents a venue configuration for one specific backtest engine.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Represents the data configuration for one specific backtest run.

Return a type for the specified data_cls for the configuration.

Return a catalog query object for the configuration.

Return the data configuration start time in UNIX nanoseconds.

Will be zero if no start_time was specified.

Return the data configuration end time in UNIX nanoseconds.

Will be sys.maxsize if no end_time was specified.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusKernelConfig

Configuration for BacktestEngine instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Represents the configuration for one specific backtest run.

This includes a backtest engine with its actors and strategies, with the external inputs of venues and data.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Configuration for SimulationModule instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for FillModel instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for a fill model instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides fill model creation from importable configurations.

Create a fill model from the given configuration.

Bases: NautilusConfig

Configuration for LatencyModel instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for a latency model instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides latency model creation from importable configurations.

Create a latency model from the given configuration.

Bases: NautilusConfig

Base configuration for FeeModel instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: FeeModelConfig

Configuration for MakerTakerFeeModel instances.

This fee model uses the maker/taker fees defined on the instrument.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: FeeModelConfig

Configuration for FixedFeeModel instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: FeeModelConfig

Configuration for PerContractFeeModel instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for a fee model instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides fee model creation from importable configurations.

Create a fee model from the given configuration.

Bases: SimulationModuleConfig

Provides an FX rollover interest simulation module.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for margin calculation models.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides margin model creation from configurations.

Create a margin model from the given configuration.

Bases: NautilusConfig

Configuration for Cache instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Raised when there is a violation of a configuration condition, making it invalid.

Exception.add_note(note) – add a note to the exception

Exception.with_traceback(tb) – set self._traceback_ to tb and return self.

The base class for all Nautilus configuration objects.

Return the hashed identifier for the configuration.

Return the fully qualified name for the NautilusConfig class.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return a dictionary representation of the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for database connections.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for MessageBus instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for InstrumentProvider instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for OrderEmulator instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

The base model for all actor configurations.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for an actor instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides actor creation from importable configurations.

Create an actor from the given configuration.

Bases: NautilusConfig

Configuration for standard output and file logging for a NautilusKernel instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Represents an importable (JSON) factory config.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Represents an importable configuration (typically live data client or live execution client).

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for DataEngine instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for ExecutionEngine instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

The base model for all execution algorithm configurations.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for an execution algorithm instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides execution algorithm creation from importable configurations.

Create an execution algorithm from the given configuration.

Bases: DataEngineConfig

Configuration for LiveDataEngine instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: RiskEngineConfig

Configuration for LiveRiskEngine instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: ExecEngineConfig

Configuration for LiveExecEngine instances.

The purpose of the in-flight order check is for live reconciliation, events emitted from the venue may have been lost at some point - leaving an order in an intermediate state, the check can recover these events via status reports.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for live client message routing.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for LiveDataClient instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for LiveExecutionClient instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

The base model for all controller configurations.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides controller creation from importable configurations.

Bases: NautilusKernelConfig

Configuration for TradingNode instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for streaming live or backtest runs to the catalog in feather format.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for a data catalog.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for RiskEngine instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for a NautilusKernel core system instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

The base model for all trading strategy configurations.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: NautilusConfig

Configuration for a trading strategy instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Provides strategy creation from importable configurations.

Create a trading strategy from the given configuration.

Bases: NautilusConfig

Configuration for a controller instance.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

**Examples:**

Example 1 (pycon):
```pycon
>>> parse_filters_expr('field("Currency") == "CHF"')<pyarrow.dataset.Expression (Currency == "CHF")>
```

Example 2 (pycon):
```pycon
>>> parse_filters_expr("print('hello')")
```

Example 3 (pycon):
```pycon
>>> parse_filters_expr("None")
```

---

## Portfolio

**URL:** https://nautilustrader.io/docs/latest/api_reference/portfolio

**Contents:**
- Portfolio
  - class Portfolio​
    - account(self, Venue venue) → Account​
    - balances_locked(self, Venue venue) → dict​
    - dispose(self) → None​
    - initialize_orders(self) → void​
    - initialize_positions(self) → void​
    - is_completely_flat(self) → bool​
    - is_flat(self, InstrumentId instrument_id) → bool​
    - is_net_long(self, InstrumentId instrument_id) → bool​

The portfolio subpackage provides portfolio management functionality.

Bases: PortfolioFacade

Portfolio(MessageBus msgbus, CacheFacade cache, Clock clock, config: PortfolioConfig | None = None) -> None

Provides a trading portfolio.

Currently there is a limitation of one account per ExecutionClient instance.

Return the account for the given venue (if found).

Return the balances locked for the given venue (if found).

Dispose of the portfolio.

All stateful fields are reset to their initial value.

Initialize the portfolios orders.

Performs all account calculations for the current orders state.

Initialize the portfolios positions.

Performs all account calculations for the current position state.

Return a value indicating whether the portfolio is completely flat.

Return a value indicating whether the portfolio is flat for the given instrument ID.

Return a value indicating whether the portfolio is net long the given instrument ID.

Return a value indicating whether the portfolio is net short the given instrument ID.

Return the initial (order) margins for the given venue (if found).

Return the maintenance (position) margins for the given venue (if found).

Return the net exposure for the given instrument (if found).

Return the net exposures for the given venue (if found).

Return the total net position for the given instrument ID. If no positions for instrument_id then will return Decimal(‘0’).

Actions to be performed on receiving an order event.

Actions to be performed on receiving a position event.

Return the realized PnL for the given instrument ID (if found).

Return the realized PnLs for the given venue (if found).

If no positions exist for the venue or if any lookups fail internally, an empty dictionary is returned.

All stateful fields are reset to their initial value.

Set a specific venue for the portfolio.

Set the use_mark_prices setting with the given value.

Set the use_mark_xrates setting with the given value.

Return the total PnL for the given instrument ID (if found).

Return the total PnLs for the given venue (if found).

Return the unrealized PnL for the given instrument ID (if found).

Returns None if the calculation fails (e.g., the account or instrument cannot be found), or zero-valued Money if no positions are open. Otherwise, it returns a Money object (usually in the account’s base currency or the instrument’s settlement currency).

Return the unrealized PnLs for the given venue (if found).

Apply the given account state.

Update the portfolio with the given bar.

Clears the cached unrealized PnL for the associated instrument, and performs any initialization calculations which may have been pending an update.

Update the portfolio with the given order.

Update the portfolio with the given position event.

Update the portfolio with the given quote tick.

Clears the cached unrealized PnL for the associated instrument, and performs any initialization calculations which may have been pending an update.

Provides a read-only facade for a Portfolio.

Abstract method (implement in subclass).

The portfolios analyzer.

Abstract method (implement in subclass).

If the portfolio is initialized.

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

The Portfolio facilitates the management of trading operations.

The intended use case is for a single Portfolio instance per running system, a fleet of trading strategies will organize around a portfolio with the help of the Trader` class.

The portfolio can satisfy queries for account information, margin balances, total risk exposures and total net positions.

Bases: PortfolioFacade

Portfolio(MessageBus msgbus, CacheFacade cache, Clock clock, config: PortfolioConfig | None = None) -> None

Provides a trading portfolio.

Currently there is a limitation of one account per ExecutionClient instance.

Return the account for the given venue (if found).

The portfolios analyzer.

Return the balances locked for the given venue (if found).

Dispose of the portfolio.

All stateful fields are reset to their initial value.

Initialize the portfolios orders.

Performs all account calculations for the current orders state.

Initialize the portfolios positions.

Performs all account calculations for the current position state.

If the portfolio is initialized.

Return a value indicating whether the portfolio is completely flat.

Return a value indicating whether the portfolio is flat for the given instrument ID.

Return a value indicating whether the portfolio is net long the given instrument ID.

Return a value indicating whether the portfolio is net short the given instrument ID.

Return the initial (order) margins for the given venue (if found).

Return the maintenance (position) margins for the given venue (if found).

Return the net exposure for the given instrument (if found).

Return the net exposures for the given venue (if found).

Return the total net position for the given instrument ID. If no positions for instrument_id then will return Decimal(‘0’).

Actions to be performed on receiving an order event.

Actions to be performed on receiving a position event.

Return the realized PnL for the given instrument ID (if found).

Return the realized PnLs for the given venue (if found).

If no positions exist for the venue or if any lookups fail internally, an empty dictionary is returned.

All stateful fields are reset to their initial value.

Set a specific venue for the portfolio.

Set the use_mark_prices setting with the given value.

Set the use_mark_xrates setting with the given value.

Return the total PnL for the given instrument ID (if found).

Return the total PnLs for the given venue (if found).

Return the unrealized PnL for the given instrument ID (if found).

Returns None if the calculation fails (e.g., the account or instrument cannot be found), or zero-valued Money if no positions are open. Otherwise, it returns a Money object (usually in the account’s base currency or the instrument’s settlement currency).

Return the unrealized PnLs for the given venue (if found).

Apply the given account state.

Update the portfolio with the given bar.

Clears the cached unrealized PnL for the associated instrument, and performs any initialization calculations which may have been pending an update.

Update the portfolio with the given order.

Update the portfolio with the given position event.

Update the portfolio with the given quote tick.

Clears the cached unrealized PnL for the associated instrument, and performs any initialization calculations which may have been pending an update.

Provides a read-only facade for a Portfolio.

Abstract method (implement in subclass).

The portfolios analyzer.

Abstract method (implement in subclass).

If the portfolio is initialized.

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

## Execution

**URL:** https://nautilustrader.io/docs/latest/api_reference/execution

**Contents:**
- Execution
- Components​
  - class ExecAlgorithm​
    - WARNING​
    - active_task_ids(self) → list​
    - add_synthetic(self, SyntheticInstrument synthetic) → void​
    - cache​
    - cancel_all_tasks(self) → void​
    - cancel_order(self, Order order, ClientId client_id=None) → void​
    - cancel_task(self, task_id: TaskId) → void​

The execution subpackage groups components relating to the execution stack for the platform.

The layered architecture of the execution stack somewhat mirrors the data stack with a central engine, cache layer beneath, database layer beneath, with alternative implementations able to be written on top.

Due to the high-performance, the core components are reusable between both backtest and live implementations - helping to ensure consistent logic for trading operations.

ExecAlgorithm(config: ExecAlgorithmConfig | None = None)

The base class for all execution algorithms.

This class allows traders to implement their own customized execution algorithms.

This class should not be used directly, but through a concrete subclass.

Return the active task identifiers.

Add the created synthetic instrument to the cache.

The read-only cache for the actor.

Cancel all queued and active tasks.

Cancel the given order with optional routing instructions.

A CancelOrder command will be created and then sent to either the OrderEmulator or the ExecutionEngine (depending on whether the order is emulated).

Logs an error if no VenueOrderId has been assigned to the order.

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

Handle the given trading command by processing it with the execution algorithm.

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

Modify the given order with optional parameters and routing instructions.

An ModifyOrder command will be created and then sent to the RiskEngine.

At least one value must differ from the original order for the command to be valid.

Will use an Order Cancel/Replace Request (a.k.a Order Modification) for FIX protocols, otherwise if order update is not available for the API, then will cancel and replace with a new order using the original ClientOrderId.

If the order is already closed or at PENDING_CANCEL status then the command will not be generated, and a warning will be logged.

Modify the given INITIALIZED order in place (immediately) with optional parameters.

At least one value must differ from the original order for the command to be valid.

If the order is already closed or at PENDING_CANCEL status then the command will not be generated, and a warning will be logged.

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

Actions to be performed when running and receives an order.

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

Actions to be performed when running and receives an order initialized event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order expired event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order filled event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order initialized event.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order list.

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

Register the execution algorithm with a trader.

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

Spawn a new LIMIT order from the given primary order.

Spawn a new MARKET order from the given primary order.

Spawn a new MARKET_TO_LIMIT order from the given primary order.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Submit the given order (may be the primary or spawned order).

A SubmitOrder command will be created and sent to the RiskEngine.

If the client order ID is duplicate, then the order will be denied.

If a position_id is passed and a position does not yet exist, then any position opened by the order will have this position ID assigned. This may not be what you intended.

Emulated orders cannot be sent from execution algorithms (intentionally constraining complexity).

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

Returns an importable configuration for this execution algorithm.

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

ExecutionClient(ClientId client_id, Venue venue: Venue | None, OmsType oms_type, AccountType account_type, Currency base_currency: Currency | None, MessageBus msgbus, Cache cache, Clock clock, config: NautilusConfig | None = None)

The base class for all execution clients.

This class should not be used directly, but through a concrete subclass.

The clients account ID.

The clients account type.

The clients account base currency (None for multi-currency accounts).

Batch cancel orders for the instrument ID contained in the given command.

Cancel all orders for the instrument ID contained in the given command.

Cancel the order with the client order ID contained in the given command.

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

Generate an AccountState event and publish on the message bus.

Generate an OrderAccepted event and send it to the ExecutionEngine.

Generate an OrderCancelRejected event and send it to the ExecutionEngine.

Generate an OrderCanceled event and send it to the ExecutionEngine.

Generate an OrderDenied event and send it to the ExecutionEngine.

Generate an OrderExpired event and send it to the ExecutionEngine.

Generate an OrderFilled event and send it to the ExecutionEngine.

Generate an OrderModifyRejected event and send it to the ExecutionEngine.

Generate an OrderRejected event and send it to the ExecutionEngine.

Generate an OrderSubmitted event and send it to the ExecutionEngine.

Generate an OrderTriggered event and send it to the ExecutionEngine.

Generate an OrderUpdated event and send it to the ExecutionEngine.

Return the account for the client (if registered).

If the client is connected.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Modify the order with parameters contained in the command.

The venues order management system type.

Query the account specified by the command which will generate an AccountState event.

Initiate a reconciliation for the queried order which will generate an OrderStatusReport.

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

Submit the order contained in the given command for execution.

Submit the order list contained in the given command for execution.

The trader ID associated with the component.

The clients venue ID (if not a routing client).

OrderEmulator(PortfolioFacade portfolio, MessageBus msgbus, Cache cache, Clock clock, config: OrderEmulatorConfig | None = None)

Provides order emulation for specified trigger types.

Return the active task identifiers.

Add the created synthetic instrument to the cache.

The read-only cache for the actor.

Cancel all queued and active tasks.

Cancel the task with the given task_id (if queued or active).

If the task is not found then a warning is logged.

The total count of commands received by the emulator.

The actors configuration.

Create an internal matching core for the given instrument.

If debug mode is active (will provide extra debug logging).

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Deregister the given event type from warning log levels.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

The total count of events received by the emulator.

Execute the given command.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

Return the emulators matching core for the given instrument ID.

Return the emulators cached submit order commands.

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

Handle the given event.

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

Actions to be performed when running and receives an order book depth.

System method (not intended to be called by user code).

Actions to be performed when running and receives an order filled event.

System method (not intended to be called by user code).

Actions to be performed on resume.

System method (not intended to be called by user code).

Actions to be performed when the actor state is saved.

Create and return a state dictionary of values to be saved.

System method (not intended to be called by user code).

Actions to be performed when running and receives signal data.

System method (not intended to be called by user code).

Return the request IDs which are currently pending processing.

The read-only portfolio for the actor.

Publish the given data to the message bus.

Publish the given value as a signal to the message bus.

Queues the callable func to be executed as fn(*args, **kwargs) sequentially.

Return the queued task identifiers.

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

Return the subscribed quote feeds for the emulator.

Return the subscribed trade feeds for the emulator.

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

The ExecutionEngine is the central component of the entire execution stack.

The execution engines primary responsibility is to orchestrate interactions between the ExecutionClient instances, and the rest of the platform. This includes sending commands to, and receiving events from, the trading venue endpoints via its registered execution clients.

The engine employs a simple fan-in fan-out messaging pattern to execute TradingCommand messages and OrderEvent messages.

Alternative implementations can be written on top of the generic engine - which just need to override the execute and process methods.

ExecutionEngine(MessageBus msgbus, Cache cache, Clock clock, config: ExecEngineConfig | None = None) -> None

Provides a high-performance execution engine for the management of many ExecutionClient instances, and the asynchronous ingest and distribution of trading commands and events.

Check all of the engines clients are connected.

Check all of the engines clients are disconnected.

Check integrity of data within the cache and clients.

Check for any residual open state and log warnings if found.

‘Open state’ is considered to be open orders and open positions.

The total count of commands received by the engine.

Connect the engine by calling connect on all registered clients.

If quote-denominated order quantities should be converted to base units before submission.

If debug mode is active (will provide extra debug logging).

Return the default execution client registered with the engine.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Deregister the given execution client from the execution engine.

Disconnect the engine by calling disconnect on all registered clients.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

The total count of events received by the engine.

Execute the given command.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Flush the execution database which permanently removes all persisted data.

Return the fully qualified name for the components class.

Get all execution clients corresponding to the given orders.

Returns the configured external client order IDs.

Get any external order claim for the given instrument ID.

Get all instrument IDs registered for external order claims.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Load the cache up from the execution database.

If the execution engine should maintain own order books based on commands and events.

The position ID count for the given strategy ID.

Process the given order event.

Reconcile the given execution mass status report.

Check the given execution report.

Reconcile the internal execution state with all execution clients (external state).

Return whether the reconciliation process will be run on start.

Register the given execution client with the execution engine.

If the client.venue is None and a default routing client has not been previously registered then will be registered as such.

Register the given client as the default routing client (when a specific venue routing cannot be found).

Any existing default routing client will be overwritten.

Register the given strategies external order claim instrument IDs (if any)

Register the given trading strategies OMS (Order Management System) type.

Register the given client to route orders to the given venue.

Any existing client in the routing map for the given venue will be overwritten.

Return the execution clients registered with the engine.

The total count of reports received by the engine.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Set the convert_quote_qty_to_base flag with the given value.

Set the manage_own_order_books setting with the given value.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

If order state snapshots should be persisted.

If position state snapshots should be persisted.

The interval (seconds) at which additional position state snapshots are persisted.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Stop the registered clients.

The trader ID associated with the component.

OrderManager(Clock clock, MessageBus msgbus, Cache cache, str component_name, bool active_local, submit_order_handler: Callable[[SubmitOrder], None] = None, cancel_order_handler: Callable[[Order], None] = None, modify_order_handler: Callable[[Order, Quantity], None] = None, bool debug=False, bool log_events=True, bool log_commands=True)

Provides a generic order execution manager.

Cache the given submit order command with the manager.

Cancel the given order with the manager.

Create a new submit order command for the given order.

Return the managers cached submit order commands.

Handle the given event.

If a handler for the given event is not implemented then this will simply be a no-op.

Modify the given order with the manager.

Pop the submit order command for the given client_order_id out of the managers cache (if found).

Reset the manager, clearing all stateful values.

Check if the given order should be managed.

MatchingCore(InstrumentId instrument_id, Price price_increment, trigger_stop_order: Callable, fill_market_order: Callable, fill_limit_order: Callable)

Provides a generic order matching core.

Return the current ask price for the matching core.

Return the current bid price for the matching core.

Return the instrument ID for the matching core.

Return the current last price for the matching core.

Match the given order.

Return the instruments minimum price increment (tick size) for the matching core.

Return the instruments price precision for the matching core.

Bases: TradingCommand

BatchCancelOrders(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, list cancels, UUID4 command_id, uint64_t ts_init, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to batch cancel orders working on a venue for an instrument.

The execution client ID for the command.

Return a batch cancel order command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: TradingCommand

CancelAllOrders(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, OrderSide order_side, UUID4 command_id, uint64_t ts_init, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to cancel all orders for an instrument.

The execution client ID for the command.

Return a cancel order command from the given dict values.

The command message ID.

The instrument ID associated with the command.

The order side for the command.

Additional specific parameters for the command.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: TradingCommand

CancelOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, UUID4 command_id, uint64_t ts_init, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to cancel an order.

The execution client ID for the command.

The client order ID associated with the command.

Return a cancel order command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the command.

ExecutionReportCommand(InstrumentId instrument_id: InstrumentId | None, datetime start: datetime | None, datetime end: datetime | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

The base class for all execution report commands.

This class should not be used directly, but through a concrete subclass.

The end datetime (UTC) of request time range.

:returns datetime or None

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

:returns datetime or None

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: ExecutionReportCommand

GenerateExecutionMassStatus(TraderId trader_id, ClientId client_id, UUID4 command_id, uint64_t ts_init, Venue venue: Venue | None = None, dict params: dict | None = None) -> None

Command to generate an execution mass status report.

The client ID associated with the command.

The end datetime (UTC) of request time range.

:returns datetime or None

Return a generate execution mass status command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

:returns datetime or None

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue associated with the command.

Bases: ExecutionReportCommand

GenerateFillReports(InstrumentId instrument_id: InstrumentId | None, VenueOrderId venue_order_id: VenueOrderId | None, datetime start: datetime | None, datetime end: datetime | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Command to generate fill reports.

The end datetime (UTC) of request time range.

:returns datetime or None

Return a generate fill reports command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

:returns datetime or None

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the command.

Bases: ExecutionReportCommand

GenerateOrderStatusReport(InstrumentId instrument_id: InstrumentId | None, ClientOrderId client_order_id: ClientOrderId | None, VenueOrderId venue_order_id: VenueOrderId | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Command to generate an order status report.

The client order ID associated with the command.

The end datetime (UTC) of request time range.

:returns datetime or None

Return a generate order status report command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

:returns datetime or None

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the command.

Bases: ExecutionReportCommand

GenerateOrderStatusReports(InstrumentId instrument_id: InstrumentId | None, datetime start: datetime | None, datetime end: datetime | None, bool open_only, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None, LogLevel log_receipt_level=LogLevel.INFO) -> None

Command to generate order status reports.

The end datetime (UTC) of request time range.

:returns datetime or None

Return a generate order status reports command from the given dict values.

The command message ID.

The instrument ID associated with the command.

The log level for logging received reports.

If the request is only for open orders.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

:returns datetime or None

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: ExecutionReportCommand

GeneratePositionStatusReports(InstrumentId instrument_id: InstrumentId | None, datetime start: datetime | None, datetime end: datetime | None, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

Command to generate position status reports.

The end datetime (UTC) of request time range.

:returns datetime or None

Return a generate position status reports command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The start datetime (UTC) of request time range (inclusive).

:returns datetime or None

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: TradingCommand

ModifyOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, Quantity quantity: Quantity | None, Price price: Price | None, Price trigger_price: Price | None, UUID4 command_id, uint64_t ts_init, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to modify the properties of an existing order.

The execution client ID for the command.

The client order ID associated with the command.

Return a modify order command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The updated price for the command.

The updated quantity for the command.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

The updated trigger price for the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the command.

QueryAccount(TraderId trader_id, AccountId account_id, UUID4 command_id, uint64_t ts_init, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to query an account.

The account ID to query.

The execution client ID for the command.

Return a query account command from the given dict values.

The command message ID.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: TradingCommand

QueryOrder(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, UUID4 command_id, uint64_t ts_init, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to query an order.

The execution client ID for the command.

The client order ID for the order to query.

Return a query order command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID for the order to query.

Bases: TradingCommand

SubmitOrder(TraderId trader_id, StrategyId strategy_id, Order order, UUID4 command_id, uint64_t ts_init, PositionId position_id: PositionId | None = None, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to submit the given order.

The execution client ID for the command.

The execution algorithm ID for the order.

Return a submit order command from the given dict values.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The position ID to associate with the order.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: TradingCommand

SubmitOrderList(TraderId trader_id, StrategyId strategy_id, OrderList order_list, UUID4 command_id, uint64_t ts_init, PositionId position_id: PositionId | None = None, ClientId client_id=None, dict params: dict | None = None) -> None

Represents a command to submit an order list consisting of an order batch/bulk of related parent-child contingent orders.

This command can correspond to a NewOrderList message for the FIX protocol.

The execution client ID for the command.

The execution algorithm ID for the order list.

Return a submit order list command from the given dict values.

If the contained order_list holds at least one emulated order.

The command message ID.

The instrument ID associated with the command.

The order list to submit.

Additional specific parameters for the command.

The position ID to associate with the orders.

The strategy ID associated with the command.

Return a dictionary representation of this object.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

TradingCommand(ClientId client_id: ClientId | None, TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, UUID4 command_id, uint64_t ts_init, dict params: dict | None = None) -> None

The base class for all trading related commands.

This class should not be used directly, but through a concrete subclass.

The execution client ID for the command.

The command message ID.

The instrument ID associated with the command.

Additional specific parameters for the command.

The strategy ID associated with the command.

The trader ID associated with the command.

UNIX timestamp (nanoseconds) when the object was initialized.

The base class for all execution reports.

The document message ID.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: ExecutionReport

Represents an order status at a point in time.

Reporting is best-effort; if filled exceeds quantity due to venue anomalies, avoid negative leaves_qty by clamping to zero.

Return whether the reported order status is ‘open’.

Return a dictionary representation of this object.

Return an order status report from the given dict values.

The document message ID.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: ExecutionReport

Represents a report of a single order fill.

Return a dictionary representation of this object.

Return a fill report from the given dict values.

The document message ID.

UNIX timestamp (nanoseconds) when the object was initialized.

Bases: ExecutionReport

Represents a position status at a point in time.

Return a dictionary representation of this object.

Return a position status report from the given dict values.

The document message ID.

UNIX timestamp (nanoseconds) when the object was initialized.

Represents an execution mass status report for an execution client - including status of all orders, trades for those orders and open positions.

The order status reports.

The position status reports.

Add the order reports to the mass status.

Add the fill reports to the mass status.

Add the position status reports to the mass status.

Return a dictionary representation of this object.

Return an execution mass status from the given dict values.

The document message ID.

UNIX timestamp (nanoseconds) when the object was initialized.

---

## Indicators

**URL:** https://nautilustrader.io/docs/latest/api_reference/indicators

**Contents:**
- Indicators
  - class AdaptiveMovingAverage​
    - alpha_diff​
    - alpha_fast​
    - alpha_slow​
    - handle_bar(self, Bar bar) → void​
    - handle_quote_tick(self, QuoteTick tick) → void​
    - handle_trade_tick(self, TradeTick tick) → void​
    - period_alpha_fast​
    - period_alpha_slow​

The indicator subpackage provides a set of efficient indicators and analyzers.

These are classes which can be used for signal discovery and filtering. The idea is to use the provided indicators as is, or as inspiration for a trader to implement their own proprietary indicator algorithms with the platform.

AdaptiveMovingAverage(int period_er, int period_alpha_fast, int period_alpha_slow, PriceType price_type=PriceType.LAST)

An indicator which calculates an adaptive moving average (AMA) across a rolling window. Developed by Perry Kaufman, the AMA is a moving average designed to account for market noise and volatility. The AMA will closely follow prices when the price swings are relatively small and the noise is low. The AMA will increase lag when the price swings increase.

The alpha difference value.

The alpha fast value.

The alpha slow value.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

The period of the fast smoothing constant.

The period of the slow smoothing constant.

The period of the internal EfficiencyRatio indicator.

Update the indicator with the given raw value.

ArcherMovingAveragesTrends(int fast_period, int slow_period, int signal_period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL)

Archer Moving Averages Trends indicator.

Update the indicator with the given bar.

Update the indicator with the given close price value.

AroonOscillator(int period)

The Aroon (AR) indicator developed by Tushar Chande attempts to determine whether an instrument is trending, and how strong the trend is. AroonUp and AroonDown lines make up the indicator with their formulas below.

The current aroon down value.

The current aroon up value.

Update the indicator with the given bar.

Update the indicator with the given raw values.

AverageTrueRange(int period, MovingAverageType ma_type=MovingAverageType.SIMPLE, bool use_previous=True, double value_floor=0)

An indicator which calculates the average true range across a rolling window. Different moving average types can be selected for the inner calculation.

Update the indicator with the given bar.

Update the indicator with the given raw values.

Bias(int period, MovingAverageType ma_type=MovingAverageType.SIMPLE)

Rate of change between the source and a moving average.

Update the indicator with the given bar.

Update the indicator with the given raw values.

BollingerBands(int period, double k, MovingAverageType ma_type=MovingAverageType.SIMPLE)

A Bollinger Band® is a technical analysis tool defined by a set of trend lines plotted two standard deviations (positively and negatively) away from a simple moving average (SMA) of an instruments price, which can be adjusted to user preferences.

Update the indicator with the given bar.

Update the indicator with the given tick.

Update the indicator with the given tick.

The standard deviation multiple.

The current value of the lower band.

The current value of the middle band.

The period for the moving average.

Update the indicator with the given prices.

The current value of the upper band.

ChandeMomentumOscillator(int period, ma_type=None)

Attempts to capture the momentum of an asset with overbought at 50 and oversold at -50.

Update the indicator with the given bar.

Update the indicator with the given value.

CommodityChannelIndex(int period, double scalar=0.015, ma_type=None)

Commodity Channel Index is a momentum oscillator used to primarily identify overbought and oversold levels relative to a mean.

Update the indicator with the given bar.

The positive float to scale the bands.

Update the indicator with the given raw values.

DirectionalMovement(int period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL)

Two oscillators that capture positive and negative trend movement.

Update the indicator with the given bar.

Update the indicator with the given raw values.

DonchianChannel(int period)

Donchian Channels are three lines generated by moving average calculations that comprise an indicator formed by upper and lower bands around a mid-range or median band. The upper band marks the highest price of a instrument_id over N periods while the lower band marks the lowest price of a instrument_id over N periods. The area between the upper and lower bands represents the Donchian Channel.

Update the indicator with the given bar.

Update the indicator with the given ticks high and low prices.

Update the indicator with the given ticks price.

Update the indicator with the given prices.

DoubleExponentialMovingAverage(int period, PriceType price_type=PriceType.LAST)

The Double Exponential Moving Average attempts to a smoother average with less lag than the normal Exponential Moving Average (EMA).

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

EfficiencyRatio(int period)

An indicator which calculates the efficiency ratio across a rolling window. The Kaufman Efficiency measures the ratio of the relative market speed in relation to the volatility, this could be thought of as a proxy for noise.

Update the indicator with the given bar.

Update the indicator with the given price.

ExponentialMovingAverage(int period, PriceType price_type=PriceType.LAST)

An indicator which calculates an exponential moving average across a rolling window.

The moving average alpha value.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

FuzzyCandle(CandleDirection direction, CandleSize size, CandleBodySize body_size, CandleWickSize upper_wick_size, CandleWickSize lower_wick_size)

Represents a fuzzy candle.

The candles fuzzy body size.

The candles close direction.

The candles fuzzy lower wick size.

The candles fuzzy overall size.

The candles fuzzy upper wick size.

FuzzyCandlesticks(int period, double threshold1=0.5, double threshold2=1.0, double threshold3=2.0, double threshold4=3.0)

An indicator which fuzzifies bar data to produce fuzzy candlesticks. Bar data is dimensionally reduced via fuzzy feature extraction.

Update the indicator with the given bar.

Update the indicator with the given raw values.

The last fuzzy candle.

The fuzzy candle represented as a vector of ints.

HullMovingAverage(int period, PriceType price_type=PriceType.LAST)

An indicator which calculates a Hull Moving Average (HMA) across a rolling window. The HMA, developed by Alan Hull, is an extremely fast and smooth moving average.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

Indicator(list params)

The base class for all indicators.

This class should not be used directly, but through a concrete subclass.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

KeltnerChannel(int period, double k_multiplier, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, MovingAverageType ma_type_atr=MovingAverageType.SIMPLE, bool use_previous=True, double atr_floor=0)

The Keltner channel is a volatility based envelope set above and below a central moving average. Traditionally the middle band is an EMA based on the typical price (high + low + close) / 3, the upper band is the middle band plus the ATR. The lower band is the middle band minus the ATR.

Update the indicator with the given bar.

Update the indicator with the given raw values.

KeltnerPosition(int period, double k_multiplier, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, MovingAverageType ma_type_atr=MovingAverageType.SIMPLE, bool use_previous=True, double atr_floor=0)

An indicator which calculates the relative position of the given price within a defined Keltner channel. This provides a measure of the relative ‘extension’ of a market from the mean, as a multiple of volatility.

Update the indicator with the given bar.

Update the indicator with the given raw value.

KlingerVolumeOscillator(int fast_period, int slow_period, int signal_period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL)

This indicator was developed by Stephen J. Klinger. It is designed to predict price reversals in a market by comparing volume to price.

Update the indicator with the given bar.

Update the indicator with the given raw values.

LinearRegression(int period=0)

An indicator that calculates a simple linear regression.

Update the indicator with the given bar.

Update the indicator with the given raw values.

MovingAverage(int period, list params, PriceType price_type)

The base class for all moving average type indicators.

This class should not be used directly, but through a concrete subclass.

The count of inputs received by the indicator.

The moving average period.

The specified price type for extracting values from quotes.

Update the indicator with the given raw value.

The current output value.

MovingAverageConvergenceDivergence(int fast_period, int slow_period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, PriceType price_type=PriceType.LAST)

An indicator which calculates the difference between two moving averages. Different moving average types can be selected for the inner calculation.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given close price.

Provides a factory to construct different moving average indicators.

Create a moving average indicator corresponding to the given ma_type.

OnBalanceVolume(int period=0)

An indicator which calculates the momentum of relative positive or negative volume.

Update the indicator with the given bar.

Update the indicator with the given raw values.

Pressure(int period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, double atr_floor=0)

An indicator which calculates the relative volume (multiple of average volume) to move the market across a relative range (multiple of ATR).

Update the indicator with the given bar.

Update the indicator with the given raw values.

PsychologicalLine(int period, ma_type=None)

The Psychological Line is an oscillator-type indicator that compares the number of the rising periods to the total number of periods. In other words, it is the percentage of bars that close above the previous bar over a given period.

Update the indicator with the given bar.

Update the indicator with the given raw value.

RateOfChange(int period, bool use_log=False)

An indicator which calculates the rate of change of price over a defined period. The return output can be simple or log.

Update the indicator with the given bar.

Update the indicator with the given price.

RelativeStrengthIndex(int period, ma_type=None)

An indicator which calculates a relative strength index (RSI) across a rolling window.

Update the indicator with the given bar.

Update the indicator with the given value.

RelativeVolatilityIndex(int period, double scalar=100.0, ma_type=None)

The Relative Volatility Index (RVI) was created in 1993 and revised in 1995. Instead of adding up price changes like RSI based on price direction, the RVI adds up standard deviations based on price direction.

Update the indicator with the given bar.

Update the indicator with the given raw values.

SimpleMovingAverage(int period, PriceType price_type=PriceType.LAST)

An indicator which calculates a simple moving average across a rolling window.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

SpreadAnalyzer(InstrumentId instrument_id, int capacity) -> None

Provides various spread analysis metrics.

The current average spread.

The indicators spread capacity.

Update the analyzer with the given quote tick.

The indicators instrument ID.

Stochastics(int period_k, int period_d)

An oscillator which can indicate when an asset may be over bought or over sold.

Update the indicator with the given bar.

Update the indicator with the given raw values.

A swing indicator which calculates and stores various swing metrics.

Update the indicator with the given bar.

Update the indicator with the given raw values.

VariableIndexDynamicAverage(int period, PriceType price_type=PriceType.LAST, MovingAverageType cmo_ma_type=MovingAverageType.SIMPLE)

Variable Index Dynamic Average (VIDYA) was developed by Tushar Chande. It is similar to an Exponential Moving Average, but it has a dynamically adjusted lookback period dependent on relative price volatility as measured by Chande Momentum Oscillator (CMO). When volatility is high, VIDYA reacts faster to price changes. It is often used as moving average or trend identifier.

The moving average alpha value.

The normal cmo value.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

VerticalHorizontalFilter(int period, MovingAverageType ma_type=MovingAverageType.SIMPLE)

The Vertical Horizon Filter (VHF) was created by Adam White to identify trending and ranging markets.

Update the indicator with the given bar.

Update the indicator with the given raw value.

VolatilityRatio(int fast_period, int slow_period, MovingAverageType ma_type=MovingAverageType.SIMPLE, bool use_previous=True, double value_floor=0)

An indicator which calculates the ratio of different ranges of volatility. Different moving average types can be selected for the inner ATR calculations.

Update the indicator with the given bar.

Update the indicator with the given raw value.

VolumeWeightedAveragePrice()

An indicator which calculates the volume weighted average price for the day.

Update the indicator with the given bar.

Update the indicator with the given raw values.

WeightedMovingAverage(int period, weights=None, PriceType price_type=PriceType.LAST)

An indicator which calculates a weighted moving average across a rolling window.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

WilderMovingAverage(int period, PriceType price_type=PriceType.LAST)

The Wilder’s Moving Average is simply an Exponential Moving Average (EMA) with a modified alpha = 1 / period.

The moving average alpha value.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

Update the indicator with the given raw value.

AdaptiveMovingAverage(int period_er, int period_alpha_fast, int period_alpha_slow, PriceType price_type=PriceType.LAST)

An indicator which calculates an adaptive moving average (AMA) across a rolling window. Developed by Perry Kaufman, the AMA is a moving average designed to account for market noise and volatility. The AMA will closely follow prices when the price swings are relatively small and the noise is low. The AMA will increase lag when the price swings increase.

The alpha difference value.

The alpha fast value.

The alpha slow value.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The period of the fast smoothing constant.

The period of the slow smoothing constant.

The period of the internal EfficiencyRatio indicator.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

DoubleExponentialMovingAverage(int period, PriceType price_type=PriceType.LAST)

The Double Exponential Moving Average attempts to a smoother average with less lag than the normal Exponential Moving Average (EMA).

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

ExponentialMovingAverage(int period, PriceType price_type=PriceType.LAST)

An indicator which calculates an exponential moving average across a rolling window.

The moving average alpha value.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

HullMovingAverage(int period, PriceType price_type=PriceType.LAST)

An indicator which calculates a Hull Moving Average (HMA) across a rolling window. The HMA, developed by Alan Hull, is an extremely fast and smooth moving average.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

MovingAverage(int period, list params, PriceType price_type)

The base class for all moving average type indicators.

This class should not be used directly, but through a concrete subclass.

The count of inputs received by the indicator.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

Provides a factory to construct different moving average indicators.

Create a moving average indicator corresponding to the given ma_type.

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

SimpleMovingAverage(int period, PriceType price_type=PriceType.LAST)

An indicator which calculates a simple moving average across a rolling window.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

VariableIndexDynamicAverage(int period, PriceType price_type=PriceType.LAST, MovingAverageType cmo_ma_type=MovingAverageType.SIMPLE)

Variable Index Dynamic Average (VIDYA) was developed by Tushar Chande. It is similar to an Exponential Moving Average, but it has a dynamically adjusted lookback period dependent on relative price volatility as measured by Chande Momentum Oscillator (CMO). When volatility is high, VIDYA reacts faster to price changes. It is often used as moving average or trend identifier.

The moving average alpha value.

The normal cmo value.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

WeightedMovingAverage(int period, weights=None, PriceType price_type=PriceType.LAST)

An indicator which calculates a weighted moving average across a rolling window.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

WilderMovingAverage(int period, PriceType price_type=PriceType.LAST)

The Wilder’s Moving Average is simply an Exponential Moving Average (EMA) with a modified alpha = 1 / period.

The moving average alpha value.

The count of inputs received by the indicator.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

The moving average period.

The specified price type for extracting values from quotes.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

The current output value.

FuzzyCandle(CandleDirection direction, CandleSize size, CandleBodySize body_size, CandleWickSize upper_wick_size, CandleWickSize lower_wick_size)

Represents a fuzzy candle.

The candles fuzzy body size.

The candles close direction.

The candles fuzzy lower wick size.

The candles fuzzy overall size.

The candles fuzzy upper wick size.

FuzzyCandlesticks(int period, double threshold1=0.5, double threshold2=1.0, double threshold3=2.0, double threshold4=3.0)

An indicator which fuzzifies bar data to produce fuzzy candlesticks. Bar data is dimensionally reduced via fuzzy feature extraction.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

The last fuzzy candle.

The fuzzy candle represented as a vector of ints.

ChandeMomentumOscillator(int period, ma_type=None)

Attempts to capture the momentum of an asset with overbought at 50 and oversold at -50.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given value.

CommodityChannelIndex(int period, double scalar=0.015, ma_type=None)

Commodity Channel Index is a momentum oscillator used to primarily identify overbought and oversold levels relative to a mean.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

The positive float to scale the bands.

Update the indicator with the given raw values.

EfficiencyRatio(int period)

An indicator which calculates the efficiency ratio across a rolling window. The Kaufman Efficiency measures the ratio of the relative market speed in relation to the volatility, this could be thought of as a proxy for noise.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given price.

PsychologicalLine(int period, ma_type=None)

The Psychological Line is an oscillator-type indicator that compares the number of the rising periods to the total number of periods. In other words, it is the percentage of bars that close above the previous bar over a given period.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

RateOfChange(int period, bool use_log=False)

An indicator which calculates the rate of change of price over a defined period. The return output can be simple or log.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given price.

RelativeStrengthIndex(int period, ma_type=None)

An indicator which calculates a relative strength index (RSI) across a rolling window.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given value.

RelativeVolatilityIndex(int period, double scalar=100.0, ma_type=None)

The Relative Volatility Index (RVI) was created in 1993 and revised in 1995. Instead of adding up price changes like RSI based on price direction, the RVI adds up standard deviations based on price direction.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

Stochastics(int period_k, int period_d)

An oscillator which can indicate when an asset may be over bought or over sold.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

SpreadAnalyzer(InstrumentId instrument_id, int capacity) -> None

Provides various spread analysis metrics.

The current average spread.

The indicators spread capacity.

Abstract method (implement in subclass).

Update the analyzer with the given quote tick.

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The indicators instrument ID.

The name of the indicator.

All stateful fields are reset to their initial value.

ArcherMovingAveragesTrends(int fast_period, int slow_period, int signal_period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL)

Archer Moving Averages Trends indicator.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given close price value.

AroonOscillator(int period)

The Aroon (AR) indicator developed by Tushar Chande attempts to determine whether an instrument is trending, and how strong the trend is. AroonUp and AroonDown lines make up the indicator with their formulas below.

The current aroon down value.

The current aroon up value.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

Bias(int period, MovingAverageType ma_type=MovingAverageType.SIMPLE)

Rate of change between the source and a moving average.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

DirectionalMovement(int period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL)

Two oscillators that capture positive and negative trend movement.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

LinearRegression(int period=0)

An indicator that calculates a simple linear regression.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

MovingAverageConvergenceDivergence(int fast_period, int slow_period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, PriceType price_type=PriceType.LAST)

An indicator which calculates the difference between two moving averages. Different moving average types can be selected for the inner calculation.

Update the indicator with the given bar.

Update the indicator with the given quote tick.

Update the indicator with the given trade tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given close price.

A swing indicator which calculates and stores various swing metrics.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

AverageTrueRange(int period, MovingAverageType ma_type=MovingAverageType.SIMPLE, bool use_previous=True, double value_floor=0)

An indicator which calculates the average true range across a rolling window. Different moving average types can be selected for the inner calculation.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

BollingerBands(int period, double k, MovingAverageType ma_type=MovingAverageType.SIMPLE)

A Bollinger Band® is a technical analysis tool defined by a set of trend lines plotted two standard deviations (positively and negatively) away from a simple moving average (SMA) of an instruments price, which can be adjusted to user preferences.

Update the indicator with the given bar.

Update the indicator with the given tick.

Update the indicator with the given tick.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The standard deviation multiple.

The current value of the lower band.

The current value of the middle band.

The name of the indicator.

The period for the moving average.

All stateful fields are reset to their initial value.

Update the indicator with the given prices.

The current value of the upper band.

DonchianChannel(int period)

Donchian Channels are three lines generated by moving average calculations that comprise an indicator formed by upper and lower bands around a mid-range or median band. The upper band marks the highest price of a instrument_id over N periods while the lower band marks the lowest price of a instrument_id over N periods. The area between the upper and lower bands represents the Donchian Channel.

Update the indicator with the given bar.

Update the indicator with the given ticks high and low prices.

Update the indicator with the given ticks price.

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given prices.

KeltnerChannel(int period, double k_multiplier, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, MovingAverageType ma_type_atr=MovingAverageType.SIMPLE, bool use_previous=True, double atr_floor=0)

The Keltner channel is a volatility based envelope set above and below a central moving average. Traditionally the middle band is an EMA based on the typical price (high + low + close) / 3, the upper band is the middle band plus the ATR. The lower band is the middle band minus the ATR.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

KeltnerPosition(int period, double k_multiplier, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, MovingAverageType ma_type_atr=MovingAverageType.SIMPLE, bool use_previous=True, double atr_floor=0)

An indicator which calculates the relative position of the given price within a defined Keltner channel. This provides a measure of the relative ‘extension’ of a market from the mean, as a multiple of volatility.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

VerticalHorizontalFilter(int period, MovingAverageType ma_type=MovingAverageType.SIMPLE)

The Vertical Horizon Filter (VHF) was created by Adam White to identify trending and ranging markets.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

VolatilityRatio(int fast_period, int slow_period, MovingAverageType ma_type=MovingAverageType.SIMPLE, bool use_previous=True, double value_floor=0)

An indicator which calculates the ratio of different ranges of volatility. Different moving average types can be selected for the inner ATR calculations.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw value.

KlingerVolumeOscillator(int fast_period, int slow_period, int signal_period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL)

This indicator was developed by Stephen J. Klinger. It is designed to predict price reversals in a market by comparing volume to price.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

OnBalanceVolume(int period=0)

An indicator which calculates the momentum of relative positive or negative volume.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

Pressure(int period, MovingAverageType ma_type=MovingAverageType.EXPONENTIAL, double atr_floor=0)

An indicator which calculates the relative volume (multiple of average volume) to move the market across a relative range (multiple of ATR).

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

VolumeWeightedAveragePrice()

An indicator which calculates the volume weighted average price for the day.

Update the indicator with the given bar.

Abstract method (implement in subclass).

Abstract method (implement in subclass).

If the indicator has received inputs.

If the indicator is warmed up and initialized.

The name of the indicator.

All stateful fields are reset to their initial value.

Update the indicator with the given raw values.

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

---

## Binance

**URL:** https://nautilustrader.io/docs/latest/api_reference/adapters/binance

**Contents:**
- Binance
  - class BinanceAccountType​
    - property is_spot​
    - property is_margin​
    - property is_spot_or_margin​
    - property is_futures : bool​
    - SPOT = 'SPOT'​
    - MARGIN = 'MARGIN'​
    - ISOLATED_MARGIN = 'ISOLATED_MARGIN'​
    - USDT_FUTURES = 'USDT_FUTURES'​

Binance cryptocurreny exchange integration adapter.

This subpackage provides an instrument provider, data and execution clients, configurations, data types and constants for connecting to and interacting with Binance’s API.

For convenience, the most commonly used symbols are re-exported at the subpackage’s top level, so downstream code can simply import from nautilus_trader.adapters.binance.

Represents a Binance account type.

Bases: LiveDataClientConfig

Configuration for BinanceDataClient instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: LiveExecClientConfig

Configuration for BinanceExecutionClient instances.

A short retry_delay with frequent retries may result in account bans.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: InstrumentProvider

Provides a means of loading instruments from the Binance Futures exchange.

Add the given instrument to the provider.

Add the given instruments bulk to the provider.

Add the given currency to the provider.

Return the count of instruments held by the provider.

Return all currencies held by the instrument provider.

Return the currency with the given code (if found).

Return the instrument for the given instrument ID (if found).

Return all loaded instruments as a map keyed by instrument ID.

If no instruments loaded, will return an empty dict.

Initialize the instrument provider.

Return all loaded instruments.

Load the instrument for the given ID into the provider, optionally applying the given filters.

Load the latest instruments into the provider, optionally applying the given filters.

Load the latest instruments into the provider asynchronously, optionally applying the given filters.

Load the instrument for the given ID into the provider asynchronously, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Represents a Binance Futures mark price and funding rate update.

Return a Binance Futures mark price update parsed from the given values.

Return the fully qualified name for the Data class.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Represents a Binance private key cryptographic algorithm type.

Bases: LiveDataClientFactory

Provides a Binance live data client factory.

Create a new Binance data client.

Bases: LiveExecClientFactory

Provides a Binance live execution client factory.

Create a new Binance execution client.

Provides a means of loading Binance order book data.

Return the deltas pandas.DataFrame loaded from the given CSV file_path.

Bases: InstrumentProvider

Provides a means of loading instruments from the Binance Spot/Margin exchange.

Add the given instrument to the provider.

Add the given instruments bulk to the provider.

Add the given currency to the provider.

Return the count of instruments held by the provider.

Return all currencies held by the instrument provider.

Return the currency with the given code (if found).

Return the instrument for the given instrument ID (if found).

Return all loaded instruments as a map keyed by instrument ID.

If no instruments loaded, will return an empty dict.

Initialize the instrument provider.

Return all loaded instruments.

Load the instrument for the given ID into the provider, optionally applying the given filters.

Load the latest instruments into the provider, optionally applying the given filters.

Load the latest instruments into the provider asynchronously, optionally applying the given filters.

Load the instrument for the given ID into the provider asynchronously, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Cache and return a Binance HTTP client with the given key and secret.

If a cached client with matching parameters already exists, the cached client will be returned.

Bases: LiveDataClientConfig

Configuration for BinanceDataClient instances.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Bases: LiveExecClientConfig

Configuration for BinanceExecutionClient instances.

A short retry_delay with frequent retries may result in account bans.

Return a dictionary representation of the configuration.

Return the fully qualified name for the NautilusConfig class.

Return the hashed identifier for the configuration.

Return serialized JSON encoded bytes.

Return a dictionary representation of the configuration with JSON primitive types as values.

Generate a JSON schema for this configuration class.

Return a decoded object of the given cls.

Return whether the configuration can be represented as valid JSON.

Cache and return a Binance HTTP client with the given key and secret.

If a cached client with matching parameters already exists, the cached client will be returned.

Cache and return an instrument provider for the Binance Spot/Margin exchange.

If a cached provider already exists, then that provider will be returned.

Cache and return an instrument provider for the Binance Futures exchange.

If a cached provider already exists, then that provider will be returned.

Bases: LiveDataClientFactory

Provides a Binance live data client factory.

Create a new Binance data client.

Bases: LiveExecClientFactory

Provides a Binance live execution client factory.

Create a new Binance execution client.

Defines Binance common enums.

Represents a Binance private key cryptographic algorithm type.

Represents a Binance Futures position side.

Represents a Binance rate limit type.

Represents a Binance rate limit interval.

Represents a Binance kline chart interval.

Represents a Binance exchange filter type.

Represents a Binance symbol filter type.

Represents a Binance account type.

Represents a Binance order side.

Represents a Binance execution type.

Represents a Binance order status.

Represents a Binance order time in force.

Represents a Binance order type.

Represents a Binance endpoint security type.

Represents a Binance newOrderRespType.

Represents a Binance error code (covers futures).

Provides common parsing methods for enums used by the ‘Binance’ exchange.

This class should not be used directly, but through a concrete subclass.

Represents an aggregated Binance bar.

This data type includes the raw data provided by Binance.

Return a Binance bar parsed from the given values.

Return a dictionary representation of this object.

Return the bar type of bar.

Return the close price of the bar.

Return a legacy Cython bar converted from the given pyo3 Rust object.

Return legacy Cython bars converted from the given pyo3 Rust objects.

Return the fully qualified name for the Data class.

Return the high price of the bar.

If this bar is a revision for a previous bar with the same ts_event.

Determine if the current class is a signal type, optionally checking for a specific signal name.

If the OHLC are all equal to a single price.

Return the low price of the bar.

Return the open price of the bar.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust bars converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the volume of the bar.

Represents a Binance 24hr statistics ticker.

This data type includes the raw data provided by Binance.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return a Binance Spot/Margin ticker parsed from the given values.

Return a dictionary representation of this object.

Return the fully qualified name for the Data class.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Bases: BinanceCommonDataClient

Provides a data client for the Binance Futures exchange.

Cancel all pending tasks and await their cancellation.

Run the given coroutine with error handling and optional callback actions when done.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Disconnect the client.

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

Run the given coroutine after a delay.

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

Defines Binance Futures specific enums.

Represents a Binance Futures derivatives contract type.

Represents a Binance Futures contract status.

Represents a Binance Futures working type.

Represents a Binance Futures margin type.

Represents a Binance Futures position and balance update reason.

Represents a Binance Futures event type.

Bases: BinanceEnumParser

Provides parsing methods for enums used by the ‘Binance Futures’ exchange.

Bases: BinanceCommonExecutionClient

Provides an execution client for the Binance Futures exchange.

The clients account ID.

The clients account type.

The clients account base currency (None for multi-currency accounts).

Batch cancel orders for the instrument ID contained in the given command.

Cancel all orders for the instrument ID contained in the given command.

Cancel the order with the client order ID contained in the given command.

Cancel all pending tasks and await their cancellation.

Run the given coroutine with error handling and optional callback actions when done.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Disconnect the client.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

Generate an AccountState event and publish on the message bus.

FillReport`s with optional query filters.

The returned list may be empty if no trades match the given parameters.

Generate an ExecutionMassStatus report.

Generate an OrderAccepted event and send it to the ExecutionEngine.

Generate an OrderCancelRejected event and send it to the ExecutionEngine.

Generate an OrderCanceled event and send it to the ExecutionEngine.

Generate an OrderDenied event and send it to the ExecutionEngine.

Generate an OrderExpired event and send it to the ExecutionEngine.

Generate an OrderFilled event and send it to the ExecutionEngine.

Generate an OrderModifyRejected event and send it to the ExecutionEngine.

Generate an OrderRejected event and send it to the ExecutionEngine.

Generate an OrderStatusReport for the given order identifier parameter(s).

If the order is not found, or an error occurs, then logs and returns None.

OrderStatusReport`s with optional query filters.

The returned list may be empty if no orders match the given parameters.

Generate an OrderSubmitted event and send it to the ExecutionEngine.

Generate an OrderTriggered event and send it to the ExecutionEngine.

Generate an OrderUpdated event and send it to the ExecutionEngine.

PositionStatusReport`s with optional query filters.

The returned list may be empty if no positions match the given parameters.

Return the account for the client (if registered).

If the client is connected.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Modify the order with parameters contained in the command.

The venues order management system type.

Query the account specified by the command which will generate an AccountState event.

Initiate a reconciliation for the queried order which will generate an OrderStatusReport.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Run the given coroutine after a delay.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Submit the order contained in the given command for execution.

Submit the order list contained in the given command for execution.

The trader ID associated with the component.

Whether the EXPIRED execution type is treated as a CANCEL.

Whether a position_id will be assigned to order events generated by the client.

The clients venue ID (if not a routing client).

Bases: InstrumentProvider

Provides a means of loading instruments from the Binance Futures exchange.

Load the latest instruments into the provider asynchronously, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Load the instrument for the given ID into the provider asynchronously, optionally applying the given filters.

Add the given instrument to the provider.

Add the given instruments bulk to the provider.

Add the given currency to the provider.

Return the count of instruments held by the provider.

Return all currencies held by the instrument provider.

Return the currency with the given code (if found).

Return the instrument for the given instrument ID (if found).

Return all loaded instruments as a map keyed by instrument ID.

If no instruments loaded, will return an empty dict.

Initialize the instrument provider.

Return all loaded instruments.

Load the instrument for the given ID into the provider, optionally applying the given filters.

Load the latest instruments into the provider, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Represents a Binance Futures mark price and funding rate update.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return a Binance Futures mark price update parsed from the given values.

Return a dictionary representation of this object.

Return the fully qualified name for the Data class.

Determine if the current class is a signal type, optionally checking for a specific signal name.

Bases: BinanceCommonDataClient

Provides a data client for the Binance Spot/Margin exchange.

Cancel all pending tasks and await their cancellation.

Run the given coroutine with error handling and optional callback actions when done.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Disconnect the client.

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

Run the given coroutine after a delay.

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

Defines Binance Spot/Margin specific enums.

Represents Binance Spot/Margin trading permissions.

Represents a Binance Spot/Margin symbol status.

Represents a Binance Spot/Margin event type.

Bases: BinanceEnumParser

Provides parsing methods for enums used by the ‘Binance Spot/Margin’ exchange.

Bases: BinanceCommonExecutionClient

Provides an execution client for the Binance Spot/Margin exchange.

The clients account ID.

The clients account type.

The clients account base currency (None for multi-currency accounts).

Batch cancel orders for the instrument ID contained in the given command.

Cancel all orders for the instrument ID contained in the given command.

Cancel the order with the client order ID contained in the given command.

Cancel all pending tasks and await their cancellation.

Run the given coroutine with error handling and optional callback actions when done.

Degrade the component.

While executing on_degrade() any exception will be logged and reraised, then the component will remain in a DEGRADING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Disconnect the client.

Dispose of the component.

While executing on_dispose() any exception will be logged and reraised, then the component will remain in a DISPOSING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Calling this method multiple times has the same effect as calling it once (it is idempotent). Once called, it cannot be reversed, and no other methods should be called on this instance.

While executing on_fault() any exception will be logged and reraised, then the component will remain in a FAULTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the fully qualified name for the components class.

Generate an AccountState event and publish on the message bus.

FillReport`s with optional query filters.

The returned list may be empty if no trades match the given parameters.

Generate an ExecutionMassStatus report.

Generate an OrderAccepted event and send it to the ExecutionEngine.

Generate an OrderCancelRejected event and send it to the ExecutionEngine.

Generate an OrderCanceled event and send it to the ExecutionEngine.

Generate an OrderDenied event and send it to the ExecutionEngine.

Generate an OrderExpired event and send it to the ExecutionEngine.

Generate an OrderFilled event and send it to the ExecutionEngine.

Generate an OrderModifyRejected event and send it to the ExecutionEngine.

Generate an OrderRejected event and send it to the ExecutionEngine.

Generate an OrderStatusReport for the given order identifier parameter(s).

If the order is not found, or an error occurs, then logs and returns None.

OrderStatusReport`s with optional query filters.

The returned list may be empty if no orders match the given parameters.

Generate an OrderSubmitted event and send it to the ExecutionEngine.

Generate an OrderTriggered event and send it to the ExecutionEngine.

Generate an OrderUpdated event and send it to the ExecutionEngine.

PositionStatusReport`s with optional query filters.

The returned list may be empty if no positions match the given parameters.

Return the account for the client (if registered).

If the client is connected.

Return whether the current component state is DEGRADED.

Return whether the current component state is DISPOSED.

Return whether the current component state is FAULTED.

Return whether the component has been initialized (component.state >= INITIALIZED).

Return whether the current component state is RUNNING.

Return whether the current component state is STOPPED.

Modify the order with parameters contained in the command.

The venues order management system type.

Query the account specified by the command which will generate an AccountState event.

Initiate a reconciliation for the queried order which will generate an OrderStatusReport.

All stateful fields are reset to their initial value.

While executing on_reset() any exception will be logged and reraised, then the component will remain in a RESETTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Resume the component.

While executing on_resume() any exception will be logged and reraised, then the component will remain in a RESUMING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Run the given coroutine after a delay.

Initiate a system-wide shutdown by generating and publishing a ShutdownSystem command.

The command is handled by the system’s NautilusKernel, which will invoke either stop (synchronously) or stop_async (asynchronously) depending on the execution context and the presence of an active event loop.

While executing on_start() any exception will be logged and reraised, then the component will remain in a STARTING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Return the components current state.

While executing on_stop() any exception will be logged and reraised, then the component will remain in a STOPPING state.

If the component is not in a valid state from which to execute this method, then the component state will not change, and an error will be logged.

Submit the order contained in the given command for execution.

Submit the order list contained in the given command for execution.

The trader ID associated with the component.

Whether the EXPIRED execution type is treated as a CANCEL.

Whether a position_id will be assigned to order events generated by the client.

The clients venue ID (if not a routing client).

Bases: InstrumentProvider

Provides a means of loading instruments from the Binance Spot/Margin exchange.

Load the latest instruments into the provider asynchronously, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

Load the instrument for the given ID into the provider asynchronously, optionally applying the given filters.

Add the given instrument to the provider.

Add the given instruments bulk to the provider.

Add the given currency to the provider.

Return the count of instruments held by the provider.

Return all currencies held by the instrument provider.

Return the currency with the given code (if found).

Return the instrument for the given instrument ID (if found).

Return all loaded instruments as a map keyed by instrument ID.

If no instruments loaded, will return an empty dict.

Initialize the instrument provider.

Return all loaded instruments.

Load the instrument for the given ID into the provider, optionally applying the given filters.

Load the latest instruments into the provider, optionally applying the given filters.

Load the instruments for the given IDs into the provider, optionally applying the given filters.

---

## Events

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/events

**Contents:**
- Events
  - class AccountState​
    - account_id​
    - account_type​
    - balances​
    - base_currency​
    - static from_dict(dict values) → AccountState​
    - id​
    - info​
    - is_reported​

Defines the fundamental event types represented within the trading domain.

AccountState(AccountId account_id, AccountType account_type, Currency base_currency, bool reported, list balances, list margins, dict info, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents an event which includes information on the state of the account.

The account ID associated with the event.

The account type for the event.

The account balances.

The account type for the event.

Return an account state event from the given dict values.

The event message identifier.

The additional implementation specific account information.

If the state is reported from the exchange (otherwise system calculated).

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

OrderAccepted(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id, AccountId account_id, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been accepted by the trading venue.

This event often corresponds to a NEW OrdStatus <39> field in FIX execution reports.

The account ID associated with the event.

The client order ID associated with the event.

Return an order accepted event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderCancelRejected(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, str reason, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where a CancelOrder command has been rejected by the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order cancel rejected event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was rejected.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderCanceled(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been canceled at the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order canceled event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderDenied(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, str reason, UUID4 event_id, uint64_t ts_init)

Represents an event where an order has been denied by the Nautilus system.

This could be due an unsupported feature, a risk limit exceedance, or for any other reason that an otherwise valid order is not able to be submitted.

The account ID associated with the event.

The client order ID associated with the event.

Return an order denied event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was denied.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderEmulated(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, UUID4 event_id, uint64_t ts_init)

Represents an event where an order has become emulated by the Nautilus system.

The account ID associated with the event.

The client order ID associated with the event.

Return an order emulated event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

The abstract base class for all order events.

This class should not be used directly, but through a concrete subclass.

The account ID associated with the event.

The client order ID associated with the event.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderExpired(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has expired at the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order expired event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderFilled(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id, AccountId account_id, TradeId trade_id, PositionId position_id: PositionId | None, OrderSide order_side, OrderType order_type, Quantity last_qty, Price last_px, Currency currency, Money commission, LiquiditySide liquidity_side, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False, dict info=None)

Represents an event where an order has been filled at the exchange.

The account ID associated with the event.

The client order ID associated with the event.

The commission generated from the fill.

The currency of the price.

Return an order filled event from the given dict values.

The event message identifier.

The additional fill information.

The instrument ID associated with the event.

Return whether the fill order side is BUY.

Return whether the fill order side is SELL.

The fill price for this execution.

The liquidity side of the event {MAKER, TAKER}.

The position ID (assigned by the venue).

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trade match ID (assigned by the venue).

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderInitialized(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, OrderType order_type, Quantity quantity, TimeInForce time_in_force, bool post_only, bool reduce_only, bool quote_quantity, dict options, TriggerType emulation_trigger, InstrumentId trigger_instrument_id: InstrumentId | None, ContingencyType contingency_type, OrderListId order_list_id: OrderListId | None, list linked_order_ids: list[ClientOrderId] | None, ClientOrderId parent_order_id: ClientOrderId | None, ExecAlgorithmId exec_algorithm_id: ExecAlgorithmId | None, dict exec_algorithm_params: dict[str, object] | None, ClientOrderId exec_spawn_id: ClientOrderId | None, list tags: list[str] | None, UUID4 event_id, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been initialized.

This is a seed event which can instantiate any order through a creation method. This event should contain enough information to be able to send it ‘over the wire’ and have a valid order created with exactly the same properties as if it had been instantiated locally.

The account ID associated with the event.

The client order ID associated with the event.

The orders contingency type.

The order emulation trigger type.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return an order initialized event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The orders linked client order ID(s).

The order initialization options.

The order list ID associated with the order.

The orders parent client order ID.

If the order will only provide liquidity (make a market).

If the order quantity is denominated in the quote currency.

If the event was generated during reconciliation.

If the order carries the ‘reduce-only’ execution instruction.

The strategy ID associated with the event.

The order custom user tags.

The order time in force.

Return a dictionary representation of this object.

The trader ID associated with the event.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderModifyRejected(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, str reason, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where a ModifyOrder command has been rejected by the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order update rejected event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was rejected.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderPendingCancel(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where a CancelOrder command has been sent to the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order pending cancel event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderPendingUpdate(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an ModifyOrder command has been sent to the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order pending update event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderRejected(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, AccountId account_id, str reason, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False, bool due_post_only=False)

Represents an event where an order has been rejected by the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

If the order was rejected because it was post-only and would execute immediately as a taker.

Return an order rejected event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was rejected.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderReleased(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, Price released_price, UUID4 event_id, uint64_t ts_init)

Represents an event where an order was released from the OrderEmulator by the Nautilus system.

The account ID associated with the event.

The client order ID associated with the event.

Return an order released event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The released price for the event.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderSubmitted(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, AccountId account_id, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents an event where an order has been submitted by the system to the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order submitted event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderTriggered(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has triggered.

Applicable to StopLimit orders only.

The account ID associated with the event.

The client order ID associated with the event.

Return an order triggered event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderUpdated(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, Quantity quantity, Price price: Price | None, Price trigger_price: Price | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been updated at the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order updated event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The orders current price.

The orders current quantity.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

The orders current trigger price.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

PositionChanged(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, double avg_px_close, double realized_return, Money realized_pnl, Money unrealized_pnl, UUID4 event_id, uint64_t ts_opened, uint64_t ts_event, uint64_t ts_init)

Represents an event where a position has changed.

Return a position changed event from the given params.

Return a position changed event from the given dict values.

Return a dictionary representation of this object.

PositionClosed(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, ClientOrderId closing_order_id, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, double avg_px_close, double realized_return, Money realized_pnl, UUID4 event_id, uint64_t ts_opened, uint64_t ts_closed, uint64_t duration_ns, uint64_t ts_init)

Represents an event where a position has been closed.

Return a position closed event from the given params.

Return a position closed event from the given dict values.

Return a dictionary representation of this object.

PositionEvent(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, ClientOrderId closing_order_id: ClientOrderId | None, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, double avg_px_close, double realized_return, Money realized_pnl, Money unrealized_pnl, UUID4 event_id, uint64_t ts_opened, uint64_t ts_closed, uint64_t duration_ns, uint64_t ts_event, uint64_t ts_init)

The base class for all position events.

This class should not be used directly, but through a concrete subclass.

The account ID associated with the position.

The average closing price.

The average open price.

The client order ID for the order which closed the position.

The position quote currency.

The total open duration (nanoseconds).

The entry direction from open.

The event message identifier.

The instrument ID associated with the event.

The last fill price for the position.

The last fill quantity for the position.

The client order ID for the order which opened the position.

The peak directional quantity reached by the position.

The position ID associated with the event.

The position open quantity.

The realized PnL for the position (including commissions).

The realized return for the position.

The position signed quantity (positive for LONG, negative for SHORT).

The strategy ID associated with the event.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the position was closed.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

UNIX timestamp (nanoseconds) when the position was opened.

The unrealized PnL for the position (including commissions).

PositionOpened(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, Money realized_pnl, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents an event where a position has been opened.

Return a position opened event from the given params.

Return a position opened event from the given dict values.

Return a dictionary representation of this object.

AccountState(AccountId account_id, AccountType account_type, Currency base_currency, bool reported, list balances, list margins, dict info, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents an event which includes information on the state of the account.

The account ID associated with the event.

The account type for the event.

The account balances.

The account type for the event.

Return an account state event from the given dict values.

The event message identifier.

The additional implementation specific account information.

If the state is reported from the exchange (otherwise system calculated).

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

OrderAccepted(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id, AccountId account_id, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been accepted by the trading venue.

This event often corresponds to a NEW OrdStatus <39> field in FIX execution reports.

The account ID associated with the event.

The client order ID associated with the event.

Return an order accepted event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderCancelRejected(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, str reason, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where a CancelOrder command has been rejected by the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order cancel rejected event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was rejected.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderCanceled(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been canceled at the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order canceled event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderDenied(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, str reason, UUID4 event_id, uint64_t ts_init)

Represents an event where an order has been denied by the Nautilus system.

This could be due an unsupported feature, a risk limit exceedance, or for any other reason that an otherwise valid order is not able to be submitted.

The account ID associated with the event.

The client order ID associated with the event.

Return an order denied event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was denied.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderEmulated(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, UUID4 event_id, uint64_t ts_init)

Represents an event where an order has become emulated by the Nautilus system.

The account ID associated with the event.

The client order ID associated with the event.

Return an order emulated event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

The abstract base class for all order events.

This class should not be used directly, but through a concrete subclass.

The account ID associated with the event.

The client order ID associated with the event.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderExpired(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has expired at the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order expired event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderFilled(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id, AccountId account_id, TradeId trade_id, PositionId position_id: PositionId | None, OrderSide order_side, OrderType order_type, Quantity last_qty, Price last_px, Currency currency, Money commission, LiquiditySide liquidity_side, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False, dict info=None)

Represents an event where an order has been filled at the exchange.

The account ID associated with the event.

The client order ID associated with the event.

The commission generated from the fill.

The currency of the price.

Return an order filled event from the given dict values.

The event message identifier.

The additional fill information.

The instrument ID associated with the event.

Return whether the fill order side is BUY.

Return whether the fill order side is SELL.

The fill price for this execution.

The liquidity side of the event {MAKER, TAKER}.

The position ID (assigned by the venue).

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trade match ID (assigned by the venue).

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderInitialized(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, OrderSide order_side, OrderType order_type, Quantity quantity, TimeInForce time_in_force, bool post_only, bool reduce_only, bool quote_quantity, dict options, TriggerType emulation_trigger, InstrumentId trigger_instrument_id: InstrumentId | None, ContingencyType contingency_type, OrderListId order_list_id: OrderListId | None, list linked_order_ids: list[ClientOrderId] | None, ClientOrderId parent_order_id: ClientOrderId | None, ExecAlgorithmId exec_algorithm_id: ExecAlgorithmId | None, dict exec_algorithm_params: dict[str, object] | None, ClientOrderId exec_spawn_id: ClientOrderId | None, list tags: list[str] | None, UUID4 event_id, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been initialized.

This is a seed event which can instantiate any order through a creation method. This event should contain enough information to be able to send it ‘over the wire’ and have a valid order created with exactly the same properties as if it had been instantiated locally.

The account ID associated with the event.

The client order ID associated with the event.

The orders contingency type.

The order emulation trigger type.

The execution algorithm ID for the order.

The execution algorithm parameters for the order.

The execution algorithm spawning client order ID.

Return an order initialized event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The orders linked client order ID(s).

The order initialization options.

The order list ID associated with the order.

The orders parent client order ID.

If the order will only provide liquidity (make a market).

If the order quantity is denominated in the quote currency.

If the event was generated during reconciliation.

If the order carries the ‘reduce-only’ execution instruction.

The strategy ID associated with the event.

The order custom user tags.

The order time in force.

Return a dictionary representation of this object.

The trader ID associated with the event.

The order emulation trigger instrument ID (will be instrument_id if None).

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderModifyRejected(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, str reason, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where a ModifyOrder command has been rejected by the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order update rejected event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was rejected.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderPendingCancel(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where a CancelOrder command has been sent to the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order pending cancel event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderPendingUpdate(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an ModifyOrder command has been sent to the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order pending update event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderRejected(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, AccountId account_id, str reason, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False, bool due_post_only=False)

Represents an event where an order has been rejected by the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

If the order was rejected because it was post-only and would execute immediately as a taker.

Return an order rejected event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

Return the reason the order was rejected.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderReleased(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, Price released_price, UUID4 event_id, uint64_t ts_init)

Represents an event where an order was released from the OrderEmulator by the Nautilus system.

The account ID associated with the event.

The client order ID associated with the event.

Return an order released event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The released price for the event.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderSubmitted(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, AccountId account_id, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents an event where an order has been submitted by the system to the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order submitted event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderTriggered(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has triggered.

Applicable to StopLimit orders only.

The account ID associated with the event.

The client order ID associated with the event.

Return an order triggered event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

OrderUpdated(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, ClientOrderId client_order_id, VenueOrderId venue_order_id: VenueOrderId | None, AccountId account_id: AccountId | None, Quantity quantity, Price price: Price | None, Price trigger_price: Price | None, UUID4 event_id, uint64_t ts_event, uint64_t ts_init, bool reconciliation=False)

Represents an event where an order has been updated at the trading venue.

The account ID associated with the event.

The client order ID associated with the event.

Return an order updated event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The orders current price.

The orders current quantity.

If the event was generated during reconciliation.

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

The orders current trigger price.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

The venue order ID associated with the event.

PositionChanged(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, double avg_px_close, double realized_return, Money realized_pnl, Money unrealized_pnl, UUID4 event_id, uint64_t ts_opened, uint64_t ts_event, uint64_t ts_init)

Represents an event where a position has changed.

The account ID associated with the position.

The average closing price.

The average open price.

The client order ID for the order which closed the position.

Return a position changed event from the given params.

The position quote currency.

The total open duration (nanoseconds).

The entry direction from open.

Return a position changed event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The last fill price for the position.

The last fill quantity for the position.

The client order ID for the order which opened the position.

The peak directional quantity reached by the position.

The position ID associated with the event.

The position open quantity.

The realized PnL for the position (including commissions).

The realized return for the position.

The position signed quantity (positive for LONG, negative for SHORT).

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the position was closed.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

UNIX timestamp (nanoseconds) when the position was opened.

The unrealized PnL for the position (including commissions).

PositionClosed(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, ClientOrderId closing_order_id, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, double avg_px_close, double realized_return, Money realized_pnl, UUID4 event_id, uint64_t ts_opened, uint64_t ts_closed, uint64_t duration_ns, uint64_t ts_init)

Represents an event where a position has been closed.

The account ID associated with the position.

The average closing price.

The average open price.

The client order ID for the order which closed the position.

Return a position closed event from the given params.

The position quote currency.

The total open duration (nanoseconds).

The entry direction from open.

Return a position closed event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The last fill price for the position.

The last fill quantity for the position.

The client order ID for the order which opened the position.

The peak directional quantity reached by the position.

The position ID associated with the event.

The position open quantity.

The realized PnL for the position (including commissions).

The realized return for the position.

The position signed quantity (positive for LONG, negative for SHORT).

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the position was closed.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

UNIX timestamp (nanoseconds) when the position was opened.

The unrealized PnL for the position (including commissions).

PositionEvent(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, ClientOrderId closing_order_id: ClientOrderId | None, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, double avg_px_close, double realized_return, Money realized_pnl, Money unrealized_pnl, UUID4 event_id, uint64_t ts_opened, uint64_t ts_closed, uint64_t duration_ns, uint64_t ts_event, uint64_t ts_init)

The base class for all position events.

This class should not be used directly, but through a concrete subclass.

The account ID associated with the position.

The average closing price.

The average open price.

The client order ID for the order which closed the position.

The position quote currency.

The total open duration (nanoseconds).

The entry direction from open.

The event message identifier.

The instrument ID associated with the event.

The last fill price for the position.

The last fill quantity for the position.

The client order ID for the order which opened the position.

The peak directional quantity reached by the position.

The position ID associated with the event.

The position open quantity.

The realized PnL for the position (including commissions).

The realized return for the position.

The position signed quantity (positive for LONG, negative for SHORT).

The strategy ID associated with the event.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the position was closed.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

UNIX timestamp (nanoseconds) when the position was opened.

The unrealized PnL for the position (including commissions).

PositionOpened(TraderId trader_id, StrategyId strategy_id, InstrumentId instrument_id, PositionId position_id, AccountId account_id, ClientOrderId opening_order_id, OrderSide entry, PositionSide side, double signed_qty, Quantity quantity, Quantity peak_qty, Quantity last_qty, Price last_px, Currency currency, double avg_px_open, Money realized_pnl, UUID4 event_id, uint64_t ts_event, uint64_t ts_init)

Represents an event where a position has been opened.

The account ID associated with the position.

The average closing price.

The average open price.

The client order ID for the order which closed the position.

Return a position opened event from the given params.

The position quote currency.

The total open duration (nanoseconds).

The entry direction from open.

Return a position opened event from the given dict values.

The event message identifier.

The instrument ID associated with the event.

The last fill price for the position.

The last fill quantity for the position.

The client order ID for the order which opened the position.

The peak directional quantity reached by the position.

The position ID associated with the event.

The position open quantity.

The realized PnL for the position (including commissions).

The realized return for the position.

The position signed quantity (positive for LONG, negative for SHORT).

The strategy ID associated with the event.

Return a dictionary representation of this object.

The trader ID associated with the event.

UNIX timestamp (nanoseconds) when the position was closed.

UNIX timestamp (nanoseconds) when the event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

UNIX timestamp (nanoseconds) when the position was opened.

The unrealized PnL for the position (including commissions).

---

## Model

**URL:** https://nautilustrader.io/docs/latest/api_reference/model/

**Contents:**
- Model
  - class AccountBalance​
    - copy(self) → AccountBalance​
    - currency​
    - free​
    - static from_dict(dict values) → AccountBalance​
    - locked​
    - to_dict(self) → dict​
    - total​
  - class AccountId​

The model subpackage defines a rich trading domain model.

The domain model is agnostic of any system design, seeking to represent the logic and state transitions of trading in a generic way. Many system implementations could be built around this domain model.

AccountBalance(Money total, Money locked, Money free) -> None

Represents an account balance denominated in a particular currency.

Return a copy of this account balance.

The currency of the account.

The account balance free for trading.

Return an account balance from the given dict values.

The account balance locked (assigned to pending orders).

Return a dictionary representation of this object.

The total account balance.

AccountId(str value) -> None

Represents a valid account ID.

Must be correctly formatted with two valid strings either side of a hyphen. It is expected an account ID is the name of the issuer with an account number separated by a hyphen.

Example: “IB-D02851908”.

The issuer and number ID combination must be unique at the firm level.

Return the account ID without issuer name.

Return the account issuer for this ID.

Bar(BarType bar_type, Price open, Price high, Price low, Price close, Quantity volume, uint64_t ts_event, uint64_t ts_init, bool is_revision=False) -> None

Represents an aggregated bar.

Return the bar type of bar.

Return the close price of the bar.

Return a bar parsed from the given values.

Return a legacy Cython bar converted from the given pyo3 Rust object.

Return legacy Cython bars converted from the given pyo3 Rust objects.

Return the high price of the bar.

If this bar is a revision for a previous bar with the same ts_event.

If the OHLC are all equal to a single price.

Return the low price of the bar.

Return the open price of the bar.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust bars converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the volume of the bar.

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

Represents an order book price level.

A price level on one side of the order book with one or more individual orders.

This class is read-only and cannot be initialized from Python.

Return the exposure at this level (price * volume).

Return the orders for the level.

Return the price for the level.

Return the side for the level.

Return the size at this level.

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

ClientId(str value) -> None

Represents a system client ID.

The ID value must be unique at the trader level.

ClientOrderId(str value) -> None

Represents a valid client order ID (assigned by the Nautilus system).

The ID value must be unique at the firm level.

ComponentId(str value) -> None

Represents a valid component ID.

The ID value must be unique at the trader level.

Currency(str code, uint8_t precision, uint16_t iso4217, str name, CurrencyType currency_type) -> None

Represents a medium of exchange in a specified denomination with a fixed decimal precision.

Handles up to 16 decimals of precision (in high-precision mode).

Return the currency code.

Return the currency type.

Return the currency with the given code from the built-in internal map (if found).

Parse a currency from the given string (if found).

Return whether a currency with the given code is CRYPTO.

Return whether a currency with the given code is FIAT.

Return the currency ISO 4217 code.

Return the currency name.

Return the currency decimal precision.

Register the given currency.

Will override the internal currency map.

CustomData(DataType data_type, Data data) -> None

Provides a wrapper for custom data which includes data type information.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

DataType(type type, dict metadata=None) -> None

Represents a data type including metadata.

This class may be used as a key in hash maps throughout the system, thus the key and value contents of metadata must themselves be hashable.

The data types metadata.

The data types topic string.

The Data type of the data.

ExecAlgorithmId(str value) -> None

Represents a valid execution algorithm ID.

FundingRateUpdate(InstrumentId instrument_id, rate, uint64_t ts_event, uint64_t ts_init, next_funding_ns=None) -> None

Represents a funding rate update for a perpetual swap instrument.

Return a funding rate update from the given dict values.

Return a legacy Cython funding rate update converted from the given pyo3 Rust object.

Return legacy Cython funding rate updates converted from the given pyo3 Rust objects.

The instrument ID for the funding rate.

UNIX timestamp (nanoseconds) of the next funding payment (if available, otherwise zero).

The current funding rate.

Return a dictionary representation of this object.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

InstrumentClose(InstrumentId instrument_id, Price close_price, InstrumentCloseType close_type, uint64_t ts_event, uint64_t ts_init) -> None

Represents an instrument close at a venue.

The instrument close price.

The instrument close type.

Return an instrument close price event from the given dict values.

Return a legacy Cython instrument close converted from the given pyo3 Rust object.

Return legacy Cython instrument closes converted from the given pyo3 Rust objects.

The event instrument ID.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust index prices converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the instance was created.

InstrumentId(Symbol symbol, Venue venue) -> None

Represents a valid instrument ID.

The symbol and venue combination should uniquely identify the instrument.

Return an instrument ID from the given PyO3 instance.

Return an instrument ID parsed from the given string value. Must be correctly formatted including symbol and venue components either side of a single period.

Examples: ‘AUD/USD.IDEALPRO’, ‘BTCUSDT.BINANCE’

Return whether the instrument ID is a spread instrument (symbol contains ‘_’ separator).

Return whether the instrument ID is a synthetic instrument (with venue of ‘SYNTH’).

Create a spread InstrumentId from a list of (instrument_id, ratio) tuples.

The resulting symbol will be in the format: (ratio1)symbol1_(ratio2)symbol2_… where positive ratios are shown as (ratio) and negative ratios as ((ratio)). All instrument IDs must have the same venue. The instrument IDs are sorted alphabetically by symbol before creating the spread symbol.

Returns the instrument ticker symbol.

Parse this InstrumentId back into a list of (instrument_id, ratio) tuples.

This is the inverse operation of new_spread(). The symbol must be in the format created by new_spread(): (ratio1)symbol1_(ratio2)symbol2_… The returned list is sorted alphabetically by symbol.

Return a pyo3 object from this legacy Cython instance.

Returns the instrument trading venue.

InstrumentStatus(InstrumentId instrument_id, MarketStatusAction action, uint64_t ts_event, uint64_t ts_init, str reason=None, str trading_event=None, is_trading: bool | None = None, is_quoting: bool | None = None, is_short_sell_restricted: bool | None = None) -> None

Represents an event that indicates a change in an instrument market status.

The instrument market status action.

Return an instrument status update from the given dict values.

Return a legacy Cython quote tick converted from the given pyo3 Rust object.

Return legacy Cython instrument status converted from the given pyo3 Rust objects.

Return the state of quoting in the instrument (if known).

Return the state of short sell restrictions for the instrument (if known and applicable).

Return the state of trading in the instrument (if known).

Additional details about the cause of the status change.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Further information about the status change (if provided).

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the instance was created.

MarginBalance(Money initial, Money maintenance, InstrumentId instrument_id=None) -> None

Represents a margin balance optionally associated with a particular instrument.

Return a copy of this margin balance.

The currency of the margin.

Return a margin balance from the given dict values.

The initial margin requirement.

The instrument ID associated with the margin.

The maintenance margin requirement.

Return a dictionary representation of this object.

MarkPriceUpdate(InstrumentId instrument_id, Price value, uint64_t ts_event, uint64_t ts_init) -> None

Represents a mark price update.

Return a mark price from the given dict values.

Return a legacy Cython mark price converted from the given pyo3 Rust object.

Return legacy Cython trades converted from the given pyo3 Rust objects.

Return the instrument ID.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust mark prices converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Money(value, Currency currency) -> None

Represents an amount of money in a specified currency denomination.

Return the value as a built-in Decimal.

Return the value as a double.

Return the currency for the money.

Return money from the given raw fixed-point integer and currency.

Small raw values can produce a zero money amount depending on the precision of the currency.

Return money parsed from the given string.

Must be correctly formatted with a value and currency separated by a whitespace delimiter.

Example: “1000000.00 USD”.

Return the raw memory representation of the money amount.

Return the formatted string representation of the money.

OrderBook(InstrumentId instrument_id, BookType book_type) -> None

Provides an order book which can handle L1/L2/L3 granularity data.

Add the given order to the book.

Apply the given data to the order book.

Apply the order book delta.

Apply the bulk deltas to the order book.

Apply the depth update to the order book.

Return the bid levels for the order book.

Return the best ask price in the book (if no asks then returns None).

Return the best ask size in the book (if no asks then returns None).

Return the best bid price in the book (if no bids then returns None).

Return the best bid size in the book (if no bids then returns None).

Return the bid levels for the order book.

Return the order book type.

Check book integrity.

Clear the entire order book.

Clear the asks from the order book.

Clear the bids from the order book.

Cancel the given order in the book.

Return the average price expected for the given quantity based on the current state of the order book.

If no average price can be calculated then will return 0.0 (zero).

Return the current total quantity for the given price based on the current state of the order book.

Return the books instrument ID.

Return the mid point (if no market exists then returns None).

Return a string representation of the order book in a human-readable table format.

Reset the order book (clear all stateful values).

Return the last sequence number for the book.

Simulate filling the book with the given order.

Return the top-of-book spread (if no bids or asks then returns None).

Return a QuoteTick created from the top of book levels.

Returns None when the top-of-book bid or ask is missing or invalid (zero size).

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

Return the UNIX timestamp (nanoseconds) when the order book was last updated.

Update the given order in the book.

Return the books update count.

Update the order book with the given quote tick.

This operation is only valid for L1_MBP books maintaining a top level.

Update the order book with the given trade tick.

OrderBookDelta(InstrumentId instrument_id, BookAction action, BookOrder order: BookOrder | None, uint8_t flags, uint64_t sequence, uint64_t ts_event, uint64_t ts_init) -> None

Represents a single update/difference on an OrderBook.

Return the deltas book action {ADD, UPDATE, DELETE, CLEAR}

Return an order book delta which acts as an initial CLEAR.

Return the flags for the delta.

Return an order book delta from the given dict values.

Return a legacy Cython order book delta converted from the given pyo3 Rust object.

Return legacy Cython order book deltas converted from the given pyo3 Rust objects.

Return an order book delta from the given raw values.

Return the deltas book instrument ID.

If the deltas book action is an ADD.

If the deltas book action is a CLEAR.

If the deltas book action is a DELETE.

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

Return the deltas book instrument ID.

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

Return the depth updates book instrument ID.

Return the sequence number for the depth update.

Return a dictionary representation of this object.

Return a QuoteTick created from the top of book levels.

Returns None when the top-of-book bid or ask is missing or invalid (NULL order or zero size).

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

OrderListId(str value) -> None

Represents a valid order list ID (assigned by the Nautilus system).

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

PositionId(str value) -> None

Represents a valid position ID.

Price(double value, uint8_t precision) -> None

Represents a price in a market.

The number of decimal places may vary. For certain asset classes, prices may have negative values. For example, prices for options instruments can be negative under certain conditions.

Handles up to 16 decimals of precision (in high-precision mode).

Return the value as a built-in Decimal.

Return the value as a double.

Return a price from the given integer value.

A precision of zero will be inferred.

Return a price from the given raw fixed-point integer and precision.

Handles up to 16 decimals of precision (in high-precision mode).

Small raw values can produce a zero price depending on the precision.

Return a price parsed from the given string.

Handles up to 16 decimals of precision (in high-precision mode).

The decimal precision will be inferred from the number of digits following the ‘.’ point (if no point then precision zero).

Return the precision for the price.

Return the raw memory representation of the price value.

Return the formatted string representation of the price.

Quantity(double value, uint8_t precision) -> None

Represents a quantity with a non-negative value.

Capable of storing either a whole number (no decimal places) of ‘contracts’ or ‘shares’ (instruments denominated in whole units) or a decimal value containing decimal places for instruments denominated in fractional units.

Handles up to 16 decimals of precision (in high-precision mode).

Return the value as a built-in Decimal.

Return the value as a double.

Return a quantity from the given integer value.

A precision of zero will be inferred.

Return a quantity from the given raw fixed-point integer and precision.

Handles up to 16 decimals of precision (in high-precision mode).

Small raw values can produce a zero quantity depending on the precision.

Return a quantity parsed from the given string.

Handles up to 16 decimals of precision (in high-precision mode).

The decimal precision will be inferred from the number of digits following the ‘.’ point (if no point then precision zero).

Return the precision for the quantity.

Return the raw memory representation of the quantity value.

Return the formatted string representation of the quantity.

Return a quantity with a value of zero.

precision : The precision for the quantity.

The default precision is zero.

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

Return the tick instrument ID.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust quotes converted from the given legacy Cython objects.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

StrategyId(str value) -> None

Represents a valid strategy ID.

Must be correctly formatted with two valid strings either side of a hyphen. It is expected a strategy ID is the class name of the strategy, with an order ID tag number separated by a hyphen.

Example: “EMACross-001”.

The reason for the numerical component of the ID is so that order and position IDs do not collide with those from another strategy within the node instance.

The name and tag combination must be unique at the trader level.

Return the order ID tag value for this ID.

If the strategy ID is the global ‘external’ strategy. This represents the strategy for all orders interacting with this instance of the system which did not originate from any strategy being managed by the system.

Symbol(str value) -> None

Represents a valid ticker symbol ID for a tradable instrument.

The ID value must be unique for a trading venue.

Returns true if the symbol string contains a period (‘.’).

Return the symbol root.

The symbol root is the substring that appears before the first period (‘.’) in the full symbol string. It typically represents the underlying asset for futures and options contracts. If no period is found, the entire symbol string is considered the root.

Return the symbol topic.

The symbol topic is the root symbol with a wildcard ‘*’ appended if the symbol has a root, otherwise returns the full symbol string.

TradeId(str value) -> None

Represents a valid trade match ID (assigned by a trading venue).

Maximum length is 36 characters. Can correspond to the TradeID <1003> field of the FIX protocol.

The unique ID assigned to the trade entity once it is received or matched by the exchange or central counterparty.

TradeTick(InstrumentId instrument_id, Price price, Quantity size, AggressorSide aggressor_side, TradeId trade_id, uint64_t ts_event, uint64_t ts_init) -> None

Represents a single trade tick in a market.

Contains information about a single unique trade which matched buyer and seller counterparties.

Return the ticks aggressor side.

Return a trade tick from the given dict values.

Return a legacy Cython trade tick converted from the given pyo3 Rust object.

Return legacy Cython trades converted from the given pyo3 Rust objects.

Return a trade tick from the given raw values.

Return the ticks instrument ID.

Return the ticks price.

Return the ticks size.

Return a dictionary representation of this object.

Return a pyo3 object from this legacy Cython instance.

Return pyo3 Rust trades converted from the given legacy Cython objects.

Return the ticks trade match ID.

UNIX timestamp (nanoseconds) when the data event occurred.

UNIX timestamp (nanoseconds) when the object was initialized.

TraderId(str value) -> None

Represents a valid trader ID.

Must be correctly formatted with two valid strings either side of a hyphen. It is expected a trader ID is the abbreviated name of the trader with an order ID tag number separated by a hyphen.

Example: “TESTER-001”.

The reason for the numerical component of the ID is so that order and position IDs do not collide with those from another node instance.

The name and tag combination ID value must be unique at the firm level.

Return the order ID tag value for this ID.

Venue(str name) -> None

Represents a valid trading venue ID.

Return the venue with the given code from the built-in internal map (if found).

Currency only supports CME Globex exchange ISO 10383 MIC codes.

Return whether the venue is synthetic (‘SYNTH’).

VenueOrderId(str value) -> None

Represents a valid venue order ID (assigned by a trading venue).

**Examples:**

Example 1 (pycon):
```pycon
>>> spec = BarSpecification(30, BarAggregation.SECOND, PriceType.LAST)>>> spec.timedeltadatetime.timedelta(seconds=30)
```

---
