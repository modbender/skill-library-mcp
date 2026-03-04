# amap-navigation

高德地图导航与出行助手 - 支持路线规划、实时路况、打车估价、POI搜索

## 快速开始

### 1. 配置 API Key

在工作区根目录 `.env` 文件中添加：

```bash
AMAP_API_KEY=你的高德地图API_Key
```

获取 API Key：
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册/登录账号
3. 创建应用，选择"Web服务"
4. 复制 Key 到 `.env`

### 2. 使用示例

```bash
# 路线规划
node scripts/navigation.js \
  --from "北京站" \
  --to "首都机场" \
  --mode driving

# POI搜索
node scripts/poi_search.js \
  --keyword "川菜" \
  --location "北京市朝阳区三里屯" \
  --radius 1000

# 打车估价
node scripts/taxi_estimate.js \
  --from "杭州东站" \
  --to "西湖风景区" \
  --platforms "didi,gaode"
```

## 功能特性

- ✅ 多种出行方式（驾车/公交/步行/骑行）
- ✅ 智能路线推荐
- ✅ 实时路况查询
- ✅ POI附近搜索
- ✅ 打车费用估算
- ✅ 多平台价格对比

## 文档

详见 [SKILL.md](./SKILL.md)

## 许可证

MIT
