#!/bin/bash

COMMAND=$1
SKILL_PATH=$2
REPORT_DIR=$3

if [ "$COMMAND" == "audit" ]; then
  if [ -z "$SKILL_PATH" ] || [ -z "$REPORT_DIR" ]; then
    echo "Uso: $0 audit <caminho-da-skill> <diretorio-de-relatorio>"
    exit 1
  fi

  SKILL_NAME=$(basename "$SKILL_PATH")
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  REPORT_FILE="$REPORT_DIR/${SKILL_NAME}-audit-${TIMESTAMP}.txt"

  echo "Iniciando auditoria de segurança para a skill: $SKILL_NAME" > "$REPORT_FILE"
  echo "Diretório da skill: $SKILL_PATH" >> "$REPORT_FILE"
  echo "Relatório gerado em: $REPORT_FILE" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"

  echo "--- Buscando por padrões de risco ---" >> "$REPORT_FILE"
  # Exemplos de padrões de risco (adicione mais conforme necessário)
  # - Execução de comandos externos (child_process, exec, eval)
  # - Acesso a variáveis de ambiente sensíveis
  # - Requisições de rede (fetch, axios, http)
  # - Manipulação de arquivos fora do diretório da skill
  # - Uso de 'npx' ou 'npm install' dentro da skill

  echo "\n[WARNING] Execução de comandos externos (exec, eval, child_process):" >> "$REPORT_FILE"
  rg -n -i "exec|eval|child_process|spawn|fork|system\(|require('child_process')" "$SKILL_PATH" >> "$REPORT_FILE" || echo "Nenhum padrão encontrado." >> "$REPORT_FILE"

  echo "\n[WARNING] Acesso a variáveis de ambiente sensíveis (process.env):" >> "$REPORT_FILE"
  rg -n -i "process\.env\.[A-Z_]+" "$SKILL_PATH" >> "$REPORT_FILE" || echo "Nenhum padrão encontrado." >> "$REPORT_FILE"

  echo "\n[WARNING] Requisições de rede (fetch, axios, http, https):" >> "$REPORT_FILE"
  rg -n -i "fetch\(|axios\.|http\.|https\.|request\(|node-fetch" "$SKILL_PATH" >> "$REPORT_FILE" || echo "Nenhum padrão encontrado." >> "$REPORT_FILE"

  echo "\n[WARNING] Manipulação de arquivos fora do diretório da skill (../, /etc, /root, /var):" >> "$REPORT_FILE"
  rg -n "\.\./|/etc/|/root/|/var/" "$SKILL_PATH" >> "$REPORT_FILE" || echo "Nenhum padrão encontrado." >> "$REPORT_FILE"

  echo "\n[INFO] Arquivos detectados:" >> "$REPORT_FILE"
  find "$SKILL_PATH" -type f >> "$REPORT_FILE"

  echo "Auditoria concluída. Relatório salvo em: $REPORT_FILE"
else
  echo "Comando desconhecido: $COMMAND"
  echo "Uso: $0 audit ..."
  exit 1
fi
