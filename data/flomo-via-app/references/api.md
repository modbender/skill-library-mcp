# Flomo API Reference

> ⚠️ **需要 PRO 会员权限** — API 和 URL Scheme 功能需要 [flomo PRO 会员](https://flomoapp.com/mine?source=incoming_webhook) 才能使用。

flomo 提供了 API 和 URL Scheme 两种方式与其他软件交互。

---

## URL Scheme（推荐）

通过 URL Scheme 直接打开 flomo 应用并填入内容，支持文本和图片。

### 基础格式
```
flomo://create?content=<encoded-content>
```

### 路径
```
flomo://create
```

### 参数

| 参数名 | 含义 | 必传 | 最大长度 | 编码方式 |
|--------|------|------|----------|----------|
| `content` | 文本内容 | 否 | 5000 字（encode 前） | `encodeURIComponent` |
| `image_urls` | 图片 URL 数组 | 否 | 最多 9 个 URL | `encodeURIComponent(JSONString(Array))` |

### 示例

**纯文本笔记：**
```
flomo://create?content=%E7%AC%94%E8%AE%B0%E5%86%85%E5%AE%B9
```

**带图片的笔记：**
```
flomo://create?image_urls=%5B%22https%3A%2F%2Fexample.com%2Fimage1.png%22%2C%22https%3A%2F%2Fexample.com%2Fimage2.png%22%5D&content=%E7%AC%94%E8%AE%B0%E5%86%85%E5%AE%B9
```

**手机端测试链接：**
[在安装了 flomo app 的手机上点击试试](flomo://create?image_urls=%5B%22https%3A%2F%2Fflomo-resource.oss-cn-shanghai.aliyuncs.com%2Fhome%2Flogo.png!web%22%2C%22https%3A%2F%2Fflomo-resource.oss-cn-shanghai.aliyuncs.com%2Fhome%2F202103%2Fpic_feature_graph.png!web%22%5D&content=%E7%AC%94%E8%AE%B0%E5%86%85%E5%AE%B9)

### macOS 使用示例

```bash
# 发送纯文本
open "flomo://create?content=Hello%20World"

# 发送带标签的文本（标签直接写在内容中）
open "flomo://create?content=%E8%AF%BB%E4%B9%A6%E7%AC%94%E8%AE%B0%20%23%E8%AF%BB%E4%B9%A6"

# 发送多行文本（使用 %0A 作为换行符）
open "flomo://create?content=Line1%0ALine2%0ALine3"
```

### 限制

- **content**: 最多 5000 字（encode 前）
- **image_urls**: 最多 9 张图片
- 需要 flomo iOS/Android/macOS 应用支持

---

## Webhook API

通过 HTTP POST 请求发送笔记到 flomo，无需打开应用。

### 获取 Webhook 地址

1. 访问 [flomo 设置页面](https://flomoapp.com/mine?source=incoming_webhook)
2. 复制你的专属 Webhook URL

格式：
```
https://flomoapp.com/iwh/{your-webhook-token}
```

### 请求格式

```bash
curl -X POST https://flomoapp.com/iwh/xxxxxxxx \
  -H "Content-Type: application/json" \
  -d '{"content": "笔记内容 #标签"}'
```

### 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 笔记内容，支持 Markdown 格式和 `#标签` |

### 完整示例

```bash
# 基础用法
curl -X POST https://flomoapp.com/iwh/xxxxxxxxx \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from API"}'

# 带标签
curl -X POST https://flomoapp.com/iwh/xxxxxxxxx \
  -H "Content-Type: application/json" \
  -d '{"content": "读书笔记 #认知 #学习"}'

# 多行内容
curl -X POST https://flomoapp.com/iwh/xxxxxxxxx \
  -H "Content-Type: application/json" \
  -d '{"content": "第一行\n第二行\n第三行"}'
```

### 响应

**成功：**
```json
{
  "code": 0,
  "message": "ok"
}
```

**失败：**
```json
{
  "code": -1,
  "message": "错误信息"
}
```

### 限制

- 需要 PRO 会员
- 有调用频率限制（具体限制参见官方文档）

---

## URL Scheme vs Webhook 对比

| 特性 | URL Scheme | Webhook API |
|------|------------|-------------|
| 需要打开应用 | ✅ 是 | ❌ 否 |
| 支持图片 | ✅ 是 | ❌ 否（仅文本） |
| 服务器/自动化场景 | ❌ 不适用 | ✅ 适用 |
| 响应速度 | 即时 | 依赖网络 |
| 跨平台 | 需安装 app | 任何支持 HTTP 的环境 |

---

## 更多资源

- [flomo 扩展中心](https://flomoapp.com/mine?source=incoming_webhook) — 使用别人提供的扩展工具
- [第三方工具提交](https://github.com/flomoapp/3rd-party-tools) — 提交你的作品
- [PRO 会员购买](https://flomoapp.com/mine?source=incoming_webhook)

---

*文档更新时间：2025-02-08*
*来源：[flomo 官方帮助文档](https://help.flomoapp.com/advance/api.html)*
