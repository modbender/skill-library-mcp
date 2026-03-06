"""Calendar view - group IPOs by deadline for funding planning."""

import json


def fetch_calendar() -> dict:
    """Group upcoming IPOs by deadline date.

    Returns: {"rounds": [{"deadline": "...", "settle_date": "...", "ipos": [...]}]}
    """
    from aipo import fetch_margin_list, fetch_ipo_brief
    
    ipos = fetch_margin_list()
    
    # 按截止日期分组
    by_deadline = {}
    for ipo in ipos:
        code = ipo.get("code", "")
        # 获取详细信息
        brief = fetch_ipo_brief(code) or {}
        deadline = brief.get("apply_end", ipo.get("listing_date", ""))[:10]
        listing = brief.get("listing_date", ipo.get("listing_date", ""))[:10]
        
        if deadline not in by_deadline:
            by_deadline[deadline] = {
                "deadline": deadline,
                "listing_date": listing,
                "ipos": []
            }
        
        by_deadline[deadline]["ipos"].append({
            "code": code,
            "name": ipo.get("name", ""),
            "entry_fee": brief.get("minimum_capital", 0),
            "total_margin": ipo.get("total_margin", 0),
            "listing_date": listing,
        })
    
    # 按日期排序
    rounds = sorted(by_deadline.values(), key=lambda x: x["deadline"])
    
    return {"rounds": rounds}


if __name__ == "__main__":
    result = fetch_calendar()
    print(json.dumps(result, indent=2, ensure_ascii=False))
