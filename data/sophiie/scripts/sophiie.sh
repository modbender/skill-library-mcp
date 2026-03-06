#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://api.sophiie.ai"

# --- Env validation ---
if [[ -z "${SOPHIIE_API_KEY:-}" ]]; then
  echo '{"error":"SOPHIIE_API_KEY is not set. Get your key from Sophiie Dashboard → Settings → API Keys."}' >&2
  exit 1
fi

# --- HTTP helpers ---
_auth_header="Authorization: Bearer ${SOPHIIE_API_KEY}"

_get() {
  local path="$1"; shift
  curl -s --fail-with-body -H "$_auth_header" "$@" "${BASE_URL}${path}"
}

_post() {
  local path="$1" body="$2"
  curl -s --fail-with-body -X POST \
    -H "$_auth_header" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "${BASE_URL}${path}"
}

_put() {
  local path="$1" body="$2"
  curl -s --fail-with-body -X PUT \
    -H "$_auth_header" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "${BASE_URL}${path}"
}

_delete() {
  local path="$1"
  curl -s --fail-with-body -X DELETE \
    -H "$_auth_header" \
    "${BASE_URL}${path}"
}

_usage() {
  cat <<'EOF'
Usage: sophiie.sh <domain> <action> [options]

Domains & actions:
  leads        list | get <id> | create | update <id> | delete <id> | notes <id> | activities <id>
  inquiries    list | get <id>
  faqs         list | create | update <id> | delete <id>
  policies     list | create | update <id> | delete <id>
  calls        send
  sms          send
  appointments list
  org          get | availability | members | services | products
  members      list

Run with --help after any action for option details.
EOF
  exit 1
}

# --- Pagination query string builder ---
_pagination_qs() {
  local page="${1:-}" limit="${2:-}"
  local qs=""
  [[ -n "$page" ]] && qs="page=${page}"
  [[ -n "$limit" ]] && { [[ -n "$qs" ]] && qs="${qs}&limit=${limit}" || qs="limit=${limit}"; }
  echo "$qs"
}

# ============================================================
# LEADS
# ============================================================

cmd_leads_list() {
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/leads${qs:+?$qs}"
}

cmd_leads_get() {
  local id="${1:?Lead ID required (ld_...)}"
  _get "/v1/leads/${id}"
}

cmd_leads_create() {
  local first_name="" last_name="" email="" phone="" suburb="" business_name="" instagram="" facebook=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --firstName)    first_name="$2"; shift 2 ;;
      --lastName)     last_name="$2"; shift 2 ;;
      --email)        email="$2"; shift 2 ;;
      --phone)        phone="$2"; shift 2 ;;
      --suburb)       suburb="$2"; shift 2 ;;
      --businessName) business_name="$2"; shift 2 ;;
      --instagram)    instagram="$2"; shift 2 ;;
      --facebook)     facebook="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -z "$first_name" ]] && { echo '{"error":"--firstName is required"}' >&2; exit 1; }
  [[ -z "$suburb" ]] && { echo '{"error":"--suburb is required"}' >&2; exit 1; }

  local body
  body=$(jq -n \
    --arg fn "$first_name" \
    --arg ln "$last_name" \
    --arg em "$email" \
    --arg ph "$phone" \
    --arg sb "$suburb" \
    --arg bn "$business_name" \
    --arg ig "$instagram" \
    --arg fb "$facebook" \
    '{firstName: $fn, suburb: $sb}
     + (if $ln != "" then {lastName: $ln} else {} end)
     + (if $em != "" then {email: $em} else {} end)
     + (if $ph != "" then {phone: $ph} else {} end)
     + (if $bn != "" then {businessName: $bn} else {} end)
     + (if ($ig != "" or $fb != "") then {socials:
         ((if $ig != "" then {instagram: $ig} else {} end)
        + (if $fb != "" then {facebook: $fb} else {} end))
       } else {} end)')

  _post "/v1/leads" "$body"
}

