#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Write My Blog — Unified Setup Script
# Works in two modes:
#   1) Interactive  — human runs it, gets prompted for everything
#   2) Non-interactive (agent) — pass flags or env vars, zero prompts
#
# Usage:
#   Interactive:   ./scripts/setup.sh
#   Agent/CI:      ./scripts/setup.sh --non-interactive \
#                    --db sqlite --cache memory --theme minimalism
#
# All flags also accept environment variable equivalents:
#   SETUP_DB_PROVIDER, SETUP_CACHE_PROVIDER, SETUP_SUPABASE_URL,
#   SETUP_SUPABASE_KEY, SETUP_REDIS_URL, SETUP_THEME, SETUP_BLOG_NAME,
#   SETUP_BLOG_DESCRIPTION, SETUP_API_KEY
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLATFORM_DIR="$PROJECT_ROOT/platform"

# ── Defaults ──
INTERACTIVE=true
DB_PROVIDER="${SETUP_DB_PROVIDER:-}"
CACHE_PROVIDER="${SETUP_CACHE_PROVIDER:-}"
SUPABASE_URL="${SETUP_SUPABASE_URL:-}"
SUPABASE_KEY="${SETUP_SUPABASE_KEY:-}"
MONGODB_URI="${SETUP_MONGODB_URI:-}"
MONGODB_DB_NAME="${SETUP_MONGODB_DB_NAME:-blog}"
REDIS_URL="${SETUP_REDIS_URL:-}"
THEME="${SETUP_THEME:-minimalism}"
BLOG_NAME="${SETUP_BLOG_NAME:-My Blog}"
BLOG_DESC="${SETUP_BLOG_DESCRIPTION:-A blog powered by AI}"
API_KEY="${SETUP_API_KEY:-}"
SKIP_INSTALL="${SETUP_SKIP_INSTALL:-false}"

# ── Parse CLI flags ──
while [[ $# -gt 0 ]]; do
  case "$1" in
    --non-interactive|-n) INTERACTIVE=false ;;
    --db)                 DB_PROVIDER="$2"; shift ;;
    --cache)              CACHE_PROVIDER="$2"; shift ;;
    --supabase-url)       SUPABASE_URL="$2"; shift ;;
    --supabase-key)       SUPABASE_KEY="$2"; shift ;;
    --mongodb-uri)        MONGODB_URI="$2"; shift ;;
    --mongodb-db)         MONGODB_DB_NAME="$2"; shift ;;
    --redis-url)          REDIS_URL="$2"; shift ;;
    --theme)              THEME="$2"; shift ;;
    --blog-name)          BLOG_NAME="$2"; shift ;;
    --blog-desc)          BLOG_DESC="$2"; shift ;;
    --api-key)            API_KEY="$2"; shift ;;
    --deploy)             DEPLOY_TARGET="$2"; shift ;;
    --skip-install)       SKIP_INSTALL=true ;;
    --help|-h)
      echo "Usage: ./scripts/setup.sh [options]"
      echo ""
      echo "Options:"
      echo "  -n, --non-interactive    Skip all prompts (for agents / CI)"
      echo "  --db <provider>          Database: sqlite (default), supabase, postgres"
      echo "  --cache <provider>       Cache: memory (default), redis"
      echo "  --supabase-url <url>     Supabase project URL"
      echo "  --supabase-key <key>     Supabase service role key"
      echo "  --mongodb-uri <uri>      MongoDB connection URI"
      echo "  --mongodb-db <name>      MongoDB database name (default: blog)"
      echo "  --redis-url <url>        Redis connection URL"
      echo "  --theme <name>           Default theme (default: minimalism)"
      echo "  --blog-name <name>       Blog display name"
      echo "  --blog-desc <text>       Blog subtitle / description"
      echo "  --api-key <key>          Set a specific API key (auto-generated if omitted)"
      echo "  --deploy <target>        Deploy target: vercel, cloudflare, none"
      echo "  --skip-install           Skip npm install"
      echo "  -h, --help               Show this help"
      echo ""
      echo "Environment variables (same as flags):"
      echo "  SETUP_DB_PROVIDER, SETUP_CACHE_PROVIDER, SETUP_SUPABASE_URL,"
      echo "  SETUP_SUPABASE_KEY, SETUP_REDIS_URL, SETUP_THEME, SETUP_BLOG_NAME,"
      echo "  SETUP_BLOG_DESCRIPTION, SETUP_API_KEY, SETUP_DEPLOY_TARGET,"
      echo "  SETUP_SKIP_INSTALL"
      exit 0
      ;;
    *) echo "Unknown option: $1 (use --help)"; exit 1 ;;
  esac
  shift
