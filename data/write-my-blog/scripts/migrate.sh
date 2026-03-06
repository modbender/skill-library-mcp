#!/usr/bin/env bash
# ═══ Database Migration ═══
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(dirname "$SCRIPT_DIR")/platform"

echo "🗄️  Running database migrations..."
cd "$PLATFORM_DIR"

# Load env vars
if [ -f .env.local ]; then
  export $(grep -v '^#' .env.local | xargs)
fi

# Run migration via Node
node -e "
const { getDatabase } = require('./src/lib/db/index.ts');
(async () => {
  const db = await getDatabase();
  await db.migrate();
  console.log('✅ Migration complete');
  await db.close();
})().catch(err => {
  console.error('❌ Migration failed:', err.message);
  process.exit(1);
});
"

echo "✅ Migrations complete"