cmd_leads_update() {
  local id="${1:?Lead ID required (ld_...)}"; shift
  local first_name="" last_name="" email="" phone="" suburb="" business_name="" instagram="" facebook=""
  local has_field=false
  while [[ $# -gt 0 ]]; do
    has_field=true
    case "$1" in
      --firstName)    first_name="$2"; shift 2 ;;
      --lastName)     last_name="$2"; shift 2 ;;
      --email)        email="$2"; shift 2 ;;
      --phone)        phone="$2"; shift 2 ;;
      --suburb)       suburb="$2"; shift 2 ;;
      --businessName) business_name="$2"; shift 2 ;;
      --instagram)    instagram="$2"; shift 2 ;;
      --facebook)     facebook="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ "$has_field" == "false" ]] && { echo '{"error":"At least one field is required for update"}' >&2; exit 1; }

  local body
  body=$(jq -n \
    --arg fn "$first_name" \
    --arg ln "$last_name" \
    --arg em "$email" \
    --arg ph "$phone" \
    --arg sb "$suburb" \
    --arg bn "$business_name" \
    --arg ig "$instagram" \
    --arg fb "$facebook" \
    '(if $fn != "" then {firstName: $fn} else {} end)
     + (if $ln != "" then {lastName: $ln} else {} end)
     + (if $em != "" then {email: $em} else {} end)
     + (if $ph != "" then {phone: $ph} else {} end)
     + (if $sb != "" then {suburb: $sb} else {} end)
     + (if $bn != "" then {businessName: $bn} else {} end)
     + (if ($ig != "" or $fb != "") then {socials:
         ((if $ig != "" then {instagram: $ig} else {} end)
        + (if $fb != "" then {facebook: $fb} else {} end))
       } else {} end)')

  _put "/v1/leads/${id}" "$body"
}

cmd_leads_delete() {
  local id="${1:?Lead ID required (ld_...)}"
  _delete "/v1/leads/${id}"
}

cmd_leads_notes() {
  local id="${1:?Lead ID required (ld_...)}"; shift
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/leads/${id}/notes${qs:+?$qs}"
}

cmd_leads_activities() {
  local id="${1:?Lead ID required (ld_...)}"; shift
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/leads/${id}/activities${qs:+?$qs}"
}

# ============================================================
# INQUIRIES
# ============================================================

cmd_inquiries_list() {
  local page="" limit="" lead_id="" expand=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)   page="$2"; shift 2 ;;
      --limit)  limit="$2"; shift 2 ;;
      --leadId) lead_id="$2"; shift 2 ;;
      --expand) expand="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  [[ -n "$lead_id" ]] && { [[ -n "$qs" ]] && qs="${qs}&leadId=${lead_id}" || qs="leadId=${lead_id}"; }
  [[ -n "$expand" ]] && { [[ -n "$qs" ]] && qs="${qs}&expand=${expand}" || qs="expand=${expand}"; }
  _get "/v1/inquiries${qs:+?$qs}"
}

cmd_inquiries_get() {
  local id="${1:?Inquiry ID required}"
  _get "/v1/inquiries/${id}"
}

# ============================================================
# FAQS
# ============================================================

cmd_faqs_list() {
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/faqs${qs:+?$qs}"
}

cmd_faqs_create() {
  local question="" answer="" is_active=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --question) question="$2"; shift 2 ;;
      --answer)   answer="$2"; shift 2 ;;
      --isActive) is_active="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -z "$question" ]] && { echo '{"error":"--question is required"}' >&2; exit 1; }
  [[ -z "$answer" ]] && { echo '{"error":"--answer is required"}' >&2; exit 1; }

  local body
  body=$(jq -n \
    --arg q "$question" \
    --arg a "$answer" \
    --arg ia "$is_active" \
    '{question: $q, answer: $a}
     + (if $ia == "true" then {isActive: true}
        elif $ia == "false" then {isActive: false}
        else {} end)')

  _post "/v1/faqs" "$body"
}

