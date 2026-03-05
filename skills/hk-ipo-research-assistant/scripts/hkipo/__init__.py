"""hkipo - Hong Kong IPO Data Tool"""

from .aastocks import get_upcoming_ipos as fetch_upcoming_ipos, get_ipo_detail as fetch_ipo_detail
from .jisilu import fetch_jisilu_history, get_jisilu_stock
from .futu import FutuListedIPO, fetch_futu_listed_ipos, fetch_futu_recent_performance
from .tradesmart import (
    fetch_tradesmart_ipos,
    get_tradesmart_ipo,
    get_entry_amount,
)
from .allotment import (
    predict_allotment,
    predict_allotment_table,
    format_allotment_table,
    base_p1,
    calculate_win_probability,
    lot_demand_multiplier,
)
from .etnet import (
    SponsorStats,
    fetch_sponsor_rankings,
    get_sponsor_stats,
    get_top_sponsors,
    get_sponsors_by_up_rate,
)
from .aipo import (
    # Data classes
    BrokerMargin,
    MarginSummary,
    AgencyRating,
    GreyMarketData,
    CornerstoneInvestor,
    # Margin APIs
    fetch_margin_list,
    fetch_margin_detail,
    get_margin_by_code,
    format_margin_table,
    # Rating APIs
    fetch_rating_list,
    fetch_rating_detail,
    get_rating_by_code,
    format_rating_table,
    # Grey Market APIs
    fetch_grey_list,
    fetch_allotment_results,
    fetch_today_grey_market,
    fetch_grey_trade_details,
    fetch_grey_price_distribution,
    fetch_grey_price_distribution_detail,
    fetch_grey_placing_detail,
    fetch_market_scroll_messages,
    # IPO Detail APIs
    fetch_ipo_brief,
    fetch_cornerstone_investors,
    fetch_placing_result,
    fetch_company_managers,
    # Sponsor APIs
    fetch_sponsor_history,
    # Statistics APIs (年度统计)
    fetch_ipo_summary,
    fetch_ipo_performance_by_year,
    fetch_ipo_by_registered_office,
)
from .aastocks import (
    get_upcoming_ipos as aastocks_get_upcoming_ipos,
    get_listed_ipos as aastocks_get_listed_ipos,
    get_ipo_detail as aastocks_get_ipo_detail,
    get_allotment_results as aastocks_get_allotment_results,
    get_grey_market_schedule as aastocks_get_grey_market_schedule,
    get_sponsor_performance as aastocks_get_sponsor_performance,
)
from .hkex import (
    HKEXIPO,
    HKEXDocument,
    fetch_hkex_active_ipos,
    fetch_hkex_listed_ipos,
    get_prospectus_url,
    get_document_by_type,
    fetch_hkex_active_ipos_sync,
    fetch_hkex_listed_ipos_sync,
)
from .cache import (
    get_cached,
    set_cached,
    get_or_fetch,
    get_sponsors,
    get_jisilu_history as get_jisilu_history_cached,
    get_active_ipos,
    get_hkex_listed,
    get_ipo_detail,
    list_cache,
    clear_expired,
    clear_all,
    get_cache_stats,
    TTL_SHORT,
    TTL_LONG,
    TTL_PERMANENT,
)

__version__ = "2.0.0"
__all__ = [
    "fetch_upcoming_ipos",
    "fetch_ipo_detail",
    "fetch_jisilu_history",
    "get_jisilu_stock",
    "FutuListedIPO",
    "fetch_futu_listed_ipos",
    "fetch_futu_recent_performance",
    "fetch_tradesmart_ipos",
    "get_tradesmart_ipo",
    "get_entry_amount",
    # allotment prediction
    "predict_allotment",
    "predict_allotment_table",
    "format_allotment_table",
    "base_p1",
    "calculate_win_probability",
    "lot_demand_multiplier",
    # etnet sponsor
    "SponsorStats",
    "fetch_sponsor_rankings",
    "get_sponsor_stats",
    "get_top_sponsors",
    "get_sponsors_by_up_rate",
    # aipo margin data
    "BrokerMargin",
    "MarginSummary",
    "AgencyRating",
    "GreyMarketData",
    "CornerstoneInvestor",
    "fetch_margin_list",
    "fetch_margin_detail",
    "get_margin_by_code",
    "format_margin_table",
    # aipo rating data
    "fetch_rating_list",
    "fetch_rating_detail",
    "get_rating_by_code",
    "format_rating_table",
    # aipo grey market data
    "fetch_grey_list",
    "fetch_allotment_results",
    "fetch_today_grey_market",
    "fetch_grey_trade_details",
    "fetch_grey_price_distribution",
    "fetch_grey_price_distribution_detail",
    "fetch_grey_placing_detail",
    "fetch_market_scroll_messages",
    # aipo ipo detail
    "fetch_ipo_brief",
    "fetch_cornerstone_investors",
    "fetch_placing_result",
    "fetch_company_managers",
    "fetch_sponsor_history",
    # aipo statistics (年度统计)
    "fetch_ipo_summary",
    "fetch_ipo_performance_by_year",
    "fetch_ipo_by_registered_office",
    # aastocks data
    "aastocks_get_upcoming_ipos",
    "aastocks_get_listed_ipos",
    "aastocks_get_ipo_detail",
    "aastocks_get_allotment_results",
    "aastocks_get_grey_market_schedule",
    "aastocks_get_sponsor_performance",
    # hkex (official)
    "HKEXIPO",
    "HKEXDocument",
    "fetch_hkex_active_ipos",
    "fetch_hkex_listed_ipos",
    "get_prospectus_url",
    "get_document_by_type",
    "fetch_hkex_active_ipos_sync",
    "fetch_hkex_listed_ipos_sync",
    # cache layer
    "get_cached",
    "set_cached",
    "get_or_fetch",
    "get_sponsors",
    "get_jisilu_history_cached",
    "get_active_ipos",
    "get_hkex_listed",
    "get_ipo_detail",
    "list_cache",
    "clear_expired",
    "clear_all",
    "get_cache_stats",
    "TTL_SHORT",
    "TTL_LONG",
    "TTL_PERMANENT",
]
