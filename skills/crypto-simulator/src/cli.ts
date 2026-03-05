import { Command } from 'commander';
import { runBacktest } from './backtest';
import { getOptimizationRankings, optimizeAllCoins, optimizeCoin } from './optimizer';
import { fetchAndCachePrices, normalizeCoin } from './prices';
import { executeSimulationTrade, getPortfolioState, getSimulationHistory } from './simulator';
import { STRATEGIES, StrategyName } from './types';

function parseNumber(value: string, label: string): number {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    throw new Error(`${label} must be a number`);
  }
  return n;
}

function printJson(data: unknown): void {
  console.log(JSON.stringify(data, null, 2));
}

function buildStrategyParams(options: Record<string, unknown>): Record<string, unknown> {
  const params: Record<string, unknown> = {};

  if (typeof options.interval === 'string') {
    params.interval = options.interval;
  }
  if (typeof options.amountPerBuy === 'string') {
    params.amount_per_buy = parseNumber(options.amountPerBuy, 'amount-per-buy');
  }
  if (typeof options.rsiPeriod === 'string') {
    params.rsi_period = parseNumber(options.rsiPeriod, 'rsi-period');
  }
  if (typeof options.buyThreshold === 'string') {
    params.buy_threshold = parseNumber(options.buyThreshold, 'buy-threshold');
  }
  if (typeof options.sellThreshold === 'string') {
    params.sell_threshold = parseNumber(options.sellThreshold, 'sell-threshold');
  }
  if (typeof options.shortPeriod === 'string') {
    params.short_period = parseNumber(options.shortPeriod, 'short-period');
  }
  if (typeof options.longPeriod === 'string') {
    params.long_period = parseNumber(options.longPeriod, 'long-period');
  }
  if (typeof options.gridWidth === 'string') {
    params.grid_width_pct = parseNumber(options.gridWidth, 'grid-width');
  }
  if (typeof options.gridPct === 'string') {
    params.grid_pct = parseNumber(options.gridPct, 'grid-pct');
  }
  if (typeof options.gridCount === 'string') {
    params.grid_count = parseNumber(options.gridCount, 'grid-count');
  }
  if (typeof options.bollingerPeriod === 'string') {
    params.period = parseNumber(options.bollingerPeriod, 'bollinger-period');
  }
  if (typeof options.stdDev === 'string') {
    params.std_dev = parseNumber(options.stdDev, 'std-dev');
  }
  if (typeof options.macdFast === 'string') {
    params.fast_period = parseNumber(options.macdFast, 'macd-fast');
  }
  if (typeof options.macdSlow === 'string') {
    params.slow_period = parseNumber(options.macdSlow, 'macd-slow');
  }
  if (typeof options.macdSignal === 'string') {
    params.signal_period = parseNumber(options.macdSignal, 'macd-signal');
  }
  if (typeof options.meanPeriod === 'string') {
    params.period = parseNumber(options.meanPeriod, 'mean-period');
  }
  if (typeof options.deviationPct === 'string') {
    params.deviation_pct = parseNumber(options.deviationPct, 'deviation-pct');
  }

  return params;
}

