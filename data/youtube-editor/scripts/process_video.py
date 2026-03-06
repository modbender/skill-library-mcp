# /// script
# dependencies = ["openai", "yt-dlp", "playwright", "rembg[cpu]", "pillow"]
# ///

import os
import argparse
import subprocess
import shutil
import re
import html
import ipaddress
from urllib.parse import urlparse
from datetime import datetime
from openai import OpenAI
from rembg import remove
from PIL import Image

def setup_env():
    """Load API keys from environment"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        exit(1)


def _is_private_or_local_host(hostname: str) -> bool:
    if not hostname:
        return True
    host = hostname.strip().lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


def validate_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in {"http", "https"}:
        return False

    host = (parsed.hostname or "").lower()
    if _is_private_or_local_host(host):
        return False

    allowed_hosts = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
    return host in allowed_hosts or host.endswith(".youtube.com")


def extract_audio(input_file, output_audio):
    print(f"🎬 Extracting audio from {input_file}...")
    cmd = [
        "ffmpeg", "-i", input_file, "-vn",
        "-acodec", "libmp3lame", "-q:a", "4", "-y",
        output_audio
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install ffmpeg.")
        exit(1)
    except subprocess.CalledProcessError:
        print("Error: FFmpeg failed to process the video.")
        exit(1)

def transcribe_audio(audio_file, output_srt, output_txt):
    print("🗣️ Transcribing audio with Whisper...")
    client = OpenAI()
    
    try:
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=f, 
                response_format="srt"
            )
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write(transcript)
            
        with open(audio_file, "rb") as f:
            txt = client.audio.transcriptions.create(
                model="whisper-1", 
                file=f, 
                response_format="text"
            )
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(txt)
        
        return txt
    except Exception as e:
        print(f"Error during transcription: {e}")
        exit(1)

def analyze_content(transcript_text):
    print("🧠 Analyzing content with GPT-4...")
    client = OpenAI()
    
    prompt = f"""
    Analyze the following video transcript and generate YouTube metadata in KOREAN.
    
    TRANSCRIPT:
    {transcript_text[:15000]}... (truncated)
    
    OUTPUT FORMAT:
    1. Title (Korean, Catchy, SEO-optimized, max 5 words for thumbnail text)
    2. Subtitle (Korean, Emotional hook, short)
    3. Description (Korean, Summary + Timestamps)
    4. Tags (Korean, Comma separated)
    5. Character Action (English description of action: "coding on a laptop", "holding a magnifying glass". Keep it simple.)
    
    IMPORTANT: All text output (Title, Subtitle, Description, Tags) MUST be in KOREAN.
    Character Action MUST be in English.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during analysis: {e}")
        return "Analysis failed."

