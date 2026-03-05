---
name: firm-hebbian-memory
version: 1.0.0
description: >
  Système de mémoire adaptative hebbienne pour Claude.md — transforme les logs
  de sessions en patterns pondérés qui renforcent ou atrophient les règles de
  travail selon l'usage réel. Implémente le Cahier des Charges v1.0.0 "Système
  de Mémoire Adaptative Hebbienne + Base Vectorielle pour Claude.md".
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 1.2.0
    cdc_version: "1.0.0"
tags:
  - hebbian
  - memory
  - adaptive
  - pgvector
  - sessions
  - pii-stripping
  - neuroscience
---

# firm-hebbian-memory

> ⚠️ Contenu généré par IA — validation humaine requise avant déploiement en production.

## Purpose

Ce skill rend le **Claude.md vivant et auto-évolutif** via des mécanismes inspirés
de la plasticité synaptique hebbienne. Les patterns de travail qui se répètent sont
renforcés, ceux qui deviennent obsolètes s'atrophient naturellement.

**Inspiration neurobiologique :**
- **Plasticité hebbienne** → renforcement des poids Layer 2 par co-activation
- **Mémoire hippocampique** → stockage épisodique en base vectorielle (pgvector)
- **Consolidation néocorticale** → job d'analyse transformant les épisodes en schémas

## Architecture — 4 couches Claude.md (CDC §3.3)

| Couche | Nom | Modification |
|--------|-----|-------------|
| Layer 1 | CORE (immuable) | Humain uniquement |
| Layer 2 | CONSOLIDATED PATTERNS | Auto-mise à jour (poids hebbiens) |
| Layer 3 | EPISODIC INDEX | Auto-mise à jour (pointeurs sessions) |
| Layer 4 | META INSTRUCTIONS | Lecture seule pour le système auto |

## Tools activés (8 tools)

### Runtime (2 tools)

```
openclaw_hebbian_harvest        — ingest JSONL session logs → SQLite (PII stripped)
openclaw_hebbian_weight_update  — calcul/application des poids hebbiens (dry_run par défaut)
```

### Audit (6 tools)

```
openclaw_hebbian_analyze           — analyse co-activation patterns (Jaccard)
openclaw_hebbian_status            — dashboard poids, atrophie, promotions
openclaw_hebbian_layer_validate    — validation structure 4 couches
openclaw_hebbian_pii_check         — audit config PII stripping
openclaw_hebbian_decay_config_check — validation paramètres hebbiens
openclaw_hebbian_drift_check       — détection drift sémantique vs baseline
```

## Formule de mise à jour des poids (CDC §4.3)

```python
nouveau_poids = ancien_poids + (learning_rate × activation) - (decay × (1 - activation))

# Paramètres par défaut
learning_rate = 0.05    # Renforcement si activée
decay         = 0.02    # Atrophie si non-activée
poids_min     = 0.0     # Floor — suppression si < 0.10
poids_max     = 0.95    # Ceiling — promotion CORE si > 0.95
```

## Seuils de consolidation

| Transition | Condition |
|-----------|-----------|
| Épisodique → Émergent | Activé 5 sessions consécutives |
| Émergent → Fort | poids > 0.8 sur 20 sessions |
| Fort → CORE | **Validation humaine obligatoire** |
| Atrophie → Suppression | poids < 0.10 pendant 4 semaines + PR humaine |

## Sécurité (CDC §5.2)

- **PII stripping obligatoire** : regex sur emails, phones, IPs, API keys, SSN, JWT, AWS keys, chemins Unix home
- **Secrets détectés** : session rejetée + alerte immédiate
- **Accès BDD** : localhost/VPN uniquement
- **Rotation embeddings** : policy de ré-embedding si fuite suspectée
- **Réversibilité** : chaque modification = 1 commit Git atomique
- **Path whitelist** : configurable via `HEBBIAN_ALLOWED_DIRS` (env) — protège containers/multi-user

### Limitations connues (PII)

Le stripping regex couvre les catégories les plus courantes (10 patterns) mais ne
détecte pas les credentials embarqués dans des URLs de connexion (e.g.
`postgres://user:password@host/db`) ni les variables d'environnement loguées dans
des stack traces (`DB_URL=...`). Un scanner de secrets dédié (e.g. `trufflehog`,
`detect-secrets`) est recommandé en complément pour les environnements à haute
sensibilité.

