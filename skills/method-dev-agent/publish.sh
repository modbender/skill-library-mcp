#!/bin/bash
# Method Dev Agent - One-click publish script
# Author: Teagee Li
# Date: 2026-02-26

echo "============================================"
echo "   Method Dev Agent - One-click Publish"
echo "============================================"
echo ""

cd "$(dirname "$0")"

echo "[1/4] Checking Git config..."
if ! git remote get-url origin &>/dev/null; then
    echo "[INFO] Adding GitHub remote..."
    git remote add origin https://github.com/teagec/t2.git
fi

echo ""
echo "[2/4] Committing code to Git..."
git add .
git commit -m "v0.1.0 ready for publish"

echo ""
echo "[3/4] Pushing to GitHub..."
if ! git push -u origin main; then
    echo "[ERROR] GitHub push failed, check network or permissions"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "[4/4] Publishing to ClawHub..."
echo "Make sure you're logged in to ClawHub (clawhub login)"
clawhub publish . --slug method-dev-agent --name "药品分析色谱方法开发助手" --version 0.1.0 --changelog "MVP: 实验记录、方法库、基础分析、专业版0.03 ETH/月"

echo ""
echo "============================================"
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Published successfully!"
    echo "Visit: https://clawhub.ai/teagec/method-dev-agent"
else
    echo "[ERROR] Publish failed"
    echo "Check: 1) ClawHub login status  2) Network connection"
fi
echo "============================================"
read -p "Press Enter to exit..."
