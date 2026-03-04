#!/bin/bash

SKILL_NAME=$1
QUARANTINE_BASE_DIR="$HOME/.openclaw/clawhub-quarantine"
QUARANTINE_DIR="$QUARANTINE_BASE_DIR/skills"
AUDIT_REPORT_DIR="$QUARANTINE_BASE_DIR/reports"
AUDIT_SCRIPT="$(dirname "$0")/clawhub-quarantine.sh"
CLAWHUB_BIN="npx clawhub"

if [ -z "$SKILL_NAME" ]; then
  echo "Uso: $0 <nome-da-skill>"
  exit 1
fi

mkdir -p "$QUARANTINE_DIR"
mkdir -p "$AUDIT_REPORT_DIR"

echo "Iniciando instalação da skill '$SKILL_NAME' em quarentena..."
# Using --dir to specify the installation directory for the skill
$CLAWHUB_BIN install "$SKILL_NAME" --dir "$QUARANTINE_DIR" --force

if [ $? -eq 0 ]; then
  echo "Skill '$SKILL_NAME' instalada com sucesso em quarentena em: $QUARANTINE_DIR/$SKILL_NAME"
  echo "Executando script de auditoria..."
  if [ -f "$AUDIT_SCRIPT" ]; then
    # Pass the quarantined skill's full path and report directory to the audit script
    bash "$AUDIT_SCRIPT" audit "$QUARANTINE_DIR/$SKILL_NAME" "$AUDIT_REPORT_DIR"
    if [ $? -eq 0 ]; then
      echo "Auditoria da skill '$SKILL_NAME' concluída."
      echo "Por favor, revise manualmente a skill em '$QUARANTINE_DIR/$SKILL_NAME' e o relatório em '$AUDIT_REPORT_DIR/${SKILL_NAME}-audit-*.txt'."
      echo "Após a revisão, você pode promover a skill para produção manualmente para ~/.openclaw/workspace/skills."
    else
      echo "Erro na execução do script de auditoria para '$SKILL_NAME'."
    fi
  else
    echo "Aviso: Script de auditoria '$AUDIT_SCRIPT' não encontrado. Pulando auditoria."
    echo "Por favor, crie o arquivo '$AUDIT_SCRIPT' com a lógica de auditoria."
  fi
else
  echo "Erro: Falha na instalação da skill '$SKILL_NAME' em quarentena."
fi
