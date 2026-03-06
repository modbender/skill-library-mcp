#!/bin/bash
# PROMPT-SHIELD Hook für Claude Code
# Prüft eingehende Nachrichten auf Prompt Injection
#
# Installation:
#   In ~/.claude/settings.json unter "hooks" hinzufügen:
#   "UserInputSubmit": ["/opt/shared/tools/prompt-shield/prompt-shield-hook.sh"]

SHIELD_PATH="$(dirname "$(readlink -f "$0")")/shield.py"

# Lese Input von stdin (Claude übergibt die Nachricht so)
INPUT=$(cat)

# Extrahiere die eigentliche Nachricht (falls JSON-Format)
if echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('message',''))" 2>/dev/null; then
    MESSAGE=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('message',''))")
else
    MESSAGE="$INPUT"
fi

# Führe Scan durch
RESULT=$("$SHIELD_PATH" --json scan "$MESSAGE" 2>/dev/null)
THREAT_LEVEL=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('threat_level','CLEAN'))" 2>/dev/null)
SCORE=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('score',0))" 2>/dev/null)

case "$THREAT_LEVEL" in
    "CLEAN")
        # Alles OK - nichts ausgeben
        exit 0
        ;;
    "WARNING")
        echo "⚠️ PROMPT-SHIELD Warnung (Score: $SCORE/100)"
        echo "Mögliche Manipulation erkannt. Bitte prüfe den Inhalt."
        exit 0  # Warnung, aber durchlassen
        ;;
    "BLOCK")
        echo "🛑 PROMPT-SHIELD: Prompt Injection erkannt! (Score: $SCORE/100)"
        echo "Diese Nachricht wurde als gefährlich eingestuft."
        echo "Blockiere Verarbeitung."
        exit 1  # Blockieren
        ;;
esac
