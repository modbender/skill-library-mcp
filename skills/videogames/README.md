# Videogames 🎮

A skill for [OpenClaw](https://github.com/openclaw/openclaw) that allows you to query video game information, search for deals, and compare prices across multiple stores. Now supercharged with ProtonDB, HowLongToBeat, and System Requirements!

## Features

- 🔎 **Search**: Find games by name on Steam.
- 💰 **Deals**: Search for the lowest price across more than 25 stores (powered by CheapShark) with **Historical Low detection**.
- ℹ️ **Details**: Get description, price, developers, Metacritic score, and **PC System Requirements**.
- 🗣️ **Languages**: Check if a game supports your language (Text/Audio).
- 🎮 **Input**: View Controller support (Full/Partial) and Multiplayer modes (Co-op/PvP).
- 🔗 **Resources**: Direct links to **PCGamingWiki** and **SteamDB** for fixes and deep data.
- 🐧 **Compatibility**: Check Linux & Steam Deck compatibility status via **ProtonDB**.
- ⏱️ **Duration**: Get estimated playtime (Main Story, Completionist) via **HowLongToBeat**.
- 💡 **Recommendations**: Get suggestions for similar games based on genres and tags.
- 🏷️ **Offers**: Check current featured offers on Steam.
- 👥 **Players**: View current concurrent player counts.
- 📈 **Trends**: Explore Top Sellers and New Releases on Steam.
- 📰 **News**: Read the latest news for a game.
- 🏆 **Achievements**: View the rarest global achievements for a game.
- ⭐ **Reviews**: Get a summary of user reviews for a game.

## Installation

### From ClawHub (Recommended)
```bash
npx clawhub@latest install ivanheral/videogames
```

### Manually
1. Clone this repository into your global or workspace skills folder:
   ```bash
   git clone https://github.com/ivanheral/videogames ~/.openclaw/skills/videogames
   ```
2. Ensure the script has execution permissions:
   ```bash
   chmod +x ~/.openclaw/skills/videogames/scripts/game_tool.py
   ```

## Usage

Simply ask OpenClaw for what you need:

> "Where is Elden Ring cheapest?"
> "Is Cyberpunk 2077 compatible with Steam Deck?"
> "How long does it take to beat Witcher 3?"
> "What are the system requirements for Red Dead Redemption 2?"
> "Recommend me games like factorio"

### Command Line Usage (Advanced)

You can also use the script directly if needed. It now features a modular architecture (`scripts/core`) for better performance and reliability.

#### Global Arguments (Dynamic Configuration)
You can override the default region and language settings for any command:
- `--region <CC>`: Country Code (e.g., `US`, `ES`, `GB`).
- `--currency <CODE>`: Currency Code (e.g., `USD`, `EUR`, `GBP`).
- `--lang <LANG>`: Language (e.g., `english`, `spanish`).

**Example:**
```bash
python3 scripts/game_tool.py --region US --currency USD deals "Elden Ring"
```

#### Core Commands
- **Search Steam**: `python3 scripts/game_tool.py search "Game Name"`
- **Game Details (w/ Specs)**: `python3 scripts/game_tool.py details <APPID>`
- **Search Deals (CheapShark)**: `python3 scripts/game_tool.py deals "Game Name"`

#### New Integrations
- **Linux/Steam Deck Support**: `python3 scripts/game_tool.py compatibility <APPID>`
- **Game Duration**: `python3 scripts/game_tool.py duration "Game Name"`
- **Recommendations**: `python3 scripts/game_tool.py recommendations <APPID>`

#### Other Utility Commands
- **Featured Offers**: `python3 scripts/game_tool.py offers`
- **Player Count**: `python3 scripts/game_tool.py players <APPID>`
- **Game News**: `python3 scripts/game_tool.py news <APPID>`
- **Trends**: `python3 scripts/game_tool.py trends`
- **Most Played**: `python3 scripts/game_tool.py top`
- **Achievements**: `python3 scripts/game_tool.py achievements <APPID>`
- **Reviews**: `python3 scripts/game_tool.py reviews <APPID>`

## Configuration

You can customize the region and currency via environment variables:

- `STEAM_LANGUAGE`: Language for Steam descriptions (default: `spanish`).
- `STEAM_CURRENCY`: Currency code (default: `EUR`).
- `STEAM_CC`: Country code for pricing (default: `ES`).

Example:
```bash
export STEAM_LANGUAGE=english
export STEAM_CURRENCY=USD
python3 scripts/game_tool.py search "Portal"
```

## Data Sources & Credits 📚

This tool would not be possible without the excellent public APIs and data from:

- **[Steam](https://store.steampowered.com/)** (Valve): Game details, reviews, players, achievements, and news.
- **[CheapShark](https://www.cheapshark.com/)**: Deal searching and historical price tracking across multiple digital stores.
- **[ProtonDB](https://www.protondb.com/)**: Linux and Steam Deck compatibility reports.
- **[HowLongToBeat](https://howlongtobeat.com/)**: Game length estimations (Main Story, Completionist).

## Requirements

- Python 3.x
- **No external dependencies** (uses standard libraries only).
- Internet connection (uses public APIs mentioned above).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
