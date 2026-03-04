---
name: volcengine-video-generate
description: Using volcengine video_generate.py script to generate video, need to provide filename and prompt, optional provide first frame image (URL or local path).
license: Complete terms in LICENSE.txt
---

# Volcengine Video Generate

## Scenarios

When you need to generate a video based on a text description, use this skill. It supports controlling the starting frame of the video using a first frame image (either a URL or a local file path).

## Steps

1. Prepare the target filename (e.g., `output.mp4`) and a clear, specific `prompt`.
2. (Optional) Prepare the first frame image, which can be a HTTP URL or a local file path (the script will automatically convert it to Base64).
3. Run the script `python scripts/video_generate.py <filename> "<prompt>" [first_frame]`. Before running, navigate to the corresponding directory.
4. The script will output the video URL to the console and automatically download the video to the specified file.

## Authentication and Credentials

- First, it will try to read the `MODEL_VIDEO_API_KEY` or `ARK_API_KEY` environment variables.
- If not configured, it will try to use `VOLCENGINE_ACCESS_KEY` and `VOLCENGINE_SECRET_KEY` to get the Ark API Key.

## Output Format

- The console will output the generated video URL.
- The video file will be downloaded to the specified path.

## Examples

**Pure Text Generation:**

```bash
python scripts/video_generate.py "cat.mp4" "a lovely cat"
```

**With First Frame Image (URL):**

```bash
python scripts/video_generate.py "dog_run.mp4" "a lovely dog is running on the grass" "https://example.com/dog_start.png"
```

**带首帧图片生成（本地文件）：**

```bash
python scripts/video_generate.py "my_video.mp4" "a person is running in the street" "/path/to/local/image.jpg"
```
