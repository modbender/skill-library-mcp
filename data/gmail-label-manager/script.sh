#!/bin/bash
#
# Intelligent Gmail Manager Script - Personalized
# Automatically classifies and processes emails based on content patterns
# Handles payments, purchases, calendar events, absences, important contacts, etc.
#

set -euo pipefail

#==============================================================================
# CONFIGURATION
#==============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="${SCRIPT_DIR}/logs"
readonly LOG_FILE="${LOG_DIR}/gmail-label-log.txt"
readonly TELEGRAM_LOG="${LOG_DIR}/telegram-log.txt"
readonly DIGEST_FILE="${SCRIPT_DIR}/weekly-digest.txt"
readonly CONFIG_FILE="${SCRIPT_DIR}/config.json"
readonly MAX_EMAILS=1  # Process up to 1 unread emails per run (Increase later)

# Telegram configuration (set via environment variables)
readonly TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
readonly TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Label configuration
readonly LABEL_PREFIX="A_Personal,A_Work"
readonly REMOVE_LABELS="CATEGORY_UPDATES,CATEGORY_PROMOTIONS,UNREAD"

#==============================================================================
# FAMILY-SPECIFIC CONFIGURATION
#==============================================================================

# Children's names
declare -a CHILDREN_NAMES=("Kid1" "Kid2" "Kid3")
declare -a CHILDREN_FULL_NAMES=("Kid1 Lastname" "Kid2 Lastname" "Kid3 Lastname")

# Wife's names (including nickname)
declare -a WIFE_NAMES=("Wife's name")

# School information
readonly SCHOOL_NAME="School"
readonly SCHOOL_FULL_NAME="Elementary School"
readonly SCHOOL_DOMAIN="school.com"

# Work information
readonly WIFE_WORK="Work"
readonly WIFE_WORK_FULL="Workplace Name"
readonly WIFE_WORK_DOMAIN="work.com"

#==============================================================================
# HEALTH & INSURANCE CONFIGURATION
#==============================================================================

# Health Insurance
readonly HEALTH_INSURANCE="INS"
readonly SOCIAL_SECURITY_1="SS"

# Hospitals
declare -a HOSPITALS=("Hospital")
declare -a HOSPITAL_DOMAINS=("hospital.com")

# Insurance contacts
declare -a INSURANCE_CONTACTS=()

