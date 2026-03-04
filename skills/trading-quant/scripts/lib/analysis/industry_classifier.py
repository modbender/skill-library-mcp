"""行业分类模块 - 完全依赖券商接口获取准确数据."""

import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# 持久化缓存行业数据
_CACHE_FILE = "/tmp/quant_industry_cache.json"
_industry_cache: Dict[str, str] = {}
_cache_loaded = False

def _load_file_cache():
    global _industry_cache, _cache_loaded
    if _cache_loaded:
        return
    try:
        import os
        if os.path.exists(_CACHE_FILE):
            with open(_CACHE_FILE) as f:
                _industry_cache = json.load(f)
    except Exception:
        pass
    if not _industry_cache:
        _prefill_from_watchlist()
    _cache_loaded = True


def _prefill_from_watchlist():
    """从 watchlist.json 预填充行业分类（自选股行业不变，无需网络请求）"""
    global _industry_cache
    try:
        import os
        wl_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "knowledge", "watchlist.json")
        wl_path = os.path.normpath(wl_path)
        if not os.path.exists(wl_path):
            return
        with open(wl_path) as f:
            wl = json.load(f)
        for cat in ("priority", "observe", "research"):
            for item in wl.get(cat, []):
                if isinstance(item, dict):
                    code = item.get("code", "")
                    sector = item.get("sector", "")
                    if code and sector:
                        _industry_cache[code] = _normalize_industry_name(sector.split("/")[0])
        if _industry_cache:
            _save_file_cache()
            logger.info(f"Pre-filled {len(_industry_cache)} industries from watchlist")
    except Exception as e:
        logger.debug(f"Watchlist prefill failed: {e}")

def _save_file_cache():
    try:
        import json as _json
        with open(_CACHE_FILE, "w") as f:
            _json.dump(_industry_cache, f, ensure_ascii=False)
    except Exception:
        pass


def classify_industry(code: str) -> str:
    """
    使用券商/数据接口获取准确的行业分类.
    
    优先级:
    1. 东方财富接口 (eastmoney) - 最可靠
    2. akshare 股票基本信息
    3. 同花顺接口 (ths)
    
    如果所有接口都失败，返回 "unknown"，不进行猜测.
    
    Args:
        code: 股票代码
    
    Returns:
        行业分类名称，失败返回 "unknown"
    """
    _load_file_cache()
    if code in _industry_cache:
        return _industry_cache[code]
    
    industry = None
    
    # 尝试 1: 东方财富接口 (akshare)
    try:
        industry = _get_industry_from_eastmoney(code)
        if industry and industry != "unknown":
            _industry_cache[code] = industry
            _save_file_cache()
            logger.debug(f"Got industry for {code} from EastMoney: {industry}")
            return industry
    except Exception as e:
        logger.debug(f"EastMoney industry fetch failed for {code}: {e}")
    
    # 尝试 2: akshare 股票基本信息（拉取全市场数据，性能差，降级跳过）
    # _get_industry_from_akshare 会调用 stock_zh_a_spot_em() 拉取 5000+ 股票
    # 东方财富个股接口已足够，无需全市场查询
    
    # 尝试 3: 同花顺接口（非常慢，遍历所有行业板块，降级跳过）
    # 注释掉以避免性能问题：对每只股票遍历所有行业板块是O(N*M)复杂度
    # try:
    #     industry = _get_industry_from_ths(code)
    #     ...
    
    # 所有接口都失败，返回 unknown
    logger.warning(f"Failed to get industry for {code} from all sources")
    _industry_cache[code] = "unknown"
    _save_file_cache()
    return "unknown"


def _get_industry_from_eastmoney(code: str) -> Optional[str]:
    """从东方财富获取行业分类（通过akshare）."""
    try:
        import akshare as ak
        
        # 使用东方财富个股信息接口
        df = ak.stock_individual_info_em(symbol=code)
        if df is not None and not df.empty:
            # 查找行业信息
            industry_row = df[df['item'] == '行业']
            if not industry_row.empty:
                industry = industry_row['value'].values[0]
                if industry and industry != '-' and industry != 'None':
                    return _normalize_industry_name(industry)
        
        return "unknown"
    except Exception as e:
        logger.debug(f"Failed to get EastMoney industry for {code}: {e}")
        return "unknown"


def _get_industry_from_akshare(code: str) -> Optional[str]:
    """从 akshare 获取行业分类."""
    try:
        import akshare as ak
        
        # 使用股票基本信息接口
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            stock_row = df[df['代码'] == code]
            if not stock_row.empty:
                # 尝试获取行业列
                if '行业' in stock_row.columns:
                    industry = stock_row['行业'].values[0]
                    if industry and industry != '-' and pd.notna(industry):
                        return _normalize_industry_name(industry)
        
        return "unknown"
    except Exception as e:
        logger.debug(f"Failed to get AKShare industry for {code}: {e}")
        return "unknown"


