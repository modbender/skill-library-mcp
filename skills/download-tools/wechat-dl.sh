#!/bin/bash

# =============================================================================
# 微信文章下载工具 v2.0
# =============================================================================
# 使用: ./wechat-dl.sh "链接" [输出名]
# =============================================================================

URL="$1"
OUTPUT="${2:-wechat_article}"

if [ -z "$URL" ]; then
    echo "用法: $0 <微信链接> [输出文件名]"
    echo "示例: $0 \"https://mp.weixin.qq.com/s/xxx\" my_article"
    exit 1
fi

echo "============================================"
echo "  微信文章下载工具"
echo "============================================"
echo ""
echo "📥 正在下载: $URL"

curl -s -L "$URL" \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
    > /tmp/wechat_tmp.html

if ! grep -q "js_content" /tmp/wechat_tmp.html; then
    echo "❌ 获取页面失败"
    rm -f /tmp/wechat_tmp.html
    exit 1
fi

# 提取正文
sed -n '/id="js_content"/,/<\/div>/p' /tmp/wechat_tmp.html | \
    sed 's/<[^>]*>//g' | \
    sed 's/&nbsp;/ /g' | \
    sed 's/&amp;/\&/g' | \
    sed 's/&lt;/</g' | \
    sed 's/&gt;/>/g' | \
    sed 's/&quot;/"/g' | \
    sed 's/[[:space:]]\+/ /g' > "${OUTPUT}.txt"

rm -f /tmp/wechat_tmp.html

if [ -s "${OUTPUT}.txt" ]; then
    echo "✅ 成功保存到: ${OUTPUT}.txt"
    echo "📊 文件大小: $(ls -lh ${OUTPUT}.txt | awk '{print $5}')"
else
    echo "❌ 提取内容失败，可能需要微信登录"
    exit 1
fi
