# Guia de Estudo: Estratégia de Marca com IA

Este guia consolida os aprendizados do webinar sobre como utilizar Inteligência Artificial para criar estratégias de branding robustas e eficientes.

## 1. O Fluxo de Trabalho (Workflow)

A grande virada de chave apresentada é a mudança de "Criar do zero" para "Orquestrar informações".

**O Processo:**
1.  **Coleta:** Grave reuniões, entrevistas e briefings com o cliente.
2.  **Transcrição:** Use ferramentas para transformar o áudio em texto (transcrição completa, não resumo).
3.  **Processamento (Claude):** Importe a transcrição e documentos de apoio para um "Projeto" no Claude.
4.  **Estratégia (RACE):** Use o framework RACE para extrair e estruturar a estratégia.
5.  **Refinamento:** Itere com a IA para ajustar tom de voz e gerar artefatos (apresentações, sites, guias).

## 2. O Framework RACE

Para separar "a criança do adulto" na estruturação de prompts, utilize o método **RACE**:

-   **[R]ole (Papel):** Dê um cargo senior à IA.
-   **[A]ction (Ação):** Liste o que deve ser feito.
-   **[C]ontext (Contexto):** Dê os dados do cliente (batalhas, concorrentes, dores).
-   **[E]xample (Exemplo):** Dê o formato e o estilo de escrita desejado.

> *Consulte o artefato `artifacts/race_framework.md` para detalhes.*

## 3. Estudo de Caso: Brand_X

O webinar utiliza a criação da marca fictícia (ou real) **Brand_X** para ilustrar o processo.

-   **Problema:** O mercado de skincare é complexo e "clean" demais.
-   **Solução Brand_X:** Skincare organizado pelo tempo (Manhã, Tarde, Noite), não por química complexa.
-   **Diferencial de IA:** A IA foi instruída a rejeitar a linguagem "colorida e luminosa" padrão e adotar uma postura direta, econômica e "Wabi-Sabi" (simplicidade imperfeita).

> *Veja o prompt real em `artifacts/saori_branding_prompt.md`.*

## 4. Dicas de Ouro do Presenter

-   **Não peça resumos:** Peça "transcrições completas". Resumos perdem a nuance que a IA precisa para captar a "voz" do cliente.
-   **Artefatos são Poder:** Use a função de "Artifacts" do Claude para gerar entregáveis finais (tabelas, apresentações, sites) prontos para o cliente.
-   **Escrita "Tradicional":** Force a IA a usar *sentence case* (apenas a primeira letra maiúscula). Isso reduz a "cara de IA" e de "marketing barato" dos textos.
-   **Evite Adjetivos Vazios:** Instrua a IA a evitar pares de adjetivos como "calmo e tranquilo" ou "inovador e disruptivo". Prefira descrições funcionais.

## 5. Próximos Passos
1.  Crie um "Projeto" no Claude para sua próxima marca.
2.  Suba todos os PDFs e transcrições que você tem.
3.  Aplique o prompt RACE adaptado.
4.  Peça para gerar uma "Plataforma de Marca" como artefato.
