# Documentation - Binance Enhanced Skill

## 📚 Language Versions

### 🇬🇧 English Documentation (Primary)
- **[README.md](README.md)** - Complete English documentation (main)
- **[SKILL.md](SKILL.md)** - Detailed skill documentation (English, main)
- **[FAQ.md](FAQ.md)** - Frequently Asked Questions (English)
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - Best practices guide (English)

### 🇷🇺 Русская документация  
- **[README_RU.md](README_RU.md)** - Полная русская документация
- **[SKILL_RU.md](SKILL_RU.md)** - Детальная документация навыка (русский)
- **[FAQ.md](FAQ.md)** - Часто задаваемые вопросы (английский)
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - Руководство по best practices (английский)

## 🎯 Quick Start Guides

### English Quick Start:
```bash
# 1. Clone repository
git clone https://github.com/s7cret/binance-enhanced.git
cd binance-enhanced

# 2. Install dependencies
./install.sh

# 3. Configure environment
cp templates/.env.example .env
# Edit .env with your API keys

# 4. Start services
docker-compose up -d
```

### Русский Quick Start:
```bash
# 1. Клонировать репозиторий
git clone https://github.com/s7cret/binance-enhanced.git
cd binance-enhanced

# 2. Установить зависимости
./install.sh

# 3. Настроить окружение
cp templates/.env.example .env
# Отредактировать .env с вашими API ключами

# 4. Запустить сервисы
docker-compose up -d
```

## 📖 Detailed Documentation

### API Documentation:
- **OpenAPI/Swagger**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Postman Collection**: `docs/postman_collection.json`

### Configuration Guides:
- **[Configuration Guide](docs/CONFIGURATION.md)** - Detailed configuration options
- **[Security Setup](docs/SECURITY_SETUP.md)** - Security configuration guide
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deployment options

### Tutorials:
- **[Getting Started](docs/TUTORIAL_GETTING_STARTED.md)** - First steps tutorial
- **[Trading Strategies](docs/TUTORIAL_STRATEGIES.md)** - How to use trading strategies
- **[Telegram Bot](docs/TUTORIAL_TELEGRAM_BOT.md)** - Telegram bot setup and usage

## 🔧 Development Documentation

### For Developers:
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System architecture
- **[API Reference](docs/API_REFERENCE.md)** - Complete API reference
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute

### For Integrators:
- **[OpenClaw Integration](docs/OPENCLAW_INTEGRATION.md)** - OpenClaw integration guide
- **[Webhook API](docs/WEBHOOK_API.md)** - Webhook integration
- **[Custom Strategies](docs/CUSTOM_STRATEGIES.md)** - Creating custom strategies

## 🌐 Internationalization

### Supported Languages:
- **English** (primary) - Full documentation and interface
- **Russian** - Full documentation and natural language commands
- **Interface**: Bilingual (English/Russian) command parser
- **Documentation**: Separate files for each language

### Language Switching:
```python
# Set language preference
export LANGUAGE=en  # English
export LANGUAGE=ru  # Russian

# Or in configuration
language: "en"  # or "ru"
```

## 📊 Diagrams and Schemas

### Architecture Diagrams:
- `docs/diagrams/architecture.png` - System architecture
- `docs/diagrams/data_flow.png` - Data flow diagram
- `docs/diagrams/security.png` - Security architecture

### API Schemas:
- `docs/schemas/openapi.yaml` - OpenAPI specification
- `docs/schemas/database.sql` - Database schema
- `docs/schemas/config_schema.json` - Configuration schema

## 🎥 Video Tutorials

### English Tutorials:
- [Getting Started Video](https://youtube.com/...) - 10 minute introduction
- [Security Setup Video](https://youtube.com/...) - Security configuration
- [Trading Strategies Video](https://youtube.com/...) - Using trading strategies

### Русские туториалы:
- [Начало работы](https://youtube.com/...) - 10-минутное введение
- [Настройка безопасности](https://youtube.com/...) - Конфигурация безопасности
- [Торговые стратегии](https://youtube.com/...) - Использование торговых стратегий

## 📞 Support

### English Support:
- **GitHub Issues**: [Report bugs](https://github.com/s7cret/binance-enhanced/issues)
- **Discord**: Join OpenClaw community (English channel)
- **Documentation Issues**: [Docs feedback](https://github.com/s7cret/binance-enhanced/issues)

### Русская поддержка:
- **GitHub Issues**: [Сообщить об ошибках](https://github.com/s7cret/binance-enhanced/issues)
- **Telegram**: @s7cret (русская поддержка)
- **Discord**: OpenClaw community (русский канал)

## 🔄 Updates

### Documentation Updates:
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history
- **Release Notes**: [RELEASE_NOTES.md](RELEASE_NOTES.md) - Release information
- **Migration Guide**: [MIGRATION.md](MIGRATION.md) - Version migration guide

### Stay Updated:
- **Watch repository** on GitHub for updates
- **Star repository** to show support
- **Follow releases** for new versions

---

**📢 Need help with documentation?**  
Open an issue on GitHub or contact support!

**🌍 Help translate documentation** into other languages!

**⭐ Star the repository** if you find the documentation helpful!