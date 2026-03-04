# 电商平台API文档

本文档记录各电商平台的API接口、抓取策略和注意事项。

## 京东 (JD.com)

### 官方API
- **搜索API**: `https://so.m.jd.com/ware/search.action`
- **商品详情API**: `https://item.m.jd.com/product/{sku_id}.html`
- **价格API**: `https://p.3.cn/prices/mgets`

### 抓取策略
1. **移动端页面**：使用移动端API，限制较少
2. **SKU识别**：通过商品URL提取SKU ID
3. **价格获取**：调用价格API获取实时价格

### 注意事项
- 需要处理登录状态获取会员价
- 自营和第三方商品价格获取方式不同
- 注意地区库存和价格差异

## 淘宝/天猫 (Taobao/Tmall)

### 官方API
- **搜索API**: `https://s.taobao.com/search`
- **商品详情API**: `https://detail.tmall.com/item.htm`
- **价格API**: 通常需要解析页面数据

### 抓取策略
1. **页面解析**：使用浏览器自动化获取完整页面
2. **数据提取**：从页面中提取价格、评价等信息
3. **反爬应对**：需要处理淘宝的强反爬机制

### 注意事项
- 淘宝的反爬非常严格，需要频繁更换IP
- 天猫商品通常有更稳定的数据结构
- 注意区分普通店铺和品牌官方店

## 拼多多 (Pinduoduo)

### 官方API
- **搜索API**: `https://mobile.yangkeduo.com/search_result.html`
- **商品详情API**: `https://mobile.yangkeduo.com/goods.html`
- **价格API**: 价格信息在页面中

### 抓取策略
1. **移动端优先**：拼多多主要面向移动端
2. **百亿补贴**：特殊标识需要单独处理
3. **团购价格**：注意团购价和单独购买价的区别

### 注意事项
- 拼多多价格波动较大
- 注意区分普通商品和百亿补贴商品
- 运费政策复杂，需要仔细计算

## 通用抓取工具

### 推荐工具
1. **Playwright**：浏览器自动化，支持JavaScript渲染
2. **Requests**：简单HTTP请求，适合API调用
3. **BeautifulSoup**：HTML解析

### 配置示例
```python
# Playwright配置
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    )
    page = await context.new_page()
```

### 反爬应对
1. **随机延迟**：请求间添加随机延迟
2. **轮换代理**：使用代理IP池
3. **更换UA**：定期更换用户代理
4. **验证码处理**：准备验证码识别方案

## 数据存储格式

### 商品信息结构
```json
{
  "platform": "jd",
  "product_id": "100000000001",
  "title": "商品标题",
  "price": 2999.00,
  "original_price": 3499.00,
  "discount": "满2999减300",
  "shipping_fee": 0.00,
  "rating": 4.8,
  "review_count": 10000,
  "shop_name": "官方旗舰店",
  "shop_rating": 4.9,
  "url": "https://item.jd.com/100000000001.html",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 比较结果结构
```json
{
  "query": "iPhone 15",
  "results": [
    {
      "platform": "jd",
      "price": 5999,
      "total_cost": 5999,
      "score": 85,
      "recommendation": "推荐",
      "reason": "价格最低，官方正品"
    }
  ],
  "best_choice": {
    "platform": "jd",
    "price": 5999,
    "reason": "综合性价比最高"
  }
}
```

## 更新维护

### 监控项目
1. **API变化**：定期检查各平台API是否变化
2. **页面结构**：监控页面HTML结构变化
3. **反爬策略**：关注平台反爬机制更新

### 维护计划
- 每周检查一次各平台抓取脚本
- 每月更新一次API文档
- 根据用户反馈优化抓取策略