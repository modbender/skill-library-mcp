#!/usr/bin/env python3
"""매수/매도 주문 (확인 필수)"""
from typing import Optional, Dict
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from kis_common import load_config, get_token, api_post, api_get, fmt_price, fmt_num, add_common_args, get_stock_name_from_api, resolve_tr_id


def get_stock_name(cfg: dict, token: str, code: str) -> str:
    """종목명 조회"""
    return get_stock_name_from_api(cfg, token, code)


def round_to_tick(price: int) -> int:
    """KRX 호가단위로 반올림"""
    if price < 1000: tick = 1
    elif price < 5000: tick = 5
    elif price < 10000: tick = 10
    elif price < 50000: tick = 50
    elif price < 100000: tick = 100
    elif price < 500000: tick = 500
    else: tick = 1000
    return int(round(price / tick) * tick)


def place_order(cfg: dict, token: str, side: str, code: str, qty: int,
                price: int = 0, market: bool = False) -> Optional[dict]:
    """주문 실행"""
    # TR ID는 api_post에서 resolve_tr_id로 자동 변환
    tr_id = "TTTC0012U" if side == 'buy' else "TTTC0011U"

    ord_dvsn = "01" if market else "00"  # 01:시장가, 00:지정가

    if not market and price > 0:
        price = round_to_tick(price)

    body = {
        "CANO": cfg['account_no'],
        "ACNT_PRDT_CD": cfg['product_code'],
        "PDNO": code,
        "ORD_DVSN": ord_dvsn,
        "ORD_QTY": str(qty),
        "ORD_UNPR": str(price if not market else 0),
    }

    return api_post(cfg, token, '/uapi/domestic-stock/v1/trading/order-cash', tr_id, body)


def main():
    parser = argparse.ArgumentParser(description='매수/매도 주문')
    add_common_args(parser)
    parser.add_argument('--side', required=True, choices=['buy', 'sell'], help='매수(buy) 또는 매도(sell)')
    parser.add_argument('--code', required=True, help='종목코드 (6자리)')
    parser.add_argument('--qty', required=True, type=int, help='주문 수량')
    parser.add_argument('--price', type=int, default=0, help='주문 가격 (지정가)')
    parser.add_argument('--market', action='store_true', help='시장가 주문')
    parser.add_argument('--dry-run', action='store_true', help='주문 내용만 확인 (실제 주문 안함)')
    args = parser.parse_args()

    if args.qty <= 0:
        print("❌ 주문 수량은 1 이상이어야 합니다.")
        sys.exit(1)

    if not args.market and args.price <= 0:
        print("❌ 지정가 주문 시 --price를 입력하거나, --market으로 시장가 주문하세요.")
        sys.exit(1)

    cfg = load_config(args.config)
    token = get_token(cfg)

    # 종목명 조회
    name = get_stock_name(cfg, token, args.code)
    side_str = '매수' if args.side == 'buy' else '매도'
    price_str = '시장가' if args.market else fmt_price(round_to_tick(args.price))

    print(f"📋 주문 확인")
    print(f"  {'🟢 매수' if args.side == 'buy' else '🔴 매도'}: {name} ({args.code})")
    print(f"  수량: {fmt_num(args.qty)}주")
    print(f"  가격: {price_str}")

    if args.dry_run:
        print(f"\n✅ 드라이런 완료 (실제 주문되지 않음)")
        return

    print(f"\n⚠️  위 내용으로 {side_str} 주문을 실행합니다.")

    result = place_order(cfg, token, args.side, args.code, args.qty, args.price, args.market)

    if result:
        out = result.get('output', {})
        order_no = out.get('ODNO', out.get('odno', ''))
        print(f"\n✅ {side_str} 주문 완료!")
        print(f"  주문번호: {order_no}")
        print(f"  주문시각: {out.get('ORD_TMD', out.get('ord_tmd', ''))}")
    else:
        print(f"\n❌ {side_str} 주문 실패")
        sys.exit(1)


if __name__ == '__main__':
    main()
