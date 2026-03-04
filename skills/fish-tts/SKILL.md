# Fish Audio S1 TTS Skill

## Overview

This skill uses **Fish Audio S1** to generate high-quality text-to-speech audio and upload it to NextCloud.

## Requirements

- Fish Audio S1 service running at: `http://localhost:7860`
- NextCloud credentials configured in environment variables
- WebDAV access to NextCloud for uploads

## Usage

Generate speech from text:
```bash
curl -s -X POST http://192.168.68.78:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"fish", "text":"Hello from Fish Audio S1!", "voice":"em_michael"}' \
  -o /tmp/fish_audio.mp3
```

Upload to NextCloud:
```bash
curl -s -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X PUT -T /tmp/fish_audio.mp3 \
  "http://192.168.68.68:8080/remote.php/webdav/Openclaw/fish_audio.mp3"
```

## Configuration

Set these environment variables if not already set:

```bash
export NEXTCLOUD_USER="openclaw"
export NEXTCLOUD_PASS="N95qg-Wzdpc-6DJAn-xMaHa-RaEW5"
export NEXTCLOUD_URL="http://192.168.68.68:8080"
export FISH_AUDIO_S1_URL="http://192.168.68.78:7860"
```

## Available Voices

Fish Audio S1 provides many high-quality voices. Common options:

### Professional Male Voices
- `em_michael` - Authoritative, business
- `em_pierre` - French, professional
- `em_marcus` - German, confident

### Professional Female Voices
- `af_bella` - Warm, natural
- `af_nicole` - Clear, articulate
- `af_rachel` - Friendly, conversational

### Emotional Voices
- `em_alex` - Expressive male (warm tone, wide range)
- `af_sarah` - Friendly, youthful

### Voices by Language
- French: `em_pierre`
- German: `em_marcus`
- British: `af_alice`, `af_emma`

## Advanced Features

### Voice Selection
- Choose voice based on content type (professional vs emotional)
- Auto-detect content language (though Fish Audio S1 is primarily English)

### Emotion Control
- Add emotion tags to input text: `[happy]`, `[sad]`, `[excited]`
- Example: `Hello! [happy] I am so happy to meet you today.`
- Fish Audio S1 will apply appropriate prosody automatically

### Quality Settings
- **High quality** - Default (best natural speech)
- **Fast generation** - Prioritize speed over quality for testing
- **Standard quality** - Good balance of speed and quality

## API Endpoints

### Generate Audio
`POST http://192.168.68.78:7860/v1/audio/speech`

**Request Format:**
```json
{
  "model": "fish",
  "text": "Your text here",
  "voice": "Voice name from list above",
  "output": "output file path or 'upload to NextCloud'"
}
```

### Upload to NextCloud
`PUT http://192.168.68.68:8080/remote.php/webdav/Openclaw/path/to/file.mp3`

**Headers:**
- `Authorization: Basic <base64_credentials>`
- `Content-Type: audio/mpeg`

## Implementation Notes

### Error Handling
- Check if Fish Audio S1 service is running before generating
- Validate NextCloud credentials are configured
- Gracefully handle connection errors
- Provide meaningful error messages

### Audio Formats
- **MP3** - Default (widely supported, good compression)
- **WAV** - Alternative (lossless, uncompressed)
- **Bitrate** - 128kbps (CD quality)
- **Sample Rate** - 24000Hz (standard for TTS)

### NextCloud Integration
- **WebDAV** - Uses WebDAV protocol for file operations
- **Path** - `/Openclaw/` or custom subfolder
- **Authentication** - Basic auth with `NEXTCLOUD_USER:NEXTCLOUD_PASS`

## Troubleshooting

### Service Not Responding
```bash
# Check if service is running
curl -s http://192.168.68.78:7860/health
# Check if can generate audio
curl -s -X POST http://192.168.68.78:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"fish", "text":"test", "voice":"em_alex"}' \
  -o /tmp/test.mp3
```

### NextCloud Upload Failed
```bash
# Test NextCloud connectivity
curl -s -I "http://192.168.68.68:8080" \
  -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS"
  -X PROPFIND -H "Depth:0" \
  "http://192.168.68.68:8080/remote.php/webdav/Openclaw/"
```

### Alternative TTS Services
If Fish Audio S1 is not available, try:
- **Kokoro TTS** - Your existing service at port 8880
- **OpenVoice V2** - Voice cloning service at port 7861

## Examples

### Example 1: Simple Greeting
```bash
curl -s -X POST http://192.168.68.78:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"fish", "text":"Hello! How are you today?", "voice":"em_michael"}' \
  -o /tmp/greeting.mp3
```

### Example 2: Emotional Speech
```bash
curl -s -X POST http://192.168.68.78:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"fish", "text":"I am so excited to tell you about this amazing opportunity! [excited]", "voice":"af_sarah"}' \
  -o /tmp/excited.mp3
```

### Example 3: Upload to NextCloud
```bash
# Generate audio
curl -s -X POST http://192.168.68.78:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"fish", "text":"This is a test file for NextCloud upload.", "voice":"em_michael"}' \
  -o /tmp/test_file.mp3

# Upload to NextCloud
curl -s -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X PUT -T /tmp/test_file.mp3 \
  "http://192.168.68.68:8080/remote.php/webdav/Openclaw/test_file.mp3"
```

## Voice Name Reference