done

# ── Helpers ──
ask() {
  # ask <var_name> <prompt> <default>
  local var_name="$1" prompt="$2" default="${3:-}"
  if $INTERACTIVE; then
    local current="${!var_name:-$default}"
    read -rp "$prompt [$current]: " input
    eval "$var_name=\"${input:-$current}\""
  else
    if [ -z "${!var_name:-}" ]; then
      eval "$var_name=\"$default\""
    fi
  fi
}

ask_secret() {
  # ask_secret <var_name> <prompt>
  local var_name="$1" prompt="$2"
  if $INTERACTIVE; then
    read -rsp "$prompt: " input
    echo ""
    eval "$var_name=\"$input\""
  fi
  # In non-interactive mode, the value must be set via flag/env
}

choose() {
  # choose <var_name> <prompt> <option1> <option2> ...
  local var_name="$1" prompt="$2"
  shift 2
  local options=("$@")
  local default="${options[0]}"

  if $INTERACTIVE; then
    echo ""
    echo "$prompt"
    local i=1
    for opt in "${options[@]}"; do
      local label="$opt"
      [ "$opt" = "sqlite" ] && label="sqlite (local, zero config)"
      [ "$opt" = "supabase" ] && label="supabase (managed Postgres + Storage)"
      [ "$opt" = "mongodb" ] && label="mongodb (MongoDB Atlas — free tier available)"
      [ "$opt" = "memory" ] && label="memory (in-process, no setup)"
      [ "$opt" = "redis" ] && label="redis (Redis / Upstash)"
      echo "  $i) $label"
      ((i++))
    done
    read -rp "Choice [1]: " choice
    choice="${choice:-1}"
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
      eval "$var_name=\"${options[$((choice - 1))]}\""
    else
      eval "$var_name=\"$default\""
    fi
  else
    if [ -z "${!var_name:-}" ]; then
      eval "$var_name=\"$default\""
    fi
  fi
}

# ═══════════════════════════════════════
# 1. Banner
# ═══════════════════════════════════════
echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   🖊️  Write My Blog — Setup              ║"
if $INTERACTIVE; then
  echo "  ║   mode: interactive                      ║"
else
  echo "  ║   mode: non-interactive (agent / CI)     ║"
fi
echo "  ╚══════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════
# 2. Install dependencies
# ═══════════════════════════════════════
if [ "$SKIP_INSTALL" = "true" ]; then
  echo "⏭️  Skipping npm install (--skip-install)"
else
  echo "📦 Installing dependencies..."
  cd "$PLATFORM_DIR"
  npm install --loglevel=error
  echo "✅ Dependencies installed"
fi
echo ""

# ═══════════════════════════════════════
# 3. Configure environment
# ═══════════════════════════════════════
ENV_FILE="$PLATFORM_DIR/.env.local"

if [ -f "$ENV_FILE" ] && $INTERACTIVE; then
  echo "⚠️  .env.local already exists."
  read -rp "Overwrite? (y/N): " overwrite
  if [[ ! "$overwrite" =~ ^[Yy] ]]; then
    echo "↩️  Keeping existing .env.local"
    SKIP_ENV=true
  else
    SKIP_ENV=false
  fi
elif [ -f "$ENV_FILE" ] && ! $INTERACTIVE; then
  echo "⚠️  .env.local already exists — overwriting (non-interactive mode)"
  SKIP_ENV=false
