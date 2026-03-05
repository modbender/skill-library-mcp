"""Core pipeline logic for ClawCut — extracted and extended from MoneyPrinterTurbo v3."""
import json
import os
import re
import subprocess
import time
import concurrent.futures
import logging

from config import (
    VERTEX_PROJECT, VERTEX_LOCATION,
    MODEL_SCRIPT, MODEL_IMAGE, MODEL_VIDEO, MODEL_VIDEO_FAST,
    FFMPEG_BIN, OUTPUT_DIR,
)

logger = logging.getLogger("clawcut")


# ─── Vertex AI Client ───────────────────────────────────────────────

def _gemini_client():
    """Create a Vertex AI client using service account credentials."""
    from google import genai
    return genai.Client(
        vertexai=True,
        project=VERTEX_PROJECT,
        location=VERTEX_LOCATION,
    )


# ─── Script Generation ──────────────────────────────────────────────

def generate_script_gemini(topic: str, reference_images: list = None, reference_video_path: str = None) -> dict:
    """Generate a 9-scene script using Gemini.

    Args:
        topic: Theme/topic for the video
        reference_images: Optional list of image file paths for character consistency
        reference_video_path: Optional video path for style imitation

    Returns:
        dict with "scenes" list of 9 dicts (narration, visual, character)
    """
    from google.genai import types

    client = _gemini_client()

    system_prompt = (
        "You are a professional short-video screenwriter. "
        "Given a topic, create exactly 9 connected scene segments for a short video. "
        "Return ONLY valid JSON (no markdown fences) with this structure:\n"
        '{"scenes": [\n'
        '  {"narration": "中文旁白文案", "visual": "English visual/scene description", '
        '"character": "English character appearance description"},\n'
        "  ... (9 items total)\n"
        "]}\n"
        "Each narration should be 1-3 sentences of engaging Chinese voiceover. "
        "Visual descriptions should be cinematic and detailed. "
        "Character descriptions must be consistent across all 9 scenes (same outfit, hair, features). "
        "The 9 scenes should tell a coherent mini-story."
    )

    # Build contents
    contents = []

    # If reference video provided, analyze it first
    if reference_video_path and os.path.exists(reference_video_path):
        system_prompt += (
            "\n\nA reference video is provided. Analyze its style, pacing, structure, "
            "and visual tone. Generate a script that matches this style closely."
        )
        with open(reference_video_path, "rb") as f:
            video_bytes = f.read()
        contents.append(types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"))

    # If reference images provided, include them
    if reference_images:
        system_prompt += (
            "\n\nReference images are provided for character consistency. "
            "Use these as visual reference for the character's appearance in all scenes."
        )
        for img_path in reference_images:
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
                contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

    contents.append(f"Topic: {topic}")

    logger.info(f"Generating 9-scene script for topic: {topic}")
    response = client.models.generate_content(
        model=MODEL_SCRIPT,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.9,
        ),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    result = json.loads(text)
    logger.info(f"Script generated: {len(result.get('scenes', []))} scenes")
    return result


def analyze_video_for_script(video_path: str) -> dict:
    """Analyze a reference video using Gemini to extract style/structure, then generate matching script.

    This uses Gemini 3 Pro to understand the video's pacing, style, and content,
    then generates a 9-scene script that matches.
    """
    from google.genai import types

    client = _gemini_client()

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    prompt = (
        "Analyze this video carefully. Extract:\n"
        "1. Overall style and tone\n"
        "2. Pacing and structure\n"
        "3. Visual style\n"
        "4. Narration style\n"
        "5. Scene breakdown\n\n"
        "Then generate a NEW 9-scene script that matches this style. "
        "Return ONLY valid JSON (no markdown fences) with this structure:\n"
        '{"analysis": {"style": "...", "pacing": "...", "tone": "..."}, '
        '"scenes": [\n'
        '  {"narration": "中文旁白文案", "visual": "English visual/scene description", '
        '"character": "English character appearance description"},\n'
        "  ... (9 items total)\n"
        "]}"
    )

    logger.info("Analyzing reference video with Gemini...")
    response = client.models.generate_content(
        model=MODEL_SCRIPT,
        contents=[
            types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=0.7),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)


def split_video_to_scenes(video_path: str) -> dict:
    """Upload video → extract audio → transcribe → split into 9 scenes.

    Uses ffmpeg to extract audio, then Gemini to transcribe and split.
    """
    from google.genai import types

    # Extract audio
    audio_path = video_path + ".audio.mp3"
    cmd = [FFMPEG_BIN, "-y", "-i", video_path, "-vn", "-acodec", "libmp3lame", "-q:a", "4", audio_path]
    subprocess.run(cmd, capture_output=True, timeout=120, check=True)

    client = _gemini_client()

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    prompt = (
        "Watch this video and transcribe all spoken content. "
        "Then split the content into exactly 9 scene segments. "
        "Return ONLY valid JSON:\n"
        '{"scenes": [\n'
        '  {"narration": "transcribed Chinese text for this segment", '
        '"visual": "description of what happens visually", '
        '"character": "character appearance description"},\n'
        "  ... (9 items)\n"
        "]}"
    )

    response = client.models.generate_content(
        model=MODEL_SCRIPT,
        contents=[
            types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=0.3),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    # Cleanup temp audio
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return json.loads(text)


# ─── Image Generation ───────────────────────────────────────────────

def generate_grid_image(scenes: list, output_path: str, reference_images: list = None) -> str:
    """Generate a 3x3 character-consistency reference grid.

    Args:
        scenes: list of 9 scene dicts
        output_path: where to save PNG
        reference_images: optional list of reference image paths for consistency

    Returns:
        output_path on success, empty string on failure.
    """
    from google.genai import types

    client = _gemini_client()

    grid_descriptions = []
    for i, s in enumerate(scenes):
        grid_descriptions.append(
            f"Panel {i+1} (row {i//3+1}, col {i%3+1}): {s['visual']}. "
            f"Character: {s['character']}"
        )

    prompt = (
        "Create a single 3x3 grid image (3 rows, 3 columns) with 9 panels. "
        "Each panel shows a scene from a short video. "
        "IMPORTANT: The main character must look EXACTLY the same in every panel "
        "(same face, hair, clothing, body type). "
        "The grid should have thin white borders between panels.\n\n"
        + "\n".join(grid_descriptions)
    )

    contents = []
    # Include reference images if provided
    if reference_images:
        prompt += "\n\nUse these reference images for the character's appearance:"
        for img_path in reference_images:
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
                contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

    contents.append(prompt)

    logger.info("Generating 3x3 character-consistency grid image...")
    response = client.models.generate_content(
        model=MODEL_IMAGE,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            logger.info(f"Grid image saved: {output_path} ({len(part.inline_data.data)} bytes)")
            return output_path

    logger.error("Gemini returned no grid image")
    return ""


# ─── Video Generation ───────────────────────────────────────────────

def generate_video_veo_prompt(prompt: str, output_path: str, image_path: str = None) -> str:
    """Generate a video clip using Veo 3.1 with optional first-frame image."""
    import requests
    from google.genai import types

    client = _gemini_client()

    kwargs = dict(model=MODEL_VIDEO, prompt=prompt)
    if image_path:
        with open(image_path, "rb") as f:
            kwargs["image"] = types.Image(image_bytes=f.read())

    logger.info(f"Veo 3.1 generating: {prompt[:100]}...")
    operation = client.models.generate_videos(**kwargs)

    max_wait = 600
    waited = 0
    while not operation.done:
        time.sleep(10)
        waited += 10
        if waited >= max_wait:
            logger.error("Veo video generation timed out")
            return ""
        operation = client.operations.get(operation=operation)
        logger.info(f"Veo in progress... ({waited}s)")

    if operation.result and operation.result.generated_videos:
        video_obj = operation.result.generated_videos[0].video
        video_data = getattr(video_obj, "video_bytes", None)
        if video_data:
            with open(output_path, "wb") as f:
                f.write(video_data)
            logger.info(f"Video saved (bytes): {output_path}")
            return output_path
        uri = getattr(video_obj, "uri", None)
        if uri:
            import google.auth
            import google.auth.transport.requests
            creds, _ = google.auth.default()
            creds.refresh(google.auth.transport.requests.Request())
            headers = {"Authorization": f"Bearer {creds.token}"}
            resp = requests.get(uri, headers=headers, timeout=120)
            if resp.status_code == 200 and len(resp.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"Video saved (uri): {output_path}")
                return output_path
            logger.error(f"URI download failed: {resp.status_code}")
            return ""
        logger.error("Veo returned video but no bytes or URI")
        return ""
    logger.error("Veo returned no videos")
    return ""


# ─── Helpers ─────────────────────────────────────────────────────────

def trim_silence(input_path: str, output_path: str, silence_thresh: float = -35.0, min_dur: float = 0.5) -> str:
    """Trim leading/trailing silence from video using ffmpeg silencedetect."""
    cmd = [
        FFMPEG_BIN, "-i", input_path,
        "-af", f"silencedetect=noise={silence_thresh}dB:d={min_dur}",
        "-f", "null", "-"
    ]
    logger.info(f"Detecting silence in {input_path}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    stderr = result.stderr

    silence_starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", stderr)]
    silence_ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", stderr)]

    dur_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", stderr)
    if not dur_match:
        logger.warning("Could not determine duration, returning original")
        return input_path
    total_dur = int(dur_match.group(1)) * 3600 + int(dur_match.group(2)) * 60 + float(dur_match.group(3))

    silence_pairs = list(zip(silence_starts, silence_ends))
    speech_start = 0.0
    for ss, se in silence_pairs:
        if ss <= 0.1:
            speech_start = se
            break

    speech_end = total_dur
    for ss, se in reversed(silence_pairs):
        if se >= total_dur - 0.1:
            speech_end = ss
            break

    if speech_start >= speech_end or (speech_end - speech_start) < 1.0:
        logger.warning("No meaningful speech found, returning original")
        return input_path

    trim_cmd = [
        FFMPEG_BIN, "-y", "-i", input_path,
        "-ss", str(max(0, speech_start - 0.1)),
        "-to", str(min(total_dur, speech_end + 0.1)),
        "-c:v", "copy", "-c:a", "aac",
        output_path,
    ]
    logger.info(f"Trimming: {speech_start:.1f}s - {speech_end:.1f}s (of {total_dur:.1f}s)")
    subprocess.run(trim_cmd, capture_output=True, timeout=120, check=True)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return output_path
    logger.warning("Trim output invalid, returning original")
    return input_path


def _extract_grid_cell(grid_path: str, index: int, output_path: str) -> str:
    """Extract a single cell from a 3x3 grid image. index: 0-8."""
    from PIL import Image
    img = Image.open(grid_path)
    w, h = img.size
    cell_w, cell_h = w // 3, h // 3
    row, col = divmod(index, 3)
    box = (col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h)
    cell = img.crop(box)
    cell.save(output_path)
    logger.info(f"Extracted grid cell {index} -> {output_path}")
    return output_path


def _extract_last_frame(video_path: str, output_path: str) -> str:
    """Extract the last frame of a video as an image."""
    cmd = [
        FFMPEG_BIN, "-y", "-sseof", "-0.1",
        "-i", video_path,
        "-frames:v", "1", "-q:v", "2",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, timeout=30, check=True)
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
        return output_path
    return ""


# ─── Full Pipeline ───────────────────────────────────────────────────

def generate_video_pipeline(
    topic: str,
    output_dir: str = None,
    reference_images: list = None,
    reference_video: str = None,
    use_keyframes: bool = False,
    progress_callback=None,
) -> str:
    """Complete pipeline: script → grid → 9 videos → trim → concat.

    Args:
        topic: Video topic/theme
        output_dir: Output directory (defaults to OUTPUT_DIR/timestamp)
        reference_images: List of image paths for character consistency
        reference_video: Path to reference video for style imitation
        use_keyframes: Use grid cells as first frames for Veo
        progress_callback: callable(step, total, message) for progress updates

    Returns:
        Path to final video file.
    """
    if output_dir is None:
        output_dir = os.path.join(OUTPUT_DIR, time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(output_dir, exist_ok=True)

    def _progress(step, total, msg):
        logger.info(f"[{step}/{total}] {msg}")
        if progress_callback:
            progress_callback(step, total, msg)

    # Step 1: Script
    _progress(1, 5, "Generating script...")
    if reference_video and os.path.exists(reference_video):
        script = analyze_video_for_script(reference_video)
    else:
        script = generate_script_gemini(topic, reference_images=reference_images, reference_video_path=reference_video)

    scenes = script["scenes"]
    if len(scenes) != 9:
        raise ValueError(f"Expected 9 scenes, got {len(scenes)}")

    with open(os.path.join(output_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    # Step 2: Grid image
    _progress(2, 5, "Generating character consistency grid...")
    grid_path = os.path.join(output_dir, "grid.png")
    generate_grid_image(scenes, grid_path, reference_images=reference_images)

    # Step 3: Video clips (concurrent)
    _progress(3, 5, "Generating 9 video clips (concurrent)...")

    def _gen_one_clip(i, scene):
        vid_path = os.path.join(output_dir, f"clip_{i:02d}_raw.mp4")
        if os.path.exists(vid_path) and os.path.getsize(vid_path) > 5000:
            logger.info(f"Clip {i+1}/9 exists, skipping")
            return (i, vid_path)

        prompt = (
            f"Scene {i+1}/9 of a short video. "
            f"Visual: {scene['visual']}. "
            f"Character: {scene['character']}. "
            f"The narrator speaks in Chinese: \"{scene['narration']}\" "
            f"Generate this as a cinematic video clip with the narrator's voice speaking the Chinese text."
        )

        first_frame = None
        if use_keyframes:
            cell_path = os.path.join(output_dir, f"cell_{i}.png")
            _extract_grid_cell(grid_path, i, cell_path)
            first_frame = cell_path

        result = generate_video_veo_prompt(prompt, vid_path, image_path=first_frame)
        return (i, result if result else None)

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        futures = {executor.submit(_gen_one_clip, i, s): i for i, s in enumerate(scenes)}
        for future in concurrent.futures.as_completed(futures):
            idx, path = future.result()
            results[idx] = path
            _progress(3, 5, f"Clip {idx+1}/9 {'done' if path else 'FAILED'}")

    raw_clips = [results[i] for i in range(9) if results.get(i)]
    if not raw_clips:
        raise RuntimeError("No clips generated")

    # Step 4: Trim silence
    _progress(4, 5, "Trimming silence...")
    trimmed_clips = []
    for i, clip in enumerate(raw_clips):
        trimmed = os.path.join(output_dir, f"clip_{i:02d}_trimmed.mp4")
        result = trim_silence(clip, trimmed)
        trimmed_clips.append(result)

    # Step 5: Concatenate
    _progress(5, 5, "Concatenating final video...")
    concat_list = os.path.join(output_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for clip in trimmed_clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    final_output = os.path.join(output_dir, "final_output.mp4")
    concat_cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-c:a", "aac",
        "-movflags", "+faststart",
        final_output,
    ]
    subprocess.run(concat_cmd, capture_output=True, timeout=300, check=True)

    if os.path.exists(final_output) and os.path.getsize(final_output) > 10000:
        logger.info(f"Pipeline complete! {final_output}")
        return final_output

    raise RuntimeError("Final concatenation failed")