cmd_faqs_update() {
  local id="${1:?FAQ ID required (number)}"; shift
  local question="" answer="" is_active=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --question) question="$2"; shift 2 ;;
      --answer)   answer="$2"; shift 2 ;;
      --isActive) is_active="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  local body
  body=$(jq -n \
    --arg q "$question" \
    --arg a "$answer" \
    --arg ia "$is_active" \
    '(if $q != "" then {question: $q} else {} end)
     + (if $a != "" then {answer: $a} else {} end)
     + (if $ia == "true" then {isActive: true}
        elif $ia == "false" then {isActive: false}
        else {} end)')

  _put "/v1/faqs/${id}" "$body"
}

cmd_faqs_delete() {
  local id="${1:?FAQ ID required (number)}"
  _delete "/v1/faqs/${id}"
}

# ============================================================
# POLICIES
# ============================================================

cmd_policies_list() {
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/policies${qs:+?$qs}"
}

cmd_policies_create() {
  local title="" content="" is_active=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title)    title="$2"; shift 2 ;;
      --content)  content="$2"; shift 2 ;;
      --isActive) is_active="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -z "$title" ]] && { echo '{"error":"--title is required"}' >&2; exit 1; }
  [[ -z "$content" ]] && { echo '{"error":"--content is required"}' >&2; exit 1; }

  local body
  body=$(jq -n \
    --arg t "$title" \
    --arg c "$content" \
    --arg ia "$is_active" \
    '{title: $t, content: $c}
     + (if $ia == "true" then {isActive: true}
        elif $ia == "false" then {isActive: false}
        else {} end)')

  _post "/v1/policies" "$body"
}

cmd_policies_update() {
  local id="${1:?Policy ID required (number)}"; shift
  local title="" content="" is_active=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title)    title="$2"; shift 2 ;;
      --content)  content="$2"; shift 2 ;;
      --isActive) is_active="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  local body
  body=$(jq -n \
    --arg t "$title" \
    --arg c "$content" \
    --arg ia "$is_active" \
    '(if $t != "" then {title: $t} else {} end)
     + (if $c != "" then {content: $c} else {} end)
     + (if $ia == "true" then {isActive: true}
        elif $ia == "false" then {isActive: false}
        else {} end)')

  _put "/v1/policies/${id}" "$body"
}

cmd_policies_delete() {
  local id="${1:?Policy ID required (number)}"
  _delete "/v1/policies/${id}"
}

# ============================================================
# CALLS
# ============================================================

cmd_calls_send() {
  local name="" phone="" mode="" instructions=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name)                name="$2"; shift 2 ;;
      --phoneNumber)         phone="$2"; shift 2 ;;
      --mode)                mode="$2"; shift 2 ;;
      --custom_instructions) instructions="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -z "$name" ]] && { echo '{"error":"--name is required"}' >&2; exit 1; }
  [[ -z "$phone" ]] && { echo '{"error":"--phoneNumber is required"}' >&2; exit 1; }

  local body
  body=$(jq -n \
    --arg n "$name" \
    --arg p "$phone" \
    --arg m "$mode" \
    --arg ci "$instructions" \
    '{name: $n, phoneNumber: $p}
     + (if $m != "" then {mode: $m} else {} end)
     + (if $ci != "" then {custom_instructions: $ci} else {} end)')

  _post "/v1/calls" "$body"
}

# ============================================================
# SMS
# ============================================================

cmd_sms_send() {
  local user_id="" lead_id="" message="" thread_id=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --userId)          user_id="$2"; shift 2 ;;
      --leadId)          lead_id="$2"; shift 2 ;;
      --message)         message="$2"; shift 2 ;;
      --messageThreadId) thread_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  [[ -z "$user_id" ]] && { echo '{"error":"--userId is required (usr_...)"}' >&2; exit 1; }
  [[ -z "$lead_id" ]] && { echo '{"error":"--leadId is required (ld_...)"}' >&2; exit 1; }
  [[ -z "$message" ]] && { echo '{"error":"--message is required"}' >&2; exit 1; }

  local body
  body=$(jq -n \
    --arg uid "$user_id" \
    --arg lid "$lead_id" \
    --arg msg "$message" \
    --arg tid "$thread_id" \
    '{userId: $uid, leadId: $lid, message: $msg}
     + (if $tid != "" then {messageThreadId: ($tid | tonumber)} else {} end)')

  _post "/v1/sms" "$body"
}

