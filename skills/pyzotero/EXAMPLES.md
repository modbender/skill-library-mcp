# Pyzotero CLI 使用示例

实用的 Python 脚本使用示例和工作流。

## 目录

1. [基本搜索示例](#基本搜索示例)
2. [高级搜索技巧](#高级搜索技巧)
3. [集合管理](#集合管理)
4. [JSON 输出处理](#json 输出处理)
5. [日常工作流](#日常工作流)
6. [自动化脚本](#自动化脚本)

---

## 基本搜索示例

### 示例 1: 简单关键词搜索

```bash
python3 scripts/zotero_tool.py search -q "machine learning"
```

**输出:**
```
✓ 已连接到本地 Zotero
找到 5 个项目:

1. [journalArticle] Machine Learning: A Probabilistic Perspective
   作者：Kevin P. Murphy
   年份：2012
   标签：machine-learning, probabilistic
   链接：https://www.zotero.org/user/items/ABC123

2. [book] Pattern Recognition and Machine Learning
   作者：Christopher M. Bishop
   年份：2006
   标签：pattern-recognition, machine-learning
   链接：https://www.zotero.org/user/items/DEF456
```

---

### 示例 2: 短语搜索

```bash
python3 scripts/zotero_tool.py search -q "\"deep learning\""
```

搜索精确匹配的短语。

---

### 示例 3: 限制结果数量

```bash
python3 scripts/zotero_tool.py search -q "python" -l 10
```

只显示前 10 个结果。

---

## 高级搜索技巧

### 示例 4: 全文搜索 (包括 PDF)

```bash
python3 scripts/zotero_tool.py search -q "neural networks" --fulltext
```

搜索标题、摘要以及 PDF 附件的全文内容。

---

### 示例 5: 按项目类型过滤

```bash
# 只搜索期刊文章
python3 scripts/zotero_tool.py search -q "machine learning" --itemtype journalArticle

# 只搜索书籍
python3 scripts/zotero_tool.py search -q "python" --itemtype book

# 只搜索会议论文
python3 scripts/zotero_tool.py search -q "deep learning" --itemtype conferencePaper
```

---

### 示例 6: 在特定集合中搜索

```bash
# 首先获取集合 ID
python3 scripts/zotero_tool.py listcollections

# 然后在特定集合中搜索
python3 scripts/zotero_tool.py search --collection ABC123 -q "test"
```

---

### 示例 7: 组合过滤

```bash
# 在特定集合中搜索特定期刊文章
python3 scripts/zotero_tool.py search \
  --collection ABC123 \
  -q "neural networks" \
  --itemtype journalArticle \
  -l 20
```

---

## 集合管理

### 示例 8: 列出所有集合

```bash
python3 scripts/zotero_tool.py listcollections
```

**输出:**
```
✓ 已连接到本地 Zotero
共有 5 个集合:

1. 📁 机器学习
   密钥：ABC123

2. 📁 深度学习
   密钥：DEF456

3. 📁 自然语言处理
   密钥：GHI789
```

---

### 示例 9: JSON 格式输出集合

```bash
python3 scripts/zotero_tool.py listcollections --json
```

---

## JSON 输出处理

### 示例 10: 基本 JSON 输出

```bash
python3 scripts/zotero_tool.py search -q "python" --json
```

---

### 示例 11: 使用 jq 提取标题

```bash
python3 scripts/zotero_tool.py search -q "machine learning" --json | jq '.[].data.title'
```

**输出:**
```
"Machine Learning: A Probabilistic Perspective"
"Pattern Recognition and Machine Learning"
```

---

### 示例 12: 统计结果数量

```bash
python3 scripts/zotero_tool.py search -q "python" --json | jq 'length'
```

**输出:**
```
15
```

---

### 示例 13: 提取作者信息

```bash
python3 scripts/zotero_tool.py search -q "deep learning" --json | \
  jq '.[].data.creators[] | select(.creatorType == "author") | .lastName'
```

---

### 示例 14: 导出到文件

```bash
# 导出为 JSON
python3 scripts/zotero_tool.py search -q "machine learning" --json > results.json

# 导出为文本
python3 scripts/zotero_tool.py search -q "machine learning" > results.txt
```

---

### 示例 15: 生成引用列表

```bash
python3 scripts/zotero_tool.py search -q "machine learning" --json | jq -r '
  .[] | 
  "\(.data.creators[0].lastName // "Unknown") (\(.data.date[:4] // "n.d.")). \(.data.title). \(.data.publicationTitle // "")"
'
```

**输出:**
```
Murphy (2012). Machine Learning: A Probabilistic Perspective. MIT Press
Bishop (2006). Pattern Recognition and Machine Learning. Springer
```

---

## 日常工作流

### 示例 16: 每日文献回顾

```bash
#!/bin/bash
# daily_review.sh

echo "=== 每日文献回顾 ==="
echo "日期：$(date +%Y-%m-%d)"
echo ""

# 搜索最近添加的机器学习文献
echo "📚 机器学习新文献:"
python3 scripts/zotero_tool.py search -q "machine learning" -l 5

echo ""
echo "📚 深度学习新文献:"
python3 scripts/zotero_tool.py search -q "deep learning" -l 5

echo ""
echo "=== 回顾完成 ==="
```

使用方法:
```bash
chmod +x daily_review.sh
./daily_review.sh
```

---

### 示例 17: 按主题整理文献

```bash
#!/bin/bash
# organize_by_topic.sh

topics=("machine learning" "deep learning" "natural language processing" "computer vision")

for topic in "${topics[@]}"; do
  echo "================================"
  echo "主题：$topic"
  echo "================================"
  
  python3 scripts/zotero_tool.py search -q "$topic" --itemtype journalArticle -l 10
  
  echo ""
done
```

---

### 示例 18: 生成阅读清单

```bash
#!/bin/bash
# reading_list.sh

echo "# 阅读清单"
echo "生成时间：$(date)"
echo ""

# 搜索关键主题的文献
python3 scripts/zotero_tool.py search -q "attention mechanism" --json | jq -r '
  .[] | 
  "- [ ] \(.data.title) (\(.data.date[:4] // "n.d."))"
'
```

---

## 自动化脚本

### 示例 19: Python 自动化脚本

```python
#!/usr/bin/env python3
"""
自动搜索并导出文献
"""

import subprocess
import json

def search_zotero(query, limit=10):
    """搜索 Zotero 并返回结果"""
    cmd = [
        'python3', 'scripts/zotero_tool.py',
        'search', '-q', query,
        '--json', '-l', str(limit)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"错误：{result.stderr}")
        return []

def main():
    topics = ["machine learning", "deep learning", "neural networks"]
    
    for topic in topics:
        print(f"\n搜索：{topic}")
        items = search_zotero(topic, limit=5)
        
        for i, item in enumerate(items, 1):
            title = item['data'].get('title', 'N/A')
            print(f"  {i}. {title}")

if __name__ == '__main__':
    main()
```

---

### 示例 20: 定期检查新文献

```python
#!/usr/bin/env python3
"""
定期检查特定主题的新文献
"""

import subprocess
import json
import time
from datetime import datetime

def check_new_items(topic, last_check):
    """检查自上次以来的新文献"""
    cmd = [
        'python3', 'scripts/zotero_tool.py',
        'search', '-q', topic,
        '--json', '-l', '100'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        items = json.loads(result.stdout)
        # 过滤新文献 (简化示例，实际需要比较日期)
        return items[:10]
    return []

def main():
    topics = ["transformer", "attention mechanism"]
    
    while True:
        for topic in topics:
            print(f"\n检查新文献：{topic}")
            items = check_new_items(topic, None)
            
            if items:
                print(f"找到 {len(items)} 篇新文献")
                for item in items[:3]:
                    print(f"  - {item['data'].get('title', 'N/A')}")
            else:
                print("  暂无新文献")
        
        # 每小时检查一次
        time.sleep(3600)

if __name__ == '__main__':
    main()
```

---

## 在线模式示例

### 示例 21: 使用在线 API

```bash
# 设置环境变量
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"

# 搜索
python3 scripts/zotero_tool.py search -q "machine learning"
```

---

### 示例 22: 切换模式

```bash
# 本地模式
export ZOTERO_LOCAL="true"
python3 scripts/zotero_tool.py listcollections

# 在线模式
export ZOTERO_LOCAL="false"
python3 scripts/zotero_tool.py listcollections
```

---

## 故障排除示例

### 示例 23: 调试连接问题

```bash
# 测试本地连接
export ZOTERO_LOCAL="true"
python3 scripts/zotero_tool.py listcollections

# 测试在线连接
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_id"
export ZOTERO_API_KEY="your_key"
python3 scripts/zotero_tool.py listcollections

# 检查环境变量
echo "ZOTERO_LOCAL=$ZOTERO_LOCAL"
echo "ZOTERO_USER_ID=$ZOTERO_USER_ID"
```

---

## 更多资源

- 📖 [QUICKSTART.md](QUICKSTART.md) - 快速入门
- 📚 [INSTALL.md](INSTALL.md) - 安装指南
- 🔧 [SKILL.md](SKILL.md) - 完整命令参考
- 📝 [CHANGELOG_v2.md](CHANGELOG_v2.md) - v2.0.0 更新说明

---

**提示:** 将这些示例脚本保存到 `~/.bin/` 目录并添加到 PATH，方便日常使用！
