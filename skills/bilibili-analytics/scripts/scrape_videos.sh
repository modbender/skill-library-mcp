#!/bin/bash
# Bilibili 视频搜索抓取脚本
# 使用方法: ./scrape_videos.sh "关键词" 页数

KEYWORD="${1:-Rollercraft}"
PAGES="${2:-5}"
OUTPUT_FILE="bilibili_data_${KEYWORD}_$(date +%Y%m%d_%H%M%S).json"

echo "开始抓取 Bilibili 关键词: $KEYWORD"
echo "页数: $PAGES"
echo "输出文件: $OUTPUT_FILE"

# 初始化数组
echo "[" > "$OUTPUT_FILE"

for page in $(seq 1 $PAGES); do
  echo "正在抓取第 $page 页..."
  
  # 构建URL
  if [ $page -eq 1 ]; then
    URL="https://search.bilibili.com/all?keyword=${KEYWORD}"
  else
    OFFSET=$(( ($page - 1) * 30 ))
    URL="https://search.bilibili.com/all?keyword=${KEYWORD}&page=$page&o=$OFFSET"
  fi
  
  # 打开页面
  agent-browser open "$URL" --timeout 15000 2>&1 > /dev/null
  
  # 抓取数据
  DATA=$(agent-browser eval '
const videos = [];
document.querySelectorAll(".bili-video-card").forEach((card) => {
  const title = card.querySelector(".bili-video-card__info--tit")?.textContent.trim() || "";
  const author = card.querySelector(".bili-video-card__info--author")?.textContent.trim() || "";
  const date = card.querySelector(".bili-video-card__info--date")?.textContent.trim() || "";
  const stats = card.querySelectorAll(".bili-video-card__stats--item");
  const playCount = stats[0]?.textContent.trim() || "0";
  const commentCount = stats[1]?.textContent.trim() || "0";
  videos.push({title, author, date, playCount, commentCount});
});
JSON.stringify(videos, null, 2);
' 2>&1)
  
  # 写入文件
  if [ $page -eq 1 ]; then
    echo "$DATA" | sed '1d;$d' >> "$OUTPUT_FILE"
  else
    echo "," >> "$OUTPUT_FILE"
    echo "$DATA" | sed '1d;$d' >> "$OUTPUT_FILE"
  fi
  
  # 避免请求过快
  sleep 2
done

# 关闭数组
echo "" >> "$OUTPUT_FILE"
echo "]" >> "$OUTPUT_FILE"

# 关闭浏览器
agent-browser close 2>&1 > /dev/null

echo "抓取完成！数据已保存到: $OUTPUT_FILE"
echo "总视频数: $(jq 'length' "$OUTPUT_FILE")"
