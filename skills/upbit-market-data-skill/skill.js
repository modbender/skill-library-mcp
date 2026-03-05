#!/usr/bin/env node

const { parseArgs } = require("./src/utils/args");
const { upbit } = require("./src/upbit/endpoints");
const { UpbitError } = require("./src/upbit/errors");
const { loadConfig } = require("./src/config");

function isStrict(options) {
  return options.strict === "true" || options.strict === true;
}

function assertNoExtraPositionals(options) {
  if (Array.isArray(options._) && options._.length > 0) {
    throw new UpbitError("Unexpected positional arguments in strict mode", { extra: options._ });
  }
}

function resolveCandleType(subcommand, options, strict) {
  if (strict) {
    if (!subcommand || String(subcommand).startsWith("--")) {
      throw new UpbitError("Missing candle type: seconds|minutes|days|weeks|months|years");
    }
    if (options.type) {
      throw new UpbitError("Do not use --type in strict mode. Use: candles <type> ...");
    }
    return String(subcommand);
  }

  return (
    (subcommand && !String(subcommand).startsWith("--") ? String(subcommand) : undefined) ||
    (options.type ? String(options.type) : undefined) ||
    (Array.isArray(options._) ? options._.find((x) => typeof x === "string" && !x.startsWith("--")) : undefined)
  );
}

async function main() {
  const { command, subcommand, options } = parseArgs(process.argv.slice(2));
  const strict = isStrict(options);

  if (options.config) {
    process.env.UPBIT_SKILL_CONFIG = String(options.config);
  }

  try {
    if (!command) throw new UpbitError("No command provided");

    let result;

    switch (command) {
      case "pairs": {
        if (strict) assertNoExtraPositionals(options);
        result = await upbit.listTradingPairs({
          is_details: options.details === "true" || options.details === true
        });
        break;
      }

      case "candles": {
        const type = resolveCandleType(subcommand, options, strict);
        if (!type) throw new UpbitError("Missing candle type: seconds|minutes|days|weeks|months|years");
        if (strict) assertNoExtraPositionals(options);
        result = await upbit.listCandles(type, options);
        break;
      }

      case "trades": {
        if (strict) assertNoExtraPositionals(options);
        result = await upbit.recentTrades({
          market: options.market,
          count: options.count,
          to: options.to,
          cursor: options.cursor,
          daysAgo: options.daysAgo
        });
        break;
      }

      case "tickers": {
        if (strict) assertNoExtraPositionals(options);
        result = await upbit.tickersByPairs({ markets: options.markets });
        break;
      }

      case "quote-tickers": {
        if (strict) assertNoExtraPositionals(options);
        result = await upbit.tickersByMarket({ quote: options.quote });
        break;
      }

      case "orderbook": {
        if (strict) assertNoExtraPositionals(options);
        result = await upbit.orderbooks({
          markets: options.markets,
          level: options.level,
          count: options.count
        });
        break;
      }

      case "watchlist": {
        if (strict) assertNoExtraPositionals(options);
        const cfg = loadConfig();
        const markets = Array.isArray(cfg.watchlist) ? cfg.watchlist.join(",") : "";
        if (!markets) throw new UpbitError("watchlist is empty in config");
        result = await upbit.tickersByPairs({ markets });
        break;
      }

      default:
        throw new UpbitError(
          `Unknown command: ${command}\n` +
            `Try:\n` +
            `  pairs --details=true --strict=true\n` +
            `  candles minutes --market=KRW-ETH --unit=5 --count=100 --strict=true\n` +
            `  trades --market=KRW-BTC --count=50 --strict=true\n` +
            `  tickers --markets=KRW-BTC,KRW-ETH --strict=true\n` +
            `  quote-tickers --quote=KRW,BTC --strict=true\n` +
            `  orderbook --markets=KRW-BTC --level=100000 --count=15 --strict=true\n` +
            `  watchlist --strict=true\n`
        );
    }

    process.stdout.write(JSON.stringify({ ok: true, result }, null, 2) + "\\n");
  } catch (err) {
    const e = UpbitError.from(err);
    process.stderr.write(JSON.stringify({ ok: false, error: e.toJSON() }, null, 2) + "\\n");
    process.exit(1);
  }
}

main();

