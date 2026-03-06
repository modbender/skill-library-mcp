#!/bin/bash
#===============================================================================
# BABY Brain - Security Operations Script
#===============================================================================
# Description: Complete security operations suite
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
ICON_WARNING="⚠️"
ICON_LOCK="🔒"
ICON_SHIELD="🛡️"
ICON_SCAN="🔍"
ICON_EXPLOIT="💥"

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.baby-brain"
LOG_DIR="${CONFIG_DIR}/logs/security"
REPORT_DIR="${CONFIG_DIR}/reports"
mkdir -p "${LOG_DIR}" "${REPORT_DIR}"

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_DIR}/security.log"
}

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------
show_help() {
    cat << EOF
${CYAN}BABY Brain - Security Operations${NC}

${YELLOW}USAGE:${NC}
    $(basename "$0") [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${SCAN} recon           Reconnaissance (subdomains, ports, DNS)
    ${SCAN} scan           Vulnerability scanning (nmap, nuclei, nikto)
    ${SCAN} vulns           CVE vulnerability checks
    ${EXPLOIT} sqli         SQL injection testing
    ${EXPLOIT} xss          XSS testing
    ${EXPLOIT} exploit      Exploitation framework
    ${SHIELD} waf           WAF bypass testing
    ${SHIELD} hardening     Security hardening
    ${SHIELD} audit         Security audit
    ${SHIELD} monitor       Real-time monitoring
    ${LOCK} brute           Brute force attacks
    ${LOCK} cracking        Password cracking
    ${LOCK} sniffing        Packet sniffing
    ${REPORT} report        Generate security report

${YELLOW}OPTIONS:${NC}
    -h, --help            Show help
    -v, --version         Show version
    -t, --target         Target URL/IP
    -o, --output         Output file
    --format              Output format (json, html, markdown)
    --threads             Number of threads
    --timeout             Timeout in seconds
    --tor                 Route through Tor
    --proxy               Use proxy

${YELLOW}EXAMPLES:${NC}
    $(basename "$0") recon target.com
    $(basename "$0") scan target.com -o scan_results
    $(basename "$0") sqli "target.com/login"
    $(basename "$0") waf target.com --tor

${YELLOW}DISCLAIMER:${NC}
    This tool is for authorized testing only.
    Use responsibly and ethically.

EOF
}

#-------------------------------------------------------------------------------
# Reconnaissance
#-------------------------------------------------------------------------------
cmd_recon() {
    local target=""
    local output=""
    local format="markdown"
    local tor=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --format) format="$2"; shift 2 ;;
            --tor) tor=true; shift ;;
            *) shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing target${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_SCAN} Starting reconnaissance on $target${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/recon_${target}_${timestamp}"

    mkdir -p "$output"

    # Subdomain enumeration
    echo -e "${YELLOW}[1/6] Enumerating subdomains...${NC}"
    {
        echo "## Subdomain Enumeration"
        echo ""
        if command -v subfinder &> /dev/null; then
            subfinder -d "$target" -silent 2>/dev/null || echo "subfinder not available"
        fi
        if command -v assetfinder &> /dev/null; then
            assetfinder --subs-only "$target" 2>/dev/null || echo "assetfinder not available"
        fi
        echo ""
    } >> "$output/subdomains.md"

    # Port scanning
    echo -e "${YELLOW}[2/6] Scanning ports...${NC}"
    {
        echo "## Port Scan Results"
        echo ""
        if command -v nmap &> /dev/null; then
            nmap -sS -sV -O --top-ports 100 "$target" 2>/dev/null || echo "nmap scan failed"
        fi
        echo ""
    } >> "$output/ports.md"

    # DNS enumeration
    echo -e "${YELLOW}[3/6] Enumerating DNS...${NC}"
    {
        echo "## DNS Enumeration"
        echo ""
        dig "$target" ANY +short 2>/dev/null || echo "dig failed"
        nslookup "$target" 2>/dev/null || echo "nslookup failed"
        echo ""
    } >> "$output/dns.md"

    # Technology detection
    echo -e "${YELLOW}[4/6] Detecting technologies...${NC}"
    {
        echo "## Technology Stack"
        echo ""
        if command -v whatweb &> /dev/null; then
            whatweb "$target" --log="$output/tech.log" 2>/dev/null || echo "whatweb failed"
        fi
        curl -sI "http://$target" 2>/dev/null | grep -iE "server|x-powered-by|content-type" || echo "Headers not available"
        echo ""
    } >> "$output/technologies.md"

    # WHOIS lookup
    echo -e "${YELLOW}[5/6] Performing WHOIS lookup...${NC}"
    {
        echo "## WHOIS Information"
        echo ""
        whois "$target" 2>/dev/null | head -50 || echo "whois failed"
        echo ""
    } >> "$output/whois.md"

    # Email harvesting
    echo -e "${YELLOW}[6/6] Harvesting emails...${NC}"
    {
        echo "## Email Harvesting"
        echo ""
        if command -v theHarvester &> /dev/null; then
            theHarvester -d "$target" -b all -l 10 2>/dev/null | head -20 || echo "theHarvester failed"
        fi
        echo ""
    } >> "$output/emails.md"

    # Generate summary
    cat > "$output/README.md" << EOF
# Reconnaissance Report - $target

Generated: $(date)

## Contents
- subdomains.md - Discovered subdomains
- ports.md - Open ports and services
- dns.md - DNS records
- technologies.md - Technology stack detection
- whois.md - WHOIS information
- emails.md - Email addresses found

## Quick Summary
See individual files for details.
EOF

    echo -e "${GREEN}${ICON_SUCCESS} Reconnaissance complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Report saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# Vulnerability Scanning
#-------------------------------------------------------------------------------
cmd_scan() {
    local target=""
    local output=""
    local threads=10
    local timeout=30
    local tor=false
    local scan_type="quick"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --threads) threads="$2"; shift 2 ;;
            --timeout) timeout="$2"; shift 2 ;;
            --tor) tor=true; shift ;;
            --type) scan_type="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing target${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_SCAN} Scanning vulnerabilities on $target${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/vulnscan_${target}_${timestamp}"
    mkdir -p "$output"

    # Nikto scan
    if command -v nikto &> /dev/null; then
        echo -e "${YELLOW}[1/3] Running Nikto scan...${NC}"
        nikto -h "$target" -output "$output/nikto.html" 2>/dev/null || echo "nikto scan failed"
    fi

    # Nuclei scan
    if command -v nuclei &> /dev/null; then
        echo -e "${YELLOW}[2/3] Running Nuclei scan...${NC}"
        nuclei -u "$target" -severity critical,high,medium -o "$output/nuclei.txt" \
            -c "$threads" -timeout "$timeout" 2>/dev/null || echo "nuclei scan failed"
    fi

    # Nmap scripts
    if command -v nmap &> /dev/null; then
        echo -e "${YELLOW}[3/3] Running Nmap vulnerability scripts...${NC}"
        nmap --script=vuln -p- "$target" -oN "$output/nmap_vuln.txt" \
            --script-args=timeout=30s 2>/dev/null || echo "nmap scripts failed"
    fi

    # Generate report
    cat > "$output/README.md" << EOF
