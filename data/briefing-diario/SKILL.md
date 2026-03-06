---
name: briefing diario
description: Fornece um dashboard visual para informações do dia a dia como localização, clima, economia, previsão do tempo. Use sempre que o usuário pedir "briefing diário" ou o comando "briefing".
---

# Skill: Resumo do Dia

Esta Skill transforma o OpenClaw em um assistente de contexto local, compilando dados de múltiplas fontes gratuitas em um dashboard.

## Instruções para o agente

### 1. Localização
Identifique a cidade do Usuário (padrão: Belo Horizonte, -19.9208, -43.9378)

### 2. Coleta de Dados

**Data e Hora:**
- Use `TZ="America/Sao_Paulo" date` para obter a data/hora correta do usuário
- Formato: "22 de fevereiro de 2026, 16:27"
- Traduza o mês para português

**Clima e Astronomia:**
Use o endpoint da Open-Meteo:
```
https://api.open-meteo.com/v1/forecast?latitude=-19.9208&longitude=-43.9378&daily=uv_index_max,sunset,sunrise&hourly=precipitation_probability&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto
```

Extraia e mapeie:
- `current.temperature_2m` → TEMP
- `current.apparent_temperature` → FEEL
- `current.wind_speed_10m` → VENTO
- `current.relative_humidity_2m` → UMIDADE
- `daily.uv_index_max[0]` → UV_INDEX
- `daily.sunrise[0]` → SUNRISE
- `daily.sunset[0]` → SUNSET
- `current.weather_code` → PREVISÃO_TEXTO (mapeie códigos WMO para texto em português)
- `hourly.precipitation_probability` → CHANCE_DE_CHUVA (identifique a probabilidade para a hora atual)

**Cotações:**
Use a AwesomeAPI:
```
https://economia.awesomeapi.com.br/json/last/USD-BRL,JPY-BRL,BTC-BRL,KRW-BRL,EUR-BRL
```

**Feriados:**
```
https://date.nager.at/api/v3/PublicHolidays/2026/BR
```

### 3. Regras de Formatação

- O output DEVE ser gerado dentro de um bloco de código (markdown code block) para preservar o alinhamento ASCII.
- Use exatamente o template visual abaixo.
- Traduza os nomes das fases da lua e condições climáticas para Português do Brasil.

### 4. Mapeamento de Códigos WMO

| Código | Texto |
|--------|-------|
| 0 | Céu limpo |
| 1, 2, 3 | Parcialmente nublado |
| 45, 48 | Neblina |
| 51, 53, 55 | Chuvisco |
| 61, 63, 65 | Chuva |
| 71, 73, 75 | Neve |
| 80, 81, 82 | Pancadas de chuva |
| 95 | Tempestade |
| 96, 99 | Granizo |

### 5. Níveis de UV

| UV Index | Risco | Dica |
|----------|-------|------|
| 0-2 | Baixo | Sem proteção necessária |
| 3-5 | Moderado | Use protetor solar |
| 6-7 | Alto | Evite exposição ao sol das 10h-16h |
| 8-10 | Muito Alto | Proteção essencial |
| 11+ | Extremo | Evite exposição ao sol |

## Template de Saída

O agente deve preencher as variáveis e manter este layout:

```
🌍 Tudo sobre onde você mora
🌄 Belo Horizonte - [DATA ATUAL], [HORA]

☀️ CLIMA AGORA
🌡 [TEMP]ºC (sensação [FEEL]ºC)
🌀 Vento: [VENTO] km/h
💧 Umidade: [UMIDADE]%
☁️ Previsão: [PREVISÃO_TEXTO]
🌧 Chance de Chuva: [CHANCE_DE_CHUVA]%

📊 ÍNDICES DO DIA
🌞 UV: [UV_INDEX] ([RISCO] - [DICA_UV])
🌅 Sol nasce: [SUNRISE] | põe: [SUNSET]

💵 COTAÇÕES
💲 Dólar: R$ [USD] ([USD_VAR]%)
💶 Euro: R$ [EUR] ([EUR_VAR]%)
💴 Iene: R$ [JPY] ([JPY_VAR]%)
🇰🇷 Won Sul-Coreano: R$ [KRW] ([KRW_VAR]%)
₿ Bitcoin: R$ [BTC] ([BTC_VAR]%)

📅 HOJE - [FERIADO_STATUS]

💡 DICA: [DICA_CONTEXTUAL]
```

## Observações

- Substitua todos os placeholders entre colchetes com os dados obtidos nas fontes acima.
- Caso alguma fonte falhe, use mensagens de erro amigáveis e placeholders como fallback.
- A data/hora devem refletir o momento da coleta dos dados.
- Esta skill está pronta para ser integrada ao seu fluxo de coleta automática e pode ser disparada via comando "dia", "resumo do dia" ou "briefing".
