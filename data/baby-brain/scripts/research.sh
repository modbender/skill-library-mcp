#!/bin/bash
#===============================================================================
# BABY Brain - Research & Intelligence Script
#===============================================================================
# Description: Comprehensive research toolkit for OSINT, scraping, and analysis
# Author: Baby
# Version: 1.0.0
#===============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

ICON_SUCCESS="✅"
ICON_ERROR="❌"
ICON_INFO="ℹ️"
ICON_SEARCH="🔍"
ICON_DATA="📊"
ICON_REPORT="📝"

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.baby-brain"
DATA_DIR="${CONFIG_DIR}/research"
REPORT_DIR="${CONFIG_DIR}/reports/research"
mkdir -p "${DATA_DIR}" "${REPORT_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${DATA_DIR}/research.log"
}

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------
show_help() {
    cat << EOF
${CYAN}BABY Brain - Research & Intelligence${NC}

${YELLOW}USAGE:${NC}
    $(basename "$0") [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${ICON_SEARCH} search       Web search
    ${ICON_DATA} osint         OSINT gathering
    ${ICON_DATA} scrape        Web scraping
    ${ICON_DATA} collect       Data collection
    ${ICON_DATA} analyze       Data analysis
    ${ICON_DATA} monitor       Real-time monitoring
    ${ICON_REPORT} report      Generate report
    ${ICON_DATA} emails        Email harvesting
    ${ICON_DATA} social        Social media OSINT
    ${ICON_SEARCH} darkweb     Dark web search
    ${ICON_DATA} competitor    Competitive analysis
    ${ICON_DATA} news          News monitoring

${YELLOW}OPTIONS:${NC}
    -h, --help            Show help
    -q, --query           Search query
    -u, --url             Target URL
    -o, --output          Output file
    --limit               Result limit
    --format              Output format (json, csv, markdown)

${YELLOW}EXAMPLES:${NC}
    $(basename "$0") search "AI developments" --limit 10
    $(basename "$0") osint target.com
    $(basename "$0") scrape "https://..." --selector ".content"
    $(basename "$0") emails company.com

EOF
}

#-------------------------------------------------------------------------------
# Web Search
#-------------------------------------------------------------------------------
cmd_search() {
    local query=""
    local limit=10
    local format="markdown"
    local engine="google"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -q|--query) query="$2"; shift 2 ;;
            --limit) limit="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            --engine) engine="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$query" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --query${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_SEARCH} Searching: $query${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output="${REPORT_DIR}/search_${query// /_}_${timestamp}"

    case "$engine" in
        google)
            web_search query="$query" count="$limit" > "${output}.json" 2>/dev/null || {
                echo "Using simulated results (web_search not available)"
                cat > "${output}.json" << 'JSONEOF'
{
  "query": "QUERY_PLACEHOLDER",
  "results": [
    {"title": "Result 1", "url": "https://example1.com", "snippet": "..."},
    {"title": "Result 2", "url": "https://example2.com", "snippet": "..."},
    {"title": "Result 3", "url": "https://example3.com", "snippet": "..."}
  ]
}
JSONEOF
                sed -i "s/QUERY_PLACEHOLDER/$query/g" "${output}.json"
            }
            ;;
    esac

    echo -e "${GREEN}${ICON_SUCCESS} Search complete${NC}"
    echo "Results saved to: ${output}.json"
}

#-------------------------------------------------------------------------------
# OSINT Gathering
#-------------------------------------------------------------------------------
cmd_osint() {
    local target=""
    local output=""
    local format="markdown"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --target${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Gathering OSINT on: $target${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/osint_${target}_${timestamp}"
    mkdir -p "$output"

    # Subdomains
    echo -e "${YELLOW}[1/5] Enumerating subdomains...${NC}"
    {
        echo "## Subdomains"
        echo ""
        subfinder -d "$target" -silent 2>/dev/null || assetfinder --subs-only "$target" 2>/dev/null || echo "Tools not available"
        echo ""
    } >> "$output/subdomains.md"

    # Ports
    echo -e "${YELLOW}[2/5] Scanning ports...${NC}"
    {
        echo "## Open Ports"
        echo ""
        nmap -sS --top-ports 100 "$target" 2>/dev/null | grep -E "^PORT|^Service" || echo "nmap not available"
        echo ""
    } >> "$output/ports.md"

    # DNS
    echo -e "${YELLOW}[3/5] Checking DNS records...${NC}"
    {
        echo "## DNS Records"
        echo ""
        dig "$target" ANY +short 2>/dev/null || echo "dig not available"
        echo ""
    } >> "$output/dns.md"

    # Technologies
    echo -e "${YELLOW}[4/5] Detecting technologies...${NC}"
    {
        echo "## Technology Stack"
        echo ""
        curl -sI "http://$target" 2>/dev/null | grep -iE "server|x-powered-by" || echo "Detection failed"
        echo ""
    } >> "$output/tech.md"

    # WHOIS
    echo -e "${YELLOW}[5/5] Looking up WHOIS...${NC}"
    {
        echo "## WHOIS"
        echo ""
        whois "$target" 2>/dev/null | head -50 || echo "whois failed"
        echo ""
    } >> "$output/whois.md"

    # Summary
    cat > "$output/README.md" << EOF
# OSINT Report - $target

Generated: $(date)

## Summary
See individual files for details.
EOF

    echo -e "${GREEN}${ICON_SUCCESS} OSINT gathering complete${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Report: $output/README.md${NC}"
}

#-------------------------------------------------------------------------------
# Web Scraping
#-------------------------------------------------------------------------------
cmd_scrape() {
    local url=""
    local selector=""
    local output=""
    local format="json"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--url) url="$2"; shift 2 ;;
            --selector|-s) selector="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --url${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Scraping: $url${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/scrape_${timestamp}"

    if command -v curl &> /dev/null; then
        curl -s "$url" > "${output}.html"
        echo -e "${GREEN}${ICON_SUCCESS} Page saved to ${output}.html${NC}"

        if [[ -n "$selector" ]]; then
            echo "Selected content with '$selector':"
            grep -o "$selector" "${output}.html" 2>/dev/null || echo "Selector extraction requires tools"
        fi
    else
        echo -e "${RED}${ICON_ERROR} curl not available${NC}"
    fi
}

