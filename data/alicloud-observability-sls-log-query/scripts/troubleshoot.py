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
    parser = argparse.ArgumentParser(description="SLS troubleshooting query helper")
    parser.add_argument("--project", default=os.getenv("SLS_PROJECT"))
    parser.add_argument("--logstore", default=os.getenv("SLS_LOGSTORE"))
    parser.add_argument("--endpoint", default=os.getenv("SLS_ENDPOINT"))
    parser.add_argument("--start", type=int, default=None, help="epoch seconds")
    parser.add_argument("--end", type=int, default=None, help="epoch seconds")
    parser.add_argument("--last-minutes", type=int, default=30)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--group-field", default="status")
    parser.add_argument("--error-query", default="status:5* or level:error or level:ERROR")
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

    query = (
        f"{args.error_query} | "
        f"SELECT {args.group_field} AS key, count(*) AS total "
        f"GROUP BY {args.group_field} "
        f"ORDER BY total DESC LIMIT {args.limit}"
    )

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
        query=query,
        line=args.limit,
    )

    response = client.get_logs(request)
    for log in response.get_logs():
        print(log.contents)


if __name__ == "__main__":
    main()