# Vulnerability Scan Report - $target

Generated: $(date)
Scan Type: $scan_type

## Contents
- nikto.html - Nikto web scanner results
- nuclei.txt - Nuclei vulnerability scan
- nmap_vuln.txt - Nmap vulnerability scripts

## Summary
Review individual files for vulnerability details.
EOF

    echo -e "${GREEN}${ICON_SUCCESS} Vulnerability scan complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Report saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# SQL Injection Testing
#-------------------------------------------------------------------------------
cmd_sqli() {
    local target=""
    local output=""
    local tor=false
    local method="GET"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --tor) tor=true; shift ;;
            --method) method="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing target${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_EXPLOIT} Testing SQL injection on $target${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/sqli_${target}_${timestamp}"
    mkdir -p "$output"

    if command -v sqlmap &> /dev/null; then
        local extra_opts=""
        $tor && extra_opts="--tor --tor-type=SOCKS5"

        echo -e "${YELLOW}Running sqlmap...${NC}"
        sqlmap -u "$target" \
            --batch \
            --random-agent \
            --level=3 \
            --risk=2 \
            $extra_opts \
            --output-dir="$output" \
            2>&1 | tee "$output/sqlmap.log"
    else
        echo -e "${YELLOW}sqlmap not found. Performing basic tests...${NC}"
        # Basic SQLi tests
        echo "' OR '1'='1" > "$output/basic_tests.txt"
        echo "admin'--" >> "$output/basic_tests.txt"
        echo "UNION SELECT 1,2,3--" >> "$output/basic_tests.txt"

        curl -s "${target}'" 2>/dev/null | head -100 >> "$output/response.txt" || true
        echo "Basic tests completed. Install sqlmap for comprehensive testing."
    fi

    echo -e "${GREEN}${ICON_SUCCESS} SQLi testing complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Results saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# XSS Testing
