import sys
import os
import argparse
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from SRT import SRT

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dep", required=True)
    parser.add_argument("--arr", required=True)
    parser.add_argument("--date", default=None)
    parser.add_argument("--time", default=None)
    args = parser.parse_args()

    SRT_ID = os.environ.get("SRT_ID")
    SRT_PW = os.environ.get("SRT_PW")

    if not SRT_ID or not SRT_PW:
        print("❌ 오류: SRT_ID, SRT_PW 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    try:
        srt = SRT(SRT_ID, SRT_PW)
        trains = srt.search_train(args.dep, args.arr, args.date, args.time)
        for t in trains:
            print(t)
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    main()
