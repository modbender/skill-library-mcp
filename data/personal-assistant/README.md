# Personal Assistant

**📋 Your personal daily briefing and productivity assistant / Seu assistente pessoal de briefing diário e produtividade**

Generate structured daily briefings with morning motivation, priorities, habit tracking, and evening reflection. Simple, effective, focused on you.

Gerencie briefings diários estruturados com motivação matinal, prioridades, hábitos e reflexão noturna. Simples, efetivo, focado em você.

## Features / Funcionalidades

- 🌅 **Morning Briefing** / **Briefing Matinal** - Start your day with structure / Comece seu dia com estrutura
- 🎯 **Priority Setting** / **Definição de Prioridades** - Top 3 tasks with space to write / Top 3 tarefas com espaço para escrever
- ✅ **Habit Tracking** / **Acompanhamento de Hábitos** - Daily goals checklist / Lista de metas diárias
- 🌡 **Weather Context** / **Contexto de Clima** - Location-aware reminders / Lembretes conscientes de localização
- 🌙 **Evening Reflection** / **Reflexão Noturna** - Structured growth questions / Questões de crescimento estruturadas
- 💚 **Self-Care Reminders** / **Lembretes de Autocuidado** - Hydration, breaks, well-being / Hidratação, pausas, bem-estar

## Quick Start / Início Rápido

```bash
# Generate daily briefing
python3 scripts/daily_briefing.py --location Columbus --summary

# Save to file
python3 scripts/daily_briefing.py --output daily_briefing.json
```

## Installation / Instalação

1. **Clone this repository / Clone este repositório:**

```bash
git clone https://github.com/GustavoZiaugra/personal-assistant-skill.git
cd personal-assistant-skill
```

2. **Load skill into OpenClaw / Carregar skill no OpenClaw:**
   - Open OpenClaw Control UI
   - Go to Skills → Import Skill
   - Select this directory

## Usage / Uso

### Morning Briefing / Briefing Matinal

```bash
# Generate your daily briefing
python3 scripts/daily_briefing.py --location Columbus --summary
```

This shows:

```
📋 Daily Briefing - 2026-02-11 (Wednesday)

🌅 Good Morning!
Start your day with focus and intention.

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

### Daily Automation / Automação Diária

Set up morning briefings with OpenClaw cron:

```bash
# Every day at 7 AM
openclaw cron add \
  --schedule "0 7 * * *" \
  --tz "America/New_York" \
  --message "Generate my daily personal briefing"
