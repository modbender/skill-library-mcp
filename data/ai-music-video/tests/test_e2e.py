"""
Tier 3: Full end-to-end pipeline test.
Music generation → Visual generation → Assembly → Final video.
Cost: ~$0.05-0.15 (low quality, 3 scenes).

Run with: pytest test_e2e.py -v -s
"""
import json
import os
import glob
import time
import pytest
from conftest import run_script


@pytest.mark.expensive
class TestFullPipeline:
    """End-to-end: Suno music → OpenAI images → ffmpeg assembly."""

    @pytest.fixture
    def project_dir(self, work_dir):
        """Create a project directory with prompts."""
        pdir = os.path.join(work_dir, "mv_project")
        os.makedirs(pdir, exist_ok=True)

        # 3 scenes — minimal for E2E while testing the pipeline
        prompts = [
            "A warm sunrise over a calm ocean, golden light on gentle waves",
            "Cherry blossom petals falling through morning light in a peaceful garden",
            "A cozy window view of rain falling on a city street at twilight",
        ]
        with open(os.path.join(pdir, "prompts.json"), "w") as f:
            json.dump(prompts, f, ensure_ascii=False)

        return pdir

    def test_full_slideshow_pipeline(self, skill_env, project_dir):
        """
        Complete pipeline: music → slideshow images → assembly.
        
        Steps:
        1. Generate music with Suno V5 (simple mode)
        2. Generate 3 images with OpenAI (low quality, cheapest)
        3. Assemble into final MP4 with ffmpeg

        Expected cost: ~10 Suno credits + 3 × $0.009 = ~$0.027 API
        """
        costs = {}
        start_time = time.time()

        # ── Step 1: Generate Music ──
        print("\n" + "=" * 60)
        print("STEP 1: Music Generation (Suno V5)")
        print("=" * 60)

        music_result = run_script("suno_music.sh", [
            "--prompt", "A peaceful melody about morning sunshine and new beginnings",
            "--outdir", project_dir,
            "--timeout", "300",
        ], skill_env, timeout=360)

        assert music_result.returncode == 0, (
            f"Music generation failed:\n"
            f"STDOUT: {music_result.stdout}\n"
            f"STDERR: {music_result.stderr}"
        )

        # Verify music output
        music_meta_path = os.path.join(project_dir, "music_meta.json")
        assert os.path.exists(music_meta_path), "music_meta.json not found"

        with open(music_meta_path) as f:
            music_meta = json.load(f)

        tracks = music_meta["tracks"]
        assert len(tracks) >= 1, "No tracks generated"

        # Pick the first track for assembly
        audio_file = os.path.join(project_dir, tracks[0]["audio_file"])
        assert os.path.exists(audio_file), f"Audio file not found: {audio_file}"
        assert os.path.getsize(audio_file) > 100_000, "Audio file too small"

        costs["music"] = "~10 Suno credits"
        music_duration = tracks[0].get("duration", 0)
        print(f"  ✅ Music done: {tracks[0]['title']} ({music_duration:.0f}s)")
        print(f"  ✅ Tracks: {len(tracks)}")

        # ── Step 2: Generate Visuals ──
        print("\n" + "=" * 60)
        print("STEP 2: Visual Generation (OpenAI, low quality)")
        print("=" * 60)

        prompts_file = os.path.join(project_dir, "prompts.json")
        visuals_result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", prompts_file,
            "--image-provider", "openai",
            "--image-quality", "low",
            "--image-size", "1024x1024",
            "--outdir", project_dir,
        ], skill_env, timeout=300)

        assert visuals_result.returncode == 0, (
            f"Visual generation failed:\n"
            f"STDOUT: {visuals_result.stdout}\n"
            f"STDERR: {visuals_result.stderr}"
        )

        # Verify images
        images = sorted(glob.glob(os.path.join(project_dir, "images", "scene_*.png")))
        assert len(images) == 3, f"Expected 3 images, got {len(images)}"

        for img in images:
            size = os.path.getsize(img)
            assert size > 50_000, f"Image too small ({size}B): {img}"
            print(f"  ✅ {os.path.basename(img)} ({size // 1024}KB)")

        # Verify visuals metadata
        vis_meta_path = os.path.join(project_dir, "visuals_meta.json")
        assert os.path.exists(vis_meta_path)
        with open(vis_meta_path) as f:
            vis_meta = json.load(f)
        costs["visuals"] = f"${vis_meta.get('total_cost', 0):.3f}"

        # ── Step 3: Assemble ──
        print("\n" + "=" * 60)
        print("STEP 3: Assembly (ffmpeg)")
        print("=" * 60)

        output_path = os.path.join(project_dir, "final_mv.mp4")
        assembly_result = run_script("assemble_mv.sh", [
            "--audio", audio_file,
            "--outdir", project_dir,
            "--output", output_path,
            "--mode", "slideshow",
            "--transition", "fade",
        ], skill_env, timeout=120)

        assert assembly_result.returncode == 0, (
            f"Assembly failed:\n"
            f"STDOUT: {assembly_result.stdout}\n"
            f"STDERR: {assembly_result.stderr}"
        )

        # Verify final video
        assert os.path.exists(output_path), "Final video not created"
        video_size = os.path.getsize(output_path)
        assert video_size > 100_000, f"Final video too small ({video_size}B)"

        # ── Final Report ──
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("🎬 E2E TEST COMPLETE")
        print("=" * 60)
        print(f"  ⏱  Time: {elapsed:.0f}s")
        print(f"  🎵 Music: {tracks[0]['title']} ({music_duration:.0f}s, {len(tracks)} tracks)")
        print(f"  🎨 Images: {len(images)}")
        print(f"  📁 Video: {output_path} ({video_size // 1024}KB)")
        print(f"  💰 Cost: music={costs['music']}, visuals={costs['visuals']}")
        print("=" * 60)

        # Save test report
        report = {
            "test": "full_slideshow_pipeline",
            "status": "PASS",
            "elapsed_seconds": round(elapsed, 1),
            "music": {
                "model": music_meta["model"],
                "tracks": len(tracks),
                "duration": music_duration,
                "title": tracks[0].get("title", ""),
            },
            "visuals": {
                "mode": "slideshow",
                "provider": "openai",
                "quality": "low",
                "count": len(images),
                "cost": vis_meta.get("total_cost", 0),
            },
            "output": {
                "path": output_path,
                "size_bytes": video_size,
            },
            "costs": costs,
        }
        report_path = os.path.join(project_dir, "test_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n  📄 Report: {report_path}")


