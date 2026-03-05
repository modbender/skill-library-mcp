"""
Powerdrill API Client

A Python client for the Powerdrill Data Analysis API v2.
All endpoints use the base URL: https://ai.data.cloud/api

Required environment variables:
  POWERDRILL_USER_ID        - Your Powerdrill user ID
  POWERDRILL_PROJECT_API_KEY - Your Powerdrill project API key
"""

import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://ai.data.cloud/api"

# Shared session with automatic retries on transient errors
_session = requests.Session()
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))


def _get_env():
    """Return (user_id, api_key) from environment, or exit with guidance."""
    user_id = os.environ.get("POWERDRILL_USER_ID", "")
    api_key = os.environ.get("POWERDRILL_PROJECT_API_KEY", "")
    if not user_id or not api_key:
        print(
            "Error: POWERDRILL_USER_ID and POWERDRILL_PROJECT_API_KEY must be set.\n"
            "Setup guide:\n"
            "  1. Create a Teamspace: https://www.youtube.com/watch?v=I-0yGD9HeDw\n"
            "  2. Get API credentials: https://www.youtube.com/watch?v=qs-GsUgjb1g",
            file=sys.stderr,
        )
        sys.exit(1)
    return user_id, api_key


def _headers(api_key: str) -> dict:
    return {
        "x-pd-api-key": api_key,
        "Content-Type": "application/json",
    }


def _check_response(resp: requests.Response) -> dict:
    """Raise on HTTP error, then check Powerdrill code field."""
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(
            f"Powerdrill API error (code={data.get('code')}): "
            f"{data.get('message', json.dumps(data))}"
        )
    return data


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------

def list_datasets(
    page_number: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
) -> dict:
    """GET /v2/team/datasets - List datasets."""
    user_id, api_key = _get_env()
    params = {"user_id": user_id, "page_number": page_number, "page_size": page_size}
    if search:
        params["search"] = search
    resp = _session.get(f"{BASE_URL}/v2/team/datasets", headers=_headers(api_key), params=params)
    return _check_response(resp)


def create_dataset(name: str, description: str = "") -> dict:
    """POST /v2/team/datasets - Create a new dataset."""
    user_id, api_key = _get_env()
    payload = {"name": name, "user_id": user_id}
    if description:
        payload["description"] = description
    resp = _session.post(f"{BASE_URL}/v2/team/datasets", headers=_headers(api_key), json=payload)
    return _check_response(resp)


def get_dataset_overview(dataset_id: str) -> dict:
    """GET /v2/team/datasets/{id}/overview - Get dataset overview."""
    user_id, api_key = _get_env()
    resp = _session.get(
        f"{BASE_URL}/v2/team/datasets/{dataset_id}/overview",
        headers=_headers(api_key),
        params={"user_id": user_id},
    )
    return _check_response(resp)


def get_dataset_status(dataset_id: str) -> dict:
    """GET /v2/team/datasets/{id}/status - Check data-source sync status."""
    user_id, api_key = _get_env()
    resp = _session.get(
        f"{BASE_URL}/v2/team/datasets/{dataset_id}/status",
        headers=_headers(api_key),
        params={"user_id": user_id},
    )
    return _check_response(resp)


def delete_dataset(dataset_id: str) -> dict:
    """DELETE /v2/team/datasets/{id} - Delete a dataset."""
    user_id, api_key = _get_env()
    resp = _session.delete(
        f"{BASE_URL}/v2/team/datasets/{dataset_id}",
        headers=_headers(api_key),
        json={"user_id": user_id},
    )
    return _check_response(resp)


# ---------------------------------------------------------------------------
# Data Sources
# ---------------------------------------------------------------------------

def list_data_sources(
    dataset_id: str,
    page_number: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
) -> dict:
    """GET /v2/team/datasets/{id}/datasources - List data sources in a dataset."""
    user_id, api_key = _get_env()
    params = {"user_id": user_id, "page_number": page_number, "page_size": page_size}
    if status:
        params["status"] = status
    resp = _session.get(
        f"{BASE_URL}/v2/team/datasets/{dataset_id}/datasources",
        headers=_headers(api_key),
        params=params,
    )
    return _check_response(resp)


