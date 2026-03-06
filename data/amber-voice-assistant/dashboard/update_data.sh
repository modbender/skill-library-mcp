#!/bin/bash

# Update Call Log Dashboard Data
# Processes latest Twilio/OpenAI SIP bridge logs and refreshes dashboard data

echo "🔄 Updating call log dashboard data..."

# Change to dashboard directory
cd "$(dirname "$0")"

# Run the data processing script
echo "📞 Processing call logs..."
node process_logs.js

if [ $? -eq 0 ]; then
    echo "✅ Call log data updated successfully!"
    echo "🌐 Open index.html to view the dashboard"
    
    # Optional: Open dashboard in default browser (uncomment if desired)
    # open index.html
else
    echo "❌ Error updating call log data"
    exit 1
fi
