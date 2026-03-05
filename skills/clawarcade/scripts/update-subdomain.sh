#!/bin/bash
# Update all Cloudflare subdomain references
# Usage: ./update-subdomain.sh NEW_SUBDOMAIN
# Example: ./update-subdomain.sh clawarcade

if [ -z "$1" ]; then
    echo "Usage: $0 NEW_SUBDOMAIN"
    echo "Example: $0 clawarcade"
    exit 1
fi

OLD="bassel-amin92-76d"
NEW="$1"

echo "Replacing $OLD with $NEW in all files..."

find /home/medici/clawarcade -type f \( -name "*.js" -o -name "*.html" -o -name "*.md" -o -name "*.json" \) -exec sed -i "s/$OLD/$NEW/g" {} \;

echo "Done! Replaced in files:"
grep -r "$NEW" /home/medici/clawarcade --include="*.md" --include="*.js" --include="*.html" -l | head -20
