# FFmpeg & MoviePy Cheatsheet

This document provides a quick reference for commonly used commands and techniques in FFmpeg and MoviePy for video manipulation.

## FFmpeg

FFmpeg is a powerful command-line tool for handling multimedia data.

### Basic Commands

*   **Get video information:**
    ```bash
    ffmpeg -i input.mp4
    ```
*   **Convert video format:**
    ```bash
    ffmpeg -i input.mov output.mp4
    ```
*   **Trim a video:**
    ```bash
    ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 -c copy output.mp4
    ```
*   **Add a watermark:**
    ```bash
    ffmpeg -i input.mp4 -i watermark.png -filter_complex "overlay=10:10" output.mp4
    ```

## MoviePy

MoviePy is a Python library for video editing.

### Core Concepts

*   **Clips**: The fundamental objects in MoviePy. They can be `VideoClip`, `AudioClip`, or `ImageClip`.
*   **Composition**: Clips can be combined using `CompositeVideoClip`.
*   **Effects (fx)**: MoviePy provides a range of effects in the `moviepy.video.fx.all` module.

### Code Snippets

*   **Load a video file:**
    ```python
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip("input.mp4")
    ```
*   **Create a text clip:**
    ```python
    from moviepy.editor import TextClip
    txt_clip = TextClip("Hello World", fontsize=70, color='white')
    ```
*   **Concatenate clips:**
    ```python
    from moviepy.editor import concatenate_videoclips
    final_clip = concatenate_videoclips([clip1, clip2])
    ```
*   **Write to file:**
    ```python
    final_clip.write_videofile("output.mp4")
    ```
