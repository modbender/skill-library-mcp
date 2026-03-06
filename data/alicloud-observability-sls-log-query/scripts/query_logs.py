import argparse
import os
import sys
import time

from aliyun.log import LogClient, GetLogsRequest


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        print(f"Missing env var: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SLS log query")
    parser.add_argument("--query", default="*")
    parser.add_argument("--project", default=os.getenv("SLS_PROJECT"))
    parser.add_argument("--logstore", default=os.getenv("SLS_LOGSTORE"))
    parser.add_argument("--endpoint", default=os.getenv("SLS_ENDPOINT"))
    parser.add_argument("--start", type=int, default=None, help="epoch seconds")
    parser.add_argument("--end", type=int, default=None, help="epoch seconds")
    parser.add_argument("--last-minutes", type=int, default=15)
    parser.add_argument("--limit", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project = args.project or get_env("SLS_PROJECT")
    logstore = args.logstore or get_env("SLS_LOGSTORE")
    endpoint = args.endpoint or get_env("SLS_ENDPOINT")

    start_time = args.start
    end_time = args.end
    if end_time is None:
        end_time = int(time.time())
    if start_time is None:
        start_time = end_time - args.last_minutes * 60

    client = LogClient(
        endpoint,
        get_env("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        get_env("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
    )

    request = GetLogsRequest(
        project,
        logstore,
        start_time,
        end_time,
        query=args.query,
        line=args.limit,
    )

    response = client.get_logs(request)
    for log in response.get_logs():
        print(log.contents)


if __name__ == "__main__":
    main()
