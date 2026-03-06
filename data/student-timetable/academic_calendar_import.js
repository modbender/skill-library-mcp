const { web_search, web_fetch } = require('./skill_runtime.js');

function normalizeToken(s) {
  return String(s || '').trim();
}

function hostFromUrl(u) {
  try {
    return new URL(u).hostname.toLowerCase();
  } catch {
    return '';
  }
}

function isOfficialSource(country, school, url) {
  const host = hostFromUrl(url);
  if (!host) return { ok: false, reason: 'invalid_url' };

  if (country === 'sg') {
    if (host === 'www.moe.gov.sg' || host.endsWith('.moe.gov.sg')) {
      return { ok: true, reason: 'sg_moe' };
    }
    if (school && host.includes(normalizeToken(school).toLowerCase().replace(/\s+/g, ''))) {
      return { ok: true, reason: 'sg_school_domain_heuristic' };
    }
    return { ok: false, reason: 'sg_not_official' };
  }

  if (country === 'cn') {
    if (host.endsWith('.gov.cn')) {
      return { ok: true, reason: 'cn_gov' };
    }
    if (host.endsWith('.edu.cn')) {
      return { ok: true, reason: 'cn_school_edu' };
    }
    if (school && host.includes(normalizeToken(school).toLowerCase().replace(/\s+/g, ''))) {
      return { ok: true, reason: 'cn_school_domain_heuristic' };
    }
    return { ok: false, reason: 'cn_not_official' };
  }

  return { ok: false, reason: 'country_unsupported' };
}

function extractDateRows(markdown) {
  const lines = String(markdown || '').split(/\r?\n/);
  const out = [];
  const re = /(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\s*(?:to|~|-|至|到)?\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})?/i;
  for (const line of lines) {
    const m = line.match(re);
    if (m) {
      out.push({ line: line.trim(), start: m[1], end: m[2] || m[1] });
    }
  }
  return out.slice(0, 24);
}

async function searchOfficialAcademicCalendar(baseInfo) {
  const country = String(baseInfo.country || '').trim().toLowerCase();
  const city = normalizeToken(baseInfo.city);
  const school = normalizeToken(baseInfo.school);

  const query = [school, city, country, 'academic calendar official'].filter(Boolean).join(' ');
  const searchResp = await web_search({ query, count: 5, search_lang: country === 'cn' ? 'zh' : 'en' });
  const results = Array.isArray(searchResp?.results) ? searchResp.results : [];

  const candidates = [];
  for (const r of results) {
    const url = r.url || r.link;
    const official = isOfficialSource(country, school, url);
    if (!official.ok) continue;

    const fetched = await web_fetch({ url, extractMode: 'markdown', maxChars: 12000 });
    const body = String(fetched?.content || '');
    const rows = extractDateRows(body);
    if (!rows.length) continue;

    candidates.push({
      source_url: url,
      source_reason: official.reason,
      title: r.title || '',
      dated_items_preview: rows.map((row, idx) => ({
        id: `ac-${Date.now()}-${idx + 1}`,
        date: String(row.start).replace(/\//g, '-').replace(/\./g, '-'),
        title: `Academic calendar item ${idx + 1}`,
        notes: row.line,
        source_url: url,
        disclaimer: 'Imported from official calendar source; verify details with school notices before relying.'
      }))
    });
  }

  return { ok: true, query, candidates };
}

module.exports = { searchOfficialAcademicCalendar, isOfficialSource };