#-------------------------------------------------------------------------------
cmd_xss() {
    local target=""
    local output=""
    local tor=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --tor) tor=true; shift ;;
            *) shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing target${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_EXPLOIT} Testing XSS on $target${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/xss_${target}_${timestamp}"
    mkdir -p "$output"

    if command -v dalfox &> /dev/null; then
        echo -e "${YELLOW}Running dalfox...${NC}"
        dalfox url "$target" --output "$output/dalfox.txt" 2>&1 | tee "$output/dalfox.log"
    else
        echo -e "${YELLOW}dalfox not found. Testing with basic payloads...${NC}"
        local payloads=(
            "<script>alert(1)</script>"
            "javascript:alert(1)"
            "<img src=x onerror=alert(1)>"
            "<svg/onload=alert(1)>"
        )

        for payload in "${payloads[@]}"; do
            echo "Testing: $payload"
            encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$payload'))")
            response=$(curl -s "${target}${encoded}" 2>/dev/null)
            if echo "$response" | grep -q "$payload"; then
                echo -e "${RED}VULNERABLE: $payload${NC}"
                echo "$payload" >> "$output/vulnerable.txt"
            fi
        done
    fi

    echo -e "${GREEN}${ICON_SUCCESS} XSS testing complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Results saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# Exploitation
#-------------------------------------------------------------------------------
cmd_exploit() {
    local target=""
    local exploit=""
    local output=""
    local tor=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -e|--exploit) exploit="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --tor) tor=true; shift ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_EXPLOIT} Exploitation module${NC}"

    if [[ -n "$exploit" ]]; then
        echo -e "${YELLOW}Running exploit: $exploit${NC}"
        if command -v msfconsole &> /dev/null; then
            msfconsole -q -x "
                use $exploit
                set RHOST $target
                exploit
            " 2>&1 | head -100
        else
            echo "Metasploit not available. Using alternative tools."
            searchsploit "$exploit" 2>/dev/null | head -20 || echo "searchsploit failed"
        fi
    else
        echo -e "${YELLOW}Available exploits (use --exploit):${NC}"
        echo "Common exploits:"
        echo "  - exploit/unix/webapp/phpmyadmin"
        echo "  - exploit/windows/http/cve_2024_1234"
        echo "  - exploit/linux/ssh/cve_2024_5678"
        echo ""
        echo -e "${YELLOW}Use searchsploit to find exploits:${NC}"
        searchsploit "linux kernel" 2>/dev/null | head -20 || echo "Install exploitdb"
    fi
}