@pytest.mark.expensive
class TestFullPipelineCustomMusic:
    """E2E with custom mode music (lyrics + style)."""

    def test_custom_music_slideshow(self, skill_env, work_dir):
        """Custom lyrics → images → video."""
        pdir = os.path.join(work_dir, "custom_mv")
        os.makedirs(pdir, exist_ok=True)

        # Lyrics-derived scene prompts
        prompts = [
            "A person walking alone on a rainy city street at night, neon reflections",
            "Close-up of raindrops on a window, blurry city lights in background",
            "Two silhouettes meeting under a streetlight, warm amber glow",
        ]
        prompts_path = os.path.join(pdir, "prompts.json")
        with open(prompts_path, "w") as f:
            json.dump(prompts, f)

        # Step 1: Custom music
        music_result = run_script("suno_music.sh", [
            "--prompt", "빗소리 사이로\n너의 이름을 부르네\n이 거리 끝에서",
            "--style", "korean ballad, soft vocal, piano, rainy mood",
            "--title", "빗소리",
            "--custom",
            "--outdir", pdir,
            "--timeout", "300",
        ], skill_env, timeout=360)

        assert music_result.returncode == 0, f"STDERR: {music_result.stderr}"

        with open(os.path.join(pdir, "music_meta.json")) as f:
            meta = json.load(f)
        audio = os.path.join(pdir, meta["tracks"][0]["audio_file"])

        # Step 2: Images (low cost)
        vis_result = run_script("gen_visuals.sh", [
            "--mode", "slideshow",
            "--prompts-file", prompts_path,
            "--image-quality", "low",
            "--image-size", "1024x1024",
            "--outdir", pdir,
        ], skill_env, timeout=300)

        assert vis_result.returncode == 0, f"STDERR: {vis_result.stderr}"

        # Step 3: Assemble
        output = os.path.join(pdir, "빗소리_mv.mp4")
        asm_result = run_script("assemble_mv.sh", [
            "--audio", audio,
            "--outdir", pdir,
            "--output", output,
            "--transition", "fade",
        ], skill_env, timeout=120)

        assert asm_result.returncode == 0, f"STDERR: {asm_result.stderr}"
        assert os.path.exists(output)
        assert os.path.getsize(output) > 100_000
        print(f"\n🎬 Custom MV: {output} ({os.path.getsize(output) // 1024}KB)")
