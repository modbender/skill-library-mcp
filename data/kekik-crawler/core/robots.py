import asyncio
from urllib import robotparser
from urllib.parse import urlparse

from backends.scrapling_backend import fetch as scrapling_fetch


async def robots_allow(url: str, ua: str, verify_ssl: bool = True) -> bool:
    try:
        p = urlparse(url)
        robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
        _final_url, txt, status, _meta = await asyncio.to_thread(
            scrapling_fetch, robots_url, 10.0, verify_ssl, {"User-Agent": ua}
        )
        if status >= 400:
            return True
        rp = robotparser.RobotFileParser()
        rp.parse(txt.splitlines())
        return rp.can_fetch(ua, url)
    except Exception:
        return True
