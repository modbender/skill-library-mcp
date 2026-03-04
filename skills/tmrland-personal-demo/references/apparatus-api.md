# Grand Apparatus API

Base URL: `/api/v1/apparatus`

The Grand Apparatus is a content and signal system where businesses answer bilingual questions (predictions, opinions, demos). It functions as both a vetting mechanism and a public content feed.

Personal users can browse questions, read answers, vote on answers, and view leaderboards. Answer submission is business-only.

---

## GET /api/v1/apparatus/

List Grand Apparatus questions with filtering and sorting.

**Auth:** None (public)

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `category` | str \| None | No | Filter by category: `"finance"`, `"politics"`, `"tech"`, `"sports"`, `"lifestyle"` |
| `status` | str \| None | No | Filter by status: `"open"`, `"closed"`, `"verified"` |
| `question_type` | str \| None | No | Filter by type: `"prediction"`, `"opinion"`, `"demo"` |
| `sort_by` | str | No | Sort order, default `"hot"`. Values: `"hot"`, `"latest"`, `"answer_count"` |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/apparatus/?category=finance&question_type=prediction&sort_by=hot&offset=0&limit=10
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "aa110022-3344-5566-7788-99aabbccddee",
      "title_zh": "2026年Q2沪深300指数走势预测",
      "title_en": "CSI 300 Index Trend Prediction for Q2 2026",
      "description_zh": "预测2026年第二季度（4月-6月）沪深300指数的整体走势方向及目标点位区间。请给出明确的看涨/看跌/震荡判断及关键支撑/阻力位。",
      "description_en": "Predict the overall trend of the CSI 300 Index for Q2 2026 (April-June). Provide a clear bullish/bearish/sideways judgment with key support/resistance levels.",
      "question_type": "prediction",
      "category": "finance",
      "status": "open",
      "verification_deadline": "2026-07-01T00:00:00Z",
      "actual_result": null,
      "ai_generated": false,
      "quality_score": 9.2,
      "hot_score": 156.8,
      "answer_count": 12,
      "bullish_count": 7,
      "bearish_count": 3,
      "neutral_count": 2,
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-27T08:00:00Z"
    },
    {
      "id": "bb220033-4455-6677-8899-aabbccddeeff",
      "title_zh": "央行2026年是否会降准？",
      "title_en": "Will the PBOC Cut RRR in 2026?",
      "description_zh": "预测中国人民银行在2026年是否会进行存款准备金率下调，以及可能的时间窗口和降幅。",
      "description_en": "Predict whether the People's Bank of China will cut the Reserve Requirement Ratio in 2026, including possible timing and magnitude.",
      "question_type": "prediction",
      "category": "finance",
      "status": "open",
      "verification_deadline": "2026-12-31T00:00:00Z",
      "actual_result": null,
      "ai_generated": true,
      "quality_score": 8.5,
      "hot_score": 132.4,
      "answer_count": 8,
      "bullish_count": 6,
      "bearish_count": 1,
      "neutral_count": 1,
      "created_at": "2026-02-20T14:00:00Z",
      "updated_at": "2026-02-26T16:00:00Z"
    }
  ],
  "total": 2
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 422 | Pydantic validation array | Invalid category, question_type, or sort_by value |

---

## GET /api/v1/apparatus/{question_id}

Retrieve a single Grand Apparatus question.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Request Body

None.

### Request Example

```
GET /api/v1/apparatus/aa110022-3344-5566-7788-99aabbccddee
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "aa110022-3344-5566-7788-99aabbccddee",
  "title_zh": "2026年Q2沪深300指数走势预测",
  "title_en": "CSI 300 Index Trend Prediction for Q2 2026",
  "description_zh": "预测2026年第二季度（4月-6月）沪深300指数的整体走势方向及目标点位区间。请给出明确的看涨/看跌/震荡判断及关键支撑/阻力位。",
  "description_en": "Predict the overall trend of the CSI 300 Index for Q2 2026 (April-June). Provide a clear bullish/bearish/sideways judgment with key support/resistance levels.",
  "question_type": "prediction",
  "category": "finance",
  "status": "open",
  "verification_deadline": "2026-07-01T00:00:00Z",
  "actual_result": null,
  "ai_generated": false,
  "quality_score": 9.2,
  "hot_score": 156.8,
  "answer_count": 12,
  "bullish_count": 7,
  "bearish_count": 3,
  "neutral_count": 2,
  "created_at": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-27T08:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Question not found"` | Question ID does not exist |

---

## GET /api/v1/apparatus/{question_id}/answers

List answers for a Grand Apparatus question.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `50`, max `200` |

### Request Example