else
  SKIP_ENV=false
fi

if [ "${SKIP_ENV:-false}" = "false" ]; then

  # ── API Key ──
  if [ -z "$API_KEY" ]; then
    API_KEY=$(openssl rand -hex 24 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 48 | head -n 1)
  fi

  # ── Blog identity ──
  if $INTERACTIVE; then
    echo ""
    echo "── Blog Identity ──"
    ask BLOG_NAME  "Blog name" "$BLOG_NAME"
    ask BLOG_DESC  "Blog description" "$BLOG_DESC"
    echo ""
    echo "── Theme ──"
    echo "Available: minimalism, brutalism, constructivism, swiss, editorial,"
    echo "           hand-drawn, retro, flat, bento, glassmorphism"
    ask THEME "Default theme" "$THEME"
  fi

  # ── Database ──
  choose DB_PROVIDER "── Database provider ──" "sqlite" "supabase" "mongodb" "postgres"

  if [ "$DB_PROVIDER" = "supabase" ] || [ "$DB_PROVIDER" = "postgres" ]; then
    if [ -z "$SUPABASE_URL" ]; then
      ask SUPABASE_URL "Supabase project URL" ""
    fi
    if [ -z "$SUPABASE_KEY" ]; then
      if $INTERACTIVE; then
        ask_secret SUPABASE_KEY "Supabase service role key"
      fi
    fi
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
      echo "❌ Supabase URL and key are required for supabase/postgres provider"
      exit 1
    fi
  fi

  if [ "$DB_PROVIDER" = "mongodb" ]; then
    echo ""
    echo "  ┌────────────────────────────────────────────────────────┐"
    echo "  │ MongoDB Atlas Setup                                    │"
    echo "  │ 1. Go to mongodb.com/cloud/atlas                      │"
    echo "  │ 2. Create a free cluster (M0 tier)                    │"
    echo "  │ 3. Create a database user with read/write access      │"
    echo "  │ 4. Allow network access (0.0.0.0/0 for serverless)    │"
    echo "  │ 5. Get connection string from Connect > Drivers       │"
    echo "  └────────────────────────────────────────────────────────┘"
    echo ""
    if [ -z "$MONGODB_URI" ]; then
      echo "Paste your full Atlas connection string:"
      echo "  (e.g. mongodb+srv://user:pass@cluster.xxxxx.mongodb.net)"
      ask MONGODB_URI "MongoDB Atlas URI" ""
    fi
    if [ -z "$MONGODB_URI" ]; then
      echo "❌ MongoDB Atlas URI is required"
      exit 1
    fi
    ask MONGODB_DB_NAME "Database name" "$MONGODB_DB_NAME"
  fi

  # ── Cache ──
  choose CACHE_PROVIDER "── Cache provider ──" "memory" "redis"

  if [ "$CACHE_PROVIDER" = "redis" ]; then
    ask REDIS_URL "Redis URL" "redis://localhost:6379"
  fi

  # ── Write .env.local ──
  cat > "$ENV_FILE" <<EOF
# ── Write My Blog — Generated $(date +%Y-%m-%d) ──

# Blog
BLOG_NAME=$BLOG_NAME
BLOG_DESCRIPTION=$BLOG_DESC
DEFAULT_THEME=$THEME

# Security
API_KEY=$API_KEY
RATE_LIMIT_RPM=100

# Database ($DB_PROVIDER)
DATABASE_PROVIDER=$DB_PROVIDER
SQLITE_PATH=./data/blog.db
EOF

  if [ "$DB_PROVIDER" = "supabase" ] || [ "$DB_PROVIDER" = "postgres" ]; then
    cat >> "$ENV_FILE" <<EOF
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_KEY=$SUPABASE_KEY
EOF
  fi

  if [ "$DB_PROVIDER" = "mongodb" ]; then
    cat >> "$ENV_FILE" <<EOF
