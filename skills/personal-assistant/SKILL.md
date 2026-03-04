---
name: personal-assistant
description: Personal daily briefing and productivity assistant. Generates morning briefings with priorities, habits, and self-care reminders. Use when starting your day, planning tasks, or maintaining daily routines and personal development. A minimalist personal productivity skill focused on you.
---

# Personal Assistant

## Overview / Visão Geral

Generate personalized daily briefings with morning motivation, priorities, habit tracking, and evening reflection. Focus on productivity and well-being with minimal complexity.

Gerencie briefings diários personalizados com motivação matinal, prioridades, hábitos e reflexão noturna. Foque em produtividade e bem-estar com complexidade mínima.

## Quick Start / Início Rápido

```bash
# Generate daily briefing
python3 scripts/daily_briefing.py --location Columbus --summary

# Save to file
python3 scripts/daily_briefing.py --output daily_briefing.json
```

## Workflow / Fluxo de Trabalho

### Morning Routine / Rotina Matinal

Start your day with a structured briefing:

1. **Motivation:** Positive start with intention / Motivação: começo positivo com intenção
2. **Weather:** Check conditions for the day / Clima: verifique condições do dia
3. **Priorities:** Set top 3 tasks / Prioridades: defina top 3 tarefas
4. **Habits:** Track daily goals / Hábitos: acompanhe metas diárias

### During the Day / Durante o Dia

Use briefing as your reference:
- Check priorities list / Verifique lista de prioridades
- Mark completed habits / Marque hábitos completados
- Take breaks and stay hydrated / Faça pausas e mantenha-se hidratado

### Evening Review / Revisão Noturna

End your day with reflection:
- What did I accomplish? / O que eu conquistei?
- What am I grateful for? / Pelo que eu sou grato?
- What could I improve? / O que eu poderia melhorar?
- Set tomorrow's priority / Defina prioridade de amanhã

## Usage / Uso

### Generate Briefing / Gerar Briefing

```bash
python3 scripts/daily_briefing.py --location Columbus --summary
```

Output:

```
📋 Daily Briefing - 2026-02-11 (Wednesday)

🌅 Good Morning!
Start your day with focus and intention.

🌡 Weather Check
Check the weather in Columbus before heading out.

🎯 Today's Focus
Top 3 priorities:
1. _____________________________
2. _____________________________
3. _____________________________

✅ Daily Habits
☐ Morning routine
☐ Hydration goals
☐ Learning time
☐ Evening review

💚 Self-Care
Remember to take breaks and stay hydrated.

🌙 Evening Review
1. What did I accomplish today?
2. What am I grateful for?
3. What could I have done better?
4. Tomorrow's top priority?
```

### Parameters / Parâmetros

| Parameter | Description | Descrição | Default |
|-----------|-------------|-------------|----------|
| `--location` | Your city / Sua cidade | Columbus | `--location Miami` |
| `--output` | Output file / Arquivo de saída | daily_briefing.json | `--output briefing.json` |
| `--summary` | Print readable output / Imprimir saída legível | false | `--summary` |

## Daily Automation / Automação Diária

Set up morning briefings with OpenClaw cron:

```bash
# Every day at 7 AM
openclaw cron add \
  --schedule "0 7 * * *" \
  --tz "America/New_York" \
  --message "Generate my daily briefing"
```

Or manually:

```bash
# Morning (7 AM)
python3 scripts/daily_briefing.py --location Columbus --summary

# Evening (9 PM)
python3 scripts/daily_briefing.py --location Columbus --summary
```

## Output Format / Formato de Saída

### JSON Structure

```json
{
  "generated_at": "2026-02-11T07:00:00.000Z",
  "location": "Columbus",
  "date": "2026-02-11",
  "weekday": "Wednesday",
  "sections": [
    {
      "title": "🌅 Good Morning!",
      "content": "Start your day...",
      "type": "motivation"
    }
  ]
}
```

## Key Sections / Seções Principais

### 🌅 Morning Motivation / Motivação Matinal
Positive start to your day with focus and intention.

Começo positivo do seu dia com foco e intenção.

### 🎯 Today's Focus / Foco do Dia
Top 3 priorities with space for your own tasks.

Top 3 prioridades com espaço para suas tarefas.

### ✅ Daily Habits / Hábitos Diários
Track recurring daily goals for personal development.

Acompanhe metas recorrentes para desenvolvimento pessoal.

### 💚 Self-Care / Autocuidado
Reminders for hydration, breaks, and work-life balance.

Lembretes para hidratação, pausas e equilíbrio vida-trabalho.

