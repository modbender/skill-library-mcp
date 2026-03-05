#!/usr/bin/env python3
&quot;&quot;&quot;Chain Entry Point for Literature Agent v2.0.0 - Novel Drug Focus.

Fuses PubMed, Semantic Scholar, ClinicalTrials.gov, bioRxiv.
Novelty scoring, auto-query boosts for phase/FDA/novel.

Usage same as v1.
&quot;&quot;&quot;

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pubmed_search import search_and_fetch as pubmed_search
from semantic_scholar import search_papers as s2_search, get_paper, get_related, get_citations
from clinicaltrials_search import search_trials as clinical_search
from biorxiv_search import search_preprints as preprint_search


def build_query(input_data: dict) -> str:
    parts = []

    if input_data.get(&quot;query&quot;):
        query = input_data[&quot;query&quot;]
    else:
        if input_data.get(&quot;compound&quot;) or input_data.get(&quot;name&quot;):
            parts.append(input_data.get(&quot;compound&quot;) or input_data.get(&quot;name&quot;))
        if input_data.get(&quot;target&quot;):
            parts.append(input_data[&quot;target&quot;])
        if input_data.get(&quot;disease&quot;):
            parts.append(input_data[&quot;disease&quot;])
        if input_data.get(&quot;mechanism&quot;):
            parts.append(input_data[&quot;mechanism&quot;])
        if input_data.get(&quot;reaction&quot;):
            parts.append(input_data[&quot;reaction&quot;] + &quot; catalyst&quot;)
        if input_data.get(&quot;topic&quot;):
            parts.append(input_data[&quot;topic&quot;])
        query = &quot; &quot;.join(parts)

    # Novel drug boosts
    novel_boost = &quot; (novel OR \&quot;first-in-class\&quot; OR \&quot;phase II\&quot; OR \&quot;phase III\&quot; OR \&quot;FDA approved\&quot;)&quot;
    if input_data.get(&quot;focus&quot;) == &quot;novel&quot; or any(word in query.lower() for word in [&quot;novel&quot;, &quot;latest&quot;, &quot;new drug&quot;]):
        query += novel_boost

    return query.strip()


def calculate_novelty(p: dict, current_year: int = 2026) -> float:
    year = int(p.get(&quot;year&quot;, 1900) or p.get(&quot;date&quot;, &quot;&quot;)[:4] or 1900)
    recency = max(0, (current_year - year) / 5.0)
    recency_score = 10 * (1 - recency / 10)  # Favor recent
    cites = p.get(&quot;citation_count&quot;, p.get(&quot;influential_citations&quot;, 0))
    age = max(1, current_year - year)
    velocity_score = min(50, (cites / age) * 10)
    text = (p.get(&quot;title&quot;, &quot;&quot;) + &quot; &quot; + p.get(&quot;abstract&quot;, &quot;&quot;)).lower()
    keyword_boost = 20 if any(word in text for word in [&quot;phase ii&quot;, &quot;phase iii&quot;, &quot;fda&quot;, &quot;novel&quot;, &quot;first-in-class&quot;]) else 0
    trial_boost = 20 if p.get(&quot;nct&quot;) else 0
    preprint_boost = 10 if p.get(&quot;repo&quot;) else 0
    return recency_score + velocity_score + keyword_boost + trial_boost + preprint_boost


def deduplicate(all_papers: list) -> list:
    seen = set()
    merged = []
    for p in all_papers:
        key = (p.get(&quot;doi&quot;, &quot;&quot;).lower(), p.get(&quot;pmid&quot;, &quot;&quot;), p.get(&quot;nct&quot;, &quot;&quot;), p.get(&quot;title&quot;, &quot;&quot;)[:80].lower())
        tkey = key[-1]
        if any(tkey in s for s in seen):
            continue
        seen.add(tkey)
        merged.append(p)
    return merged


def chain_run(input_data: dict) -> dict:
    context = input_data.get(&quot;context&quot;, &quot;user&quot;)
    max_results = input_data.get(&quot;max_results&quot;, 10)
    years = input_data.get(&quot;years&quot;, 3)  # Default recency

    # Specific lookups
    if input_data.get(&quot;doi&quot;):
        return get_paper(f&quot;DOI:{input_data[&#x27;doi&#x27;]}&quot;)
    if input_data.get(&quot;pmid&quot;):
        return get_paper(f&quot;PMID:{input_data[&#x27;pmid&#x27;]}&quot;)

    query = build_query(input_data)
    if not query:
        return {&quot;agent&quot;: &quot;literature&quot;, &quot;version&quot;: &quot;2.0.0&quot;, &quot;status&quot;: &quot;error&quot;, &quot;error&quot;: &quot;No query.&quot;}

    # Multi-source search
    pubmed_res = pubmed_search(query, max_results//2, &quot;relevance&quot;, years)
    s2_res = s2_search(query, max_results//2)
    trials_res = clinical_search(query, max_results//4, &quot;2,3,4&quot;)
    preprints_res = preprint_search(query, &quot;biorxiv&quot;, max_results//4)

    all_papers = (pubmed_res.get(&quot;papers&quot;, []) + 
                  s2_res.get(&quot;papers&quot;, []) + 
                  trials_res.get(&quot;trials&quot;, []) + 
                  preprints_res.get(&quot;papers&quot;, []))

    merged = deduplicate(all_papers)

    # Novelty scoring & sort
    for p in merged:
        p[&quot;novelty_score&quot;] = calculate_novelty(p)
    merged.sort(key=lambda p: p[&quot;novelty_score&quot;], reverse=True)
    merged = merged[:max_results]

    # Recs
    recommend_next = [&quot;pharmacology&quot;, &quot;chemistry-query&quot;]
    if any(p.get(&quot;nct&quot;) for p in merged):
        recommend_next.append(&quot;market-intel&quot;)
    if any(&quot;patent&quot; in p.get(&quot;title&quot;, &quot;&quot;).lower() for p in merged):
        recommend_next.append(&quot;ip-expansion&quot;)

    return {
        &quot;agent&quot;: &quot;literature&quot;,
        &quot;version&quot;: &quot;2.0.0&quot;,
        &quot;context&quot;: context,
        &quot;query&quot;: query,
        &quot;status&quot;: &quot;success&quot;,
        &quot;pubmed_total&quot;: pubmed_res.get(&quot;total_found&quot;, 0),
        &quot;s2_total&quot;: s2_res.get(&quot;total_found&quot;, 0),
        &quot;trials_total&quot;: trials_res.get(&quot;total_found&quot;, 0),
        &quot;preprints_total&quot;: preprints_res.get(&quot;total_found&quot;, 0),
        &quot;returned&quot;: len(merged),
        &quot;papers&quot;: merged,
        &quot;recommend_next&quot;: list(set(recommend_next)),
        &quot;timestamp&quot;: datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description=&quot;Literature Agent v2 Chain Entry&quot;)
    parser.add_argument(&quot;--input-json&quot;, required=True)
    args = parser.parse_args()

    try:
        input_data = json.loads(args.input_json)
    except json.JSONDecodeError as e:
        print(json.dumps({&quot;agent&quot;: &quot;literature&quot;, &quot;status&quot;: &quot;error&quot;, &quot;error&quot;: str(e)}))
        sys.exit(1)

    result = chain_run(input_data)
    print(json.dumps(result, indent=2))


if __name__ == &quot;__main__&quot;:
    main()
