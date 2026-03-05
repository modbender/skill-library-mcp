---
name: daily-report-joig
description: 生成简洁的中文日报（highlights/blockers/next），并可落盘为 Markdown 文件，适合个人复盘与同步。
user-invocable: true
metadata: {"openclaw": {"emoji": "🗒️"}}
---

# Daily Report (joig)

## Inputs
- date（必填）：YYYY-MM-DD 或 YYYY/MM/DD
- highlights（必填）：字符串数组，例如：["在 azure vm 上部署 openclaw","尝试写 skill"]
- blockers（可选）：字符串数组
- next（可选）：字符串数组（明日/下一步）
- outputPath（可选）：默认 `reports/{date}-daily-report.md`

## Output
返回固定结构：
- status: ok|error
- summary: 一句话总结
- data: { date, outputPath }
- nextAction: 建议的下一步

## Behavior
1) 规范化日期格式为 YYYY-MM-DD
2) 生成 Markdown：

```md
# 日报（{{date}}）

## Highlights
- ...

## Blockers
- ...

## Next
- ...
```

3) 写入 outputPath（确保父目录存在）

## Boundaries
- 不输出/复述任何 token、密钥、个人隐私。
- 不做绩效/压力话术；强调可执行与复盘。
