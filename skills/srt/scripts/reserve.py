#!/usr/bin/env python3
"""
Reservation-related tools for SRT skill.
Covers one-shot reserve, retry monitoring, list, cancel, and log inspection.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

from utils import (
    load_credentials,
    handle_error,
    output_json,
    format_reservation_info,
    print_table,
    get_data_dir,
    validate_safe_path,
    RateLimiter,
)
from train import fetch_trains_from_cache


# ── Retry Logger ──────────────────────────────────────────────────────────────

class RetryLogger:
    """Log retry progress to file and stdout."""

    def __init__(self, log_file=None):
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = get_data_dir() / f'reserve_{timestamp}.log'
        self.log_file = validate_safe_path(Path(log_file))
        self.log_file.touch(exist_ok=True)
        os.chmod(self.log_file, 0o600)
        print(f"LOG_FILE: {self.log_file}", flush=True)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {level}: {message}"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry + "\n")
        print(entry, flush=True)

    def log_json(self, data):
        self.log(f"JSON OUTPUT:\n{json.dumps(data, ensure_ascii=False, indent=2)}")


# ── reserve one-shot / retry ──────────────────────────────────────────────────

def _attempt_reservation(credentials, train, logger=None):
    """Attempt to reserve a specific train. Returns reservation or None."""
    from SRT import SRT
    try:
        msg = f"🎫 예약 시도 중... (열차 {train.train_number}, {train.dep_time})"
        (logger.log(msg) if logger else print(msg))
        srt = SRT(credentials['phone'], credentials['password'])
        return srt.reserve(train)
    except Exception as e:
        error_msg = str(e)
        if "잔여석없음" in error_msg or "매진" in error_msg:
            msg = f"❌ 좌석 없음 (열차 {train.train_number})"
            (logger.log(msg, "WARN") if logger else print(msg))
        else:
            msg = f"❌ 예약 실패: {error_msg}"
            (logger.log(msg, "ERROR") if logger else print(msg))
        return None


def _display_reservation_success(reservation, logger=None, attempts=1):
    """Print and log a successful reservation."""
    msgs = [
        "✅ 예약 성공!",
        f"예약번호: {getattr(reservation, 'reservation_number', 'N/A')}",
        f"열차번호: {getattr(reservation, 'train_number', 'N/A')}",
        f"좌석: {getattr(reservation, 'seat_number', 'N/A')}",
        "⚠️  결제는 SRT 앱 또는 웹사이트에서 완료해주세요!",
    ]
    for msg in msgs:
        (logger.log(msg, "SUCCESS") if logger else print(msg))

    info = format_reservation_info(reservation)
    info.update({"success": True, "payment_required": True, "attempts": attempts})
    (logger.log_json(info) if logger else output_json(info, success=True))


def run_one_shot(args):
    """Single reservation attempt."""
    try:
        credentials = load_credentials()
        all_trains = fetch_trains_from_cache(credentials)
        if not all_trains:
            print("❌ 검색 결과를 찾을 수 없습니다. 먼저 'train search' 명령으로 열차를 검색해주세요.",
                  file=sys.stderr)
            sys.exit(2)

        if args.train_id:
            train_ids = [int(t.strip()) for t in args.train_id.split(',')]
            trains = []
            for tid in train_ids:
                idx = tid - 1
                if idx < 0 or idx >= len(all_trains):
                    print(f"❌ 잘못된 열차 번호: {tid}", file=sys.stderr)
                    sys.exit(2)
                trains.append(all_trains[idx])
        else:
            trains = all_trains

        limiter = RateLimiter()
        for train in trains:
            can_reserve, wait_time = limiter.check_reserve_rate()
            if not can_reserve:
                time.sleep(wait_time)
            reservation = _attempt_reservation(credentials, train)
            limiter.record_reserve()
            if reservation:
                _display_reservation_success(reservation)
                sys.exit(0)

        error_info = handle_error(Exception("좌석 없음"), context="reserve one-shot")
        output_json(error_info, success=False)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        output_json(handle_error(e, context="reserve one-shot"), success=False)
        sys.exit(2)


def run_retry(args):
    """Continuous retry until success or timeout."""
    try:
        credentials = load_credentials()
        all_trains = fetch_trains_from_cache(credentials)
        if not all_trains:
            print("❌ 검색 결과를 찾을 수 없습니다. 먼저 'train search' 명령으로 열차를 검색해주세요.",
                  file=sys.stderr)
            sys.exit(2)

        if args.train_id:
            train_ids = [int(t.strip()) for t in args.train_id.split(',')]
            trains = []
            for tid in train_ids:
                idx = tid - 1
                if idx < 0 or idx >= len(all_trains):
                    print(f"❌ 잘못된 열차 번호: {tid}", file=sys.stderr)
                    sys.exit(2)
                trains.append(all_trains[idx])
        else:
            trains = all_trains

        limiter = RateLimiter()
        logger = RetryLogger(log_file=getattr(args, 'log_file', None))

        first = trains[0]
        logger.log("=" * 60)
        logger.log("SRT 예약 재시도 시작")
        logger.log("=" * 60)
        logger.log(f"출발역: {first.dep_station_name}")
        logger.log(f"도착역: {first.arr_station_name}")
        logger.log(f"타임아웃: {args.timeout_minutes}분")
        logger.log(f"재시도 간격: {args.wait_seconds}초")
        logger.log(f"대상 열차: {args.train_id or '전체'} (총 {len(trains)}개)")
        logger.log(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.log("=" * 60)

        start_time = time.time()
        timeout_seconds = args.timeout_minutes * 60
        attempt = 0
        train_index = 0

        while True:
            attempt += 1
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                logger.log(f"⏰ 타임아웃 ({args.timeout_minutes}분 경과)", "ERROR")
                logger.log(f"===== 최종결과: TIMEOUT (총 {attempt - 1}회 시도) =====", "ERROR")
                logger.log_json({"success": False, "error": "Timeout",
                                 "attempts": attempt - 1})
                sys.exit(1)

            if train_index >= len(trains):
                logger.log("모든 열차 시도 완료. 처음부터 다시 시작합니다.")
                train_index = 0

            train = trains[train_index]
            logger.log(f"\n=== 시도 #{attempt} (열차 {train_index + 1}/{len(trains)}) ===")
            logger.log(f"열차: {train.train_number} ({train.dep_time} → {train.arr_time})")

            can_reserve, wait_time = limiter.check_reserve_rate()
            if not can_reserve:
                logger.log(f"⏳ Rate limit 대기 중... ({int(wait_time)}초)")
                time.sleep(wait_time)

            reservation = _attempt_reservation(credentials, train, logger)
            limiter.record_reserve()

            if reservation:
                _display_reservation_success(reservation, logger, attempt)
                logger.log(f"===== 최종결과: SUCCESS (총 {attempt}회 시도) =====", "SUCCESS")
                sys.exit(0)

            train_index += 1

            if attempt % 10 == 0:
                elapsed_min = int(elapsed / 60)
                logger.log("=" * 60)
                logger.log(f"📊 진행 상황 요약 (시도 #{attempt})")
                logger.log(f"경과 시간: {elapsed_min}분 / 남은 시간: {args.timeout_minutes - elapsed_min}분")
                logger.log("=" * 60)

            logger.log(f"⏳ {args.wait_seconds}초 대기 후 재시도...")
            time.sleep(args.wait_seconds)

    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}", file=sys.stderr)
        sys.exit(2)


# ── reserve list ──────────────────────────────────────────────────────────────

def run_list(args):
    """List all current reservations."""
    try:
        from SRT import SRT
        credentials = load_credentials()
        print("📋 예약 조회 중...")
        srt = SRT(credentials['phone'], credentials['password'])
        reservations = srt.get_reservations()

        if not reservations:
            print("\n📭 현재 예약이 없습니다.")
            output_json([], success=True)
            sys.exit(0)

        print(f"\n✅ {len(reservations)}개의 예약을 찾았습니다.\n")
        fmt = getattr(args, 'format', 'table')

        if fmt == 'table':
            headers = ["예약번호", "날짜", "시간", "출발", "도착", "열차", "좌석", "결제"]
            rows = []
            for res in reservations:
                rows.append([
                    getattr(res, 'reservation_number', 'N/A'),
                    getattr(res, 'journey_date', 'N/A'),
                    getattr(res, 'journey_time', 'N/A'),
                    getattr(res, 'dep_station_name', 'N/A'),
                    getattr(res, 'arr_station_name', 'N/A'),
                    getattr(res, 'train_number', 'N/A'),
                    getattr(res, 'seat_number', 'N/A'),
                    "필요" if getattr(res, 'payment_required', True) else "완료",
                ])
            print_table(headers, rows)
            unpaid = [r for r in reservations if getattr(r, 'payment_required', True)]
            if unpaid:
                print(f"\n⚠️  결제가 필요한 예약이 {len(unpaid)}개 있습니다.")
                print("   SRT 앱 또는 웹사이트에서 결제를 완료해주세요.")

        output_json([format_reservation_info(r) for r in reservations], success=True)
        sys.exit(0)

    except Exception as e:
        output_json(handle_error(e, context="list"), success=False)
        sys.exit(2)


# ── reserve cancel ────────────────────────────────────────────────────────────

def run_cancel(args):
    """Cancel a reservation by ID."""
    try:
        from SRT import SRT
        credentials = load_credentials()
        print("🔍 예약 조회 중...")
        srt = SRT(credentials['phone'], credentials['password'])
        reservations = srt.get_reservations()

        if not reservations:
            raise Exception("예약을 찾을 수 없습니다.")

        reservation = next(
            (r for r in reservations
             if getattr(r, 'reservation_number', '') == args.reservation_id),
            None
        )
        if not reservation:
            raise Exception(
                f"예약번호 '{args.reservation_id}'를 찾을 수 없습니다.\n"
                "예약 목록 확인: srt_cli.py reserve list"
            )

        if not getattr(args, 'confirm', False):
            print("\n⚠️  예약을 취소하시겠습니까?")
            print(f"   예약번호: {getattr(reservation, 'reservation_number', 'N/A')}")
            print(f"   열차번호: {getattr(reservation, 'train_number', 'N/A')}")
            print(f"   출발: {getattr(reservation, 'dep_station_name', 'N/A')} "
                  f"{getattr(reservation, 'journey_time', 'N/A')}")
            if input("\n계속하려면 'yes' 입력: ").lower() not in ['yes', 'y']:
                print("취소가 중단되었습니다.")
                sys.exit(0)

        print("\n🗑️  예약 취소 중...")
        srt.cancel(reservation)
        print("\n✅ 예약이 취소되었습니다.")
        print(f"   예약번호: {getattr(reservation, 'reservation_number', 'N/A')}")

        output_json({
            "success": True,
            "reservation_id": getattr(reservation, 'reservation_number', 'N/A'),
            "message": "Reservation cancelled successfully",
        }, success=True)
        sys.exit(0)

    except Exception as e:
        output_json(handle_error(e, context="cancel"), success=False)
        sys.exit(2)


# ── reserve status ───────────────────────────────────────────────────────────

def run_status(args):
    """Check whether the background retry process is alive."""
    pid_file = validate_safe_path(Path(args.pid_file))
    if not pid_file.exists():
        print("NOT_RUNNING (PID 파일 없음)")
        sys.exit(0)
    raw = pid_file.read_text().strip()
    if not raw.isdigit():
        print(f"ERROR: PID 파일 내용이 유효하지 않습니다: {raw!r}")
        sys.exit(1)
    pid = int(raw)
    try:
        os.kill(pid, 0)
        print(f"RUNNING ({pid})")
    except ProcessLookupError:
        print(f"NOT_RUNNING (PID {pid} 종료됨)")
    except PermissionError:
        print(f"RUNNING ({pid}, 권한 없음으로 신호 전송 불가)")


# ── reserve stop ──────────────────────────────────────────────────────────────

def run_stop(args):
    """Send SIGTERM to the background retry process."""
    import signal
    pid_file = validate_safe_path(Path(args.pid_file))
    if not pid_file.exists():
        print(f"❌ PID 파일이 없습니다: {pid_file}")
        sys.exit(1)
    raw = pid_file.read_text().strip()
    if not raw.isdigit():
        print(f"❌ PID 파일 내용이 유효하지 않습니다: {raw!r}")
        sys.exit(1)
    pid = int(raw)
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"✅ 프로세스 {pid} 종료 요청 완료")
    except ProcessLookupError:
        print(f"⚠️  프로세스 {pid}는 이미 종료되어 있습니다")
    except PermissionError:
        print(f"❌ 프로세스 {pid} 종료 권한 없음")
        sys.exit(1)


# ── reserve log ───────────────────────────────────────────────────────────────

def run_log(args):
    """Tail the latest retry log file."""
    log_dir = get_data_dir()
    candidates = sorted(log_dir.glob('reserve_*.log'),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        print(f"❌ 로그 파일이 없습니다. ({log_dir}/reserve_*.log)")
        sys.exit(1)

    log_file = candidates[0]
    print(f"📄 로그 파일: {log_file}")

    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    tail = all_lines[-args.lines:]
    print("".join(tail))
    print(f"\n--- 총 {len(all_lines)}줄 중 마지막 {len(tail)}줄 표시 ---")
