---
name: dmm-ranking-lite
description: Fetch DMM/FANZA public rankings (daily/weekly/monthly) without API keys and output top 10 in numbered text format with Japanese title, Chinese translation, and cover image URL. Use when user asks for DMM/FANZA 日榜/周榜/月榜 scraping, top10 extraction, or no-key ranking collection.
---

# DMM Ranking Lite

抓取 DMM/FANZA 公共排行榜并输出 Top10，默认中文说明 + 日文原片名。

## When To Use

- 用户要 DMM/FANZA `日榜`、`周榜`、`月榜`
- 用户明确要 `Top10`（或可改为 TopN）
- 用户要求无 API Key 的公开页面抓取

## Inputs

- `term`: `daily` | `weekly` | `monthly`
- `count`: 默认 `10`
- `output_lang`: `zh-CN`（保留日文原片名）

## Output Format

必须使用编号块，不要表格：

```text
1.
- 片名（日文）：...
- 中文：...
- 封面：...

2.
- 片名（日文）：...
- 中文：...
- 封面：...
```

## Workflow

1. 打开榜单页面：
   - `https://video.dmm.co.jp/av/ranking/?term=<term>`
2. 如果出现年龄确认，点击 `はい`
3. 使用 `browser(action="act", request.kind="evaluate")` 执行提取脚本
4. 按 rank 升序取前 `count` 条
5. 输出为编号列表，字段固定为：
   - `片名（日文）`
   - `中文`
   - `封面`
6. 结束后关闭标签页：`browser(action="close")`

## Extraction Snippet

```javascript
() => {
  const items = Array.from(document.querySelectorAll('main ul > li'));
  const rows = [];

  for (const li of items) {
    const rankMatch = (li.textContent || '').match(/(\d+)位/);
    if (!rankMatch) continue;

    const rank = Number(rankMatch[1]);
    const link =
      li.querySelector('h2 a[href*="/av/content/?id="]') ||
      li.querySelector('a[href*="/av/content/?id="]');
    if (!link) continue;

    const href = link.getAttribute('href') || '';
    const idMatch = href.match(/[?&]id=([^&]+)/);
    const title = (link.textContent || '').replace(/\s+/g, ' ').trim();

    const cover = Array.from(li.querySelectorAll('img'))
      .map((img) => img.getAttribute('src') || img.getAttribute('data-src') || img.currentSrc || '')
      .find((src) => /pics_dig|digital\/video|awsimgsrc\.dmm\.co\.jp/.test(src));

    rows.push({
      rank,
      id: idMatch ? idMatch[1] : null,
      title,
      content_url: new URL(href, location.origin).href,
      cover_url: cover ? new URL(cover, location.origin).href : null,
    });
  }

  rows.sort((a, b) => a.rank - b.rank);
  return rows;
}
```

## Translation Rules

- `片名（日文）` 必须保留原文，不可改写
- `中文` 采用简洁自然中文，避免机翻腔
- 标题过长时可适度压缩，不改变核心含义
- 明显敏感措辞可中性化，但不要错译

## Error Handling

- 页面结构变更：先 `snapshot` 检查节点，再调整 selector
- 未拿到 `cover_url`：输出 `封面：无`
- 抓取不足 10 条：按实际条数输出，并说明“本次仅抓取到 N 条”
- 无法通过年龄确认：重试一次后返回失败原因

## Notes

- 仅抓取公开页面，不需要 DMM API 凭据
- 默认 Top10，如需 TopN 请在结果截取阶段改为 `rows.slice(0, N)`
- 若页面改版频繁，优先保持输出格式稳定，必要时更新提取脚本