load_insurance_contacts() {
  if [ -f "$CONFIG_FILE" ]; then
    INSURANCE_CONTACTS=($(jq -r '.contacts.insurance[]?' "$CONFIG_FILE" 2>/dev/null || echo ""))
  fi

  # Default insurance contacts
  if [ ${#INSURANCE_CONTACTS[@]} -eq 0 ]; then
    INSURANCE_CONTACTS=(
      "@ss.com"
      "ss"
    )
  fi
}

#=============================================================================
# EMAIL CLASSIFICATION PATTERNS
#==============================================================================

# Define email patterns and their handlers
# Format: "pattern|handler_function|priority|description"
declare -A EMAIL_PATTERNS=(
  # Financial & Payments (High Priority)
  ["payment_confirmation"]="WOW Membership fee has been paid|handle_coupang_payment|high|Coupang WOW membership payment"
  ["card_transaction"]="card ending|handle_card_transaction|high|Credit/debit card transaction"
  ["bank_transfer"]="transfer.*completed|handle_bank_transfer|high|Bank transfer notification"
  ["payment_receipt"]="payment.*receipt|handle_payment_receipt|high|Payment receipt"
  ["invoice"]="invoice|handle_invoice|medium|Invoice received"
  ["subscription"]="subscription.*renewed|handle_subscription|medium|Subscription renewal"

  # Purchases & Deliveries (High Priority)
  ["order_confirmation"]="order.*confirmed|handle_order_confirmation|high|Order confirmation"
  ["shipment_tracking"]="shipped|tracking|handle_shipment|medium|Shipment notification"
  ["delivery_notification"]="delivered|arrived|handle_delivery|high|Delivery confirmation"
  ["delivery_schedule"]="delivery.*scheduled|handle_delivery_schedule|medium|Delivery scheduled"

  # School & Children (Critical Priority) - Enhanced for school
  ["school_absence"]="Absence Notification|handle_absence_notification|critical|school child absence notification"
  ["school_event"]="(school).*(event|meeting|conference)|handle_school_event|high|school school event"
  ["school_grade"]="grade.*report|academic.*progress|report card|handle_grade_report|high|school grade/academic report"
  ["school_announcement"]="(school).*announcement|handle_school_announcement|medium|school school announcement"
  ["school_homework"]="homework|assignment.*due|handle_homework|low|school homework reminder"
  ["school_attendance"]="attendance|tardy|late|handle_attendance|medium|school attendance notification"
  ["school_permission"]="permission.*slip|field.*trip|excursion|handle_permission_slip|high|school permission slip"
  ["school_parent_teacher"]="parent.*teacher.*conference|PTC|handle_parent_teacher|high|school parent-teacher conference"
  ["school_lunch"]="lunch.*menu|cafeteria|handle_school_lunch|low|school lunch information"
  ["school_discipline"]="behavior|discipline|incident|handle_discipline|critical|school discipline notification"

  # Wife's Work (High Priority)
  ["work_travel"]="business.*trip|travel.*approval|mission|handle_work_travel|high|Work travel notification"

  # Children-specific (Critical Priority)
  ["child_mentioned"]="(kid1|kid2|kid3)|handle_child_mention|high|Email mentioning children"
  ["wife_mentioned"]="(wifesname)|handle_wife_mention|high|Email mentioning wife"

  # Calendar & Events (Medium-High Priority)
  ["meeting_invitation"]="meeting.*invitation|invited.*you|handle_meeting_invitation|medium|Meeting invitation"
  ["event_reminder"]="event.*reminder|upcoming.*event|handle_event_reminder|medium|Event reminder"
  ["appointment_confirmation"]="appointment.*confirmed|handle_appointment|high|Appointment confirmation"
  ["reservation"]="reservation.*confirmed|booking.*confirmed|handle_reservation|high|Reservation/booking"

  # Family & VIP Contacts (Critical Priority)
  ["family_email"]="FAMILY_SENDER|handle_family_email|critical|Email from family member"
  ["vip_contact"]="VIP_SENDER|handle_vip_email|high|Email from VIP contact"

  # Bills & Utilities (Medium Priority)
  ["utility_bill"]="electricity.*bill|water.*bill|gas.*bill|handle_utility_bill|medium|Utility bill"
  ["phone_bill"]="mobile.*bill|phone.*bill|handle_phone_bill|medium|Phone bill"
  ["internet_bill"]="internet.*bill|broadband.*bill|handle_internet_bill|medium|Internet bill"

  # Health & Medical (High Priority)
  ["medical_appointment"]="medical.*appointment|doctor.*appointment|handle_medical_appointment|high|Medical appointment"
  ["prescription_ready"]="prescription.*ready|medication.*available|handle_prescription|high|Prescription ready"
  ["lab_results"]="lab.*results|test.*results|handle_lab_results|critical|Lab/test results"
  ["vaccination"]="vaccination|immunization|vaccine|handle_vaccination|high|Vaccination notification"

  # Travel (Medium-High Priority)
  ["flight_booking"]="flight.*confirmation|boarding.*pass|handle_flight_booking|high|Flight booking"
  ["hotel_reservation"]="hotel.*confirmation|accommodation|handle_hotel_reservation|medium|Hotel reservation"
  ["travel_itinerary"]="itinerary|travel.*plan|handle_travel_itinerary|medium|Travel itinerary"
  ["visa_passport"]="visa|passport|immigration|handle_visa_passport|high|Visa/passport notification"

  # Security & Alerts (Critical Priority)
  ["security_alert"]="security.*alert|suspicious.*activity|handle_security_alert|critical|Security alert"
  ["password_reset"]="password.*reset|verify.*account|handle_password_reset|high|Password reset"
  ["login_notification"]="new.*login|login.*detected|handle_login_notification|medium|Login notification"

#==============================================================================
# EMAIL CLASSIFICATION PATTERNS (Medical)
#==============================================================================

  # Health Insurance & Social Security (High Priority)
  ["dosz_insurance"]="(DOSZ|health insurance claim|insurance reimbursement)|handle_health_insurance|high|DOSZ health insurance"
  ["rsz_social"]="(Rsz|RSZ|social security contribution)|handle_social_security|high|Rsz social security"
  ["onss_social"]="(ONSS|rijksdienst|social security)|handle_social_security|high|ONSS social security"
  ["insurance_claim"]="claim.*approved|reimbursement.*processed|claim.*rejected|handle_insurance_claim|high|Insurance claim status"
  ["insurance_renewal"]="insurance.*renewal|policy.*expir|handle_insurance_renewal|high|Insurance renewal"
  ["insurance_card"]="insurance.*card|membership.*card|handle_insurance_card|medium|Insurance card notification"

  # Hospital & Medical (High Priority)
  ["bnh_hospital"]="(BNH|Bangkok Nursing Home)|handle_hospital_communication|high|BNH Hospital communication"
  ["samitivej_hospital"]="Samitivej|handle_hospital_communication|high|Samitivej Hospital communication"
  ["hospital_bill"]="hospital.*bill|medical.*invoice|treatment.*cost|handle_hospital_bill|critical|Hospital bill"
  ["test_results"]="test.*results|lab.*report|blood.*work|handle_test_results|critical|Medical test results"
  ["hospital_appointment"]="hospital.*appointment|clinic.*visit|follow.*up.*appointment|handle_hospital_appointment|high|Hospital appointment"
  ["surgery_schedule"]="surgery.*scheduled|operation.*date|procedure.*planned|handle_surgery_notification|critical|Surgery notification"
  ["discharge_summary"]="discharge.*summary|hospital.*discharge|treatment.*summary|handle_discharge_summary|high|Hospital discharge"
  ["medication_prescription"]="prescription|medication.*prescribed|pharmacy|handle_prescription_hospital|high|Hospital prescription"

  # Medical Emergency (Critical Priority)
  ["emergency_contact"]="emergency|urgent.*medical|immediate.*attention|handle_medical_emergency|critical|Medical emergency"
  ["vaccination_reminder"]="vaccination.*due|immunization.*reminder|vaccine.*schedule|handle_vaccination|high|Vaccination reminder"

  # Insurance Pre-approval (Critical Priority)
  ["pre_approval"]="pre-approval|pre-authorization|prior.*authorization|treatment.*approval|handle_pre_approval|critical|Insurance pre-approval"
  ["coverage_inquiry"]="coverage.*inquiry|benefits.*check|eligible.*treatment|handle_coverage_inquiry|medium|Coverage inquiry"
)

#==============================================================================
# CONTACT LISTS (Load from config or define here)
#==============================================================================

declare -a FAMILY_CONTACTS=()
declare -a VIP_CONTACTS=()
declare -a WORK_CONTACTS=()
declare -a SCHOOL_CONTACTS=()

load_contacts() {
  if [ -f "$CONFIG_FILE" ]; then
    FAMILY_CONTACTS=($(jq -r '.contacts.family[]?' "$CONFIG_FILE" 2>/dev/null || echo ""))
    VIP_CONTACTS=($(jq -r '.contacts.vip[]?' "$CONFIG_FILE" 2>/dev/null || echo ""))
    WORK_CONTACTS=($(jq -r '.contacts.work[]?' "$CONFIG_FILE" 2>/dev/null || echo ""))
    SCHOOL_CONTACTS=($(jq -r '.contacts.school[]?' "$CONFIG_FILE" 2>/dev/null || echo ""))
  fi

  # Default family contacts
  if [ ${#FAMILY_CONTACTS[@]} -eq 0 ]; then
    FAMILY_CONTACTS=(
      "dad@dad.com"
    )
  fi

  # Default VIP contacts
  if [ ${#VIP_CONTACTS[@]} -eq 0 ]; then
    VIP_CONTACTS=(
      "friend@gmail.com"
    )
  fi

  # School contacts (school)
  if [ ${#SCHOOL_CONTACTS[@]} -eq 0 ]; then
    SCHOOL_CONTACTS=(
      "@school.com"
      "office@school.com"
    )
  fi

  # Work contacts
  if [ ${#WORK_CONTACTS[@]} -eq 0 ]; then
    WORK_CONTACTS=(
      "@work.com"
    )
  fi
}

#==============================================================================
# INITIALIZATION
#==============================================================================

mkdir -p "$LOG_DIR"

for cmd in jq curl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: Required command '$cmd' is not installed" >&2
    exit 1
  fi
done

if ! command -v gog &>/dev/null; then
  echo "Error: 'gog' command not found. Please install the Google CLI tool." >&2
  exit 1
fi

# Load contact lists
load_contacts
# Load insurance contacts
load_insurance_contacts

#==============================================================================
# LOGGING FUNCTIONS
#==============================================================================

log() {
  local level="${1:-INFO}"
  shift
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$LOG_FILE"
}

log_error() { log "ERROR" "$@" >&2; }
log_warn() { log "WARN" "$@"; }
log_info() { log "INFO" "$@"; }
log_debug() { log "DEBUG" "$@"; }

#==============================================================================
# TELEGRAM FUNCTIONS
#==============================================================================

send_telegram() {
  local message="$1"
  local priority="${2:-normal}"  # critical, high, normal, low

  if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    log_warn "Telegram credentials not configured. Skipping notification."
    return 1
  fi

  # Add priority emoji
  local emoji=""
  case "$priority" in
    critical) emoji="" ;;
    high) emoji="⚠️" ;;
    normal) emoji="ℹ️" ;;
    low) emoji="" ;;
  esac

  local formatted_message="${emoji} ${message}"

  local response
  response=$(curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${formatted_message}" \
    --data-urlencode "parse_mode=HTML" 2>&1)

  local exit_code=$?
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${response}" >> "$TELEGRAM_LOG"

  if [ $exit_code -ne 0 ]; then
    log_error "Failed to send Telegram message"
    return 1
  fi

  log_info "Telegram notification sent (priority: $priority)"
  return 0
}

#==============================================================================
# DIGEST FUNCTIONS
#==============================================================================

add_to_digest() {
  local category="$1"
  local entry="$2"
  local priority="${3:-normal}"

  {
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${priority^^}]"
    echo "Category: $category"
    echo "$entry"
    echo "---"
  } >> "$DIGEST_FILE"
}

#==============================================================================
# CALENDAR FUNCTIONS
#==============================================================================

add_calendar_event() {
  local title="$1"
  local date="$2"
  local all_day="${3:-true}"
  local time="${4:-}"
  local description="${5:-}"

  log_info "Creating calendar event: $title on $date"

  local cmd="gog calendar event create --title \"$title\" --startDate \"$date\""

  if [ "$all_day" = "true" ]; then
    cmd="$cmd --allDay true"
  elif [ -n "$time" ]; then
    cmd="$cmd --startTime \"$time\""
  fi

  if [ -n "$description" ]; then
    cmd="$cmd --description \"$description\""
  fi

  local result
  result=$(eval "$cmd" 2>&1) || log_warn "Failed to create calendar event: $result"

  return 0
}

#==============================================================================
# EMAIL PROCESSING UTILITIES
#==============================================================================

get_unread_emails() {
  local unread_emails
  unread_emails=$(gog gmail messages search "is:unread" --max "$MAX_EMAILS" --json 2>&1)

  if [ $? -ne 0 ]; then
    log_error "Failed to search for unread emails: $unread_emails"
    return 1
  fi

  echo "$unread_emails"
}

extract_email_data() {
  local email_json="$1"
  local field="$2"

  local value
  value=$(echo "$email_json" | jq -r ".${field} // empty")
  echo "$value"
}

get_thread_content() {
  local thread_id="$1"

  local content
  content=$(gog gmail thread get "$thread_id" --full --json 2>&1)

  if [ $? -ne 0 ]; then
    log_error "Failed to get thread content: $content"
    echo ""
    return 1
  fi

  echo "$content"
}

apply_label() {
  local thread_id="$1"
  local label="$2"

  log_info "Applying label '$label' to thread $thread_id"

  local result
  result=$(gog gmail thread modify "$thread_id" --add "$label" 2>&1)

  if [ $? -ne 0 ]; then
    log_error "Failed to apply label: $result"
    return 1
  fi

  return 0
}

remove_labels() {
  local thread_id="$1"

  local result
  result=$(gog gmail thread modify "$thread_id" --remove "$REMOVE_LABELS" 2>&1)

  if [ $? -ne 0 ]; then
    log_warn "Failed to remove labels: $result"
    return 1
  fi

  return 0
}

archive_email() {
  local thread_id="$1"

  log_info "Archiving thread $thread_id"

  local result
  result=$(gog gmail thread modify "$thread_id" --remove INBOX 2>&1)

  if [ $? -ne 0 ]; then
    log_error "Failed to archive email: $result"
    return 1
  fi

  return 0
}

get_label_pattern() {
  local sender="$1"

  local archived_emails
  archived_emails=$(gog gmail messages search "is:archived from:\"${sender}\"" --max 20 --json 2>&1)

  if [ $? -ne 0 ]; then
    echo ""
    return 1
  fi

  local label_pattern
  label_pattern=$(echo "$archived_emails" | jq -r "
    [.messages[]? | .labels[]? | select(startswith(\"A_Personal\") or startswith(\"A_Work\"))]
    | group_by(.)
    | map({label: .[0], count: length})
    | sort_by(.count)
    | reverse
    | .[0].label // empty
  ")

  echo "$label_pattern"
}

#==============================================================================
# EMAIL CLASSIFICATION
#==============================================================================

check_sender_category() {
  local sender="$1"

  # Check if sender is from school (school)
  for contact in "${SCHOOL_CONTACTS[@]}"; do
    if [[ "$sender" =~ $contact ]]; then
      echo "school"
      return 0
    fi
  done

  # Check if sender is family
  for contact in "${FAMILY_CONTACTS[@]}"; do
    if [[ "$sender" =~ $contact ]]; then
      echo "family"
      return 0
    fi
  done

  # Check if sender is VIP
  for contact in "${VIP_CONTACTS[@]}"; do
    if [[ "$sender" =~ $contact ]]; then
      echo "vip"
      return 0
    fi
  done

  # Check if sender is work-related
  for contact in "${WORK_CONTACTS[@]}"; do
    if [[ "$sender" =~ $contact ]]; then
      echo "work"
      return 0
    fi
  done

  echo "unknown"
}

check_family_mention() {
  local text="$1"

  # Check for children's names
  for child in "${CHILDREN_NAMES[@]}"; do
    if echo "$text" | grep -qiE "\b${child}\b"; then
      echo "$child"
      return 0
    fi
  done

  # Check for wife's names
  for name in "${WIFE_NAMES[@]}"; do
    if echo "$text" | grep -qiE "\b${name}\b"; then
      echo "Wife's Name"
      return 0
    fi
  done

  echo ""
}

classify_email() {
  local subject="$1"
  local sender="$2"
  local content="$3"

  local matches=()
  local combined_text="${subject} ${content}"

  # Check sender category first
  local sender_category
  sender_category=$(check_sender_category "$sender")

  # Prioritize school emails from school
  if [ "$sender_category" = "school" ]; then
    matches+=("school_email:critical")
    log_debug "Email from school detected"
  fi

  if [ "$sender_category" = "family" ]; then
    matches+=("family_email:critical")
  elif [ "$sender_category" = "vip" ]; then
    matches+=("vip_contact:high")
  elif [ "$sender_category" = "work" ]; then
    matches+=("work:high")
  fi

  # Check for family member mentions
  local family_mention
  family_mention=$(check_family_mention "$combined_text")
  if [ -n "$family_mention" ]; then
    log_debug "Family member mentioned: $family_mention"
    matches+=("child_mentioned:high")
  fi

  # Check content patterns
  for pattern_key in "${!EMAIL_PATTERNS[@]}"; do
    local pattern_data="${EMAIL_PATTERNS[$pattern_key]}"
    IFS='|' read -r pattern handler priority description <<< "$pattern_data"

    # Skip special sender patterns (already handled above)
    if [ "$pattern" = "FAMILY_SENDER" ] || [ "$pattern" = "VIP_SENDER" ]; then
      continue
    fi

    # Check if pattern matches (case-insensitive)
    if echo "$combined_text" | grep -qiE "$pattern"; then
      matches+=("${pattern_key}:${priority}")
      log_debug "Pattern matched: $pattern_key ($description)"
    fi
  done

  # Return all matches as JSON array
  if [ ${#matches[@]} -gt 0 ]; then
    printf '%s\n' "${matches[@]}" | jq -R . | jq -s .
  else
    echo "[]"
  fi
}

#==============================================================================
# CONTENT EXTRACTION UTILITIES
#==============================================================================

extract_amount() {
  local text="$1"

  # Try different currency formats

  if [ -z "$amount" ]; then
    # USD: $1,234.56
    amount=$(echo "$text" | grep -oP '\$\s*[0-9,]+\.?[0-9]*' | head -n 1 | tr -d '$ ' | tr -d ',')
  fi

  if [ -z "$amount" ]; then
    # Euro: €1,234.56
    amount=$(echo "$text" | grep -oP '€\s*[0-9,]+\.?[0-9]*' | head -n 1 | tr -d '€ ' | tr -d ',')
  fi

  if [ -z "$amount" ]; then
    # Generic number with currency keyword
    amount=$(echo "$text" | grep -oiP '(amount|total|price|cost).*?[0-9,]+\.?[0-9]*' | grep -oP '[0-9,]+\.?[0-9]*' | head -n 1 | tr -d ',')
  fi

  echo "$amount"
}

extract_date() {
  local text="$1"
  local format="${2:-any}"  # any, iso, natural

  local date_found=""

  case "$format" in
    iso)
      # ISO format: 2025-01-15
      date_found=$(echo "$text" | grep -oP '\d{4}-\d{2}-\d{2}' | head -n 1)
      ;;
    natural)
      # Natural language: January 15, 2025 or 15 January 2025
      date_found=$(echo "$text" | grep -oP '(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}' | head -n 1)
      ;;
    *)
      # Try ISO first
      date_found=$(echo "$text" | grep -oP '\d{4}-\d{2}-\d{2}' | head -n 1)

      # Try natural language if ISO not found
      if [ -z "$date_found" ]; then
        date_found=$(echo "$text" | grep -oP '(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}' | head -n 1)
      fi

      # Try day name format: Thursday, February 13
      if [ -z "$date_found" ]; then
        date_found=$(echo "$text" | grep -oP '(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}' | head -n 1)
      fi
      ;;
  esac

  echo "$date_found"
}

extract_time() {
  local text="$1"

  # Extract time in various formats: 14:30, 2:30 PM, 2:30pm
  local time_found
  time_found=$(echo "$text" | grep -oiP '\d{1,2}:\d{2}\s*(AM|PM|am|pm)?' | head -n 1)

  echo "$time_found"
}

extract_tracking_number() {
  local text="$1"

  # Common tracking number patterns
  local tracking

  # Generic alphanumeric tracking (8-20 chars)
  tracking=$(echo "$text" | grep -oP '(tracking|shipment|parcel).*?([A-Z0-9]{8,20})' | grep -oP '[A-Z0-9]{8,20}' | head -n 1)

  echo "$tracking"
}

extract_child_name() {
  local text="$1"

  # Check which child is mentioned
  for child in "${CHILDREN_NAMES[@]}"; do
    if echo "$text" | grep -qiE "\b${child}\b"; then
      echo "$child"
      return 0
    fi
  done

  # Check full names as fallback
  for child_full in "${CHILDREN_FULL_NAMES[@]}"; do
    if echo "$text" | grep -qiE "${child_full}"; then
      # Extract first name
      echo "$child_full" | awk '{print $1}'
      return 0
    fi
  done

  echo ""
}

#==============================================================================
# EMAIL CONTENT HANDLERS - Family/Professional/...
#==============================================================================

# NEW HANDLERS FOR FAMILY-SPECIFIC CONTENT

handle_child_mention() {
  local email_content="$1"
  local subject="$2"
  local sender="$3"

  local child_name
  child_name=$(extract_child_name "$email_content $subject")

  log_info "Processing email mentioning child: ${child_name:-one of the children}"

  local sender_name
  sender_name=$(echo "$sender" | grep -oP '^[^<]+' | xargs)

  local preview
  preview=$(echo "$email_content" | head -c 300)

  local telegram_message="<b> Child Mentioned: ${child_name:-Children}</b>

<b>From:</b> ${sender_name}
<b>Subject:</b> ${subject}

<b>Preview:</b> ${preview}...

 Check email - may require attention"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Child Mentioned: ${child_name:-Children}]
From: ${sender_name}
Subject: ${subject}
Action: Review email content"

  add_to_digest "Family/Children" "$digest_entry" "high"

  return 0
}

handle_wife_mention() {
  local email_content="$1"
  local subject="$2"
  local sender="$3"

  log_info "Processing email mentioning wife"

  local sender_name
  sender_name=$(echo "$sender" | grep -oP '^[^<]+' | xargs)

  local preview
  preview=$(echo "$email_content" | head -c 300)

  local telegram_message="<b> Wife Mentioned</b>

<b>From:</b> ${sender_name}
<b>Subject:</b> ${subject}

<b>Preview:</b> ${preview}...

 May be work-related or personal matter"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Wife Mentioned]
From: ${sender_name}
Subject: ${subject}
Action: Review email content"

  add_to_digest "Family/Spouse" "$digest_entry" "high"

  return 0
}

handle_work() {
  local email_content="$1"
  local subject="$2"
  local sender="$3"

  log_info "Processing work-related email"

  local sender_name
  sender_name=$(echo "$sender" | grep -oP '^[^<]+' | xargs)

  local preview
  preview=$(echo "$email_content" | head -c 300)

  local telegram_message="<b> Work Email</b>

<b>From:</b> ${sender_name}
<b>Subject:</b> ${subject}

<b>Preview:</b> ${preview}...

 Related to wife's work"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Work Email]
From: ${sender_name}
Subject: ${subject}
Action: May require wife's attention"

  add_to_digest "Work" "$digest_entry" "high"

  return 0
}

handle_attendance() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school attendance notification"

  local child_name
  local attendance_date
  local reason

  child_name=$(extract_child_name "$email_content")
  attendance_date=$(extract_date "$email_content")
  reason=$(echo "$email_content" | grep -oiP "(tardy|late|absent).*?reason[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  local telegram_message="<b> school Attendance Alert</b>

<b>Child:</b> ${child_name:-Unknown}
<b>Date:</b> ${attendance_date:-$(date '+%Y-%m-%d')}
<b>Reason:</b> ${reason:-See email}

⚠️ Review attendance notification from School"

  send_telegram "$telegram_message" "high"

  local digest_entry="[school Attendance]
Child: ${child_name:-Unknown}
Date: ${attendance_date:-$(date '+%Y-%m-%d')}
Reason: ${reason:-See email}
Action: Review and follow up if needed"

  add_to_digest "School/school/Attendance" "$digest_entry" "high"

  return 0
}

handle_permission_slip() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school permission slip"

  local child_name
  local event_name
  local event_date
  local deadline

  child_name=$(extract_child_name "$email_content")
  event_name=$(echo "$subject" | sed 's/permission.*slip//i' | xargs)
  event_date=$(extract_date "$email_content")
  deadline=$(echo "$email_content" | grep -oiP "deadline[: ]*\K.*" | head -n 1 | xargs)

  local telegram_message="<b> school Permission Slip Required</b>

<b>Child:</b> ${child_name:-Unknown}
<b>Event:</b> ${event_name}
<b>Event Date:</b> ${event_date:-TBD}
<b>Deadline:</b> ${deadline:-ASAP}

⚠️ <b>ACTION REQUIRED:</b> Sign and return permission slip"

  send_telegram "$telegram_message" "critical"

  local digest_entry="[school Permission Slip]
Child: ${child_name:-Unknown}
Event: ${event_name}
Event Date: ${event_date:-TBD}
Deadline: ${deadline:-ASAP}
Action: URGENT - Sign and return"

  add_to_digest "School/school/PermissionSlip" "$digest_entry" "critical"

  if [ -n "$deadline" ]; then
    add_calendar_event "school Permission Slip Due: ${event_name}" "$deadline" true "" "Child: ${child_name}. Event: ${event_date}"
  fi

  return 0
}

handle_parent_teacher() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school parent-teacher conference"

  local child_name
  local conference_date
  local conference_time
  local teacher

  child_name=$(extract_child_name "$email_content")
  conference_date=$(extract_date "$email_content")
  conference_time=$(extract_time "$email_content")
  teacher=$(echo "$email_content" | grep -oiP "teacher[: ]*\K[A-Z][a-z]+ [A-Z][a-z]+" | head -n 1)

  local telegram_message="<b>‍ school Parent-Teacher Conference</b>

<b>Child:</b> ${child_name:-Unknown}
<b>Teacher:</b> ${teacher:-TBD}
<b>Date:</b> ${conference_date:-TBD}
<b>Time:</b> ${conference_time:-TBD}

 Mark your calendar!"

  send_telegram "$telegram_message" "high"

  local digest_entry="[school Parent-Teacher Conference]
Child: ${child_name:-Unknown}
Teacher: ${teacher:-TBD}
Date: ${conference_date:-TBD}
Time: ${conference_time:-TBD}
Action: Attend conference"

  add_to_digest "School/school/ParentTeacher" "$digest_entry" "high"

  if [ -n "$conference_date" ]; then
    local all_day="false"
    if [ -z "$conference_time" ]; then
      all_day="true"
    fi
    add_calendar_event "school Parent-Teacher: ${child_name}" "$conference_date" "$all_day" "$conference_time" "Teacher: ${teacher}"
  fi

  return 0
}

handle_school_lunch() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school lunch information"

  # Low priority - just log it
  local digest_entry="[school Lunch Menu]
Subject: ${subject}
Action: Review if interested"

  add_to_digest "School/school/Lunch" "$digest_entry" "low"

  return 0
}

handle_discipline() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school discipline notification"

  local child_name
  local incident_date
  local description

  child_name=$(extract_child_name "$email_content")
  incident_date=$(extract_date "$email_content")
  description=$(echo "$email_content" | grep -oiP "(incident|behavior)[: ]*\K[^.\n]{10,100}" | head -n 1 | xargs)

  local telegram_message="<b> school DISCIPLINE NOTIFICATION</b>

<b>Child:</b> ${child_name:-Unknown}
<b>Date:</b> ${incident_date:-$(date '+%Y-%m-%d')}
<b>Description:</b> ${description:-See email}

⚠️ <b>URGENT:</b> Review immediately and discuss with ${child_name}"

  send_telegram "$telegram_message" "critical"

  local digest_entry="[school DISCIPLINE ALERT]
Child: ${child_name:-Unknown}
Date: ${incident_date:-$(date '+%Y-%m-%d')}
Description: ${description:-See email}
Action: URGENT - Review and discuss"

  add_to_digest "School/school/Discipline" "$digest_entry" "critical"

  return 0
}

handle_work_travel() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing work travel notification"

  local destination
  local travel_dates
  local purpose

  destination=$(echo "$email_content" | grep -oiP "(destination|traveling to)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  travel_dates=$(extract_date "$email_content")
  purpose=$(echo "$email_content" | grep -oiP "(purpose|reason)[: ]*\K[^.\n]{10,100}" | head -n 1 | xargs)

  local telegram_message="<b>✈️ Work Travel Notification</b>

<b>Destination:</b> ${destination:-See email}
<b>Dates:</b> ${travel_dates:-TBD}
<b>Purpose:</b> ${purpose:-See email}

 Plan accordingly for work travel"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Work Travel]
Destination: ${destination:-See email}
Dates: ${travel_dates:-TBD}
Purpose: ${purpose:-See email}
Action: Coordinate family schedule"

  add_to_digest "Work/Travel" "$digest_entry" "high"

  if [ -n "$travel_dates" ]; then
    add_calendar_event "Work Travel: ${destination}" "$travel_dates" true "" "Purpose: ${purpose}"
  fi

  return 0
}

handle_vaccination() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing vaccination notification"

  local patient
  local vaccine_type
  local appointment_date
  local location

  patient=$(extract_child_name "$email_content")
  if [ -z "$patient" ]; then
    patient=$(echo "$email_content" | grep -oiP "(patient|for)[: ]*\K[A-Z][a-z]+ [A-Z][a-z]+" | head -n 1)
  fi
  vaccine_type=$(echo "$email_content" | grep -oiP "(vaccine|immunization)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  appointment_date=$(extract_date "$email_content")
  location=$(echo "$email_content" | grep -oiP "(location|clinic)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  local telegram_message="<b> Vaccination Notification</b>

<b>Patient:</b> ${patient:-Unknown}
<b>Vaccine:</b> ${vaccine_type:-See email}
<b>Date:</b> ${appointment_date:-TBD}
<b>Location:</b> ${location:-TBD}

 Schedule vaccination appointment"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Vaccination]
Patient: ${patient:-Unknown}
Vaccine: ${vaccine_type:-See email}
Date: ${appointment_date:-TBD}
Location: ${location:-TBD}
Action: Confirm appointment"

  add_to_digest "Health/Vaccination" "$digest_entry" "high"

  if [ -n "$appointment_date" ]; then
    add_calendar_event "Vaccination: ${patient}" "$appointment_date" true "" "Vaccine: ${vaccine_type}. Location: ${location}"
  fi

  return 0
}

handle_visa_passport() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing visa/passport notification"

  local document_type
  local person
  local expiry_date
  local status

  document_type=$(echo "$subject $email_content" | grep -oiP "(visa|passport)" | head -n 1)
  person=$(extract_child_name "$email_content")
  if [ -z "$person" ]; then
    person=$(check_family_mention "$email_content")
  fi
  expiry_date=$(echo "$email_content" | grep -oiP "(expir|valid until)[: ]*\K.*" | head -n 1 | xargs)
  status=$(echo "$email_content" | grep -oiP "(status|application)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  local telegram_message="<b> ${document_type^^} Notification</b>

<b>Person:</b> ${person:-Family}
<b>Status:</b> ${status:-See email}
<b>Expiry:</b> ${expiry_date:-TBD}

⚠️ Keep track of travel document status"

  send_telegram "$telegram_message" "high"

  local digest_entry="[${document_type^^} Notification]
Person: ${person:-Family}
Status: ${status:-See email}
Expiry: ${expiry_date:-TBD}
Action: Monitor and renew if needed"

  add_to_digest "Travel/Documents" "$digest_entry" "high"

  if [ -n "$expiry_date" ]; then
    add_calendar_event "${document_type^^} Expiry: ${person}" "$expiry_date" true "" "Renew before expiration"
  fi

  return 0
}

#==============================================================================
# EMAIL CONTENT HANDLERS
#==============================================================================

# FINANCIAL HANDLERS

handle_coupang_payment() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing Coupang WOW membership payment"

  local payment_amount
  local payment_method
  local membership_period

  payment_amount=$(extract_amount "$email_content")
  payment_method=$(echo "$email_content" | grep -oP "Payment method[: ]*\K.*" | head -n 1 | xargs)
  membership_period=$(echo "$email_content" | grep -oP "Membership period[: ]*\K.*" | head -n 1 | xargs)

  if [ -z "$payment_amount" ]; then
    log_warn "Failed to extract payment amount from Coupang email"
    return 1
  fi

  local telegram_message="<b> Coupang WOW Membership Payment</b>

<b>Amount:</b> ₩${payment_amount}
<b>Method:</b> ${payment_method:-N/A}
<b>Period:</b> ${membership_period:-N/A}
<b>Date:</b> $(date '+%Y-%m-%d %H:%M')"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Coupang WOW Membership Payment]
Amount: ₩${payment_amount}
Method: ${payment_method:-N/A}
Period: ${membership_period:-N/A}
Date: $(date '+%Y-%m-%d')"

  add_to_digest "Financial/Subscription" "$digest_entry" "high"

  return 0
}

handle_card_transaction() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing card transaction notification"

  local amount card_last_four merchant transaction_date

  amount=$(extract_amount "$email_content")
  card_last_four=$(echo "$email_content" | grep -oP "card ending (in )?\K\d{4}" | head -n 1)
  merchant=$(echo "$email_content" | grep -oiP "(at|merchant|store)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  transaction_date=$(extract_date "$email_content")

  if [ -z "$amount" ]; then
    log_warn "Failed to extract transaction amount"
    return 1
  fi

  local telegram_message="<b> Card Transaction</b>

<b>Amount:</b> ₩${amount}
<b>Card:</b> •••• ${card_last_four:-Unknown}
<b>Merchant:</b> ${merchant:-Unknown}
<b>Date:</b> ${transaction_date:-$(date '+%Y-%m-%d')}"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Card Transaction]
Amount: ₩${amount}
Card: •••• ${card_last_four:-Unknown}
Merchant: ${merchant:-Unknown}
Date: ${transaction_date:-$(date '+%Y-%m-%d')}"

  add_to_digest "Financial/Transaction" "$digest_entry" "high"

  return 0
}

handle_bank_transfer() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing bank transfer notification"

  local amount recipient account_from transfer_date

  amount=$(extract_amount "$email_content")
  recipient=$(echo "$email_content" | grep -oiP "(to|recipient|beneficiary)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  account_from=$(echo "$email_content" | grep -oP "from.*?account.*?\K\d{4,}" | head -n 1)
  transfer_date=$(extract_date "$email_content")

  local telegram_message="<b> Bank Transfer Completed</b>

<b>Amount:</b> ₩${amount:-Unknown}
<b>To:</b> ${recipient:-Unknown}
<b>From Account:</b> •••• ${account_from:-Unknown}
<b>Date:</b> ${transfer_date:-$(date '+%Y-%m-%d')}"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Bank Transfer]
Amount: ₩${amount:-Unknown}
To: ${recipient:-Unknown}
From: •••• ${account_from:-Unknown}
Date: ${transfer_date:-$(date '+%Y-%m-%d')}"

  add_to_digest "Financial/Transfer" "$digest_entry" "high"

  return 0
}

handle_payment_receipt() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing payment receipt"

  local amount merchant payment_date payment_method

  amount=$(extract_amount "$email_content")
  merchant=$(echo "$subject $email_content" | grep -oiP "(from|merchant|store|company)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  payment_date=$(extract_date "$email_content")
  payment_method=$(echo "$email_content" | grep -oiP "(payment method|paid (with|by))[: ]*\K[^.\n]{3,30}" | head -n 1 | xargs)

  local telegram_message="<b>茶 Payment Receipt</b>

<b>Merchant:</b> ${merchant:-Unknown}
<b>Amount:</b> ₩${amount:-Unknown}
<b>Method:</b> ${payment_method:-Unknown}
<b>Date:</b> ${payment_date:-$(date '+%Y-%m-%d')}"

  send_telegram "$telegram_message" "normal"

  local digest_entry="[Payment Receipt]
Merchant: ${merchant:-Unknown}
Amount: ₩${amount:-Unknown}
Method: ${payment_method:-Unknown}
Date: ${payment_date:-$(date '+%Y-%m-%d')}"

  add_to_digest "Financial/Receipt" "$digest_entry" "normal"

  return 0
}

handle_invoice() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing invoice"

  local invoice_number amount due_date vendor

  invoice_number=$(echo "$email_content" | grep -oiP "invoice (number|#)[: ]*\K[A-Z0-9-]+" | head -n 1)
  amount=$(extract_amount "$email_content")
  due_date=$(echo "$email_content" | grep -oiP "due (date|by)[: ]*\K.*" | head -n 1 | xargs)
  vendor=$(echo "$subject $email_content" | grep -oiP "(from|vendor|company)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  local telegram_message="<b> Invoice Received</b>

<b>Vendor:</b> ${vendor:-Unknown}
<b>Invoice #:</b> ${invoice_number:-Unknown}
<b>Amount:</b> ₩${amount:-Unknown}
<b>Due Date:</b> ${due_date:-Not specified}

⚠️ Remember to pay before due date!"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Invoice Received]
Vendor: ${vendor:-Unknown}
Invoice #: ${invoice_number:-Unknown}
Amount: ₩${amount:-Unknown}
Due Date: ${due_date:-Not specified}
Action: Review and schedule payment"

  add_to_digest "Financial/Invoice" "$digest_entry" "medium"

  # Add calendar reminder for due date if available
  if [ -n "$due_date" ]; then
    add_calendar_event "Invoice Payment Due: ${vendor}" "$due_date" true "" "Invoice #${invoice_number} - Amount: ₩${amount}"
  fi

  return 0
}

handle_subscription() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing subscription renewal"

  local service amount renewal_date next_billing

  service=$(echo "$subject" | grep -oiP '^[^-:]+' | head -n 1 | xargs)
  amount=$(extract_amount "$email_content")
  renewal_date=$(extract_date "$email_content")
  next_billing=$(echo "$email_content" | grep -oiP "next billing[: ]*\K.*" | head -n 1 | xargs)

  local telegram_message="<b> Subscription Renewed</b>

<b>Service:</b> ${service:-Unknown}
<b>Amount:</b> ₩${amount:-Unknown}
<b>Renewal Date:</b> ${renewal_date:-$(date '+%Y-%m-%d')}
<b>Next Billing:</b> ${next_billing:-Not specified}"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Subscription Renewal]
Service: ${service:-Unknown}
Amount: ₩${amount:-Unknown}
Renewed: ${renewal_date:-$(date '+%Y-%m-%d')}
Next Billing: ${next_billing:-Not specified}"

  add_to_digest "Financial/Subscription" "$digest_entry" "medium"

  return 0
}

# PURCHASE & DELIVERY HANDLERS

handle_order_confirmation() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing order confirmation"

  local order_number amount items estimated_delivery merchant

  order_number=$(echo "$email_content" | grep -oiP "order (number|#|id)[: ]*\K[A-Z0-9-]+" | head -n 1)
  amount=$(extract_amount "$email_content")
  items=$(echo "$email_content" | grep -oiP "item(s)?[: ]*\K[^.\n]{3,100}" | head -n 1 | xargs)
  estimated_delivery=$(extract_date "$email_content")
  merchant=$(echo "$subject" | grep -oP '^[^-:]+' | head -n 1 | xargs)

  local telegram_message="<b> Order Confirmed</b>

<b>Merchant:</b> ${merchant:-Unknown}
<b>Order #:</b> ${order_number:-Unknown}
<b>Amount:</b> ₩${amount:-Unknown}
<b>Items:</b> ${items:-See email}
<b>Est. Delivery:</b> ${estimated_delivery:-TBD}"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Order Confirmation]
Merchant: ${merchant:-Unknown}
Order #: ${order_number:-Unknown}
Amount: ₩${amount:-Unknown}
Items: ${items:-See email}
Est. Delivery: ${estimated_delivery:-TBD}"

  add_to_digest "Shopping/Order" "$digest_entry" "high"

  # Add calendar event for estimated delivery
  if [ -n "$estimated_delivery" ]; then
    add_calendar_event "Delivery Expected: ${merchant}" "$estimated_delivery" true "" "Order #${order_number}"
  fi

  return 0
}

handle_shipment() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing shipment notification"

  local tracking_number carrier estimated_delivery order_number

  tracking_number=$(extract_tracking_number "$email_content")
  carrier=$(echo "$email_content" | grep -oiP "(carrier|shipped via|courier)[: ]*\K[^.\n]{3,30}" | head -n 1 | xargs)
  estimated_delivery=$(extract_date "$email_content")
  order_number=$(echo "$email_content" | grep -oiP "order (number|#|id)[: ]*\K[A-Z0-9-]+" | head -n 1)

  local telegram_message="<b> Package Shipped</b>

<b>Order #:</b> ${order_number:-Unknown}
<b>Tracking:</b> ${tracking_number:-Not available}
<b>Carrier:</b> ${carrier:-Unknown}
<b>Est. Delivery:</b> ${estimated_delivery:-TBD}"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Package Shipped]
Order #: ${order_number:-Unknown}
Tracking: ${tracking_number:-Not available}
Carrier: ${carrier:-Unknown}
Est. Delivery: ${estimated_delivery:-TBD}"

  add_to_digest "Shopping/Shipment" "$digest_entry" "medium"

  return 0
}

handle_delivery() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing delivery confirmation"

  local order_number delivery_location delivery_time

  order_number=$(echo "$email_content" | grep -oiP "order (number|#|id)[: ]*\K[A-Z0-9-]+" | head -n 1)
  delivery_location=$(echo "$email_content" | grep -oiP "delivered (to|at)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  delivery_time=$(extract_time "$email_content")

  local telegram_message="<b>✅ Package Delivered</b>

<b>Order #:</b> ${order_number:-Unknown}
<b>Location:</b> ${delivery_location:-Your address}
<b>Time:</b> ${delivery_time:-$(date '+%H:%M')}
<b>Date:</b> $(date '+%Y-%m-%d')

 Check your ${delivery_location:-doorstep}!"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Package Delivered]
Order #: ${order_number:-Unknown}
Location: ${delivery_location:-Your address}
Delivered: $(date '+%Y-%m-%d %H:%M')"

  add_to_digest "Shopping/Delivery" "$digest_entry" "high"

  return 0
}

handle_delivery_schedule() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing delivery schedule"

  local order_number delivery_date delivery_time_window

  order_number=$(echo "$email_content" | grep -oiP "order (number|#|id)[: ]*\K[A-Z0-9-]+" | head -n 1)
  delivery_date=$(extract_date "$email_content")
  delivery_time_window=$(echo "$email_content" | grep -oiP "between[: ]*\K\d{1,2}:\d{2}.*?and.*?\d{1,2}:\d{2}" | head -n 1)

  local telegram_message="<b> Delivery Scheduled</b>

<b>Order #:</b> ${order_number:-Unknown}
<b>Date:</b> ${delivery_date:-TBD}
<b>Time Window:</b> ${delivery_time_window:-All day}

⏰ Be available to receive package!"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Delivery Scheduled]
Order #: ${order_number:-Unknown}
Date: ${delivery_date:-TBD}
Time: ${delivery_time_window:-All day}
Action: Be available"

  add_to_digest "Shopping/Delivery" "$digest_entry" "medium"

  if [ -n "$delivery_date" ]; then
    add_calendar_event "Package Delivery: Order #${order_number}" "$delivery_date" true "" "Time window: ${delivery_time_window:-All day}"
  fi

  return 0
}

# SCHOOL & CHILDREN HANDLERS

handle_absence_notification() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing absence notification"

  local absence_date absence_child reason

  absence_date=$(extract_date "$email_content")
  absence_child=$(echo "$email_content" | grep -oP "Your child, \K[A-Za-z ]+" | xargs)
  reason=$(echo "$email_content" | grep -oiP "reason[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  if [ -z "$absence_date" ] || [ -z "$absence_child" ]; then
    log_warn "Failed to extract absence details"
    return 1
  fi

  local telegram_message="<b> Absence Notification</b>

<b>Child:</b> ${absence_child}
<b>Date:</b> ${absence_date}
<b>Reason:</b> ${reason:-Not specified}

⚠️ <b>Action Required:</b> Provide excusal note on ManageBac"

  send_telegram "$telegram_message" "critical"

  local digest_entry="[School Absence]
Child: ${absence_child}
Date: ${absence_date}
Reason: ${reason:-Not specified}
Action: Submit excusal note on ManageBac"

  add_to_digest "School/Absence" "$digest_entry" "critical"

  add_calendar_event "Absence: ${absence_child}" "$absence_date" true "" "Reason: ${reason:-Not specified}. Submit excusal note."

  return 0
}

handle_school_event() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school event"

  local event_name event_date event_time location child_name

  event_name=$(echo "$subject" | xargs)
  event_date=$(extract_date "$email_content")
  event_time=$(extract_time "$email_content")
  location=$(echo "$email_content" | grep -oiP "(location|venue|at)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  child_name=$(echo "$email_content" | grep -oiP "(student|child)'s name[: ]*\K[A-Za-z ]+" | head -n 1 | xargs)

  local telegram_message="<b> School Event</b>

<b>Event:</b> ${event_name}
<b>Date:</b> ${event_date:-TBD}
<b>Time:</b> ${event_time:-TBD}
<b>Location:</b> ${location:-School}
<b>Student:</b> ${child_name:-All children}

 Mark your calendar!"

  send_telegram "$telegram_message" "high"

  local digest_entry="[School Event]
Event: ${event_name}
Date: ${event_date:-TBD}
Time: ${event_time:-TBD}
Location: ${location:-School}
Student: ${child_name:-All children}"

  add_to_digest "School/Event" "$digest_entry" "high"

  if [ -n "$event_date" ]; then
    local all_day="true"
    if [ -n "$event_time" ]; then
      all_day="false"
    fi
    add_calendar_event "${event_name}" "$event_date" "$all_day" "$event_time" "Location: ${location:-School}"
  fi

  return 0
}

handle_grade_report() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing grade report"

  local student_name report_period report_date

  student_name=$(echo "$email_content" | grep -oiP "(student|child)'s name[: ]*\K[A-Za-z ]+" | head -n 1 | xargs)
  report_period=$(echo "$email_content" | grep -oiP "(semester|quarter|term)[: ]*\K[^.\n]{3,30}" | head -n 1 | xargs)
  report_date=$(extract_date "$email_content")

  local telegram_message="<b> Grade Report Available</b>

<b>Student:</b> ${student_name:-Unknown}
<b>Period:</b> ${report_period:-Current}
<b>Date:</b> ${report_date:-$(date '+%Y-%m-%d')}

 Review grades and discuss with ${student_name:-your child}"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Grade Report]
Student: ${student_name:-Unknown}
Period: ${report_period:-Current}
Date: ${report_date:-$(date '+%Y-%m-%d')}
Action: Review and discuss"

  add_to_digest "School/Grades" "$digest_entry" "high"

  return 0
}

