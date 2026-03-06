import sys
import os
import argparse
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from SRT import SRT

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="취소 대상 날짜 (YYYYMMDD). 미지정 시 전체 취소.")
    args = parser.parse_args()

    SRT_ID = os.environ.get("SRT_ID")
    SRT_PW = os.environ.get("SRT_PW")

    if not SRT_ID or not SRT_PW:
        print("❌ 오류: SRT_ID, SRT_PW 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    try:
        srt = SRT(SRT_ID, SRT_PW)
        reservations = srt.get_reservations()

        if not reservations:
            print("✅ 취소할 예약이 없습니다.")
            return

        for r in reservations:
            if args.date and hasattr(r, 'dep_date') and r.dep_date != args.date:
                print(f"⏩ 건너뜀 (날짜 불일치): {r}")
                continue
            print(f"🔥 취소 시도: {r}")
            try:
                srt.cancel(r)
                print("✅ 취소 완료")
            except Exception as e:
                print(f"❌ 취소 실패: {e}")

    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    main()
