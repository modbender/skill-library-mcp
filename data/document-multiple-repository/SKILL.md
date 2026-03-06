---
name: document-multiple-repository
description: Gera documentação técnica consolidada para sistemas de software com múltiplos repositórios (frontend, backend, microservices, wikis). Use quando o usuário pedir documentação de multi-repo, visão de arquitetura consolidada, mapeamento de repositórios ou documentação a partir de vários repos locais.
version: 0.1.0
---

# Skill: document-multiple-repository

## Propósito
Gerar documentação técnica consolidada para sistemas de software compostos por múltiplos repositórios
(frontend, backend, microservices, infra, docs, wikis) armazenados localmente em um sistema de arquivos compartilhado.

## Premissas
- Todos os repositórios (incluindo Wikis) já estão clonados localmente.
- Múltiplos repositórios podem compor um único sistema lógico.
- Wikis são tipicamente repositórios git com o sufixo `.wiki`.
- As linguagens podem incluir Java, Python, JavaScript.
- Não existem convenções rígidas de nomenclatura.
- A execução é manual via agente de IA (VS Code, Copilot, Gemini CLI, etc).

## Entradas (Inputs)
- ROOT_PATH: pasta contendo múltiplos sistemas.
- OUTPUT_PATH: destino para a documentação gerada.
- TEMPLATES_PATH: templates para README, ARCHITECTURE, API, CODE_COMMENTS.

## Etapas de Processamento

### 1. Descoberta de Sistemas (Discover Systems)
- Escanear ROOT_PATH recursivamente.
- Detectar repositórios git (pastas .git).
- Identificar repositórios de Wiki (nome da pasta termina com `.wiki`).
- Agrupar (cluster) repositórios por proximidade no sistema de arquivos.
- Tratar cada grupo (código + wikis) como um único sistema lógico.

### 2. Análise de Repositórios (Analyze Repositories)
Para cada repositório:
- Detectar o tipo (code, docs ou wiki).
- Se for Code (Código):
  - Detectar linguagem e framework (Spring, Django, Node, etc).
  - Detectar o tipo de serviço (backend, frontend, microservice, infra).
  - Extrair: README, build files, manifests, API routes, entities, configs.
- Se for Wiki:
  - Detectar páginas principais (Home.md, index.md).
  - Extrair: guias de infraestrutura, tutoriais de setup, processos de negócio (DoR/DoD) e links para legislação externa ou ativos.
- Se for Docs:
  - Detectar geradores estáticos (MkDocs, Sphinx, etc).
  - Extrair: manuais funcionais e guias de usuário.

### 3. Geração de Documentação (Generate Documentation)
Criar para cada sistema:
- SYSTEM_OVERVIEW.md (Visão consolidada incluindo negócio e tecnologia).
- ARCHITECTURE.md.
- REPOSITORY_MAP.md.
- DEPLOYMENT.md (Informações mescladas de manifests de código e guias de wiki).
- PROCESSES_AND_GUIDELINES.md (Extraído de Wikis: DoR, DoD, regras de contribuição).

Criar para cada repositório:
- README.generated.md.
- API.generated.md.
- CODE_STRUCTURE.md (para repositórios de código).
- WIKI_SUMMARY.md (para repositórios de wiki).

### 4. Estrutura de Saída (Output Structure)
OUTPUT_PATH/
  system-name/
    SYSTEM_OVERVIEW.md
    ARCHITECTURE.md
    REPOSITORY_MAP.md
    DEPLOYMENT.md
    PROCESSES_AND_GUIDELINES.md
    repos/
       repo-name/
         README.generated.md
         API.generated.md
         CODE_STRUCTURE.md
         WIKI_SUMMARY.md

## Execução
O agente recebe o comando:
"Run skill document-multiple-repository on <ROOT_PATH>"

## Restrições (Constraints)
- Não executar código.
- Não modificar os repositórios originais.
- Apenas documentação.