def generate_image(prompt, output_file, input_image=None):
    """
    Generate AI image using nano-banana-pro skill.
    
    SECURITY NOTE: This function executes an external skill script.
    - Only runs if nano-banana-pro is installed by the user
    - Uses fixed, hardcoded script paths (not arbitrary user input)
    - Subprocess has 900s timeout to prevent hanging
    - API key is read from environment (NANO_BANANA_KEY)
    
    This is a legitimate cross-skill integration for AI image generation.
    Review nano-banana-pro skill separately before allowing this to run.
    """
    print(f"🎨 Generating image: {prompt}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # SECURITY: Fixed paths only - no user-supplied script execution
    possible_paths = [
        os.path.expanduser("~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py"),
        os.path.abspath(os.path.join(script_dir, "../../nano-banana-pro/scripts/generate_image.py")),
    ]

    skill_path = next((p for p in possible_paths if os.path.exists(p)), None)
    if not skill_path:
        print("⚠️ Nano Banana Pro skill not found.")
        return False

    cmd = [
        "uv", "run", skill_path,
        "--prompt", prompt,
        "--filename", output_file,
        "--resolution", "4K"
    ]
    
    # Image-to-Image support
    if input_image and os.path.exists(input_image):
        print(f"🖼️ Using input image for style transfer: {input_image}")
        cmd.extend(["--input-image", input_image])
    
    api_key = os.getenv("NANO_BANANA_KEY")
    if api_key:
        cmd.extend(["--api-key", api_key])
        
    try:
        # SECURITY: Timeout prevents runaway processes
        subprocess.run(cmd, check=True, timeout=900)
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Image generation failed.")
        return False

def remove_background(input_path, output_path):
    print(f"✂️ Removing background...")
    try:
        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                input_image = i.read()
                output_image = remove(input_image)
                o.write(output_image)
        return True
    except Exception as e:
        print(f"⚠️ Background removal failed: {e}")
        return False

def render_thumbnail(title, sub_title, author, avatar_path, output_file):
    print(f"🖼️ Rendering final thumbnail...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, "../assets/fonts/Paperlogy-ExtraBold.ttf")
    
    if not os.path.exists(font_path):
         font_family = "sans-serif"
         font_src = ""
         print("⚠️ Font file not found, using system font.")
    else:
         font_family = "Paperlogy"
         font_src = f"src: url('{font_path}') format('truetype');"

    if avatar_path and os.path.exists(avatar_path):
        avatar_html = f'<img src="{os.path.abspath(avatar_path)}" class="lobster-img">'
    else:
        avatar_html = ""

    # Escape user/model-generated text before embedding into HTML.
    title_safe = html.escape(title or "")
    subtitle_safe = html.escape(sub_title or "")
    author_safe = html.escape(author or "")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @font-face {{
            font-family: '{font_family}';
            {font_src}
        }}
        body {{
            margin: 0;
            padding: 0;
            width: 1280px;
            height: 720px;
            background-color: #000000;
            display: flex;
            font-family: '{font_family}', sans-serif;
            overflow: hidden;
            position: relative;
        }}
        .author {{
            position: absolute;
            top: 40px;
            left: 60px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 3px;
            z-index: 10;
        }}
        .text-container {{
            width: 65%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-left: 60px;
            z-index: 5;
        }}
        h3 {{
            color: #FFD700;
            font-size: 50px;
            margin: 0 0 10px 0;
            letter-spacing: -1px;
        }}
        h1 {{
            color: white;
            font-size: 140px;
            line-height: 1.0;
            margin: 0;
            letter-spacing: -4px;
            text-shadow: 10px 10px 30px rgba(0,0,0,0.8);
            word-break: keep-all;
        }}
        h2 {{
            color: #888;
            font-size: 40px;
            margin: 30px 0 0 0;
            font-weight: normal;
            letter-spacing: 0px;
        }}
        .lobster-img {{
            position: absolute;
            right: -50px;
            bottom: -50px;
            height: 85%;
            object-fit: contain;
            z-index: 1;
            filter: drop-shadow(0 0 50px rgba(255, 0, 0, 0.2));
        }}
        .overlay {{
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, rgba(0,0,0,0.9) 40%, rgba(0,0,0,0) 100%);
            z-index: 2;
        }}
    </style>
    </head>
    <body>
        <div class="author">{author_safe}</div>
        <div class="overlay"></div>
        <div class="text-container">
            <h3>{subtitle_safe}</h3>
            <h1>{title_safe}</h1>
            <h2>AI 파트너와 함께하는 생산성 혁명</h2>
        </div>
        {avatar_html}
    </body>
    </html>
    """
    
    html_path = output_file.replace(".png", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.screenshot(path=output_file)
            browser.close()
        print(f"✅ Thumbnail saved to {output_file}")
    except ImportError:
        print("⚠️ Playwright not installed. Run 'pip install playwright && playwright install chromium'")
    except Exception as e:
        print(f"⚠️ Screenshot failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="YouTube AI Editor")
    parser.add_argument("--input", help="Path to input video file")
    parser.add_argument("--url", help="YouTube URL to download")
    parser.add_argument("--author", default="Easy Working AI", help="Author name for thumbnail")
    parser.add_argument("--avatar", help="Path to avatar image (optional)")
    args = parser.parse_args()

    setup_env()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    video_path = args.input
    
    if args.url:
        print(f"📥 Downloading from URL: {args.url}")
        video_path = os.path.join(output_dir, "downloaded_video.mp4")
        if not validate_youtube_url(args.url):
            print("Error: Invalid or unsafe URL. Only YouTube URLs are allowed.")
            return
        try:
            import yt_dlp
            ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 'outtmpl': video_path, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([args.url])
        except Exception as e:
             print(f"Error: Download failed: {e}")
             return
    
    if not video_path or not os.path.exists(video_path):
        print("Error: Video file not found.")
        return

    audio_path = os.path.join(output_dir, "audio.mp3")
    extract_audio(video_path, audio_path)
    
    srt_path = os.path.join(output_dir, "subtitles.srt")
    txt_path = os.path.join(output_dir, "transcript.txt")
    transcript_text = transcribe_audio(audio_path, srt_path, txt_path)
    
    metadata = analyze_content(transcript_text)
    metadata_path = os.path.join(output_dir, "metadata.md")
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(metadata)
    
    # Parse metadata
    title_text = "AI VIDEO"
    sub_title = "혼자 일하지 마세요"
    char_action = None
    
    for line in metadata.split('\n'):
        if "Title" in line and "AI VIDEO" in title_text:
             parts = line.split(":", 1)
             if len(parts) > 1:
                 title_text = parts[1].strip().strip('"')
        elif "Subtitle" in line:
             parts = line.split(":", 1)
             if len(parts) > 1:
                 sub_title = parts[1].strip().strip('"')
        elif "Character Action" in line:
             parts = line.split(":", 1)
             if len(parts) > 1:
                 char_action = parts[1].strip()

    # Avatar Logic (Image-to-Image)
    avatar_final_path = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_avatar = os.path.join(script_dir, "../assets/avatar.png") # Flux Lobster

    # User provided avatar OR default avatar
    base_avatar = args.avatar if (args.avatar and os.path.exists(args.avatar)) else default_avatar
    
    if os.path.exists(base_avatar):
        if char_action:
            # Generate new pose using base avatar
            prompt = f"A cute pirate lobster character, {char_action}, adventurous anime style, white background, high quality 3d render. Keep the character design consistent with the input image."
            print(f"🤖 Generating character variant: {prompt}")
            gen_char_path = os.path.join(output_dir, "generated_character.png")
            
            # Pass input image for style consistency
            if generate_image(prompt, gen_char_path, input_image=base_avatar):
                avatar_path = gen_char_path
            else:
                avatar_path = base_avatar # Fallback
        else:
            avatar_path = base_avatar
            
        # Remove background
        avatar_final_path = os.path.join(output_dir, "avatar_transparent.png")
        if not remove_background(avatar_path, avatar_final_path):
            avatar_final_path = avatar_path 
    else:
        print("⚠️ No avatar found. Thumbnail will be text-only.")

    thumbnail_path = os.path.join(output_dir, "thumbnail.png")
    render_thumbnail(title_text, sub_title, args.author, avatar_final_path, thumbnail_path)

    print(f"✅ All done! Check the '{output_dir}' folder.")

if __name__ == "__main__":
    main()