## Anti-dérive (CDC §5.1)

- Aucune règle ne peut atteindre poids = 1.0 automatiquement (max 0.95)
- Détecteur de drift : alerte si cosine similarity vs baseline < 0.7
- 3 changements auto consécutifs → review forcée
- Snapshot mensuel archivé en Git tag

## Pipeline global

```
[ Session Claude Code ]
         ↓ fin de session
[ openclaw_hebbian_harvest ] → extrait résumé + tags + règles (PII stripped)
         ↓
[ SQLite local ] → stockage épisodique structuré
         ↓
[ openclaw_hebbian_analyze ] → clustering Jaccard + co-activations
         ↓
[ openclaw_hebbian_weight_update ] → mise à jour Layer 2 (dry_run=True)
         ↓
[ Human Review ] → validation avant application (dry_run=False)
```

## Hook post-session (MVP)

Sans hook automatique, l'ingestion reste manuelle — adoption = zéro.
Voici le minimum pour boucler le pipeline dès le MVP.

### Option A — Script shell (le plus simple)

Créer `~/.openclaw/hooks/post-session.sh` :

```bash
#!/usr/bin/env bash
# Hook post-session: ingest le dernier JSONL automatiquement
set -euo pipefail

SESSION_LOG="${1:-$(ls -t ~/.openclaw/sessions/*.jsonl 2>/dev/null | head -1)}"
[ -z "$SESSION_LOG" ] && exit 0

# Appel MCP via curl (le serveur doit tourner sur :8012)
curl -s -X POST http://localhost:8012/mcp \
  -H "Content-Type: application/json" \
  -d "{
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"openclaw_hebbian_harvest\",
      \"arguments\": {\"session_jsonl_path\": \"$SESSION_LOG\"}
    }
  }" | jq '.result.ingested // .error'
```

### Option B — Entrée cron (automatisation passive)

```bash
# Toutes les 30 min, ingérer les nouveaux JSONL
*/30 * * * * /bin/bash ~/.openclaw/hooks/post-session.sh >> ~/.openclaw/hebbian-harvest.log 2>&1
```

### Option C — Intégration `pi-coding-agent`

Si le projet utilise `pi-coding-agent`, ajouter dans sa config :

```json
{
  "hooks": {
    "post_session": {
      "command": "~/.openclaw/hooks/post-session.sh",
      "trigger": "on_session_end"
    }
  }
}
```

> **Note :** Le hook ne déclenche **que** le harvest (lecture). La mise à jour
> des poids (`weight_update`) reste toujours manuelle avec `dry_run=True` par
> défaut — conformément à la règle absolue n°1 du CDC.

## Adaptation OpenClaw

| Composant CDC | Adaptation OpenClaw |
|--------------|---------------------|
| Hook post-session | Lecture fichiers `.jsonl` de `pi-coding-agent` |
| Claude.md Layer 2 | Skills OpenClaw (`.md` ou `.json`) |
| Claude.md Layer 4 | Extension `pi-coding-agent` dédiée |
| GitHub PR for review | PR sur repo privé skills |
| Secrets stripping | **Renforcé** — 9 patterns regex + détection runtime |

## Configuration requise

```json
{
  "hebbian": {
    "parameters": {
      "learning_rate": 0.05,
      "decay": 0.02,
      "poids_min": 0.0,
      "poids_max": 0.95
    },
    "thresholds": {
      "episodic_to_emergent": 5,
      "emergent_to_strong": 0.8
    },
    "pii_stripping": {
      "enabled": true,
      "patterns": ["email", "phone", "ip", "api_key", "ssn"]
    },
    "security": {
      "secret_detection": true,
      "access_restriction": "localhost",
      "embedding_rotation": "on_breach"
    },
    "anti_drift": {
      "max_consecutive_auto_changes": 3
    }
  }
}
```

## Référence

- CDC : `cahier_des_charges_memoire_hebbienne.md` v1.0.0
- Module : `src/hebbian_memory.py`
- Modèles : 8 classes Pydantic dans `src/models.py`

---

## 💎 Support

Si ce skill vous est utile, vous pouvez soutenir le développement :

**Dogecoin** : `DQBggqFNWsRNTPb6kkiwppnMo1Hm8edfWq`
