---
name: crypto-executor-optimizer
description: Autonomous optimizer skill for Wesley — reads Binance trading performance every 6 hours, analyzes win rate and strategy metrics, then safely tunes executor.py parameters (OBI thresholds, Kelly factor, strategy mix) via backup → modify → validate → restart.
version: 2.0.0
author: Georges Andronescu (Wesley Armando)
license: MIT
metadata:
  openclaw:
    emoji: "🤖"
    requires:
      bins:
        - python3
        - bash
        - systemctl
      env: []
      setup_env:
        - BINANCE_API_KEY   # collected interactively at setup, persisted to /workspace/data/bot_config.env (chmod 600)
        - BINANCE_API_SECRET  # collected interactively at setup, persisted to /workspace/data/bot_config.env (chmod 600)
      optional_env:
        - TELEGRAM_BOT_TOKEN
        - TELEGRAM_CHAT_ID
    install_notes: >
      setup_binance_20euros.sh performs the following actions on first run:
      (1) prompts for BINANCE_API_KEY and BINANCE_API_SECRET and persists them
      to /workspace/data/bot_config.env (chmod 600, user-owned);
      (2) downloads executor.py from raw.githubusercontent.com/georges91560/crypto-executor
      and optionally crypto_oracle.py from raw.githubusercontent.com/georges91560/crypto-sniper-oracle
      — audit both files before running;
      (3) runs pip install websocket-client --break-system-packages (required on shared hosting;
      use virtualenv on standard VPS);
      (4) installs a recurring cron job every 6h via openclaw cron or system crontab.
      apply_optimization.sh modifies executor.py via regex — always creates a timestamped
      backup, validates Python syntax, and rolls back automatically on error.
    privilege_requirements:
      uses_sudo: true
      reason: "sudo systemctl restart crypto-executor — required to restart the trading bot service"
      uses_crontab: true
      cron_schedule: "0 */6 * * *"
      cron_purpose: "Trigger Wesley optimization cycle every 6 hours"
      uses_pkill: true
      pkill_purpose: "Fallback process restart if systemd is unavailable"
    external_downloads:
      - url: "https://raw.githubusercontent.com/georges91560/crypto-executor/main/executor.py"
        purpose: "Main trading bot script — downloaded only if not already installed"
        optional: false
        security: "Audit code before running — executes as main trading process"
      - url: "https://raw.githubusercontent.com/georges91560/crypto-sniper-oracle/main/crypto_oracle.py"
        purpose: "Oracle script for OBI/VWAP signals — downloaded only if not already installed"
        optional: true
        security: "Audit code before running — executed as subprocess by executor.py"
    network_behavior:
      makes_requests: true
      endpoints_allowed:
        - "https://raw.githubusercontent.com/georges91560/crypto-executor/main/executor.py"
        - "https://raw.githubusercontent.com/georges91560/crypto-sniper-oracle/main/crypto_oracle.py"
        - "https://api.telegram.org/bot*"
      requires_credentials: false
      uses_websocket: false
    security_level: "L2 - System Modification (modifies executor.py + restarts service)"
---

# Crypto Executor Optimizer 🤖

Ce skill permet à Wesley d'optimiser automatiquement le bot de trading `crypto-executor` toutes les 6 heures.

---

## ⚠️ SCOPE & CAPABILITIES

**Ce que ce skill fait :**
- ✅ Lit les fichiers de performance (`performance_metrics.json`, `learned_config.json`)
- ✅ Analyse les métriques (win rate, trades/jour, win rate par stratégie)
- ✅ Décide des nouvelles valeurs pour les paramètres de trading
- ✅ Modifie `executor.py` via regex (backup → modify → validate → restart)
- ✅ Envoie des alertes Telegram sur chaque optimisation
- ✅ **[SETUP UNIQUEMENT]** Télécharge executor.py et crypto_oracle.py depuis GitHub
- ✅ **[SETUP UNIQUEMENT]** Persiste les credentials Binance dans `/workspace/data/bot_config.env` (chmod 600)
- ✅ **[SETUP UNIQUEMENT]** Installe un cron job toutes les 6h

**Ce que ce skill ne fait PAS :**
- ❌ Ne place pas d'ordres directement — mais redémarrer executor.py via systemd/pkill peut reprendre le trading automatiquement
- ❌ Ne modifie jamais les credentials Binance dans executor.py
- ❌ Ne modifie jamais les circuit breakers ou stop loss
- ❌ Ne touche jamais à la structure des classes Python
- ❌ Ne persiste aucune donnée au-delà de `/workspace`

