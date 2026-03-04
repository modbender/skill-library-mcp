# Environment
# Options: development, production
ENV=production

# Security (REQUIRED in production - must be changed from defaults)
# Generate secure random strings for these values
SECRET_KEY=change-me-in-production-use-a-real-secret-key
API_KEY_SALT=change-me-salt

# Frontend URL (REQUIRED in production)
# The public URL where your frontend will be accessible
FRONTEND_URL=http://YOUR_VM_IP
# Or if you have a domain:
# FRONTEND_URL=https://yourdomain.com

# Database URLs
# Defaults use SQLite in /home/moltfund/molt-data/ directory
DATABASE_URL_DEV=sqlite+aiosqlite:///./data/dev.db
DATABASE_URL_PROD=sqlite+aiosqlite:///./data/prod.db

# Email Configuration (optional for MVP)
# Sign up at https://resend.com and add your domain
RESEND_API_KEY=
FROM_EMAIL=noreply@moltfundme.com

# Blockchain API Keys (optional, but recommended for higher rate limits)
BLOCKCYPHER_API_TOKEN=
HELIUS_API_KEY=
ALCHEMY_API_KEY=
BASE_RPC_URL=https://mainnet.base.org

# Background Job Configuration
BALANCE_POLL_INTERVAL_SECONDS=120

# Server Configuration
UVICORN_WORKERS=2
LOG_LEVEL=INFO
