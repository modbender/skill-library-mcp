#!/usr/bin/env python3
"""
Train-related tools for SRT skill.
Covers search and any future train query operations.
"""

import sys
import argparse
from utils import (
    load_credentials,
    handle_error,
    output_json,
    format_train_info,
    print_table,
    save_search_results,
    load_search_cache,
    RateLimiter,
    wait_with_message
)


def fetch_trains_from_cache(credentials=None):
    """
    Re-hydrate cached search results as live SRT train objects.
    Loads cached search params, delegates actual search to search_trains(),
    then filters results to the originally cached train numbers.

    Args:
        credentials: dict with phone and password (loaded automatically if None)

    Returns:
        list: Live SRT train objects, or None if cache is missing / search fails.
    """
    cache = load_search_cache()
    if not cache:
        print("❌ 캐시에 검색 정보가 없습니다. 먼저 'train search' 명령으로 열차를 검색해주세요.",
              file=sys.stderr)
        return None

    params = cache.get('search_params', {})
    cached_numbers = [t['train_number'] for t in cache.get('trains', [])]

    if not params.get('departure') or not params.get('arrival') or not params.get('date'):
        print("❌ 캐시에 검색 파라미터가 없습니다. 다시 'train search'를 실행해주세요.",
              file=sys.stderr)
        return None

    if credentials is None:
        credentials = load_credentials()

    # Build a minimal args namespace so search_trains() can be reused as-is
    search_args = argparse.Namespace(
        departure=params['departure'],
        arrival=params['arrival'],
        date=params['date'],
        time=params.get('time', '000000'),
        passengers=None,
    )

    try:
        trains = search_trains(credentials, search_args)
        if cached_numbers:
            train_map = {t.train_number: t for t in trains}
            filtered = [train_map[n] for n in cached_numbers if n in train_map]
            return filtered if filtered else trains
        return trains
    except Exception as e:
        print(f"⚠️  Warning: Re-search failed: {e}", file=sys.stderr)
        return None


def search_trains(credentials, args):
    """
    Search for available trains.

    Args:
        credentials: dict with phone and password
        args: argparse namespace with search parameters

    Returns:
        list: List of available trains
    """
    from SRT import SRT

    # Rate limiting
    limiter = RateLimiter()
    can_search, wait_time = limiter.check_search_rate()
    if not can_search:
        wait_with_message(wait_time, "SRT 서버 보호를 위해 대기 중")

    # Login
    print(f"🔍 열차 검색 중... ({args.departure} → {args.arrival})")
    srt = SRT(credentials['phone'], credentials['password'])

    # Search trains (include sold-out trains)
    trains = srt.search_train(
        dep=args.departure,
        arr=args.arrival,
        date=args.date,
        time=args.time,
        available_only=False
    )

    # Record search
    limiter.record_search()

    if not trains:
        raise Exception("검색 결과가 없습니다. 날짜, 시간, 역 이름을 확인해주세요.")

    return trains


def _display_results(trains):
    """Display search results in table and JSON format."""
    print(f"\n✅ {len(trains)}개의 열차를 찾았습니다.\n")

    # Table format
    headers = ["번호", "열차", "출발", "도착", "일반석", "특실"]
    rows = []
    for i, train in enumerate(trains, 1):
        general_seat = getattr(train, 'general_seat_state', 'N/A')
        special_seat = getattr(train, 'special_seat_state', 'N/A')
        rows.append([
            i,
            train.train_number,
            train.dep_time,
            train.arr_time,
            general_seat,
            special_seat
        ])

    print_table(headers, rows)

    # JSON output for AI
    json_data = []
    for i, train in enumerate(trains, 1):
        info = format_train_info(train)
        info['train_id'] = str(i)  # Add index for reservation
        json_data.append(info)

    output_json(json_data, success=True)

    print("\n💡 예약하려면: python3 scripts/srt_cli.py reserve --train-id <번호>")


def run(args):
    """Run search with pre-parsed args from srt_cli.py."""
    try:
        credentials = load_credentials()
        trains = search_trains(credentials, args)
        save_search_results(trains, args)
        _display_results(trains)
        sys.exit(0)
    except Exception as e:
        error_info = handle_error(e, context="search")
        output_json(error_info, success=False)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="SRT 열차 검색")
    parser.add_argument('--departure', required=True, help="출발역 (한글, 예: 수서)")
    parser.add_argument('--arrival', required=True, help="도착역 (한글, 예: 부산)")
    parser.add_argument('--date', required=True, help="날짜 (YYYYMMDD, 예: 20260217)")
    parser.add_argument('--time', required=True, help="시간 (HHMMSS, 예: 140000)")
    parser.add_argument('--passengers', help="승객 수 (예: adult=2, default=1)")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
