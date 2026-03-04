# Heartbeat Contract For Bazi Profile

本文件定义 `bazi-daily` Skill 与 OpenClaw heartbeat 的读写契约。

## Events

- `bazi_profile_get`
- `bazi_profile_upsert`

## Scope And Idempotency

- scope：`user`
- 主键：`user_id`
- upsert 语义：同一 `user_id` 重复写入覆盖旧值。

## bazi_profile_get

请求：

```json
{
  "event": "bazi_profile_get",
  "scope": "user",
  "user_id": "u_123"
}
```

成功响应（命中）：

```json
{
  "ok": true,
  "data": {
    "pillars": {
      "year": "甲子",
      "month": "丙寅",
      "day": "辛亥",
      "hour": "壬辰"
    },
    "source": "user_provided",
    "updated_at": "2026-03-03T11:00:00+08:00"
  }
}
```

成功响应（未命中）：

```json
{
  "ok": true,
  "data": {}
}
```

## bazi_profile_upsert

请求：

```json
{
  "event": "bazi_profile_upsert",
  "scope": "user",
  "user_id": "u_123",
  "payload": {
    "pillars": {
      "year": "甲子",
      "month": "丙寅",
      "day": "辛亥",
      "hour": "壬辰"
    },
    "source": "user_provided",
    "updated_at": "2026-03-03T11:00:00+08:00"
  }
}
```

成功响应：

```json
{
  "ok": true
}
```

## Error Codes

- `HB_TIMEOUT`：heartbeat 服务超时（瞬时错误，可重试一次）
- `HB_UNAVAILABLE`：heartbeat 服务不可用（瞬时错误，可重试一次）
- `HB_INVALID_PAYLOAD`：入参不合法（非瞬时错误，不重试）
- `HB_UNAUTHORIZED`：无权限（非瞬时错误，不重试）

## Retry Rule

- 仅对瞬时错误重试一次：`HB_TIMEOUT`、`HB_UNAVAILABLE`
- 重试仍失败时：
  - get：进入首次引导并提示“记忆服务暂不可用，本次可先临时分析”
  - upsert：继续本次分析并提示“本次已解读，但暂未保存”

## Validation Rule

写入前必须校验四柱完整性：`year/month/day/hour` 四项都存在且非空。