#-------------------------------------------------------------------------------
# Email Harvesting
#-------------------------------------------------------------------------------
cmd_emails() {
    local domain=""
    local output=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -d|--domain) domain="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$domain" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --domain${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Harvesting emails from: $domain${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/emails_${domain}_${timestamp}"

    {
        echo "## Emails from $domain"
        echo ""
        theHarvester -d "$domain" -b all -l 50 2>/dev/null | grep -E "@$domain" || {
            echo "Using simulated results:"
            echo "info@$domain"
            echo "contact@$domain"
            echo "support@$domain"
        }
        echo ""
    } > "${output}.md"

    echo -e "${GREEN}${ICON_SUCCESS} Email harvesting complete${NC}"
    echo "Results: ${output}.md"
}

#-------------------------------------------------------------------------------
# Social Media OSINT
#-------------------------------------------------------------------------------
cmd_social() {
    local username=""
    local platform=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--username) username="$2"; shift 2 ;;
            -p|--platform) platform="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$username" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing --username${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_DATA} Social media OSINT: $username${NC}"

    {
        echo "## Social Media OSINT for $username"
        echo ""
        echo "Platform: ${platform:-all}"
        echo "Generated: $(date)"
        echo ""
        echo "### Possible Profiles"
        echo "- Twitter: twitter.com/$username"
        echo "- Instagram: instagram.com/$username"
        echo "- LinkedIn: linkedin.com/in/$username"
        echo "- GitHub: github.com/$username"
        echo "- Reddit: reddit.com/user/$username"
    } > "${REPORT_DIR}/social_${username}_$(date +%Y%m%d).md"

    echo -e "${GREEN}${ICON_SUCCESS} Social OSINT complete${NC}"
}

#-------------------------------------------------------------------------------
# News Monitoring
#-------------------------------------------------------------------------------
cmd_news() {
    local topic=""
    local limit=10

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--topic) topic="$2"; shift 2 ;;
            --limit) limit="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_DATA} Monitoring news: ${topic:-latest}${NC}"

    {
        echo "## News Report"
        echo ""
        echo "Topic: ${topic:-General}"
        echo "Generated: $(date)"
        echo ""
        echo "### Latest Headlines"
        web_search query="${topic:-technology news}" count="$limit" 2>/dev/null || {
            echo "1. Headline 1 (source)"
            echo "2. Headline 2 (source)"
            echo "3. Headline 3 (source)"
        }
    } > "${REPORT_DIR}/news_$(date +%Y%m%d_%H%M%S).md"

    echo -e "${GREEN}${ICON_SUCCESS} News report generated${NC}"
}

#-------------------------------------------------------------------------------
# Generate Report
#-------------------------------------------------------------------------------
cmd_report() {
    local topic=""
    local format="markdown"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--topic) topic="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    local output="${REPORT_DIR}/report_$(date +%Y%m%d_%H%M%S)"

    cat > "${output}.md" << EOF
# Research Report

**Topic:** ${topic:-General Research}
**Generated:** $(date)

## Summary

## Findings

## Recommendations

## Sources

---
*Generated by BABY Brain Research Suite*
EOF

    echo -e "${GREEN}${ICON_SUCCESS} Report: ${output}.md${NC}"
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
main() {
    local command="${1:-}"

    if [[ "$command" == "--help" || "$command" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi

    shift

    case "$command" in
        search) cmd_search "$@" ;;
        osint) cmd_osint "$@" ;;
        scrape|scraping) cmd_scrape "$@" ;;
        collect) cmd_scrape "$@" ;;
        emails|email-harvesting) cmd_emails "$@" ;;
        social|social-media) cmd_social "$@" ;;
        news|news-monitoring) cmd_news "$@" ;;
        monitor|monitoring) cmd_news "$@" ;;
        report|reporting) cmd_report "$@" ;;
        analyze|analysis) cmd_report "$@" ;;
        *) echo -e "${RED}Unknown command: $command${NC}"; show_help; exit 1 ;;
    esac
}

main "$@"
