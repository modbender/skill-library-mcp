#!/usr/bin/env bash
# test_security.sh — Verify shell injection protections work correctly
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the common library (or proxybase.sh's embedded version)
source "$SCRIPT_DIR/proxybase.sh" help 2>/dev/null || true

# Source functions directly
source "$SCRIPT_DIR/lib/common.sh"

PASS=0
FAIL=0

assert_pass() {
    local DESC="$1"
    shift
    if "$@" 2>/dev/null; then
        echo "  ✅ PASS: $DESC"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL: $DESC (expected pass, got fail)"
        FAIL=$((FAIL + 1))
    fi
}

assert_fail() {
    local DESC="$1"
    shift
    if "$@" 2>/dev/null; then
        echo "  ❌ FAIL: $DESC (expected fail, got pass)"
        FAIL=$((FAIL + 1))
    else
        echo "  ✅ PASS: $DESC"
        PASS=$((PASS + 1))
    fi
}

echo "==========================================="
echo "  ProxyBase Security Test Suite"
echo "==========================================="
echo ""

# ─── Test validate_safe_string ────────────────────────────────────────
echo "── validate_safe_string tests ──"

# Valid usernames
assert_pass "valid username: pb_user123" validate_safe_string "pb_user123" "username"
assert_pass "valid username: user.name" validate_safe_string "user.name" "username"
assert_pass "valid username: user-name" validate_safe_string "user-name" "username"

# Invalid usernames (shell injection attempts)
assert_fail "reject username with \$(...)" validate_safe_string 'pb_$(whoami)' "username"
assert_fail "reject username with backtick" validate_safe_string 'pb_`id`' "username"
assert_fail "reject username with semicolon" validate_safe_string 'pb_user;rm -rf /' "username"
assert_fail "reject username with pipe" validate_safe_string 'user|cat /etc/passwd' "username"
assert_fail "reject username with ampersand" validate_safe_string 'user&echo pwned' "username"
assert_fail "reject username with quote" validate_safe_string "user'quote" "username"
assert_fail "reject username with double quote" validate_safe_string 'user"quote' "username"
assert_fail "reject username with space" validate_safe_string 'user name' "username"
assert_fail "reject username with newline" validate_safe_string $'user\nname' "username"

# Valid passwords
assert_pass "valid password: abc123" validate_safe_string "abc123" "password"
assert_pass "valid password: Pass.word!123" validate_safe_string "Pass.word!123" "password"
assert_pass "valid password: complex*pass+ok" validate_safe_string "complex*pass+ok" "password"

# Invalid passwords (shell injection attempts)
assert_fail "reject password with \$(...)" validate_safe_string '$(rm -rf /)' "password"
assert_fail "reject password with backtick" validate_safe_string '`whoami`' "password"
assert_fail "reject password with semicolon" validate_safe_string 'pass;echo pwned' "password"
assert_fail "reject password with pipe" validate_safe_string 'pass|cat /etc/shadow' "password"
assert_fail "reject password with backslash" validate_safe_string 'pass\ninjection' "password"
assert_fail "reject password with single quote" validate_safe_string "pass'injection" "password"
assert_fail "reject password with double quote" validate_safe_string 'pass"injection' "password"

# Valid hosts
assert_pass "valid host: api.proxybase.xyz" validate_safe_string "api.proxybase.xyz" "host"
assert_pass "valid host: 192.168.1.1" validate_safe_string "192.168.1.1" "host"
assert_pass "valid host: localhost" validate_safe_string "localhost" "host"

# Invalid hosts
assert_fail "reject host with \$()" validate_safe_string '$(evil).com' "host"
assert_fail "reject host with semicolon" validate_safe_string 'host;rm -rf /' "host"
assert_fail "reject host with space" validate_safe_string 'host name' "host"

# Valid ports
assert_pass "valid port: 1080" validate_safe_string "1080" "port"
assert_pass "valid port: 8080" validate_safe_string "8080" "port"
assert_pass "valid port: 65535" validate_safe_string "65535" "port"

# Invalid ports
assert_fail "reject port: 0" validate_safe_string "0" "port"
assert_fail "reject port: 99999" validate_safe_string "99999" "port"
assert_fail "reject port: abc" validate_safe_string "abc" "port"
assert_fail "reject port with injection" validate_safe_string '1080$(echo)' "port"

# Valid order_ids
assert_pass "valid order_id: gmp6vp2k" validate_safe_string "gmp6vp2k" "order_id"
assert_pass "valid order_id: order-123" validate_safe_string "order-123" "order_id"
assert_pass "valid order_id: order_456" validate_safe_string "order_456" "order_id"

# Invalid order_ids
assert_fail "reject order_id with \$()" validate_safe_string '$(whoami)' "order_id"
assert_fail "reject order_id with semicolon" validate_safe_string 'id;rm -rf /' "order_id"
assert_fail "reject order_id with space" validate_safe_string 'order id' "order_id"
assert_fail "reject order_id with slash" validate_safe_string 'order/../../etc/passwd' "order_id"
assert_fail "reject order_id with dot" validate_safe_string 'order.id' "order_id"

# Valid API keys
assert_pass "valid api_key: pk_abc123" validate_safe_string "pk_abc123" "api_key"
assert_pass "valid api_key: pk_test-key" validate_safe_string "pk_test-key" "api_key"

# Invalid API keys
assert_fail "reject api_key with \$()" validate_safe_string 'pk_$(whoami)' "api_key"
assert_fail "reject api_key with semicolon" validate_safe_string 'pk;evil' "api_key"

# Valid package_ids
assert_pass "valid package_id: us_residential_1gb" validate_safe_string "us_residential_1gb" "package_id"
assert_pass "valid package_id: eu-datacenter-10gb" validate_safe_string "eu-datacenter-10gb" "package_id"

# Invalid package_ids
assert_fail "reject package_id with \$()" validate_safe_string 'pkg_$(evil)' "package_id"

# Valid proxy URLs
assert_pass "valid proxy_url" validate_safe_string "socks5://pb_user:pass123@api.proxybase.xyz:1080" "proxy_url"

# Invalid proxy URLs
assert_fail "reject proxy_url with injection in user" validate_safe_string 'socks5://$(id):pass@host:1080' "proxy_url"
assert_fail "reject proxy_url with injection in pass" validate_safe_string 'socks5://user:$(id)@host:1080' "proxy_url"
assert_fail "reject proxy_url with injection in host" validate_safe_string 'socks5://user:pass@$(evil):1080' "proxy_url"
assert_fail "reject proxy_url wrong protocol" validate_safe_string 'http://user:pass@host:1080' "proxy_url"

echo ""

# ─── Test build_safe_proxy_url ────────────────────────────────────────
echo "── build_safe_proxy_url tests ──"

# Valid construction
PROXY_URL=""
if build_safe_proxy_url "api.proxybase.xyz" "1080" "pb_user" "pass123"; then
    if [[ "$PROXY_URL" == "socks5://pb_user:pass123@api.proxybase.xyz:1080" ]]; then
        echo "  ✅ PASS: builds correct URL from valid parts"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL: URL mismatch: $PROXY_URL"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  ❌ FAIL: build_safe_proxy_url rejected valid inputs"
    FAIL=$((FAIL + 1))
fi

# Injection in username
PROXY_URL=""
if build_safe_proxy_url "host" "1080" '$(whoami)' "pass" 2>/dev/null; then
    echo "  ❌ FAIL: should reject injected username"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: rejects injected username"
    PASS=$((PASS + 1))
fi

# Injection in password
PROXY_URL=""
if build_safe_proxy_url "host" "1080" "user" '`id`' 2>/dev/null; then
    echo "  ❌ FAIL: should reject injected password"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: rejects injected password"
    PASS=$((PASS + 1))
fi

# Injection in host
PROXY_URL=""
if build_safe_proxy_url '$(evil).com' "1080" "user" "pass" 2>/dev/null; then
    echo "  ❌ FAIL: should reject injected host"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: rejects injected host"
    PASS=$((PASS + 1))
fi

# Injection in port
PROXY_URL=""
if build_safe_proxy_url "host" '1080$(echo)' "user" "pass" 2>/dev/null; then
    echo "  ❌ FAIL: should reject injected port"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: rejects injected port"
    PASS=$((PASS + 1))
fi

echo ""

# ─── Test write_proxy_env_file ────────────────────────────────────────
echo "── write_proxy_env_file tests ──"

TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# Valid write
if write_proxy_env_file "$TMPFILE" "test-order" "socks5://pb_user:pass123@api.proxybase.xyz:1080"; then
    # Check that values are single-quoted (not double-quoted)
    if grep -q "export ALL_PROXY='socks5://pb_user:pass123@api.proxybase.xyz:1080'" "$TMPFILE"; then
        echo "  ✅ PASS: env file uses single-quoted values"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL: env file does not use single-quoted values"
        cat "$TMPFILE"
        FAIL=$((FAIL + 1))
    fi

    # Verify NO double-quoted exports exist
    if grep -q 'export ALL_PROXY="' "$TMPFILE"; then
        echo "  ❌ FAIL: env file still contains double-quoted exports (vulnerable!)"
        FAIL=$((FAIL + 1))
    else
        echo "  ✅ PASS: env file has no double-quoted exports"
        PASS=$((PASS + 1))
    fi
else
    echo "  ❌ FAIL: write_proxy_env_file rejected valid inputs"
    FAIL=$((FAIL + 1))
fi

# Reject injection attempt
if write_proxy_env_file "$TMPFILE" "test" 'socks5://$(whoami):pass@host:1080' 2>/dev/null; then
    echo "  ❌ FAIL: should reject injected proxy URL"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: rejects injected proxy URL in write_proxy_env_file"
    PASS=$((PASS + 1))
fi

echo ""

# ─── Test write_credentials_file ──────────────────────────────────────
echo "── write_credentials_file tests ──"

CRED_TMPFILE=$(mktemp)
trap "rm -f $TMPFILE $CRED_TMPFILE" EXIT

if write_credentials_file "$CRED_TMPFILE" "pk_abc123" "https://api.proxybase.xyz/v1" "agent-1"; then
    if grep -q "export PROXYBASE_API_KEY='pk_abc123'" "$CRED_TMPFILE"; then
        echo "  ✅ PASS: credentials file uses single-quoted API key"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL: credentials file does not use single-quoted API key"
        cat "$CRED_TMPFILE"
        FAIL=$((FAIL + 1))
    fi

    if grep -q 'export PROXYBASE_API_KEY="' "$CRED_TMPFILE"; then
        echo "  ❌ FAIL: credentials file has double-quoted API key (vulnerable!)"
        FAIL=$((FAIL + 1))
    else
        echo "  ✅ PASS: credentials file has no double-quoted API key"
        PASS=$((PASS + 1))
    fi
else
    echo "  ❌ FAIL: write_credentials_file rejected valid inputs"
    FAIL=$((FAIL + 1))
fi

# Reject injected API key
if write_credentials_file "$CRED_TMPFILE" 'pk_$(whoami)' "https://api.example.com" "agent" 2>/dev/null; then
    echo "  ❌ FAIL: should reject injected API key"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: rejects injected API key"
    PASS=$((PASS + 1))
fi

echo ""

# ─── Test command-level argument validation ───────────────────────────
echo "── Command argument validation tests ──"

# Test that proxybase.sh rejects malicious order_ids
RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" poll '$(whoami)' --once 2>&1) || true
if echo "$RESULT" | grep -qi "invalid\|security"; then
    echo "  ✅ PASS: poll rejects injected order_id"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: poll did not reject injected order_id"
    echo "  Output: $RESULT"
    FAIL=$((FAIL + 1))
fi

RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" rotate ';echo pwned' 2>&1) || true
if echo "$RESULT" | grep -qi "invalid\|security"; then
    echo "  ✅ PASS: rotate rejects injected order_id"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: rotate did not reject injected order_id"
    echo "  Output: $RESULT"
    FAIL=$((FAIL + 1))
fi

RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" order '$(evil)_package' 2>&1) || true
if echo "$RESULT" | grep -qi "invalid\|security"; then
    echo "  ✅ PASS: order rejects injected package_id"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: order did not reject injected package_id"
    echo "  Output: $RESULT"
    FAIL=$((FAIL + 1))
fi

RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" topup '$(evil)' us_residential_1gb 2>&1) || true
if echo "$RESULT" | grep -qi "invalid\|security"; then
    echo "  ✅ PASS: topup rejects injected order_id"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: topup did not reject injected order_id"
    echo "  Output: $RESULT"
    FAIL=$((FAIL + 1))
fi

RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" status '|cat /etc/passwd' 2>&1) || true
if echo "$RESULT" | grep -qi "invalid\|security"; then
    echo "  ✅ PASS: status rejects injected order_id"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: status did not reject injected order_id"
    echo "  Output: $RESULT"
    FAIL=$((FAIL + 1))
fi

RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" inject-gateway '`whoami`' 2>&1) || true
if echo "$RESULT" | grep -qi "invalid\|security"; then
    echo "  ✅ PASS: inject-gateway rejects injected order_id"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: inject-gateway did not reject injected order_id"
    echo "  Output: $RESULT"
    FAIL=$((FAIL + 1))
fi

echo ""

# ─── Test that valid operations still work ────────────────────────────
echo "── Positive functionality tests ──"

# help command
RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" help 2>&1)
if echo "$RESULT" | grep -q "ProxyBase"; then
    echo "  ✅ PASS: help command works"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: help command broken"
    FAIL=$((FAIL + 1))
fi

# poll with valid order_id format (will fail at API level but should pass validation)
RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" poll abc123 --once 2>&1) || true
if echo "$RESULT" | grep -qi "invalid characters"; then
    echo "  ❌ FAIL: poll rejected valid order_id format"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: poll accepts valid order_id format"
    PASS=$((PASS + 1))
fi

# order with valid package_id (will fail at API level but should pass validation)
RESULT=$(bash "$SCRIPT_DIR/proxybase.sh" order us_residential_1gb 2>&1) || true
if echo "$RESULT" | grep -qi "invalid characters"; then
    echo "  ❌ FAIL: order rejected valid package_id format"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: order accepts valid package_id format"
    PASS=$((PASS + 1))
fi

echo ""
echo "==========================================="
echo "  Results: $PASS passed, $FAIL failed"
echo "==========================================="

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
exit 0
