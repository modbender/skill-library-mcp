import argparse
import base64
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from typing import Any, Dict, List, Optional, Tuple

import google.auth
from google.auth.transport.requests import Request
import requests

DFCX_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/dialogflow",
]
CES_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/ces",
]

DEFAULT_DFCX_BASE = "https://dialogflow.googleapis.com/v3beta1"
DEFAULT_CES_BASE = "https://ces.googleapis.com/v1beta"


def get_access_token(scopes: List[str]) -> str:
    creds, _ = google.auth.default(scopes=scopes)
    if not creds.valid:
        creds.refresh(Request())
    if not creds.token:
        raise RuntimeError("Failed to obtain access token.")
    return creds.token


def http_request(method: str, url: str, token: str, **kwargs) -> Dict[str, Any]:
    headers = kwargs.pop("headers", {})
    headers.setdefault("Authorization", f"Bearer {token}")
    headers.setdefault("Content-Type", "application/json")
    response = requests.request(method, url, headers=headers, **kwargs)
    if response.status_code >= 400:
        raise RuntimeError(
            f"HTTP {response.status_code} for {method} {url}: {response.text}"
        )
    if response.text:
        return response.json()
    return {}


def wait_operation(base_url: str, op_name: str, token: str, timeout_s: int = 900) -> Dict[str, Any]:
    start = time.time()
    delay = 2.0
    if op_name.startswith("http"):
        op_url = op_name
    else:
        op_url = f"{base_url}/{op_name}"

    while True:
        op = http_request("GET", op_url, token)
        if op.get("done"):
            if "error" in op:
                raise RuntimeError(f"Operation failed: {json.dumps(op['error'], indent=2)}")
            return op.get("response", {})
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Operation timed out after {timeout_s}s: {op_name}")
        time.sleep(delay)
        delay = min(delay * 1.5, 10.0)


def get_dfcx_agent(dfcx_base: str, agent_name: str, token: str) -> Dict[str, Any]:
    url = f"{dfcx_base}/{agent_name}"
    return http_request("GET", url, token)


def export_dfcx_agent(
    dfcx_base: str,
    agent_name: str,
    token: str,
    data_format: str = "JSON_PACKAGE",
    environment: Optional[str] = None,
    agent_uri: Optional[str] = None,
    include_bigquery_export_settings: bool = False,
) -> Dict[str, Any]:
    url = f"{dfcx_base}/{agent_name}:export"
    body: Dict[str, Any] = {"dataFormat": data_format}
    if environment:
        body["environment"] = environment
    if agent_uri:
        body["agentUri"] = agent_uri
    if include_bigquery_export_settings:
        body["includeBigqueryExportSettings"] = True

    op = http_request("POST", url, token, json=body)
    return wait_operation(dfcx_base, op["name"], token)


def parse_flow_id(start_flow: Optional[str]) -> Optional[str]:
    if not start_flow:
        return None
    parts = start_flow.split("/flows/")
    if len(parts) == 2:
        return parts[1]
    if "/flows/" in start_flow:
        return start_flow.split("/flows/")[-1]
    return None


def parse_environment_id(environment: Optional[str]) -> Optional[str]:
    if not environment:
        return None
    if "/environments/" in environment:
        return environment.split("/environments/")[-1]
    return environment


def parse_json_from_zip(zf: zipfile.ZipFile, path: str) -> Dict[str, Any]:
    with zf.open(path) as fp:
        return json.loads(fp.read().decode("utf-8"))


def summarize_export(zip_bytes: bytes, output_dir: str) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "component_counts": {},
        "components": {},
        "unclassified_files": [],
    }
    component_index: Dict[str, List[Dict[str, Any]]] = {}

    if not zipfile.is_zipfile(io.BytesIO(zip_bytes)):
        summary["note"] = "Export content is not a zip archive. Skipping detailed parsing."
        return summary

    os.makedirs(output_dir, exist_ok=True)
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    zf.extractall(output_dir)

    for path in zf.namelist():
        if not path.endswith(".json"):
            continue
        if path.endswith("/agent.json") or path == "agent.json":
            data = parse_json_from_zip(zf, path)
            summary["agent"] = {
                "name": data.get("name"),
                "displayName": data.get("displayName"),
                "defaultLanguageCode": data.get("defaultLanguageCode"),
                "supportedLanguageCodes": data.get("supportedLanguageCodes", []),
                "timeZone": data.get("timeZone"),
                "startFlow": data.get("startFlow"),
                "startPlaybook": data.get("startPlaybook"),
            }
            continue

        category = classify_path(path)
        if category is None:
            summary["unclassified_files"].append(path)
            continue

        data = parse_json_from_zip(zf, path)
        entry = {
            "file": path,
            "name": data.get("name"),
            "displayName": data.get("displayName"),
        }
        component_index.setdefault(category, []).append(entry)

    for category, items in component_index.items():
        summary["component_counts"][category] = len(items)
        summary["components"][category] = items

    return summary


