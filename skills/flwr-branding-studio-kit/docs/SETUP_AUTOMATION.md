# Configuração da Automação (SkillsMP/ClawHub)

Para que o GitHub publique sua skill automaticamente no marketplace, você precisa adicionar um segredo.

## Passo 1: Obter o Token do ClawHub

1.  Crie sua conta ou faça login no [ClawHub](https://clawhub.com) (ou plataforma equivalente do SkillsMP).
2.  Vá nas configurações da sua conta (Settings/Profile).
3.  Procure por "API Tokens" ou "Access Tokens".
4.  Gere um novo token e **copie-o** (ele começa geralmente com `clh_`).

## Passo 2: Adicionar ao GitHub

1.  Vá até o seu repositório no GitHub.
2.  Clique na aba **Settings** (Configurações).
3.  No menu lateral esquerdo, clique em **Secrets and variables** > **Actions**.
4.  Clique no botão verde **New repository secret**.
5.  Preencha os campos:
    *   **Name:** `CLAWDHUB_TOKEN` (Exatamente assim, letras maiúsculas).
    *   **Secret:** Cole o token que você copiou no Passo 1.
6.  Clique em **Add secret**.

## Passo 3: Publicar!

Agora, sempre que você criar uma **Release** no GitHub (ex: `v1.0.1`), a automação vai rodar sozinha e publicar sua atualização no marketplace! 🚀