handle_school_announcement() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing school announcement"

  local announcement_title announcement_date

  announcement_title=$(echo "$subject" | xargs)
  announcement_date=$(extract_date "$email_content")

  local telegram_message="<b> School Announcement</b>

<b>Subject:</b> ${announcement_title}
<b>Date:</b> ${announcement_date:-$(date '+%Y-%m-%d')}

 Check email for full details"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[School Announcement]
Subject: ${announcement_title}
Date: ${announcement_date:-$(date '+%Y-%m-%d')}
Action: Review email"

  add_to_digest "School/Announcement" "$digest_entry" "medium"

  return 0
}

handle_homework() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing homework reminder"

  local assignment_name due_date subject_area student_name

  assignment_name=$(echo "$subject" | xargs)
  due_date=$(extract_date "$email_content")
  subject_area=$(echo "$email_content" | grep -oiP "(subject|course)[: ]*\K[^.\n]{3,30}" | head -n 1 | xargs)
  student_name=$(echo "$email_content" | grep -oiP "(student|child)'s name[: ]*\K[A-Za-z ]+" | head -n 1 | xargs)

  local telegram_message="<b> Homework Reminder</b>

<b>Assignment:</b> ${assignment_name}
<b>Subject:</b> ${subject_area:-Unknown}
<b>Student:</b> ${student_name:-Unknown}
<b>Due:</b> ${due_date:-ASAP}

