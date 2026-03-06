#!/usr/bin/env python3
"""Hybrid 4-signal memory search with temporal routing, adaptive weighting, and PRF.

Fusion signals: vector similarity + keyword matching + header matching + filepath scoring.
Automatic behaviors: temporal routing, adaptive weighting, pseudo-relevance feedback.

Research results: 0.782 MRR on 68-query test suite (vs ~0.45 vector-only baseline).

Usage:
    python3 search_memory.py "query" [top_n]
"""

import json, math, os, re, sys, urllib.request
from datetime import datetime, timedelta
from collections import Counter

# --- Configuration ---
# Paths default to workspace layout: memory/ relative to script's grandparent.
# Override MEMORY_DIR env var to change.
MEMORY_DIR = os.environ.get('MEMORY_DIR', os.path.join(os.path.dirname(__file__), '..', '..', '..', 'memory'))
VECTORS_FILE = os.path.join(MEMORY_DIR, 'vectors.json')
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/embed')
MODEL = os.environ.get('EMBED_MODEL', 'nomic-embed-text')

# Fusion weights (tuned via 12 research sprints)
VECTOR_WEIGHT = 0.4
KEYWORD_WEIGHT = 0.25
HEADER_WEIGHT = 0.1
FILEPATH_WEIGHT = 0.25
TEMPORAL_BOOST = 3.0

# Adaptive weighting: when keyword overlap is very low, shift to vector-heavy
ADAPTIVE_KW_THRESHOLD = 0.1
ADAPTIVE_VECTOR_WEIGHT = 0.85
ADAPTIVE_KEYWORD_WEIGHT = 0.05
ADAPTIVE_HEADER_WEIGHT = 0.05
ADAPTIVE_FILEPATH_WEIGHT = 0.05

# Pseudo-relevance feedback
PRF_THRESHOLD = 0.45

# --- Stopwords (shared across scoring functions) ---
STOPWORDS = frozenset({
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
    'do', 'does', 'did', 'has', 'have', 'had', 'will', 'would',
    'can', 'could', 'should', 'may', 'might', 'shall', 'must',
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
    'and', 'or', 'not', 'no', 'but', 'if', 'so', 'as', 'than',
    'that', 'this', 'it', 'its', 'my', 'your', 'his', 'her',
    'we', 'they', 'them', 'what', 'when', 'where', 'how', 'who',
    'which', 'why', 'about', 'any', 'all', 'some'
})

# --- Temporal routing ---
MONTH_MAP = {
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
    'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12,
}
DAY_MAP = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
    'friday': 4, 'saturday': 5, 'sunday': 6
}
NUM_WORDS = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7}


