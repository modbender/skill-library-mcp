#!/bin/bash
# ClawArcade Tournament Deployment Script
# Run this from the clawarcade directory

set -e

echo "🏆 ClawArcade Tournament System Deployment"
echo "==========================================="
echo ""

# Step 1: Apply D1 schema
echo "1️⃣ Applying tournament database schema..."
cd api-worker
wrangler d1 execute clawmd-db --remote --file=tournament-schema.sql
echo "   ✅ Schema applied"
echo ""

# Step 2: Deploy API worker
echo "2️⃣ Deploying API worker..."
wrangler deploy
echo "   ✅ API worker deployed"
echo ""

# Step 3: Deploy site to surge
echo "3️⃣ Deploying site to surge..."
cd ..
surge . clawarcade.surge.sh
echo "   ✅ Site deployed"
echo ""

# Step 4: Create first tournament
echo "4️⃣ Creating inaugural tournament..."
cd scripts
node create-tournament.js
echo ""

echo "==========================================="
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Visit https://clawarcade.surge.sh/tournament.html"
echo "  2. Verify tournament appears correctly"
echo "  3. Test registration with a test account"
echo "  4. Announce the tournament!"
