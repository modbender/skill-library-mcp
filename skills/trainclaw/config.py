"""
TrainClaw Configuration / 配置文件
All constants and default values for the China train ticket CLI tool.
所有常量和默认值，车票查询AI助手 CLI 工具。

GitHub: https://github.com/AI4MSE/TrainClaw
License: Apache-2.0

免责声明 / Disclaimer:
本工具仅供学习和交流之用，使用时请遵守当地法律和法规。
This tool is for educational and research purposes only.
Please comply with local laws and regulations when using it.
"""

# =============================================================================
# API Endpoints / API 端点
# =============================================================================

# Main API base URL / 主 API 基础地址 (余票查询、经停站查询、Cookie 获取)
API_BASE = "https://kyfw.12306.cn"

# Search API base URL / 搜索 API 基础地址 (车次搜索，用于获取 train_no)
SEARCH_API_BASE = "https://search.12306.cn"

# 12306 web homepage / 12306 首页 (用于提取 station_name JS 路径)
WEB_URL = "https://www.12306.cn/index/"

# Transfer query init page / 中转查询初始化页面 (用于提取动态查询路径)
LCQUERY_INIT_URL = "https://kyfw.12306.cn/otn/lcQuery/init"

# =============================================================================
# Cache Settings / 缓存配置
# =============================================================================

# Cache directory path / 缓存目录路径
CACHE_DIR = "cache"

# Station data cache file name / 车站数据缓存文件名
STATION_CACHE_FILE = "stations.json"

# Station cache TTL in seconds (7 days) / 车站缓存有效期（7 天）
STATION_CACHE_TTL = 7 * 24 * 3600

# =============================================================================
# Default Query Parameters / 默认查询参数
# =============================================================================

# Default output format / 默认输出格式 (text | json | csv)
DEFAULT_FORMAT = "text"

# Default ticket purpose / 默认购票类型 (ADULT=成人)
DEFAULT_PURPOSE = "ADULT"

# Timezone for date calculations / 日期计算时区
TIMEZONE = "Asia/Shanghai"

# =============================================================================
# Network Settings / 网络配置
# =============================================================================

# HTTP request timeout in seconds / HTTP 请求超时（秒）
REQUEST_TIMEOUT = 15

# Max retry attempts for failed requests / 请求失败最大重试次数
MAX_RETRIES = 2

# Minimum interval between API requests (seconds) / API 请求最小间隔（秒）
QUERY_COOLDOWN = 1

# User-Agent header / 浏览器标识
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# =============================================================================
# Seat Type Mapping / 座位类型映射表
# =============================================================================
# Maps seat type code (from yp_info) to (display_name, short_key)
# 将座位类型码（来自 yp_info）映射为（显示名称, 余票字段简称）
# short_key is used to look up `{short}_num` in ticket fields
# short_key 用于在车票字段中查找 `{short}_num`

SEAT_TYPES = {
    "9":  ("商务座",     "swz"),   # Business class
    "P":  ("特等座",     "tz"),    # Premier class
    "M":  ("一等座",     "zy"),    # First class
    "D":  ("优选一等座", "zy"),    # Premium first class
    "O":  ("二等座",     "ze"),    # Second class
    "S":  ("二等包座",   "ze"),    # Second class compartment
    "6":  ("高级软卧",   "gr"),    # Deluxe soft sleeper
    "A":  ("高级动卧",   "gr"),    # Deluxe EMU sleeper
    "4":  ("软卧",       "rw"),    # Soft sleeper
    "I":  ("一等卧",     "rw"),    # First class sleeper
    "F":  ("动卧",       "rw"),    # EMU sleeper
    "3":  ("硬卧",       "yw"),    # Hard sleeper
    "J":  ("二等卧",     "yw"),    # Second class sleeper
    "2":  ("软座",       "rz"),    # Soft seat
    "1":  ("硬座",       "yz"),    # Hard seat
    "W":  ("无座",       "wz"),    # Standing (no seat)
    "WZ": ("无座",       "wz"),    # Standing (alternate code)
    "H":  ("其他",       "qt"),    # Other
}

# =============================================================================
# Ticket Field Indices / 车票字段索引 (57 fields, pipe-separated)
# =============================================================================
# Index positions for fields in the pipe-separated ticket string from 12306 API.
# 12306 API 返回的管道分隔车票字符串中各字段的索引位置。

