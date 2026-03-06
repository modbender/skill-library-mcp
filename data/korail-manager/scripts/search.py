import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
# The .env file should be in the skill's root directory (e.g., skills/korail-manager/.env)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

# Add local lib to path to use patched korail2
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from korail2 import Korail

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dep", required=True)
    parser.add_argument("--arr", required=True)
    parser.add_argument("--date", default=None)
    parser.add_argument("--time", default=None)
    args = parser.parse_args()

    # Load credentials from environment variables
    KORAIL_ID = os.environ.get("KORAIL_ID")
    KORAIL_PW = os.environ.get("KORAIL_PW")

    if not KORAIL_ID or not KORAIL_PW:
        print("❌ 오류: KORAIL_ID, KORAIL_PW 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    try:
        korail = Korail(KORAIL_ID, KORAIL_PW)
        trains = korail.search_train(args.dep, args.arr, args.date, args.time)
        for t in trains:
            print(t)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
