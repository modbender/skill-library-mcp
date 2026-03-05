#!/bin/bash
# Wrapper robuste pour l'auto-router
# Gère correctement les caractères spéciaux comme ?, !, etc.

# Vérifier qu'on a au moins un argument
if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 'votre question'"
    echo "Exemple: $0 'Comment faire du JavaScript ?'"
    exit 1
fi

# Récupérer toute la question comme un seul argument
QUESTION="$*"

# Debug (optionnel)
# echo "🔍 Question reçue: '$QUESTION'"

# Exécuter le router avec la question entre quotes pour préserver les caractères spéciaux
cd /Users/thibaut/clawd
exec node auto-router.js "$QUESTION"