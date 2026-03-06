#!/usr/bin/env bash
# sigaa_professor.sh - Professor portal operations for SIGAA
#
# REQUIRES (exported by sigaa_login.sh):
#   SIGAA_COOKIE_FILE, SIGAA_USER_ID, SIGAA_BASE_URL
#
# USAGE: bash scripts/sigaa_professor.sh <action>
#
# ACTIONS:
#   classes              - List current semester classes
#   students <turma_id>  - List students in a class
#   attendance           - Show pending attendance entries
#   schedule             - Show professor teaching schedule

set -euo pipefail

AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

for var in SIGAA_COOKIE_FILE SIGAA_USER_ID SIGAA_BASE_URL; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: \$$var is not set. Run: source scripts/sigaa_login.sh" >&2
    exit 1
  fi
done

_get() {
  sleep 0.5
  curl -s -L -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" -A "$AGENT" "$1"
}

_post_menu() {
  local action="$1"
  sleep 0.5
  local html
  html=$(curl -s -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" "${SIGAA_BASE_URL}/sigaa/verPortalDocente.do")
  local vs
  vs=$(echo "$html" | grep -oP 'name="javax\.faces\.ViewState"[^>]*value="\K[^"]+' | head -1)
  sleep 0.5
  curl -s -L -c "$SIGAA_COOKIE_FILE" -b "$SIGAA_COOKIE_FILE" \
    -A "$AGENT" \
    -X POST "${SIGAA_BASE_URL}/sigaa/verPortalDocente.do" \
    -d "menu%3Aform_menu_docente=menu%3Aform_menu_docente" \
    -d "id=${SIGAA_USER_ID}" \
    --data-urlencode "jscook_action=${action}" \
    --data-urlencode "javax.faces.ViewState=${vs}"
}

_extract_table() {
  python3 -c "
import sys, re, html as h
content = sys.stdin.read()
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
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

action_classes() {
  echo "=== Turmas do Docente ==="
  _get "${SIGAA_BASE_URL}/sigaa/verPortalDocente.do" | python3 -c "
import sys, re, html as h
text = sys.stdin.read()
m = re.search(r'(turma.*?)(?:Pesquisa|Extens|$)', text, re.DOTALL | re.IGNORECASE)
if m:
    block = re.sub(r'<[^>]+>', ' ', m.group(1))
    block = h.unescape(re.sub(r'[ \t]+', ' ', block))
    for line in block.split('\n'):
        line = line.strip()
        if line and len(line) > 5:
            print(line)
" | head -40
}

action_students() {
  local turma_id="${1:-}"
  [[ -z "$turma_id" ]] && { echo "Usage: sigaa_professor.sh students <turma_id>" >&2; exit 1; }
  echo "=== Alunos da Turma ${turma_id} ==="
  _get "${SIGAA_BASE_URL}/sigaa/graduacao/turma/discente/lista.jsf?id=${turma_id}" | _extract_table | head -80
}

action_attendance() {
  echo "=== Frequência Pendente ==="
  _post_menu "menu_form_menu_docente_docente_menu:A]#{frequenciaAluno.listarTurmasComFrequenciaPendente}" | _extract_table | head -40
}

action_schedule() {
  echo "=== Grade de Horários ==="
  _post_menu "menu_form_menu_docente_docente_menu:A]#{horarioDocente.visualizarHorario}" | _extract_table | head -40
}

ACTION="${1:-classes}"
shift || true
case "$ACTION" in
  classes)    action_classes ;;
  students)   action_students "$@" ;;
  attendance) action_attendance ;;
  schedule)   action_schedule ;;
  *)
    echo "Unknown action: $ACTION" >&2
    echo "Available: classes | students <turma_id> | attendance | schedule" >&2
    exit 1
    ;;
esac
