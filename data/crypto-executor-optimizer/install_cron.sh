#!/bin/bash

#########################################################
# CRON INSTALLER - Wesley Auto-Optimizer
# Installe le cron OpenClaw toutes les 6h
# Author: Georges Andronescu (Wesley Armando)
# Version: 2.0.0
#########################################################

SKILL_DIR="/workspace/skills/crypto-executor-optimizer"

echo "========================================"
echo "WESLEY CRON INSTALLER v2.0"
echo "========================================"
echo ""

# Vérifier que le skill est installé
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ SKILL.md non trouvé dans $SKILL_DIR"
    echo "Installe d'abord le skill crypto-executor-optimizer."
    exit 1
fi

chmod +x "$SKILL_DIR/apply_optimization.sh"
echo "✅ apply_optimization.sh exécutable"

# Créer les dossiers nécessaires
mkdir -p /workspace/logs
echo "✅ Dossiers créés"

# Installer le cron OpenClaw (toutes les 6h)
echo ""
echo "[CRON] Installation du job OpenClaw..."

openclaw cron add \
  --name "crypto-executor-optimizer" \
  --cron "0 */6 * * *" \
  --session isolated \
  --message "Run the crypto-executor-optimizer skill. Read /workspace/performance_metrics.json and /workspace/skills/crypto-executor/executor.py, analyze performance, decide what to optimize, then call apply_optimization.sh with the new values."

if [ $? -eq 0 ]; then
    echo "✅ Cron OpenClaw installé (toutes les 6h)"
else
    echo "⚠️  openclaw CLI non disponible. Fallback crontab système..."
    
    # Fallback: crontab système qui demande à Wesley via openclaw
    CRON_LINE="0 */6 * * * openclaw run --skill crypto-executor-optimizer >> /workspace/logs/cron.log 2>&1"
    (crontab -l 2>/dev/null | grep -v crypto-executor-optimizer; echo "# Wesley Optimizer") | crontab -
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "✅ Cron système installé en fallback"
fi

echo ""
echo "========================================"
echo "INSTALLATION COMPLETE"
echo "========================================"
echo ""
echo "📅 Schedule : toutes les 6h (00:00, 06:00, 12:00, 18:00)"
echo ""
echo "📊 Monitoring :"
echo "   tail -f /workspace/logs/auto_optimize.log"
echo "   tail -f /workspace/logs/wesley_optimizations.log"
echo ""
echo "▶️  Tester maintenant :"
echo "   openclaw run --skill crypto-executor-optimizer"
echo ""
echo "🗑️  Désinstaller :"
echo "   openclaw cron remove --name crypto-executor-optimizer"
echo ""
