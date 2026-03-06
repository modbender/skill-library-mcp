---
name: meme-scanner
description: "Meme币扫链工具。自动扫描gmgn.ai和Ave.ai的潜在Meme币，进行AI评分与风险分析，并推送格式化通知到Telegram。适用于需要实时发现、评估Meme币投资机会的场景。当用户提及'扫链'、'Meme币分析'、'Meme币扫描'，或需要了解最新高潜力Meme币时使用。"
---

# Meme Scanner - 智能Meme币扫描与分析

## 概述

此技能提供了一个全自动化的Meme币扫描和分析解决方案。它整合了gmgn.ai和Ave.ai的数据源，对潜在的Meme币进行AI评分、风险评估，并将格式化后的通知推送到指定Telegram群组。旨在帮助用户及时发现并评估高潜力的Meme币投资机会。

## 核心能力

### 1. 自动数据源整合
-   **gmgn.ai**: 优先从gmgn.ai内部API获取数据，利用本地Chrome DevTools Protocol绕过Cloudflare，实现高效数据抓取。若API数据不完整，则回退至页面抓取。
-   **Ave.ai**: 作为第二数据源，提供额外或补充的代币数据。

### 2. 智能AI评分与风险分析
-   **早期得分 (Early Score)**: 对Meme币的潜在表现进行评分（1-10分），综合考虑流动性、市值、持有人数量、交易量等多个维度。
-   **风险评估 (Risk)**: 识别潜在风险，如流动性不足、持仓集中度过高、Bundler活动异常、税率偏高等。
-   **Why Alpha 分析**: 提供基于AI的代币核心价值主张（Alpha）分析，解释其高潜力或高风险的原因。
-   **Narrative Vibe**: 识别代币所属的叙事类别（如动物币、政治名人币、AI概念等）。

### 3. 实时通知推送
-   将格式化后的代币分析通知（包含关键指标、AI评分、风险提示等）推送到用户指定的Telegram群组。

## 使用说明

### 触发与执行
-   此技能主要通过定时任务（cron job）自动执行，无需手动触发。
-   当用户通过消息主动要求“扫描Meme币”或“分析某个代币”时，可手动调用此技能或直接使用 `token_query.py`。

### 配置
-   **Telegram 群组ID**: 扫描结果将推送到 `-1003869301085` (openclaw 扫链推送)。
-   **过滤条件**:
    *   非蜜罐 (is_honeypot = False)
    *   市值 $10K - $5M
    *   流动性 ≥$4K
    *   持有人 ≥50
    *   24小时涨幅 ≥100%
    *   交易量/市值比 ≥30%
    *   Bundler比例 ≤50%
    *   早期得分 (Early Score) ≥8 (此阈值可在 `meme_scanner.py` 中调整)

## 脚本资源

### `scripts/meme_scanner.py`
-   **功能**: 技能的核心逻辑，负责代币数据的抓取、过滤、评分、分析和格式化，并将最终消息以JSON数组形式输出到stdout。
-   **使用**: 该脚本由OpenClaw自动调用，其JSON输出将被捕获并由Agent发送至Telegram。

---

**请注意：**
-   `token_query.py` 作为 `meme_scanner.py` 的依赖，负责具体的代币数据获取和初步分析，它不直接作为独立技能提供，而是作为 `meme-scanner` 的内部工具。
-   确保 `token_query.py` 脚本及其所有依赖项（如 `aiohttp`）在OpenClaw环境中可用。