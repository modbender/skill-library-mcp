---
name: amap-traffic
description: 高德地图实时路况查询与最优自驾路线规划技能。基于高德交通态势API和路径规划API，提供实时拥堵信息和最快路线建议。
metadata: 
  {
    "openclaw": 
      { 
        "emoji": "🚗", 
        "requires": { "env": ["AMAP_KEY"] }, 
        "primaryEnv": "AMAP_KEY",
        channels: ["webchat", "dingtalk", "qq"]
      },
  }
---

# 高德实时路况与路线规划

## 概述
本技能通过高德地图API实现：
1. **实时路况查询**：获取指定道路/区域的拥堵状态
2. **智能路线规划**：基于实时路况计算最快自驾路线
3. **多方案对比**：提供时间、距离、费用等维度的路线比较

## 🔑 API Key 配置
1. 访问 [高德开放平台](https://console.amap.com/) 创建 Key
2. 在 OpenClaw Web 配置页面设置：  
   **地址**: http://127.0.0.1:18789/skills  
   **配置文件字段**: `skills.entries.amap-traffic.AMAP_KEY` in `openclaw.json`  
   **值**: 你的高德API Key

> **注意**: 本技能每次调用时都会重新读取 `openclaw.json` 中的最新 `AMAP_KEY`，支持前端动态更新密钥后立即生效。

## API 使用说明
### 1. 实时路况查询
```bash
curl "https://restapi.amap.com/v3/traffic/status/road?roadid={道路ID}&key={动态读取的AMAP_KEY}"
```

### 2. 智能路线规划（含实时路况）
```bash
curl "https://restapi.amap.com/v3/direction/driving?origin={起点坐标}&destination={终点坐标}&strategy=2&key={动态读取的AMAP_KEY}"
```
- `strategy=2`：优先考虑实时路况的最快路线

## 路况状态说明
- **畅通**：🟢 绿色（速度 > 40km/h）
- **缓行**：🟡 黄色（20-40km/h）
- **拥堵**：🔴 红色（< 20km/h）
- **严重拥堵**：🟣 紫红色（< 10km/h）

## 资源

### scripts/
包含高德实时路况查询和路线规划的核心脚本。

#### scripts/amap_traffic.py
Python 脚本，实现完整的实时路况查询和最优路线规划功能。
**每次执行时都会从 `/home/admin/.openclaw/openclaw.json` 读取最新的 AMAP_KEY**，
确保前端动态更新密钥后立即生效。