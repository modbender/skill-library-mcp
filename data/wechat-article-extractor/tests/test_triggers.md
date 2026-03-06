# Trigger Tests

## True Positives (should trigger)

| # | Input | Expected |
|---|-------|----------|
| 1 | "Save this: https://mp.weixin.qq.com/s/abc123" | ✓ trigger |
| 2 | "Extract this wechat article for me" | ✓ trigger |
| 3 | "帮我保存这篇公众号文章" | ✓ trigger |
| 4 | "Archive this mp.weixin.qq.com link" | ✓ trigger |
| 5 | "提取公众号文章内容" | ✓ trigger |
| 6 | "Can you grab this WeChat article?" | ✓ trigger |
| 7 | "保存微信公众号这篇" | ✓ trigger |

## True Negatives (should NOT trigger)

| # | Input | Expected |
|---|-------|----------|
| 1 | "Send a message on WeChat" | ✗ no trigger |
| 2 | "Help me write an article" | ✗ no trigger |
| 3 | "Extract text from this PDF" | ✗ no trigger |
| 4 | "Save this webpage: https://example.com" | ✗ no trigger |
| 5 | "微信转账给我" | ✗ no trigger |
| 6 | "How do I create a WeChat account?" | ✗ no trigger |
