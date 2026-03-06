# Timing & Audio Synchronization Guide

## Core Principle: VO Drives Duration

Each **frame on-screen for X seconds = length of its corresponding VO segment**

```
Timeline:
0:00 ━━━━━━━━━ Frame 1 (4.2s) ━━━━━━━━━ 4.2s
     └─ VO1.mp3: 4.2s plays underneath

4.2s ━━━━━━━━━ Frame 2 (3.8s) ━━━━━━━━━ 8.0s
     └─ VO2.mp3: 3.8s plays underneath

[Music plays continuously under all segments]
```

## Getting VO Duration

### Option 1: ffprobe (fast)
```bash
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1:novalue=1 \
  vo1.mp3
# Output: 4.2345
```

### Option 2: Python (scriptable)
```python
from pydub import AudioSegment

audio = AudioSegment.from_mp3("vo1.mp3")
duration_seconds = len(audio) / 1000.0
print(f"{duration_seconds:.1f}")
```

### Option 3: Manual (ffmpeg)
```bash
ffmpeg -i vo1.mp3 2>&1 | grep Duration
# Output: Duration: 00:00:04.23, ...
```

## Creating timing.json

### Basic Structure
```json
{
  "project": "Muffin Video",
  "output_resolution": "1080x1920",
  "output_fps": 24,
  "total_duration": 47.3,
  "segments": [
    {
      "id": "shot01",
      "frame": "frames/shot01-apartment.png",
      "vo_file": "vo/vo1-awakening.mp3",
      "vo_duration": 4.2,
      "vo_start": 0.0,
      "segment_start": 0.0,
      "segment_end": 4.2,
      "effect": "ken_burns",
      "music_start": 0.0
    },
    {
      "id": "shot02",
      "frame": "frames/shot02-macmini.png",
      "vo_file": "vo/vo2-power.mp3",
      "vo_duration": 3.8,
      "vo_start": 0.0,
      "segment_start": 4.2,
      "segment_end": 8.0,
      "effect": "ken_burns",
      "music_start": 4.2
    }
  ],
  "music": {
    "file": "music/ambient-cinematic.mp3",
    "duration": 47.3,
    "volume": -6.0
  }
}
```

### Fields Explained

| Field | Purpose |
|-------|---------|
| `id` | Unique scene identifier |
| `frame` | Path to frame/image file |
| `vo_file` | Path to VO MP3 for this segment |
| `vo_duration` | Length of VO file (seconds) |
| `vo_start` | Trim start within VO (0 = full file) |
| `segment_start` | When this segment starts in final video |
| `segment_end` | When segment ends (= start + vo_duration) |
| `effect` | Visual effect (ken_burns, static, fade, etc) |
| `music_start` | Music playback position when segment starts |

### Auto-Generate timing.json

```python
import json
from pathlib import Path
from pydub import AudioSegment

def generate_timing(frames_dir, vo_dir, music_file):
    """Generate timing.json from frame and VO files."""
    
    frames = sorted([f for f in Path(frames_dir).glob("*.png")])
    vo_files = sorted([f for f in Path(vo_dir).glob("*.mp3")])
    
    segments = []
    current_start = 0.0
    
    for i, (frame, vo_file) in enumerate(zip(frames, vo_files)):
        # Get VO duration
        audio = AudioSegment.from_mp3(str(vo_file))
        vo_duration = len(audio) / 1000.0
        
        segment = {
            "id": f"shot{i+1:02d}",
            "frame": str(frame),
            "vo_file": str(vo_file),
            "vo_duration": round(vo_duration, 1),
            "vo_start": 0.0,
            "segment_start": round(current_start, 1),
            "segment_end": round(current_start + vo_duration, 1),
            "effect": "ken_burns",
            "music_start": round(current_start, 1)
        }
        
        segments.append(segment)
        current_start += vo_duration
    
    # Get music duration
    music_audio = AudioSegment.from_mp3(music_file)
    music_duration = len(music_audio) / 1000.0
    
    timing = {
        "project": "Video Project",
        "output_resolution": "1080x1920",
        "output_fps": 24,
        "total_duration": round(current_start, 1),
        "segments": segments,
        "music": {
            "file": music_file,
            "duration": round(music_duration, 1),
            "volume": -6.0
        }
    }
    
    with open("timing.json", "w") as f:
        json.dump(timing, f, indent=2)
    
    return timing

# Usage
timing = generate_timing("frames/", "vo/", "music/ambient.mp3")
print(f"Total duration: {timing['total_duration']}s")
```

