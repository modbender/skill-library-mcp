# Crypto Executor Optimizer v2.0 🤖⚡

**Wesley analyse les performances du bot toutes les 6h et optimise executor.py automatiquement.**

---

## Architecture

```
OpenClaw (cron toutes les 6h)
    ↓
Wesley reçoit la tâche
    ↓
Wesley lit performance_metrics.json + executor.py
    ↓
Wesley analyse et décide des nouvelles valeurs
    ↓
Wesley appelle apply_optimization.sh avec les nouvelles valeurs
    ↓
apply_optimization.sh → backup → modifie → valide → redémarre → Telegram
```

**Wesley est l'intelligence. apply_optimization.sh est l'outil.**

---

## Installation

```bash
# 1. Setup du bot (première fois)
chmod +x setup_binance_20euros.sh
./setup_binance_20euros.sh

# 2. Installer le cron OpenClaw
chmod +x install_cron.sh
./install_cron.sh
```

---

## Ce que Wesley optimise

| Paramètre | Défaut | Plage |
|---|---|---|
| OBI scalping `obi > X` | 0.10 | 0.06–0.18 |
| OBI momentum `obi > X` | 0.12 | 0.08–0.20 |
| Price change trigger | 0.8% | 0.4–2.0% |
| Spread filter | 8 bps | 4–15 bps |
| Kelly factor | 0.5 | 0.3–0.6 |
| Strategy mix | 70/25/5 | voir SKILL.md |

## Sécurité

- Backup automatique avant chaque modification
- Validation syntaxe Python avant restart
- Rollback automatique si erreur
- 5 derniers backups conservés
- Jamais de modification des credentials ou circuit breakers
- `apply_optimization.sh` modifie uniquement les seuils OBI, Kelly et strategy mix via regex — aucune autre ligne du code n'est touchée

## Monitoring

```bash
tail -f /workspace/logs/auto_optimize.log
tail -f /workspace/logs/wesley_optimizations.log
ls /workspace/skills/crypto-executor/executor_backup_*.py
sudo systemctl status crypto-executor
```

## Fichiers

```
crypto-executor-optimizer/
├── SKILL.md                  # Instructions pour Wesley
├── apply_optimization.sh     # Script utilitaire (Wesley l'appelle)
├── install_cron.sh           # Installe le cron OpenClaw
├── setup_binance_20euros.sh  # Setup initial du bot
├── README.md                 # Ce fichier
└── LICENSE                   # MIT
```
