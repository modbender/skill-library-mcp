---
name: firm-a2a-bridge
version: 2.0.0
description: >
  Agent-to-Agent (A2A) Protocol RC v1.0 bridge for OpenClaw agents.
  Enables agent discovery, identity cards, task lifecycle management,
  push notification configuration, task cancellation, and SSE subscriptions
  compliant with the A2A RC v1.0 specification.
  Covers gaps G1-G8 from the Phase 7 disruption roadmap.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - a2a
  - agent-card
  - discovery
  - interoperability
  - multi-agent
  - protocol
  - sse
  - cancel-task
---

# firm-a2a-bridge

> ⚠️ Contenu généré par IA — validation humaine requise avant déploiement en production.

## Purpose

Ce skill implémente le **A2A Protocol RC v1.0** (Agent-to-Agent) pour OpenClaw,
permettant aux agents de se découvrir mutuellement, d'échanger des tâches, et de
recevoir des notifications push — tout cela via une interface MCP standardisée.

**Gaps couverts :**
| Gap | Sévérité | Outil |
|-----|----------|-------|
| G1 — Pas de génération Agent Card | CRITICAL | `openclaw_a2a_card_generate` |
| G2 — Pas de validation Agent Card | CRITICAL | `openclaw_a2a_card_validate` |
| G3 — Pas d'envoi de tâches A2A | HIGH | `openclaw_a2a_task_send` |
| G4 — Pas de suivi de tâches A2A | HIGH | `openclaw_a2a_task_status` |
| G5 — Pas de push notifications A2A | MEDIUM | `openclaw_a2a_push_config` |
| G6 — Pas de découverte d'agents | HIGH | `openclaw_a2a_discovery` |
| G7 — Pas d'annulation de tâches | HIGH | `openclaw_a2a_cancel_task` |
| G8 — Pas de souscription SSE | HIGH | `openclaw_a2a_subscribe_task` |

## Tools

### `openclaw_a2a_card_generate`
Génère un fichier `.well-known/agent-card.json` à partir d'un fichier SOUL.md.
Extrait automatiquement l'identité, les compétences, les capacités et les schémas
de sécurité depuis le frontmatter et le corps du SOUL.md.

