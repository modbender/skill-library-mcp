#!/usr/bin/env python3
"""
Generate video clips using Veo 3.1 via Vertex AI.
Handles predictLongRunning + fetchPredictOperation polling + GCS download.
"""

import os
import sys
import json
import argparse
import subprocess
import time
import requests
import yaml

DEFAULT_PROJECT_ID = "gen-lang-client-0383477693"
DEFAULT_LOCATION = "us-central1"
DEFAULT_MODEL = "veo-3.1-generate-preview"
DEFAULT_GCS_BUCKET = "ai-junkie-mv-output"


def get_access_token():
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ gcloud auth failed: {e}", flush=True)
        sys.exit(1)


def download_from_gcs(gcs_uri: str, local_path: str) -> bool:
    """Download generated video from GCS (handles UUID/sample_0.mp4 structure)."""
    try:
        result = subprocess.run(
            ["gsutil", "ls", "-r", gcs_uri],
            capture_output=True, text=True, check=True
        )
        mp4_files = [f for f in result.stdout.strip().split("\n") if f.endswith(".mp4")]
        if not mp4_files:
            print(f"⚠️ No MP4 found in {gcs_uri}", flush=True)
            return False

        target = mp4_files[0]
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        subprocess.run(["gsutil", "cp", target, local_path], check=True)
        print(f"✅ Downloaded: {local_path}", flush=True)
        return True
    except subprocess.CalledProcessError:
        return False


def generate_single(prompt: str, output_path: str, project_id: str,
                    location: str, model: str, gcs_bucket: str,
                    duration: int = 8, timeout: int = 900):
    """Generate a single video clip."""
    token = get_access_token()
    
    filename = os.path.basename(output_path)
    gcs_uri = f"gs://{gcs_bucket}/veo-outputs/{filename}/"

    url = (f"https://{location}-aiplatform.googleapis.com/v1beta1/"
           f"projects/{project_id}/locations/{location}/"
           f"publishers/google/models/{model}:predictLongRunning")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "storageUri": gcs_uri,
            "video_generation_config": {
                "duration_seconds": duration,
                "fps": 24,
                "aspect_ratio": "16:9",
                "person_generation": "allow_adult"
            }
        }
    }

    print(f"🎬 Generating: {filename}", flush=True)
    print(f"   Prompt: {prompt[:80]}...", flush=True)

    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        print(f"❌ API error {resp.status_code}: {resp.text}", flush=True)
        return False

    op_name = resp.json().get("name")
    print(f"   Operation: {op_name}", flush=True)

    fetch_url = (f"https://{location}-aiplatform.googleapis.com/v1beta1/"
                 f"projects/{project_id}/locations/{location}/"
                 f"publishers/google/models/{model}:fetchPredictOperation")

    start = time.time()
    while time.time() - start < timeout:
        time.sleep(15)
        elapsed = int(time.time() - start)
        print(f"   ⏳ Waiting... ({elapsed}s)", flush=True)

        poll = requests.post(fetch_url, headers=headers,
                             json={"operationName": op_name})
        if poll.status_code != 200:
            continue

        result = poll.json()
        if result.get("done"):
            if "error" in result:
                print(f"❌ Generation failed: {result['error']}", flush=True)
                return False
            return download_from_gcs(gcs_uri, output_path)

    print(f"❌ Timeout ({timeout}s)", flush=True)
    return False


def generate_from_yaml(scene_list_path: str, output_dir: str, **kwargs):
    """Generate all scenes from a scene_list.yaml file."""
    with open(scene_list_path) as f:
        data = yaml.safe_load(f)

    scenes = data.get("scenes", [])
    results = []

    for scene in scenes:
        sid = scene["id"]
        output_path = os.path.join(output_dir, f"{sid}.mp4")

        if os.path.exists(output_path):
            print(f"⏭️ {sid}.mp4 already exists, skipping", flush=True)
            results.append({"id": sid, "status": "skipped"})
            continue

        ok = generate_single(
            prompt=scene["prompt"],
            output_path=output_path,
            duration=scene.get("duration", 8),
            **kwargs
        )
        results.append({"id": sid, "status": "ok" if ok else "failed"})
        time.sleep(5)

    print("\n📊 Results:")
    for r in results:
        icon = "✅" if r["status"] == "ok" else "⏭️" if r["status"] == "skipped" else "❌"
        print(f"  {icon} {r['id']}: {r['status']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate video with Veo 3.1")
    parser.add_argument("--prompt", help="Single prompt")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--scene-list", help="YAML scene list file")
    parser.add_argument("--project-dir", help="Project directory (uses video/scene_list.yaml)")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--gcs-bucket", default=DEFAULT_GCS_BUCKET)
    parser.add_argument("--duration", type=int, default=8)
    args = parser.parse_args()

    common = dict(project_id=args.project_id, location=args.location,
                  model=args.model, gcs_bucket=args.gcs_bucket)

    if args.prompt and args.output:
        generate_single(args.prompt, args.output, duration=args.duration, **common)
    elif args.scene_list:
        out_dir = os.path.dirname(args.scene_list) if not args.output else args.output
        generate_from_yaml(args.scene_list, out_dir, **common)
    elif args.project_dir:
        sl = os.path.join(args.project_dir, "video", "scene_list.yaml")
        out = os.path.join(args.project_dir, "video", "scenes")
        generate_from_yaml(sl, out, **common)
    else:
        parser.print_help()
