"""
Tier 1: Dry-run tests — no API calls, no cost.
Tests argument parsing, cost estimation, dry-run output.
"""
import json
import os
import pytest
from conftest import run_script, SCRIPTS_DIR


class TestSunoMusicDryRun:
    """suno_music.sh dry-run tests."""

    @pytest.mark.free
    def test_dry_run_shows_cost_estimate(self, skill_env, work_dir):
        """Dry-run should show cost estimate and exit 0."""
        result = run_script("suno_music.sh", [
            "--prompt", "test lyrics",
            "--style", "pop",
            "--title", "Test Song",
            "--custom",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Cost Estimate" in result.stdout
        assert "DRY_RUN" in result.stdout
        assert "Model: V4_5ALL" in result.stdout

    @pytest.mark.free
    def test_dry_run_custom_model(self, skill_env, work_dir):
        """Dry-run with non-default model."""
        result = run_script("suno_music.sh", [
            "--prompt", "test",
            "--model", "V4_5ALL",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Model: V4_5ALL" in result.stdout

    @pytest.mark.free
    def test_dry_run_instrumental_flag(self, skill_env, work_dir):
        """Dry-run with instrumental mode."""
        result = run_script("suno_music.sh", [
            "--prompt", "ambient electronic",
            "--instrumental",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Instrumental: true" in result.stdout

    @pytest.mark.free
    def test_dry_run_with_persona_id(self, skill_env, work_dir):
        """Dry-run with persona-id shows persona info."""
        result = run_script("suno_music.sh", [
            "--prompt", "coding vibe music",
            "--persona-id", "persona_abc123",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Persona: persona_abc123" in result.stdout

    @pytest.mark.free
    def test_dry_run_create_persona_flag(self, skill_env, work_dir):
        """Dry-run with create-persona shows the flag."""
        result = run_script("suno_music.sh", [
            "--prompt", "test track",
            "--create-persona",
            "--persona-name", "Dev Singer",
            "--persona-desc", "Coding music vocalist",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Create Persona: true" in result.stdout

    @pytest.mark.free
    def test_missing_prompt_errors(self, skill_env, work_dir):
        """Should error when --prompt is missing."""
        result = run_script("suno_music.sh", [
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode != 0
        assert "prompt" in result.stderr.lower()

    @pytest.mark.free
    def test_dry_run_music_video_flag(self, skill_env, work_dir):
        """Dry-run with --music-video flag."""
        result = run_script("suno_music.sh", [
            "--prompt", "test",
            "--music-video",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Music Video: true" in result.stdout

    @pytest.mark.free
    def test_dry_run_vocal_gender(self, skill_env, work_dir):
        """Dry-run with --vocal-gender option."""
        result = run_script("suno_music.sh", [
            "--prompt", "test song",
            "--vocal-gender", "f",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "DRY_RUN" in result.stdout

    @pytest.mark.free
    def test_dry_run_negative_tags(self, skill_env, work_dir):
        """Dry-run with --negative-tags option."""
        result = run_script("suno_music.sh", [
            "--prompt", "chill vibes",
            "--negative-tags", "Heavy Metal, Screaming",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "DRY_RUN" in result.stdout

    @pytest.mark.free
    def test_missing_api_key_errors(self, work_dir):
        """Should error when SUNO_API_KEY is not set."""
        env = os.environ.copy()
        env.pop("SUNO_API_KEY", None)
        result = run_script("suno_music.sh", [
            "--prompt", "test",
            "--dry-run",
        ], env)

        assert result.returncode != 0
        assert "SUNO_API_KEY" in result.stderr


class TestGenVisualsDryRun:
    """gen_visuals.sh dry-run tests."""

    @pytest.mark.free
    def test_slideshow_dry_run(self, skill_env, work_dir, sample_prompts_file):
        """Slideshow mode dry-run with 3 scenes."""
        result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", sample_prompts_file,
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Cost Estimate" in result.stdout
        assert "Images: 3" in result.stdout
        # Check cost estimate JSON was written
        est_path = os.path.join(work_dir, "cost_estimate.json")
        assert os.path.exists(est_path)
        with open(est_path) as f:
            est = json.load(f)
        assert est["mode"] == "slideshow"
        assert est["num_images"] == 3
        assert est["num_videos"] == 0

    @pytest.mark.free
    def test_video_dry_run(self, skill_env, work_dir, sample_prompts_file):
        """Video mode dry-run."""
        result = run_script("gen_visuals.sh", [
            "--mode", "video",
            "--prompts-file", sample_prompts_file,
            "--video-provider", "seedance-lite",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        est_path = os.path.join(work_dir, "cost_estimate.json")
        with open(est_path) as f:
            est = json.load(f)
        assert est["num_images"] == 0
        assert est["num_videos"] == 3
        assert est["video_cost_each"] == 0.14  # seedance-lite price

    @pytest.mark.free
    def test_hybrid_dry_run(self, skill_env, work_dir, sample_prompts_file):
        """Hybrid mode splits scenes between image and video."""
        result = run_script("gen_visuals.sh", [
            "--mode", "hybrid",
            "--prompts-file", sample_prompts_file,
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        est_path = os.path.join(work_dir, "cost_estimate.json")
        with open(est_path) as f:
            est = json.load(f)
        assert est["num_images"] + est["num_videos"] == 3
        assert est["num_images"] == 1  # 3//2 = 1
        assert est["num_videos"] == 2  # 3 - 1 = 2

    @pytest.mark.free
    def test_missing_prompts_file_errors(self, skill_env, work_dir):
        """Should error when prompts file doesn't exist."""
        result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", "/nonexistent/prompts.json",
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode != 0
        assert "prompts-file" in result.stderr.lower()

    @pytest.mark.free
    @pytest.mark.parametrize("provider,model,quality,size,expected_cost", [
        # Token-based pricing (Feb 2026):
        # gpt-image-1-mini: text_in=$2/1M, img_out=$8/1M
        # gpt-image-1:      text_in=$5/1M, img_out=$40/1M
        # Output tokens: low=272, medium=1056, high=4160
        # Size multiplier: 1024x1024=1x, others=1.5x
        # Cost = (80*text_rate + output_tokens*img_rate) / 1M
        ("openai", "gpt-image-1-mini", "low", "1024x1024", 0.002336),
        ("openai", "gpt-image-1-mini", "medium", "1024x1024", 0.008608),
        ("openai", "gpt-image-1-mini", "medium", "1536x1024", 0.012800),
        ("openai", "gpt-image-1", "medium", "1024x1024", 0.042640),
        ("openai", "gpt-image-1", "medium", "1536x1024", 0.063760),
        ("openai", "gpt-image-1", "high", "1024x1024", 0.166800),
        ("google-together", "gpt-image-1-mini", "medium", "1536x1024", 0.040),
    ])
    def test_image_cost_accuracy(self, skill_env, work_dir, single_prompt_file,
                                  provider, model, quality, size, expected_cost):
        """Verify token-based cost calculation matches expected values."""
        result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", single_prompt_file,
            "--image-provider", provider,
            "--image-model", model,
            "--image-quality", quality,
            "--image-size", size,
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        est_path = os.path.join(work_dir, "cost_estimate.json")
        with open(est_path) as f:
            est = json.load(f)
        assert abs(est["image_cost_each"] - expected_cost) < 0.0001, \
            f"Expected ~{expected_cost}, got {est['image_cost_each']}"

    @pytest.mark.free
    @pytest.mark.parametrize("provider,expected_cost", [
        ("sora", 0.80),
        ("sora-pro", 2.40),
        ("seedance-lite", 0.14),
        ("seedance-pro", 0.57),
        ("veo-fast", 0.80),
        ("veo-audio", 3.20),
    ])
    def test_video_cost_accuracy(self, skill_env, work_dir, single_prompt_file,
                                  provider, expected_cost):
        """Verify video cost per provider."""
        result = run_script("gen_visuals.sh", [
            "--mode", "video",
            "--prompts-file", single_prompt_file,
            "--video-provider", provider,
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        est_path = os.path.join(work_dir, "cost_estimate.json")
        with open(est_path) as f:
            est = json.load(f)
        assert est["video_cost_each"] == expected_cost


class TestAssembleDryRun:
    """assemble_mv.sh dry-run tests."""

    @pytest.mark.free
    def test_dry_run_with_audio(self, skill_env, work_dir):
        """Dry-run should describe what it would do."""
        # Create a short silent audio file for testing
        audio_path = os.path.join(work_dir, "test.mp3")
        os.system(
            f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 '
            f'-q:a 9 "{audio_path}" 2>/dev/null'
        )
        # Create dummy image files
        img_dir = os.path.join(work_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        for i in range(3):
            os.system(
                f'ffmpeg -y -f lavfi -i color=c=blue:s=1024x1024:d=1 '
                f'"{img_dir}/scene_{i:03d}.png" 2>/dev/null'
            )

        result = run_script("assemble_mv.sh", [
            "--audio", audio_path,
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "DRY_RUN" in result.stdout
        assert "3 images" in result.stdout

    @pytest.mark.free
    def test_auto_detect_lyrics_srt(self, skill_env, work_dir):
        """Should auto-detect lyrics.srt in outdir."""
        audio_path = os.path.join(work_dir, "test.mp3")
        os.system(
            f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 '
            f'-q:a 9 "{audio_path}" 2>/dev/null'
        )
        img_dir = os.path.join(work_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        for i in range(2):
            os.system(
                f'ffmpeg -y -f lavfi -i color=c=blue:s=1024x1024:d=1 '
                f'"{img_dir}/scene_{i:03d}.png" 2>/dev/null'
            )
        # Create lyrics.srt
        srt_path = os.path.join(work_dir, "lyrics.srt")
        with open(srt_path, "w") as f:
            f.write("1\n00:00:01,000 --> 00:00:03,000\nTest lyric\n\n")

        result = run_script("assemble_mv.sh", [
            "--audio", audio_path,
            "--outdir", work_dir,
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Auto-detected lyrics" in result.stdout

    @pytest.mark.free
    def test_no_subtitle_flag(self, skill_env, work_dir):
        """--no-subtitle should suppress auto-detection."""
        audio_path = os.path.join(work_dir, "test.mp3")
        os.system(
            f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 '
            f'-q:a 9 "{audio_path}" 2>/dev/null'
        )
        img_dir = os.path.join(work_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        os.system(
            f'ffmpeg -y -f lavfi -i color=c=blue:s=1024x1024:d=1 '
            f'"{img_dir}/scene_000.png" 2>/dev/null'
        )
        srt_path = os.path.join(work_dir, "lyrics.srt")
        with open(srt_path, "w") as f:
            f.write("1\n00:00:01,000 --> 00:00:03,000\nTest\n\n")

        result = run_script("assemble_mv.sh", [
            "--audio", audio_path,
            "--outdir", work_dir,
            "--no-subtitle",
            "--dry-run",
        ], skill_env)

        assert result.returncode == 0
        assert "Auto-detected lyrics" not in result.stdout

    @pytest.mark.free
    def test_missing_audio_errors(self, skill_env, work_dir):
        """Should error when audio file missing."""
        result = run_script("assemble_mv.sh", [
            "--audio", "/nonexistent/audio.mp3",
            "--outdir", work_dir,
        ], skill_env)

        assert result.returncode != 0
        assert "audio" in result.stderr.lower()
