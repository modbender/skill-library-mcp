# Skill: Supervisor

Superviseur autonome des ressources et des connexions.

## Usage
- **/supervisor status** : Affiche un bilan complet (CPU, RAM, Docker, Sites).
- **/supervisor restart <nom>** : Relance un service spécifique.

## Fonctionnement
L'agent scanne le serveur toutes les 5 minutes et tente une auto-guérison si un site tombe ou si un conteneur s'arrête.