export async function main(argv = process.argv): Promise<void> {
  const program = new Command();

  program.name('crypto-simulator').description('Crypto simulator CLI');

  program
    .command('fetch-prices')
    .description('Fetch and cache historical prices')
    .requiredOption('--coins <coins>', 'Comma separated list, e.g. btc,eth,sol')
    .option('--days <days>', 'Number of days', '365')
    .action(async (options: { coins: string; days: string }) => {
      const days = parseNumber(options.days, 'days');
      const coins = options.coins.split(',').map((coin) => normalizeCoin(coin.trim()));

      const summaries = [];
      for (const coin of coins) {
        const rows = await fetchAndCachePrices(coin, days);
        summaries.push({
          coin,
          count: rows.length,
          start_date: rows[0]?.date,
          end_date: rows[rows.length - 1]?.date,
        });
      }

      printJson({ ok: true, summaries });
    });

  program
    .command('backtest')
    .description('Run backtest for one strategy')
    .requiredOption('--strategy <strategy>', `One of: ${STRATEGIES.join(', ')}`)
    .requiredOption('--coin <coin>', 'Coin id or alias')
    .option('--capital <capital>', 'Initial capital', '10000')
    .option('--start-date <startDate>', 'YYYY-MM-DD')
    .option('--end-date <endDate>', 'YYYY-MM-DD')
    .option('--interval <interval>', 'dca interval: daily/weekly/biweekly/monthly')
    .option('--amount-per-buy <amountPerBuy>', 'dca amount per buy')
    .option('--rsi-period <rsiPeriod>', 'rsi period')
    .option('--buy-threshold <buyThreshold>', 'rsi buy threshold')
    .option('--sell-threshold <sellThreshold>', 'rsi sell threshold')
    .option('--short-period <shortPeriod>', 'ma short period')
    .option('--long-period <longPeriod>', 'ma long period')
    .option('--grid-width <gridWidth>', 'grid width percent')
    .option('--grid-pct <gridPct>', 'grid width percent')
    .option('--grid-count <gridCount>', 'grid count')
    .option('--bollinger-period <bollingerPeriod>', 'bollinger period')
    .option('--std-dev <stdDev>', 'bollinger std dev')
    .option('--macd-fast <macdFast>', 'macd fast period')
    .option('--macd-slow <macdSlow>', 'macd slow period')
    .option('--macd-signal <macdSignal>', 'macd signal period')
    .option('--mean-period <meanPeriod>', 'mean reversion period')
    .option('--deviation-pct <deviationPct>', 'mean reversion deviation percent')
    .action(
      async (options: {
        strategy: string;
        coin: string;
        capital: string;
        startDate?: string;
        endDate?: string;
      } & Record<string, unknown>) => {
        if (!STRATEGIES.includes(options.strategy as StrategyName)) {
          throw new Error(`Invalid strategy: ${options.strategy}`);
        }

        const params = buildStrategyParams(options);

        const result = await runBacktest({
          strategy: options.strategy as StrategyName,
          coin: normalizeCoin(options.coin),
          initial_capital: parseNumber(options.capital, 'capital'),
          start_date: options.startDate,
          end_date: options.endDate,
          params,
        });

        printJson(result);
      },
    );

  program
    .command('optimize')
    .description('Optimize strategy parameters for one coin')
    .requiredOption('--coin <coin>', 'Coin id or alias')
    .option('--capital <capital>', 'Initial capital', '10000')
    .option('--start-date <startDate>', 'YYYY-MM-DD')
    .option('--end-date <endDate>', 'YYYY-MM-DD')
    .option('--top <top>', 'Top ranking count', '10')
    .action(
      async (options: {
        coin: string;
        capital: string;
        startDate?: string;
        endDate?: string;
        top: string;
      }) => {
        const result = await optimizeCoin({
          coin: normalizeCoin(options.coin),
          initial_capital: parseNumber(options.capital, 'capital'),
          start_date: options.startDate,
          end_date: options.endDate,
          top: Math.max(1, Math.floor(parseNumber(options.top, 'top'))),
        });

        printJson(result);
      },
    );

  program
    .command('optimize-all')
    .description('Optimize all strategies for all supported coins')
    .option('--capital <capital>', 'Initial capital', '10000')
    .option('--start-date <startDate>', 'YYYY-MM-DD')
    .option('--end-date <endDate>', 'YYYY-MM-DD')
    .option('--top <top>', 'Top ranking count', '10')
    .action(
      async (options: { capital: string; startDate?: string; endDate?: string; top: string }) => {
        const result = await optimizeAllCoins({
          initial_capital: parseNumber(options.capital, 'capital'),
          start_date: options.startDate,
          end_date: options.endDate,
          top: Math.max(1, Math.floor(parseNumber(options.top, 'top'))),
        });

        printJson(result);
      },
    );

  program
    .command('rankings')
    .description('Show optimization rankings')
    .option('--coin <coin>', 'Coin id or alias')
    .option('--strategy <strategy>', `One of: ${STRATEGIES.join(', ')}`)
    .option('--limit <limit>', 'Ranking limit', '50')
    .action((options: { coin?: string; strategy?: string; limit: string }) => {
      if (options.strategy && !STRATEGIES.includes(options.strategy as StrategyName)) {
        throw new Error(`Invalid strategy: ${options.strategy}`);
      }

      const result = getOptimizationRankings({
        coin: options.coin ? normalizeCoin(options.coin) : undefined,
        strategy: options.strategy as StrategyName | undefined,
        limit: Math.max(1, Math.floor(parseNumber(options.limit, 'limit'))),
      });

      printJson(result);
    });

  program
    .command('compare')
    .description('Compare all strategies')
    .requiredOption('--coin <coin>', 'Coin id or alias')
    .option('--capital <capital>', 'Initial capital', '10000')
    .option('--start-date <startDate>', 'YYYY-MM-DD')
    .option('--end-date <endDate>', 'YYYY-MM-DD')
    .action(
      async (options: { coin: string; capital: string; startDate?: string; endDate?: string }) => {
        const coin = normalizeCoin(options.coin);
        const capital = parseNumber(options.capital, 'capital');

        const results = [];
        for (const strategy of STRATEGIES) {
          const result = await runBacktest({
            strategy,
            coin,
            initial_capital: capital,
            start_date: options.startDate,
            end_date: options.endDate,
          });

          results.push({
            strategy,
            total_return_pct: result.metrics.total_return_pct,
            max_drawdown_pct: result.metrics.max_drawdown_pct,
            sharpe_ratio: result.metrics.sharpe_ratio,
            win_rate_pct: result.metrics.win_rate_pct,
            trade_count: result.metrics.trade_count,
            final_value: result.final_value,
          });
        }

        results.sort((a, b) => b.total_return_pct - a.total_return_pct);
        printJson({ coin, capital, results });
      },
    );

  program
    .command('trade')
    .description('Execute simulated trade')
    .requiredOption('--action <action>', 'buy or sell')
    .requiredOption('--coin <coin>', 'Coin id or alias')
    .option('--amount <amount>', 'Notional amount in JPY')
    .option('--quantity <quantity>', 'Quantity in coin units')
    .option('--initial-capital <initialCapital>', 'Initial simulation cash', '10000')
    .action(
      async (options: {
        action: string;
        coin: string;
        amount?: string;
        quantity?: string;
        initialCapital: string;
      }) => {
        if (options.action !== 'buy' && options.action !== 'sell') {
          throw new Error('action must be buy or sell');
        }

        const result = await executeSimulationTrade(
          {
            action: options.action,
            coin: normalizeCoin(options.coin),
            amount: options.amount !== undefined ? parseNumber(options.amount, 'amount') : undefined,
            quantity:
              options.quantity !== undefined ? parseNumber(options.quantity, 'quantity') : undefined,
          },
          parseNumber(options.initialCapital, 'initial-capital'),
        );

        printJson(result);
      },
    );

  program
    .command('portfolio')
    .description('Show simulated portfolio')
    .option('--initial-capital <initialCapital>', 'Initial simulation cash', '10000')
    .action(async (options: { initialCapital: string }) => {
      const result = await getPortfolioState(parseNumber(options.initialCapital, 'initial-capital'));
      printJson(result);
    });

  program
    .command('history')
    .description('Show simulated trade history')
    .option('--limit <limit>', 'History limit', '100')
    .action((options: { limit: string }) => {
      const limit = Math.max(1, Math.floor(parseNumber(options.limit, 'limit')));
      const rows = getSimulationHistory(limit);
      printJson(rows);
    });

  await program.parseAsync(argv);
}

if (require.main === module) {
  main().catch((error: unknown) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exit(1);
  });
}
