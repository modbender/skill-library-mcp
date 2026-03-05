#!/usr/bin/env bash
# DepGuard — Dependency Scanner Module
# Detects package managers, runs audits, parses licenses

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ─── Package manager detection ─────────────────────────────────────────────

detect_package_managers() {
  local dir="$1"
  local managers=()

  [[ -f "$dir/package-lock.json" ]] && managers+=("npm")
  [[ -f "$dir/yarn.lock" ]] && managers+=("yarn")
  [[ -f "$dir/pnpm-lock.yaml" ]] && managers+=("pnpm")
  [[ -f "$dir/package.json" && ${#managers[@]} -eq 0 ]] && managers+=("npm")
  [[ -f "$dir/requirements.txt" || -f "$dir/Pipfile.lock" || -f "$dir/pyproject.toml" ]] && managers+=("pip")
  [[ -f "$dir/Cargo.lock" || -f "$dir/Cargo.toml" ]] && managers+=("cargo")
  [[ -f "$dir/go.sum" || -f "$dir/go.mod" ]] && managers+=("go")
  [[ -f "$dir/composer.lock" || -f "$dir/composer.json" ]] && managers+=("composer")
  [[ -f "$dir/Gemfile.lock" || -f "$dir/Gemfile" ]] && managers+=("bundler")
  [[ -f "$dir/pom.xml" ]] && managers+=("maven")
  [[ -f "$dir/build.gradle" || -f "$dir/build.gradle.kts" ]] && managers+=("gradle")

  printf '%s\n' "${managers[@]}"
}

# ─── Vulnerability scanning ────────────────────────────────────────────────

scan_npm() {
  local dir="$1"
  local output
  output=$(mktemp)

  echo -e "  ${BLUE}●${NC} Scanning npm dependencies..."

  if command -v npm &>/dev/null; then
    (cd "$dir" && npm audit --json 2>/dev/null) > "$output" || true

    # Parse JSON output
    if command -v node &>/dev/null; then
      node -e "
const data = require('$output');
const vulns = data.vulnerabilities || {};
let critical=0, high=0, moderate=0, low=0;
for (const [name, info] of Object.entries(vulns)) {
  const sev = info.severity || 'unknown';
  if (sev === 'critical') critical++;
  else if (sev === 'high') high++;
  else if (sev === 'moderate') moderate++;
  else if (sev === 'low') low++;
  console.log([sev, name, info.range || '*', info.title || 'Unknown vulnerability', info.url || ''].join('\t'));
}
console.error(JSON.stringify({critical, high, moderate, low}));
" 2>"${output}.summary" || true
    else
      # Fallback: just report raw
      if grep -q '"critical"' "$output" 2>/dev/null; then
        echo -e "critical\tnpm\t*\tVulnerabilities found (install node for details)\t"
      fi
    fi
  else
    echo -e "  ${YELLOW}⚠${NC} npm not found — skipping npm audit"
  fi

  cat "$output" 2>/dev/null | grep -P "^\w" || true
  rm -f "$output" "${output}.summary"
}

scan_pip() {
  local dir="$1"
  echo -e "  ${BLUE}●${NC} Scanning Python dependencies..."

  if command -v pip-audit &>/dev/null; then
    (cd "$dir" && pip-audit --format=columns 2>/dev/null) || true
  elif command -v safety &>/dev/null; then
    (cd "$dir" && safety check 2>/dev/null) || true
  elif command -v pip &>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} Install pip-audit for vulnerability scanning: ${CYAN}pip install pip-audit${NC}"
    echo -e "  ${DIM}Checking for outdated packages instead...${NC}"
    (cd "$dir" && pip list --outdated --format=columns 2>/dev/null | head -20) || true
  else
    echo -e "  ${YELLOW}⚠${NC} pip not found — skipping Python audit"
  fi
}

scan_cargo() {
  local dir="$1"
  echo -e "  ${BLUE}●${NC} Scanning Cargo dependencies..."

  if command -v cargo-audit &>/dev/null; then
    (cd "$dir" && cargo audit 2>/dev/null) || true
  elif command -v cargo &>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} Install cargo-audit: ${CYAN}cargo install cargo-audit${NC}"
  else
    echo -e "  ${YELLOW}⚠${NC} cargo not found — skipping Rust audit"
  fi
}

scan_go() {
  local dir="$1"
  echo -e "  ${BLUE}●${NC} Scanning Go dependencies..."

  if command -v govulncheck &>/dev/null; then
    (cd "$dir" && govulncheck ./... 2>/dev/null) || true
  elif command -v go &>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} Install govulncheck: ${CYAN}go install golang.org/x/vuln/cmd/govulncheck@latest${NC}"
  else
    echo -e "  ${YELLOW}⚠${NC} go not found — skipping Go audit"
  fi
}

