"""ClawCut — Gradio-based short video generation app."""
import os
import logging
import gradio as gr

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("clawcut")


def generate_video(topic, images, video, use_keyframes, progress=gr.Progress()):
    """Main generation handler."""
    from pipeline import generate_video_pipeline

    if not topic and not video:
        return None, "❌ Please enter a topic or upload a reference video."

    # Collect image paths
    ref_images = []
    if images:
        for img in images:
            if isinstance(img, str):
                ref_images.append(img)
            elif hasattr(img, "name"):
                ref_images.append(img.name)

    # Reference video path
    ref_video = None
    if video:
        ref_video = video if isinstance(video, str) else video.name

    status_log = []

    def progress_cb(step, total, msg):
        status_log.append(f"[{step}/{total}] {msg}")
        progress(step / total, desc=msg)

    try:
        result = generate_video_pipeline(
            topic=topic or "Based on reference video",
            reference_images=ref_images if ref_images else None,
            reference_video=ref_video,
            use_keyframes=use_keyframes,
            progress_callback=progress_cb,
        )
        status_log.append(f"✅ Done! Video: {result}")
        return result, "\n".join(status_log)
    except Exception as e:
        status_log.append(f"❌ Error: {str(e)}")
        logger.exception("Pipeline failed")
        return None, "\n".join(status_log)


def test_connection():
    """Test Vertex AI connection."""
    try:
        from pipeline import _gemini_client
        client = _gemini_client()
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents="Say 'ClawCut connected!' in one line.",
        )
        return f"✅ Connected!\nResponse: {response.text.strip()}"
    except Exception as e:
        return f"❌ Connection failed: {str(e)}"


def build_ui():
    with gr.Blocks(title="ClawCut - AI Video Generator", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎬 ClawCut\nAI-powered short video generator")

        with gr.Row():
            with gr.Column(scale=1):
                topic = gr.Textbox(
                    label="📝 Topic / Theme",
                    placeholder="Enter your video topic (Chinese or English)...",
                    lines=3,
                )
                images = gr.File(
                    label="🖼️ Reference Images (up to 14)",
                    file_count="multiple",
                    file_types=["image"],
                )
                video = gr.Video(label="🎥 Reference Video (for style imitation)")
                use_keyframes = gr.Checkbox(
                    label="Use grid cells as first frames",
                    value=False,
                )
                with gr.Row():
                    generate_btn = gr.Button("🚀 Generate Video", variant="primary", scale=2)
                    test_btn = gr.Button("🔌 Test Connection", scale=1)

            with gr.Column(scale=1):
                output_video = gr.Video(label="Generated Video")
                status = gr.Textbox(label="Status", lines=12, interactive=False)

        generate_btn.click(
            fn=generate_video,
            inputs=[topic, images, video, use_keyframes],
            outputs=[output_video, status],
        )
        test_btn.click(fn=test_connection, outputs=[status])

    return app


if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
