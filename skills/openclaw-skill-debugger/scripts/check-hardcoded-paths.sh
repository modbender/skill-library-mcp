#!/bin/bash

SKILL_PATH="$1"

if [ -z "$SKILL_PATH" ]; then
  echo "Uso: $0 <caminho-da-skill>"
  exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
  echo "Erro: O caminho especificado não é um diretório de skill válido: $SKILL_PATH"
  exit 1
fi

echo "Verificando a skill '$SKILL_PATH' em busca de caminhos hardcoded..."

# Padrões comuns de caminhos hardcoded:
# - Caminhos absolutos que começam com / (exceto /bin, /usr, /dev, etc. que são legítimos para comandos)
# - Caminhos com diretórios home de usuários específicos (e.g., /home/alessandro)
# - Caminhos para diretórios de sistema (/etc, /var, /root)

# Usando ripgrep para procurar padrões. A opção -q (quiet) é para não imprimir o conteúdo da linha, apenas indicar se encontrou.
# A opção -l (files-with-matches) lista apenas os arquivos que contêm correspondências.

# Excluir alguns diretórios comuns de dependências para evitar falsos positivos
EXCLUDE_DIRS="--exclude-dir node_modules --exclude-dir .git --exclude-dir build"

# Busca por caminhos absolutos começando com / que não são comandos comuns ou diretórios de sistema esperados.
# Esta é uma busca heurística e pode precisar de ajustes dependendo do contexto da skill.

echo "\n--- Caminhos absolutos suspeitos: ---"
rg -n "^/([a-zA-Z0-9_-]+/)+" "$SKILL_PATH" $EXCLUDE_DIRS |
  grep -v "/bin/" |
  grep -v "/usr/" |
  grep -v "/dev/" |
  grep -v "/proc/" |
  grep -v "/sys/" || echo "Nenhum encontrado." # Ajuste conforme necessário

echo "\n--- Caminhos de usuário hardcoded (/home/, /root/): ---"
rg -n "/home/[a-zA-Z0-9_-]+/|/root/" "$SKILL_PATH" $EXCLUDE_DIRS || echo "Nenhum encontrado."

echo "\n--- Caminhos de sistema (/etc/, /var/, /opt/): ---"
rg -n "/etc/|/var/|/opt/" "$SKILL_PATH" $EXCLUDE_DIRS || echo "Nenhum encontrado."

echo "Verificação de caminhos hardcoded concluída. Revise os resultados acima."
