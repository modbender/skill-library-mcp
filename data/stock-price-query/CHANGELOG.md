# Changelog

## v1.0.3 (2026-02-25)

### Security
- 新增输入安全校验，stock_code 仅允许字母和数字（`^[A-Za-z0-9]{1,10}$`），market 使用白名单（sh/sz/hk/us），防止 shell 命令注入
- SKILL.md 增加输入安全校验说明
- 解决 ClawHub VirusTotal 扫描报告中的 Suspicious 标记

## v1.0.2 (2026-02-24)

### Reverted
- 移除 stock_query.sh wrapper 脚本，保持纯 .py 脚本方案
- SKILL.md 调用方式还原为直接 python3 调用

## v1.0.1 (2026-02-24)

### Changed
- 数据源从新浪财经 API (hq.sinajs.cn) 切换为腾讯财经 API (qt.gtimg.cn)，解决 403 Forbidden 问题
- 腾讯 API 无需 Referer Header，稳定性更好
- 统一了各市场（A 股/港股/美股）的数据解析逻辑，代码更简洁
- 更新 references/api-docs.md 为腾讯 API 文档

## v1.0.0 (2026-02-24)

### Added
- 初版发布，支持查询股票实时价格
- 支持 A 股沪市（sh）、A 股深市（sz）、港股（hk）、美股（us）四个市场
- 自动识别股票代码所属市场
- 零外部依赖，纯 Python 标准库实现
- 返回结构化 JSON 数据（当前价、涨跌幅、开高低收、成交量等）
- API 限流自动重试机制
- 提供 API 参考文档（references/api-docs.md）
- SKILL.md 元数据格式对齐 OpenClaw 官方示例规范