✏️ Help ${student_name:-your child} complete on time"

  send_telegram "$telegram_message" "low"

  local digest_entry="[Homework]
Assignment: ${assignment_name}
Subject: ${subject_area:-Unknown}
Student: ${student_name:-Unknown}
Due: ${due_date:-ASAP}"

  add_to_digest "School/Homework" "$digest_entry" "low"

  if [ -n "$due_date" ]; then
    add_calendar_event "Homework Due: ${assignment_name}" "$due_date" true "" "Subject: ${subject_area}"
  fi

  return 0
}

# CALENDAR & EVENT HANDLERS

handle_meeting_invitation() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing meeting invitation"

  local meeting_title meeting_date meeting_time organizer location

  meeting_title=$(echo "$subject" | sed 's/invitation://i' | xargs)
  meeting_date=$(extract_date "$email_content")
  meeting_time=$(extract_time "$email_content")
  organizer=$(echo "$email_content" | grep -oiP "(organizer|from)[: ]*\K[^<\n]{3,50}" | head -n 1 | xargs)
  location=$(echo "$email_content" | grep -oiP "(location|where|room)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  local telegram_message="<b> Meeting Invitation</b>

<b>Meeting:</b> ${meeting_title}
<b>Date:</b> ${meeting_date:-TBD}
<b>Time:</b> ${meeting_time:-TBD}
<b>Organizer:</b> ${organizer:-Unknown}
<b>Location:</b> ${location:-TBD}

 Remember to accept/decline"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Meeting Invitation]
Meeting: ${meeting_title}
Date: ${meeting_date:-TBD}
Time: ${meeting_time:-TBD}
Organizer: ${organizer:-Unknown}
Location: ${location:-TBD}
Action: Accept or decline"

  add_to_digest "Calendar/Meeting" "$digest_entry" "medium"

  return 0
}