def create_data_source(
    dataset_id: str,
    name: str,
    *,
    url: Optional[str] = None,
    file_object_key: Optional[str] = None,
) -> dict:
    """POST /v2/team/datasets/{id}/datasources - Create a data source.

    Provide either `url` (public file URL) or `file_object_key` (from upload).
    """
    user_id, api_key = _get_env()
    payload = {"name": name, "type": "FILE", "user_id": user_id}
    if url:
        payload["url"] = url
    elif file_object_key:
        payload["file_object_key"] = file_object_key
    else:
        raise ValueError("Either url or file_object_key must be provided")
    resp = _session.post(
        f"{BASE_URL}/v2/team/datasets/{dataset_id}/datasources",
        headers=_headers(api_key),
        json=payload,
    )
    return _check_response(resp)


# ---------------------------------------------------------------------------
# Local File Upload (multipart)
# ---------------------------------------------------------------------------

def _initiate_multipart_upload(file_name: str, file_size: int) -> dict:
    """POST /v2/team/file/init-multipart-upload"""
    user_id, api_key = _get_env()
    payload = {"file_name": file_name, "file_size": file_size, "user_id": user_id}
    resp = _session.post(
        f"{BASE_URL}/v2/team/file/init-multipart-upload",
        headers=_headers(api_key),
        json=payload,
    )
    return _check_response(resp)


def _complete_multipart_upload(
    file_object_key: str, upload_id: str, part_etags: list
) -> dict:
    """POST /v2/team/file/complete-multipart-upload"""
    user_id, api_key = _get_env()
    payload = {
        "file_object_key": file_object_key,
        "upload_id": upload_id,
        "part_etags": part_etags,
        "user_id": user_id,
    }
    resp = _session.post(
        f"{BASE_URL}/v2/team/file/complete-multipart-upload",
        headers=_headers(api_key),
        json=payload,
    )
    return _check_response(resp)


def upload_local_file(file_path: str) -> str:
    """Upload a local file via multipart upload.

    Returns the file_object_key to be used with create_data_source().
    """
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = p.stat().st_size
    file_name = p.name

    # Step 1: Initiate
    init = _initiate_multipart_upload(file_name, file_size)
    upload_id = init["data"]["upload_id"]
    file_object_key = init["data"]["file_object_key"]
    part_items = init["data"]["part_items"]

    # Step 2: Upload each part
    part_etags = []
    with open(p, "rb") as f:
        for part in part_items:
            chunk = f.read(part["size"])
            put_resp = requests.put(
                part["upload_url"],
                data=chunk,
                headers={"Content-Type": "application/octet-stream"},
            )
            put_resp.raise_for_status()
            etag = put_resp.headers.get("ETag", "").strip('"')
            part_etags.append({"number": part["number"], "etag": etag})

    # Step 3: Complete
    _complete_multipart_upload(file_object_key, upload_id, part_etags)
    return file_object_key


def upload_and_create_data_source(dataset_id: str, file_path: str) -> dict:
    """Upload a local file then create a data source in the given dataset.

    Returns the create_data_source response.
    """
    file_object_key = upload_local_file(file_path)
    file_name = Path(file_path).name
    return create_data_source(dataset_id, file_name, file_object_key=file_object_key)


# ---------------------------------------------------------------------------
# Wait for Data Sources to Sync
# ---------------------------------------------------------------------------

def wait_for_dataset_sync(
    dataset_id: str,
    max_attempts: int = 30,
    delay_seconds: float = 3.0,
) -> dict:
    """Poll dataset status until all data sources are synched.

    Returns the final status response.
    Raises RuntimeError on timeout or if invalid sources are detected.
    """
    for attempt in range(1, max_attempts + 1):
        status = get_dataset_status(dataset_id)
        d = status["data"]
        synched = d["synched_count"]
        invalid = d["invalid_count"]
        synching = d["synching_count"]

        if invalid > 0:
            raise RuntimeError(
                f"Dataset {dataset_id} has {invalid} invalid data source(s). "
                "Check file format and re-upload."
            )
        if synching == 0:
            print(f"All {synched} data source(s) synced.", file=sys.stderr)
            return status

        print(
            f"[{attempt}/{max_attempts}] {synching} source(s) still syncing, "
            f"{synched} synced. Waiting {delay_seconds}s...",
            file=sys.stderr,
        )
        time.sleep(delay_seconds)

    raise RuntimeError(
        f"Timed out after {max_attempts} attempts waiting for dataset {dataset_id} to sync."
    )


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def list_sessions(
    page_number: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
) -> dict:
    """GET /v2/team/sessions - List sessions."""
    user_id, api_key = _get_env()
    params = {"user_id": user_id, "page_number": page_number, "page_size": page_size}
    if search:
        params["search"] = search
    resp = _session.get(f"{BASE_URL}/v2/team/sessions", headers=_headers(api_key), params=params)
    return _check_response(resp)