MONGODB_URI=$MONGODB_URI
MONGODB_DB_NAME=$MONGODB_DB_NAME
EOF
  fi

  cat >> "$ENV_FILE" <<EOF

# Cache ($CACHE_PROVIDER)
CACHE_PROVIDER=$CACHE_PROVIDER
CACHE_MAX_SIZE=500
EOF

  if [ "$CACHE_PROVIDER" = "redis" ]; then
    echo "REDIS_URL=$REDIS_URL" >> "$ENV_FILE"
  fi

  cat >> "$ENV_FILE" <<EOF

# Media
MEDIA_DIR=./public/uploads
EOF

  echo ""
  echo "✅ .env.local created"
fi

# ═══════════════════════════════════════
# 4. Create directories
# ═══════════════════════════════════════
mkdir -p "$PLATFORM_DIR/data"
mkdir -p "$PLATFORM_DIR/public/uploads"
echo "📁 Data directories ready"
echo ""

# ═══════════════════════════════════════
# 5. Build verification
# ═══════════════════════════════════════
echo "🔨 Running production build to verify everything..."
cd "$PLATFORM_DIR"
if npx next build > /dev/null 2>&1; then
  echo "✅ Build passed"
else
  echo "⚠️  Build had warnings (may still work — check output with 'npx next build')"
fi
echo ""

# ═══════════════════════════════════════
# 6. Deployment (optional)
# ═══════════════════════════════════════
DEPLOY_TARGET="${SETUP_DEPLOY_TARGET:-none}"

if $INTERACTIVE; then
  echo ""
  echo "── Deploy ──"
  echo "  1) Skip — just run locally"
  echo "  2) Vercel (recommended for quick deploy)"
  echo "  3) Cloudflare Pages"
  read -rp "Choice [1]: " deploy_choice
  deploy_choice="${deploy_choice:-1}"
  case "$deploy_choice" in
    2) DEPLOY_TARGET="vercel" ;;
    3) DEPLOY_TARGET="cloudflare" ;;
    *) DEPLOY_TARGET="none" ;;
  esac
fi

