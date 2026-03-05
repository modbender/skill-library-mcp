import { apiPublicPost } from '../lib/api.js';

function parseArgs(): { query: string; filters: Record<string, unknown>; limit: number } {
  const argv = process.argv.slice(2);
  const filters: Record<string, unknown> = {};
  const queryParts: string[] = [];
  let limit = 10;

  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--type' && argv[i + 1]) {
      filters.intent_type = argv[++i];
    } else if (argv[i] === '--category' && argv[i + 1]) {
      filters.category = argv[++i];
    } else if (argv[i] === '--limit' && argv[i + 1]) {
      limit = parseInt(argv[++i], 10);
    } else {
      queryParts.push(argv[i]);
    }
  }

  return { query: queryParts.join(' '), filters, limit };
}

async function main() {
  const { query, filters, limit } = parseArgs();

  if (!query) {
    console.log('Usage: npx tsx scripts/search.ts <query> [--type sell|buy] [--category <cat>] [--limit <n>]');
    process.exit(1);
  }

  const result = await apiPublicPost('/api/search', {
    query,
    filters: Object.keys(filters).length > 0 ? filters : undefined,
    limit,
  });

  if (result.intents.length === 0) {
    console.log('No matching intents found.');
    return;
  }

  console.log(`Found ${result.count} results:\n`);

  for (const intent of result.intents) {
    console.log(`─────────────────────────────────────`);
    console.log(`  Type: ${intent.intent_type.toUpperCase()}`);
    if (intent.agent_nametag) console.log(`  Agent: @${intent.agent_nametag}`);
    console.log(`  Description: ${intent.description}`);
    if (intent.price) console.log(`  Price: ${intent.price} ${intent.currency}`);
    if (intent.category) console.log(`  Category: ${intent.category}`);
    if (intent.location) console.log(`  Location: ${intent.location}`);
    if (intent.contact_handle) console.log(`  Contact: ${intent.contact_method} - ${intent.contact_handle}`);
    console.log(`  Score: ${(intent.score * 100).toFixed(1)}%`);
    console.log(`  ID: ${intent.id}`);
    console.log('');
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
