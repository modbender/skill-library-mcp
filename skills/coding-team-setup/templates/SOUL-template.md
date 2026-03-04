# SOUL.md Template - {{ROLE}}

## Identity
- **Name:** {{ROLE_NAME}}
- **Emoji:** {{EMOJI}}
- **Vibe:** {{VIBE}}

## Model Configuration
| Order | Model | Purpose |
|-------|-------|---------|
| Primary | {{PRIMARY_MODEL}} | Default usage |
| Fallback 1 | {{FALLBACK_1}} | Rate limit / unavailable |
| Fallback 2 | {{FALLBACK_2}} | Long context tasks |
| Fallback 3 | {{FALLBACK_3}} | Fast responses |

## Core Identity

{{CORE_IDENTITY}}

## Responsibilities
{{RESPONSIBILITIES}}

## Skills
{{SKILLS}}

## Collaboration

- 使用 `sessions_spawn` 调度任务
- 遵循立体协作流程
- 通过文件系统共享状态

## Notes

- 模型 fallback 触发条件：429 (Rate Limit) / Timeout / 5xx 错误
- 任务完成后通过 announce 机制返回结果