handle_event_reminder() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing event reminder"

  local event_title event_date event_time

  event_title=$(echo "$subject" | sed 's/reminder://i' | xargs)
  event_date=$(extract_date "$email_content")
  event_time=$(extract_time "$email_content")

  local telegram_message="<b> Event Reminder</b>

<b>Event:</b> ${event_title}
<b>Date:</b> ${event_date:-Soon}
<b>Time:</b> ${event_time:-TBD}

⏰ Don't forget!"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Event Reminder]
Event: ${event_title}
Date: ${event_date:-Soon}
Time: ${event_time:-TBD}"

  add_to_digest "Calendar/Reminder" "$digest_entry" "medium"

  return 0
}

handle_appointment() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing appointment confirmation"

  local appointment_type appointment_date appointment_time location provider

  appointment_type=$(echo "$subject" | grep -oiP '(medical|dental|doctor|clinic|hospital|appointment with)[: ]*\K[^-\n]{3,50}' | head -n 1 | xargs)
  appointment_date=$(extract_date "$email_content")
  appointment_time=$(extract_time "$email_content")
  location=$(echo "$email_content" | grep -oiP "(location|address|clinic|office)[: ]*\K[^.\n]{3,100}" | head -n 1 | xargs)
  provider=$(echo "$email_content" | grep -oiP "(doctor|provider|with)[: ]*\K[A-Z][a-z]+ [A-Z][a-z]+" | head -n 1)

  local telegram_message="<b> Appointment Confirmed</b>

