#!/usr/bin/env bash
# tenk.sh — TenK CLI for OpenClaw
# Usage: tenk.sh <command> [args]

set -euo pipefail

API="https://tenk.oventlabs.com/api"
CONFIG_DIR="${HOME}/.config/tenk-connect"
TOKEN_FILE="${CONFIG_DIR}/token"

mkdir -p "$CONFIG_DIR"

# ── helpers ────────────────────────────────────────────────────────────────
token_get()  { [[ -f "$TOKEN_FILE" ]] && cat "$TOKEN_FILE" || echo ""; }
token_save() { echo -n "$1" > "$TOKEN_FILE"; chmod 600 "$TOKEN_FILE"; }

api_get() {
  local path="$1"
  local tok; tok=$(token_get)
  curl -sf "$API$path" -H "Authorization: Bearer $tok"
}

die() { echo "❌ $*" >&2; exit 1; }

# ── commands ────────────────────────────────────────────────────────────────

cmd_auth() {
  echo "🔐 Iniciando autenticación con TenK..."

  # Request device code
  local resp; resp=$(curl -sf -X POST "$API/device-auth/code") || die "No se pudo conectar a TenK API"
  local code expires
  code=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(d['code'])")
  expires=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(d['expires_in'])")

  echo ""
  echo "  Abre este enlace en tu navegador:"
  echo "  👉  https://tenk.oventlabs.com/#/authorize/$code"
  echo ""
  echo "  Código: $code"
  echo "  (expira en ${expires}s)"
  echo ""

  # Poll every 3s until approved or expired
  local max_attempts=$(( expires / 3 ))
  local i=0
  while [[ $i -lt $max_attempts ]]; do
    sleep 3
    local status_resp; status_resp=$(curl -sf "$API/device-auth/code/$code/status") || continue
    local status; status=$(echo "$status_resp" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['status'])")

    if [[ "$status" == "approved" ]]; then
      local token; token=$(echo "$status_resp" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['token'])")
      token_save "$token"
      echo "✅ Autenticado exitosamente. Token guardado."
      exit 0
    elif [[ "$status" == "expired" ]]; then
      die "El código expiró. Vuelve a ejecutar: tenk.sh auth"
    fi

    i=$(( i + 1 ))
  done

  die "Tiempo de espera agotado. Intenta de nuevo."
}