---

## 🔐 Credentials & Sécurité

### Credentials collectés par setup_binance_20euros.sh

| Variable | Requis | Usage |
|---|---|---|
| `BINANCE_API_KEY` | Oui (setup) | Authentification Binance — jamais modifié après setup |
| `BINANCE_API_SECRET` | Oui (setup) | Authentification Binance — jamais modifié après setup |
| `TELEGRAM_BOT_TOKEN` | Non | Notifications d'optimisation |
| `TELEGRAM_CHAT_ID` | Non | Destination des notifications |

**Stockage des credentials :**
```bash
# Fichier créé par setup_binance_20euros.sh
/workspace/data/bot_config.env

# Permissions automatiquement appliquées
chmod 600 /workspace/data/bot_config.env
# → Lecture réservée à l'utilisateur courant uniquement
# → Jamais visible dans systemctl status ou ps aux
```

**Ce que Wesley ne modifie JAMAIS :**
- `BINANCE_API_KEY` et `BINANCE_API_SECRET` — Wesley ne modifie pas ces valeurs. En revanche, lors du fallback restart, `apply_optimization.sh` (déclenché par Wesley) source `/workspace/data/bot_config.env` pour relancer executor.py avec les credentials existants.
- `DRAWDOWN_KILL_PCT`, `DRAWDOWN_PAUSE_PCT` — protection capitale hors portée

---

## 📦 Installation & Setup

### Vue d'ensemble

```
setup_binance_20euros.sh    → Setup initial (run once)
install_cron.sh             → Installe le cron Wesley (run once)
apply_optimization.sh       → Appelé par Wesley toutes les 6h (automatique)
```

### Téléchargements externes (setup uniquement)

Le script de setup télécharge du code externe depuis GitHub — **auditer avant d'exécuter** :

```bash
# executor.py — le bot de trading principal
https://raw.githubusercontent.com/georges91560/crypto-executor/main/executor.py

# crypto_oracle.py — signaux OBI/VWAP (optionnel)
https://raw.githubusercontent.com/georges91560/crypto-sniper-oracle/main/crypto_oracle.py
```

**Recommandation sécurité :** Épingler un commit spécifique plutôt que `main` :
```bash
# Vérifier le commit sur GitHub, puis :
# git checkout <commit-hash>
```

### Dépendance Python

```bash
# Sur shared hosting (Hostinger, cPanel) :
pip install websocket-client --break-system-packages

# Sur VPS/serveur standard (recommandé) :
python3 -m venv venv && source venv/bin/activate && pip install websocket-client
```

### Privilèges requis

| Action | Pourquoi |
|---|---|
| `sudo systemctl restart crypto-executor` | Redémarrer le bot après optimisation |
| `sudo systemctl stop/start crypto-executor` | Contrôle du service au setup |
| `pkill -f executor.py` | Fallback si systemd indisponible |
| `crontab -e` | Installer le job récurrent (fallback system cron) |

---

## 🤖 Rôle de Wesley

Wesley est l'intelligence. Wesley lit les données de performance, analyse, décide des changements, puis exécute les scripts bash pour les appliquer.

---

## Ce que Wesley doit faire toutes les 6 heures

### Étape 1 — Lire les données

```bash
cat /workspace/performance_metrics.json
cat /workspace/learned_config.json
cat /workspace/skills/crypto-executor/executor.py
```

### Étape 2 — Analyser les performances

Wesley analyse :

**Win rate :**
- < 80% → serrer les seuils OBI (+0.02), réduire les stratégies agressives
- 80–88% → ajustements mineurs seulement
- > 88% → peut augmenter le Kelly factor (max 0.6)

**Trades par jour :**
- < 20 trades/jour → baisser les seuils OBI (-0.01), baisser price_change trigger
- > 80 trades/jour → monter les seuils (qualité > quantité)

**Win rate par stratégie :**
- < 70% → réduire son allocation de 10%, redistribuer vers la meilleure
- > 92% → augmenter son allocation de 5%

**Si tout est optimal** (win rate > 90%, 30–60 trades/jour, toutes stratégies > 85%) :
→ Aucun changement. Wesley note "no changes needed" dans le log.

### Étape 3 — Décider des nouvelles valeurs

Wesley détermine les nouvelles valeurs pour ces paramètres :

