#!/bin/bash
# Initialize a new Checkly monitoring project

set -e

PROJECT_NAME="${1:-my-monitoring-project}"

echo "🚀 Creating Checkly monitoring project: $PROJECT_NAME"

# Create project
npm create checkly@latest "$PROJECT_NAME" -- --yes

cd "$PROJECT_NAME"

echo "✅ Project created successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  npx checkly login"
echo "  npx checkly test"
echo "  npx checkly deploy"
