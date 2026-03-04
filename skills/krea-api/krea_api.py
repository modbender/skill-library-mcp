#!/usr/bin/env python3
"""
Krea.ai API - Image Generation Skill

Usage:
    python krea_api.py --prompt "A beautiful sunset" --model flux

Or use as a module:
    from krea_api import KreaAPI
    api = KreaAPI(key_id="...", secret="...")
    urls = api.generate_and_wait(prompt="...")
"""

import json
import os
import time
import urllib.request
import urllib.error
import argparse
import webbrowser
from typing import Optional, List


class KreaAPI:
    """Client for Krea.ai image generation API."""
    
    BASE_URL = "https://api.krea.ai"
    
    # Available image models and their endpoints
    IMAGE_MODELS = {
        "flux": "/generate/image/bfl/flux-1-dev",
        "flux-kontext": "/generate/image/bfl/flux-1-dev-kontext",
        "flux-1.1-pro": "/generate/image/bfl/flux-1-1-pro",
        "flux-1.1-pro-ultra": "/generate/image/bfl/flux-1-1-pro-ultra",
        "nano-banana": "/generate/image/krea/nano-banana",
        "nano-banana-pro": "/generate/image/krea/nano-banana-pro",
        "imagen-3": "/generate/image/google/imagen-3",
        "imagen-4": "/generate/image/google/imagen-4",
        "imagen-4-fast": "/generate/image/google/imagen-4-fast",
        "imagen-4-ultra": "/generate/image/google/imagen-4-ultra",
        "ideogram-2.0a-turbo": "/generate/image/ideogram/ideogram-2-0a-turbo",
        "ideogram-3.0": "/generate/image/ideogram/ideogram-3-0",
        "seedream-3": "/generate/image/seedream/seedream-3",
        "seedream-4": "/generate/image/seedream/seedream-4",
        "chatgpt-image": "/generate/image/openai/chatgpt-image",
        "runway-gen-4": "/generate/image/runway/gen-4",
    }
    
    def __init__(self, key_id: str = None, secret: str = None):
        """
        Initialize the Krea API client.
        
        Args:
            key_id: Your API key ID (or set via config file)
            secret: Your API secret (or set via config file)
        """
        # Use provided credentials or read from file
        if not key_id or not secret:
            key_id, secret = self._get_credentials_from_file()
        
        if not key_id or not secret:
            raise ValueError(
                "API credentials required. Set via:\n"
                "  1. Arguments: --key-id ID --secret SECRET\n"
                "  2. File: ~/.openclaw/credentials/krea.json\n"
                "     Format: {\"apiKey\": \"KEY_ID:SECRET\"}\n"
                "     Permissions: chmod 600 ~/.openclaw/credentials/krea.json"
            )
        
        self.token = f"{key_id}:{secret}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Krea-API/1.0)"
        }
    
    def _get_credentials_from_file(self) -> tuple:
        """Read credentials from ~/.openclaw/credentials/krea.json"""
        possible_paths = [
            "~/.openclaw/credentials/krea.json",
        ]
        
        for creds_path in possible_paths:
            expanded_path = os.path.expanduser(creds_path)
            
            try:
                if os.path.exists(expanded_path):
                    with open(expanded_path, 'r') as f:
                        creds = json.load(f)
                    
                    api_key = creds.get("apiKey", "")
                    if api_key and ":" in api_key:
                        key_id, secret = api_key.split(":", 1)
                        return key_id, secret
            except (json.JSONDecodeError, OSError, PermissionError):
                continue  # Try next path
        
        return None, None
    
    def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        width: int = 1024,
        height: int = 1024,
        steps: int = 25,
        guidance_scale: float = 3.0,
        seed: Optional[str] = None,
    ) -> dict:
        """
        Create an image generation job.
        
        Args:
            prompt: Text description of the image (max 1800 chars)
            model: Model name (default: "flux")
            width: Image width (512-2368, default: 1024)
            height: Image height (512-2368, default: 1024)
            steps: Generation steps (1-100, default: 25)
            guidance_scale: Guidance scale (0-24, default: 3.0)
            seed: Random seed for reproducibility
            
        Returns:
            dict with job_id, status, created_at
        """
        endpoint = self.IMAGE_MODELS.get(model)
        if not endpoint:
            raise ValueError(
                f"Unknown model: {model}. Available: {list(self.IMAGE_MODELS.keys())}"
            )
        
        # Input validation
        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")
        if len(prompt) > 1800:
            raise ValueError(f"prompt must be 1800 characters or less (got {len(prompt)})")
        
        if not isinstance(width, int) or not (512 <= width <= 2368):
            raise ValueError(f"width must be between 512 and 2368 (got {width})")
        if not isinstance(height, int) or not (512 <= height <= 2368):
            raise ValueError(f"height must be between 512 and 2368 (got {height})")
        if not isinstance(steps, int) or not (1 <= steps <= 100):
            raise ValueError(f"steps must be between 1 and 100 (got {steps})")
        if not isinstance(guidance_scale, (int, float)) or not (0 <= guidance_scale <= 24):
            raise ValueError(f"guidance_scale must be between 0 and 24 (got {guidance_scale})")
        
        url = f"{self.BASE_URL}{endpoint}"
        
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale_flux": guidance_scale,
        }
        
        if seed:
            payload["seed"] = seed
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
        for k, v in self.headers.items():
            req.add_header(k, v)
        
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    
    def get_job(self, job_id: str) -> dict:
        """Get the status and result of a job."""
        url = f"{self.BASE_URL}/jobs/{job_id}"
        req = urllib.request.Request(url, method="GET")
        for k, v in self.headers.items():
            if k.lower() == "content-type":
                continue
            req.add_header(k, v)

        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    
    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: float = 120.0
    ) -> dict:
        """Poll until job completes or times out."""
        start = time.time()
        while time.time() - start < timeout:
            job = self.get_job(job_id)
            status = job.get("status")
            
            if status == "completed":
                return job
            elif status == "failed":
                raise Exception(f"Job failed: {job}")
            elif status == "cancelled":
                raise Exception("Job was cancelled")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
    
    def generate_and_wait(self, prompt: str, **kwargs) -> List[str]:
        """Generate an image and wait for the result."""
        job = self.generate_image(prompt, **kwargs)
        print(f"Job created: {job['job_id']} (status: {job['status']})")

        result = self.wait_for_completion(job["job_id"])
        return result.get("result", {}).get("urls", [])

    def list_jobs(self, limit: int = 100, job_type: str = None) -> dict:
        """List your recent jobs."""
        url = f"{self.BASE_URL}/jobs"
        params = [f"limit={limit}"]
        if job_type:
            params.append(f"types={job_type}")

        full_url = f"{url}?{'&'.join(params)}"
        req = urllib.request.Request(full_url, method="GET")
        for k, v in self.headers.items():
            if k.lower() == "content-type":
                continue
            req.add_header(k, v)

        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())

    def get_usage_summary(self) -> str:
        """
        Get a summary of recent API usage.
        Note: Krea doesn't provide a usage API, so we list recent jobs.
        For accurate compute unit usage, check the web dashboard.
        """
        summary = []
        summary.append("Recent API Jobs:")
        summary.append("-" * 40)

        for model_name, endpoint in self.IMAGE_MODELS.items():
            # Extract job type from endpoint
            job_type = endpoint.strip("/").split("/")[-1]
            result = self.list_jobs(limit=5, job_type=job_type)
            items = result.get("items", [])
            if items:
                summary.append(f"\n{model_name}: {len(items)} recent jobs")

        summary.append("\n" + "=" * 40)
        summary.append("For accurate compute unit usage, visit:")
        summary.append("https://www.krea.ai/settings/usage-statistics")
        return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="Generate images with Krea.ai API")
    parser.add_argument("--prompt", help="Image description")
    parser.add_argument("--model", default="flux", help="Model name (default: flux)")
    parser.add_argument("--width", type=int, default=1024, help="Image width (512-2368)")
    parser.add_argument("--height", type=int, default=1024, help="Image height (512-2368)")
    parser.add_argument("--steps", type=int, default=25, help="Generation steps (1-100)")
    parser.add_argument("--guidance-scale", type=float, default=3.0, help="Guidance scale (0-24)")
    parser.add_argument("--key-id", help="API key ID")
    parser.add_argument("--secret", help="API secret")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--usage", action="store_true", help="Open usage statistics page")
    parser.add_argument("--jobs", type=int, metavar="N", help="List N recent jobs (default: 10)")

    args = parser.parse_args()

    if args.list_models:
        print("Available models:")
        for name in KreaAPI.IMAGE_MODELS:
            print(f"  - {name}")
        return

    if args.usage:
        print("Opening Krea.ai usage statistics...")
        webbrowser.open("https://www.krea.ai/settings/usage-statistics")
        print("Check your browser for the usage dashboard.")
        return

    if args.jobs is not None:
        api = KreaAPI(key_id=args.key_id, secret=args.secret)
        limit = min(args.jobs, 100)  # Cap at 100
        result = api.list_jobs(limit=limit)
        items = result.get("items", [])
        if not items:
            print("No recent jobs found.")
        else:
            print(f"Recent jobs (last {len(items)}):")
            for i, job in enumerate(items, 1):
                status = job.get("status", "unknown")
                created = job.get("created_at", "")[:19].replace("T", " ")
                summary = f"{i}. [{status}] {created}"
                if job.get("result", {}).get("urls"):
                    summary += " ✓ Generated"
                print(summary)
        return

    if not args.prompt:
        parser.error("--prompt is required unless --list-models is set")

    api = KreaAPI(key_id=args.key_id, secret=args.secret)

    print(f"Generating '{args.prompt[:50]}...' with {args.model}...")
    urls = api.generate_and_wait(
        prompt=args.prompt,
        model=args.model,
        width=args.width,
        height=args.height,
        steps=args.steps,
        guidance_scale=args.guidance_scale
    )

    print("\nGenerated images:")
    for url in urls:
        print(f"  {url}")


if __name__ == "__main__":
    main()