def create_session(
    name: str,
    output_language: str = "AUTO",
    job_mode: str = "AUTO",
    max_contextual_job_history: int = 10,
) -> dict:
    """POST /v2/team/sessions - Create a new session."""
    user_id, api_key = _get_env()
    payload = {
        "name": name,
        "user_id": user_id,
        "output_language": output_language,
        "job_mode": job_mode,
        "max_contextual_job_history": max_contextual_job_history,
        "agent_id": "DATA_ANALYSIS_AGENT",
    }
    resp = _session.post(f"{BASE_URL}/v2/team/sessions", headers=_headers(api_key), json=payload)
    return _check_response(resp)


def delete_session(session_id: str) -> dict:
    """DELETE /v2/team/sessions/{id} - Delete a session."""
    user_id, api_key = _get_env()
    resp = _session.delete(
        f"{BASE_URL}/v2/team/sessions/{session_id}",
        headers=_headers(api_key),
        json={"user_id": user_id},
    )
    return _check_response(resp)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def create_job(
    session_id: str,
    question: str,
    dataset_id: Optional[str] = None,
    datasource_ids: Optional[list] = None,
    stream: bool = False,
    output_language: str = "AUTO",
    job_mode: str = "AUTO",
) -> dict | str:
    """POST /v2/team/jobs - Create an analysis job.

    When stream=False, returns parsed JSON response.
    When stream=True, returns the full streamed text (parsed SSE events).
    """
    user_id, api_key = _get_env()
    payload = {
        "session_id": session_id,
        "user_id": user_id,
        "question": question,
        "stream": stream,
        "output_language": output_language,
        "job_mode": job_mode,
    }
    if dataset_id:
        payload["dataset_id"] = dataset_id
    if datasource_ids:
        payload["datasource_ids"] = datasource_ids

    if not stream:
        resp = _session.post(
            f"{BASE_URL}/v2/team/jobs", headers=_headers(api_key), json=payload
        )
        return _check_response(resp)

    # Streaming mode - parse SSE events
    resp = _session.post(
        f"{BASE_URL}/v2/team/jobs",
        headers=_headers(api_key),
        json=payload,
        stream=True,
    )
    resp.raise_for_status()

    result = _parse_streaming_response(resp)
    return result


def _parse_streaming_response(resp: requests.Response) -> dict:
    """Parse SSE streaming response into a structured result.

    Returns a dict with:
      - job_id: str
      - text: str (accumulated MESSAGE content)
      - blocks: list of non-MESSAGE blocks (TABLE, IMAGE, CODE, etc.)
    """
    job_id = ""
    text_parts = []
    blocks = []
    current_event = None

    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith(":keep-alive"):
            continue
        if line.startswith("event:"):
            current_event = line[len("event:"):].strip()
            if current_event == "END_MARK":
                break
            continue
        if line.startswith("data:"):
            raw = line[len("data:"):].strip()
            if raw == "[DONE]":
                break
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if not job_id and event.get("id"):
                job_id = event["id"]

            choices = event.get("choices", [])
            if not choices:
                continue

            content = choices[0].get("delta", {}).get("content", "")
            group_name = event.get("group_name", "")
            stage = event.get("stage", "")

            # Determine block type from group_name or infer from content
            if isinstance(content, str):
                text_parts.append(content)
            elif isinstance(content, dict):
                block_type = "UNKNOWN"
                if "url" in content and "name" in content:
                    ext = content.get("name", "").rsplit(".", 1)[-1].lower()
                    block_type = "TABLE" if ext == "csv" else "IMAGE"
                blocks.append({
                    "type": block_type,
                    "group_name": group_name,
                    "stage": stage,
                    "content": content,
                })

    return {
        "job_id": job_id,
        "text": "".join(text_parts),
        "blocks": blocks,
    }


# ---------------------------------------------------------------------------
# High-Level Convenience: Full Analysis Workflow
# ---------------------------------------------------------------------------

