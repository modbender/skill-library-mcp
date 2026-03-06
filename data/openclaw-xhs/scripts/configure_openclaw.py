#!/usr/bin/env python3
"""
Configure openclaw.json for the XHS skill.
Called by install.sh — updates the skill entry with user-provided settings.
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Configure OpenClaw for XHS skill")
    parser.add_argument("--config", required=True, help="Path to openclaw.json")
    parser.add_argument("--toolkit-dir", required=True)
    parser.add_argument("--cookies-file", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--chrome-profile", required=True)
    parser.add_argument("--chrome-path", required=True)
    parser.add_argument("--image-api-key", default="")
    parser.add_argument("--image-base-url", default="")
    parser.add_argument("--image-model", default="")
    parser.add_argument("--gateway-token", default="")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = json.loads(config_path.read_text())

    cfg.setdefault("skills", {}).setdefault("entries", {})

    env = {
        "XHS_TOOLKIT_DIR": args.toolkit_dir,
        "XHS_COOKIES_FILE": args.cookies_file,
        "XHS_DATA_DIR": args.data_dir,
        "XHS_CHROME_PROFILE": args.chrome_profile,
        "CHROME_PATH": args.chrome_path,
    }

    if args.image_api_key:
        env["IMAGE_API_KEY"] = args.image_api_key
    if args.image_base_url:
        env["IMAGE_BASE_URL"] = args.image_base_url
    if args.image_model:
        env["IMAGE_MODEL"] = args.image_model
    if args.gateway_token:
        env["OPENCLAW_GATEWAY_TOKEN"] = args.gateway_token

    cfg["skills"]["entries"]["xhs"] = {"env": env}

    config_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print("Config updated successfully.")


if __name__ == "__main__":
    main()
