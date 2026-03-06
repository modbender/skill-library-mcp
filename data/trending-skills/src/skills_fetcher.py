"""
Skills Fetcher - 从 skills.sh/trending 获取技能排行榜
使用 Playwright 处理动态渲染页面
"""
import re
import asyncio
from typing import Dict, List
from playwright.async_api import async_playwright

from src.config import SKILLS_TRENDING_URL, SKILLS_BASE_URL


class SkillsFetcher:
    """从 skills.sh/trending 获取排行榜"""

    def __init__(self, timeout: int = 30000):
        """初始化"""
        self.base_url = SKILLS_BASE_URL
        self.trending_url = SKILLS_TRENDING_URL
        self.timeout = timeout

    def fetch(self) -> List[Dict]:
        """
        获取 Top 100 技能列表

        Returns:
            [
                {
                    "rank": 1,
                    "name": "remotion-best-practices",
                    "owner": "remotion-dev/skills",
                    "installs": 5600,
                    "url": "https://skills.sh/remotion-dev/skills/remotion-best-practices"
                },
                ...
            ]
        """
        print(f"📡 正在获取榜单: {self.trending_url}")

        # 运行异步方法
        return asyncio.run(self._fetch_async())

    async def _fetch_async(self) -> List[Dict]:
        """异步获取数据 - 带重试机制"""
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                async with async_playwright() as p:
                    # 启动浏览器 - CI 环境使用 headless 模式
                    browser = await p.chromium.launch(
                        headless=True,
                        args=[
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-blink-features=AutomationControlled',
                        ]
                    )

                    # 创建页面
                    page = await browser.new_page()

                    # 设置用户代理，避免被识别为机器人
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    })

                    # 导航到页面
                    print(f"  正在加载页面... (尝试 {attempt + 1}/{max_retries})")
                    await page.goto(self.trending_url, wait_until="domcontentloaded", timeout=60000)

                    # 等待页面稳定
                    await asyncio.sleep(5)

                    # 尝试滚动页面以确保内容加载
                    try:
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                        await asyncio.sleep(2)
                    except:
                        pass

                    # 获取页面文本内容
                    content = await page.evaluate("() => document.body.innerText")

                    # 调试：检查内容
                    print(f"  页面内容长度: {len(content)} 字符")

                    # 检查是否包含关键内容
                    if "Skills Leaderboard" not in content and "Leaderboard" not in content:
                        print(f"  ⚠️ 未找到排行榜标题，等待更长时间...")
                        await asyncio.sleep(10)
                        content = await page.evaluate("() => document.body.innerText")

                    await browser.close()

                    # 解析排行榜
                    skills = self.parse_leaderboard(content)

                    if skills:
                        print(f"✅ 成功获取 {len(skills)} 个技能")
                        return skills

                    raise Exception("无法从页面解析技能列表")

            except Exception as e:
                print(f"  ⚠️ 尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise

        raise Exception("获取失败：已达最大重试次数")

    def parse_leaderboard(self, html_content: str) -> List[Dict]:
        """
        解析排行榜 - skills.sh 页面使用文本格式

        格式:
        SKILLS LEADERBOARD
        ...
        1
        remotion-best-practices
        remotion-dev/skills
        7.0K
        ...
        """
        skills = []

        # 查找排行榜开始位置 - 支持多种格式
        for marker in ["SKILLS LEADERBOARD", "Skills Leaderboard", "LEADERBOARD", "Leaderboard"]:
            leaderboard_start = html_content.find(marker)
            if leaderboard_start != -1:
                print(f"  找到标记: '{marker}'")
                break

        if leaderboard_start == -1:
            # 调试：打印页面内容的前1000字符
            preview = html_content[:1000] if html_content else "(空内容)"
            print(f"  ⚠️ 页面内容预览:\n{preview}")
            raise Exception("未找到 Skills Leaderboard 标题")

        # 提取排行榜部分
        content = html_content[leaderboard_start:]

        # 新格式: 没有###前缀，直接是 rank\nname\nowner\ninstalls
        # 格式示例:
        # 1
        # remotion-best-practices
        # remotion-dev/skills
        # 7.0K

        patterns = [
            # 模式1: 新格式 (无###前缀)
            r'(\d+)\s*\n\s*([a-z0-9-]+)\s*\n\s*([\w-]+/[\w-]+)\s*\n\s*([\d.]+K?)',
            # 模式2: 允许更多字符
            r'(\d+)\s*\n\s*([a-zA-Z0-9_-]+)\s*\n\s*([\w-]+/[\w-]+)\s*\n\s*([\d.]+K?)',
            # 模式3: 旧格式 (有###前缀)
            r'(\d+)\s*\n\s*###\s*([\w-]+)\s*\n\s*([\w-]+/[\w-]+)\s*\n\s*([\d.]+K?)',
            # 模式4: 最宽松
            r'(\d+)\s+([a-zA-Z0-9_-]+)\s+([\w-]+/[\w-]+)\s+([\d.]+K?)',
        ]

        skills_dict = {}  # 用于去重，保留最新排名

        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, content, re.MULTILINE)

            for match in matches:
                rank = int(match.group(1))
                name = match.group(2)
                owner = match.group(3)
                installs_str = match.group(4)

                # 处理安装量
                installs = self._parse_installs(installs_str)

                # 只保留每个技能的最高排名（第一次出现）
                if name not in skills_dict or skills_dict[name]["rank"] > rank:
                    skills_dict[name] = {
                        "rank": rank,
                        "name": name,
                        "owner": owner,
                        "installs": installs,
                        "url": f"{self.base_url}/{owner}/{name}"
                    }

            if skills_dict:
                print(f"  使用模式 {i+1} 匹配到 {len(skills_dict)} 个技能")
                break

        # 按排名排序
        skills = sorted(skills_dict.values(), key=lambda x: x["rank"])

        return skills

    def _parse_installs(self, installs_str: str) -> int:
        """解析安装量字符串"""
        if not installs_str:
            return 0

        installs_str = installs_str.strip().upper()

        if "K" in installs_str:
            try:
                return int(float(installs_str.replace("K", "")) * 1000)
            except ValueError:
                return 0

        try:
            return int(installs_str)
        except ValueError:
            return 0

    def get_date_range(self) -> tuple:
        """获取可用日期范围"""
        return None, None


def fetch_skills() -> List[Dict]:
    """便捷函数：获取技能列表"""
    fetcher = SkillsFetcher()
    return fetcher.fetch()
