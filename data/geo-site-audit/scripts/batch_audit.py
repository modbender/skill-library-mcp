#!/usr/bin/env python3
"""
Batch GEO Audit - Audit multiple sites from a file.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import geo_audit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_audit import GEOAuditor, output_markdown


def main():
    parser = argparse.ArgumentParser(description="Batch GEO Site Audits")
    parser.add_argument("input_file", help="File with one domain per line or CSV with 'domain,notes'")
    parser.add_argument("--output-dir", default="./geo-reports", help="Output directory for reports")
    parser.add_argument("--format", choices=["json", "md", "both"], default="both", help="Output format")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--delay", type=float, default=1, help="Delay between sites")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read input file
    sites = []
    with open(args.input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ',' in line:
                domain, *notes = line.split(',', 1)
                sites.append((domain.strip(), notes[0].strip() if notes else ''))
            else:
                sites.append((line, ''))
    
    print(f"Auditing {len(sites)} sites...")
    
    # Audit each site
    all_results = []
    for i, (domain, notes) in enumerate(sites, 1):
        print(f"\n[{i}/{len(sites)}] Auditing {domain}...")
        
        try:
            auditor = GEOAuditor(domain, timeout=args.timeout, delay=args.delay)
            results = auditor.run_full_audit()
            results['notes'] = notes
            all_results.append(results)
            
            # Save individual report
            safe_domain = domain.replace('/', '_').replace(':', '_')
            
            if args.format in ['json', 'both']:
                json_path = output_dir / f"{safe_domain}.json"
                with open(json_path, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"  Saved JSON: {json_path}")
            
            if args.format in ['md', 'both']:
                md_path = output_dir / f"{safe_domain}.md"
                with open(md_path, 'w') as f:
                    f.write(output_markdown(results))
                print(f"  Saved Markdown: {md_path}")
            
            print(f"  Score: {results['score']}/{results['total']} ({results['grade']})")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results.append({
                "site": domain,
                "error": str(e),
                "score": 0,
                "grade": "F"
            })
    
    # Save summary
    summary = {
        "audited_at": all_results[0]['timestamp'] if all_results else None,
        "total_sites": len(sites),
        "successful": len([r for r in all_results if 'error' not in r]),
        "average_score": sum(r.get('score', 0) for r in all_results) / len(all_results) if all_results else 0,
        "sites": all_results
    }
    
    summary_path = output_dir / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Batch audit complete!")
    print(f"Summary saved to: {summary_path}")
    print(f"Average score: {summary['average_score']:.1f}/29")


if __name__ == "__main__":
    main()
