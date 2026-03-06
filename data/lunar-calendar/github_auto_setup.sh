#!/bin/bash
# 自动化GitHub设置脚本
# 需要设置 GITHUB_TOKEN 环境变量

if [ -z "$GITHUB_TOKEN" ]; then
    echo "请设置 GITHUB_TOKEN 环境变量"
    exit 1
fi

# 创建仓库
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "lunar-birthday-reminder",
    "description": "农历生日提醒系统 - 专业农历计算系统 v0.9.0",
    "private": false
  }'

# 初始化本地仓库
git init
git add .
git commit -m "农历生日提醒系统 v0.9.0 初始提交"
git branch -M main
git remote add origin https://$GITHUB_TOKEN@github.com/xiamuciqing/lunar-birthday-reminder.git
git push -u origin main

# 创建标签
git tag v0.9.0
git push origin v0.9.0

echo "✅ GitHub仓库创建完成！"
