#!/usr/bin/env bash
# sigaa_login.sh - Authenticate to SIGAA via CAS SSO or direct login
#
# USAGE: source scripts/sigaa_login.sh
#
# REQUIRED ENV VARS (set before sourcing):
#   SIGAA_URL      - Institution base URL, e.g. https://sigaa.unb.br
#   SIGAA_USER     - Login (matricula number, CPF, or SIAPE depending on institution)
#   SIGAA_PASSWORD - Account password
#
# EXPORTS (available after sourcing):
#   SIGAA_COOKIE_FILE - Path to session cookie file (chmod 600, auto-deleted on shell exit)
#   SIGAA_USER_ID     - Numeric user ID used in JSF menu POSTs
#   SIGAA_BASE_URL    - Same as SIGAA_URL (convenience alias)
#
# EXAMPLE:
#   export SIGAA_URL='https://sigaa.unb.br'
#   export SIGAA_USER='241104251'
#   export SIGAA_PASSWORD='mypassword'
#   source scripts/sigaa_login.sh
#   bash scripts/sigaa_student.sh enrollment-result

set -euo pipefail

# ---- Validate env vars -------------------------------------------------------

_sigaa_check_env() {
  local missing=()
  [[ -z "${SIGAA_URL:-}" ]]      && missing+=("SIGAA_URL")
  [[ -z "${SIGAA_USER:-}" ]]     && missing+=("SIGAA_USER")
  [[ -z "${SIGAA_PASSWORD:-}" ]] && missing+=("SIGAA_PASSWORD")

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "ERROR: Missing required environment variables: ${missing[*]}" >&2
    echo "  export SIGAA_URL='https://sigaa.unb.br'" >&2
    echo "  export SIGAA_USER='<your-login>'" >&2
    echo "  export SIGAA_PASSWORD='<your-password>'" >&2
    return 1 2>/dev/null || exit 1
  fi
}

_sigaa_check_env

# ---- Setup cookie file -------------------------------------------------------

SIGAA_COOKIE_FILE="$(mktemp /tmp/sigaa_session_XXXXXX.txt)"
chmod 600 "$SIGAA_COOKIE_FILE"

# Auto-delete cookie file when the shell exits (only when sourced)
trap 'rm -f "$SIGAA_COOKIE_FILE" 2>/dev/null; unset SIGAA_COOKIE_FILE SIGAA_USER_ID SIGAA_BASE_URL' EXIT 2>/dev/null || true

AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

# ---- Detect login type -------------------------------------------------------

# Follow initial redirect to see if institution uses CAS SSO
INITIAL_URL=$(curl -s -o /dev/null -w "%{url_effective}" -L \
  -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
  -A "$AGENT" \
  "${SIGAA_URL}/sigaa/verTelaLogin.do" 2>/dev/null)

# ---- CAS SSO Login (UNB and others) -----------------------------------------

if echo "$INITIAL_URL" | grep -qiE "autenticacao|sso-server|/cas"; then
  LOGIN_PAGE=$(curl -s \
    -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" "$INITIAL_URL")

  ACTION_PATH=$(echo "$LOGIN_PAGE" | grep -oP 'action="[^"]*"' | head -1 | sed 's/action="//;s/"//')
  LT=$(echo "$LOGIN_PAGE" | grep 'name="lt"' | grep -oP 'value="[^"]*"' | sed 's/value="//;s/"//')
  EXEC=$(echo "$LOGIN_PAGE" | grep 'name="execution"' | grep -oP 'value="[^"]*"' | sed 's/value="//;s/"//')
  CAS_BASE=$(echo "$INITIAL_URL" | grep -oP 'https?://[^/]+')
  FULL_ACTION="${CAS_BASE}${ACTION_PATH}"

  RESULT=$(curl -s -L \
    -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" \
    -X POST "$FULL_ACTION" \
    --data-urlencode "username=${SIGAA_USER}" \
    --data-urlencode "password=${SIGAA_PASSWORD}" \
    --data-urlencode "lt=${LT}" \
    --data-urlencode "execution=${EXEC}" \
    -d "_eventId=submit" \
    -w "\n__FINAL_URL__:%{url_effective}")

  if echo "$RESULT" | grep -qiE "credenciais inv|invalid credential|login-error"; then
    echo "ERROR: Invalid credentials for user '${SIGAA_USER}'" >&2
    rm -f "$SIGAA_COOKIE_FILE"
    return 1 2>/dev/null || exit 1
  fi

# ---- Direct Login (most other institutions) ----------------------------------

else
  LOGIN_PAGE=$(curl -s \
    -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" \
    "${SIGAA_URL}/sigaa/verTelaLogin.do")

  VS=$(echo "$LOGIN_PAGE" | grep -oP 'name="javax\.faces\.ViewState"[^>]*value="\K[^"]+' | head -1)

  RESULT=$(curl -s -L \
    -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" \
    -X POST "${SIGAA_URL}/sigaa/logar.do" \
    -d "dispatch=logOn" \
    --data-urlencode "user.login=${SIGAA_USER}" \
    --data-urlencode "user.senha=${SIGAA_PASSWORD}" \
    --data-urlencode "javax.faces.ViewState=${VS}" \
    -w "\n__FINAL_URL__:%{url_effective}")

  if echo "$RESULT" | grep -qiE "senha ou login inv|Usuário e/ou Senha"; then
    echo "ERROR: Invalid credentials for user '${SIGAA_USER}'" >&2
    rm -f "$SIGAA_COOKIE_FILE"
    return 1 2>/dev/null || exit 1
  fi
fi

# ---- Extract user ID ---------------------------------------------------------

PORTAL_HTML=$(curl -s \
  -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
  -A "$AGENT" \
  "${SIGAA_URL}/sigaa/portais/discente/discente.jsf" 2>/dev/null || \
  curl -s \
  -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
  -A "$AGENT" \
  "${SIGAA_URL}/sigaa/verPortalDiscente.do")

SIGAA_USER_ID=$(echo "$PORTAL_HTML" | grep -oP 'name="id"\s+value="\K[0-9]+' | head -1)

export SIGAA_COOKIE_FILE
export SIGAA_USER_ID
export SIGAA_BASE_URL="${SIGAA_URL}"

# ---- Result ------------------------------------------------------------------

if [[ -n "$SIGAA_USER_ID" ]]; then
  echo "OK: Logged in as user ID ${SIGAA_USER_ID} | Cookie: ${SIGAA_COOKIE_FILE} (chmod 600, auto-cleaned)"
else
  echo "WARNING: Logged in but could not extract user ID — some operations may fail"
fi

unset SIGAA_PASSWORD  # Don't keep password in env after login
