#!/usr/bin/env bash
# DepGuard — SBOM Generation Module (TEAM tier)
# Generates Software Bill of Materials in CycloneDX JSON format

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scanner.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

do_sbom() {
  local dir="${1:-.}"
  local project_name
  project_name=$(basename "$(cd "$dir" && pwd)")
  local output="$dir/sbom.cdx.json"
  local timestamp
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local managers
  managers=$(detect_package_managers "$dir")

  echo -e "${BLUE}[DepGuard]${NC} Generating SBOM for ${BOLD}$project_name${NC}..."

  # Collect all dependencies with licenses
  local deps_file
  deps_file=$(mktemp)

  while IFS= read -r mgr; do
    case "$mgr" in
      npm|yarn|pnpm)
        scan_npm_licenses "$dir" | while IFS=$'\t' read -r name ver lic; do
          [[ -z "$name" ]] && continue
          echo "npm|$name|$ver|$lic"
        done >> "$deps_file"
        ;;
      pip)
        scan_pip_licenses "$dir" | while IFS=$'\t' read -r name ver lic; do
          [[ -z "$name" ]] && continue
          echo "pip|$name|$ver|$lic"
        done >> "$deps_file"
        ;;
    esac
  done <<< "$managers"

  # Generate CycloneDX JSON
  if command -v node &>/dev/null; then
    node -e "
const fs = require('fs');
const deps = fs.readFileSync('$deps_file', 'utf8').trim().split('\n').filter(Boolean);

const components = deps.map(line => {
  const [mgr, name, version, license] = line.split('|');
  const purl = mgr === 'npm'
    ? 'pkg:npm/' + (name.includes('/') ? name : name) + '@' + version
    : 'pkg:pypi/' + name + '@' + version;

  const component = {
    type: 'library',
    name: name,
    version: version || 'unknown',
    purl: purl,
    'bom-ref': purl
  };

  if (license && license !== 'UNKNOWN') {
    component.licenses = [{ license: { id: license } }];
  }

  return component;
});

const sbom = {
  bomFormat: 'CycloneDX',
  specVersion: '1.5',
  serialNumber: 'urn:uuid:' + require('crypto').randomUUID(),
  version: 1,
  metadata: {
    timestamp: '$timestamp',
    tools: [{
      vendor: 'DepGuard',
      name: 'depguard',
      version: '1.0.0'
    }],
    component: {
      type: 'application',
      name: '$project_name',
      'bom-ref': 'pkg:generic/$project_name'
    }
  },
  components: components,
  dependencies: [{
    ref: 'pkg:generic/$project_name',
    dependsOn: components.map(c => c.purl)
  }]
};

fs.writeFileSync('$output', JSON.stringify(sbom, null, 2));
console.log('Components: ' + components.length);
" 2>/dev/null
  else
    # Fallback: generate basic SBOM without node
    local count=0
    {
      echo "{"
      echo "  \"bomFormat\": \"CycloneDX\","
      echo "  \"specVersion\": \"1.5\","
      echo "  \"version\": 1,"
      echo "  \"metadata\": {"
      echo "    \"timestamp\": \"$timestamp\","
      echo "    \"tools\": [{\"vendor\": \"DepGuard\", \"name\": \"depguard\", \"version\": \"1.0.0\"}],"
      echo "    \"component\": {\"type\": \"application\", \"name\": \"$project_name\"}"
      echo "  },"
      echo "  \"components\": ["

      local first=true
      while IFS='|' read -r mgr name ver lic; do
        [[ -z "$name" ]] && continue
        [[ "$first" != "true" ]] && echo ","
        first=false
        echo -n "    {\"type\": \"library\", \"name\": \"$name\", \"version\": \"${ver:-unknown}\""
        if [[ -n "$lic" && "$lic" != "UNKNOWN" ]]; then
          echo -n ", \"licenses\": [{\"license\": {\"id\": \"$lic\"}}]"
        fi
        echo -n "}"
        ((count++)) || true
      done < "$deps_file"

      echo ""
      echo "  ]"
      echo "}"
    } > "$output"
    echo "Components: $count"
  fi

  rm -f "$deps_file"
  echo -e "${GREEN}[DepGuard]${NC} SBOM written to ${BOLD}$output${NC} (CycloneDX 1.5)"
}
