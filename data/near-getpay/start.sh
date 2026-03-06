#!/bin/bash

echo ""
echo "🚀 Starting GetPay Server with localhost.run tunnel..."
echo ""

cd "$(dirname "$0")"

# Start the server
npx ts-node start-tunnel.ts