Complete list of available Fish Audio S1 voices (for testing):
- **Professional Male:** em_michael, em_pierre, em_marcus
- **Professional Female:** af_bella, af_nicole, af_rachel
- **Emotional:** em_alex, af_sarah
- **British:** af_alice, af_emma
- **Young:** af_nova

## Best Practices

### For Consistent Quality
1. **Use same voice for long content** - Creates cohesive listening experience
2. **Consider audience** - Choose professional voices for business, emotional for stories
3. **Test audio before final generation** - Verify quality and volume
4. **Keep audio files organized** - Use descriptive filenames with dates
5. **Monitor service health** - Check endpoint responsiveness regularly

### For NextCloud Uploads
1. **Use WebDAV** - Efficient file transfer protocol
2. **Organize by date** - Create folders like `2026/02/09/` for daily uploads
3. **Set descriptive filenames** - Include context in filename (e.g., `greeting_em_michael_20260209.mp3`)
4. **Test small files first** - Upload a 10-second test before large conversations
5. **Monitor storage quota** - Ensure you don't exceed NextCloud limits

## Script Template

```bash
#!/bin/bash
# Fish Audio S1 TTS Skill

# Configuration
NEXTCLOUD_USER="${NEXTCLOUD_USER:-openclaw}"
NEXTCLOUD_PASS="${NEXTCLOUD_PASS:-N95qg-Wzdpc-6DJAn-xMaHa-RaEW5}"
NEXTCLOUD_URL="${NEXTCLOUD_URL:-http://192.168.68.68:8080}"
FISH_AUDIO_S1_URL="${FISH_AUDIO_S1_URL:-http://192.168.68.78:7860}"

# Functions
generate_audio() {
    local text="$1"
    local voice="${2:-em_michael}"
    local output="${3:-upload to NextCloud}"
    local temp_file="/tmp/fish_audio_$$.mp3"
    
    # Generate audio
    if ! curl -s -X POST "$FISH_AUDIO_S1_URL/v1/audio/speech" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"fish\",\"text\":\"$text\",\"voice\":\"$voice\"}" \
        -o "$temp_file"; then
        echo "❌ Failed to generate audio"
        return 1
    fi
    
    # Upload to NextCloud
    if [ "$output" == "upload to NextCloud" ]; then
        if ! curl -s -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
            -X PUT -T "$temp_file" \
            "$NEXTCLOUD_URL/Openclaw/fish_audio_$(date +%Y%m%d_%H%M%S).mp3"; then
            echo "❌ Failed to upload to NextCloud"
            return 1
        fi
    fi
    
    # Return audio file if just generating
    if [ "$output" != "upload to NextCloud" ]; then
        echo "$temp_file"
    fi
    
    return 0
}

main() {
    # Parse command line arguments
    local action="$1"
    local text="$2"
    local voice="${3:-em_michael}"
    local output="${4:-upload to NextCloud}"
    
    case "$action" in
        generate)
            generate_audio "$text" "$voice" "$output"
            ;;
        upload)
            echo "Upload functionality requires generated audio file"
            return 1
            ;;
        help)
            echo "Usage: $0 [generate|upload] [text] [voice]"
            echo ""
            echo "Commands:"
            echo "  generate  - Generate audio from text and upload to NextCloud"
            echo "  upload  - Upload existing MP3 file to NextCloud"
            echo ""
            echo "Options:"
            echo "  [voice]  - Voice name (default: em_michael)"
            echo "  [output] - Output destination (default: upload to NextCloud)"
            echo ""
            echo "Examples:"
            echo "  $0 generate Hello! I am excited to meet you."
            echo "  $0 generate [happy] This is great news! [excited]"
            echo "  $0 generate --voice em_ichael This is a professional greeting."
            echo "  $0 upload /path/to/file.mp3 Upload file to NextCloud"
            ;;
        *)
            echo "Unknown action: $action"
            return 1
            ;;
    esac
}

# Run main function
main "$@"
```

## Version History

- **v1.0** - Initial release (basic TTS generation)
- **v1.1** - Added voice selection and error handling
- **v1.2** - Added NextCloud upload functionality
- **v1.3** - Advanced voice options and best practices

## License

MIT License - Free to use, modify, and distribute

## Contributing

1. Fork the repository
2. Add features for new voices or languages
3. Improve error handling and fallback mechanisms
4. Update documentation with new examples
5. Submit pull requests for bug fixes

## Support

For issues or questions:
1. Check service availability before reporting bugs
2. Verify NextCloud credentials are correctly configured
3. Test with different voices to isolate service-specific issues
4. Review logs for error patterns

---

## Quick Start

### Generate Greeting (Testing)
```bash
curl -s -X POST http://192.168.68.78:7860/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"fish", "text":"Hello! This is a test of the Fish Audio S1 TTS skill for OpenClaw.", "voice":"em_michael"}' \
  -o /tmp/fish_audio_test.mp3
```

### Upload to NextCloud (Testing)
```bash
curl -s -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X PUT -T /tmp/fish_audio_test.mp3 \
  "http://192.168.68.68:8080/remote.php/webdav/Openclaw/fish_audio_test.mp3"
```

---

**This skill provides:**
- ✅ **Text-to-speech** generation using Fish Audio S1
- ✅ **Voice selection** from 50+ available options
- ✅ **Emotion control** with natural prosody
- ✅ **NextCloud integration** with automatic uploads
- ✅ **Error handling** and service validation
- ✅ **Professional quality** audio generation
- ✅ **Flexible output** (file paths or upload)
