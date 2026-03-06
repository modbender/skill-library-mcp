#!/usr/bin/env node
// Brave AI Answers - uses Brave AI Grounding (chat/completions) endpoint
// Requires: BRAVE_ANSWERS_API_KEY env var

const BASE_URL = 'https://api.search.brave.com/res/v1';

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
      args[key] = val;
    }
  }
  return args;
}

// Parse <citation>...</citation> tags and extract sources
function parseCitations(text) {
  const sources = [];
  const seen = new Set();

  // Extract citation blocks
  const citationRegex = /<citation>([\s\S]*?)<\/citation>/g;
  let match;
  while ((match = citationRegex.exec(text)) !== null) {
    try {
      const citation = JSON.parse(match[1]);
      if (citation.url && !seen.has(citation.url)) {
        seen.add(citation.url);
        sources.push({ url: citation.url, title: citation.title || citation.url, snippet: citation.snippet || '' });
      }
    } catch {
      // ignore malformed citation
    }
  }

  // Strip all XML-like tags from the answer text
  const cleanText = text
    .replace(/<citation>[\s\S]*?<\/citation>/g, '')
    .replace(/<[^>]+>/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  return { cleanText, sources };
}

async function braveAnswers(query, country, enableCitations, enableResearch) {
  const apiKey = process.env.BRAVE_ANSWERS_API_KEY;
  if (!apiKey) {
    console.error('Error: BRAVE_ANSWERS_API_KEY environment variable not set.');
    console.error('Get your key at: https://api-dashboard.search.brave.com');
    process.exit(1);
  }

  const body = {
    model: 'brave',
    messages: [{ role: 'user', content: query }],
    stream: false,
    extra_body: {
      country,
      language: 'en',
      enable_citations: enableCitations,
      enable_research: enableResearch,
    },
  };

  const res = await fetch(`${BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Subscription-Token': apiKey,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errBody = await res.text();
    console.error(`Brave Answers API error ${res.status}: ${errBody}`);
    process.exit(1);
  }

  return res.json();
}

function formatAnswer(data, query) {
  const content = data.choices?.[0]?.message?.content || '';
  if (!content) return 'No answer returned.';

  const { cleanText, sources } = parseCitations(content);
  const lines = [];

  lines.push(`**Query:** ${query}\n`);
  lines.push(cleanText);

  if (sources.length > 0) {
    lines.push('\n**Sources:**');
    sources.forEach((s, i) => {
      lines.push(`${i + 1}. [${s.title}](${s.url})`);
      if (s.snippet) lines.push(`   > ${s.snippet}`);
    });
  }

  // Usage info
  const usage = data.usage;
  if (usage) {
    lines.push(`\n*Tokens: ${usage.total_tokens} (prompt: ${usage.prompt_tokens}, completion: ${usage.completion_tokens})*`);
  }

  return lines.join('\n');
}

async function main() {
  const args = parseArgs(process.argv);

  const query = args.query;
  if (!query) {
    console.error('Usage: brave_answers.js --query "your question" [--country us] [--enable-citations true] [--enable-research false]');
    process.exit(1);
  }

  const country = args.country || 'us';
  const enableCitations = args['enable-citations'] !== 'false';
  const enableResearch = args['enable-research'] === 'true';

  const data = await braveAnswers(query, country, enableCitations, enableResearch);
  console.log(formatAnswer(data, query));
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