<b>Type:</b> ${appointment_type:-Appointment}
<b>Provider:</b> ${provider:-Unknown}
<b>Date:</b> ${appointment_date:-TBD}
<b>Time:</b> ${appointment_time:-TBD}
<b>Location:</b> ${location:-TBD}

 Add to calendar and set reminder"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Appointment Confirmed]
Type: ${appointment_type:-Appointment}
Provider: ${provider:-Unknown}
Date: ${appointment_date:-TBD}
Time: ${appointment_time:-TBD}
Location: ${location:-TBD}"

  add_to_digest "Health/Appointment" "$digest_entry" "high"

  if [ -n "$appointment_date" ]; then
    local all_day="false"
    if [ -z "$appointment_time" ]; then
      all_day="true"
    fi
    add_calendar_event "${appointment_type:-Appointment}" "$appointment_date" "$all_day" "$appointment_time" "Provider: ${provider}. Location: ${location}"
  fi

  return 0
}

handle_reservation() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing reservation confirmation"

  local reservation_type venue reservation_date reservation_time confirmation_number

  reservation_type=$(echo "$subject" | grep -oiP '(restaurant|hotel|flight|car|rental|booking|reservation)[: ]*' | head -n 1 | xargs)
  venue=$(echo "$email_content" | grep -oiP "(at|venue|property|restaurant)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  reservation_date=$(extract_date "$email_content")
  reservation_time=$(extract_time "$email_content")
  confirmation_number=$(echo "$email_content" | grep -oiP "(confirmation|reservation) (number|#|code)[: ]*\K[A-Z0-9-]+" | head -n 1)

  local telegram_message="<b> Reservation Confirmed</b>

<b>Type:</b> ${reservation_type:-Reservation}
<b>Venue:</b> ${venue:-Unknown}
<b>Date:</b> ${reservation_date:-TBD}
<b>Time:</b> ${reservation_time:-TBD}
<b>Confirmation #:</b> ${confirmation_number:-See email}

 Added to calendar"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Reservation Confirmed]
Type: ${reservation_type:-Reservation}
Venue: ${venue:-Unknown}
Date: ${reservation_date:-TBD}
Time: ${reservation_time:-TBD}
Confirmation: ${confirmation_number:-See email}"

  add_to_digest "Travel/Reservation" "$digest_entry" "high"

  if [ -n "$reservation_date" ]; then
    local all_day="false"
    if [ -z "$reservation_time" ]; then
      all_day="true"
    fi
    add_calendar_event "${reservation_type:-Reservation}: ${venue}" "$reservation_date" "$all_day" "$reservation_time" "Confirmation: ${confirmation_number}"
  fi

  return 0
}

