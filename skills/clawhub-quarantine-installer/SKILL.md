---
name: clawhub-quarantine-installer
description: Instala e audita skills do ClawHub em um ambiente de quarentena isolado para análise de segurança, permitindo revisar riscos antes de promover para produção. Use esta skill para testar habilidades de terceiros que o ClawHub sinaliza como suspeitas, investigar suas dependências e comportamento, e gerar relatórios de auditoria básicos.
homepage: https://github.com/alessandropcostabr/clawhub-quarantine-installer
---

# Clawhub Quarantine Installer

## Overview

Esta skill automatiza a instalação de habilidades do ClawHub em um diretório de quarentena dedicado (`$HOME/.openclaw/clawhub-quarantine/skills/`) e executa um script de auditoria básica para identificar potenciais riscos. Ela é projetada para permitir uma análise manual mais segura de skills antes de integrá-las ao seu ambiente de produção do OpenClaw.

## Workflow de Uso

1.  **Instalar uma Skill em Quarentena:**
    *   Execute o script `scripts/install_and_audit.sh` com o nome da skill desejada.
    *   Exemplo: `bash ~/.openclaw/workspace/skills/clawhub-quarantine-installer/scripts/install_and_audit.sh <nome-da-skill>`
    *   **Importante:** O script `install_and_audit.sh` usa `npx clawhub install --force`. Este comando irá **baixar e executar código remoto** do registro `npm`. **É crucial que esta skill seja executada APENAS em um ambiente isolado (como uma VM ou container Docker) que não tenha acesso a dados sensíveis ou à sua máquina de produção.** A quarentena isolada é projetada para mitigar, mas não eliminar, todos os riscos.
    *   **Nota:** A flag `--force` é usada para instalar skills sinalizadas como suspeitas pelo ClawHub.

2.  **Revisar o Relatório de Auditoria:**
    *   Um relatório de auditoria será gerado em `$HOME/.openclaw/clawhub-quarantine/reports/<nome-da-skill>-audit-<timestamp>.txt`.
    *   Este relatório lista os arquivos da skill e procura por padrões de risco (comandos perigosos, acessos de rede, dicas de segredos) usando `ripgrep`.

3.  **Inspeção Manual Aprofundada:**
    *   Acesse o diretório da skill em quarentena (`$HOME/.openclaw/clawhub-quarantine/skills/<nome-da-skill>`).
    *   Examine o `SKILL.md` da skill e seus arquivos de código-fonte (se houver) e dependências para entender seu comportamento.
    *   Verifique as dependências externas e, se possível, revise seus repositórios no GitHub para issues de segurança ou informações adicionais.

4.  **Promover para Produção (Manual):**
    *   Se, após a revisão manual e a auditoria, a skill for considerada segura, ela pode ser movida manualmente para `~/.openclaw/workspace/skills/`.

## Scripts

### `scripts/install_and_audit.sh`

Este script é o ponto de entrada da skill. Ele:
*   Recebe o nome da skill como argumento.
*   Cria os diretórios de quarentena e relatórios, se não existirem.
*   Instala a skill no diretório de quarentena (`$HOME/.openclaw/clawhub-quarantine/skills/`) usando `npx clawhub install --force`.
*   Chama o script `clawhub-quarantine.sh audit` para gerar um relatório de segurança, passando o caminho da skill e o diretório de relatórios.

### `scripts/clawhub-quarantine.sh`

Este script auxiliar realiza as operações de auditoria. Atualmente, ele suporta o comando `audit`, que:
*   Recebe o caminho completo da skill em quarentena e o diretório para salvar o relatório.
*   Utiliza `ripgrep` para buscar por padrões de código potencialmente perigosos dentro da skill (e.g., execução de comandos externos, acesso a variáveis de ambiente sensíveis, requisições de rede).
*   Gera um relatório detalhado com os achados da auditoria.

## Requisitos (Pré-requisitos)

Para que esta skill funcione corretamente, os seguintes softwares devem estar instalados e disponíveis no PATH do ambiente onde o OpenClaw está rodando:

*   **Node.js**: Versão `>=22` (necessário para `npm` e `npx`).
*   **`clawhub` CLI**: Pode ser instalado globalmente via `npm i -g clawhub`.
*   **`ripgrep` (`rg`)**: Uma ferramenta de busca de padrões (similar ao `grep`, mas mais rápido) utilizada pelo script de auditoria.

## Descobertas e Lições Aprendidas (Exemplo com a skill 'gram')

*   **Alertas de Segurança:** O ClawHub utiliza "VirusTotal Code Insight" para sinalizar skills suspeitas (ex: uso de chaves criptográficas, APIs externas, `eval`). Isso é um ponto de partida crítico para a revisão.
*   **Quarentena Funcional:** A instalação em um diretório isolado (`$HOME/.openclaw/clawhub-quarantine/skills/`) é eficaz para conter a skill durante a análise.
*   **Auditoria por Padrões:** O script `clawhub-quarantine.sh audit` busca por padrões de risco comuns.
*   **Dependências de Alto Risco:** Skills podem depender de bibliotecas que interagem com o sistema operacional em baixo nível (ex: `sweet-cookie` para acesso a cookies de navegador, decifração de senhas do keyring e execução de comandos externos via `child_process`). Essas dependências exigem a maior atenção na revisão.
*   **Incompatibilidade de API:** Mesmo com autenticação, as APIs de terceiros (como o Instagram) podem bloquear ou desativar funcionalidades para automação (ex: User-Agent mismatch, Invalid media_id, Too Many Requests). Isso afeta a utilidade da skill.