### 🌙 Evening Reflection / Reflexão Noturna
Structured reflection questions for growth and gratitude.

Reflexão estruturada para crescimento e gratidão.

## Features / Funcionalidades

- ✅ Simple and fast / Simples e rápido
- 📝 Human-readable output / Saída legível para humanos
- 🎨 Emoji-enhanced sections / Seções com emojis
- 🌍 Location-aware / Consciente de localização
- 💾 JSON export for automation / Exportação JSON para automação
- 📅 Weekday-aware / Consciente do dia da semana

## How It Works / Como Funciona

1. **Date & Location:** Gets current date and your location / Obtém data atual e sua localização
2. **Section Generation:** Creates 5 key sections / Cria 5 seções principais
3. **Formatting:** Structures output for easy reading / Estrutura saída para leitura fácil
4. **Saving:** Exports to JSON for integrations / Exporta para JSON para integrações

## Use Cases / Casos de Uso

### Personal Productivity / Produtividade Pessoal

Start each morning with a structured briefing to set focus and priorities.

Comece cada manhã com um briefing estruturado para definir foco e prioridades.

### Personal Development / Desenvolvimento Pessoal

Use habit tracking and evening reflection to build self-awareness and growth.

Use rastreamento de hábitos e reflexão noturna para construir autoconsciência e crescimento.

### Remote Work / Trabalho Remoto

Maintain structure and self-care while working from home with briefings and breaks.

Mantenha estrutura e autocuidado enquanto trabalha de casa com briefings e pausas.

### Well-being / Bem-Estar

Stay mindful of self-care with regular hydration and break reminders.

Mantenha-se consciente do autocuidado com lembretes regulares de hidratação e pausas.

## Philosophy / Filosofia

This skill follows minimal productivity principles:
- Focus on what matters / Foque no que importa
- Simple over complex / Simples sobre complexo
- Consistency > intensity / Consistência > intensidade
- Progress, not perfection / Progresso, não perfeição

## Resources / Recursos

### scripts/daily_briefing.py
Main script that generates daily briefings with all sections.

Script principal que gera briefings diários com todas as seções.

### references/productivity.md
Tips and techniques for personal productivity and habit formation.

Dicas e técnicas para produtividade pessoal e formação de hábitos.

## Dependencies / Dependências

**None!** / **Nenhuma!**

Uses only Python standard library - no external dependencies required.

Usa apenas biblioteca padrão do Python - sem dependências externas necessárias.

## Tips / Dicas

### Morning Routine / Rotina Matinal

- Read your briefing while having coffee / Leia seu briefing enquanto toma café
- Fill in priorities the night before / Preencha prioridades na noite anterior
- Keep it simple - max 3 priorities / Mantenha simples - máx 3 prioridades

### Evening Routine / Rotina Noturna

- Spend 5 minutes on reflection / Gaste 5 minutos na reflexão
- Write down tomorrow's priority / Anote a prioridade de amanhã
- Practice gratitude daily / Pratique gratidão diariamente

### Building Habits / Construindo Hábitos

- Start with 1-2 habits / Comece com 1-2 hábitos
- Focus on consistency, not intensity / Foque na consistência, não na intensidade
- Track visually (use ☐/☑) / Acompanhe visualmente (use ☐/☑)

## Customization / Personalização

### Adding New Sections / Adicionando Novas Seções

Edit `scripts/daily_briefing.py` and add to the `generate_briefing()` function.

Edite `scripts/daily_briefing.py` e adicione à função `generate_briefing()`.

### Modifying Sections / Modificando Seções

Each section has: title, content, type. Customize as needed.

Cada seção tem: título, conteúdo, tipo. Personalize conforme necessário.

## License / Licença

MIT License - Use freely for personal and commercial purposes.
Licença MIT - Use livremente para fins pessoais e comerciais.

## Credits / Créditos

Created by **Gustavo (GustavoZiaugra)** with OpenClaw
Criado por **Gustavo (GustavoZiaugra)** com OpenClaw

- Simple productivity framework / Framework de produtividade simples
- Personal well-being focus / Foque em bem-estar pessoal
- Minimal and functional approach / Abordagem minimalista e funcional

---

**Find this and more OpenClaw skills at ClawHub.com**
**Encontre este e mais skills do OpenClaw em ClawHub.com**

⭐ **Star this repository if you find it useful!**
**⭐ Dê uma estrela neste repositório se você achar útil!**

📋 **Your personal assistant, just for you.**
📋 **Seu assistente pessoal, só para você.**