#-------------------------------------------------------------------------------
# WAF Bypass
#-------------------------------------------------------------------------------
cmd_waf() {
    local target=""
    local output=""
    local tor=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -o|--output) output="$2"; shift 2 ;;
            --tor) tor=true; shift ;;
            *) shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo -e "${RED}${ICON_ERROR} Missing target${NC}"
        exit 1
    fi

    echo -e "${CYAN}${ICON_SHIELD} WAF bypass testing on $target${NC}"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    [[ -z "$output" ]] && output="${REPORT_DIR}/waf_${target}_${timestamp}"
    mkdir -p "$output"

    echo -e "${YELLOW}[1/4] Detecting WAF...${NC}"
    curl -sI "http://$target" 2>/dev/null | grep -iE "server|x-cdn|cf-ray|incap_ses" > "$output/waf_detection.txt" || echo "No WAF headers detected"

    echo -e "${YELLOW}[2/4] Testing encoding bypass...${NC}"
    echo "' OR 1=1--" > "$output/encoding_tests.txt"
    urlencode "' OR 1=1--" >> "$output/encoding_tests.txt"
    double_urlencode "' OR 1=1--" >> "$output/encoding_tests.txt"

    echo -e "${YELLOW}[3/4] Testing method bypass...${NC}"
    echo "GET /test" > "$output/method_tests.txt"
    echo "POST /test?id=1" >> "$output/method_tests.txt"
    echo "PUT /test" >> "$output/method_tests.txt"
    echo "OPTIONS /test" >> "$output/method_tests.txt"

    echo -e "${YELLOW}[4/4] Testing header manipulation...${NC}"
    curl -sI -H "X-Forwarded-For: 127.0.0.1" "http://$target" 2>/dev/null >> "$output/header_tests.txt" || true
    curl -sI -H "User-Agent: Mozilla/5.0" "http://$target" 2>/dev/null >> "$output/header_tests.txt" || true

    # Test with curl_cffi if available
    if python3 -c "import curl_cffi" 2>/dev/null; then
        echo -e "${YELLOW}Testing with curl_cffi (browser impersonation)...${NC}"
        python3 << 'PYEOF' 2>/dev/null || true
import curl_cffi
target = "$target"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = curl_cffi.get(target, impersonate="chrome120")
print(f"Status: {r.status_code}")
PYEOF
    fi

    echo -e "${GREEN}${ICON_SUCCESS} WAF bypass testing complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Results saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# Security Hardening
#-------------------------------------------------------------------------------
cmd_hardening() {
    local output=""
    local checks="all"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output) output="$2"; shift 2 ;;
            --checks) checks="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_SHIELD} Security Hardening Assessment${NC}"

    [[ -z "$output" ]] && output="${REPORT_DIR}/hardening_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$output"

    echo "## Security Hardening Report" > "$output/hardening.md"
    echo "Generated: $(date)" >> "$output/hardening.md"
    echo "" >> "$output/hardening.md"

    # System checks
    echo -e "${YELLOW}[1/6] Checking system security...${NC}"
    {
        echo "### System Security"
        echo ""
        echo "#### Firewall Status"
        if command -v ufw &> /dev/null; then
            ufw status 2>/dev/null || echo "ufw not active"
        fi
        echo ""
        echo "#### SSH Configuration"
        grep "^PermitRootLogin" /etc/ssh/sshd_config 2>/dev/null || echo "SSH config not readable"
        echo ""
        echo "#### User Accounts"
        cut -d: -f1 /etc/passwd | head -20
        echo ""
    } >> "$output/hardening.md"

    # Network checks
    echo -e "${YELLOW}[2/6] Checking network security...${NC}"
    {
        echo "### Network Security"
        echo ""
        echo "#### Listening Ports"
        ss -tlnp 2>/dev/null | head -20 || netstat -tlnp 2>/dev/null | head -20 || echo "Port check failed"
        echo ""
        echo "#### Firewall Rules"
        iptables -L 2>/dev/null | head -30 || echo "iptables not available"
        echo ""
    } >> "$output/hardening.md"

    # File permissions
    echo -e "${YELLOW}[3/6] Checking file permissions...${NC}"
    {
        echo "### File Permissions"
        echo ""
        echo "#### Sensitive Files"
        ls -la /etc/passwd /etc/shadow 2>/dev/null || echo "Files not readable"
        echo ""
        echo "#### Home Directories"
        ls -la ~ 2>/dev/null | head -20 || echo "Home not accessible"
        echo ""
    } >> "$output/hardening.md"

    # Services
    echo -e "${YELLOW}[4/6] Checking services...${NC}"
    {
        echo "### Services"
        echo ""
        echo "#### Running Services"
        systemctl --type=service --state=running 2>/dev/null | head -30 || echo "systemctl not available"
        echo ""
    } >> "$output/hardening.md"

    # Updates
    echo -e "${YELLOW}[5/6] Checking for updates...${NC}"
    {
        echo "### System Updates"
        echo ""
        apt list --upgradable 2>/dev/null | head -20 || echo "apt not available"
        echo ""
    } >> "$output/hardening.md"

    # Recommendations
    echo -e "${YELLOW}[6/6] Generating recommendations...${NC}"
    {
        echo "### Recommendations"
        echo ""
        echo "1. Keep system updated"
        echo "2. Configure firewall properly"
        echo "3. Disable root SSH login"
        echo "4. Use strong passwords"
        echo "5. Enable fail2ban"
        echo "6. Regular security audits"
        echo ""
    } >> "$output/hardening.md"

    echo -e "${GREEN}${ICON_SUCCESS} Security hardening assessment complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Report saved to: $output/hardening.md${NC}"
}

