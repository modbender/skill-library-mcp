#!/usr/bin/env python3
"""
TrainClaw - 车票查询AI助手 Train Ticket CLI Tool
单文件 CLI 工具，查询中国铁路余票、经停站、中转信息。

GitHub: https://github.com/AI4MSE/TrainClaw
License: Apache-2.0

免责声明 / Disclaimer:
本工具仅供学习和交流之用，使用时请遵守当地法律和法规。
This tool is for educational and research purposes only.
Please comply with local laws and regulations when using it.

Usage:
    python trainclaw.py query -f 北京 -t 上海 -d 2026-03-04 --type G
    python trainclaw.py route -c G1033 -d 2026-03-04
    python trainclaw.py transfer -f 深圳 -t 拉萨 -m 西安 -d 2026-03-04

Version: 0.0.3
"""

import argparse
import csv
import io
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests

import config

__version__ = "0.0.3"

logger = logging.getLogger("trainclaw")


# =============================================================================
# Data Classes / 数据类
# =============================================================================

@dataclass
class StationData:
    """Station information / 车站信息"""
    station_id: str
    station_name: str
    station_code: str      # 3-letter telecode (e.g. BJP)
    station_pinyin: str
    station_short: str
    station_index: str
    code: str              # Numeric code
    city: str
    r1: str
    r2: str


@dataclass
class Price:
    """Seat price information / 席位价格信息"""
    seat_name: str         # Display name / 显示名称 (e.g. 二等座)
    seat_type_code: str    # Type code / 类型码 (e.g. O)
    price: float           # Price in CNY / 票价（元）
    num: str               # Remaining tickets / 余票数 ("有"/"无"/"12"/...)
    discount: Optional[int] = None  # Discount percentage / 折扣百分比 (e.g. 95 = 95折)


@dataclass
class TicketInfo:
    """Train ticket information / 车票信息"""
    train_no: str              # Internal train number / 内部编号
    station_train_code: str    # Display code (e.g. G1033) / 显示车次
    start_date: str            # Departure date yyyy-MM-dd / 出发日期
    start_time: str            # Departure time HH:MM / 出发时间
    arrive_date: str           # Arrival date yyyy-MM-dd / 到达日期
    arrive_time: str           # Arrival time HH:MM / 到达时间
    lishi: str                 # Duration HH:MM / 历时
    from_station: str          # Boarding station name / 出发站名
    to_station: str            # Alighting station name / 到达站名
    from_station_code: str     # Boarding station telecode / 出发站代码
    to_station_code: str       # Alighting station telecode / 到达站代码
    prices: List[Price] = field(default_factory=list)
    dw_flags: List[str] = field(default_factory=list)  # Feature tags / 特征标签


@dataclass
class RouteStationInfo:
    """Route stop information / 经停站信息"""
    station_name: str
    station_train_code: str
    arrive_time: str
    start_time: str
    lishi: str                 # Running time / 运行时长
    arrive_day_str: str        # Day indicator / 日期标识
    # First station only / 仅首站有:
    train_class_name: Optional[str] = None   # e.g. "高速动车"
    service_type: Optional[str] = None       # "0"=no AC, "1"=AC
    end_station_name: Optional[str] = None   # Terminal station / 终到站


@dataclass
class InterlineInfo:
    """Transfer route information / 中转方案信息"""
    lishi: str                     # Total duration HH:MM / 总历时
    start_time: str
    start_date: str
    middle_date: str
    arrive_date: str
    arrive_time: str
    from_station_name: str
    from_station_code: str
    middle_station_name: str
    middle_station_code: str
    end_station_name: str
    end_station_code: str
    start_train_code: str          # First train code (for filtering)
    first_train_no: str
    second_train_no: str
    train_count: int
    ticket_list: List[TicketInfo] = field(default_factory=list)
    same_station: bool = False     # Same station transfer / 同站换乘
    same_train: bool = False       # Same train transfer / 同车换乘
    wait_time: str = ""            # Wait time at transfer / 换乘等待时间


# =============================================================================
# Station Manager / 车站数据管理
# =============================================================================