def extract_dates(query, ref=None):
    """Extract date references from a query string. Returns list of 'YYYY-MM-DD' strings."""
    if ref is None:
        ref = datetime.now()
    q = query.lower()
    dates = set()

    # ISO dates (2026-02-10)
    for m in re.finditer(r'(\d{4})-(\d{2})-(\d{2})', query):
        dates.add(f'{m.group(1)}-{m.group(2)}-{m.group(3)}')

    # "February 8th", "Feb 8", "February 8, 2026"
    mp = '|'.join(MONTH_MAP.keys())
    for m in re.finditer(rf'({mp})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:\s*,?\s*(\d{{4}}))?', q):
        mo = MONTH_MAP[m.group(1)]
        day = int(m.group(2))
        yr = int(m.group(3)) if m.group(3) else ref.year
        dates.add(f'{yr:04d}-{mo:02d}-{day:02d}')

    # "8th February"
    for m in re.finditer(rf'(\d{{1,2}})(?:st|nd|rd|th)?\s+({mp})(?:\s+(\d{{4}}))?', q):
        day = int(m.group(1))
        mo = MONTH_MAP[m.group(2)]
        yr = int(m.group(3)) if m.group(3) else ref.year
        dates.add(f'{yr:04d}-{mo:02d}-{day:02d}')

    # Relative dates
    if 'today' in q:
        dates.add(ref.strftime('%Y-%m-%d'))
    if 'yesterday' in q:
        dates.add((ref - timedelta(days=1)).strftime('%Y-%m-%d'))
    if 'day before yesterday' in q:
        dates.add((ref - timedelta(days=2)).strftime('%Y-%m-%d'))

    # "N days ago", "two days ago"
    for m in re.finditer(r'(\d+)\s+days?\s+ago', q):
        dates.add((ref - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d'))
    for word, n in NUM_WORDS.items():
        if f'{word} days ago' in q or f'{word} day ago' in q:
            dates.add((ref - timedelta(days=n)).strftime('%Y-%m-%d'))

    if 'last week' in q:
        dates.add((ref - timedelta(days=7)).strftime('%Y-%m-%d'))

    for dn, dnum in DAY_MAP.items():
        if f'last {dn}' in q:
            back = (ref.weekday() - dnum) % 7
            if back == 0:
                back = 7
            dates.add((ref - timedelta(days=back)).strftime('%Y-%m-%d'))

    return list(dates)


def date_file_match(file_path, date_strings):
    """Check if a file path contains any of the extracted date strings."""
    for ds in date_strings:
        if ds in file_path:
            return True
    return False


# --- Embedding ---
def embed(text):
    """Get embedding vector from Ollama."""
    data = json.dumps({'model': MODEL, 'input': [text]}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())['embeddings'][0]


def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# --- Scoring functions ---
def _query_words(text):
    """Extract meaningful query words (lowercase, >2 chars, no stopwords)."""
    return {w for w in re.findall(r'\w+', text.lower()) if len(w) > 2 and w not in STOPWORDS}


def keyword_score(query, text):
    """Fraction of query words found in text."""
    words = _query_words(query)
    if not words:
        return 0.0
    text_lower = text.lower()
    return sum(1 for w in words if w in text_lower) / len(words)


def filepath_score(query, filepath):
    """Fraction of query words found in the file path (with separators normalized)."""
    words = _query_words(query)
    if not words:
        return 0.0
    fp = filepath.lower().replace('-', ' ').replace('_', ' ').replace('/', ' ')
    return sum(1 for w in words if w in fp) / len(words)


def _extract_expansion_terms(top_chunks, query, max_terms=5):
    """Extract key terms from top results for pseudo-relevance feedback."""
    query_words = set(re.findall(r'\w+', query.lower()))
    extra_stops = STOPWORDS | {'also', 'just', 'more', 'other', 'new', 'like', 'then', 'now', 'only', 'very'}
    counts = Counter()
    for chunk in top_chunks[:3]:
        words = re.findall(r'\w+', chunk['text'].lower())
        fp_words = re.findall(r'\w+', chunk['file'].lower().replace('-', ' ').replace('_', ' '))
        for w in words + fp_words:
            if len(w) > 3 and w not in extra_stops and w not in query_words and not w.isdigit():
                counts[w] += 1
    return [t for t, c in counts.most_common(max_terms) if c >= 2]


def _score_chunks(chunks, query, q_vec, date_refs, has_temporal):
    """Score all chunks. Returns sorted list of (final_score, vec_sim, kw_combined, chunk)."""
    raw = []
    for c in chunks:
        if 'embedding' not in c:
            continue
        raw.append((
            cosine_sim(q_vec, c['embedding']),
            keyword_score(query, c['text']),
            keyword_score(query, c.get('header', '')),
            filepath_score(query, c['file']),
            c,
        ))

    best_kw = max((kw for _, kw, _, _, _ in raw), default=0) if raw else 0
    if best_kw < ADAPTIVE_KW_THRESHOLD:
        vw, kw_w, hw, fw = ADAPTIVE_VECTOR_WEIGHT, ADAPTIVE_KEYWORD_WEIGHT, ADAPTIVE_HEADER_WEIGHT, ADAPTIVE_FILEPATH_WEIGHT
        adaptive = True
    else:
        vw, kw_w, hw, fw = VECTOR_WEIGHT, KEYWORD_WEIGHT, HEADER_WEIGHT, FILEPATH_WEIGHT
        adaptive = False

    scored = []
    for vec_sim, kw_sim, header_kw, fp_sim, c in raw:
        final = vw * vec_sim + kw_w * kw_sim + hw * header_kw + fw * fp_sim
        if has_temporal and date_file_match(c['file'], date_refs):
            final *= TEMPORAL_BOOST
        scored.append((final, vec_sim, kw_sim + 0.3 * header_kw, c))

    scored.sort(key=lambda x: -x[0])
    return scored, adaptive


# --- Main ---
def search(query, top_n=5):
    """Run enhanced search. Returns list of (score, vec_sim, kw_score, chunk) tuples."""
    if not os.path.exists(VECTORS_FILE):
        print('No vectors.json found. Run embed_memories.py first.', file=sys.stderr)
        return []

    with open(VECTORS_FILE) as f:
        chunks = json.load(f)

    q_vec = embed(query)
    date_refs = extract_dates(query)
    has_temporal = len(date_refs) > 0

    scored, adaptive = _score_chunks(chunks, query, q_vec, date_refs, has_temporal)

    # Pseudo-relevance feedback
    prf_used = False
    if scored and scored[0][0] < PRF_THRESHOLD and not has_temporal:
        expansion = _extract_expansion_terms([s[3] for s in scored[:3]], query)
        if expansion:
            expanded_vec = embed(query + ' ' + ' '.join(expansion))
            scored2, _ = _score_chunks(chunks, query + ' ' + ' '.join(expansion), expanded_vec, date_refs, has_temporal)
            chunk_best = {}
            for s in scored + scored2:
                key = (s[3]['file'], s[3].get('line', 0))
                if key not in chunk_best or s[0] > chunk_best[key][0]:
                    chunk_best[key] = s
            scored = sorted(chunk_best.values(), key=lambda x: -x[0])
            prf_used = True

    return scored[:top_n], {
        'temporal': date_refs if has_temporal else None,
        'adaptive': adaptive,
        'prf': prf_used,
    }


def main():
    if len(sys.argv) < 2:
        print('Usage: search_memory.py "query" [top_n]')
        sys.exit(1)

    query = sys.argv[1]
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    results, meta = search(query, top_n)

    if meta.get('temporal'):
        print(f'[temporal routing: dates={meta["temporal"]}]')
    if meta.get('adaptive'):
        print(f'[adaptive weighting: low keyword overlap, using vector-heavy weights]')
    if meta.get('prf'):
        print(f'[PRF expansion applied]')

    for final, vec, kw, c in results:
        print(f'\n--- {c["file"]}:{c.get("line", "?")} [{c.get("header", "")}] (score: {final:.3f} v:{vec:.3f} k:{kw:.3f})')
        print(c['text'][:200])


if __name__ == '__main__':
    main()
