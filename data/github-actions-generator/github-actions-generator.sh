#!/bin/bash
# GitHub Actions Generator

TYPE="${1:-ci}"
LANG="${2:-node}"

mkdir -p .github/workflows

case "$TYPE" in
  ci)
    cat > .github/workflows/ci.yml << 'YML'
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
YML
    ;;
  deploy)
    cat > .github/workflows/deploy.yml << 'YML'
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install && npm run build
      - name: Deploy
        run: echo "Deploying..."
YML
    ;;
esac

echo "✅ GitHub Actions workflow generated!"
