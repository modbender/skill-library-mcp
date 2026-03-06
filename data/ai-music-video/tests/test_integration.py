"""
Tier 2: Integration tests — minimal real API calls.
Each script tested independently with smallest possible input.
Cost: ~$0.04-0.10 per full run.
"""
import json
import os
import glob
import pytest
from conftest import run_script


class TestSunoMusicIntegration:
    """Test actual music generation with Suno API."""

    @pytest.mark.cheap
    def test_simple_generation(self, skill_env, work_dir):
        """Generate music in simple (non-custom) mode.
        Cost: ~10 Suno credits. Produces 2 tracks.
        """
        result = run_script("suno_music.sh", [
            "--prompt", "A short happy melody about sunshine and flowers",
            "--outdir", work_dir,
            "--timeout", "300",
        ], skill_env, timeout=360)

        assert result.returncode == 0, f"Script failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        assert "Generation complete" in result.stdout

        # Verify output files
        meta_path = os.path.join(work_dir, "music_meta.json")
        assert os.path.exists(meta_path), "music_meta.json not created"

        with open(meta_path) as f:
            meta = json.load(f)

        assert len(meta["tracks"]) >= 1, "Should have at least 1 track"
        assert meta["model"] == "V5"

        # Verify MP3 files downloaded
        mp3_files = glob.glob(os.path.join(work_dir, "track_*.mp3"))
        assert len(mp3_files) >= 1, f"No MP3 files found in {work_dir}"

        for mp3 in mp3_files:
            size = os.path.getsize(mp3)
            assert size > 100_000, f"MP3 too small ({size}B): {mp3}"

        # Verify track metadata
        for track in meta["tracks"]:
            assert track.get("duration", 0) > 0, "Track should have duration"
            assert track.get("audio_file"), "Track should have audio_file"

    @pytest.mark.cheap
    def test_custom_mode_generation(self, skill_env, work_dir):
        """Generate music in custom mode with style and title.
        Cost: ~10 Suno credits.
        """
        result = run_script("suno_music.sh", [
            "--prompt", "Walking through the rain\nSearching for your name\nEvery drop a memory",
            "--style", "indie acoustic, soft vocal, lo-fi",
            "--title", "Rain Memory",
            "--custom",
            "--outdir", work_dir,
            "--timeout", "300",
        ], skill_env, timeout=360)

        assert result.returncode == 0, f"Script failed:\nSTDERR: {result.stderr}"
        meta_path = os.path.join(work_dir, "music_meta.json")
        with open(meta_path) as f:
            meta = json.load(f)
        assert len(meta["tracks"]) >= 1


class TestGenVisualsIntegration:
    """Test actual image generation (cheapest: 1 image, low quality)."""

    @pytest.mark.cheap
    def test_single_image_openai(self, skill_env, work_dir, single_prompt_file):
        """Generate 1 image with OpenAI (low quality).
        Cost: ~$0.009.
        """
        result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", single_prompt_file,
            "--image-provider", "openai",
            "--image-quality", "low",
            "--image-size", "1024x1024",
            "--outdir", work_dir,
        ], skill_env, timeout=120)

        assert result.returncode == 0, f"Script failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

        # Verify image file created
        images = glob.glob(os.path.join(work_dir, "images", "scene_*.png"))
        assert len(images) == 1, f"Expected 1 image, got {len(images)}"
        assert os.path.getsize(images[0]) > 50_000, "Image too small"

        # Verify metadata
        meta_path = os.path.join(work_dir, "visuals_meta.json")
        assert os.path.exists(meta_path)
        with open(meta_path) as f:
            meta = json.load(f)
        assert meta["mode"] == "slideshow"
        assert len(meta["images"]) == 1
        assert meta["total_cost"] > 0

    @pytest.mark.cheap
    def test_multiple_images_openai(self, skill_env, work_dir, sample_prompts_file):
        """Generate 3 images with OpenAI (low quality).
        Cost: ~$0.027.
        """
        result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", sample_prompts_file,
            "--image-provider", "openai",
            "--image-quality", "low",
            "--image-size", "1024x1024",
            "--outdir", work_dir,
        ], skill_env, timeout=300)

        assert result.returncode == 0, f"STDERR: {result.stderr}"

        images = glob.glob(os.path.join(work_dir, "images", "scene_*.png"))
        assert len(images) == 3, f"Expected 3 images, got {len(images)}"


class TestAssembleIntegration:
    """Test ffmpeg assembly with synthetic inputs."""

    @pytest.mark.free
    def test_slideshow_assembly_synthetic(self, skill_env, work_dir):
        """Assemble slideshow from synthetic test inputs (no API cost).
        Uses ffmpeg-generated color images + silent audio.
        """
        # Arrange: create synthetic audio (10s silence)
        audio_path = os.path.join(work_dir, "test_audio.mp3")
        os.system(
            f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 '
            f'-q:a 9 "{audio_path}" 2>/dev/null'
        )
        assert os.path.exists(audio_path)

        # Arrange: create 3 synthetic images (solid color)
        img_dir = os.path.join(work_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            img_path = os.path.join(img_dir, f"scene_{i:03d}.png")
            os.system(
                f'ffmpeg -y -f lavfi -i color=c={color}:s=1024x1024:d=1 '
                f'-frames:v 1 "{img_path}" 2>/dev/null'
            )
            assert os.path.exists(img_path), f"Failed to create {img_path}"

        # Arrange: write visuals_meta.json
        meta = {"mode": "slideshow", "images": [], "videos": []}
        with open(os.path.join(work_dir, "visuals_meta.json"), "w") as f:
            json.dump(meta, f)

        output_path = os.path.join(work_dir, "test_mv.mp4")

        # Act
        result = run_script("assemble_mv.sh", [
            "--audio", audio_path,
            "--outdir", work_dir,
            "--output", output_path,
            "--mode", "slideshow",
            "--transition", "none",
        ], skill_env, timeout=60)

        # Assert
        assert result.returncode == 0, f"Assembly failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        assert os.path.exists(output_path), "Output video not created"
        assert os.path.getsize(output_path) > 10_000, "Output video too small"
        assert "Music Video Complete" in result.stdout

    @pytest.mark.free
    def test_slideshow_assembly_with_fade(self, skill_env, work_dir):
        """Assemble slideshow with crossfade transitions."""
        # Arrange
        audio_path = os.path.join(work_dir, "audio.mp3")
        os.system(
            f'ffmpeg -y -f lavfi -i "sine=f=440:d=12" '
            f'-q:a 9 "{audio_path}" 2>/dev/null'
        )

        img_dir = os.path.join(work_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        for i in range(3):
            img_path = os.path.join(img_dir, f"scene_{i:03d}.png")
            os.system(
                f'ffmpeg -y -f lavfi -i color=c=0x{i*80:02x}{i*40:02x}FF:s=1920x1080:d=1 '
                f'-frames:v 1 "{img_path}" 2>/dev/null'
            )

        meta = {"mode": "slideshow", "images": [], "videos": []}
        with open(os.path.join(work_dir, "visuals_meta.json"), "w") as f:
            json.dump(meta, f)

        output_path = os.path.join(work_dir, "fade_mv.mp4")

        # Act
        result = run_script("assemble_mv.sh", [
            "--audio", audio_path,
            "--outdir", work_dir,
            "--output", output_path,
            "--mode", "slideshow",
            "--transition", "fade",
        ], skill_env, timeout=60)

        # Assert
        assert result.returncode == 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        assert os.path.exists(output_path)
        size = os.path.getsize(output_path)
        assert size > 10_000, f"Output too small: {size}B"
