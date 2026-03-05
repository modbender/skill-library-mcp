# Product Description Generator

Generate compelling product descriptions for e-commerce platforms.

## Platforms

- Taobao, Tmall, JD, Pinduoduo
- Shopify, Amazon
- Instagram, Facebook

## Usage

```bash
npx product-description
```

## API

```typescript
import { generateDescription } from 'product-description';

const result = await generateDescription({
  product: "无线蓝牙耳机",
  platform: "xiaohongshu",
  tone: "种草",
  features: ["降噪", "30小时续航"]
});
```
