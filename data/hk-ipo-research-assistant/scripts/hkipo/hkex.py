"""港交所披露易 (HKEX News) API 数据源

直接从港交所官方 API 获取 IPO 申请和上市数据。

API 端点：
- 主板处理中: https://www.hkexnews.hk/ncms/json/eds/appactive_appphip_sehk_c.json
- 主板已上市: https://www.hkexnews.hk/ncms/json/eds/applisted_sehk_c.json
- 创业板处理中: https://www.hkexnews.hk/ncms/json/eds/appactive_appphip_gem_c.json
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

# API endpoints
BASE_URL = "https://www.hkexnews.hk"
ACTIVE_MAIN_URL = f"{BASE_URL}/ncms/json/eds/appactive_appphip_sehk_c.json"
ACTIVE_GEM_URL = f"{BASE_URL}/ncms/json/eds/appactive_appphip_gem_c.json"
LISTED_MAIN_URL = f"{BASE_URL}/ncms/json/eds/applisted_sehk_c.json"

# 状态码映射
STATUS_MAP = {
    "A": "处理中",  # Active
    "LT": "已上市",  # Listed
    "W": "已撤回",  # Withdrawn
    "L": "已失效",  # Lapsed
    "R": "已拒绝",  # Rejected
}


@dataclass
class HKEXDocument:
    """港交所文档"""
    date: str
    name: str  # 文档名称（如"聆讯后资料集"）
    full_url: str | None  # 完整PDF链接
    multi_url: str | None  # 多文件HTML链接


@dataclass
class HKEXIPO:
    """港交所 IPO 数据"""
    id: int  # 披露易 ID
    name: str  # 公司名称
    submit_date: str  # 提交日期 DD/MM/YYYY
    status: str  # 状态码 (A/LT/W/L/R)
    status_cn: str  # 状态中文
    stock_code: str | None  # 股票代码（仅已上市）
    board: str  # "main" 或 "gem"
    has_phip: bool  # 是否有聆讯后资料
    warning_url: str | None  # 警告声明 PDF
    documents: list[HKEXDocument]  # 文档列表
    raw: dict[str, Any]  # 原始数据


def _parse_date(date_str: str) -> datetime | None:
    """解析 DD/MM/YYYY 格式日期"""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except (ValueError, TypeError):
        return None


def _parse_document(doc: dict[str, Any]) -> HKEXDocument:
    """解析文档数据"""
    # 优先用 nF（文档分类名），否则用 nS1
    name = doc.get("nF") or doc.get("nS1") or "未知文档"
    full_url = f"{BASE_URL}/{doc['u1']}" if doc.get("u1") else None
    multi_url = f"{BASE_URL}/{doc['u2']}" if doc.get("u2") else None
    
    return HKEXDocument(
        date=doc.get("d", ""),
        name=name,
        full_url=full_url,
        multi_url=multi_url,
    )


def _parse_ipo(raw: dict[str, Any], board: str) -> HKEXIPO:
    """解析单个 IPO 数据"""
    status = raw.get("s", "")
    
    # 合并 ls（文档列表）和 ps（其他公告）
    docs = []
    for doc in raw.get("ls", []):
        docs.append(_parse_document(doc))
    for doc in raw.get("ps", []):
        docs.append(_parse_document(doc))
    
    return HKEXIPO(
        id=raw.get("id", 0),
        name=raw.get("a", ""),
        submit_date=raw.get("d", ""),
        status=status,
        status_cn=STATUS_MAP.get(status, status),
        stock_code=raw.get("st"),
        board=board,
        has_phip=raw.get("hasPhip", False),
        warning_url=f"{BASE_URL}/{raw['w']}" if raw.get("w") else None,
        documents=docs,
        raw=raw,
    )


async def _fetch_json(url: str, timeout: float = 30.0) -> dict[str, Any]:
    """获取 JSON 数据"""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def fetch_hkex_active_ipos() -> list[HKEXIPO]:
    """获取处理中的 IPO（主板+创业板）
    
    Returns:
        按提交日期倒序排列的 IPO 列表（最新的在前）
    
    Example:
        >>> ipos = await fetch_hkex_active_ipos()
        >>> for ipo in ipos[:3]:
        ...     print(f"{ipo.name} - {ipo.submit_date} - {ipo.status_cn}")
    """
    results: list[HKEXIPO] = []
    
    # 并发获取主板和创业板数据
    async with httpx.AsyncClient(timeout=30.0) as client:
        main_resp, gem_resp = await asyncio.gather(
            client.get(ACTIVE_MAIN_URL),
            client.get(ACTIVE_GEM_URL),
            return_exceptions=True,
        )
        
        # 处理主板
        if isinstance(main_resp, httpx.Response) and main_resp.status_code == 200:
            data = main_resp.json()
            for item in data.get("app", []):
                results.append(_parse_ipo(item, "main"))
        
        # 处理创业板
        if isinstance(gem_resp, httpx.Response) and gem_resp.status_code == 200:
            data = gem_resp.json()
            for item in data.get("app", []):
                results.append(_parse_ipo(item, "gem"))
    
    # 按提交日期倒序排列
    results.sort(key=lambda x: _parse_date(x.submit_date) or datetime.min, reverse=True)
    
    return results


async def fetch_hkex_listed_ipos(limit: int = 50) -> list[HKEXIPO]:
    """获取已上市的 IPO
    
    Args:
        limit: 返回数量限制，默认50。设为0返回全部。
    
    Returns:
        按上市日期倒序排列的 IPO 列表（最新的在前）
    
    Example:
        >>> ipos = await fetch_hkex_listed_ipos(10)
        >>> for ipo in ipos:
        ...     print(f"{ipo.stock_code} {ipo.name}")
    """
    data = await _fetch_json(LISTED_MAIN_URL)
    
    results: list[HKEXIPO] = []
    for item in data.get("app", []):
        results.append(_parse_ipo(item, "main"))
    
    # 按提交日期（上市日期）倒序排列
    results.sort(key=lambda x: _parse_date(x.submit_date) or datetime.min, reverse=True)
    
    if limit > 0:
        return results[:limit]
    return results


def get_prospectus_url(ipo: HKEXIPO) -> str | None:
    """获取招股书 PDF 链接
    
    优先返回聆讯后资料集，其次申请版本。
    
    Args:
        ipo: HKEXIPO 对象
    
    Returns:
        招股书 PDF URL，未找到则返回 None
    
    Example:
        >>> url = get_prospectus_url(ipo)
        >>> if url:
        ...     print(f"招股书: {url}")
    """
    # 优先查找聆讯后资料集
    for doc in ipo.documents:
        if "聆訊後資料集" in doc.name or "聆讯后资料集" in doc.name:
            if doc.full_url:
                return doc.full_url
    
    # 其次查找申请版本
    for doc in ipo.documents:
        if "申請版本" in doc.name or "申请版本" in doc.name:
            if doc.full_url:
                return doc.full_url
    
    return None


def get_document_by_type(ipo: HKEXIPO, doc_type: str) -> HKEXDocument | None:
    """按类型获取文档
    
    Args:
        ipo: HKEXIPO 对象
        doc_type: 文档类型关键词（如"聆讯后"、"申请版本"、"整体协调人"）
    
    Returns:
        匹配的文档，未找到则返回 None
    """
    for doc in ipo.documents:
        if doc_type in doc.name:
            return doc
    return None


# 同步版本（方便测试）
def fetch_hkex_active_ipos_sync() -> list[HKEXIPO]:
    """同步版本：获取处理中的 IPO"""
    import asyncio
    return asyncio.run(fetch_hkex_active_ipos())


def fetch_hkex_listed_ipos_sync(limit: int = 50) -> list[HKEXIPO]:
    """同步版本：获取已上市的 IPO"""
    import asyncio
    return asyncio.run(fetch_hkex_listed_ipos(limit))


# 需要 asyncio
import asyncio


if __name__ == "__main__":
    # 测试
    async def main():
        print("=== 处理中的 IPO ===")
        active = await fetch_hkex_active_ipos()
        print(f"共 {len(active)} 个处理中")
        for ipo in active[:5]:
            phip = "✓" if ipo.has_phip else "✗"
            print(f"  [{phip}] {ipo.name} ({ipo.submit_date}) - {ipo.board}")
            url = get_prospectus_url(ipo)
            if url:
                print(f"      招股书: {url[:80]}...")
        
        print("\n=== 最近上市的 IPO ===")
        listed = await fetch_hkex_listed_ipos(10)
        for ipo in listed:
            print(f"  {ipo.stock_code} {ipo.name} ({ipo.submit_date})")
    
    asyncio.run(main())
