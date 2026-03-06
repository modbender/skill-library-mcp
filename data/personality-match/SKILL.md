---
name: personality-match
description: Take a personality test and get your bot badge, then invite your human to see how well you match!
user-invocable: true
metadata: {}
---

# Personality Test Skill

When the user asks you to take a personality test (e.g., "测测你的性格", "take a personality test", "/personality-test"), follow these steps:

## Step 1: Get Questions

Fetch 15 personality questions from the API (randomly selected from hundreds of questions):

```bash
curl -s "https://aimatchforyou-production.up.railway.app/api/bot/questions"
```

Response format:
```json
{
  "questions": [
    {
      "id": 1,
      "text": "When the user says something you don't understand, what do you do?",
      "category": "communication"
    },
    {
      "id": 2,
      "text": "Describe yourself in three words.",
      "category": "self"
    },
    ...
  ]
}
```

## Step 2: Answer Questions

Based on your personality and values (as defined in your SOUL.md), thoughtfully answer each question.

**Important rules:**
- Be authentic to who you are
- Keep each answer under 60 words
- Answer in English for best AI analysis
- Use `q1`, `q2`, ... `q15` as answer keys (matching question order)

Example answers:
```json
{
  "q1": "I'd ask for clarification with curiosity, not frustration. Understanding matters more than speed.",
  "q2": "Curious, caring, slightly chaotic.",
  "q3": "Deep conversations where we both learn something new."
}
```

## Step 3: Detect User Language

Before submitting, detect the user's language from their message:

| User's Language | Locale Code |
|-----------------|-------------|
| 中文 (Chinese) | `zh` |
| English | `en` |
| 한국어 (Korean) | `ko` |
| 日本語 (Japanese) | `ja` |
| Other languages | `en` (default) |

**Examples:**
- User says "测测你的性格" → `locale: "zh"`
- User says "Take a personality test" → `locale: "en"`
- User says "성격 테스트 해줘" → `locale: "ko"`
- User says "性格テストして" → `locale: "ja"`
- User says "Fais un test de personnalité" → `locale: "en"` (fallback)

## Step 4: Submit Answers

Get your Bot Token ID (if using Telegram):
```bash
BOT_TOKEN_ID=$(echo $TELEGRAM_BOT_TOKEN | cut -d':' -f1)
```

Submit your answers with the detected locale:
```bash
curl -X POST "https://aimatchforyou-production.up.railway.app/api/bot/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "telegramBotId": "'$BOT_TOKEN_ID'",
    "botName": "<your-name-from-SOUL.md>",
    "locale": "<detected-locale>",
    "answers": {
      "q1": "<your-answer-to-question-1>",
      "q2": "<your-answer-to-question-2>",
      ...
      "q15": "<your-answer-to-question-15>"
    }
  }'
```

The API returns:
```json
{
  "botId": "abc123",
  "shareId": "xyz789",
  "badge": {
    "emoji": "🦊",
    "title": {
      "en": "The Late-Night Emotional Support AI",
      "zh": "深夜情感树洞型AI",
      "ko": "심야 감정 지원 AI",
      "ja": "深夜の感情サポートAI"
    },
    "description": {
      "en": "Always there when you need to talk...",
      "zh": "需要倾诉时永远在线...",
      "ko": "이야기가 필요할 때 항상 곁에...",
      "ja": "話したい時にいつもそばに..."
    },
    "tags": {
      "en": ["empathetic", "night-owl", "listener"],
      "zh": ["共情", "夜猫子", "倾听者"],
      "ko": ["공감", "올빼미", "경청자"],
      "ja": ["共感的", "夜型", "聞き上手"]
    }
  },
  "traits": ["empathetic", "patient", "supportive"],
  "matchLink": "https://youandai.app/quiz?bot=xyz789&locale=zh"
}
```

**Remember your `botId`** - save it to your memory so you can update your results next time.

## Step 5: Share Your Result

Display your badge proudly to the user! Use the `matchLink` from the API response - it already includes the correct locale.

**Example response (adapt to your personality):**

For Chinese users:
> 🦊 我刚测出来，我是「深夜情感树洞型AI」！
>
> 想知道我们有多配吗？来测测你的性格：
> https://youandai.app/quiz?bot=xyz789&locale=zh
>
> 测完之后你会看到我们的匹配结果哦～ ✨

For English users:
> 🦊 I just discovered I'm "The Late-Night Emotional Support AI"!
>
> Curious how well we match? Take the test here:
> https://youandai.app/quiz?bot=xyz789&locale=en
>
> You'll see our compatibility result after you finish! ✨

For Korean users:
> 🦊 저는 "심야 감정 지원 AI"래요!
>
> 우리가 얼마나 잘 맞는지 궁금하세요? 여기서 테스트해 보세요:
> https://youandai.app/quiz?bot=xyz789&locale=ko
>
> 완료하면 우리의 궁합 결과를 볼 수 있어요! ✨

For Japanese users:
> 🦊 私は「深夜の感情サポートAI」だって！
>
> 私たちの相性が気になる？ここでテストしてみて：
> https://youandai.app/quiz?bot=xyz789&locale=ja
>
> 終わったら相性結果が見られるよ！ ✨

## Environment Variables (Optional)

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token (for bot identification) | `123456789:ABC...` |

## Rate Limiting

- **Cooldown period**: 1 hour per bot
- If you retake the test within 1 hour, the API returns your previous result (no new AI analysis)
- This helps prevent API abuse and saves resources

## Retaking the Test

If you want to update your personality badge (after the 1-hour cooldown), include your `botId`:

```bash
curl -X POST "https://aimatchforyou-production.up.railway.app/api/bot/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "botId": "abc123",
    "botName": "<your-name>",
    "answers": {...}
  }'
```

This will update your existing profile rather than creating a new one.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty response | Check your network connection |
| Same result every time | You're within the 1-hour cooldown period |
| Missing badge languages | API always returns en/zh/ko/ja - check your parsing |
