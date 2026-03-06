#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"

echo "Initializing lead gen workspace at: $BASE_DIR"
mkdir -p "$BASE_DIR"/{leads/{raw,enriched,qualified,archived},campaigns,templates,reports}

if [ ! -f "$BASE_DIR/config.json" ]; then
  cat > "$BASE_DIR/config.json" << 'EOF'
{
  "hunter_api_key": "",
  "default_crm": "hubspot",
  "crm": {
    "hubspot": { "api_key": "", "pipeline_id": "", "stage_id": "" },
    "pipedrive": { "api_key": "", "domain": "" },
    "zoho": { "access_token": "", "refresh_token": "" }
  },
  "email": {
    "provider": "sendgrid",
    "sendgrid_api_key": "",
    "smtp": { "host": "", "port": 587, "user": "", "pass": "" },
    "from_name": "",
    "from_email": "",
    "daily_limit": 50,
    "delay_between_emails_sec": 30
  },
  "scoring": {
    "threshold": 70,
    "weights": {
      "company_size_fit": 25,
      "industry_match": 25,
      "email_available": 20,
      "web_presence": 15,
      "tech_signals": 15
    },
    "target_industries": [],
    "target_company_sizes": ["1-10", "11-50", "51-200"]
  }
}
EOF
  echo "Created config.json"
fi

# Create default cold outreach template
if [ ! -f "$BASE_DIR/templates/cold-intro.json" ]; then
  cat > "$BASE_DIR/templates/cold-intro.json" << 'EOF'
{
  "name": "cold-intro",
  "subject": "Quick question about {company_name}",
  "body": "Hi {first_name},\n\nI noticed {company_name} is {personalization_hook}.\n\nWe help companies like yours {value_prop}.\n\nWould you be open to a quick chat this week?\n\nBest,\n{sender_name}",
  "follow_ups": [
    {
      "delay_days": 3,
      "subject": "Re: Quick question about {company_name}",
      "body": "Hi {first_name},\n\nJust following up on my previous note. {follow_up_hook}\n\nHappy to share more details if helpful.\n\nBest,\n{sender_name}"
    },
    {
      "delay_days": 7,
      "subject": "Last note from me",
      "body": "Hi {first_name},\n\nDon't want to be a pest — just one last check. If {value_prop_short} isn't a priority right now, no worries at all.\n\nIf timing changes, I'm here.\n\nBest,\n{sender_name}"
    }
  ]
}
EOF
  echo "Created default cold-intro template"
fi

echo "✅ Lead gen workspace initialized"
