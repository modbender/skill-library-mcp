#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Google's Nano Banana Pro (Gemini 3 Pro Image) API.

Usage:
    # Synchronous (default)
    uv run generate_image.py --prompt "description" --filename "output.png"

    # Batch API - submit single (non-blocking, 50% cheaper)
    uv run generate_image.py --prompt "description" --filename "output.png" --batch

    # Batch API - submit multiple from JSON
    uv run generate_image.py --batch-file requests.json

    # Batch API - check/retrieve results
    uv run generate_image.py --batch-check "batches/abc123" --filename "output.png"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

MODEL = "gemini-3-pro-image-preview"
PENDING_JOBS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "memory" / "pending-batch-jobs.json"


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY")


def _load_pending_jobs() -> list[dict]:
    """Load pending batch jobs list from memory."""
    if PENDING_JOBS_PATH.exists():
        try:
            return json.loads(PENDING_JOBS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_pending_jobs(jobs: list[dict]) -> None:
    """Save pending batch jobs list to memory."""
    PENDING_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PENDING_JOBS_PATH.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n")


def add_pending_job(job_name: str, filenames: str | list[str], prompt: str | None = None) -> None:
    """Register a batch job as pending. filenames can be single string or list of strings."""
    jobs = _load_pending_jobs()
    # Avoid duplicates
    if any(j["job_name"] == job_name for j in jobs):
        return
    # Normalize filenames to list
    if isinstance(filenames, str):
        filenames = [filenames]
    jobs.append({
        "job_name": job_name,
        "filenames": filenames,
        "prompt": prompt,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    _save_pending_jobs(jobs)


def get_pending_job(job_name: str) -> dict | None:
    """Get a pending job by name."""
    jobs = _load_pending_jobs()
    for j in jobs:
        if j["job_name"] == job_name:
            return j
    return None


def remove_pending_job(job_name: str) -> None:
    """Remove a completed batch job from pending list."""
    jobs = _load_pending_jobs()
    jobs = [j for j in jobs if j["job_name"] != job_name]
    if jobs:
        _save_pending_jobs(jobs)
    elif PENDING_JOBS_PATH.exists():
        PENDING_JOBS_PATH.unlink()


def save_image_from_response(response, output_path: Path) -> bool:
    """Save image from a GenerateContentResponse to output_path.

    Returns True if image was saved successfully.
    """
    from io import BytesIO
    from PIL import Image as PILImage

    image_saved = False
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image_data = part.inline_data.data
            if isinstance(image_data, str):
                import base64
                image_data = base64.b64decode(image_data)

            image = PILImage.open(BytesIO(image_data))

            if image.mode == 'RGBA':
                rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                rgb_image.save(str(output_path), 'PNG')
            elif image.mode == 'RGB':
                image.save(str(output_path), 'PNG')
            else:
                image.convert('RGB').save(str(output_path), 'PNG')
            image_saved = True

    if image_saved:
        full_path = output_path.resolve()
        print(f"\nImage saved.")
        print(f"MEDIA:{full_path}")
    return image_saved


def load_batch_file(filepath: str) -> list[dict]:
    """Load batch requests from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of request objects")

        # Validate required fields
        for i, req in enumerate(data):
            if not isinstance(req, dict):
                raise ValueError(f"Request {i} is not an object")
            if "prompt" not in req:
                raise ValueError(f"Request {i} missing 'prompt' field")
            if "filename" not in req:
                raise ValueError(f"Request {i} missing 'filename' field")
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading batch file: {e}", file=sys.stderr)
        sys.exit(1)


def build_batch_request(
    prompt: str,
    input_image_path: str | None,
    resolution: str,
    aspect_ratio: str | None,
    client,
) -> dict:
    """Build an inline request dict for the Batch API."""
    parts = []

    if input_image_path:
        ext = Path(input_image_path).suffix.lower()
        mime_map = {
            '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp',
        }
        mime_type = mime_map.get(ext, 'application/octet-stream')

        uploaded = client.files.upload(
            file=input_image_path,
            config={'mime_type': mime_type},
        )
        print(f"Uploaded input image: {uploaded.name}")
        parts.append({
            'file_data': {
                'file_uri': uploaded.uri,
                'mime_type': uploaded.mime_type,
            }
        })

    parts.append({'text': prompt})

    image_config = {'image_size': resolution}
    if aspect_ratio and not input_image_path:
        image_config['aspect_ratio'] = aspect_ratio

    return {
        'contents': [{'parts': parts, 'role': 'user'}],
        'config': {
            'response_modalities': ['TEXT', 'IMAGE'],
            'image_config': image_config,
        },
    }



def handle_batch_result(job, output_paths: Path | list[Path]) -> None:
    """Process a completed batch job and save image results.

    output_paths can be a single Path or list of Paths.
    """
    state_name = job.state.value if job.state else "UNKNOWN"

    if state_name == 'JOB_STATE_FAILED':
        error_msg = job.error.message if job.error else "Unknown error"
        print(f"Error: Batch job failed: {error_msg}", file=sys.stderr)
        sys.exit(1)
    elif state_name == 'JOB_STATE_CANCELLED':
        print("Error: Batch job was cancelled.", file=sys.stderr)
        sys.exit(1)
    elif state_name == 'JOB_STATE_EXPIRED':
        print("Error: Batch job expired.", file=sys.stderr)
        sys.exit(1)
    elif state_name != 'JOB_STATE_SUCCEEDED':
        print(f"Error: Unexpected job state: {state_name}", file=sys.stderr)
        sys.exit(1)

    if not job.dest or not job.dest.inlined_responses:
        print("Error: No inlined responses in batch result.", file=sys.stderr)
        sys.exit(1)

    # Normalize to list
    if isinstance(output_paths, Path):
        output_paths = [output_paths]

    # Save each response to corresponding file
    for i, resp_entry in enumerate(job.dest.inlined_responses):
        if i >= len(output_paths):
            print(f"Warning: More responses ({len(job.dest.inlined_responses)}) than output files ({len(output_paths)})", file=sys.stderr)
            break

        if resp_entry.error:
            error_msg = resp_entry.error.message if hasattr(resp_entry.error, 'message') else str(resp_entry.error)
            print(f"Error in response {i+1}: {error_msg}", file=sys.stderr)
            continue

        if not save_image_from_response(resp_entry.response, output_paths[i]):
            print(f"Error: No image was generated in response {i+1}.", file=sys.stderr)
            continue


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro (Gemini 3 Pro Image)"
    )
    parser.add_argument(
        "--prompt", "-p",
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        help="Output filename (e.g., sunset-mountains.png). Required for single-image mode, omitted for --batch-file."
    )
    parser.add_argument(
        "--input-image", "-i",
        help="Optional input image path for editing/modification"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        default=None,
        help="Aspect ratio (e.g., 16:9, 9:16, 1:1). Only for generation, not editing."
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (overrides GEMINI_API_KEY env var)"
    )

    # Batch mode arguments
    batch_group = parser.add_mutually_exclusive_group()
    batch_group.add_argument(
        "--batch", "--batch-submit",
        action="store_true",
        default=False,
        dest="batch",
        help="Submit to Batch API (non-blocking, 50%% cheaper). Prints job name."
    )
    batch_group.add_argument(
        "--batch-file",
        metavar="FILE",
        help="Submit multiple images from JSON file (array of {prompt, filename, resolution, aspect_ratio})"
    )
    batch_group.add_argument(
        "--batch-check",
        metavar="JOB_NAME",
        help="Check status / retrieve results of a batch job (e.g., batches/abc123)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.batch_check:
        # For batch-check: filename is required, prompt is not
        if not args.filename:
            parser.error("--batch-check requires --filename")
    elif args.batch_file:
        # For batch-file: no filename/prompt needed (in JSON)
        pass
    else:
        # For single-image mode (default, --batch): both required
        if not args.prompt or not args.filename:
            parser.error("--prompt and --filename are required for single-image mode")

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Import here after checking API key to avoid slow import on error
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    # Initialise client
    client = genai.Client(api_key=api_key)

    # --- BATCH CHECK MODE ---
    if args.batch_check:
        try:
            job = client.batches.get(name=args.batch_check)
            state_val = job.state.value if job.state else "UNKNOWN"
            print(f"Batch job: {args.batch_check}")
            print(f"State: {state_val}")

            if not job.done:
                print("Job is still in progress. Use --batch-check again later.")
                sys.exit(0)

            # Get filenames from pending job info or use --filename
            pending = get_pending_job(args.batch_check)
            if pending:
                filenames = pending.get("filenames", [args.filename])
            else:
                filenames = [args.filename]

            # Create output paths
            output_paths = [Path(f) for f in filenames]
            for p in output_paths:
                p.parent.mkdir(parents=True, exist_ok=True)

            remove_pending_job(args.batch_check)
            handle_batch_result(job, output_paths)
        except Exception as e:
            print(f"Error checking batch job: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Set up output path(s) - only for non-batch-check modes
    if args.filename:
        output_path = Path(args.filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input image if provided (for editing & auto-resolution detection)
    input_image = None
    output_resolution = args.resolution
    if args.input_image:
        try:
            input_image = PILImage.open(args.input_image)
            print(f"Loaded input image: {args.input_image}")

            # Auto-detect resolution if not explicitly set by user
            if args.resolution == "1K":  # Default value
                width, height = input_image.size
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                else:
                    output_resolution = "1K"
                print(f"Auto-detected resolution: {output_resolution} (from input {width}x{height})")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)

    # --- BATCH FILE SUBMIT MODE ---
    if args.batch_file:
        try:
            batch_requests = load_batch_file(args.batch_file)
            filenames = []

            print(f"Loading {len(batch_requests)} image requests from {args.batch_file}...")
            requests = []

            for i, req in enumerate(batch_requests):
                prompt = req["prompt"]
                filename = req["filename"]
                resolution = req.get("resolution", "1K")
                aspect_ratio = req.get("aspect_ratio", None)

                filenames.append(filename)
                print(f"  [{i+1}] {filename}: {prompt[:50]}...")

                request = build_batch_request(
                    prompt=prompt,
                    input_image_path=None,  # batch-file doesn't support input images yet
                    resolution=resolution,
                    aspect_ratio=aspect_ratio,
                    client=client,
                )
                requests.append(request)

            display_name = f"batch-{len(batch_requests)}"[:63]
            print(f"Submitting batch job with {len(requests)} images: {display_name}...")
            batch_job = client.batches.create(
                model=MODEL,
                src=requests,
                config={'display_name': display_name},
            )
            print(f"Batch job created: {batch_job.name}")
            add_pending_job(batch_job.name, filenames)
            print(f"\nBATCH_JOB: {batch_job.name}")
        except Exception as e:
            print(f"Error in batch operation: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # --- SINGLE IMAGE BATCH SUBMIT MODE ---
    if args.batch:
        try:
            aspect_info = f", aspect ratio {args.aspect_ratio}" if args.aspect_ratio and not input_image else ""
            mode = "Editing" if args.input_image else "Generating"
            print(f"[Batch] {mode} image with resolution {output_resolution}{aspect_info}...")

            request = build_batch_request(
                prompt=args.prompt,
                input_image_path=args.input_image,
                resolution=output_resolution,
                aspect_ratio=args.aspect_ratio,
                client=client,
            )

            stem = Path(args.filename).stem
            display_name = f"img-{stem}"[:63]

            print(f"Submitting batch job: {display_name}...")
            batch_job = client.batches.create(
                model=MODEL,
                src=[request],
                config={'display_name': display_name},
            )
            print(f"Batch job created: {batch_job.name}")
            add_pending_job(batch_job.name, args.filename, args.prompt)
            print(f"\nBATCH_JOB: {batch_job.name}")
        except Exception as e:
            print(f"Error in batch operation: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # --- SYNCHRONOUS MODE (default) ---
    if input_image:
        contents = [input_image, args.prompt]
        print(f"Editing image with resolution {output_resolution}...")
    else:
        contents = args.prompt
        aspect_info = f", aspect ratio {args.aspect_ratio}" if args.aspect_ratio else ""
        print(f"Generating image with resolution {output_resolution}{aspect_info}...")

    image_config_kwargs = {"image_size": output_resolution}
    if args.aspect_ratio and not input_image:
        image_config_kwargs["aspect_ratio"] = args.aspect_ratio

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(**image_config_kwargs)
            )
        )

        if not save_image_from_response(response, output_path):
            print("Error: No image was generated in the response.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
