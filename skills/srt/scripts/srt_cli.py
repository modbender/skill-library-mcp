#!/usr/bin/env python3
"""
Main CLI router for SRT skill.
Routes commands to appropriate tool modules.
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="SRT (Korean Train Service) CLI",
        epilog=(
            "예시:\n"
            "  열차 검색:    python3 scripts/srt_cli.py train search --departure 수서 --arrival 부산 --date 20260217 --time 140000\n"
            "  단일 예약:    python3 scripts/srt_cli.py reserve one-shot --train-id 1\n"
            "  반복 예약:    python3 scripts/srt_cli.py reserve retry --train-id 1 --timeout-minutes 1440\n"
            "  예약 상태:    python3 scripts/srt_cli.py reserve status --pid-file /tmp/srt/job.pid\n"
            "  예약 중단:    python3 scripts/srt_cli.py reserve stop --pid-file /tmp/srt/job.pid\n"
            "  예약 로그:    python3 scripts/srt_cli.py reserve log -n 30\n"
            "  예약 목록:    python3 scripts/srt_cli.py reserve list\n"
            "  예약 취소:    python3 scripts/srt_cli.py reserve cancel --reservation-id RES123"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령')

    # ── train ─────────────────────────────────────────────────────────────────
    train_parser = subparsers.add_parser('train', help='열차 조회 관련 명령')
    train_sub = train_parser.add_subparsers(dest='train_command', help='열차 서브 명령')

    # train search
    search_p = train_sub.add_parser('search', help='열차 검색')
    search_p.add_argument('--departure', required=True, help='출발역 (한글)')
    search_p.add_argument('--arrival',   required=True, help='도착역 (한글)')
    search_p.add_argument('--date',      required=True, help='날짜 (YYYYMMDD)')
    search_p.add_argument('--time',      required=True, help='시간 (HHMMSS)')
    search_p.add_argument('--passengers', help='승객 수 (예: adult=2)')

    # ── reserve ───────────────────────────────────────────────────────────────
    reserve_parser = subparsers.add_parser('reserve', help='열차 예약 관련 명령')
    reserve_sub = reserve_parser.add_subparsers(dest='reserve_command', help='예약 서브 명령')

    # reserve one-shot
    one_shot = reserve_sub.add_parser('one-shot', help='단일 예약 시도 (1회)')
    one_shot.add_argument('--train-id',
                          help='열차 번호 (검색 결과 순번, 쉼표로 복수 지정, 생략 시 전체 시도)')

    # reserve retry
    retry_p = reserve_sub.add_parser('retry', help='취소표 반복 시도 (백그라운드 실행 권장)')
    retry_p.add_argument('--train-id',
                         help='열차 번호 (검색 결과 순번, 쉼표로 복수 지정, 생략 시 전체 시도)')
    retry_p.add_argument('--timeout-minutes', type=int, default=60,
                         help='최대 시도 시간 (분, 기본값: 60)')
    retry_p.add_argument('--wait-seconds', type=int, default=10,
                         help='재시도 대기 시간 (초, 기본값: 10)')
    retry_p.add_argument('--log-file', type=str, default=None,
                         help='로그 파일 경로 (기본값: SRT_DATA_DIR 하위 자동 생성)')

    # reserve status
    status_p = reserve_sub.add_parser('status', help='백그라운드 반복 예약 프로세스 상태 확인')
    status_p.add_argument('--pid-file', required=True, help='PID 파일 경로')

    # reserve stop
    stop_p = reserve_sub.add_parser('stop', help='백그라운드 반복 예약 프로세스 종료')
    stop_p.add_argument('--pid-file', required=True, help='PID 파일 경로')

    # reserve log
    log_p = reserve_sub.add_parser('log', help='반복 예약 로그 확인')
    log_p.add_argument('--lines', '-n', type=int, default=20,
                       help='표시할 라인 수 (기본값: 20)')

    # reserve list
    list_p = reserve_sub.add_parser('list', help='예약 목록 조회')
    list_p.add_argument('--format', choices=['table', 'json'], default='table',
                        help='출력 형식')

    # reserve cancel
    cancel_p = reserve_sub.add_parser('cancel', help='예약 취소')
    cancel_p.add_argument('--reservation-id', required=True, help='예약번호')
    cancel_p.add_argument('--confirm', action='store_true', help='확인 없이 바로 취소')

    # ─────────────────────────────────────────────────────────────────────────
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # ── train ──────────────────────────────────────────────────────────
        if args.command == 'train':
            if not args.train_command:
                train_parser.print_help()
                sys.exit(1)

            if args.train_command == 'search':
                from train import run
                run(args)

        # ── reserve ────────────────────────────────────────────────────────
        elif args.command == 'reserve':
            if not args.reserve_command:
                reserve_parser.print_help()
                sys.exit(1)

            if args.reserve_command == 'one-shot':
                from reserve import run_one_shot
                run_one_shot(args)

            elif args.reserve_command == 'retry':
                from reserve import run_retry
                run_retry(args)

            elif args.reserve_command == 'status':
                from reserve import run_status
                run_status(args)

            elif args.reserve_command == 'stop':
                from reserve import run_stop
                run_stop(args)

            elif args.reserve_command == 'log':
                from reserve import run_log
                run_log(args)

            elif args.reserve_command == 'list':
                from reserve import run_list
                run_list(args)

            elif args.reserve_command == 'cancel':
                from reserve import run_cancel
                run_cancel(args)

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
