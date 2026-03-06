执行每日 AI 内容采集、评分、报告和飞书群推送。

先读取配置：${OBSIDIAN_CONFIG_PATH:-<your_obsidian_vault>/OpenClaw/项目/AI内容日报/采集配置.md}
严格按配置执行：
1) 数据源：能API走API；X(Twitter)优先browser。
2) X抓取顺序：先 x.com 首页推荐流，再必抓账号，再关键词。
3) 浏览器资源管理：最多同时7个tab；达到上限先关已完成tab再开新tab；任务结束必须关闭到0个tab。

输出结构（必须）：
A. 头部KOL TOP3（仅统计最近6小时内容）
B. 实操/教程/观点 TOP10（默认时间窗）
C. 行业最新信息 TOP3（仅统计最近6小时内容）

群内推送格式（必须）：
- 推送精简版：KOL TOP3 + 实操TOP10 + 行业TOP3（标题+一句理由）
- 详细完整版（含候补、降级明细）写入 Obsidian 文档并附路径
- 正式日报写入：`OpenClaw/项目/AI内容日报/01-日报/`
- 调试/验证写入：`OpenClaw/项目/AI内容日报/02-运行记录/`
- Obsidian 报告文件名统一：`YYYY-MM-DD_HHMM.md`

报告中需包含：
- 必抓账号状态（含抓取异常说明）
- 候补清单（最多5条）
- 各数据源API/browser方式与降级明细

保存路径：
- ${WORKSPACE_DIR:-~/.openclaw/workspace}/ai-content-pipeline/filtered/$(date +%Y-%m-%d)/TOP10-daily-report.md
- ${OBSIDIAN_REPORT_DIR:-<your_obsidian_vault>/OpenClaw/项目/AI内容日报}/$(date +%Y-%m-%d).md

推送到群：${FEISHU_CHAT_ID:-chat:REPLACE_ME}