# FAMILY & VIP HANDLERS

handle_family_email() {
  local email_content="$1"
  local subject="$2"
  local sender="$3"

  log_info "Processing email from family member: $sender"

  local sender_name
  sender_name=$(echo "$sender" | grep -oP '^[^<]+' | xargs)

  # Extract first few lines as preview
  local preview
  preview=$(echo "$email_content" | head -c 200)

  local telegram_message="<b>‍‍‍ Family Email</b>

<b>From:</b> ${sender_name}
<b>Subject:</b> ${subject}

<b>Preview:</b> ${preview}...

 Check your email for full message"

  send_telegram "$telegram_message" "critical"

  local digest_entry="[Family Email]
From: ${sender_name}
Subject: ${subject}
Action: Review and respond"

  add_to_digest "Personal/Family" "$digest_entry" "critical"

  return 0
}

handle_vip_email() {
  local email_content="$1"
  local subject="$2"
  local sender="$3"

  log_info "Processing email from VIP contact: $sender"

  local sender_name
  sender_name=$(echo "$sender" | grep -oP '^[^<]+' | xargs)

  local preview
  preview=$(echo "$email_content" | head -c 200)

  local telegram_message="<b>⭐ VIP Email</b>

<b>From:</b> ${sender_name}
<b>Subject:</b> ${subject}

<b>Preview:</b> ${preview}...

⚠️ <b>Important:</b> Respond promptly"

  send_telegram "$telegram_message" "high"

  local digest_entry="[VIP Email]
From: ${sender_name}
Subject: ${subject}
Action: Priority response required"

  add_to_digest "Work/VIP" "$digest_entry" "high"

  return 0
}

# BILLS & UTILITIES HANDLERS

handle_utility_bill() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing utility bill"

  local utility_type amount due_date account_number

  utility_type=$(echo "$subject" | grep -oiP '(electricity|electric|water|gas|utility)' | head -n 1)
  amount=$(extract_amount "$email_content")
  due_date=$(extract_date "$email_content")
  account_number=$(echo "$email_content" | grep -oiP "account (number|#)[: ]*\K[0-9-]+" | head -n 1)

  local telegram_message="<b> Utility Bill</b>

<b>Type:</b> ${utility_type^^} Bill
<b>Amount:</b> ₩${amount:-Unknown}
<b>Account:</b> •••${account_number: -4}
<b>Due Date:</b> ${due_date:-Unknown}

 Schedule payment before due date"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Utility Bill]
Type: ${utility_type^^}
Amount: ₩${amount:-Unknown}
Due: ${due_date:-Unknown}
Action: Schedule payment"

  add_to_digest "Bills/Utility" "$digest_entry" "medium"

  if [ -n "$due_date" ]; then
    add_calendar_event "${utility_type^^} Bill Payment" "$due_date" true "" "Amount: ₩${amount}. Account: ${account_number}"
  fi

  return 0
}

handle_phone_bill() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing phone bill"

  local amount due_date phone_number

  amount=$(extract_amount "$email_content")
  due_date=$(extract_date "$email_content")
  phone_number=$(echo "$email_content" | grep -oP '\d{3}-\d{3,4}-\d{4}' | head -n 1)

  local telegram_message="<b> Phone Bill</b>

<b>Number:</b> ${phone_number:-Your number}
<b>Amount:</b> ₩${amount:-Unknown}
<b>Due Date:</b> ${due_date:-Unknown}

 Schedule payment"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Phone Bill]
Number: ${phone_number:-Your number}
Amount: ₩${amount:-Unknown}
Due: ${due_date:-Unknown}
Action: Schedule payment"

  add_to_digest "Bills/Phone" "$digest_entry" "medium"

  if [ -n "$due_date" ]; then
    add_calendar_event "Phone Bill Payment" "$due_date" true "" "Amount: ₩${amount}"
  fi

  return 0
}

handle_internet_bill() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing internet bill"

  local amount due_date provider

  amount=$(extract_amount "$email_content")
  due_date=$(extract_date "$email_content")
  provider=$(echo "$subject" | grep -oP '^[^-:]+' | head -n 1 | xargs)

  local telegram_message="<b> Internet Bill</b>

<b>Provider:</b> ${provider:-ISP}
<b>Amount:</b> ₩${amount:-Unknown}
<b>Due Date:</b> ${due_date:-Unknown}

 Schedule payment"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Internet Bill]
Provider: ${provider:-ISP}
Amount: ₩${amount:-Unknown}
Due: ${due_date:-Unknown}
Action: Schedule payment"

  add_to_digest "Bills/Internet" "$digest_entry" "medium"

  if [ -n "$due_date" ]; then
    add_calendar_event "Internet Bill Payment: ${provider}" "$due_date" true "" "Amount: ₩${amount}"
  fi

  return 0
}

# HEALTH & MEDICAL HANDLERS

handle_medical_appointment() {
  local email_content="$1"
  local subject="$2"

  # Reuse appointment handler
  handle_appointment "$email_content" "$subject"

  return 0
}

handle_prescription() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing prescription notification"

  local pharmacy medication patient pickup_by

  pharmacy=$(echo "$email_content" | grep -oiP "(pharmacy|at)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  medication=$(echo "$email_content" | grep -oiP "(medication|prescription|drug)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  patient=$(echo "$email_content" | grep -oiP "(patient|for)[: ]*\K[A-Z][a-z]+ [A-Z][a-z]+" | head -n 1)
  pickup_by=$(extract_date "$email_content")

  local telegram_message="<b> Prescription Ready</b>

<b>Patient:</b> ${patient:-Unknown}
<b>Medication:</b> ${medication:-See email}
<b>Pharmacy:</b> ${pharmacy:-Unknown}
<b>Pickup By:</b> ${pickup_by:-ASAP}

 Pick up prescription soon"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Prescription Ready]
Patient: ${patient:-Unknown}
Medication: ${medication:-See email}
Pharmacy: ${pharmacy:-Unknown}
Pickup By: ${pickup_by:-ASAP}
Action: Pick up medication"

  add_to_digest "Health/Prescription" "$digest_entry" "high"

  if [ -n "$pickup_by" ]; then
    add_calendar_event "Pickup Prescription: ${patient}" "$pickup_by" true "" "Medication: ${medication}. Pharmacy: ${pharmacy}"
  fi

  return 0
}

handle_lab_results() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing lab results notification"

  local patient test_type result_date

  patient=$(echo "$email_content" | grep -oiP "(patient|for)[: ]*\K[A-Z][a-z]+ [A-Z][a-z]+" | head -n 1)
  test_type=$(echo "$email_content" | grep -oiP "(test|exam|screening)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  result_date=$(extract_date "$email_content")

  local telegram_message="<b> Lab Results Available</b>

<b>Patient:</b> ${patient:-Unknown}
<b>Test:</b> ${test_type:-See email}
<b>Date:</b> ${result_date:-$(date '+%Y-%m-%d')}

⚠️ <b>IMPORTANT:</b> Review results immediately and consult doctor if needed"

  send_telegram "$telegram_message" "critical"

  local digest_entry="[Lab Results Available]
Patient: ${patient:-Unknown}
Test: ${test_type:-See email}
Date: ${result_date:-$(date '+%Y-%m-%d')}
Action: Review results and follow up with doctor"

  add_to_digest "Health/LabResults" "$digest_entry" "critical"

  return 0
}

# TRAVEL HANDLERS

handle_flight_booking() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing flight booking"

  local confirmation_number flight_date departure_time airline route

  confirmation_number=$(echo "$email_content" | grep -oiP "(confirmation|booking|PNR) (number|#|code)[: ]*\K[A-Z0-9]+" | head -n 1)
  flight_date=$(extract_date "$email_content")
  departure_time=$(extract_time "$email_content")
  airline=$(echo "$email_content" | grep -oiP "(airline|carrier|operated by)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  route=$(echo "$email_content" | grep -oiP "from [A-Z]{3} to [A-Z]{3}" | head -n 1)

  local telegram_message="<b>✈️ Flight Booking Confirmed</b>

<b>Confirmation:</b> ${confirmation_number:-See email}
<b>Airline:</b> ${airline:-Unknown}
<b>Route:</b> ${route:-See email}
<b>Date:</b> ${flight_date:-TBD}
<b>Departure:</b> ${departure_time:-TBD}

✅ Check in 24 hours before departure"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Flight Booking]
Confirmation: ${confirmation_number:-See email}
Airline: ${airline:-Unknown}
Route: ${route:-See email}
Date: ${flight_date:-TBD}
Departure: ${departure_time:-TBD}
Action: Check in 24h before"

  add_to_digest "Travel/Flight" "$digest_entry" "high"

  if [ -n "$flight_date" ]; then
    local all_day="false"
    if [ -z "$departure_time" ]; then
      all_day="true"
    fi
    add_calendar_event "Flight: ${route}" "$flight_date" "$all_day" "$departure_time" "Airline: ${airline}. Confirmation: ${confirmation_number}"
  fi

  return 0
}