def _get_industry_from_ths(code: str) -> Optional[str]:
    """从同花顺获取行业分类."""
    try:
        import akshare as ak
        
        # 使用同花顺行业数据接口
        # 获取所有行业板块
        df = ak.stock_board_industry_name_ths()
        if df is not None and not df.empty:
            # 遍历行业，查找成分股
            for _, row in df.iterrows():
                industry_name = row.get('名称', '')
                if not industry_name:
                    continue
                
                try:
                    # 获取该行业的成分股
                    stocks_df = ak.stock_board_industry_cons_ths(symbol=industry_name)
                    if stocks_df is not None and not stocks_df.empty:
                        # 检查目标股票是否在该行业
                        if '代码' in stocks_df.columns:
                            if code in stocks_df['代码'].values:
                                return _normalize_industry_name(industry_name)
                        elif 'symbol' in stocks_df.columns:
                            if code in stocks_df['symbol'].values:
                                return _normalize_industry_name(industry_name)
                except Exception:
                    continue
        
        return "unknown"
    except Exception as e:
        logger.debug(f"Failed to get THS industry for {code}: {e}")
        return "unknown"


def _normalize_industry_name(industry: str) -> str:
    """
    标准化行业名称到内部分类.
    
    将各种数据源返回的行业名称统一为内部标准名称.
    """
    if not industry or industry == '-':
        return "unknown"
    
    industry = str(industry).strip()
    
    # 直接映射表
    industry_map = {
        # 银行
        "银行": "银行", "商业银行": "银行", "股份制银行": "银行", "城商行": "银行",
        
        # 地产
        "房地产": "地产", "房地产开发": "地产", "物业管理": "地产", "商业地产": "地产",
        
        # 钢铁
        "钢铁": "钢铁", "普钢": "钢铁", "特钢": "钢铁", "钢铁制品": "钢铁",
        
        # 煤炭
        "煤炭": "煤炭", "煤炭开采": "煤炭", "焦炭": "煤炭", "煤化工": "煤炭",
        
        # 石油
        "石油": "石油", "石油化工": "石油", "油气开采": "石油", "炼油": "石油",
        
        # 电力
        "电力": "电力", "火电": "电力", "水电": "电力", "核电": "电力", 
        "风电": "新能源", "光伏": "新能源", "电力设备": "新能源",
        
        # 有色
        "有色金属": "有色", "贵金属": "有色", "工业金属": "有色", "稀有金属": "有色",
        "铜": "有色", "铝": "有色", "锌": "有色", "镍": "有色", "钴": "有色", "锂": "有色",
        
        # 化工
        "化工": "化工", "化学制品": "化工", "化学原料": "化工", "化肥": "化工", 
        "农药": "化工", "化纤": "化工", "塑料": "化工", "橡胶": "化工",
        
        # 消费
        "食品加工": "消费", "饮料制造": "消费", "休闲食品": "消费", "调味品": "消费",
        "乳业": "消费", "肉制品": "消费", "啤酒": "消费", "食品饮料": "消费",
        
        # 白酒
        "白酒": "白酒", "白酒Ⅱ": "白酒", "白酒Ⅲ": "白酒", "酿酒": "白酒",
        
        # 医药
        "医药": "医药", "生物医药": "医药", "化学制药": "医药", "中药": "医药", 
        "医疗器械": "医药", "医疗服务": "医药", "疫苗": "医药", "生物制品": "医药",
        
        # 科技
        "计算机": "科技", "软件": "科技", "IT服务": "科技", "互联网": "科技",
        "通信": "科技", "通信设备": "科技", "传媒": "科技", "电子": "半导体",
        
        # 半导体
        "半导体": "半导体", "集成电路": "半导体", "芯片": "半导体", 
        "元件": "半导体", "光学光电子": "半导体",
        
        # 军工
        "国防军工": "军工", "军工": "军工", "航天": "军工", "航空": "军工", 
        "船舶": "军工", "兵器": "军工",
        
        # 新能源
        "新能源": "新能源", "电池": "新能源", "锂电池": "新能源", "储能": "新能源",
        "光伏设备": "新能源", "风电设备": "新能源", "新能源汽车": "新能源",
        "电网设备": "新能源",
        
        # ETF
        "ETF": "ETF",
    }
    
    # 直接映射
    if industry in industry_map:
        return industry_map[industry]
    
    # 部分匹配
    for key, value in industry_map.items():
        if key in industry:
            return value
    
    # 无法识别的行业，返回原始值（小写处理）
    logger.debug(f"Unrecognized industry name: {industry}, using as-is")
    return industry


def clear_industry_cache():
    """清除行业分类缓存."""
    global _industry_cache
    _industry_cache.clear()


def get_cached_industries() -> Dict[str, str]:
    """获取已缓存的行业分类."""
    return _industry_cache.copy()


# 兼容性别名
classify_industry_by_api = classify_industry