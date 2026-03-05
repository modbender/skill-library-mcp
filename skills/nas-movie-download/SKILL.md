---
name: nas-movie-download
description: Search and download movies via Jackett and qBittorrent. Use when user wants to download movies or videos from torrent sources, search for specific movie titles, or manage movie downloads. Now includes automatic subtitle download support with SMB integration.
---

# NAS Movie Download

Automated movie downloading system using Jackett for torrent search and qBittorrent for download management.

**新功能：SMB 自动字幕下载！** 🎬 下载完成后自动通过 SMB 为视频下载并上传字幕。

## Configuration

### Environment Variables

Set these environment variables for the skill to function properly:

**Jackett Configuration:**
- `JACKETT_URL`: Jackett service URL (default: http://192.168.1.246:9117)
- `JACKETT_API_KEY`: Jackett API key (default: o5gp976vq8cm084cqkcv30av9v3e5jpy)

**qBittorrent Configuration:**
- `QB_URL`: qBittorrent Web UI URL (default: http://192.168.1.246:8888)
- `QB_USERNAME`: qBittorrent username (default: admin)
- `QB_PASSWORD`: qBittorrent password (default: adminadmin)

**SMB Configuration (for subtitle download):**
- `SMB_USERNAME`: SMB username (default: 13917908083)
- `SMB_PASSWORD`: SMB password (default: Roger0808)
- `SMB_SERVER`: SMB server IP (default: 192.168.1.246)
- `SMB_SHARE`: SMB share name (default: super8083)
- `SMB_PATH`: SMB download path (default: qb/downloads)

**Subtitle Configuration:**
- `SUBTITLE_LANGUAGES`: Default subtitle languages (default: zh,en)

### SMB Setup

SMB 配置已保存到 `config/smb.env`：
```bash
cat config/smb.env
```

### Indexer Setup

The skill works with Jackett indexers. Currently configured indexers:
- The Pirate Bay
- TheRARBG
- YTS

Ensure these indexers are enabled and configured in your Jackett installation for best results.

## Usage

### Search Movies

Search for movies without downloading:

```bash
scripts/jackett-search.sh -q "Inception"
scripts/jackett-search.sh -q "The Matrix"
scripts/jackett-search.sh -q "死期将至"  # Chinese movie names supported
```

### Download Movie Only

Download movie without subtitles:

```bash
scripts/download-movie.sh -q "The Matrix"
```

### Download with Automatic Subtitles via SMB 🆕

**完整流程：搜索 → 下载 → 自动下载字幕 → 上传到 SMB**

```bash
# 下载电影并自动通过 SMB 下载字幕
scripts/download-movie.sh -q "Young Sheldon" --subtitle

# 指定字幕语言
scripts/download-movie.sh -q "Community" --subtitle --lang zh,en
```

**参数说明：**
- `--subtitle`: 启用自动字幕下载（通过 SMB）
- `--lang`: 指定字幕语言（默认：zh,en）

### SMB Subtitle Download (Standalone)

为 NAS 上已下载的视频通过 SMB 下载字幕：

```bash
# 为单个视频下载字幕
python3 scripts/smb-download-subtitle.py -f "movie.mkv"

# 为整个目录下载字幕
python3 scripts/smb-download-subtitle.py -d "qb/downloads/Movie Folder"

# 批量处理所有视频
python3 scripts/smb-download-subtitle.py --all
```

## Workflow

### 完整下载流程

1. **搜索电影**: 使用 Jackett 搜索种子
2. **添加到 qBittorrent**: 自动添加最高质量的种子
3. **等待下载完成**: qBittorrent 下载视频到 NAS
4. **自动下载字幕**: 通过 SMB 连接到 NAS，为视频下载字幕
5. **上传字幕**: 将字幕文件上传到 NAS 对应位置

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Jackett    │───▶│ qBittorrent  │───▶│    NAS       │───▶│   字幕下载    │
│   搜索      │    │   下载       │    │  存储视频     │    │  SMB + subliminal│
└─────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

## Script Details

### jackett-search.sh

Search Jackett for torrents.

**Parameters:**
- `-q, --query`: Search query (required)
- `-u, --url`: Jackett URL (optional, uses env var)
- `-k, --api-key`: API key (optional, uses env var)

### qbittorrent-add.sh

Add torrent to qBittorrent.

**Parameters:**
- `-m, --magnet`: Magnet link (required)
- `-u, --url`: qBittorrent URL (optional, uses env var)
- `-n, --username`: Username (optional, uses env var)
- `-p, --password`: Password (optional, uses env var)

### download-movie.sh

One-click search, download, and subtitle fetching.

**Parameters:**
- `-q, --query`: Movie name (required)
- `-s, --subtitle`: Enable automatic subtitle download via SMB
- `-l, --lang`: Subtitle languages (default: zh,en)
- `--quality`: Quality preference (4k, 1080p, 720p, any)

### smb-download-subtitle.py 🆕

Download subtitles for videos on NAS via SMB.

**Parameters:**
- `-f, --file`: Single video filename (relative to SMB path)
- `-d, --directory`: Directory path (relative to SMB path)
- `-l, --lang`: Subtitle languages (default: zh,en)
- `--all`: Process all videos in SMB download folder

**Example:**
```bash
# Single video
python3 scripts/smb-download-subtitle.py -f "Lilo And Stitch 2025.mkv"

# Entire folder
python3 scripts/smb-download-subtitle.py -d "qb/downloads/Movie Folder"

# All videos
python3 scripts/smb-download-subtitle.py --all
```

**Features:**
- Connects to NAS via SMB
- Uses subliminal for subtitle search
- Downloads Chinese and English subtitles
- Uploads subtitles to corresponding video folders
- Skips existing subtitle files

## Tips and Best Practices

- **Use English movie names** for better search results
- **Check Jackett indexer status** if searches return no results
- **Monitor qBittorrent** to manage download progress
- **SMB subtitle download** works best for popular movies and TV shows
- **Test SMB connection** with `python3 scripts/smb-download-subtitle.py --test`
- **For TV series**: Use `--subtitle` flag to auto-download subtitles for all episodes

## Troubleshooting

### SMB Connection Failed

1. Verify SMB credentials in `config/smb.env`
2. Check NAS IP address: `ping 192.168.1.246`
3. Ensure SMB service is running on NAS
4. Verify network connectivity

### Subtitle Download Issues

1. **No subtitles found**: Try different language codes or the video may not have subtitles available
2. **subliminal not installed**: `pip3 install subliminal`
3. **SMB upload failed**: Check folder permissions on NAS

### Permission Issues

Ensure scripts have execute permissions:

```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

## Security Notes

- Keep SMB credentials secure in `config/smb.env`
- Use HTTPS connections when possible
- Consider setting up VPN for torrent traffic
- Monitor qBittorrent for unauthorized downloads

## Dependencies

- `curl`: For HTTP requests
- `jq`: For JSON parsing
- `python3` with `pysmb`: For SMB operations
- `subliminal`: For subtitle download

Install dependencies:
```bash
apt-get install curl jq python3 python3-pip
pip3 install pysmb subliminal
```

## Changelog

### v3.0 - 2025-02-23
- ✅ Added SMB subtitle download support
- ✅ New `smb-download-subtitle.py` script
- ✅ Integrated subtitle download into download workflow
- ✅ Automatic subtitle upload via SMB
- ✅ Support for Chinese and English subtitles

### v2.0 - 2025-02-17
- ✅ Added automatic subtitle download support
- ✅ New `subtitle-download.sh` script
- ✅ Updated `download-movie.sh` with `-s` and `-w` flags
- ✅ Support for OpenSubtitles API
- ✅ Multi-language subtitle support (zh-cn, en, ja, ko, etc.)