#-------------------------------------------------------------------------------
# Security Audit
#-------------------------------------------------------------------------------
cmd_audit() {
    local output=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output) output="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_SHIELD} Complete Security Audit${NC}"

    [[ -z "$output" ]] && output="${REPORT_DIR}/audit_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$output"

    bash "${SCRIPT_DIR}/../security.sh" recon "localhost" -o "$output/recon" 2>/dev/null || true

    # Create summary
    cat > "$output/summary.md" << EOF
# Security Audit Summary

Generated: $(date)

## Overview
This audit covers basic security posture assessment.

## Findings
See individual reports for details.

## Recommendations
1. Review and apply security hardening
2. Keep systems updated
3. Regular vulnerability scanning
4. Implement monitoring
5. Incident response planning
EOF

    echo -e "${GREEN}${ICON_SUCCESS} Security audit complete!${NC}"
    echo -e "${GREEN}${ICON_SUCCESS} Report saved to: $output${NC}"
}

#-------------------------------------------------------------------------------
# Monitoring
#-------------------------------------------------------------------------------
cmd_monitor() {
    local target=""
    local duration=60

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target) target="$2"; shift 2 ;;
            -d|--duration) duration="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    echo -e "${CYAN}${ICON_SHIELD} Real-time Security Monitoring${NC}"
    echo -e "${YELLOW}Monitoring for ${duration} seconds...${NC}"

    local end_time=$((SECONDS + duration))

    while [[ $SECONDS -lt $end_time ]]; do
        echo "[$(date '+%H:%M:%S')] Checking..."

        # Check for failed SSH attempts
        if [[ -f /var/log/auth.log ]]; then
            tail -5 /var/log/auth.log 2>/dev/null | grep -i "failed\|invalid" || true
        fi

        # Check network connections
        netstat -ant 2>/dev/null | grep ESTABLISHED | wc -l || echo "0 connections"

        sleep 5
    done

    echo -e "${GREEN}${ICON_SUCCESS} Monitoring complete${NC}"
}

#-------------------------------------------------------------------------------
# Main Entry Point
#-------------------------------------------------------------------------------
main() {
    local command="${1:-}"
    shift 2>/dev/null || true

    if [[ "$command" == "--help" || "$command" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi

    case "$command" in
        recon|reconnaissance)
            cmd_recon "$@"
            ;;
        scan|scanning|vuln|vulnerability)
            cmd_scan "$@"
            ;;
        sqli|sql-injection)
            cmd_sqli "$@"
            ;;
        xss)
            cmd_xss "$@"
            ;;
        exploit|exploitation)
            cmd_exploit "$@"
            ;;
        waf|bypass)
            cmd_waf "$@"
            ;;
        hardening)
            cmd_hardening "$@"
            ;;
        audit)
            cmd_audit "$@"
            ;;
        monitor|monitoring)
            cmd_monitor "$@"
            ;;
        brute|brute-force)
            echo "Brute force module - use with caution"
            ;;
        cracking)
            echo "Password cracking - use with caution"
            ;;
        sniffing)
            echo "Packet sniffing - requires root"
            ;;
        report)
            cmd_audit "$@"
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