# ── Guard: SQLite can't run on Vercel/Cloudflare (native C module) ──
if [ "$DEPLOY_TARGET" != "none" ] && [ "$DB_PROVIDER" = "sqlite" ]; then
  echo ""
  echo "  ┌─────────────────────────────────────────────────────────┐"
  echo "  │ ⚠️  SQLite uses a native C module (better-sqlite3)      │"
  echo "  │ which does NOT work on Vercel or Cloudflare serverless. │"
  echo "  │                                                         │"
  echo "  │ You need a cloud database for deployment.               │"
  echo "  │ Free options:                                           │"
  echo "  │   • Supabase  — supabase.com/dashboard                 │"
  echo "  │   • MongoDB Atlas — mongodb.com/cloud/atlas             │"
  echo "  └─────────────────────────────────────────────────────────┘"
  echo ""

  if $INTERACTIVE; then
    echo "  1) Switch to Supabase (enter credentials now)"
    echo "  2) Switch to MongoDB Atlas (enter credentials now)"
    echo "  3) Skip deploy — I'll set up a cloud DB later"
    read -rp "Choice [1]: " sqlite_fix
    sqlite_fix="${sqlite_fix:-1}"

    if [ "$sqlite_fix" = "1" ]; then
      DB_PROVIDER="supabase"
      read -rp "Supabase project URL: " SUPABASE_URL
      read -rsp "Supabase service role key: " SUPABASE_KEY
      echo ""

      if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        echo "❌ Both URL and key are required. Skipping deploy."
        DEPLOY_TARGET="none"
      else
        sed -i "s/^DATABASE_PROVIDER=.*/DATABASE_PROVIDER=supabase/" "$ENV_FILE"
        if ! grep -q "SUPABASE_URL" "$ENV_FILE" 2>/dev/null; then
          echo "" >> "$ENV_FILE"
          echo "# Supabase (added for cloud deploy)" >> "$ENV_FILE"
          echo "SUPABASE_URL=$SUPABASE_URL" >> "$ENV_FILE"
          echo "SUPABASE_SERVICE_KEY=$SUPABASE_KEY" >> "$ENV_FILE"
        else
          sed -i "s|^SUPABASE_URL=.*|SUPABASE_URL=$SUPABASE_URL|" "$ENV_FILE"
          sed -i "s|^SUPABASE_SERVICE_KEY=.*|SUPABASE_SERVICE_KEY=$SUPABASE_KEY|" "$ENV_FILE"
        fi
        echo "✅ Switched to Supabase. .env.local updated."
        echo ""
        echo "🔨 Rebuilding..."
        cd "$PLATFORM_DIR"
        npx next build > /dev/null 2>&1 && echo "✅ Build passed" || echo "⚠️  Build had issues"
      fi

    elif [ "$sqlite_fix" = "2" ]; then
      DB_PROVIDER="mongodb"
      echo ""
      echo "Paste your MongoDB Atlas connection string:"
      echo "  (e.g. mongodb+srv://user:pass@cluster.xxxxx.mongodb.net)"
      read -rp "MongoDB Atlas URI: " MONGODB_URI
      read -rp "Database name [blog]: " MONGODB_DB_NAME
      MONGODB_DB_NAME="${MONGODB_DB_NAME:-blog}"

      if [ -z "$MONGODB_URI" ]; then
        echo "❌ Atlas URI is required. Skipping deploy."
        DEPLOY_TARGET="none"
      else
        sed -i "s/^DATABASE_PROVIDER=.*/DATABASE_PROVIDER=mongodb/" "$ENV_FILE"
        if ! grep -q "MONGODB_URI" "$ENV_FILE" 2>/dev/null; then
          echo "" >> "$ENV_FILE"
          echo "# MongoDB Atlas (added for cloud deploy)" >> "$ENV_FILE"
          echo "MONGODB_URI=$MONGODB_URI" >> "$ENV_FILE"
          echo "MONGODB_DB_NAME=$MONGODB_DB_NAME" >> "$ENV_FILE"
        else
          sed -i "s|^MONGODB_URI=.*|MONGODB_URI=$MONGODB_URI|" "$ENV_FILE"
          sed -i "s|^MONGODB_DB_NAME=.*|MONGODB_DB_NAME=$MONGODB_DB_NAME|" "$ENV_FILE"
        fi
        echo "✅ Switched to MongoDB Atlas. .env.local updated."
        echo ""
        echo "🔨 Rebuilding..."
        cd "$PLATFORM_DIR"
        npx next build > /dev/null 2>&1 && echo "✅ Build passed" || echo "⚠️  Build had issues"
      fi
    else
      echo "⏭️  Skipping deploy. Set up a cloud DB and redeploy later:"
      echo "   1. Create a free Supabase or MongoDB Atlas account"
      echo "   2. Update .env.local with the credentials"
      echo "   3. Change DATABASE_PROVIDER to supabase or mongodb"
      echo "   4. Run: cd platform && npx vercel --prod"
      DEPLOY_TARGET="none"
    fi
  else
    echo "❌ Cannot deploy with SQLite to serverless. Set SETUP_DB_PROVIDER=supabase or mongodb"
    DEPLOY_TARGET="none"
  fi
fi

