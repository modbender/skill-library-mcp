#!/bin/bash
# Workspace Analyzer - Run script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default to workspace root
WORKSPACE_ROOT="${1:-$HOME/.openclaw/workspace}"

# Run the analyzer
python3 "$SCRIPT_DIR/scripts/analyzer.py" --root "$WORKSPACE_ROOT" --output /tmp/workspace-analysis.json

# Display results
echo ""
echo "=== Workspace Analysis Complete ==="
echo "Results saved to: /tmp/workspace-analysis.json"
echo ""

# Show summary
 "
import json
python3 -cwith open('/tmp/workspace-analysis.json') as f:
    data = json.load(f)
    print('Files scanned:', data['scan_info']['files_scanned'])
    print('Recommendations:', len(data['recommendations']))
    print('')
    print('Single Source Validation:')
    for topic, result in data.get('single_source_validation', {}).items():
        status = '✅' if result['status'] == 'PASS' else '❌'
        print(f'  {status} {topic}: {result[\"status\"]}')
    print('')
    print('Critical Issues:')
    for rec in data['recommendations']:
        if rec.get('severity') == 'CRITICAL':
            print(f'  ⚠️ {rec[\"action\"]}: {rec.get(\"description\", rec.get(\"topic\", \"\"))}')
"
