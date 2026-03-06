import sys
import os
import argparse

# Add local lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from korail2 import Korail

def main():
    KORAIL_ID = os.environ.get("KORAIL_ID", "0650620216")
    KORAIL_PW = os.environ.get("KORAIL_PW", "fly*2015")

    try:
        korail = Korail(KORAIL_ID, KORAIL_PW)
        reservations = korail.reservations()
        
        if not reservations:
            print("✅ 취소할 예약이 없습니다.")
            return

        for r in reservations:
            print(f"🔥 취소 시도: {r}")
            try:
                korail.cancel(r)
                print("✅ 취소 요청 완료")
            except Exception as e:
                # Patched korail2 might still raise error depending on version, but we ignore 'Extra data'
                if "Extra data" in str(e):
                    print("⚠️ 응답 해석 오류(무시)")
                else:
                    print(f"❌ 오류: {e}")

    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    main()
