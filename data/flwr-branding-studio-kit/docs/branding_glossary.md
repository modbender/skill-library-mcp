# Glossário de Branding e IA

Termos e conceitos chave extraídos do webinar sobre estratégia de marca com IA, incluindo definições técnicas apresentadas nos slides.

## Conceitos de Estratégia de Marca
- **Plataforma de Marca:** Um resumo visual e estratégico da marca. Geralmente inclui posicionamento, propósito, diferenciais, valores e personalidade. Serve para consulta rápida.
- **Briefing Denso:** A prática de fornecer à IA transcrições completas de reuniões, entrevistas e dados brutos (Raw Data), em vez de resumos, para permitir que o modelo gere insights mais profundos e menos alucinados.
- **Ecossistema de Conteúdo:** O fluxo de trabalho sugerido: `Gravação de Reunião -> Transcrição (ex: Read.ai) -> Análise na IA (Claude) -> Estratégia`.

## Conceitos Técnicos de IA (Apresentados no Webinar)
- **LLM (Large Language Model):** Tipo de modelo de inteligência artificial treinado com enormes volumes de dados textuais para compreender, gerar e manipular linguagem humana em grande escala.
- **Janela de Contexto (Context Window):** A "memória de curto prazo" da IA. É a quantidade de texto (tokens) que o modelo consegue processar de uma vez só para entender e responder sua pergunta.
    *   *Analogia:* É como contar uma história onde a pessoa precisa lembrar do começo para entender o final.
    *   *Capacidade:* Varia por modelo (ex: Claude tem uma janela muito maior que o GPT padrão, permitindo processar livros inteiros).
- **Tokens:** A unidade básica de texto para a IA (aproximadamente 4 caracteres ou 0.75 palavras em inglês). A "moeda" de troca e limite dos modelos.
- **Alucinação:** Quando a IA inventa informações factuais ou características da marca por falta de restrições claras (Contexto/Exemplo) no prompt.

## Ferramentas e Funcionalidades
- **Claude Projects:** Funcionalidade que permite criar "cápsulas" de conhecimento com instruções (Custom Instructions) e arquivos específicos (Artifacts/Knowledge) que formam a memória do projeto.
- **Artefatos (Artifacts):** Recurso do Claude que gera documentos, códigos ou layouts em uma janela separada, permitindo visualização, edição e exportação imediata.
- **Sentence Case (Escrita Tradicional):** Instrução de prompt para evitar Title Case (Todas As Palavras Com Maiúscula). Essencial para que os textos gerados pela IA não pareçam "marketing genérico" ou excessivamente artificiais.