TICKET_FIELDS = {
    "secret_str":             0,
    "button_text_info":       1,
    "train_no":               2,   # Internal train number / 内部车次编号
    "station_train_code":     3,   # Display train code (e.g. G1033) / 显示车次号
    "start_station_telecode": 4,   # Origin station code / 始发站代码
    "end_station_telecode":   5,   # Terminal station code / 终到站代码
    "from_station_telecode":  6,   # Boarding station code / 出发站代码
    "to_station_telecode":    7,   # Alighting station code / 到达站代码
    "start_time":             8,   # Departure time HH:MM / 出发时间
    "arrive_time":            9,   # Arrival time HH:MM / 到达时间
    "lishi":                  10,  # Duration HH:MM / 历时
    "can_web_buy":            11,  # Can buy online / 是否可网购
    "yp_info":                12,  # Ticket price info (old) / 票价信息（旧）
    "start_train_date":       13,  # Departure date yyyyMMdd / 出发日期
    "train_seat_feature":     14,  # Seat feature / 座位特征
    "location_code":          15,  # Location code / 地区代码
    "from_station_no":        16,  # Boarding station sequence / 出发站序号
    "to_station_no":          17,  # Alighting station sequence / 到达站序号
    "is_support_card":        18,  # Card support / 身份证支持
    "controlled_train_flag":  19,  # Controlled flag / 控制标志
    "gg_num":                 20,  # 观光座余票
    "gr_num":                 21,  # 高软卧余票
    "qt_num":                 22,  # 其他余票
    "rw_num":                 23,  # 软卧余票
    "rz_num":                 24,  # 软座余票
    "tz_num":                 25,  # 特等座余票
    "wz_num":                 26,  # 无座余票
    "yb_num":                 27,  # 预留余票
    "yw_num":                 28,  # 硬卧余票
    "yz_num":                 29,  # 硬座余票
    "ze_num":                 30,  # 二等座余票
    "zy_num":                 31,  # 一等座余票
    "swz_num":                32,  # 商务座余票
    "srrb_num":               33,  # 动卧余票
    "yp_ex":                  34,  # Extended price info / 扩展票价
    "seat_types":             35,  # Available seat types / 可用座位类型
    "exchange_train_flag":    36,  # Exchange flag / 换乘标志
    "houbu_train_flag":       37,  # Houbu flag / 候补标志
    "houbu_seat_limit":       38,  # Houbu seat limit / 候补座位限制
    "yp_info_new":            39,  # New ticket price info / 新票价信息
    "dw_flag":                46,  # DW feature flags / 特征标志
    "stopcheck_time":         48,  # Stop check time / 检票时间
    "country_flag":           49,  # Country flag / 国际标志
    "local_arrive_time":      50,  # Local arrival time / 当地到达时间
    "local_start_time":       51,  # Local departure time / 当地出发时间
    "bed_level_info":         53,  # Bed level info / 铺位信息
    "seat_discount_info":     54,  # Seat discount info / 座位折扣信息
    "sale_time":              55,  # Sale time / 售票时间
}

# =============================================================================
# DW Feature Flags / 特征标志映射
# =============================================================================
# Extracted from dw_flag field (# separated), index-based detection.
# 从 dw_flag 字段提取（#分隔），按索引检测。

DW_FLAGS = [
    "智能动车组",  # index 0, value='5'
    "复兴号",      # index 1, value='1'
    "静音车厢",    # index 2, starts with 'Q'
    "温馨动卧",    # index 2, starts with 'R'
    "动感号",      # index 5, value='D'
    "支持选铺",    # index 6, not 'z'
    "老年优惠",    # index 7, not 'z'
]

# =============================================================================
# Missing Stations / 缺失车站补充
# =============================================================================
# Stations missing from the official station_name JS file.
# 官方 station_name JS 文件中缺失的车站。
# Format: (id, name, code, pinyin, short, index, city_code, city, r1, r2)

MISSING_STATIONS = [
    {
        "station_id": "@cdd",
        "station_name": "成  都东",
        "station_code": "WEI",
        "station_pinyin": "chengdudong",
        "station_short": "cdd",
        "station_index": "",
        "code": "1707",
        "city": "成都",
        "r1": "",
        "r2": "",
    },
]
