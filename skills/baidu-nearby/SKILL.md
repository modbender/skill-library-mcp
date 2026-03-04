# Baidu Skills for OpenClaw

百度能力集合 - 提供百度搜索和百度地图路线规划功能。

## 功能

1. **baidu_search** - 百度搜索
2. **baidu_direction** - 百度地图路线规划
3. **baidu_nearby** - 附近场所推荐（餐饮、娱乐、景点等）

## 配置

需要设置百度API Key：

```bash
export BAIDU_API_KEY="你的百度AK"
```

获取AK：
1. 访问 https://lbsyun.baidu.com/
2. 登录百度账号，申请成为开发者
3. 创建应用获取AK

## 使用方法

### 百度搜索

```bash
python ~/.openclaw/workspace/skills/baidu/baidu_search.py "搜索关键词" [结果数量]
```

### 路线规划

```bash
python ~/.openclaw/workspace/skills/baidu/baidu_direction.py "起点地址" "终点地址" [driving|riding|walking|transit]
```

### 附近场所推荐

```bash
python ~/.openclaw/workspace/skills/baidu/baidu_nearby.py "位置" [类别] [半径(米)] [数量]
```

**支持的类别：**
- 餐饮/美食/餐厅 - 餐厅、咖啡厅、小吃等
- 娱乐/休闲 - KTV、电影院、公园、健身房等
- 景点/旅游/景区 - 旅游景点、博物馆、古迹等
- 酒店/住宿 - 酒店、宾馆
- 购物/商场/超市 - 商场、超市、便利店
- 交通/地铁/公交 - 交通设施

**示例：**
```bash
# 搜索三里屯附近的美食（半径1公里，返回5个）
python ~/.openclaw/workspace/skills/baidu/baidu_nearby.py "北京市朝阳区三里屯" 餐饮 1000 5

# 搜索天安门附近的景点（半径5公里，返回10个）
python ~/.openclaw/workspace/skills/baidu/baidu_nearby.py "天安门" 景点 5000 10

# 使用坐标搜索
python ~/.openclaw/workspace/skills/baidu/baidu_nearby.py "39.9,116.4" 娱乐
```

## 依赖

```bash
pip install requests beautifulsoup4
```
