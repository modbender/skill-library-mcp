# Social Media Scheduler

Optimize posting schedule for maximum engagement.

## Platforms

- **Chinese**: Douyin, Xiaohongshu, WeChat, Weibo, Kuaishou
- **International**: Instagram, Twitter, Facebook, LinkedIn

## Usage

```bash
npx social-scheduler
```

## API

```typescript
import { getSchedule } from 'social-scheduler';

const schedule = await getSchedule({
  platform: 'xiaohongshu',
  contentType: 'product-review',
  frequency: 'daily'
});
```
