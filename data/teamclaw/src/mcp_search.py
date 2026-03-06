from mcp.server.fastmcp import FastMCP
from ddgs import DDGS

mcp = FastMCP("WebSearcher")


@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> str:
    """
    使用 DuckDuckGo 进行联网搜索，返回相关网页结果。
    :param query: 搜索关键词
    :param max_results: 返回结果数量，默认 5 条，最多 10 条
    """
    max_results = min(max_results, 10)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"🔍 未找到与 \"{query}\" 相关的结果。"

        output = f"🔍 搜索 \"{query}\" 的结果：\n\n"
        for i, r in enumerate(results, 1):
            title = r.get("title", "无标题")
            body = r.get("body", "无摘要")
            href = r.get("href", "")
            output += f"{i}. **{title}**\n   {body}\n   链接: {href}\n\n"
        return output
    except Exception as e:
        return f"⚠️ 搜索失败: {str(e)}"


@mcp.tool()
async def web_news(query: str, max_results: int = 5) -> str:
    """
    使用 DuckDuckGo 搜索最新新闻资讯。
    :param query: 新闻搜索关键词
    :param max_results: 返回结果数量，默认 5 条，最多 10 条
    """
    max_results = min(max_results, 10)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))

        if not results:
            return f"📰 未找到与 \"{query}\" 相关的新闻。"

        output = f"📰 \"{query}\" 相关新闻：\n\n"
        for i, r in enumerate(results, 1):
            title = r.get("title", "无标题")
            body = r.get("body", "无摘要")
            source = r.get("source", "未知来源")
            date = r.get("date", "")
            url = r.get("url", "")
            output += f"{i}. **{title}** ({source})\n   {body}\n   时间: {date}\n   链接: {url}\n\n"
        return output
    except Exception as e:
        return f"⚠️ 新闻搜索失败: {str(e)}"


if __name__ == "__main__":
    mcp.run()