def classify_path(path: str) -> Optional[str]:
    parts = [p for p in path.split("/") if p]
    if not parts:
        return None
    if parts[0] == "intents":
        return "intents"
    if parts[0] == "entityTypes":
        return "entity_types"
    if parts[0] == "webhooks":
        return "webhooks"
    if parts[0] == "testCases":
        return "test_cases"
    if parts[0] == "playbooks":
        return "playbooks"
    if parts[0] == "generators":
        return "generators"
    if parts[0] == "transitionRouteGroups":
        return "transition_route_groups"
    if parts[0] == "flows":
        if len(parts) == 2 and parts[1].endswith(".json"):
            return "flows"
        if len(parts) >= 4 and parts[2] == "pages":
            return "pages"
        if len(parts) >= 4 and parts[2] == "transitionRouteGroups":
            return "transition_route_groups"
    return None


def create_ces_app(
    ces_base: str,
    project: str,
    location: str,
    token: str,
    display_name: str,
    description: Optional[str] = None,
    app_id: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    url = f"{ces_base}/projects/{project}/locations/{location}/apps"
    params = {"appId": app_id} if app_id else None
    body: Dict[str, Any] = {"displayName": display_name}
    if description:
        body["description"] = description
    if metadata:
        body["metadata"] = metadata
    op = http_request("POST", url, token, params=params, json=body)
    return wait_operation(ces_base, op["name"], token)


def create_ces_agent(
    ces_base: str,
    app_name: str,
    token: str,
    display_name: str,
    remote_agent: Dict[str, Any],
    agent_id: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    url = f"{ces_base}/{app_name}/agents"
    params = {"agentId": agent_id} if agent_id else None
    body: Dict[str, Any] = {
        "displayName": display_name,
        "remoteDialogflowAgent": remote_agent,
    }
    if description:
        body["description"] = description
    return http_request("POST", url, token, params=params, json=body)


def set_root_agent(ces_base: str, app_name: str, agent_name: str, token: str) -> Dict[str, Any]:
    url = f"{ces_base}/{app_name}"
    params = {"updateMask": "root_agent"}
    body = {"name": app_name, "rootAgent": agent_name}
    return http_request("PATCH", url, token, params=params, json=body)


def load_json_arg(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if not value:
        return None
    if os.path.exists(value):
        with open(value, "r", encoding="utf-8") as fp:
            return json.load(fp)
    return json.loads(value)


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate a Dialogflow CX agent into CX Agent Studio (CES) using official APIs."
    )
    parser.add_argument("--dfcx-agent", required=True, help="DFCX agent resource name")
    parser.add_argument("--dfcx-base-url", default=DEFAULT_DFCX_BASE)
    parser.add_argument("--dfcx-environment", default=None)
    parser.add_argument("--dfcx-flow-id", default=None)
    parser.add_argument("--dfcx-export-gcs-uri", default=None)
    parser.add_argument("--include-bigquery-export-settings", action="store_true")

    parser.add_argument("--ces-base-url", default=DEFAULT_CES_BASE)

    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--skip-export", action="store_true")

    parser.add_argument("--studio-project", help="CES project ID")
    parser.add_argument("--studio-location", help="CES location")
    parser.add_argument("--studio-app", help="Existing CES app resource name")
    parser.add_argument("--studio-app-id", help="Optional CES app ID")
    parser.add_argument("--studio-app-display-name", help="Display name for CES app")
    parser.add_argument("--studio-app-description", default=None)

    parser.add_argument("--studio-agent-id", help="Optional CES agent ID")
    parser.add_argument("--studio-agent-display-name", help="Display name for CES agent")
    parser.add_argument("--studio-agent-description", default=None)
    parser.add_argument(
        "--skip-root-agent",
        action="store_false",
        dest="set_root_agent",
        help="Do not set the CES app root_agent",
    )
    parser.set_defaults(set_root_agent=True)

    parser.add_argument("--input-map", help="JSON string or file path for input variable mapping")
    parser.add_argument("--output-map", help="JSON string or file path for output variable mapping")
    parser.add_argument(
        "--respect-response-interruption-settings",
        action="store_true",
        help="Honor DFCX allow_playback_interruption settings",
    )

    parser.add_argument("--output-dir", default="./dfcx_migration_output")
    parser.add_argument("--report", default=None)

    args = parser.parse_args()

    token = get_access_token(list(set(DFCX_SCOPES + CES_SCOPES)))

    dfcx_agent = get_dfcx_agent(args.dfcx_base_url, args.dfcx_agent, token)
    dfcx_display = dfcx_agent.get("displayName") or "DFCX Agent"
    dfcx_flow_id = args.dfcx_flow_id or parse_flow_id(dfcx_agent.get("startFlow"))
    dfcx_env_id = parse_environment_id(args.dfcx_environment)

    report: Dict[str, Any] = {
        "dfcx_agent": dfcx_agent,
        "dfcx_agent_display_name": dfcx_display,
        "dfcx_flow_id": dfcx_flow_id,
        "dfcx_environment_id": dfcx_env_id,
    }

    export_bytes: Optional[bytes] = None

    if not args.skip_export:
        export_response = export_dfcx_agent(
            args.dfcx_base_url,
            args.dfcx_agent,
            token,
            data_format="JSON_PACKAGE",
            environment=args.dfcx_environment,
            agent_uri=args.dfcx_export_gcs_uri,
            include_bigquery_export_settings=args.include_bigquery_export_settings,
        )
        report["dfcx_export_response"] = export_response

        if "agentContent" in export_response:
            export_bytes = base64.b64decode(export_response["agentContent"])
            export_hash = hashlib.sha256(export_bytes).hexdigest()
            report["dfcx_export_sha256"] = export_hash

            os.makedirs(args.output_dir, exist_ok=True)
            export_path = os.path.join(args.output_dir, "dfcx_agent_export.zip")
            with open(export_path, "wb") as fp:
                fp.write(export_bytes)
            report["dfcx_export_path"] = export_path

            summary = summarize_export(export_bytes, os.path.join(args.output_dir, "export"))
            report["dfcx_export_summary"] = summary
        else:
            report["dfcx_export_note"] = (
                "Export returned agentUri only. Use the GCS URI to retrieve content."
            )

    if args.export_only:
        output_report = args.report or os.path.join(args.output_dir, "migration_report.json")
        report_dir = os.path.dirname(output_report)
        if report_dir:
            os.makedirs(report_dir, exist_ok=True)
        write_json(output_report, report)
        print(f"Export-only report written to {output_report}")
        return 0

    if not args.studio_app:
        if not args.studio_project or not args.studio_location:
            raise ValueError("--studio-project and --studio-location are required if --studio-app is not provided.")

    ces_app_name = args.studio_app
    ces_app_resource: Optional[Dict[str, Any]] = None
    if not ces_app_name:
        app_display = args.studio_app_display_name or f"{dfcx_display} (CX Studio)"
        metadata = {
            "dfcxAgent": args.dfcx_agent,
        }
        if report.get("dfcx_export_sha256"):
            metadata["dfcxExportSha256"] = report["dfcx_export_sha256"]

        ces_app_resource = create_ces_app(
            args.ces_base_url,
            args.studio_project,
            args.studio_location,
            token,
            display_name=app_display,
            description=args.studio_app_description,
            app_id=args.studio_app_id,
            metadata=metadata,
        )
        ces_app_name = ces_app_resource.get("name")
        report["ces_app"] = ces_app_resource
    else:
        report["ces_app"] = {"name": ces_app_name}

    remote_agent: Dict[str, Any] = {"agent": args.dfcx_agent}
    if dfcx_flow_id:
        remote_agent["flowId"] = dfcx_flow_id
    if dfcx_env_id:
        remote_agent["environmentId"] = dfcx_env_id

    input_map = load_json_arg(args.input_map)
    output_map = load_json_arg(args.output_map)
    if input_map:
        remote_agent["inputVariableMapping"] = input_map
    if output_map:
        remote_agent["outputVariableMapping"] = output_map
    if args.respect_response_interruption_settings:
        remote_agent["respectResponseInterruptionSettings"] = True

    ces_agent_display = args.studio_agent_display_name or f"{dfcx_display} (Remote DFCX)"
    ces_agent_resource = create_ces_agent(
        args.ces_base_url,
        ces_app_name,
        token,
        display_name=ces_agent_display,
        remote_agent=remote_agent,
        agent_id=args.studio_agent_id,
        description=args.studio_agent_description,
    )
    report["ces_agent"] = ces_agent_resource

    if args.set_root_agent:
        updated_app = set_root_agent(args.ces_base_url, ces_app_name, ces_agent_resource["name"], token)
        report["ces_app_updated"] = updated_app

    output_report = args.report or os.path.join(args.output_dir, "migration_report.json")
    report_dir = os.path.dirname(output_report)
    if report_dir:
        os.makedirs(report_dir, exist_ok=True)
    write_json(output_report, report)
    print(f"Migration report written to {output_report}")
    print(f"CES app: {ces_app_name}")
    print(f"CES agent: {ces_agent_resource.get('name')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
