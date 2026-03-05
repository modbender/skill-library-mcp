# YouTube Download Patterns & Best Practices

## Common Use Cases

### Music Extraction
- **Purpose**: Convert YouTube music videos to MP3 files
- **Best quality**: Use `--audio` flag (default) for highest quality MP3
- **Naming**: Let yt-dlp auto-name or specify custom names
- **Batch**: Use playlists for album downloads

### Video Archiving
- **Purpose**: Save videos for offline viewing or backup
- **Quality options**: 
  - `best` - Highest available quality (default)
  - `720p` - Good balance of quality/size
  - `480p` - Smaller files, decent quality
- **Format**: MP4 for maximum compatibility

### Educational Content
- **Mixed approach**: Download video for visual content, extract audio for reviewing
- **Organization**: Use output directory structure
- **Playlists**: Course playlists work well with batch download

### Podcast/Audio Content
- **Audio-only**: Always use `--audio` flag
- **Quality**: Default MP3 quality is usually sufficient
- **Batch processing**: Great for podcast series

## Quality Guidelines

### Audio Quality
- **Default**: Automatically selects best available audio
- **File size**: MP3 compression balances quality vs size
- **Use case**: Perfect for music, podcasts, lectures

### Video Quality Options
- **best**: Highest resolution/bitrate available (can be large)
- **720p**: HD quality, good for most content (balanced)
- **480p**: SD quality, smaller files, mobile-friendly
- **360p**: Low quality, very small files, basic viewing

## File Management Tips

### Naming Conventions
- **Auto-naming**: Uses video title (default)
- **Custom naming**: Specify output filename for single downloads
- **Batch naming**: Includes playlist index numbers automatically

### Organization Strategies
```bash
# By category
-o ~/Downloads/Music
-o ~/Downloads/Tutorials  
-o ~/Downloads/Entertainment

# By date
-o ~/Downloads/$(date +%Y-%m-%d)

# By playlist name
-o ~/Downloads/Playlist_Name
```

### Storage Considerations
- **Audio files**: ~3-10MB per song (MP3)
- **720p videos**: ~50-200MB per video
- **1080p+ videos**: 200MB+ per video
- **Plan accordingly** for batch downloads

## Troubleshooting

### Common Issues
- **"Video unavailable"**: Content may be private/deleted
- **"No suitable formats"**: Try different quality settings
- **"Download too slow"**: Network connectivity issues
- **"Format not supported"**: Rare formats may need conversion

### Error Recovery
- **Partial downloads**: yt-dlp auto-resumes interrupted downloads
- **Failed items in batch**: Continues with remaining items
- **Network issues**: Retry the same command

### Legal Considerations
- **Personal use**: Generally acceptable for offline viewing
- **Respect copyrights**: Don't distribute copyrighted content
- **Terms of service**: Follow YouTube's terms of service
- **Fair use**: Consider fair use guidelines for educational content

## Advanced Usage

### Playlist Range Selection
```bash
# Items 5-10 only
--start 5 --end 10

# From item 20 to end
--start 20

# First 50 items only  
--max-downloads 50
```

### Quality-Size Optimization
- **For mobile**: Use 480p or 360p
- **For archiving**: Use best quality
- **For sharing**: Balance quality/size at 720p
- **For audio**: Always extract audio for music content

### Batch File Processing
Create a `urls.txt` file with one URL per line:
```
https://www.youtube.com/watch?v=video1
https://www.youtube.com/watch?v=video2
https://www.youtube.com/watch?v=video3
```

Then use: `batch_download.sh -f urls.txt`