#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


BASE_URL = "https://boosta.pro/api/v1"


class BoostaClient:
    def __init__(self, api_key, timeout=60):
        self.api_key = api_key
        self.timeout = timeout

    def _request(self, method, path, payload=None):
        body = None
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url=f"{BASE_URL}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = resp.read().decode("utf-8")
                return resp.getcode(), _safe_json(data)
        except urllib.error.HTTPError as exc:
            data = exc.read().decode("utf-8") if exc.fp else ""
            return exc.code, _safe_json(data)
        except urllib.error.URLError as exc:
            return 0, {"error": f"network_error: {exc}"}

    def submit_job(self, video_url, video_type, config_name=None):
        payload = {"video_url": video_url, "video_type": video_type}
        if config_name:
            payload["config_name"] = config_name
        return self._request("POST", "/jobs", payload)

    def get_job(self, job_id):
        return self._request("GET", f"/jobs/{job_id}")

    def list_jobs(self):
        return self._request("GET", "/jobs")

    def get_usage(self):
        return self._request("GET", "/usage")


def _safe_json(raw):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _require_api_key():
    api_key = os.getenv("BOOSTA_API_KEY")
    if not api_key:
        print(
            "Missing BOOSTA_API_KEY environment variable.",
            file=sys.stderr,
        )
        sys.exit(2)
    return api_key


def _print_result(status_code, payload):
    out = {"status_code": status_code, "data": payload}
    print(json.dumps(out, indent=2, ensure_ascii=True))


def _poll_until_done(client, job_id, interval, max_wait):
    deadline = time.time() + max_wait if max_wait > 0 else None
    while True:
        status_code, payload = client.get_job(job_id)
        if status_code >= 400:
            if status_code == 429:
                retry_after = int(payload.get("retry_after", 60))
                print(
                    json.dumps(
                        {
                            "info": "rate_limited_during_poll",
                            "retry_after": retry_after,
                            "job_id": job_id,
                        },
                        ensure_ascii=True,
                    )
                )
                time.sleep(retry_after)
                continue
            return status_code, payload

        job_status = payload.get("status")
        if job_status in {"completed", "failed"}:
            return status_code, payload

        print(
            json.dumps(
                {
                    "job_id": job_id,
                    "status": job_status,
                    "progress": payload.get("progress"),
                    "step": payload.get("step"),
                },
                ensure_ascii=True,
            )
        )

        if deadline is not None and time.time() >= deadline:
            return 408, {"error": "poll_timeout", "job_id": job_id}
        time.sleep(interval)


def cmd_submit(args):
    client = BoostaClient(_require_api_key(), timeout=args.timeout)
    status_code, payload = client.submit_job(
        video_url=args.video_url,
        video_type=args.video_type,
        config_name=args.config_name,
    )

    if status_code >= 400 and payload.get("status") == "active_job_exists":
        job_id = payload.get("job_id")
        if args.wait and job_id:
            print(
                json.dumps(
                    {"info": "active_job_exists", "job_id": job_id},
                    ensure_ascii=True,
                )
            )
            poll_code, poll_payload = _poll_until_done(
                client, job_id, args.poll_interval, args.max_wait
            )
            _print_result(poll_code, poll_payload)
            return 0 if poll_code < 400 else 1
        _print_result(status_code, payload)
        return 1

    if status_code >= 400:
        _print_result(status_code, payload)
        return 1

    if not args.wait:
        _print_result(status_code, payload)
        return 0

    job_id = payload.get("job_id")
    if not job_id:
        _print_result(500, {"error": "missing_job_id_in_response", "raw": payload})
        return 1

    poll_code, poll_payload = _poll_until_done(
        client, job_id, args.poll_interval, args.max_wait
    )
    _print_result(poll_code, poll_payload)
    return 0 if poll_code < 400 else 1


def cmd_status(args):
    client = BoostaClient(_require_api_key(), timeout=args.timeout)
    status_code, payload = client.get_job(args.job_id)
    _print_result(status_code, payload)
    return 0 if status_code < 400 else 1


def cmd_list(args):
    client = BoostaClient(_require_api_key(), timeout=args.timeout)
    status_code, payload = client.list_jobs()
    _print_result(status_code, payload)
    return 0 if status_code < 400 else 1


def cmd_usage(args):
    client = BoostaClient(_require_api_key(), timeout=args.timeout)
    status_code, payload = client.get_usage()
    _print_result(status_code, payload)
    return 0 if status_code < 400 else 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="Boosta API utility for submit/status/list/usage."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    submit = sub.add_parser("submit", help="Submit a new Boosta job.")
    submit.add_argument("--video-url", required=True, help="Source video URL.")
    submit.add_argument(
        "--video-type",
        required=True,
        choices=["conversation", "gaming", "faceless", "solo", "vlog", "movies"],
        help="Boosta video_type value.",
    )
    submit.add_argument("--config-name", help="Optional Boosta config name.")
    submit.add_argument(
        "--wait",
        action="store_true",
        help="Poll until job reaches completed or failed.",
    )
    submit.add_argument(
        "--poll-interval",
        type=int,
        default=15,
        help="Polling interval in seconds when --wait is used.",
    )
    submit.add_argument(
        "--max-wait",
        type=int,
        default=1800,
        help="Max wait in seconds for --wait (0 = no timeout).",
    )
    submit.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds.")
    submit.set_defaults(func=cmd_submit)

    status = sub.add_parser("status", help="Get job status.")
    status.add_argument("--job-id", required=True, help="Boosta job_id.")
    status.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds.")
    status.set_defaults(func=cmd_status)

    lst = sub.add_parser("list", help="List jobs.")
    lst.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds.")
    lst.set_defaults(func=cmd_list)

    usage = sub.add_parser("usage", help="Get usage/credits.")
    usage.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds.")
    usage.set_defaults(func=cmd_usage)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
