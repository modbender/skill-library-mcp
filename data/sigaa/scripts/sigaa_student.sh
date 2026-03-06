#!/usr/bin/env bash
# sigaa_student.sh - Student portal operations for SIGAA
#
# REQUIRES (exported by sigaa_login.sh):
#   SIGAA_COOKIE_FILE, SIGAA_USER_ID, SIGAA_BASE_URL
#
# USAGE: bash scripts/sigaa_student.sh <action>
#
# ACTIONS:
#   status            - Show enrollment status and program info
#   enrollments       - List current semester classes
#   enrollment-result - Show enrollment request status (SUBMETIDA / DEFERIDA / NEGADA)
#   grades            - Grades for current/past semesters
#   history           - Full academic history
#   schedule          - Current semester class schedule

set -euo pipefail

AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

# ---- Guard: check required vars ----------------------------------------------

for var in SIGAA_COOKIE_FILE SIGAA_USER_ID SIGAA_BASE_URL; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: \$$var is not set. Run: source scripts/sigaa_login.sh" >&2
    exit 1
  fi
done

# ---- Helpers -----------------------------------------------------------------

_get() {
  sleep 0.5
  curl -s -L -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" -A "$AGENT" "$1"
}

_post_menu() {
  local action="$1"
  sleep 0.5
  local html
  html=$(curl -s -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" "${SIGAA_BASE_URL}/sigaa/portais/discente/discente.jsf")
  local vs
  vs=$(echo "$html" | grep -oP 'name="javax\.faces\.ViewState"[^>]*value="\K[^"]+' | head -1)

  sleep 0.5
  curl -s -L -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" \
    -X POST "${SIGAA_BASE_URL}/sigaa/portais/discente/discente.jsf" \
    -d "menu%3Aform_menu_discente=menu%3Aform_menu_discente" \
    -d "id=${SIGAA_USER_ID}" \
    --data-urlencode "jscook_action=${action}" \
    --data-urlencode "javax.faces.ViewState=${vs}"
}

_clean_html() {
  python3 -c "
import sys, re, html as h
t = sys.stdin.read()
t = re.sub(r'<script[^>]*>.*?</script>', '', t, flags=re.DOTALL)
t = re.sub(r'<style[^>]*>.*?</style>', '', t, flags=re.DOTALL)
t = re.sub(r'<[^>]+>', ' ', t)
t = h.unescape(t)
t = re.sub(r'[ \t]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
for line in t.split('\n'):
    line = line.strip()
    if line:
        print(line)
"
}

_extract_table() {
  python3 -c "
import sys, re, html as h
content = sys.stdin.read()
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL)
for row in rows:
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
    if cells:
        clean = [h.unescape(re.sub(r'<[^>]+>|\s+', ' ', c)).strip() for c in cells]
        clean = [c for c in clean if c]
        if clean:
            print('\t'.join(clean))
"
}

# ---- Actions -----------------------------------------------------------------

action_status() {
  local html
  html=$(_get "${SIGAA_BASE_URL}/sigaa/portais/discente/discente.jsf")
  echo "$html" | python3 -c "
import sys, re, html as h
text = re.sub(r'<[^>]+>', ' ', sys.stdin.read())
text = h.unescape(re.sub(r'[ \t]+', ' ', text))
keywords = ['PROGRAMA','Curso:','Status:','ATIVO','INATIVO','Mestrado','Doutorado','Graduação','Semestre atual']
seen = set()
for kw in keywords:
    for line in text.split('\n'):
        line = line.strip()
        if kw in line and len(line) < 200 and line not in seen:
            print(line)
            seen.add(line)
            break
"
}

action_enrollments() {
  echo "=== Turmas do Semestre Atual ==="
  local html
  html=$(_get "${SIGAA_BASE_URL}/sigaa/portais/discente/discente.jsf")

  local semester
  semester=$(echo "$html" | grep -oP 'Semestre atual:.*?<strong>\K[^<]+' || echo "")
  [[ -n "$semester" ]] && echo "Semestre: $semester"

  echo "$html" | python3 -c "
import sys, re, html as h
text = sys.stdin.read()
m = re.search(r'turmas-portal(.*?)(?:Comunidades|$)', text, re.DOTALL)
if m:
    block = re.sub(r'<[^>]+>', ' ', m.group(1))
    block = h.unescape(re.sub(r'[ \t]+', ' ', block))
    for line in block.split('\n'):
        line = line.strip()
        if line and line != 'Ver turmas anteriores':
            print(line)
"
}

action_enrollment_result() {
  echo "=== Comprovante de Solicitação de Matrícula ==="
  local html
  html=$(_post_menu "menu_form_menu_discente_discente_menu:A]#{matriculaGraduacao.verComprovanteSolicitacoes}")

  local period
  period=$(echo "$html" | grep -oP 'Per[íi]odo [0-9.]+' | head -1 || echo "")
  [[ -n "$period" ]] && echo "$period"
  echo ""
  echo -e "Componente\tTurma\tSituação"
  echo "---"
  echo "$html" | _extract_table | grep -E "SUBMETIDA|DEFERIDA|NEGADA|APROVADA|INDEFERIDA|AGUARDANDO|[0-9]{6}" || \
    echo "(nenhuma solicitação encontrada)"
}

action_grades() {
  echo "=== Notas ==="
  local html
  html=$(_post_menu "menu_form_menu_discente_discente_menu:A]#{relatorioNotasAluno.gerarRelatorio}")
  echo "$html" | _extract_table | grep -E "[0-9]\.[0-9]|Aprovado|Reprovado|Trancado|Cursando" | head -60 || \
    echo "$html" | _clean_html | grep -E "[0-9]\.[0-9]|Aprovado|Reprovado" | head -30
}

action_history() {
  echo "=== Histórico Acadêmico ==="
  local html
  html=$(_post_menu "menu_form_menu_discente_discente_menu:A]#{portalDiscente.historicoComDadosAdicionais}")
  echo "$html" | _extract_table | grep -E "[0-9]{4}\.[12]|Aprovado|Reprovado|Trancado|Cursando" | head -100
}

action_schedule() {
  echo "=== Turmas Virtuais ==="
  local html
  html=$(_get "${SIGAA_BASE_URL}/sigaa/portais/discente/turmas.jsf")
  echo "$html" | _extract_table | head -50
}

# ---- Dispatch ----------------------------------------------------------------

ACTION="${1:-status}"
case "$ACTION" in
  status)            action_status ;;
  enrollments)       action_enrollments ;;
  enrollment-result) action_enrollment_result ;;
  grades)            action_grades ;;
  history)           action_history ;;
  schedule)          action_schedule ;;
  *)
    echo "Unknown action: $ACTION" >&2
    echo "Available: status | enrollments | enrollment-result | grades | history | schedule" >&2
    exit 1
    ;;
esac