scan_composer() {
  local dir="$1"
  echo -e "  ${BLUE}●${NC} Scanning Composer dependencies..."

  if command -v composer &>/dev/null; then
    (cd "$dir" && composer audit 2>/dev/null) || true
  else
    echo -e "  ${YELLOW}⚠${NC} composer not found — skipping PHP audit"
  fi
}

scan_bundler() {
  local dir="$1"
  echo -e "  ${BLUE}●${NC} Scanning Bundler dependencies..."

  if command -v bundle &>/dev/null; then
    (cd "$dir" && bundle audit check 2>/dev/null) || \
    (cd "$dir" && bundle exec bundler-audit check 2>/dev/null) || true
  else
    echo -e "  ${YELLOW}⚠${NC} bundle not found — skipping Ruby audit"
  fi
}

# ─── License scanning ──────────────────────────────────────────────────────

scan_npm_licenses() {
  local dir="$1"
  local output
  output=$(mktemp)

  if [[ -f "$dir/package.json" ]] && command -v node &>/dev/null; then
    node -e "
const fs = require('fs');
const path = require('path');
const nmDir = path.join('$dir', 'node_modules');

if (!fs.existsSync(nmDir)) {
  console.error('node_modules not found — run npm install first');
  process.exit(0);
}

const packages = fs.readdirSync(nmDir).filter(d => !d.startsWith('.'));
const results = [];

for (const pkg of packages) {
  try {
    const pkgPath = path.join(nmDir, pkg, 'package.json');
    if (pkg.startsWith('@')) {
      const scoped = fs.readdirSync(path.join(nmDir, pkg));
      for (const sp of scoped) {
        try {
          const spPath = path.join(nmDir, pkg, sp, 'package.json');
          const data = JSON.parse(fs.readFileSync(spPath, 'utf8'));
          const license = data.license || (data.licenses && data.licenses[0] && data.licenses[0].type) || 'UNKNOWN';
          console.log(pkg + '/' + sp + '\t' + (data.version || '?') + '\t' + license);
        } catch(e) {}
      }
    } else {
      const data = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const license = data.license || (data.licenses && data.licenses[0] && data.licenses[0].type) || 'UNKNOWN';
      console.log(pkg + '\t' + (data.version || '?') + '\t' + license);
    }
  } catch(e) {}
}
" 2>/dev/null > "$output" || true
  fi

  cat "$output"
  rm -f "$output"
}

scan_pip_licenses() {
  local dir="$1"

  if command -v pip &>/dev/null; then
    pip show $(pip freeze 2>/dev/null | cut -d= -f1 | head -50) 2>/dev/null | \
      grep -P "^(Name|Version|License):" | \
      paste - - - 2>/dev/null | \
      awk -F'\t' '{
        name=$1; sub(/Name: /, "", name);
        ver=$2; sub(/Version: /, "", ver);
        lic=$3; sub(/License: /, "", lic);
        print name "\t" ver "\t" lic;
      }' || true
  fi
}

# ─── Categorize licenses ───────────────────────────────────────────────────

categorize_license() {
  local license="$1"
  case "$license" in
    MIT|ISC|BSD-2-Clause|BSD-3-Clause|Apache-2.0|Unlicense|0BSD|CC0-1.0|Zlib|BlueOak-1.0.0)
      echo "permissive"
      ;;
    GPL-2.0*|GPL-3.0*|AGPL-*|LGPL-*|MPL-2.0|EUPL-*)
      echo "copyleft"
      ;;
    UNKNOWN|""|UNLICENSED)
      echo "unknown"
      ;;
    *)
      echo "other"
      ;;
  esac
}