## Assembly with timing.json

### Ken Burns Effect (Static Frames)

Use `ffmpeg_assembler.py` to process timing.json:

```python
def build_ken_burns_video(timing_file, output_file):
    """Build video with Ken Burns effect based on timing.json"""
    
    import subprocess
    import json
    
    with open(timing_file) as f:
        timing = json.load(f)
    
    # Build ffmpeg filter for each segment
    filter_parts = []
    inputs = []
    
    for i, seg in enumerate(timing['segments']):
        # Input each frame
        frame_path = seg['frame']
        inputs.extend(["-loop", "1", "-t", str(seg['vo_duration']), 
                      "-i", frame_path])
        
        # Apply Ken Burns zoom effect
        # Zoom in slowly: z goes from 1 to 1.1 over segment duration
        zoom_speed = seg['vo_duration'] * 0.002  # Adjust for smoothness
        
        filter_parts.append(
            f"[{i}:v]scale=1080:1920,setsar=1,"
            f"zoompan=z='min(zoom+{zoom_speed},1.1)':"
            f"x='w/2-(w/2)*z':"
            f"y='h/2-(h/2)*z':"
            f"d={int(seg['vo_duration']*24)}:s=1080x1920[p{i}]"
        )
    
    # Add audio inputs
    vo_files = [seg['vo_file'] for seg in timing['segments']]
    music_file = timing['music']['file']
    
    # Build ffmpeg command
    cmd = ["ffmpeg"] + inputs + \
          ["-i", music_file] + \
          ["-i", " ".join(vo_files)]  # Concatenate VO
    
    # ... (complex filter building)
    
    subprocess.run(cmd)
```

## Overlapping Audio vs. Sequential

### Sequential (Recommended for VO)
Each segment = one VO track back-to-back
```
Music: ═══════════════════════════════════
VO:    ╔═══════╗╔════════╗╔═════╗
       └ vo1  └ vo2     └ vo3
```

### Overlapping (For crossfades)
Fade out VO1 while fading in VO2
```
Music: ═════════════════════════════════
VO:    ╔════════╗
       └ vo1 ╔════════╗
          └ vo2 ╔═════╗
             └ vo3
```

Use `ffmpeg -filter_complex "..." -t [duration]` with volume fade:
```bash
ffmpeg ... \
  -filter_complex "[0:a]volume=1[vo1]; \
                   [1:a]volume=0.5[vo2]; \
                   [2:a]amix=inputs=2:duration=first[a]" \
  ...
```

## Handling Timing Mismatches

### Problem: Music Duration ≠ Video Duration

**Solution**: Loop music or fade out

```bash
# Option 1: Loop music to match video
ffmpeg -i input_music.mp3 -t [video_duration] -c copy \
  output_music_looped.mp3

# Option 2: Fade out at end
ffmpeg -i input_music.mp3 \
  -af "afade=t=out:st=[fade_start]:d=2" \
  output_music_fadeout.mp3
```

### Problem: VO Segment Too Short/Long

Extend with silence or trim:

```bash
# Add 2 seconds of silence at end
ffmpeg -i vo.mp3 -af "apad=whole_dur=6" vo_extended.mp3

# Trim to exact duration
ffmpeg -i vo.mp3 -t 4.2 vo_trimmed.mp3
```

## Audio Levels

**Master mix levels** (for Premiere Pro import):
- Music: -6.0 dB
- VO: -3.0 dB (slightly louder)
- SFX: -9.0 dB (background)

Ensure final mix doesn't peak above -1.0 dB (headroom for mastering).

```bash
# Check audio levels
ffmpeg -i output.mp4 -af "ebur128=video=1" -f null -
```

## Quality Checklist

- [ ] All VO segments finalized (no re-recording mid-project)
- [ ] VO durations locked in timing.json
- [ ] Music track selected and licensed
- [ ] Frames/video clips ready for assembly
- [ ] timing.json created and validated
- [ ] Audio levels correct (no clipping)
- [ ] Test assembly with first 2-3 segments
- [ ] Full assembly run
- [ ] Raw video imported to Premiere Pro
- [ ] Color grade + VFX applied
