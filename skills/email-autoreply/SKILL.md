# Email Auto-Reply Generator

Generate context-aware email replies.

## Usage

```bash
npx email-autoreply
```

## API

```typescript
import { generateReply } from 'email-autoreply';

const reply = await generateReply({
  scenario: "product-inquiry",
  tone: "professional",
  originalEmail: "你们的产品多少钱？"
});
```
