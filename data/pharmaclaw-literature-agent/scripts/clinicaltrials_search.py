#!/usr/bin/env python3
\"\"\"ClinicalTrials.gov Search for Novel Drugs.

Fetches ongoing/late-phase trials for compounds, targets, diseases. Key for novel drugs.

API: https://clinicaltrials.gov/data-api/v2/studies (public JSON).

Usage:
    python clinicaltrials_search.py --query \\\"KRAS lung cancer\\\"
    python clinicaltrials_search.py --query \\\"sotorasib\\\" --filter-phase \\\"2,3\\\"
\"\"\"

import argparse
import json
import sys
from urllib.parse import quote_plus

try:
    import requests
except ImportError:
    print(json.dumps({&quot;status&quot;: &quot;error&quot;, &quot;error&quot;: &quot;requests not installed&quot;}))
    sys.exit(1)

BASE_URL = &quot;https://clinicaltrials.gov/api/v2/studies&quot;
TIMEOUT = 15


def search_trials(query: str, max_results: int = 10, phase_filter: str = None, status_filter: str = None) -> dict:
    params = {
        &quot;query.cond&quot;: query,
        &quot;limit&quot;: min(max_results * 2, 100),  # Overfetch for filtering
        &quot;format&quot;: &quot;json&quot;,
    }
    if phase_filter:
        params[&quot;filter.phase&quot;] = phase_filter
    if status_filter:
        params[&quot;filter.overallStatus&quot;] = status_filter

    try:
        resp = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        trials = []
        for study in data.get(&quot;studies&quot;, [])[:max_results]:
            trial = {
                &quot;nct&quot;: study.get(&quot;nctId&quot;, &quot;&quot;),
                &quot;title&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;statusSection&quot;, {}).get(&quot;briefTitle&quot;, &quot;&quot;),
                &quot;conditions&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;diseasesSection&quot;, {}).get(&quot;conditions&quot;, []),
                &quot;interventions&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;interventionsSection&quot;, {}).get(&quot;interventionNames&quot;, []),
                &quot;phase&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;designSection&quot;, {}).get(&quot;phaseCode&quot;, &quot;&quot;).title(),
                &quot;status&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;statusSection&quot;, {}).get(&quot;overallStatus&quot;, &quot;&quot;),
                &quot;sponsors&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;sponsorsSection&quot;, {}).get(&quot;leadSponsor&quot;, {}).get(&quot;name&quot;, &quot;&quot;),
                &quot;start_date&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;statusSection&quot;, {}).get(&quot;initiationDateStruct&quot;, {}).get(&quot;firstPostDateStruct&quot;, {}).get(&quot;date&quot;, &quot;&quot;),
                &quot;completion_date&quot;: study.get(&quot;protocolSection&quot;, {}).get(&quot;statusSection&quot;, {}).get(&quot;completionDateStruct&quot;, {}).get(&quot;date&quot;, &quot;&quot;),
                &quot;nct_url&quot;: f&quot;https://clinicaltrials.gov/study/{study.get(&#x27;nctId&#x27;, &#x27;&#x27;)}&quot;,
            }
            trials.append(trial)

        return {
            &quot;agent&quot;: &quot;literature&quot;,
            &quot;subagent&quot;: &quot;clinicaltrials&quot;,
            &quot;version&quot;: &quot;2.0.0&quot;,
            &quot;source&quot;: &quot;clinicaltrials.gov&quot;,
            &quot;query&quot;: query,
            &quot;total_found&quot;: len(data.get(&quot;studies&quot;, [])),
            &quot;returned&quot;: len(trials),
            &quot;trials&quot;: trials,
            &quot;status&quot;: &quot;success&quot; if trials else &quot;no_results&quot;,
        }
    except Exception as e:
        return {
            &quot;agent&quot;: &quot;literature&quot;,
            &quot;version&quot;: &quot;2.0.0&quot;,
            &quot;source&quot;: &quot;clinicaltrials.gov&quot;,
            &quot;query&quot;: query,
            &quot;status&quot;: &quot;error&quot;,
            &quot;error&quot;: str(e),
        }


def main():
    parser = argparse.ArgumentParser(description=&quot;ClinicalTrials.gov Search&quot;)
    parser.add_argument(&quot;--query&quot;, required=True, help=&quot;Search query (condition or drug)&quot;)
    parser.add_argument(&quot;--max-results&quot;, type=int, default=10)
    parser.add_argument(&quot;--filter-phase&quot;, help=&quot;Phases, e.g. &#x27;2,3&#x27;&quot;)
    parser.add_argument(&quot;--filter-status&quot;, help=&quot;Status, e.g. &#x27;RECRUITING,ACTIVE&#x27;&quot;)
    args = parser.parse_args()

    result = search_trials(args.query, args.max_results, args.filter_phase, args.filter_status)
    print(json.dumps(result, indent=2))


if __name__ == &quot;__main__&quot;:
    main()
