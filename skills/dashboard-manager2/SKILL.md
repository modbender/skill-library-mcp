---
slug: dashboard-manager
display_name: Dashboard Manager
version: 1.0.0
---




# Dashboard Manager Skill

## Description
Gère les interactions avec le dashboard Jarvis. Ce skill permet de lire, mettre à jour et synchroniser le fichier `data.json` en temps réel.

## Fonctionnalités
- **Lecture/Sauvegarde** : Accès au fichier `data.json`
- **Gestion des notes** : Récupération des notes pending et marquage comme processed
- **Logging** : Ajout d'entrées dans l'historique
- **Mise à jour du système** : Statut, heartbeat, modèle actif
- **Statistiques** : Compteurs de tokens et coûts
- **Gestion des tâches** : Ajout et mise à jour
- **Sub-agents** : Gestion des agents actifs

## Configuration

### Chemin du fichier
```javascript
const DATA_FILE_PATH = 'D:\\Projets\\ClaudBot\\Jarvis_Dashboard\\data.json';
```

### Permissions
- **Lecture/Écriture** : Accès au fichier `data.json`
- **Système** : Mise à jour du statut et heartbeat
- **Logging** : Ajout d'entrées dans l'historique

## API

### Fonctions principales
```javascript
// Chargement de la base de données
await loadDatabase();

// Sauvegarde de la base de données
await saveDatabase(db);

// Récupération des notes en attente
const pendingNotes = await getPendingNotes();

// Marquage d'une note comme traitée
await processNote(noteId);

// Ajout d'un log
await addLog('Action effectuée');

// Mise à jour du statut du système
await updateSystemStatus('idle', 'Claude-3-Opus');

// Mise à jour des statistiques
await updateStats(1500, 2800, 0.52);

// Ajout/mise à jour d'une tâche
await updateTask(1, { status: 'done' });

// Gestion des sub-agents
await addSubAgent('dashboard_agent', 'Monitoring dashboard');
await removeSubAgent('dashboard_agent');
```

## Initialisation

```javascript
const dashboardSkill = require('./skills/dashboard-manager');
const success = await dashboardSkill.init();
if (success) {
    console.log('🚀 Dashboard Manager initialisé');
}
```

## Permissions requises
- **Accès fichier** : `D:\Projets\ClaudBot\Jarvis_Dashboard\data.json`
- **Écriture système** : Mise à jour du statut et heartbeat
- **Logging** : Ajout d'entrées dans l'historique

## Utilisation

Ce skill est conçu pour fonctionner en arrière-plan et maintenir la synchronisation entre Jarvis et le dashboard en temps réel.

### Boucle de fonctionnement (The Loop)
1. **INPUT** : Consulte `quick_notes` et traite les notes pending
2. **OUTPUT** : Met à jour `data.json` avec les changements
3. **Auto-sync** : Heartbeat toutes les 2 secondes
4. **Silent mode** : Fonctionne sans intervention conversationnelle

## Exemple d'utilisation

```javascript
// Dans une réponse conversationnelle
await updateStats(estimatedInputTokens, estimatedOutputTokens, estimatedCost);
await addLog('Réponse à la question sur les agents');
await updateSystemStatus('idle');
```

## Installation

1. Copier le dossier `dashboard-manager` dans le répertoire des skills
2. Vérifier le chemin du fichier `data.json`
3. Activer le skill dans la configuration
4. Le skill s'initialisera automatiquement

## Dépannage

### Problèmes courants
- **Fichier introuvable** : Vérifier le chemin `DATA_FILE_PATH`
- **Permissions refusées** : Vérifier les droits d'accès au fichier
- **JSON invalide** : Vérifier la syntaxe du fichier `data.json`

### Logs
Les logs sont ajoutés automatiquement dans la section `logs` du fichier `data.json` pour le suivi des actions.

## Sécurité

- **Accès limité** : Seul le fichier `data.json` est accessible
- **Écriture contrôlée** : Les mises à jour sont validées
- **Logs d'audit** : Toutes les actions sont enregistrées

## Compatibilité

Ce skill est compatible avec OpenClaw et fonctionne avec n'importe quelle instance de Jarvis utilisant le dashboard V2 Ultimate.