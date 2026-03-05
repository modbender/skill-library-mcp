# yt-dlp Comprehensive Usage Guide

**Date:** December 17, 2025  
**Author:** Technical Documentation  
**Version:** 1.0.0

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Basic Usage](#3-basic-usage)
4. [Format Selection](#4-format-selection)
   - [Listing Formats](#41-listing-formats)
   - [Selecting Specific Quality](#42-selecting-specific-quality)
   - [Merging Video and Audio](#43-merging-video-and-audio)
5. [Audio Extraction](#5-audio-extraction)
6. [Playlists and Channels](#6-playlists-and-channels)
7. [Advanced Features](#7-advanced-features)
   - [Subtitles](#71-subtitles)
   - [Thumbnails and Metadata](#72-thumbnails-and-metadata)
   - [Authentication (Cookies)](#73-authentication-cookies)
   - [Output Templates](#74-output-templates)
8. [Configuration File](#8-configuration-file)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Introduction

`yt-dlp` is a command-line media downloader based on the now-inactive project `youtube-dlc`. It is currently the most active and feature-rich fork of `youtube-dl`, supporting thousands of sites beyond just YouTube, including Twitch, Vimeo, SoundCloud, and many others.

Key features include:

- **Speed**: Optimized download speeds.
- **SponsorBlock**: Integration to skip sponsored segments.
- **Format Control**: precise control over resolution, codecs, and containers.
- **Extensibility**: Active development and plugin support.

---

## 2. Installation

### General Installation (Python)

If you have Python installed, the recommended way to install `yt-dlp` is via pip:

```bash
pip install -U yt-dlp
```

### Binaries (Linux/macOS/Windows)

Standalone binaries are available if you do not wish to install Python dependencies.

**Linux:**

```bash
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

**macOS (via Homebrew):**

```bash
brew install yt-dlp
```

**Dependencies:**
For merging separate video and audio streams (essential for 1080p+ on YouTube), you **must** install `ffmpeg`.

---

## 3. Basic Usage

The simplest command downloads the best available quality for a single URL.

```bash
yt-dlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Note:** Always wrap URLs in quotes to prevent your shell from interpreting special characters (like `&` or `?`).

---

## 4. Format Selection

By default, `yt-dlp` attempts to download the best available video and audio and merge them. However, you often need specific resolutions or codecs.

### 4.1 Listing Formats

To see what formats are available for a video without downloading:

```bash
yt-dlp -F "URL"
```

This outputs a table with columns for **ID**, **EXT** (extension), **RESOLUTION**, **FPS**, **FILESIZE**, and **TBR** (bitrate).

### 4.2 Selecting Specific Quality

You can download a specific format by referring to its **ID code**:

```bash
yt-dlp -f 137 "URL"
```

To strictly download a specific resolution (e.g., best video no larger than 1080p):

```bash
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" "URL"
```

### 4.3 Merging Video and Audio

Modern streaming platforms separate high-quality video and audio streams. To get the best experience, you combine the best video (`bv`) and best audio (`ba`):

```bash
yt-dlp -f bv+ba --merge-output-format mp4 "URL"
```

*Note: This requires `ffmpeg` installed on your system.*

---

## 5. Audio Extraction

To download only the audio track and convert it to a common format (like MP3 or M4A).

**Extract to MP3:**

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 "URL"
```

- `-x`: Extract audio.
- `--audio-format`: Specify format (`mp3`, `aac`, `m4a`, `wav`, `opus`).
- `--audio-quality`: 0 is best, 9 is worst. Default is 5.

---

## 6. Playlists and Channels

`yt-dlp` handles playlists natively.

**Download entire playlist:**

```bash
yt-dlp "https://www.youtube.com/playlist?list=PL..."
```

**Download specific range (e.g., items 1, 2, 5, and 10 to 20):**

```bash
yt-dlp --playlist-items 1,2,5,10-20 "URL"
```

**Download only uploaded videos from a channel:**

```bash
yt-dlp "https://www.youtube.com/@ChannelName/videos"
```

---

## 7. Advanced Features

### 7.1 Subtitles

To list available subtitles:

```bash
yt-dlp --list-subs "URL"
```

To download English subtitles (auto-generated or manual) and embed them in the video:

```bash
yt-dlp --write-subs --sub-langs "en.*" --embed-subs "URL"
```

- `--write-auto-subs`: Include auto-generated captions if manual ones aren't available.

### 7.2 Thumbnails and Metadata

To write metadata to the video file and save the thumbnail to disk:

```bash
yt-dlp --add-metadata --write-thumbnail "URL"
```

To embed the thumbnail into the file (for music players, etc.):

```bash
yt-dlp --embed-thumbnail "URL"
```

### 7.3 Authentication (Cookies)

Some videos (age-restricted or premium) require login. The safest way is to import cookies from your browser.

```bash
yt-dlp --cookies-from-browser chrome "URL"
```

*Replace `chrome` with `firefox`, `brave`, `edge`, or `safari` as needed.*

### 7.4 Output Templates

Customize the filename of downloaded files.

```bash
yt-dlp -o "%(uploader)s - %(title)s [%(id)s].%(ext)s" "URL"
```

**Common placeholders:**

- `%(title)s`: Video title
- `%(uploader)s`: Channel name
- `%(upload_date)s`: Date (YYYYMMDD)
- `%(id)s`: Video ID

---

## 8. Configuration File

Instead of typing arguments every time, save them in a configuration file.
**Location:**

- **Linux/macOS:** `~/.config/yt-dlp/config`
- **Windows:** `%APPDATA%\yt-dlp\config.txt`

**Example Config:**

```text
# Always extract audio for music
--extract-audio
--audio-format mp3

# Save to Downloads folder
-o ~/Downloads/%(title)s.%(ext)s

# Embed metadata
--add-metadata
```

---

## 9. Troubleshooting

**"Unable to download webpage"**

- Ensure `yt-dlp` is up to date: `yt-dlp -U`
- Check your internet connection.

**"ffmpeg not found"**

- Install FFmpeg.
- On Ubuntu/Debian: `sudo apt install ffmpeg`
- On macOS: `brew install ffmpeg`

**"Sign in to confirm you’re not a bot"**

- Use the `--cookies-from-browser` option mentioned in section 7.3.