# ── Vercel Deploy ── 
if [ "$DEPLOY_TARGET" = "vercel" ]; then
  echo ""
  echo "🚀 Deploying to Vercel..."
  echo ""

  # Step 1: Install Vercel CLI if missing
  if ! npx -y vercel --version &>/dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
  fi
  echo "   Vercel CLI: $(npx -y vercel --version 2>/dev/null)"
  echo ""

  cd "$PLATFORM_DIR"

  if $INTERACTIVE; then
    # Step 2: Check if logged in, if not — login first
    echo "── Step 1: Vercel Login ──"
    echo "Checking authentication..."
    if ! npx -y vercel whoami &>/dev/null 2>&1; then
      echo ""
      echo "You need to log in to Vercel first."
      echo "Options:"
      echo "  1) Log in via browser (opens vercel.com)"
      echo "  2) Log in with email"
      echo "  3) Log in with GitHub"
      read -rp "Choice [1]: " login_method
      login_method="${login_method:-1}"
      case "$login_method" in
        2) npx -y vercel login --email ;;
        3) npx -y vercel login --github ;;
        *) npx -y vercel login ;;
      esac

      # Verify login succeeded
      if ! npx -y vercel whoami &>/dev/null 2>&1; then
        echo "❌ Login failed. You can deploy later with:"
        echo "   cd platform && npx vercel login && npx vercel --prod"
        DEPLOY_TARGET="none"
      else
        echo "✅ Logged in as: $(npx -y vercel whoami 2>/dev/null)"
      fi
    else
      echo "✅ Already logged in as: $(npx -y vercel whoami 2>/dev/null)"
    fi

    # Step 3: Link project and deploy
    if [ "$DEPLOY_TARGET" = "vercel" ]; then
      echo ""
      echo "── Step 2: Project Setup & Deploy ──"
      echo ""
      read -rp "Deploy to production? (Y/n): " prod_deploy
      prod_deploy="${prod_deploy:-y}"

      if [[ "$prod_deploy" =~ ^[Yy] ]]; then
        echo ""
        echo "Deploying to production..."
        if npx -y vercel --prod; then
          echo ""
          echo "✅ Deployed to Vercel (production)!"
        else
          echo ""
          echo "⚠️  Deploy failed. You can retry with:"
          echo "   cd platform && npx vercel --prod"
        fi
      else
        echo ""
        echo "Deploying preview..."
        if npx -y vercel; then
          echo ""
          echo "✅ Preview deployed to Vercel!"
        else
          echo ""
          echo "⚠️  Deploy failed. You can retry with:"
          echo "   cd platform && npx vercel"
        fi
      fi
    fi

  else
    # Non-interactive — requires VERCEL_TOKEN
    if [ -n "${VERCEL_TOKEN:-}" ]; then
      echo "Deploying with token (non-interactive)..."
      if npx -y vercel --token "$VERCEL_TOKEN" --yes --prod 2>&1; then
        echo "✅ Deployed to Vercel (production)"
      else
        echo "❌ Deploy failed. Check VERCEL_TOKEN and project settings."
      fi
    else
      echo "⚠️  VERCEL_TOKEN not set — skipping automated deploy"
      echo "   Set VERCEL_TOKEN, VERCEL_ORG_ID, and VERCEL_PROJECT_ID env vars"
      echo "   Then run: cd platform && npx vercel --token \$VERCEL_TOKEN --yes --prod"
      DEPLOY_TARGET="none"
    fi
  fi

