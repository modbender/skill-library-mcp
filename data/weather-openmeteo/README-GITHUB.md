# Weather-Open-Meteo

A weather query skill optimized for PowerShell environments with Chinese support, using the Open-Meteo API.

## Features

- ✅ **No API key required** - Completely free to use Open-Meteo API
- ✅ **PowerShell optimized** - Specifically designed for PowerShell environments
- ✅ **Bilingual support** - English and Chinese (Pinyin) versions
- ✅ **Multi-city support** - Built-in 10 major Chinese cities
- ✅ **Complete documentation** - Detailed usage and creation documentation

## Installation

### Via ClawHub CLI

```bash
# Search for the skill
clawhub search "weather openmeteo"

# Install the skill
clawhub install weather-openmeteo
```

### Manual Installation

```bash
# Navigate to skills directory
cd ~/.openclaw/workspace/skills

# Clone the repository
git clone https://github.com/yourusername/weather-openmeteo.git
```

## Usage

### Basic Commands

```powershell
# Navigate to skill directory
cd ~/.openclaw/workspace/skills/weather-openmeteo

# English version
.\weather-en.ps1 -City Shanghai

# Chinese version
.\weather-cn.ps1 -City Beijing
```

### Supported Cities

- Shanghai (上海)
- Beijing (北京)
- Guangzhou (广州)
- Shenzhen (深圳)
- Chengdu (成都)
- Hangzhou (杭州)
- Nanjing (南京)
- Wuhan (武汉)
- Xian (西安)
- Chongqing (重庆)

## File Structure

```
weather-openmeteo/
├── SKILL.md                 # Skill description
├── README.md                # Project overview
├── USAGE.md                 # Usage guide
├── QUICK-REF.md             # Quick reference
├── CREATION.md              # Creation process
├── SUMMARY.md               # Project summary
├── PROJECT-COMPLETE.md      # Project completion
├── PUBLISH.md               # Publishing instructions
├── README-GITHUB.md         # GitHub README
├── weather-en.ps1           # English version script
├── weather-cn.ps1           # Chinese version script
├── weather-simple.ps1       # Simplified version script
├── test-skill.ps1           # Test script
├── demo-en.ps1              # Demo script
├── example.ps1              # Usage examples
└── weather.ps1              # Complete script
```

## Technical Details

### API Endpoints

- **Base URL**: `https://api.open-meteo.com/v1/forecast`
- **Current weather**: `?current_weather=true`
- **7-day forecast**: `?daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum`

### Coordinate System

- **Coordinate system**: WGS84
- **Timezone**: Asia/Shanghai (GMT+8)
- **Update frequency**: Every 15 minutes

### Weather Codes

- **Range**: 0-99
- **Description**: Chinese and English
- **Coverage**: Clear, cloudy, rain, snow, fog, thunderstorm, etc.

## Testing

All tests passed:
- ✅ Script file check
- ✅ English version test
- ✅ Chinese version test
- ✅ API connection test
- ✅ Documentation completeness check

## Version Information

- **Version**: 1.0.0
- **Created**: March 3, 2026
- **Author**: OpenClaw User
- **License**: MIT License

## Changelog

### v1.0.0 (2026-03-03)
- Initial release
- Support for 10 major Chinese cities
- English and Chinese versions
- Complete documentation system

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - Free to use and modify