cmd_whoami() {
  local tok; tok=$(token_get)
  [[ -z "$tok" ]] && die "No autenticado. Ejecuta: tenk.sh auth"

  local resp; resp=$(api_get "/auth/me") || die "Token inválido o expirado. Ejecuta: tenk.sh auth"
  echo "$resp" | python3 -c "
import json, sys
d = json.load(sys.stdin)['data']
print(f\"👤 {d['name']} ({d['email']})\")
print(f\"   Tier: {d['tier']} | Onboarding: {'✅' if d['hasCompletedOnboarding'] else '❌'}\")
"
}

cmd_skills() {
  local tok; tok=$(token_get)
  [[ -z "$tok" ]] && die "No autenticado. Ejecuta: tenk.sh auth"

  local resp; resp=$(api_get "/skills") || die "Error al obtener habilidades"
  echo "$resp" | python3 -c "
import json, sys
data = json.load(sys.stdin)
skills = data.get('data', [])
if not skills:
    print('📭 No tienes habilidades registradas.')
    sys.exit(0)
print(f'🎯 Habilidades ({len(skills)}):')
for s in skills:
    total = s.get('totalSessions', 0)
    hours = round(total / 3600, 1) if total else 0
    gps = '📍' if s.get('isGpsSkill') else ''
    print(f\"  {gps} {s['icon']} {s['name']} — {hours}h ({total} sesiones)\")
"
}

cmd_stats() {
  local tok; tok=$(token_get)
  [[ -z "$tok" ]] && die "No autenticado. Ejecuta: tenk.sh auth"

  local resp; resp=$(api_get "/skills") || die "Error"
  echo "$resp" | python3 -c "
import json, sys
skills = json.load(sys.stdin).get('data', [])
total_sec = sum(s.get('totalSessions', 0) for s in skills)
total_h = round(total_sec / 3600, 1)
goal = 10000
pct = round(total_h / goal * 100, 2)
remaining = round(goal - total_h, 1)
print(f'📊 Stats TenK:')
print(f'   Total: {total_h}h de {goal}h ({pct}%)')
print(f'   Faltan: {remaining}h para las 10,000h')
print(f'   Habilidades activas: {len(skills)}')
"
}

cmd_log() {
  # tenk.sh log <skill_name> <minutes> [note]
  local tok; tok=$(token_get)
  [[ -z "$tok" ]] && die "No autenticado. Ejecuta: tenk.sh auth"

  local skill_query="${1:-}"
  local minutes="${2:-}"
  local note="${3:-}"

  [[ -z "$skill_query" ]] && die "Uso: tenk.sh log <habilidad> <minutos> [nota]"
  [[ -z "$minutes" ]] && die "Uso: tenk.sh log <habilidad> <minutos> [nota]"

  # Find skill by name
  local skills_resp; skills_resp=$(api_get "/skills") || die "Error al obtener habilidades"
  local skill_id skill_name
  skill_id=$(echo "$skills_resp" | python3 -c "
import json, sys
q = '$skill_query'.lower()
skills = json.load(sys.stdin).get('data', [])
match = next((s for s in skills if q in s['name'].lower()), None)
if match:
    print(match['id'])
" 2>/dev/null)
  skill_name=$(echo "$skills_resp" | python3 -c "
import json, sys
q = '$skill_query'.lower()
skills = json.load(sys.stdin).get('data', [])
match = next((s for s in skills if q in s['name'].lower()), None)
if match:
    print(match['name'])
" 2>/dev/null)

  [[ -z "$skill_id" ]] && die "Habilidad '$skill_query' no encontrada. Usa: tenk.sh skills"

  local duration_sec=$(( minutes * 60 ))
  local body
  body=$(python3 -c "
import json, sys
print(json.dumps({'skillId': '$skill_id', 'duration': $duration_sec, 'notes': sys.argv[1]}))
" "$note") || die "Error al construir payload"

  local resp; resp=$(curl -sf -X POST "$API/sessions" \
    -H "Authorization: Bearer $(token_get)" \
    -H "Content-Type: application/json" \
    -d "$body") || die "Error al registrar sesión"

  echo "$resp" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('success'):
    print(f\"✅ Registrado: $skill_name — ${minutes} min\")
else:
    print(f\"❌ Error: {d}\")
"
}

cmd_streak() {
  local tok; tok=$(token_get)
  [[ -z "$tok" ]] && die "No autenticado. Ejecuta: tenk.sh auth"

  local resp; resp=$(api_get "/skills") || die "Error"
  echo "$resp" | python3 -c "
import json, sys
from datetime import datetime, timezone
skills = json.load(sys.stdin).get('data', [])
# Show last session per skill
print('🔥 Última actividad:')
for s in sorted(skills, key=lambda x: x.get('lastSessionAt') or '', reverse=True)[:5]:
    last = s.get('lastSessionAt', 'Nunca')
    if last and last != 'Nunca':
        try:
            dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
            diff = datetime.now(timezone.utc) - dt
            days = diff.days
            label = f'{days}d atrás' if days > 0 else 'Hoy'
        except:
            label = last[:10]
    else:
        label = 'Sin sesiones'
    print(f\"  {s['icon']} {s['name']}: {label}\")
"
}

cmd_logout() {
  rm -f "$TOKEN_FILE"
  echo "👋 Sesión cerrada."
}

cmd_help() {
  cat <<EOF
tenk.sh — TenK CLI para OpenClaw

Comandos:
  auth          Autenticar con tu cuenta TenK (OAuth Device Flow)
  whoami        Ver usuario autenticado
  skills        Listar tus habilidades con horas acumuladas
  stats         Resumen total de horas y progreso hacia 10,000h
  log <skill> <min> [nota]  Registrar sesión de práctica
  streak        Ver última actividad por habilidad
  logout        Cerrar sesión

Ejemplos:
  tenk.sh auth
  tenk.sh skills
  tenk.sh log guitarra 30 "Escalas pentatónicas"
  tenk.sh stats
EOF
}

# ── dispatch ────────────────────────────────────────────────────────────────
case "${1:-help}" in
  auth)    cmd_auth ;;
  whoami)  cmd_whoami ;;
  skills)  cmd_skills ;;
  stats)   cmd_stats ;;
  log)     shift; cmd_log "$@" ;;
  streak)  cmd_streak ;;
  logout)  cmd_logout ;;
  help|--help|-h) cmd_help ;;
  *)       die "Comando desconocido: ${1}. Usa: tenk.sh help" ;;
esac