# ─── Main scan function ────────────────────────────────────────────────────

do_scan() {
  local dir="${1:-.}"
  local flags="${2:-}"
  local managers
  managers=$(detect_package_managers "$dir")

  if [[ -z "$managers" ]]; then
    echo -e "${YELLOW}[DepGuard]${NC} No package managers detected in ${BOLD}$dir${NC}"
    echo "  Supported: npm, yarn, pnpm, pip, cargo, go, composer, bundler, maven, gradle"
    return 1
  fi

  echo -e "${BOLD}━━━ DepGuard Security Scan ━━━${NC}"
  echo ""
  echo -e "Target: ${BOLD}$dir${NC}"
  echo -e "Package managers: ${CYAN}$(echo "$managers" | tr '\n' ', ' | sed 's/,$//')${NC}"
  echo ""

  # Vulnerability scan
  if [[ "$flags" != "--licenses-only" ]]; then
    echo -e "${BOLD}Vulnerabilities:${NC}"
    echo ""
    while IFS= read -r mgr; do
      case "$mgr" in
        npm|yarn|pnpm) scan_npm "$dir" ;;
        pip) scan_pip "$dir" ;;
        cargo) scan_cargo "$dir" ;;
        go) scan_go "$dir" ;;
        composer) scan_composer "$dir" ;;
        bundler) scan_bundler "$dir" ;;
      esac
    done <<< "$managers"
    echo ""
  fi

  # License scan
  echo -e "${BOLD}Licenses:${NC}"
  echo ""

  local license_data
  license_data=$(mktemp)

  while IFS= read -r mgr; do
    case "$mgr" in
      npm|yarn|pnpm) scan_npm_licenses "$dir" >> "$license_data" ;;
      pip) scan_pip_licenses "$dir" >> "$license_data" ;;
    esac
  done <<< "$managers"

  local permissive=0 copyleft=0 unknown=0 other=0

  while IFS=$'\t' read -r name ver lic; do
    [[ -z "$name" ]] && continue
    local cat
    cat=$(categorize_license "$lic")
    case "$cat" in
      permissive) ((permissive++)) || true ;;
      copyleft)
        ((copyleft++)) || true
        echo -e "  ${YELLOW}⚠${NC} ${BOLD}$name${NC}@$ver — ${YELLOW}$lic${NC} (copyleft)"
        ;;
      unknown)
        ((unknown++)) || true
        echo -e "  ${RED}?${NC} ${BOLD}$name${NC}@$ver — ${RED}UNKNOWN LICENSE${NC}"
        ;;
      other) ((other++)) || true ;;
    esac
  done < "$license_data"

  local total=$((permissive + copyleft + unknown + other))
  echo ""
  echo -e "${BOLD}License Summary:${NC} $total packages scanned"
  echo -e "  ${GREEN}✓ $permissive permissive${NC}  ${YELLOW}⚠ $copyleft copyleft${NC}  ${RED}? $unknown unknown${NC}  $other other"

  rm -f "$license_data"
}

# ─── Report generation ──────────────────────────────────────────────────────

do_report() {
  local dir="${1:-.}"
  local output="$dir/DEPENDENCY-REPORT.md"
  local project_name
  project_name=$(basename "$(cd "$dir" && pwd)")
  local managers
  managers=$(detect_package_managers "$dir")

  {
    echo "# Dependency Health Report: $project_name"
    echo ""
    echo "> Generated by [DepGuard](https://depguard.pages.dev) — $(date +%Y-%m-%d)"
    echo ""
    echo "## Package Managers"
    echo ""
    echo "$managers" | while IFS= read -r mgr; do
      echo "- $mgr"
    done
    echo ""
    echo "## Vulnerability Summary"
    echo ""
    echo "| Severity | Count |"
    echo "|----------|-------|"
    echo "| Critical | <!-- auto-filled by scan --> |"
    echo "| High | <!-- auto-filled by scan --> |"
    echo "| Moderate | <!-- auto-filled by scan --> |"
    echo "| Low | <!-- auto-filled by scan --> |"
    echo ""
    echo "## License Summary"
    echo ""
    echo "| Category | Count | Risk |"
    echo "|----------|-------|------|"
    echo "| Permissive (MIT, Apache, BSD) | <!-- auto --> | Low |"
    echo "| Copyleft (GPL, AGPL) | <!-- auto --> | High |"
    echo "| Unknown | <!-- auto --> | Critical |"
    echo ""
    echo "## Recommendations"
    echo ""
    echo "<!-- Populated by DepGuard scan results -->"
    echo ""
    echo "---"
    echo ""
    echo "*Report generated by [DepGuard](https://depguard.pages.dev). Run \`depguard scan\` for full details.*"

  } > "$output"

  echo -e "${GREEN}[DepGuard]${NC} Report written to ${BOLD}$output${NC}"
}

