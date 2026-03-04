---
name: context-gatekeeper
description: Keeps the conversation token-friendly by summarizing recent exchanges, surfacing pending actions, and delivering a compact briefing for each turn before calling the model. Trigger this skill whenever you need to prune a bloated thread or keep the next prompt lean.
author: Davi Marques
---

# Context Gatekeeper

## Objetivo
Reduzir o volume de tokens enviados ao modelo preservando apenas o essencial: o resumo das decisões, os próximos passos e os trechos mais recentes da conversa. Este skill roda em paralelo à sua rotina habitual, produzindo o artefato `context/current-summary.md` que serve como contexto de substituição (em vez de reenviar toda a conversa).

## Fluxo mínimo
1. **Registre as trocas**: a cada prompt/resposta, grave uma linha formatada `ROLE: texto` em um arquivo de histórico (`context/history.txt` ou qualquer caminho acessível). Exemplo:
   ```
   USER: Quero definir metas para o Q2
   ASSISTANT: Fiz um plano com marcos e métricas
   ```
2. **Execute o guardião**:
   ```bash
   python skills/context-gatekeeper/scripts/context_gatekeeper.py \
     --history context/history.txt \
     --summary context/current-summary.md
   ```
   O script limita o resumo (até 6 sentenças por padrão), extrai atividades abertas (TODO, próxima ação, tarefa, follow-up) e inclui as últimas 4 jogadas para contexto imediato.
3. **Use o resumo**: antes de chamar a API (ou responder ao usuário), injete o conteúdo de `context/current-summary.md` e cite os itens pendentes. Apenas depois disso, se for necessário, adicione as últimas trocas concretas (máximo de 2-3 mensagens) para clareza imediata.
4. **Repita**: atualize `context/history.txt` com a nova resposta e execute o script novamente antes do próximo turno.

## Argumentos do script
- `--history`: caminho do arquivo com o log das trocas (cada linha deve ser `ROLE: texto`). Usa STDIN se omitido.
- `--summary`: destino do resumo (substitui o arquivo se já existir).
- `--max-summary-sents`: limite de sentenças resumidas (padrão 6).
- `--max-recent-turns`: quantas trocas finais aparecerão na seção "Últimos turnos" (padrão 4).

## Dica de operação diária
- Monte um cron/loop leve que chame o script antes de cada resposta automática.
- Guarde um paralelo `context/pending-tasks.md` e copie a seção "Pendências" do resumo para lá.
- Sempre cite o caminho do resumo no parágrafo inicial da resposta (por exemplo: "Resumo compacto: ...") para facilitar auditoria.

## Por quê isso funciona?
OpenClaw já persiste memórias em arquivos Markdown e executa `/compact` quando precisa. Este skill assume a mesma disciplina: em vez de confiar nos 100+ mensagens antigas que ainda estão no contexto, você carrega um briefing de 1 página antes de cada chamada. Economiza tokens e mantém o modelo focado no que realmente importa (decisões, pendências, mudanças recentes).
