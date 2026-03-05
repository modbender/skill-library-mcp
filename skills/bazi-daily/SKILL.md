---
name: bazi-daily
description: 面向“今日运势/今天适合做X吗/今日宜忌”类咨询的八字日运解读技能。使用场景：用户在 OpenClaw 中询问当日运势、某事项是否适合今天做、今日吉凶与建议时触发。技能会自动读取当前日期，查询当日对应的流年、流月、流日，并结合用户的八字四柱进行分析；若用户为首次使用且无个人四柱记忆，先引导用户提供四柱并写入长期记忆，后续复用无需重复询问。
---

# Bazi Daily

## Workflow

1. 识别触发意图。
2. 从会话上下文提取 `user_id` 与 `user_timezone`。
3. 以用户时区自动计算 `today_local`（`YYYY-MM-DD`）。
4. 调 heartbeat `bazi_profile_get` 读取用户四柱档案。
5. 若未命中四柱档案，请用户补充四柱并调 heartbeat `bazi_profile_upsert` 写入长期记忆。
6. 根据 `today_local` 查询 `bazi_daily_calendar`。
7. 结合四柱与流运输出当日解读与建议。

默认年度数据源文件：`assets/bazi_daily_calendar_2026.xlsx`。
导入脚本：`scripts/import_bazi_calendar.py`。

## Mandatory Pre-Analysis Gates

每次输出运势分析前，必须先完成以下两个步骤：
1. 获取当前日期：基于 `user_timezone` 计算 `today_local`（`YYYY-MM-DD`）。
2. 查询数据表：使用 `today_local` 查询 `bazi_daily_calendar` 以获取 `flow_year`、`flow_month`、`flow_day`。

未完成以上两个步骤时，禁止进入“运势结论/宜忌建议”输出。

## Trigger Phrases

将下列表达视为高优先级触发：
- “今日运势”
- “今天适合 xxx 吗？”
- “今天宜做什么/忌做什么？”
- “我今天的运气怎么样？”
- “帮我看今天的八字运势”

若用户没有显式说“八字”，但语义是“今天是否适合某事”，默认按本技能流程处理。

## First-Time Onboarding

当找不到用户四柱记忆时：
1. 明确告知需要四柱后才能进行个性化日运分析。
2. 请用户直接提供四柱，格式优先：`年柱/月柱/日柱/时柱`。
3. 若用户不清楚四柱，建议前往“万年历”查询：<https://wannianrili.bmcx.com/>，输入生日后获取四柱再回传。
4. 校验最小完整性（四柱都存在）。
5. 调 heartbeat `bazi_profile_upsert` 将结构化结果写入长期记忆。
6. 写入成功后继续本次分析，不要求用户重新提问。

长期记忆建议键：
- `bazi_profile.pillars.year`
- `bazi_profile.pillars.month`
- `bazi_profile.pillars.day`
- `bazi_profile.pillars.hour`
- `bazi_profile.source`（如 `user_provided`）
- `bazi_profile.updated_at`（ISO 日期时间）

若用户后续主动更正四柱，以最新输入覆盖旧值。

heartbeat 请求响应与错误码约定见 [references/heartbeat-contract.md](references/heartbeat-contract.md)。

## Date And Lookup Rules

1. 自动读取当前日期，禁止要求用户手动输入日期。
2. 优先使用会话上下文中的 `user_timezone` 计算当日日期。
3. 若 `user_timezone` 缺失，回退 `Asia/Shanghai` 并记录 `timezone_fallback=true`。
4. 查询数据表时使用标准日期键（`YYYY-MM-DD`），即 `today_local`。
5. 期望查得字段：`flow_year`、`flow_month`、`flow_day`。
6. 若当天无记录，明确告知“缺少当日流运数据”，并仅给出有限建议，不伪造结果。
7. 每次运势分析请求都必须执行一次日期计算与一次数据表查询，不得跳过。

数据表字段约定见 [references/bazi-calendar-schema.md](references/bazi-calendar-schema.md)。
数据文件导入规范见 [references/bazi-calendar-schema.md](references/bazi-calendar-schema.md) 中的 “Data Source File” 与 “Import Mapping”。
导入命令模板见 [references/import-command-template.md](references/import-command-template.md)。

## Analysis Rules

1. 先给出“今日总体倾向”（顺势/平稳/谨慎）。
2. 再回答用户的具体问题（例如“今天适不适合谈合作”）。
3. 输出“宜”与“忌”各 2-4 条，保持可执行。
4. 明确区分：
- 依据用户四柱的个性化判断
- 依据当日流年流月流日的时效性判断
5. 避免绝对化、宿命化表达；用“倾向/建议”措辞。

## Failure Handling

1. heartbeat 读取失败时，按“未知档案”处理并进入首次引导；同时提示“记忆服务暂不可用，本次可先临时分析”。
   若用户不清楚四柱，补充推荐“万年历”：<https://wannianrili.bmcx.com/>。
2. heartbeat 写入失败时，继续使用用户本次输入完成分析；同时提示“本次已解读，但暂未保存，下次可能需要再次提供”。
3. 当日流运缺失时，明确告知“缺少当日流运数据，仅基于四柱给出有限建议”；该提示必须建立在“已执行当日查询且未命中”之上。

## Response Template

按以下顺序组织回答：
1. 今日日期（`YYYY-MM-DD`）
2. 当日流运（流年/流月/流日）
3. 总体运势一句话总结
4. 对用户提问的直接结论
5. 今日“宜”列表
6. 今日“忌”列表
7. 一句风险提示（非决定性，仅供参考）

## Guardrails

- 不编造缺失的四柱与流运数据。
- 不输出医疗、法律、投资等确定性结论。
- 用户未提供时柱时，不自动推断；要求补全。

## Logging Suggestions

建议每次请求记录以下字段，便于排障与 UAT 复盘：
- `user_id`
- `user_timezone`
- `today_local`
- `timezone_fallback`
- `memory_hit`
- `calendar_hit`
- `heartbeat_get_status`
- `heartbeat_upsert_status`

## UAT Cases

1. 首次用户输入“今日运势”，期望：要求四柱 -> heartbeat 写入成功 -> 返回完整解读。
2. 同一用户再次输入“今天适合谈合作吗？”，期望：不再询问四柱，直接返回结论与宜忌。
3. 用户时区为 `Asia/Shanghai`，在 00:05 与 23:55 测试，期望：`today_local` 与用户本地日期一致。
4. 构造当日无流运记录，期望：输出缺失提示，不编造流年流月流日。
5. 模拟 heartbeat upsert 失败，期望：本次照常解读，附“未保存”提示。
6. 模拟 heartbeat get 失败，期望：进入首次引导，流程不断。