**Paramètres :**
- `soul_path` (str, required) — Chemin vers le fichier SOUL.md
- `base_url` (str, required) — URL de base où l'agent sera joignable
- `output_path` (str, optional) — Chemin de sortie pour le JSON
- `capabilities` (dict, optional) — Capacités A2A (streaming, pushNotifications)
- `security_schemes` (dict, optional) — Schémas OAuth2/apiKey/http
- `extensions` (list, optional) — Déclarations d'extensions A2A
- `sign` (bool, optional) — Signer la carte avec JCS+JWS
- `signing_key` (str, optional) — Clé de signature (masquée dans l'output)
- `default_input_modes` (list, optional) — Types MIME d'entrée par défaut
- `default_output_modes` (list, optional) — Types MIME de sortie par défaut

**Exemple :**
```json
{
  "name": "openclaw_a2a_card_generate",
  "arguments": {
    "soul_path": "./souls/ceo/SOUL.md",
    "base_url": "https://agents.example.com/ceo"
  }
}
```

### `openclaw_a2a_card_validate`
Valide un Agent Card contre la spécification A2A v1.0 RC.
Vérifie les champs requis, le format des URLs, la structure des skills,
les capabilities, et les schémas de sécurité.

**Paramètres :**
- `card_path` (str, optional) — Chemin vers un fichier agent-card.json
- `card_json` (dict, optional) — Agent Card inline (alternative à card_path)

### `openclaw_a2a_task_send`
Envoie un message/tâche à un agent A2A distant.
Crée un Task dans le lifecycle A2A (submitted → working → completed/failed).
Inclut une protection SSRF contre les URLs localhost.

**Paramètres :**
- `agent_url` (str, required) — URL de l'agent cible
- `message` (str, required) — Message texte à envoyer
- `context_id` (str, optional) — ID de contexte pour grouper les tâches
- `blocking` (bool, optional) — Attendre la complétion
- `metadata` (dict, optional) — Métadonnées additionnelles

### `openclaw_a2a_task_status`
Récupère le statut d'une tâche ou liste les tâches.
Mappe les opérations GetTask / ListTasks du protocole A2A.

**Paramètres :**
- `task_id` (str, optional) — ID de tâche spécifique (GetTask)
- `context_id` (str, optional) — Filtre par contexte (ListTasks)
- `include_history` (bool, optional) — Inclure l'historique des messages

### `openclaw_a2a_push_config`
CRUD pour les configurations de webhook push notification A2A.
Supporte create, get, list, delete avec protection SSRF.

**Paramètres :**
- `task_id` (str, required) — ID de la tâche concernée
- `action` (str) — create, get, list, delete
- `webhook_url` (str, optional) — URL du webhook (requis pour create)
- `auth_token` (str, optional) — Token Bearer pour la livraison
- `config_id` (str, optional) — ID de config (requis pour get/delete)

### `openclaw_a2a_cancel_task`
Annule une tâche A2A en cours d'exécution (CancelTask RC v1.0).
Erreur si la tâche est déjà en état terminal.

**Paramètres :**
- `task_id` (str, required) — ID de la tâche à annuler

### `openclaw_a2a_subscribe_task`
Souscrit aux mises à jour d'une tâche via SSE (SubscribeToTask RC v1.0).
Diffuse TaskStatusUpdateEvent et TaskArtifactUpdateEvent.

**Paramètres :**
- `task_id` (str, required) — ID de la tâche à surveiller
- `callback_url` (str, optional) — URL de callback pour les events

### `openclaw_a2a_discovery`
Découvre les agents A2A via leurs endpoints Agent Card ou scan local de SOUL.md.

**Paramètres :**
- `urls` (list[str], optional) — URLs d'agents à scanner
- `souls_dir` (str, optional) — Répertoire local avec des fichiers SOUL.md
- `check_reachability` (bool, optional) — Vérifier l'accessibilité des URLs

## Architecture

```
SOUL.md files                    A2A Protocol v1.0 RC
     │                                  │
     ├── card_generate ──► .well-known/agent-card.json
     │                                  │
     ├── card_validate ◄── Spec validation (8 checks)
     │                                  │
     ├── task_send ────────► SendMessage (submitted → working → completed)
     │                                  │
     ├── task_status ──────► GetTask / ListTasks
     │                                  │
     ├── cancel_task ──────► CancelTask (→ canceled)
     │                                  │
     ├── subscribe_task ───► SubscribeToTask (SSE events)
     │                                  │
     ├── push_config ──────► CRUD webhook configs (SSRF-safe)
     │                                  │
     └── discovery ────────► Agent Card endpoint probe + local SOUL.md scan
```

## Security

- **Path traversal protection** : tous les chemins de fichiers validés par Pydantic
- **SSRF protection** : URLs localhost/127.0.0.1/0.0.0.0/::1 bloquées pour task_send et push_config
- **URL scheme validation** : seuls http/https acceptés
- **Token masking** : les auth_token sont masqués (4 derniers chars visibles)
- **Input validation** : tous les paramètres validés par Pydantic v2 avec contraintes strictes

## Testing

```bash
python -m pytest tests/test_smoke.py -k "TestA2aBridge" -v
```

17 tests couvrent :
- Génération de carte depuis un SOUL.md valide (avec signature JCS+JWS)
- Gestion des fichiers manquants
- Protection path traversal
- Validation de cartes valides/invalides (détection patterns v0.4.0 dépréciés)
- Envoi de tâches avec SSRF protection
- Annulation de tâches (CancelTask)
- Souscription SSE (SubscribeToTask)
- Statut de tâches (GetTask/ListTasks)
- Configuration push notifications (CRUD + SSRF)
- Découverte locale d'agents
