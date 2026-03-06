#!/bin/bash
# 并行抓取四个快讯网站内容，输出到 /tmp/news_*.txt
# 用法：bash fetch_news.sh

echo "[1/4] 抓取 BlockBeats..."
curl -s --max-time 15 "https://www.theblockbeats.info/newsflash" \
  -H "User-Agent: Mozilla/5.0" \
  -o /tmp/news_blockbeats.html &

echo "[2/4] 抓取 Odaily..."
curl -s --max-time 15 "https://www.odaily.news/zh-CN/newsflash" \
  -H "User-Agent: Mozilla/5.0" \
  -o /tmp/news_odaily.html &

echo "[3/4] 抓取 PANews..."
curl -s --max-time 15 "https://www.panewslab.com/zh/newsflash" \
  -H "User-Agent: Mozilla/5.0" \
  -o /tmp/news_panews.html &

echo "[4/4] 抓取 CoinDesk..."
curl -s --max-time 15 "https://www.coindesk.com/latest-crypto-news" \
  -H "User-Agent: Mozilla/5.0" \
  -o /tmp/news_coindesk.html &

wait
echo "所有快讯网站抓取完成"
echo "文件: /tmp/news_blockbeats.html /tmp/news_odaily.html /tmp/news_panews.html /tmp/news_coindesk.html"
