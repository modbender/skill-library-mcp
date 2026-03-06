import type { CategoryId } from "../pipeline/types";

export interface ScoringPromptArticle {
  index: number;
  title: string;
  description: string;
  sourceName: string;
  link: string;
}

export interface SummaryPromptArticle {
  index: number;
  title: string;
  description: string;
  sourceName: string;
  link: string;
  category: CategoryId;
  keywords: string[];
}

export interface HighlightsPromptArticle {
  index: number;
  category: CategoryId;
  titleZh: string;
  summaryZh: string;
}

export function buildScoringPrompt(articles: ScoringPromptArticle[]): string {
  const articleList = articles
    .map(
      (article) =>
        `Index ${article.index}: [${article.sourceName}] ${article.title}\nURL: ${article.link}\n${article.description.slice(0, 800)}`,
    )
    .join("\n\n---\n\n");

  return `你是网络空间安全研究员助手。请为以下文章进行多维评分、分类和关键词提取。

评分维度（1-10整数）：
1) relevance：总体阅读价值
2) quality：信息质量与技术深度
3) timeliness：时效性
4) security：安全相关性
5) ai：AI/LLM 相关性

分类（category）必须从以下枚举中选择：
- ai-ml
- security
- engineering
- tools
- opinion
- other

关键词（keywords）要求：
- 2-4个
- 使用英文短词
- 聚焦技术主题

待处理文章：
${articleList}

严格返回 JSON，不要 markdown，不要额外文字：
{
  "results": [
    {
      "index": 0,
      "relevance": 8,
      "quality": 7,
      "timeliness": 9,
      "security": 8,
      "ai": 7,
      "category": "security",
      "keywords": ["CVE", "RCE", "patch"]
    }
  ]
}`;
}

export function buildSummaryPrompt(articles: SummaryPromptArticle[], lang: "zh" | "en"): string {
  const articleList = articles
    .map(
      (article) =>
        `Index ${article.index}: [${article.sourceName}] ${article.title}\nURL: ${article.link}\nCategory: ${article.category}\nKeywords: ${article.keywords.join(", ")}\n${article.description.slice(0, 1200)}`,
    )
    .join("\n\n---\n\n");

  const langInstruction =
    lang === "zh"
      ? "请使用中文输出 title_zh、summary_zh、reason_zh。"
      : "Use English output for title_zh, summary_zh, and reason_zh.";

  return `你是网络空间安全领域的技术情报编辑，请为每篇文章输出翻译与结构化摘要。

输出字段：
- title_zh: 中文标题（若原标题已是中文，可保持）
- summary_zh: 4-6句结构化摘要（主题、关键信息、结论）
- reason_zh: 1句推荐理由，说明为什么值得读

要求：
- summary_zh 不要空话，保留关键术语、数字、版本号
- 若有对比或选型，指出比较对象与结论
- 保持可读性，读者在30秒内可判断是否继续阅读
- 严格输出 JSON
- ${langInstruction}

待处理文章：
${articleList}

返回格式：
{
  "results": [
    {
      "index": 0,
      "title_zh": "中文标题",
      "summary_zh": "4-6句摘要",
      "reason_zh": "推荐理由"
    }
  ]
}`;
}

export function buildHighlightsPrompt(articles: HighlightsPromptArticle[], lang: "zh" | "en"): string {
  const articleList = articles
    .map((article, idx) => `${idx + 1}. [${article.category}] ${article.titleZh} - ${article.summaryZh.slice(0, 120)}`)
    .join("\n");

  const langInstruction = lang === "zh" ? "请用中文回答。" : "Please answer in English.";

  return `基于以下今日精选，输出 3-5 句宏观趋势总结。

要求：
- 提炼 2-3 个主要趋势
- 不要逐篇列举
- 像情报简报导语，简洁直接
- ${langInstruction}

文章列表：
${articleList}

直接返回纯文本，不要 JSON，不要 markdown。`;
}
