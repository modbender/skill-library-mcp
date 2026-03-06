#!/usr/bin/env python3
&quot;&quot;&quot;bioRxiv/medRxiv Preprint Search for Latest Drug Research.

Fetches recent preprints - crucial for novel drugs ahead of peer-review.

API: https://api.biorxiv.org (public).

Usage:
    python biorxiv_search.py --query &quot;KRAS inhibitor&quot; --repo biorxiv --max-results 5
&quot;&quot;&quot;

import argparse
import json
import sys
from datetime import datetime
from urllib.parse import quote

try:
    import requests
except ImportError:
    print(json.dumps({&quot;status&quot;: &quot;error&quot;, &quot;error&quot;: &quot;requests not installed&quot;}))
    sys.exit(1)

BASE_URL = &quot;https://api.biorxiv.org&quot;
TIMEOUT = 15


def search_preprints(query: str, repo: str = &quot;biorxiv&quot;, max_results: int = 10, date_range: str = None) -> dict:
    &quot;&quot;&quot;Search bioRxiv or medRxiv.&quot;&quot;&quot;
    params = {
        &quot;query.term&quot;: query,
        &quot;format&quot;: &quot;json&quot;,
        &quot;count&quot;: min(max_results, 50),
    }
    if date_range:
        params[&quot;query.date&quot;] = date_range  # e.g., &quot;2024-01-01/2026-12-31&quot;

    try:
        resp = requests.get(f&quot;{BASE_URL}/search/{repo}/latest/0/50&quot;, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for p in data.get(&quot;collection&quot;, [])[:max_results]:
            paper = {
                &quot;title&quot;: p.get(&quot;title&quot;, &quot;&quot;),
                &quot;authors&quot;: [a.get(&quot;creator&quot;, &quot;&quot;) for a in p.get(&quot;authors&quot;, [])[:5]],
                &quot;date&quot;: p.get(&quot;date&quot;, &quot;&quot;),
                &quot;abstract&quot;: p.get(&quot;text&quot;, &quot;&quot;)[:2000],
                &quot;doi&quot;: p.get(&quot;doi&quot;, &quot;&quot;),
                &quot;doi_url&quot;: f&quot;https://doi.org/{p.get(&#x27;doi&#x27;, &#x27;&#x27;)}&quot;,
                &quot;pdf_url&quot;: f&quot;https://www.biorxiv.org/content/10.1101/{p.get(&#x27;doi&#x27;, &#x27;&#x27;).split(&#x27;.&#x27;)[-1]}.full.pdf&quot;,
                &quot;repo&quot;: repo,
            }
            papers.append(paper)

        return {
            &quot;agent&quot;: &quot;literature&quot;,
            &quot;subagent&quot;: &quot;preprints&quot;,
            &quot;version&quot;: &quot;2.0.0&quot;,
            &quot;source&quot;: f&quot;{repo.capitalize()}Xiv&quot;,
            &quot;query&quot;: query,
            &quot;total_found&quot;: len(data.get(&quot;collection&quot;, [])),
            &quot;returned&quot;: len(papers),
            &quot;papers&quot;: papers,
            &quot;status&quot;: &quot;success&quot; if papers else &quot;no_results&quot;,
        }
    except Exception as e:
        return {
            &quot;agent&quot;: &quot;literature&quot;,
            &quot;version&quot;: &quot;2.0.0&quot;,
            &quot;source&quot;: f&quot;{repo.capitalize()}Xiv&quot;,
            &quot;query&quot;: query,
            &quot;status&quot;: &quot;error&quot;,
            &quot;error&quot;: str(e),
        }


def main():
    parser = argparse.ArgumentParser(description=&quot;bioRxiv/medRxiv Search&quot;)
    parser.add_argument(&quot;--query&quot;, required=True)
    parser.add_argument(&quot;--repo&quot;, choices=[&quot;biorxiv&quot;, &quot;medrxiv&quot;], default=&quot;biorxiv&quot;)
    parser.add_argument(&quot;--max-results&quot;, type=int, default=10)
    args = parser.parse_args()

    result = search_preprints(args.query, args.repo, args.max_results)
    print(json.dumps(result, indent=2))


if __name__ == &quot;__main__&quot;:
    main()