# ─── Auto-fix (PRO) ────────────────────────────────────────────────────────

do_fix() {
  local dir="${1:-.}"
  local managers
  managers=$(detect_package_managers "$dir")

  echo -e "${BOLD}━━━ DepGuard Auto-Fix ━━━${NC}"
  echo ""

  while IFS= read -r mgr; do
    case "$mgr" in
      npm)
        echo -e "  ${BLUE}●${NC} Running npm audit fix..."
        (cd "$dir" && npm audit fix 2>&1) || true
        ;;
      yarn)
        echo -e "  ${BLUE}●${NC} Running yarn upgrade (vulnerable packages)..."
        (cd "$dir" && yarn upgrade 2>&1 | tail -5) || true
        ;;
      pnpm)
        echo -e "  ${BLUE}●${NC} Running pnpm audit fix..."
        (cd "$dir" && pnpm audit --fix 2>&1) || true
        ;;
      pip)
        echo -e "  ${BLUE}●${NC} Upgrading vulnerable Python packages..."
        if command -v pip-audit &>/dev/null; then
          (cd "$dir" && pip-audit --fix 2>&1) || true
        else
          echo -e "  ${YELLOW}⚠${NC} Install pip-audit for auto-fix: ${CYAN}pip install pip-audit${NC}"
        fi
        ;;
      cargo)
        echo -e "  ${BLUE}●${NC} Updating Cargo dependencies..."
        (cd "$dir" && cargo update 2>&1 | tail -5) || true
        ;;
      *)
        echo -e "  ${YELLOW}⚠${NC} Auto-fix not available for $mgr"
        ;;
    esac
  done <<< "$managers"

  echo ""
  echo -e "${GREEN}[DepGuard]${NC} Auto-fix complete. Run ${BOLD}depguard scan${NC} to verify."
}

# ─── Watch mode (PRO) ──────────────────────────────────────────────────────

do_watch() {
  local dir="${1:-.}"

  echo -e "${BLUE}[DepGuard]${NC} Watching lockfiles in ${BOLD}$dir${NC} for changes..."
  echo -e "${DIM}  Press Ctrl+C to stop${NC}"
  echo ""

  local lockfiles="package-lock.json yarn.lock pnpm-lock.yaml Cargo.lock go.sum composer.lock Gemfile.lock"
  local checksums
  checksums=$(mktemp)

  # Initial checksums
  for lf in $lockfiles; do
    if [[ -f "$dir/$lf" ]]; then
      md5sum "$dir/$lf" 2>/dev/null || md5 -q "$dir/$lf" 2>/dev/null || true
    fi
  done > "$checksums"

  while true; do
    sleep 5
    local new_checksums
    new_checksums=$(mktemp)

    for lf in $lockfiles; do
      if [[ -f "$dir/$lf" ]]; then
        md5sum "$dir/$lf" 2>/dev/null || md5 -q "$dir/$lf" 2>/dev/null || true
      fi
    done > "$new_checksums"

    if ! diff -q "$checksums" "$new_checksums" &>/dev/null; then
      echo -e "${YELLOW}[DepGuard]${NC} Lockfile change detected! Re-scanning..."
      do_scan "$dir"
      cp "$new_checksums" "$checksums"
    fi

    rm -f "$new_checksums"
  done

  rm -f "$checksums"
}
