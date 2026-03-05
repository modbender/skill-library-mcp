/**
 * PMC Harvest API Client
 * Direct NCBI API access - no API key required
 */

const https = require('https');
const zlib = require('zlib');
const { URL } = require('url');

const EUTILS_BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';
const OAI_BASE = 'https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/';

// Rate limiting: NCBI requires 3 requests/second max without API key
const NCBI_DELAY_MS = 400;
let lastRequestTime = 0;

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function rateLimitedGet(url) {
  const now = Date.now();
  const elapsed = now - lastRequestTime;
  if (elapsed < NCBI_DELAY_MS) {
    await sleep(NCBI_DELAY_MS - elapsed);
  }
  lastRequestTime = Date.now();
  return httpGet(url);
}

/**
 * HTTP GET with redirect following and gzip handling
 */
function httpGet(url, redirects = 0) {
  return new Promise((resolve, reject) => {
    if (redirects > 5) {
      reject(new Error('Too many redirects'));
      return;
    }
    
    const parsedUrl = new URL(url);
    const options = {
      hostname: parsedUrl.hostname,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET',
      headers: {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'PMC-Harvest/1.0'
      }
    };
    
    https.get(options, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        const location = res.headers.location;
        const redirectUrl = location.startsWith('http') ? location : new URL(location, parsedUrl.origin).href;
        return httpGet(redirectUrl, redirects + 1).then(resolve).catch(reject);
      }
      
      let stream = res;
      const encoding = res.headers['content-encoding'];
      if (encoding === 'gzip') {
        stream = res.pipe(zlib.createGunzip());
      } else if (encoding === 'deflate') {
        stream = res.pipe(zlib.createInflate());
      }
      
      let data = '';
      stream.on('data', chunk => data += chunk);
      stream.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
      stream.on('error', reject);
    }).on('error', reject);
  });
}

/**
 * Search PMC for articles
 * @param {string} query - Search query (e.g., "J Stroke[journal]")
 * @param {object} options - { year, retmax, retstart }
 */
async function searchPMC(query, options = {}) {
  const { year, retmax = 100, retstart = 0 } = options;
  
  let fullQuery = query;
  if (year) {
    fullQuery += ` AND ${year}[pdat]`;
  }
  
  const params = new URLSearchParams({
    db: 'pmc',
    term: fullQuery,
    retmax,
    retstart,
    retmode: 'json',
    sort: 'pub_date'
  });
  
  const url = `${EUTILS_BASE}/esearch.fcgi?${params}`;
  const data = await rateLimitedGet(url);
  const json = JSON.parse(data);
  
  const count = parseInt(json.esearchresult?.count || 0);
  const ids = json.esearchresult?.idlist || [];
  const pmcids = ids.map(id => `PMC${id}`);
  
  return { count, pmcids, query: fullQuery };
}

/**
 * Get article summaries
 * @param {string[]} pmcids - Array of PMC IDs
 */
async function getSummaries(pmcids) {
  if (pmcids.length === 0) return [];
  
  const batchSize = 200;
  const results = [];
  
  for (let i = 0; i < pmcids.length; i += batchSize) {
    const batch = pmcids.slice(i, i + batchSize);
    const numericIds = batch.map(id => id.replace(/^PMC/i, ''));
    
    const params = new URLSearchParams({
      db: 'pmc',
      id: numericIds.join(','),
      retmode: 'json'
    });
    
    const url = `${EUTILS_BASE}/esummary.fcgi?${params}`;
    const data = await rateLimitedGet(url);
    const json = JSON.parse(data);
    
    const summaries = Object.entries(json.result || {})
      .filter(([key]) => key !== 'uids')
      .map(([uid, article]) => ({
        pmcid: `PMC${uid}`,
        title: article.title,
        authors: article.authors?.map(a => a.name).join(', '),
        journal: article.fulljournalname,
        pubdate: article.pubdate,
        pmid: article.articleids?.find(id => id.idtype === 'pmid')?.value,
        url: `https://pmc.ncbi.nlm.nih.gov/articles/PMC${uid}/`
      }));
    
    results.push(...summaries);
  }
  
  return results;
}

/**
 * Fetch full text from OAI-PMH
 * @param {string} pmcid - PMC ID (e.g., "PMC12345678")
 */
async function fetchFullText(pmcid) {
  const numericId = pmcid.replace(/^PMC/i, '');
  const identifier = `oai:pubmedcentral.nih.gov:${numericId}`;
  
  const params = new URLSearchParams({
    verb: 'GetRecord',
    identifier,
    metadataPrefix: 'pmc'
  });
  
  const url = `${OAI_BASE}?${params}`;
  const xml = await httpGet(url);
  
  if (xml.includes('<error code="cannotDisseminateFormat"')) {
    return { pmcid, available: false, reason: 'restricted' };
  }
  if (xml.includes('<error')) {
    const match = xml.match(/<error[^>]*>(.*?)<\/error>/s);
    return { pmcid, available: false, reason: match?.[1] || 'unknown error' };
  }
  
  return { pmcid, available: true, xml };
}

/**
 * Parse JATS XML to extract content
 */
function parseJATS(xml) {
  const stripTags = (s) => s?.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() || '';
  
  const titleMatch = xml.match(/<article-title[^>]*>(.*?)<\/article-title>/s);
  const abstractMatch = xml.match(/<abstract[^>]*>(.*?)<\/abstract>/s);
  const bodyMatch = xml.match(/<body[^>]*>(.*?)<\/body>/s);
  const keywordMatches = xml.matchAll(/<kwd[^>]*>(.*?)<\/kwd>/gs);
  const articleTypeMatch = xml.match(/<article[^>]*article-type="([^"]+)"/);
  
  return {
    title: stripTags(titleMatch?.[1]),
    abstract: stripTags(abstractMatch?.[1]),
    body: stripTags(bodyMatch?.[1]),
    keywords: [...keywordMatches].map(m => stripTags(m[1])).filter(Boolean),
    articleType: articleTypeMatch?.[1] || 'research'
  };
}

/**
 * Fetch abstract only (lightweight)
 */
async function fetchAbstract(pmcid) {
  const result = await fetchFullText(pmcid);
  
  if (!result.available) {
    return { pmcid, error: result.reason };
  }
  
  const parsed = parseJATS(result.xml);
  return {
    pmcid,
    title: parsed.title,
    abstract: parsed.abstract,
    articleType: parsed.articleType,
    keywords: parsed.keywords
  };
}

/**
 * Batch harvest from multiple journals
 */
async function harvestJournals(journals, options = {}) {
  const { year } = options;
  const allArticles = [];
  
  for (const journal of journals) {
    const { count, pmcids } = await searchPMC(journal.query, { year, retmax: 500 });
    
    if (pmcids.length > 0) {
      const summaries = await getSummaries(pmcids);
      summaries.forEach(s => {
        allArticles.push({ ...s, journalKey: journal.name });
      });
    }
    
    await sleep(NCBI_DELAY_MS * 2);
  }
  
  return allArticles;
}

module.exports = {
  searchPMC,
  getSummaries,
  fetchFullText,
  fetchAbstract,
  parseJATS,
  harvestJournals,
  httpGet
};
