# Product Description Generator

Generate compelling product descriptions for e-commerce platforms.

## Supported Platforms

- **Chinese**: Taobao, Tmall, JD, Pinduoduo, Xiaohongshu
- **International**: Amazon, Shopify, eBay
- **Social**: Instagram, Facebook, TikTok Shop

## Usage

### Interactive Mode

```bash
npx product-description
```

### API Mode

```typescript
import { generateProductDescription } from 'product-description';

const result = await generateProductDescription({
  product: "无线蓝牙降噪耳机",
  platform: "xiaohongshu",
  tone: "种草",
  highlights: ["-45dB降噪", "30小时续航", "HiFi音质"]
});
```

## Input Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| product | string | required | Product name |
| platform | taobao/tmall/jd/xiaohongshu/amazon/shopify | xiaohongshu | Target platform |
| tone | promotional/emotional/humor/professional | promotional | Writing style |
| highlights | string[] | [] | Key product features |

## Output Format

```typescript
{
  title: "种草标题",
  description: "产品描述正文",
  sellingPoints: ["卖点1", "卖点2"],
  tags: ["#标签1", "#标签2"]
}
```
