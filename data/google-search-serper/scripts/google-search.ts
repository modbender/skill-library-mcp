import { query, SearchType, SearchParams } from './lib/serper.ts';
import * as fmt from './lib/format.ts';

const TIME_MAP: Record<string, string> = {
  hour: 'qdr:h', day: 'qdr:d', week: 'qdr:w', month: 'qdr:m', year: 'qdr:y',
  h: 'qdr:h', d: 'qdr:d', w: 'qdr:w', m: 'qdr:m', y: 'qdr:y',
};

function parseArgs(args: string[]): { command: string; queryStr: string; flags: Record<string, string> } {
  const command = args[0] || 'search';
  const flags: Record<string, string> = {};
  const positional: string[] = [];

  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      if (key === 'json') { flags.json = 'true'; continue; }
      const val = args[++i] || '';
      flags[key] = val;
    } else {
      positional.push(args[i]);
    }
  }

  return { command, queryStr: positional.join(' '), flags };
}

async function main() {
  const { command, queryStr, flags } = parseArgs(process.argv.slice(2));
  const jsonOut = flags.json === 'true';

  try {
    if (command === 'credits') {
      const data = await query('account');
      if (jsonOut) { console.log(JSON.stringify(data, null, 2)); return; }
      console.log(fmt.formatCredits(data));
      return;
    }

    if (!queryStr && command !== 'credits') {
      console.error(`Usage: google-search <command> "query" [--num N] [--time day] [--country us] [--lang en] [--year 2023] [--json]`);
      console.error('Commands: search, news, images, videos, places, shopping, scholar, patents, suggest, credits');
      process.exit(1);
    }

    const params: SearchParams = { q: queryStr };
    if (flags.num) params.num = parseInt(flags.num);
    if (flags.country) params.gl = flags.country;
    if (flags.lang) params.hl = flags.lang;
    if (flags.time) params.tbs = TIME_MAP[flags.time] || flags.time;
    if (flags.page) params.page = parseInt(flags.page);
    if (flags.year) params.as_ylo = parseInt(flags.year);

    const typeMap: Record<string, SearchType> = {
      search: 'search', news: 'news', images: 'images', videos: 'videos',
      places: 'places', shopping: 'shopping', scholar: 'scholar',
      patents: 'patents', suggest: 'autocomplete',
    };

    const type = typeMap[command];
    if (!type) { console.error(`Unknown command: ${command}`); process.exit(1); }

    const data = await query(type, params);

    if (jsonOut) { console.log(JSON.stringify(data, null, 2)); return; }

    const formatters: Record<string, (d: any, q: string) => string> = {
      search: fmt.formatSearch, news: fmt.formatNews, images: fmt.formatImages,
      videos: fmt.formatVideos, places: fmt.formatPlaces, shopping: fmt.formatShopping,
      scholar: fmt.formatScholar, patents: fmt.formatPatents, suggest: fmt.formatSuggest,
    };

    console.log(formatters[command](data, queryStr));
  } catch (e: any) {
    console.error(`❌ ${e.message}`);
    process.exit(1);
  }
}

main();