class StationManager:
    """Loads, caches, and queries station data from 12306."""

    def __init__(self):
        self._stations: Dict[str, StationData] = {}      # code -> StationData
        self._name_index: Dict[str, str] = {}             # name -> code
        self._city_index: Dict[str, List[str]] = {}       # city -> [codes]
        self._city_code: Dict[str, str] = {}              # city -> representative code
        self._loaded = False

    def ensure_loaded(self):
        """Load station data if not already loaded."""
        if not self._loaded:
            self._load()
            self._loaded = True

    def _cache_path(self) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, config.CACHE_DIR, config.STATION_CACHE_FILE)

    def _is_cache_valid(self) -> bool:
        path = self._cache_path()
        if not os.path.exists(path):
            return False
        age = time.time() - os.path.getmtime(path)
        return age < config.STATION_CACHE_TTL

    def _load(self):
        if self._is_cache_valid():
            self._load_from_cache()
        else:
            self._load_from_web()
        self._build_indices()

    def _load_from_cache(self):
        with open(self._cache_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        for code, info in data.items():
            self._stations[code] = StationData(**info)

    def _save_cache(self):
        path = self._cache_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {code: asdict(st) for code, st in self._stations.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

    def _load_from_web(self):
        logger.info("Downloading station data from 12306...")
        resp = requests.get(config.WEB_URL, timeout=config.REQUEST_TIMEOUT,
                            headers={"User-Agent": config.USER_AGENT})
        resp.raise_for_status()
        match = re.search(r'(/script/core/common/station_name[^"\']+\.js)', resp.text)
        if not match:
            raise RuntimeError("Failed to find station_name JS path in 12306 homepage")

        js_url = config.WEB_URL.rstrip("/") + match.group(1)
        resp2 = requests.get(js_url, timeout=config.REQUEST_TIMEOUT,
                             headers={"User-Agent": config.USER_AGENT})
        resp2.raise_for_status()

        # Extract raw data: var station_names = '...'
        m = re.search(r"var\s+station_names\s*=\s*'([^']*)'", resp2.text)
        if not m:
            raise RuntimeError("Failed to parse station_names from JS file")

        raw = m.group(1)
        self._parse_stations(raw)

        # Add missing stations / 补充缺失车站
        for ms in config.MISSING_STATIONS:
            code = ms["station_code"]
            if code not in self._stations:
                self._stations[code] = StationData(**ms)

        self._save_cache()
        logger.info("Cached %d stations.", len(self._stations))

    def _parse_stations(self, raw: str):
        """Parse pipe-separated station data (10 fields per station)."""
        parts = raw.split("|")
        keys = ["station_id", "station_name", "station_code", "station_pinyin",
                "station_short", "station_index", "code", "city", "r1", "r2"]
        count = len(parts) // 10
        for i in range(count):
            group = parts[i * 10: i * 10 + 10]
            if len(group) < 10:
                continue
            d = dict(zip(keys, group))
            code = d.get("station_code", "")
            if not code:
                continue
            self._stations[code] = StationData(**d)

    def _build_indices(self):
        for code, st in self._stations.items():
            self._name_index[st.station_name] = code
            city = st.city
            if city:
                self._city_index.setdefault(city, []).append(code)

        # City representative station: prefer station whose name == city name
        for city, codes in self._city_index.items():
            representative = codes[0]
            for c in codes:
                if self._stations[c].station_name == city:
                    representative = c
                    break
            self._city_code[city] = representative

    def resolve_station(self, name_or_code: str) -> str:
        """
        Resolve a station name, city name, or telecode to a station telecode.
        解析站名/城市名/三字母代码为车站电报码。
        """
        self.ensure_loaded()
        # Exact station name match / 精确站名匹配
        if name_or_code in self._name_index:
            return self._name_index[name_or_code]
        # City name match / 城市名匹配 → representative station
        if name_or_code in self._city_code:
            return self._city_code[name_or_code]
        # 3-letter code direct / 三字母代码直接返回
        if len(name_or_code) == 3 and name_or_code.isalpha():
            upper = name_or_code.upper()
            if upper in self._stations:
                return upper
        suggestions = self.suggest_stations(name_or_code)
        if suggestions:
            raise ValueError(f"无法识别的车站: '{name_or_code}'。您是否要找: {'、'.join(suggestions)}")
        else:
            raise ValueError(f"无法识别的车站: '{name_or_code}'。请检查站名是否正确")

    def get_station(self, code: str) -> Optional[StationData]:
        """Get station data by telecode."""
        self.ensure_loaded()
        return self._stations.get(code)

    def get_name(self, code: str) -> str:
        """Get station display name by telecode."""
        self.ensure_loaded()
        st = self._stations.get(code)
        return st.station_name if st else code

    def suggest_stations(self, query: str, limit: int = 5) -> List[str]:
        """Suggest station names by substring > city > pinyin prefix matching."""
        if not query:
            return []
        self.ensure_loaded()
        candidates = []
        for code, st in self._stations.items():
            if query in st.station_name:
                candidates.append((0, st.station_name))
            elif query in st.city:
                candidates.append((1, st.station_name))
            elif st.station_pinyin.startswith(query.lower()) or st.station_short.startswith(query.lower()):
                candidates.append((2, st.station_name))
        candidates.sort(key=lambda x: (x[0], x[1]))
        seen = set()
        return [name for _, name in candidates if not (name in seen or seen.add(name))][:limit]


# Global singleton / 全局单例
station_manager = StationManager()


# =============================================================================
# HTTP Client / HTTP 客户端
# =============================================================================

class TrainAPI:
    """HTTP client for 12306 API calls with cookie management."""

    def __init__(self):
        self._cookie_str: Optional[str] = None
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": config.USER_AGENT})
        self._last_request_time = 0.0

    def _get_cookie(self) -> str:
        """Fetch cookies from 12306 leftTicket/init page."""
        url = f"{config.API_BASE}/otn/leftTicket/init"
        resp = self._session.get(url, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        cookies = resp.cookies.get_dict()
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        if not cookie_str:
            raise RuntimeError("Failed to get cookies from 12306")
        return cookie_str

    def _ensure_cookie(self):
        if not self._cookie_str:
            self._cookie_str = self._get_cookie()

    def _get(self, url: str, params: dict = None, use_cookie: bool = True,
             retries: int = None) -> requests.Response:
        """GET request with retries, cooldown, and optional cookie."""
        if retries is None:
            retries = config.MAX_RETRIES

        # Enforce cooldown between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < config.QUERY_COOLDOWN:
            wait = config.QUERY_COOLDOWN - elapsed
            logger.debug("Cooldown: waiting %.1fs", wait)
            time.sleep(wait)

        headers = {}
        if use_cookie:
            self._ensure_cookie()
            headers["Cookie"] = self._cookie_str

        last_err = None
        for attempt in range(retries + 1):
            try:
                logger.debug("GET %s params=%s", url, params)
                resp = self._session.get(
                    url, params=params, headers=headers,
                    timeout=config.REQUEST_TIMEOUT
                )
                resp.raise_for_status()
                self._last_request_time = time.time()
                logger.debug("Response %d, %d bytes", resp.status_code, len(resp.content))
                return resp
            except Exception as e:
                last_err = e
                logger.debug("Request failed (attempt %d/%d): %s", attempt + 1, retries + 1, e)
                if attempt < retries:
                    time.sleep(0.5)
        raise last_err

    # --- Query Methods ---

    def query_tickets(self, date: str, from_code: str, to_code: str) -> Tuple[List[str], Dict[str, str]]:
        """
        Query remaining tickets.
        Returns (raw_result_list, station_code_to_name_map).
        """
        params = {
            "leftTicketDTO.train_date": date,
            "leftTicketDTO.from_station": from_code,
            "leftTicketDTO.to_station": to_code,
            "purpose_codes": config.DEFAULT_PURPOSE,
        }
        resp = self._get(f"{config.API_BASE}/otn/leftTicket/query", params=params)
        data = resp.json()
        if not data.get("status"):
            msg = data.get("messages", data.get("errorMsg", "Unknown error"))
            raise RuntimeError(f"12306 query failed: {msg}")
        result = data["data"]["result"]
        station_map = data["data"].get("map", {})
        return result, station_map

    def query_route(self, train_code: str, date: str) -> List[dict]:
        """
        Query train route (stop stations).
        Two-step: search train_no → query route info.
        """
        # Step 1: search for train_no
        search_params = {
            "keyword": train_code,
            "date": date.replace("-", ""),
        }
        resp = self._get(
            f"{config.SEARCH_API_BASE}/search/v1/train/search",
            params=search_params, use_cookie=False
        )
        search_data = resp.json()
        if not search_data.get("data"):
            raise RuntimeError(f"未查询到车次: {train_code}")
        train_no = search_data["data"][0]["train_no"]

        # Step 2: query route with train_no
        route_params = {
            "leftTicketDTO.train_no": train_no,
            "leftTicketDTO.train_date": date,
            "rand_code": "",
        }
        resp2 = self._get(f"{config.API_BASE}/otn/queryTrainInfo/query", params=route_params)
        route_data = resp2.json()
        if not route_data.get("data", {}).get("data"):
            raise RuntimeError(f"未查询到经停站信息: {train_code}")
        return route_data["data"]["data"]

    def query_transfer(self, date: str, from_code: str, to_code: str,
                       middle: str = "", show_wz: bool = False,
                       limit: int = 10) -> List[dict]:
        """
        Query transfer (interline) tickets.
        Fetches lc_search_url dynamically, then paginates results.
        """
        # Get dynamic query path
        resp_init = self._get(config.LCQUERY_INIT_URL)
        m = re.search(r"var\s+lc_search_url\s*=\s*'([^']*)'", resp_init.text)
        if not m:
            raise RuntimeError("Failed to extract lc_search_url from lcQuery/init")
        query_path = m.group(1)
        query_url = f"{config.API_BASE}{query_path}"

        params = {
            "train_date": date,
            "from_station_telecode": from_code,
            "to_station_telecode": to_code,
            "middle_station": middle,
            "result_index": "0",
            "can_query": "Y",
            "isShowWZ": "Y" if show_wz else "N",
            "purpose_codes": "00",
            "channel": "E",
        }

        all_results = []
        while len(all_results) < limit:
            resp = self._get(query_url, params=params)
            data = resp.json()
            if not data.get("status"):
                msg = data.get("errorMsg", "Unknown error")
                raise RuntimeError(f"Transfer query failed: {msg}")

            resp_data = data.get("data")
            if isinstance(resp_data, str) or not resp_data:
                if not all_results:
                    raise RuntimeError(f"未查到中转信息: {data.get('errorMsg', '')}")
                break

            middle_list = resp_data.get("middleList", [])
            all_results.extend(middle_list)

            if resp_data.get("can_query") == "N":
                break
            params["result_index"] = str(resp_data.get("result_index", 0))

        return all_results[:limit]


# =============================================================================
# Data Parsing / 数据解析
# =============================================================================

def parse_tickets(raw_items: List[str], station_map: Dict[str, str]) -> List[TicketInfo]:
    """Parse raw pipe-separated ticket strings into TicketInfo list."""
    TF = config.TICKET_FIELDS
    results = []
    for raw in raw_items:
        fields = raw.split("|")
        if len(fields) < 40:
            continue

        yp_info = fields[TF["yp_info_new"]] if TF["yp_info_new"] < len(fields) else ""
        discount_info = fields[TF["seat_discount_info"]] if TF["seat_discount_info"] < len(fields) else ""
        dw_flag_str = fields[TF["dw_flag"]] if TF["dw_flag"] < len(fields) else ""

        prices = _extract_prices(yp_info, discount_info, fields)
        dw_flags = _extract_dw_flags(dw_flag_str)

        start_date_raw = fields[TF["start_train_date"]]  # yyyyMMdd
        start_time = fields[TF["start_time"]]
        lishi = fields[TF["lishi"]]

        # Calculate dates
        try:
            start_dt = datetime.strptime(start_date_raw, "%Y%m%d")
        except ValueError:
            start_dt = datetime.now()
        start_date_str = start_dt.strftime("%Y-%m-%d")

        # Calculate arrive date from start + duration
        try:
            h, m = map(int, lishi.split(":"))
            sh, sm = map(int, start_time.split(":"))
            arrive_dt = start_dt.replace(hour=sh, minute=sm) + timedelta(hours=h, minutes=m)
            arrive_date_str = arrive_dt.strftime("%Y-%m-%d")
        except (ValueError, IndexError):
            arrive_date_str = start_date_str

        from_code = fields[TF["from_station_telecode"]]
        to_code = fields[TF["to_station_telecode"]]

        results.append(TicketInfo(
            train_no=fields[TF["train_no"]],
            station_train_code=fields[TF["station_train_code"]],
            start_date=start_date_str,
            start_time=start_time,
            arrive_date=arrive_date_str,
            arrive_time=fields[TF["arrive_time"]],
            lishi=lishi,
            from_station=station_map.get(from_code, from_code),
            to_station=station_map.get(to_code, to_code),
            from_station_code=from_code,
            to_station_code=to_code,
            prices=prices,
            dw_flags=dw_flags,
        ))
    return results


def _extract_prices(yp_info: str, discount_info: str, fields) -> List[Price]:
    """
    Extract seat prices from yp_info string.
    Each 10-char block: [0]=type_code, [1:6]/10=price(CNY), [6:10]>=3000→standing.
    """
    PRICE_LEN = 10
    DISC_LEN = 5

    # Parse discounts
    discounts = {}
    for i in range(len(discount_info) // DISC_LEN):
        chunk = discount_info[i * DISC_LEN: (i + 1) * DISC_LEN]
        discounts[chunk[0]] = int(chunk[1:])

    prices = []
    for i in range(len(yp_info) // PRICE_LEN):
        chunk = yp_info[i * PRICE_LEN: (i + 1) * PRICE_LEN]
        type_code = chunk[0]

        # Determine seat type
        if int(chunk[6:10]) >= 3000:
            type_code = "W"  # Standing / 无座
        elif type_code not in config.SEAT_TYPES:
            type_code = "H"  # Other / 其他

        seat_name, short_key = config.SEAT_TYPES.get(type_code, ("其他", "qt"))
        price_val = int(chunk[1:6]) / 10.0

        # Look up remaining tickets from fields
        num_key = f"{short_key}_num"
        idx = config.TICKET_FIELDS.get(num_key)
        num = ""
        if isinstance(fields, list) and idx is not None and idx < len(fields):
            num = fields[idx]
        elif isinstance(fields, dict):
            num = fields.get(num_key, "")

        discount = discounts.get(chunk[0])

        prices.append(Price(
            seat_name=seat_name,
            seat_type_code=type_code,
            price=price_val,
            num=num,
            discount=discount,
        ))
    return prices


def _extract_dw_flags(dw_flag_str: str) -> List[str]:
    """Extract feature flags from #-separated dw_flag string."""
    if not dw_flag_str:
        return []
    parts = dw_flag_str.split("#")
    flags = []
    if parts[0] == "5":
        flags.append(config.DW_FLAGS[0])  # 智能动车组
    if len(parts) > 1 and parts[1] == "1":
        flags.append(config.DW_FLAGS[1])  # 复兴号
    if len(parts) > 2:
        if parts[2].startswith("Q"):
            flags.append(config.DW_FLAGS[2])  # 静音车厢
        elif parts[2].startswith("R"):
            flags.append(config.DW_FLAGS[3])  # 温馨动卧
    if len(parts) > 5 and parts[5] == "D":
        flags.append(config.DW_FLAGS[4])  # 动感号
    if len(parts) > 6 and parts[6] != "z":
        flags.append(config.DW_FLAGS[5])  # 支持选铺
    if len(parts) > 7 and parts[7] != "z":
        flags.append(config.DW_FLAGS[6])  # 老年优惠
    return flags


def parse_route(raw_data: List[dict]) -> List[RouteStationInfo]:
    """Parse route station data into RouteStationInfo list."""
    results = []
    for i, item in enumerate(raw_data):
        info = RouteStationInfo(
            station_name=item.get("station_name", ""),
            station_train_code=item.get("station_train_code", ""),
            arrive_time=item.get("arrive_time", ""),
            start_time=item.get("start_time", ""),
            lishi=item.get("running_time", ""),
            arrive_day_str=item.get("arrive_day_str", ""),
        )
        if i == 0:
            info.train_class_name = item.get("train_class_name")
            info.service_type = item.get("service_type")
            info.end_station_name = item.get("end_station_name")
        results.append(info)
    return results


def parse_transfer(raw_data: List[dict]) -> List[InterlineInfo]:
    """Parse transfer (interline) data into InterlineInfo list."""
    results = []
    for item in raw_data:
        # Parse embedded ticket list
        ticket_list = []
        for tkt in item.get("fullList", []):
            yp_info = tkt.get("yp_info", "")
            discount_info = tkt.get("seat_discount_info", "")
            prices = _extract_prices(yp_info, discount_info, tkt)
            dw_flags = _extract_dw_flags(tkt.get("dw_flag", ""))

            start_date_raw = tkt.get("start_train_date", "")
            start_time = tkt.get("start_time", "")
            lishi = tkt.get("lishi", "")

            try:
                start_dt = datetime.strptime(start_date_raw, "%Y%m%d")
            except ValueError:
                start_dt = datetime.now()
            start_date_str = start_dt.strftime("%Y-%m-%d")

            try:
                h, m = map(int, lishi.split(":"))
                sh, sm = map(int, start_time.split(":"))
                arrive_dt = start_dt.replace(hour=sh, minute=sm) + timedelta(hours=h, minutes=m)
                arrive_date_str = arrive_dt.strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                arrive_date_str = start_date_str

            ticket_list.append(TicketInfo(
                train_no=tkt.get("train_no", ""),
                station_train_code=tkt.get("station_train_code", ""),
                start_date=start_date_str,
                start_time=start_time,
                arrive_date=arrive_date_str,
                arrive_time=tkt.get("arrive_time", ""),
                lishi=lishi,
                from_station=tkt.get("from_station_name", ""),
                to_station=tkt.get("to_station_name", ""),
                from_station_code=tkt.get("from_station_telecode", ""),
                to_station_code=tkt.get("to_station_telecode", ""),
                prices=prices,
                dw_flags=dw_flags,
            ))

        lishi = _extract_lishi(item.get("all_lishi", ""))

        results.append(InterlineInfo(
            lishi=lishi,
            start_time=item.get("start_time", ""),
            start_date=item.get("train_date", ""),
            middle_date=item.get("middle_date", ""),
            arrive_date=item.get("arrive_date", ""),
            arrive_time=item.get("arrive_time", ""),
            from_station_name=item.get("from_station_name", ""),
            from_station_code=item.get("from_station_code", ""),
            middle_station_name=item.get("middle_station_name", ""),
            middle_station_code=item.get("middle_station_code", ""),
            end_station_name=item.get("end_station_name", ""),
            end_station_code=item.get("end_station_code", ""),
            start_train_code=ticket_list[0].station_train_code if ticket_list else "",
            first_train_no=item.get("first_train_no", ""),
            second_train_no=item.get("second_train_no", ""),
            train_count=item.get("train_count", 0),
            ticket_list=ticket_list,
            same_station=item.get("same_station") == "0",
            same_train=item.get("same_train") == "Y",
            wait_time=item.get("wait_time", ""),
        ))
    return results


def _extract_lishi(all_lishi: str) -> str:
    """Convert 'X小时Y分钟' or 'Y分钟' to 'HH:MM' format."""
    m = re.match(r"(?:(\d+)小时)?(\d+)分钟", all_lishi)
    if not m:
        return all_lishi  # Return as-is if no match
    hours = m.group(1) or "0"
    minutes = m.group(2)
    return f"{int(hours):02d}:{int(minutes):02d}"


# =============================================================================
# Filter & Sort / 筛选排序
# =============================================================================

def filter_and_sort(items, train_type=None, earliest=0, latest=24,
                    sort_by=None, reverse=False, limit=0):
    """
    Filter and sort ticket/transfer results.
    items: List of TicketInfo or InterlineInfo.
    """
    result = list(items)

    # Train type filter / 车次类型筛选
    if train_type:
        type_chars = train_type.upper()
        filtered = []
        for item in result:
            code = item.station_train_code if hasattr(item, 'station_train_code') else item.start_train_code
            dw = item.dw_flags if hasattr(item, 'dw_flags') else (
                item.ticket_list[0].dw_flags if item.ticket_list else [])
            for tc in type_chars:
                if _match_train_type(code, dw, tc):
                    filtered.append(item)
                    break
        result = filtered

    # Time window filter / 出发时间窗口
    if earliest > 0 or latest < 24:
        result = [
            item for item in result
            if earliest <= int(item.start_time.split(":")[0]) < latest
        ]

    # Sort / 排序
    if sort_by:
        key_fn = _sort_key(sort_by)
        if key_fn:
            result.sort(key=key_fn, reverse=reverse)

    # Limit / 限制数量
    if limit > 0:
        result = result[:limit]

    return result


def _match_train_type(code: str, dw_flags: List[str], type_char: str) -> bool:
    """Check if a train matches the given type filter character."""
    c = code[0] if code else ""
    if type_char == "G":
        return c in ("G", "C")
    elif type_char == "D":
        return c == "D"
    elif type_char == "Z":
        return c == "Z"
    elif type_char == "T":
        return c == "T"
    elif type_char == "K":
        return c == "K"
    elif type_char == "O":
        return c not in ("G", "C", "D", "Z", "T", "K")
    elif type_char == "F":
        return "复兴号" in dw_flags
    elif type_char == "S":
        return "智能动车组" in dw_flags
    return False


def _sort_key(sort_by: str):
    """Return a sort key function for the given sort flag."""
    if sort_by == "startTime":
        return lambda x: (x.start_date, x.start_time)
    elif sort_by == "arriveTime":
        return lambda x: (x.arrive_date, x.arrive_time)
    elif sort_by == "duration":
        return lambda x: x.lishi
    return None


# =============================================================================
# Output Formatting / 格式化输出
# =============================================================================

def _format_ticket_status(num: str) -> str:
    """Format remaining ticket count for display."""
    if num.isdigit():
        n = int(num)
        return "无票" if n == 0 else f"{n}张"
    status_map = {"有": "有票", "充足": "有票", "无": "无票", "--": "无票",
                  "": "无票", "候补": "候补"}
    return status_map.get(num, num)


def format_tickets_text(tickets: List[TicketInfo]) -> str:
    """Format ticket list as human-readable text table."""
    if not tickets:
        return "没有查询到相关车次信息。建议: 尝试调整日期、取消类型筛选、或扩大时间范围"

    lines = ["车次 | 出发站→到达站 | 出发→到达 | 历时 | 席位信息 | 标签"]
    lines.append("-" * 80)
    for t in tickets:
        tags = "/".join(t.dw_flags) if t.dw_flags else ""
        seats = ", ".join(
            f"{p.seat_name}:{_format_ticket_status(p.num)}/{p.price}元"
            + (f"({p.discount}折)" if p.discount and p.discount < 100 else "")
            for p in t.prices
        )
        lines.append(
            f"{t.station_train_code} | {t.from_station}→{t.to_station} | "
            f"{t.start_time}→{t.arrive_time} | {t.lishi} | {seats}"
            + (f" | {tags}" if tags else "")
        )
    return "\n".join(lines)


def format_tickets_json(tickets: List[TicketInfo]) -> str:
    """Format ticket list as JSON."""
    return json.dumps([asdict(t) for t in tickets], ensure_ascii=False, indent=2)


def format_tickets_csv(tickets: List[TicketInfo]) -> str:
    """Format ticket list as CSV."""
    if not tickets:
        return "没有查询到相关车次信息。建议: 尝试调整日期、取消类型筛选、或扩大时间范围"
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["车次", "出发站", "到达站", "出发时间", "到达时间", "历时", "票价", "标签"])
    for t in tickets:
        seats = "; ".join(
            f"{p.seat_name}:{_format_ticket_status(p.num)}/{p.price}元" for p in t.prices
        )
        tags = "/".join(t.dw_flags) if t.dw_flags else ""
        writer.writerow([
            t.station_train_code, t.from_station, t.to_station,
            t.start_time, t.arrive_time, t.lishi, seats, tags
        ])
    return buf.getvalue()


def format_route_text(stations: List[RouteStationInfo]) -> str:
    """Format route station list as text."""
    if not stations:
        return "未查询到经停站信息。建议: 请确认车次号和日期是否正确"

    first = stations[0]
    ac = "有空调" if first.service_type == "1" else "无空调"
    header = f"{first.station_train_code}次列车（{first.train_class_name or ''} {ac}）"
    lines = [header, "站序 | 车站 | 到达时间 | 出发时间 | 停留 | 运行时长"]
    lines.append("-" * 60)
    for i, st in enumerate(stations):
        lines.append(
            f"{i+1:3d} | {st.station_name} | {st.arrive_time} | "
            f"{st.start_time} | {st.arrive_day_str} | {st.lishi}"
        )
    return "\n".join(lines)


def format_route_json(stations: List[RouteStationInfo]) -> str:
    """Format route station list as JSON."""
    return json.dumps([asdict(s) for s in stations], ensure_ascii=False, indent=2)


def format_transfer_text(transfers: List[InterlineInfo]) -> str:
    """Format transfer list as text."""
    if not transfers:
        return "没有查询到中转方案。建议: 尝试调整日期或不指定中转站"

    lines = ["出发时间→到达时间 | 出发站→中转站→到达站 | 换乘方式 | 等待时间 | 总历时"]
    lines.append("=" * 90)
    for tr in transfers:
        if tr.same_train:
            mode = "同车换乘"
        elif tr.same_station:
            mode = "同站换乘"
        else:
            mode = "换站换乘"

        lines.append(
            f"{tr.start_date} {tr.start_time}→{tr.arrive_date} {tr.arrive_time} | "
            f"{tr.from_station_name}→{tr.middle_station_name}→{tr.end_station_name} | "
            f"{mode} | {tr.wait_time} | {tr.lishi}"
        )
        # Show each leg's ticket info
        for tkt in tr.ticket_list:
            seats = ", ".join(
                f"{p.seat_name}:{_format_ticket_status(p.num)}/{p.price}元"
                for p in tkt.prices
            )
            lines.append(
                f"  └ {tkt.station_train_code} {tkt.from_station}→{tkt.to_station} "
                f"{tkt.start_time}→{tkt.arrive_time} {tkt.lishi} | {seats}"
            )
        lines.append("")
    return "\n".join(lines)


def format_transfer_json(transfers: List[InterlineInfo]) -> str:
    """Format transfer list as JSON."""
    return json.dumps([asdict(t) for t in transfers], ensure_ascii=False, indent=2)


# =============================================================================
# CLI Commands / CLI 命令
# =============================================================================

def cmd_query(args):
    """Handle 'query' subcommand."""
    api = TrainAPI()
    from_code = station_manager.resolve_station(args.from_station)
    to_code = station_manager.resolve_station(args.to_station)
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    logger.info("Query: %s→%s on %s", args.from_station, args.to_station, date)

    raw_items, station_map = api.query_tickets(date, from_code, to_code)
    tickets = parse_tickets(raw_items, station_map)
    logger.info("Found %d tickets", len(tickets))

    tickets = filter_and_sort(
        tickets,
        train_type=args.type,
        earliest=args.earliest,
        latest=args.latest,
        sort_by=args.sort,
        reverse=args.reverse,
        limit=args.limit,
    )

    fmt = (args.format or config.DEFAULT_FORMAT).lower()
    if fmt == "json":
        print(format_tickets_json(tickets))
    elif fmt == "csv":
        print(format_tickets_csv(tickets))
    else:
        print(format_tickets_text(tickets))


def cmd_route(args):
    """Handle 'route' subcommand."""
    api = TrainAPI()
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    logger.info("Route: %s on %s", args.code, date)

    raw_data = api.query_route(args.code, date)
    stations = parse_route(raw_data)
    logger.info("Found %d stops", len(stations))

    fmt = (args.format or config.DEFAULT_FORMAT).lower()
    if fmt == "json":
        print(format_route_json(stations))
    else:
        print(format_route_text(stations))


def cmd_transfer(args):
    """Handle 'transfer' subcommand."""
    api = TrainAPI()
    from_code = station_manager.resolve_station(args.from_station)
    to_code = station_manager.resolve_station(args.to_station)
    middle_code = ""
    if args.middle:
        middle_code = station_manager.resolve_station(args.middle)
    date = args.date or datetime.now().strftime("%Y-%m-%d")
    limit = args.limit or 10
    logger.info("Transfer: %s→%s on %s", args.from_station, args.to_station, date)

    raw_data = api.query_transfer(date, from_code, to_code, middle_code,
                                  show_wz=args.show_wz, limit=limit)
    transfers = parse_transfer(raw_data)
    logger.info("Found %d transfer options", len(transfers))

    transfers = filter_and_sort(
        transfers,
        train_type=args.type,
        earliest=args.earliest,
        latest=args.latest,
        sort_by=args.sort,
        reverse=args.reverse,
        limit=limit,
    )

    fmt = (args.format or config.DEFAULT_FORMAT).lower()
    if fmt == "json":
        print(format_transfer_json(transfers))
    else:
        print(format_transfer_text(transfers))


# =============================================================================
# CLI Argument Parser / CLI 参数解析
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trainclaw",
        description="TrainClaw - 12306 Train Ticket CLI Tool (v{})".format(__version__),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Enable verbose/debug logging / 启用详细日志")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- query (alias: filter) ---
    query_parser = subparsers.add_parser("query", aliases=["filter"],
                                         help="Query remaining tickets / 余票查询")
    query_parser.add_argument("-f", "--from", dest="from_station", required=True,
                              help="Departure station name/city/code / 出发站")
    query_parser.add_argument("-t", "--to", dest="to_station", required=True,
                              help="Arrival station name/city/code / 到达站")
    query_parser.add_argument("-d", "--date", default=None,
                              help="Date yyyy-MM-dd (default: today) / 日期")
    query_parser.add_argument("--type", default=None,
                              help="Train type filter: G/D/Z/T/K/O/F/S / 车次类型")
    query_parser.add_argument("--earliest", type=int, default=0,
                              help="Earliest departure hour 0-24 (default: 0)")
    query_parser.add_argument("--latest", type=int, default=24,
                              help="Latest departure hour 0-24 (default: 24)")
    query_parser.add_argument("--sort", default=None,
                              choices=["startTime", "arriveTime", "duration"],
                              help="Sort by field / 排序方式")
    query_parser.add_argument("--reverse", action="store_true",
                              help="Reverse sort order / 倒序")
    query_parser.add_argument("-n", "--limit", type=int, default=0,
                              help="Max results (default: 0=unlimited) / 最大结果数")
    query_parser.add_argument("-o", "--format", default=None,
                              choices=["text", "json", "csv"],
                              help="Output format (default: text)")
    query_parser.set_defaults(func=cmd_query)

    # --- route ---
    route_parser = subparsers.add_parser("route", help="Query train route / 经停站查询")
    route_parser.add_argument("-c", "--code", required=True,
                              help="Train code, e.g. G1033 / 车次号")
    route_parser.add_argument("-d", "--date", default=None,
                              help="Date yyyy-MM-dd (default: today) / 日期")
    route_parser.add_argument("-o", "--format", default=None,
                              choices=["text", "json"],
                              help="Output format (default: text)")
    route_parser.set_defaults(func=cmd_route)

    # --- transfer ---
    transfer_parser = subparsers.add_parser("transfer", help="Query transfer routes / 中转查询")
    transfer_parser.add_argument("-f", "--from", dest="from_station", required=True,
                                 help="Departure station / 出发站")
    transfer_parser.add_argument("-t", "--to", dest="to_station", required=True,
                                 help="Arrival station / 到达站")
    transfer_parser.add_argument("-m", "--middle", default=None,
                                 help="Transfer station (optional) / 中转站")
    transfer_parser.add_argument("-d", "--date", default=None,
                                 help="Date yyyy-MM-dd (default: today) / 日期")
    transfer_parser.add_argument("--type", default=None,
                                 help="Train type filter: G/D/Z/T/K/O/F/S")
    transfer_parser.add_argument("--earliest", type=int, default=0,
                                 help="Earliest departure hour 0-24")
    transfer_parser.add_argument("--latest", type=int, default=24,
                                 help="Latest departure hour 0-24")
    transfer_parser.add_argument("--sort", default=None,
                                 choices=["startTime", "arriveTime", "duration"],
                                 help="Sort by field / 排序方式")
    transfer_parser.add_argument("--reverse", action="store_true",
                                 help="Reverse sort order / 倒序")
    transfer_parser.add_argument("-n", "--limit", type=int, default=10,
                                 help="Max results (default: 10)")
    transfer_parser.add_argument("--show-wz", action="store_true",
                                 help="Include standing tickets / 显示无座")
    transfer_parser.add_argument("-o", "--format", default=None,
                                 choices=["text", "json"],
                                 help="Output format (default: text)")
    transfer_parser.set_defaults(func=cmd_transfer)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if getattr(args, 'verbose', False) else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except ValueError as e:
        logger.debug("ValueError", exc_info=True)
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        logger.debug("RuntimeError", exc_info=True)
        msg = str(e)
        if "12306 query failed" in msg or "Transfer query failed" in msg:
            print("查询失败: 12306 服务暂时不可用，请稍后重试", file=sys.stderr)
        else:
            print(f"错误: {msg}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException:
        logger.debug("RequestException", exc_info=True)
        print("网络连接失败，请检查网络后重试", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