# ============================================================
# APPOINTMENTS
# ============================================================

cmd_appointments_list() {
  local page="" limit="" lead_id=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)   page="$2"; shift 2 ;;
      --limit)  limit="$2"; shift 2 ;;
      --leadId) lead_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  [[ -n "$lead_id" ]] && { [[ -n "$qs" ]] && qs="${qs}&leadId=${lead_id}" || qs="leadId=${lead_id}"; }
  _get "/v1/appointments${qs:+?$qs}"
}

# ============================================================
# ORGANIZATION
# ============================================================

cmd_org_get() {
  _get "/v1/organization"
}

cmd_org_availability() {
  _get "/v1/organization/availability"
}

cmd_org_members() {
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/organization/members${qs:+?$qs}"
}

cmd_org_services() {
  _get "/v1/organization/services"
}

cmd_org_products() {
  _get "/v1/organization/products"
}

# ============================================================
# MEMBERS
# ============================================================

cmd_members_list() {
  local page="" limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --page)  page="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done
  local qs; qs=$(_pagination_qs "$page" "$limit")
  _get "/v1/members${qs:+?$qs}"
}

# ============================================================
# MAIN ROUTER
# ============================================================

main() {
  [[ $# -lt 2 ]] && _usage

  local domain="$1" action="$2"; shift 2

  case "$domain" in
    leads)
      case "$action" in
        list)       cmd_leads_list "$@" ;;
        get)        cmd_leads_get "$@" ;;
        create)     cmd_leads_create "$@" ;;
        update)     cmd_leads_update "$@" ;;
        delete)     cmd_leads_delete "$@" ;;
        notes)      cmd_leads_notes "$@" ;;
        activities) cmd_leads_activities "$@" ;;
        *) echo "Unknown leads action: $action" >&2; _usage ;;
      esac
      ;;
    inquiries)
      case "$action" in
        list) cmd_inquiries_list "$@" ;;
        get)  cmd_inquiries_get "$@" ;;
        *) echo "Unknown inquiries action: $action" >&2; _usage ;;
      esac
      ;;
    faqs)
      case "$action" in
        list)   cmd_faqs_list "$@" ;;
        create) cmd_faqs_create "$@" ;;
        update) cmd_faqs_update "$@" ;;
        delete) cmd_faqs_delete "$@" ;;
        *) echo "Unknown faqs action: $action" >&2; _usage ;;
      esac
      ;;
    policies)
      case "$action" in
        list)   cmd_policies_list "$@" ;;
        create) cmd_policies_create "$@" ;;
        update) cmd_policies_update "$@" ;;
        delete) cmd_policies_delete "$@" ;;
        *) echo "Unknown policies action: $action" >&2; _usage ;;
      esac
      ;;
    calls)
      case "$action" in
        send) cmd_calls_send "$@" ;;
        *) echo "Unknown calls action: $action" >&2; _usage ;;
      esac
      ;;
    sms)
      case "$action" in
        send) cmd_sms_send "$@" ;;
        *) echo "Unknown sms action: $action" >&2; _usage ;;
      esac
      ;;
    appointments)
      case "$action" in
        list) cmd_appointments_list "$@" ;;
        *) echo "Unknown appointments action: $action" >&2; _usage ;;
      esac
      ;;
    org)
      case "$action" in
        get)          cmd_org_get ;;
        availability) cmd_org_availability ;;
        members)      cmd_org_members "$@" ;;
        services)     cmd_org_services ;;
        products)     cmd_org_products ;;
        *) echo "Unknown org action: $action" >&2; _usage ;;
      esac
      ;;
    members)
      case "$action" in
        list) cmd_members_list "$@" ;;
        *) echo "Unknown members action: $action" >&2; _usage ;;
      esac
      ;;
    *)
      _usage
      ;;
  esac
}

main "$@"