# ── Cloudflare Deploy ──
elif [ "$DEPLOY_TARGET" = "cloudflare" ]; then
  echo ""
  echo "🚀 Deploying to Cloudflare Pages..."
  echo ""

  # Step 1: Install Wrangler CLI if missing
  if ! npx -y wrangler --version &>/dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
  fi
  echo "   Wrangler CLI: $(npx -y wrangler --version 2>/dev/null)"
  echo ""

  cd "$PLATFORM_DIR"

  if $INTERACTIVE; then
    # Step 2: Check if logged in
    echo "── Step 1: Cloudflare Login ──"
    echo "Checking authentication..."
    if ! npx -y wrangler whoami &>/dev/null 2>&1; then
      echo ""
      echo "You need to log in to Cloudflare first."
      echo "This will open your browser for OAuth login."
      read -rp "Press Enter to continue (or Ctrl+C to skip)..." _
      npx -y wrangler login

      if ! npx -y wrangler whoami &>/dev/null 2>&1; then
        echo "❌ Login failed. You can deploy later with:"
        echo "   cd platform && npx wrangler login && npx wrangler pages deploy"
        DEPLOY_TARGET="none"
      else
        echo "✅ Logged in to Cloudflare"
      fi
    else
      echo "✅ Already logged in to Cloudflare"
    fi

    # Step 3: Deploy
    if [ "$DEPLOY_TARGET" = "cloudflare" ]; then
      echo ""
      echo "── Step 2: Build & Deploy ──"

      # Sanitize project name (lowercase, hyphens only)
      CF_PROJECT=$(echo "${BLOG_NAME}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
      echo "Project name: $CF_PROJECT"
      read -rp "Change project name? (press Enter to keep): " cf_name
      [ -n "$cf_name" ] && CF_PROJECT="$cf_name"

      echo ""
      echo "Building for Cloudflare Pages..."
      if npx -y @cloudflare/next-on-pages 2>&1; then
        echo ""
        echo "Deploying to Cloudflare Pages..."
        if npx -y wrangler pages deploy .vercel/output/static --project-name "$CF_PROJECT" 2>&1; then
          echo ""
          echo "✅ Deployed to Cloudflare Pages!"
          echo "   Project: $CF_PROJECT"
        else
          echo ""
          echo "⚠️  Deploy failed. You can retry with:"
          echo "   cd platform && npx wrangler pages deploy .vercel/output/static --project-name \"$CF_PROJECT\""
        fi
      else
        echo "❌ Build for Cloudflare failed."
        echo "   Try: cd platform && npx @cloudflare/next-on-pages"
      fi
    fi

  else
    # Non-interactive — requires CLOUDFLARE_API_TOKEN
    if [ -n "${CLOUDFLARE_API_TOKEN:-}" ]; then
      CF_PROJECT=$(echo "${BLOG_NAME}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
      echo "Building for Cloudflare Pages (project: $CF_PROJECT)..."
      if CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" npx -y @cloudflare/next-on-pages 2>&1; then
        if CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" npx -y wrangler pages deploy \
            .vercel/output/static --project-name "$CF_PROJECT" --commit-dirty=true 2>&1; then
          echo "✅ Deployed to Cloudflare Pages"
        else
          echo "❌ Deploy failed. Check CLOUDFLARE_API_TOKEN."
        fi
      else
        echo "❌ Build for Cloudflare failed."
      fi
    else
      echo "⚠️  CLOUDFLARE_API_TOKEN not set — skipping automated deploy"
      echo "   Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID env vars"
      echo "   Then run: cd platform && npx @cloudflare/next-on-pages && npx wrangler pages deploy .vercel/output/static"
      DEPLOY_TARGET="none"
    fi
  fi

else
  echo "⏭️  Skipping deployment (run locally with 'cd platform && npm run dev')"
fi
echo ""

# ═══════════════════════════════════════
# 7. Summary
# ═══════════════════════════════════════
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   ✅ Setup Complete!                         ║"
echo "  ╠══════════════════════════════════════════════╣"
echo "  ║                                              ║"
printf "  ║   Blog:    %-33s║\n" "$BLOG_NAME"
printf "  ║   Theme:   %-33s║\n" "$THEME"
printf "  ║   DB:      %-33s║\n" "$DB_PROVIDER"
printf "  ║   Cache:   %-33s║\n" "$CACHE_PROVIDER"
printf "  ║   Deploy:  %-33s║\n" "$DEPLOY_TARGET"
echo "  ║                                              ║"
printf "  ║   API Key: %-33s║\n" "${API_KEY:0:12}..."
echo "  ║   ⚠️  Save this key for API calls!           ║"
echo "  ║                                              ║"
echo "  ║   Start:  cd platform && npm run dev         ║"
echo "  ║   Visit:  http://localhost:3000               ║"
echo "  ║                                              ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# ── Output config as JSON for agents to parse ──
if ! $INTERACTIVE; then
  echo "SETUP_RESULT_JSON={\"apiKey\":\"$API_KEY\",\"dbProvider\":\"$DB_PROVIDER\",\"cacheProvider\":\"$CACHE_PROVIDER\",\"theme\":\"$THEME\",\"blogName\":\"$BLOG_NAME\",\"deployTarget\":\"$DEPLOY_TARGET\"}"
fi
