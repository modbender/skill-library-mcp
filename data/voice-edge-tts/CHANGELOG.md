# Changelog

## v1.10 (2026-02-24)

### Security Updates (安全更新)
- **Enterprise-grade security** - Full command injection protection
- Voice whitelist validation - only pre-approved voices can be used
- Replaced `exec()` with `spawn()` with array arguments
- Input sanitization for all parameters
- Shell execution disabled (`shell: false`)

### Features
- Streaming playback support (real-time audio while generating)
- Multiple voice support (Chinese, English, Japanese, Korean)
- Customizable rate, volume, and pitch

## v1.0.0 (2026-02-23)

### Added
- Initial release
- Basic TTS using edge-tts
- Multiple voice support
- Rate/volume/pitch adjustment