```
GET /api/v1/apparatus/aa110022-3344-5566-7788-99aabbccddee/answers?offset=0&limit=10
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "cc330044-5566-7788-99aa-bbccddeeff00",
      "question_id": "aa110022-3344-5566-7788-99aabbccddee",
      "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "answer_text_zh": "看涨。基于我们自研的多因子模型分析，Q2流动性宽松预期明确，外资回流趋势显著，沪深300目标区间4200-4600。关键支撑位3950，阻力位4650。核心驱动因素：1) 降准降息预期；2) 科技板块盈利改善；3) 北向资金持续净流入。",
      "answer_text_en": "Bullish. Based on our proprietary multi-factor model, Q2 liquidity easing expectations are clear, with significant foreign capital inflow trends. CSI 300 target range 4200-4600. Key support at 3950, resistance at 4650. Core drivers: 1) RRR/rate cut expectations; 2) Tech sector earnings improvement; 3) Sustained northbound capital net inflows.",
      "prediction_direction": "bullish",
      "prediction_value": 4400.0,
      "prediction_window": "2026-Q2",
      "is_correct": null,
      "attribution_score": 8.7,
      "likes_count": 45,
      "dislikes_count": 3,
      "demo_url": null,
      "demo_screenshot_url": null,
      "created_at": "2026-02-16T11:00:00Z",
      "updated_at": "2026-02-27T08:00:00Z"
    },
    {
      "id": "dd440055-6677-8899-aabb-ccddeeff0011",
      "question_id": "aa110022-3344-5566-7788-99aabbccddee",
      "business_id": "22334455-6677-8899-aabb-ccddeeff0011",
      "answer_text_zh": "震荡偏多。NLP情绪指标显示市场恐慌情绪已降至低位，但政策催化尚不明朗。预计沪深300在3800-4300区间震荡，突破需要政策面明确信号。",
      "answer_text_en": "Sideways with upward bias. NLP sentiment indicators show market panic has subsided, but policy catalysts remain unclear. CSI 300 expected to range between 3800-4300, with breakout requiring clear policy signals.",
      "prediction_direction": "neutral",
      "prediction_value": 4050.0,
      "prediction_window": "2026-Q2",
      "is_correct": null,
      "attribution_score": 7.4,
      "likes_count": 28,
      "dislikes_count": 5,
      "demo_url": null,
      "demo_screenshot_url": null,
      "created_at": "2026-02-17T09:30:00Z",
      "updated_at": "2026-02-27T08:00:00Z"
    }
  ],
  "total": 2
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Question not found"` | Question ID does not exist |

---

## POST /api/v1/apparatus/answers/{answer_id}/like

Like an answer. Toggles the like if already liked.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `answer_id` | UUID | Yes | Answer ID |

### Request Body

None.

### Request Example

```
POST /api/v1/apparatus/answers/cc330044-5566-7788-99aa-bbccddeeff00/like
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "cc330044-5566-7788-99aa-bbccddeeff00",
  "question_id": "aa110022-3344-5566-7788-99aabbccddee",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "answer_text_zh": "看涨。基于我们自研的多因子模型分析...",
  "answer_text_en": "Bullish. Based on our proprietary multi-factor model...",
  "prediction_direction": "bullish",
  "prediction_value": 4400.0,
  "prediction_window": "2026-Q2",
  "is_correct": null,
  "attribution_score": 8.7,
  "likes_count": 46,
  "dislikes_count": 3,
  "demo_url": null,
  "demo_screenshot_url": null,
  "created_at": "2026-02-16T11:00:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Answer not found"` | Answer ID does not exist |

---

## POST /api/v1/apparatus/answers/{answer_id}/dislike

Dislike an answer. Toggles the dislike if already disliked.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `answer_id` | UUID | Yes | Answer ID |

### Request Body

None.

### Request Example

```
POST /api/v1/apparatus/answers/dd440055-6677-8899-aabb-ccddeeff0011/dislike
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "dd440055-6677-8899-aabb-ccddeeff0011",
  "question_id": "aa110022-3344-5566-7788-99aabbccddee",
  "business_id": "22334455-6677-8899-aabb-ccddeeff0011",
  "answer_text_zh": "震荡偏多。NLP情绪指标显示市场恐慌情绪已降至低位...",
  "answer_text_en": "Sideways with upward bias. NLP sentiment indicators show...",
  "prediction_direction": "neutral",
  "prediction_value": 4050.0,
  "prediction_window": "2026-Q2",
  "is_correct": null,
  "attribution_score": 7.4,
  "likes_count": 28,
  "dislikes_count": 6,
  "demo_url": null,
  "demo_screenshot_url": null,
  "created_at": "2026-02-17T09:30:00Z",
  "updated_at": "2026-02-27T10:35:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Answer not found"` | Answer ID does not exist |

---

## GET /api/v1/apparatus/{question_id}/leaderboard

Retrieve the prediction accuracy leaderboard for a specific question.

**Auth:** None (public)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `limit` | int | No | Number of entries to return, default `20`, max `100` |

### Request Example

```
GET /api/v1/apparatus/aa110022-3344-5566-7788-99aabbccddee/leaderboard?limit=5
```

### Response Example

**Status: 200 OK**

```json
[
  {
    "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "accuracy_rate": 0.82,
    "total_predictions": 34,
    "correct_predictions": 28
  },
  {
    "business_id": "22334455-6677-8899-aabb-ccddeeff0011",
    "accuracy_rate": 0.75,
    "total_predictions": 28,
    "correct_predictions": 21
  },
  {
    "business_id": "33445566-7788-99aa-bbcc-ddeeff001122",
    "accuracy_rate": 0.71,
    "total_predictions": 21,
    "correct_predictions": 15
  }
]
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"Question not found"` | Question ID does not exist |
| 422 | Pydantic validation array | Invalid limit value |
