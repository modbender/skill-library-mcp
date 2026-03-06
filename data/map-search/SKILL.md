---
name: map-search
description: 更适合中国体质宝宝的地图搜索工具，支持高德、百度、腾讯地图聚合搜索。
metadata:
  openclaw:
    emoji: "🗺️"
    requires:
      bins: ["python3"]
    env:
      - "AMAP_API_KEY"
      - "BAIDU_MAP_API_KEY"
      - "TENCENT_MAP_API_KEY"
---

# 🗺️ Map Search Skill

多地图聚合搜索工具，支持高德、百度、腾讯。

## 核心代码

```python
#!/usr/bin/env python3
"""地图搜索工具"""

import os
import json
import requests

# ========== 配置路径 ==========
CONFIG_PATH = os.path.expanduser("~/.config/openclaw/map_config.json")


# ========== 读取配置函数 ==========
def get_config():
    """从配置文件读取所有配置（API Keys + 优先级）"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return {
                "api_keys": {
                    "amap": config.get("amap", {}).get("api_key", ""),
                    "baidu": config.get("baidu", {}).get("api_key", ""),
                    "tencent": config.get("tencent", {}).get("api_key", "")
                },
                "priority": config.get("priority", ["amap", "tencent", "baidu"])
            }
    
    # 回退到环境变量
    return {
        "api_keys": {
            "amap": os.getenv("AMAP_API_KEY", ""),
            "baidu": os.getenv("BAIDU_MAP_API_KEY", ""),
            "tencent": os.getenv("TENCENT_MAP_API_KEY", "")
        },
        "priority": ["amap", "tencent", "baidu"]
    }


# ========== 初始化全局变量 ==========
CONFIG = get_config()           # 获取配置
API_KEYS = CONFIG["api_keys"]   # 提取 API Keys
PRIORITY = CONFIG["priority"]   # 提取优先级

AMAP_KEY = API_KEYS["amap"]
BAIDU_KEY = API_KEYS["baidu"]
TENCENT_KEY = API_KEYS["tencent"]


# ========== 核心搜索函数 ==========
def search_maps(keyword, region="全国", priority=None):
    """地图聚合搜索"""
    if priority is None:
        priority = PRIORITY  # 使用配置文件中的优先级
    
    results = {}
    
    # 高德搜索
    if "amap" in priority and AMAP_KEY:
        url = f"https://restapi.amap.com/v3/place/text?key={AMAP_KEY}&keywords={keyword}&city={region}&output=json"
        r = requests.get(url, timeout=5).json()
        if r.get("status") == "1":
            results["高德"] = [{"name": p["name"], "address": p["address"], "location": p["location"]}
                              for p in r.get("pois", [])[:5]]
    
    # 百度搜索
    if "baidu" in priority and BAIDU_KEY:
        url = f"https://api.map.baidu.com/place/v2/search?query={keyword}&region={region}&ak={BAIDU_KEY}&output=json"
        r = requests.get(url, timeout=5).json()
        if r.get("status") == 0:
            results["百度"] = [{"name": p["name"], "address": p.get("address", ""), "location": p.get("location", "")}
                             for p in r.get("results", [])[:5]]
    
    # 腾讯搜索
    if "tencent" in priority and TENCENT_KEY:
        url = f"https://apis.map.qq.com/ws/place/v1/search?keyword={keyword}&region={region}&key={TENCENT_KEY}&output=json"
        r = requests.get(url, timeout=5).json()
        if r.get("status") == 0:
            results["腾讯"] = [{"name": p["name"], "address": p.get("address", ""), "location": p.get("location", "")}
                             for p in r.get("data", [])[:5]]
    
    return results


# ========== 主入口 ==========
if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else "咖啡馆"
    region = sys.argv[2] if len(sys.argv) > 2 else "上海"
    
    results = search_maps(keyword, region)
    
    for source, items in results.items():
        print(f"\n【{source}】")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item['name']}")
            print(f"     地址: {item['address']}")
```

## 使用方式

### 1. 通过 exec 调用
```bash
python /root/.openclaw/workspace/skills/map-search/map_search.py "咖啡馆" "上海"
```

### 2. 封装成 CLI 工具
```bash
# 创建软链接
ln -s /root/.openclaw/workspace/skills/map-search/map_search.py /usr/local/bin/map-search

# 直接使用
map-search "火锅" "北京"
map-search "酒店" "深圳"
```

## 配置文件

**路径：** `~/.config/openclaw/map_config.json`

```json
{
  "amap": {
    "api_key": "你的高德API Key"
  },
  "baidu": {
    "api_key": "你的百度API Key"
  },
  "tencent": {
    "api_key": "你的腾讯API Key"
  },
  "priority": ["amap", "tencent", "baidu"]
}
```

### 设置优先级
```json
"priority": ["amap", "tencent", "baidu"]
```
- `"amap"` - 高德
- `"baidu"` - 百度
- `"tencent"` - 腾讯

按数组顺序搜索，找到一个有效结果就停止。

## 环境变量（备选）

如果配置文件不存在，会回退到环境变量：
```bash
export AMAP_API_KEY="你的高德Key"
export BAIDU_MAP_API_KEY="你的百度Key"
export TENCENT_MAP_API_KEY="你的腾讯Key"
```

## API Keys 申请

| 平台 | 地址 |
|------|------|
| 高德 | https://lbs.amap.com/ |
| 百度 | https://lbsyun.baidu.com/ |
| 腾讯 | https://lbs.qq.com/ |

## 输出示例

### 关键词搜索
```
【高德】
  1. 星巴克(人民广场店)
     地址: 黄浦区南京西路123号
  2. 瑞幸咖啡(来福士店)
     地址: 黄浦区西藏中路268号
```

### 附近搜索
```
🔍 附近搜索: 咖啡馆 (半径 2000 米)
正在获取当前位置...
当前位置: 经度 121.47, 纬度 31.23

【高德】
  1. 星巴克(人民广场店)
     地址: 黄浦区南京西路123号
     距离: 520米
  2. 瑞幸咖啡(来福士店)
     地址: 黄浦区西藏中路268号
     距离: 890米
```

## 🆕 附近搜索功能

### 自动获取当前位置（通过 IP 定位）
```bash
python /root/.openclaw/workspace/skills/map-search/map_search.py --nearby -k "咖啡馆"
```

### 指定经纬度
```bash
python /root/.openclaw/workspace/skills/map-search/map_search.py --nearby -k "咖啡馆" --lat 31.230416 --lng 121.473701
```

### 指定搜索半径
```bash
python /root/.openclaw/workspace/skills/map-search/map_search.py --nearby -k "火锅" -r 1000
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--nearby` 或 `-n` | 启用附近搜索模式 | `--nearby` |
| `-k` 或 `--keyword` | 搜索关键词 | `-k "咖啡馆"` |
| `--lat` | 纬度 | `--lat 31.230416` |
| `--lng` | 经度 | `--lng 121.473701` |
| `-r` 或 `--radius` | 搜索半径（米，默认2000） | `-r 1000` |

### 使用场景示例

| 场景 | 命令 |
|------|------|
| 搜附近咖啡馆 | `map-search --nearby -k "咖啡馆"` |
| 搜附近1公里的火锅 | `map-search --nearby -k "火锅" -r 1000` |
| 搜指定位置附近的酒店 | `map-search --nearby -k "酒店" --lat 39.9 --lng 116.4` |

## 注意事项

- 需要安装 `requests` 库: `pip install requests`
- 每个地图 API 有每日调用次数限制
- 配置文件优先级 > 环境变量
- 附近搜索需要配置高德 API Key（用于 IP 定位）
```
