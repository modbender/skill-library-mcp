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

SKILL_MD="$SKILL_PATH/SKILL.md"

if [ ! -f "$SKILL_MD" ]; then
  echo "Erro: SKILL.md não encontrado no caminho especificado: $SKILL_MD"
  exit 1
fi

echo "Verificando dependências para a skill '$SKILL_PATH'..."

# Tentativa de extrair dependências da seção 'Requisitos' do SKILL.md
# Esta é uma abordagem heurística e pode não ser perfeita para todos os SKILL.mds

DEPENDENCIES=$(grep -A 10 "## Requisitos" "$SKILL_MD" | grep "*   " | sed -E 's/\*\s*([a-zA-Z0-9._-]+)(.*)/\1/g' | tr '\n' ' ')

if [ -z "$DEPENDENCIES" ]; then
  echo "Aviso: Nenhuma dependência foi extraída automaticamente do SKILL.md. Por favor, verifique manualmente."
  exit 0
fi

echo "Dependências identificadas no SKILL.md: $DEPENDENCIES"
echo "\n--- Verificando a presença das dependências: ---"

RETURN_CODE=0
for dep in $DEPENDENCIES;
do
  # Remover parênteses e outros caracteres que podem vir junto com o nome da dependência
  CLEAN_DEP=$(echo "$dep" | sed -E 's/[^a-zA-Z0-9_-].*//')
  if [ -z "$CLEAN_DEP" ]; then
    continue
  fi

  echo -n "Verificando '$CLEAN_DEP': "
  if command -v "$CLEAN_DEP" &> /dev/null;
  then
    echo "[OK]"
  else
    echo "[FALHA] - Não encontrado no PATH."
    RETURN_CODE=1
  fi
done

if [ $RETURN_CODE -eq 0 ]; then
  echo "\nTodas as dependências identificadas parecem estar instaladas."
else
  echo "\nUma ou mais dependências identificadas não foram encontradas. Por favor, instale-as manualmente."
fi

exit $RETURN_CODE