```

This provides structure to your day automatically every morning.

## Philosophy / Filosofia

This skill is built on **minimal productivity** principles:

### Less is More / Menos é Mais

Focus on 3 priorities per day, not 10.
Foque em 3 prioridades por dia, não 10.

### Consistency > Intensity / Consistência > Intensidade

Small daily actions compound over time.
Pequenas ações diárias se multiplicam ao longo do tempo.

### Progress, Not Perfection / Progresso, Não Perfeição

Done is better than perfect. Celebrate wins, learn from failures.
Feito é melhor que perfeito. Celebre vitórias, aprenda com erros.

## Example Day / Exemplo de Dia

### Morning / Manhã

7:00 AM - Receive briefing via Telegram
7:05 AM - Review while drinking coffee
7:10 AM - Write your top 3 priorities
7:15 AM - Start your day

### During Day / Durante o Dia

- Check habits (water intake, breaks)
- Focus on priority #1
- Mark completed items

### Evening / Noite

9:00 PM - Receive evening prompts
9:05 PM - Spend 5 minutes reflecting
9:10 PM - Set tomorrow's priority
9:15 PM - Practice gratitude
9:20 PM - Rest

## Sections Explained / Seções Explicadas

### 🌅 Morning Motivation / Motivação Matinal

Sets positive tone for your day. Reminds you to start with intention, not reaction.

Define tom positivo para seu dia. Lembra você de começar com intenção, não reação.

### 🎯 Today's Focus / Foco do Dia

**Top 3 priorities only** - More feels overwhelming, fewer feels unambitious.

**Apenas top 3 prioridades** - Mais parece esmagador, menos parece subambicioso.

Write your priorities where you'll see them all day.

Escreva suas prioridades onde você as verá o dia todo.

### ✅ Daily Habits / Hábitos Diários

Track 4-5 key habits that build your ideal self over time.

Acompanhe 4-5 hábitos principais que constroem seu eu ideal ao longo do tempo.

Default habits:
- ☐ Morning routine (exercise, meditation, journal)
- ☐ Hydration (8 glasses of water)
- ☐ Learning time (30 min reading/course)
- ☐ Evening review (reflection questions)

### 💚 Self-Care / Autocuidado

Reminders that are easy to forget but crucial for wellbeing.

Lembretes fáceis de esquecer mas cruciais para bem-estar.

### 🌙 Evening Reflection / Reflexão Noturna

4 powerful questions for growth:

1. **Accomplishment:** What did I achieve? / **Conquista:** O que eu conquistei?
2. **Gratitude:** What am I thankful for? / **Gratidão:** Pelo que sou grato?
3. **Learning:** What could I improve? / **Aprendizado:** O que eu poderia melhorar?
4. **Planning:** Tomorrow's top priority? / **Planejamento:** Prioridade de amanhã?

## Use Cases / Casos de Uso

### Remote Worker / Trabalhador Remoto

Maintain structure and self-care while working from home. Briefing provides daily anchor.

Mantenha estrutura e autocuidado enquanto trabalha de casa. Briefing fornece ancora diária.

### Student / Estudante

Build consistency in study habits and prioritize assignments. Evening reflection reinforces learning.

Construa consistência em hábitos de estudo e priorize tarefas. Reflexão noturna reforça aprendizado.

### Entrepreneur / Empreendedor

Focus daily priorities on revenue-generating activities. Use reflection to iterate and improve.

Foque prioridades diárias em atividades que geram receita. Use reflexão para iterar e melhorar.

### Personal Development / Desenvolvimento Pessoal

Use habit tracking and reflection to build self-awareness and intentional growth.

Use rastreamento de hábitos e reflexão para construir autoconsciência e crescimento intencional.

## Customization / Personalização

### Add Your Own Sections / Adicione Suas Próprias Seções

Edit `scripts/daily_briefing.py`:

```python
# Add new section to briefing['sections']
briefing['sections'].append({
    'title': '🎨 Creative Time',
    'content': '30 min of art or music',
    'type': 'creative'
})
```

### Modify Existing Sections / Modifique Seções Existentes

Each section has customizable content. Edit the strings to match your style.

Cada seção tem conteúdo personalizável. Edite as strings para combinar com seu estilo.

## Benefits / Benefícios

- ✅ **Structure** - Start each day with clarity / **Estrutura** - Comece cada dia com clareza
- 🎯 **Focus** - Know your top priorities instantly / **Foco** - Conheça suas prioridades principais instantaneamente
- 🧘 **Habit Building** - Consistent daily goals / **Construção de Hábitos** - Metas diárias consistentes
- 📚 **Growth** - Evening reflection for continuous improvement / **Crescimento** - Reflexão noturna para melhoria contínua
- ⚡ **Fast** - No external dependencies, runs instantly / **Rápido** - Sem dependências externas, roda instantaneamente
- 🔒 **Private** - All data stays on your system / **Privado** - Todos os dados ficam no seu sistema

## Limitations / Limitações

- **Manual Entry Required:** Priorities and habits need to be filled by you.
- **Requer Entrada Manual:** Prioridades e hábitos precisam ser preenchidos por você.
- **Weather:** Location is for context only - actual weather requires separate skill.
- **Clima:** Localização é apenas para contexto - clima real requer skill separada.

## Dependencies / Dependências

**None!** / **Nenhuma!**

Uses only Python standard library.

Usa apenas biblioteca padrão do Python.

## License / Licença

MIT License - Use freely for personal and commercial purposes.
Licença MIT - Use livremente para fins pessoais e comerciais.

## Credits / Créditos

Created by **Gustavo (GustavoZiaugra)** with OpenClaw
Criado por **Gustavo (GustavoZiaugra)** com OpenClaw

- Minimal productivity philosophy / Filosofia de produtividade minimalista
- Personal growth focus / Foque em crescimento pessoal
- Simple and effective approach / Abordagem simples e efetiva

---

**Find this and more OpenClaw skills at ClawHub.com**
**Encontre este e mais skills do OpenClaw em ClawHub.com**

⭐ **Star this repository if you find it useful!**
**⭐ Dê uma estrela neste repositório se você achar útil!**

📋 **Your personal assistant, just for you.**
📋 **Seu assistente pessoal, só para você.**
