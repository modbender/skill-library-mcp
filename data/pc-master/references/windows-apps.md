# Common Windows App Executable Names

## Browsers
| App | Executable |
|-----|-----------|
| Google Chrome | `chrome.exe` |
| Microsoft Edge | `msedge.exe` |
| Firefox | `firefox.exe` |
| Brave | `brave.exe` |

## Media
| App | Executable |
|-----|-----------|
| Spotify | `Spotify.exe` |
| VLC | `vlc.exe` |
| Windows Media Player | `wmplayer.exe` |
| iTunes | `iTunes.exe` |

## Communication
| App | Executable |
|-----|-----------|
| Discord | `Discord.exe` |
| WhatsApp | `WhatsApp.exe` |
| Telegram | `Telegram.exe` |
| Slack | `slack.exe` |
| Teams | `ms-teams.exe` or `Teams.exe` |
| Zoom | `Zoom.exe` |

## Productivity
| App | Executable |
|-----|-----------|
| Notepad | `notepad.exe` |
| Word | `WINWORD.EXE` |
| Excel | `EXCEL.EXE` |
| PowerPoint | `POWERPNT.EXE` |
| VS Code | `Code.exe` |
| Notepad++ | `notepad++.exe` |

## System
| App | Executable |
|-----|-----------|
| Task Manager | `Taskmgr.exe` |
| File Explorer | `explorer.exe` |
| Calculator | `calc.exe` |
| Paint | `mspaint.exe` |
| Snipping Tool | `SnippingTool.exe` |

## Launch Paths (if `start` doesn't work)
```bash
# VS Code
/mnt/c/Users/$(ls /mnt/c/Users | grep -v "Public\|Default")/AppData/Local/Programs/Microsoft\ VS\ Code/Code.exe

# Spotify
/mnt/c/Users/$(ls /mnt/c/Users | grep -v "Public\|Default")/AppData/Roaming/Spotify/Spotify.exe

# Discord
/mnt/c/Users/$(ls /mnt/c/Users | grep -v "Public\|Default")/AppData/Local/Discord/app-*/Discord.exe
```
