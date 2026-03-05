# 在 OpenClaw 中使用 Pyzotero CLI

本文档说明如何在 OpenClaw 会话中使用 pyzotero-cli 技能。

## 快速使用

### 1. 确保已安装 pyzotero 库

```bash
pipx install pyzotero
```

### 2. 配置环境变量 (可选)

在 OpenClaw 会话中设置:

```bash
export ZOTERO_LOCAL="true"  # 本地模式 (默认)
```

或在线模式:

```bash
export ZOTERO_LOCAL="false"
export ZOTERO_USER_ID="your_user_id"
export ZOTERO_API_KEY="your_api_key"
```

### 3. 在 OpenClaw 中使用

**搜索文献:**
```
/python3 /root/.openclaw/workspace/skills/pyzotero-cli/scripts/zotero_tool.py search -q "machine learning"
```

**列出集合:**
```
/python3 /root/.openclaw/workspace/skills/pyzotero-cli/scripts/zotero_tool.py listcollections
```

## 在 OpenClaw 技能中使用

您可以在其他 OpenClaw 技能或脚本中调用 pyzotero:

```python
import subprocess

def search_zotero(query):
    cmd = [
        'python3',
        '/root/.openclaw/workspace/skills/pyzotero-cli/scripts/zotero_tool.py',
        'search', '-q', query,
        '-l', '10'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

## 每日文献推送示例

创建一个定时任务脚本:

```python
#!/usr/bin/env python3
"""
每日眼科学文献推送 (示例)
"""

import subprocess
import json

def get_literature(topic, limit=10):
    """获取指定主题的文献"""
    cmd = [
        'python3',
        '/root/.openclaw/workspace/skills/pyzotero-cli/scripts/zotero_tool.py',
        'search', '-q', topic,
        '--json', '-l', str(limit)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []

def format_literature(items):
    """格式化文献列表"""
    text = f"📚 找到 {len(items)} 篇文献:\n\n"
    
    for i, item in enumerate(items, 1):
        data = item.get('data', {})
        title = data.get('title', '无标题')
        authors = []
        
        for c in data.get('creators', [])[:2]:
            if c.get('lastName'):
                authors.append(c['lastName'])
        
        year = data.get('date', '')[:4] if data.get('date') else 'n.d.'
        
        text += f"{i}. **{title}**\n"
        if authors:
            text += f"   作者：{', '.join(authors)}\n"
        text += f"   年份：{year}\n\n"
    
    return text

if __name__ == '__main__':
    # 搜索眼科学文献
    items = get_literature('ophthalmology', limit=10)
    text = format_literature(items)
    print(text)
```

## 注意事项

1. **本地模式**: 确保 Zotero 7+ 正在运行并启用本地 API
2. **在线模式**: 确保 API 密钥有效且有读取权限
3. **路径**: 使用绝对路径 `/root/.openclaw/workspace/skills/pyzotero-cli/scripts/zotero_tool.py`
4. **Python**: 确保 Python 3 已安装并可访问

## 相关文档

- [SKILL.md](SKILL.md) - 完整技能文档
- [QUICKSTART.md](QUICKSTART.md) - 快速入门
- [EXAMPLES.md](EXAMPLES.md) - 使用示例
- [INSTALL.md](INSTALL.md) - 安装指南