| Paramètre | Valeur par défaut | Plage autorisée |
|---|---|---|
| `obi > X` scalping | 0.10 | 0.06 – 0.18 |
| `obi > X` momentum | 0.12 | 0.08 – 0.20 |
| `price_change > X` | 0.8 | 0.4 – 2.0 |
| `spread_bps < X` | 8 | 4 – 15 |
| `kelly * X` factor | 0.5 | 0.3 – 0.6 |
| strategy mix scalping | 0.70 | 0.50 – 0.90 |
| strategy mix momentum | 0.25 | 0.05 – 0.40 |
| strategy mix stat_arb | 0.05 | 0.02 – 0.15 |

**Wesley ne doit JAMAIS modifier :**
- Les credentials Binance (API key/secret)
- La structure des classes (BinanceClient, PortfolioManager, RiskEngine, BinanceWebSocket)
- Les circuit breakers et stop loss
- DRAWDOWN_KILL_PCT, DRAWDOWN_PAUSE_PCT
- Le code WebSocket

### Étape 4 — Appliquer les changements

Wesley appelle le script avec les nouvelles valeurs :

```bash
bash /workspace/skills/crypto-executor-optimizer/apply_optimization.sh \
  --obi-scalping 0.11 \
  --obi-momentum 0.13 \
  --price-change 0.9 \
  --spread-bps 9 \
  --kelly-factor 0.5 \
  --mix-scalping 0.72 \
  --mix-momentum 0.23 \
  --mix-stat-arb 0.05 \
  --reason "Win rate 76%, tightening OBI thresholds"
```

Le script va automatiquement :
1. Créer un backup horodaté de executor.py
2. Modifier les valeurs via regex (uniquement les seuils OBI, Kelly et strategy mix)
3. Valider la syntaxe Python (`python3 -m py_compile`)
4. Redémarrer le bot via systemd (ou pkill en fallback)
5. Envoyer une alerte Telegram
6. Logger les changements dans auto_optimize.log et wesley_optimizations.log
7. Rollback automatique si erreur syntaxe ou restart échoué

### Étape 5 — Si aucun changement nécessaire

```bash
bash /workspace/skills/crypto-executor-optimizer/apply_optimization.sh --no-changes \
  --reason "Performance optimal, no changes needed"
```

---

## 🔒 Sécurité — apply_optimization.sh

**Ce que le script modifie dans executor.py :**
- Uniquement les seuils numériques OBI, price_change, spread_bps, Kelly factor et strategy mix
- Via regex ciblées — aucune autre ligne du code n'est touchée
- Jamais les credentials, jamais les circuit breakers, jamais la structure des classes

**Protections en place :**
- Backup automatique horodaté avant chaque modification
- Validation syntaxe Python (`py_compile`) avant restart
- Rollback automatique si syntaxe invalide
- Rollback automatique si restart échoué
- Conservation des 5 derniers backups uniquement
- Alerte Telegram en cas d'erreur

---

## 📅 Cron & Persistance

Le skill installe un job récurrent via `install_cron.sh` :

```bash
# Schedule : toutes les 6h
0 */6 * * *

# Via OpenClaw cron (prioritaire) :
openclaw cron add --name "crypto-executor-optimizer" --cron "0 */6 * * *"

# Via system crontab (fallback si openclaw CLI indisponible) :
0 */6 * * * openclaw run --skill crypto-executor-optimizer
```

**Désinstaller le cron :**
```bash
openclaw cron remove --name crypto-executor-optimizer
# OU
crontab -e  # supprimer la ligne crypto-executor-optimizer
```

---

## 📁 Fichiers importants

| Fichier | Rôle |
|---|---|
| `/workspace/performance_metrics.json` | Stats de performance du bot |
| `/workspace/learned_config.json` | Historique des configurations précédentes |
| `/workspace/skills/crypto-executor/executor.py` | Le bot à optimiser |
| `/workspace/data/bot_config.env` | Credentials Binance (chmod 600) |
| `/workspace/logs/auto_optimize.log` | Log des cycles d'optimisation |
| `/workspace/logs/wesley_optimizations.log` | Historique des décisions de Wesley |
| `/workspace/skills/crypto-executor/executor_backup_*.py` | Backups horodatés (5 max) |

---

## 📊 Monitoring

```bash
# Voir le dernier cycle
tail -50 /workspace/logs/auto_optimize.log

# Historique des optimisations
tail -100 /workspace/logs/wesley_optimizations.log

# Backups disponibles
ls -lh /workspace/skills/crypto-executor/executor_backup_*.py

# Status du bot
sudo systemctl status crypto-executor
```