def analyze(
    question: str,
    dataset_id: str,
    session_id: str,
    datasource_ids: Optional[list] = None,
    stream: bool = False,
    output_language: str = "AUTO",
) -> dict | str:
    """Run a single analysis question. Thin wrapper around create_job."""
    return create_job(
        session_id=session_id,
        question=question,
        dataset_id=dataset_id,
        datasource_ids=datasource_ids,
        stream=stream,
        output_language=output_language,
    )


# ---------------------------------------------------------------------------
# Cleanup Helpers
# ---------------------------------------------------------------------------

def cleanup_session(session_id: str) -> None:
    """Delete a session, ignoring errors if already deleted."""
    try:
        delete_session(session_id)
        print(f"Session {session_id} deleted.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: could not delete session {session_id}: {e}", file=sys.stderr)


def cleanup_dataset(dataset_id: str) -> None:
    """Delete a dataset, ignoring errors if already deleted."""
    try:
        delete_dataset(dataset_id)
        print(f"Dataset {dataset_id} deleted.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: could not delete dataset {dataset_id}: {e}", file=sys.stderr)


def cleanup(session_id: Optional[str] = None, dataset_id: Optional[str] = None) -> None:
    """Clean up session and/or dataset after analysis is complete."""
    if session_id:
        cleanup_session(session_id)
    if dataset_id:
        cleanup_dataset(dataset_id)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli():
    """Minimal CLI for testing individual operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Powerdrill API Client")
    sub = parser.add_subparsers(dest="command", required=True)

    # list-datasets
    p = sub.add_parser("list-datasets")
    p.add_argument("--search", default=None)
    p.add_argument("--page-size", type=int, default=10)

    # create-dataset
    p = sub.add_parser("create-dataset")
    p.add_argument("name")
    p.add_argument("--description", default="")

    # get-dataset-overview
    p = sub.add_parser("get-dataset-overview")
    p.add_argument("dataset_id")

    # delete-dataset
    p = sub.add_parser("delete-dataset")
    p.add_argument("dataset_id")

    # list-data-sources
    p = sub.add_parser("list-data-sources")
    p.add_argument("dataset_id")

    # upload-file
    p = sub.add_parser("upload-file")
    p.add_argument("dataset_id")
    p.add_argument("file_path")

    # wait-sync
    p = sub.add_parser("wait-sync")
    p.add_argument("dataset_id")

    # create-session
    p = sub.add_parser("create-session")
    p.add_argument("name")
    p.add_argument("--output-language", default="AUTO")

    # list-sessions
    p = sub.add_parser("list-sessions")
    p.add_argument("--search", default=None)

    # delete-session
    p = sub.add_parser("delete-session")
    p.add_argument("session_id")

    # create-job
    p = sub.add_parser("create-job")
    p.add_argument("session_id")
    p.add_argument("question")
    p.add_argument("--dataset-id", default=None)
    p.add_argument("--stream", action="store_true")

    # cleanup
    p = sub.add_parser("cleanup")
    p.add_argument("--session-id", default=None)
    p.add_argument("--dataset-id", default=None)

    args = parser.parse_args()

    result = None
    if args.command == "list-datasets":
        result = list_datasets(search=args.search, page_size=args.page_size)
    elif args.command == "create-dataset":
        result = create_dataset(args.name, args.description)
    elif args.command == "get-dataset-overview":
        result = get_dataset_overview(args.dataset_id)
    elif args.command == "delete-dataset":
        result = delete_dataset(args.dataset_id)
    elif args.command == "list-data-sources":
        result = list_data_sources(args.dataset_id)
    elif args.command == "upload-file":
        result = upload_and_create_data_source(args.dataset_id, args.file_path)
    elif args.command == "wait-sync":
        result = wait_for_dataset_sync(args.dataset_id)
    elif args.command == "create-session":
        result = create_session(args.name, output_language=args.output_language)
    elif args.command == "list-sessions":
        result = list_sessions(search=args.search)
    elif args.command == "delete-session":
        result = delete_session(args.session_id)
    elif args.command == "create-job":
        result = create_job(args.session_id, args.question, dataset_id=args.dataset_id, stream=args.stream)
    elif args.command == "cleanup":
        cleanup(session_id=args.session_id, dataset_id=args.dataset_id)
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
