# Example Prompts

Use these examples to show how the skill should be invoked from different starting points.

## Topic-first

```text
围绕“AI Agent 在中小企业里的真实落地成本”写一篇 deep-analysis 风格文章。
需要深度研究、3 张正文配图、一个封面，最后转成公众号 HTML 并保存草稿。
```

## Article URL

```text
把这篇文章链接整理成公众号版本，保留核心观点，但改成 explainer 风格。
需要更清晰的小标题、正文配图和封面，最后保存为公众号草稿。
```

## Video URL

```text
根据这个视频链接做一篇 trend-report 风格文章。
先提取能拿到的字幕或关键信息，如果素材不足请只问我一个问题。
最后输出 Markdown、HTML 和公众号草稿。
```

## Transcript-first

```text
下面是播客逐字稿，请整理成 newsletter 风格文章。
要求高信息密度、易扫描、5 个以内小节、2 张正文配图，最后生成草稿。
```

## Author-style request

```text
模仿我提供的三篇样文的节奏和视角来写这篇文章，但不要复制明显句式。
选题是“独立开发者为什么越来越需要内容系统而不是单篇爆文”。
```

## Custom brief

```text
目标读者是做知识付费的个人品牌。
语气要克制、锋利、不要鸡汤。
结构希望是“问题 - 误区 - 机制 - 解法 - 结论”。
证据密度高，禁用“时代红利”“认知升级”这类表达。
```

## Conversion-only orientation

```text
我已经有一篇完整 Markdown。
请不要重写核心观点，只做结构优化、配图、封面、HTML 转换和公众号草稿保存。
```

## Safe publish boundary

```text
这篇内容只需要保存到公众号草稿箱，不要正式发布。
如果登录公众号网页是必需步骤，就暂停等我登录后继续。
```

## What good output looks like

The result should leave behind:

- one article workspace directory
- one canonical formatted markdown file
- one HTML file ready for WeChat
- one cover image
- resolved inline image paths
- one saved draft in the browser flow

## What to avoid

- starting design polish before the article angle is stable
- copying a named writer too literally
- decorative images that do not improve understanding
- direct live publishing when the request says draft only