handle_hotel_reservation() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing hotel reservation"

  local hotel_name check_in check_out confirmation_number

  hotel_name=$(echo "$email_content" | grep -oiP "(hotel|property)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  check_in=$(echo "$email_content" | grep -oiP "check.?in[: ]*\K.*" | head -n 1 | xargs)
  check_out=$(echo "$email_content" | grep -oiP "check.?out[: ]*\K.*" | head -n 1 | xargs)
  confirmation_number=$(echo "$email_content" | grep -oiP "(confirmation|reservation) (number|#|code)[: ]*\K[A-Z0-9-]+" | head -n 1)

  local telegram_message="<b> Hotel Reservation Confirmed</b>

<b>Hotel:</b> ${hotel_name:-Unknown}
<b>Check-in:</b> ${check_in:-TBD}
<b>Check-out:</b> ${check_out:-TBD}
<b>Confirmation:</b> ${confirmation_number:-See email}

 Added to calendar"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Hotel Reservation]
Hotel: ${hotel_name:-Unknown}
Check-in: ${check_in:-TBD}
Check-out: ${check_out:-TBD}
Confirmation: ${confirmation_number:-See email}"

  add_to_digest "Travel/Hotel" "$digest_entry" "medium"

  if [ -n "$check_in" ]; then
    add_calendar_event "Hotel: ${hotel_name}" "$check_in" true "" "Check-out: ${check_out}. Confirmation: ${confirmation_number}"
  fi

  return 0
}

handle_travel_itinerary() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing travel itinerary"

  local trip_name start_date end_date destination

  trip_name=$(echo "$subject" | xargs)
  start_date=$(extract_date "$email_content" | head -n 1)
  destination=$(echo "$email_content" | grep -oiP "(destination|traveling to|visiting)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)

  local telegram_message="<b>️ Travel Itinerary</b>

<b>Trip:</b> ${trip_name}
<b>Destination:</b> ${destination:-See email}
<b>Start:</b> ${start_date:-TBD}

 Check email for full itinerary details"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Travel Itinerary]
Trip: ${trip_name}
Destination: ${destination:-See email}
Start: ${start_date:-TBD}
Action: Review full itinerary"

  add_to_digest "Travel/Itinerary" "$digest_entry" "medium"

  return 0
}

# SECURITY HANDLERS

handle_security_alert() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing security alert"

  local service alert_type alert_date

  service=$(echo "$subject" | grep -oP '^[^-:]+' | head -n 1 | xargs)
  alert_type=$(echo "$email_content" | grep -oiP "(suspicious|unusual|unauthorized|new|unrecognized).*?(activity|login|access|device)" | head -n 1 | xargs)
  alert_date=$(extract_date "$email_content")

  local telegram_message="<b> SECURITY ALERT</b>

<b>Service:</b> ${service}
<b>Alert:</b> ${alert_type}
<b>Date:</b> ${alert_date:-$(date '+%Y-%m-%d %H:%M')}

⚠️ <b>URGENT:</b> Review immediately and take action if unauthorized!"

  send_telegram "$telegram_message" "critical"

  local digest_entry="[SECURITY ALERT]
Service: ${service}
Alert: ${alert_type}
Date: ${alert_date:-$(date '+%Y-%m-%d %H:%M')}
Action: URGENT - Review and secure account if needed"

  add_to_digest "Security/Alert" "$digest_entry" "critical"

  return 0
}

handle_password_reset() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing password reset notification"

  local service request_time

  service=$(echo "$subject" | grep -oP '^[^-:]+' | head -n 1 | xargs)
  request_time=$(extract_date "$email_content")

  local telegram_message="<b> Password Reset Request</b>

<b>Service:</b> ${service}
<b>Time:</b> ${request_time:-$(date '+%Y-%m-%d %H:%M')}

⚠️ If you didn't request this, secure your account immediately!"

  send_telegram "$telegram_message" "high"

  local digest_entry="[Password Reset]
Service: ${service}
Time: ${request_time:-$(date '+%Y-%m-%d %H:%M')}
Action: Verify request was legitimate"

  add_to_digest "Security/Password" "$digest_entry" "high"

  return 0
}

handle_login_notification() {
  local email_content="$1"
  local subject="$2"

  log_info "Processing login notification"

  local service location device login_time

  service=$(echo "$subject" | grep -oP '^[^-:]+' | head -n 1 | xargs)
  location=$(echo "$email_content" | grep -oiP "(location|from|in)[: ]*\K[A-Za-z, ]{3,50}" | head -n 1 | xargs)
  device=$(echo "$email_content" | grep -oiP "(device|on)[: ]*\K[^.\n]{3,50}" | head -n 1 | xargs)
  login_time=$(extract_date "$email_content")

  local telegram_message="<b> New Login Detected</b>

<b>Service:</b> ${service}
<b>Location:</b> ${location:-Unknown}
<b>Device:</b> ${device:-Unknown}
<b>Time:</b> ${login_time:-$(date '+%Y-%m-%d %H:%M')}

ℹ️ If this wasn't you, secure your account"

  send_telegram "$telegram_message" "medium"

  local digest_entry="[Login Notification]
Service: ${service}
Location: ${location:-Unknown}
Device: ${device:-Unknown}
Time: ${login_time:-$(date '+%Y-%m-%d %H:%M')}"

  add_to_digest "Security/Login" "$digest_entry" "medium"

  return 0
}

#==============================================================================
# MAIN EMAIL PROCESSING
#==============================================================================

process_single_email() {
  local email_json="$1"

  # Extract basic metadata
  local email_id thread_id subject sender
  email_id=$(extract_email_data "$email_json" "id")
  thread_id=$(extract_email_data "$email_json" "threadId")
  subject=$(extract_email_data "$email_json" "subject")
  sender=$(extract_email_data "$email_json" "from")

  if [ -z "$email_id" ] || [ -z "$thread_id" ]; then
    log_warn "Skipping email with missing ID or thread ID"
    return 1
  fi

  if [ -z "$sender" ]; then
    sender="unknown"
  fi

  if [ -z "$subject" ]; then
    subject="(No Subject)"
  fi

  log_info "=========================================="
  log_info "Processing: $subject"
  log_info "From: $sender"
  log_info "Thread ID: $thread_id"
  log_info "=========================================="

  # Get full thread content
  local email_content
  email_content=$(get_thread_content "$thread_id")

  if [ -z "$email_content" ]; then
    log_warn "Failed to retrieve email content, skipping classification"
    email_content=""
  fi

  # Classify email
  local classifications
  classifications=$(classify_email "$subject" "$sender" "$email_content")

  local num_matches
  num_matches=$(echo "$classifications" | jq 'length')

  log_info "Found $num_matches pattern match(es)"

  # Process each matched pattern
  if [ "$num_matches" -gt 0 ]; then
    for i in $(seq 0 $((num_matches - 1))); do
      local match
      match=$(echo "$classifications" | jq -r ".[$i]")

      IFS=':' read -r pattern_key priority <<< "$match"

      log_info "Handling pattern: $pattern_key (priority: $priority)"

      # Get handler function
      local pattern_data="${EMAIL_PATTERNS[$pattern_key]}"
      if [ -z "$pattern_data" ]; then
        log_warn "No handler data found for pattern: $pattern_key"
        continue
      fi

      IFS='|' read -r pattern handler_func handler_priority description <<< "$pattern_data"

      # Call handler function
      if declare -f "$handler_func" > /dev/null; then
        $handler_func "$email_content" "$subject" "$sender" || log_warn "Handler $handler_func failed"
      else
        log_warn "Handler function not found: $handler_func"
      fi
    done
  else
    log_info "No special patterns matched - applying standard label processing"
  fi

  # Apply label based on sender history
  local label_pattern
  label_pattern=$(get_label_pattern "$sender")

  local label_applied=false
  if [ -n "$label_pattern" ]; then
    if apply_label "$thread_id" "$label_pattern"; then
      label_applied=true
    fi
  else
    log_info "No label pattern found for sender"
  fi

  # Remove standard labels
  remove_labels "$thread_id"

  # Archive if label was applied or if email was classified
  if [ "$label_applied" = true ] || [ "$num_matches" -gt 0 ]; then
    archive_email "$thread_id"
  else
    log_info "Email not archived (no label and no classification)"
  fi

  log_info "Email processing completed"
  echo ""

  return 0
}

process_all_emails() {
  log_info "Starting email batch processing (max: $MAX_EMAILS emails)"

  local unread_emails
  unread_emails=$(get_unread_emails)

  if [ -z "$unread_emails" ]; then
    log_info "No unread emails found"
    return 0
  fi

  local email_count
  email_count=$(echo "$unread_emails" | jq '.messages | length')

  if [ "$email_count" -eq 0 ]; then
    log_info "No unread emails to process"
    return 0
  fi

  log_info "Found $email_count unread email(s)"

  # Process each email
  for i in $(seq 0 $((email_count - 1))); do
    local email_json
    email_json=$(echo "$unread_emails" | jq ".messages[$i]")

    process_single_email "$email_json" || log_warn "Failed to process email $((i+1))"

    # Small delay between emails to avoid rate limiting
    sleep 1
  done

  log_info "Batch processing completed"

  return 0
}

#==============================================================================
# MAIN EXECUTION
#==============================================================================

main() {
  log_info "==========================================="
  log_info "Intelligent Gmail Manager Started"
  log_info "==========================================="
  log_info "Configuration:"
  log_info "  - Max emails per run: $MAX_EMAILS"
  log_info "  - Family contacts: ${#FAMILY_CONTACTS[@]}"
  log_info "  - VIP contacts: ${#VIP_CONTACTS[@]}"
  log_info "  - Telegram enabled: $([ -n "$TELEGRAM_BOT_TOKEN" ] && echo "Yes" || echo "No")"
  log_info "==========================================="

  if ! process_all_emails; then
    log_error "Email processing failed"
    exit 1
  fi

  log_info "==========================================="
  log_info "Intelligent Gmail Manager Finished"
  log_info "==========================================="

  exit 0
}

# Run main function
main "$@"
