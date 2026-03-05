# Gas Price Alert / Alerta de Preço de Combustível

**⛽ Find cheapest gas prices with daily notifications / Encontre os preços mais baratos de combustível com alertas diários**

This OpenClaw skill helps you find and monitor gas prices, with special focus on Costco and other discount stations.

Este skill do OpenClaw ajuda você a encontrar e monitorar preços de combustível, com foco especial em Costco e outros postos com desconto.

## Features / Funcionalidades

- 🔍 **ZIP code search** - Search by any US ZIP code / Busca por qualquer CEP dos EUA
- 💰 **Best price detection** - Shows cheapest options first / Mostra opções mais baratas primeiro
- 📏 **Configurable radius** - Set your preferred search range / Defina o raio de busca preferido
- 🏠 **Costco support** - Special tracking of Costco locations / Rastreamento especial de locais da Costco
- ⏰ **Daily alerts** - Schedule automated notifications / Agende notificações automatizadas
- 🌍 **Works anywhere** - Supports any US location / Funciona em qualquer lugar dos EUA

## Quick Start / Início Rápido

### English

```bash
# Search by ZIP code
python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --summary

# Save to file
python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --output gas_prices.json
```

### Português

```bash
# Buscar por CEP
python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --summary

# Salvar em arquivo
python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --output gas_prices.json
```

## Installation / Instalação

1. **Clone this repository / Clone este repositório:**

```bash
git clone https://github.com/GustavoZiaugra/gas-price-alert-skill.git
cd gas-price-alert-skill
```

2. **Install dependencies / Instale dependências:**

```bash
pip install requests geopy
```

3. **Load skill into OpenClaw / Carregar skill no OpenClaw:**
   - Open OpenClaw Control UI
   - Go to Skills → Import Skill
   - Select this directory

## Usage Examples / Exemplos de Uso

### By ZIP Code / Por CEP (Recommended)

```bash
# Columbus, OH
python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --summary

# Miami, FL
python3 scripts/gas_alternative.py --zip 33101 --radius 15 --fuel 87 --summary

# Los Angeles, CA
python3 scripts/gas_alternative.py --zip 90210 --radius 10 --fuel 91 --summary
```

### Por Coordenadas (Português)

```bash
# Buscar por coordenadas
python3 scripts/gas_alternative.py --lat 39.9612 --lon -82.9988 --radius 20 --fuel 87 --summary
```

### Daily Alerts / Alertas Diários

Set up automated daily alerts using OpenClaw's cron system / Configure alertas diárias automatizadas usando o sistema cron do OpenClaw:

```json
{
  "name": "Gas price alert",
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "America/New_York"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "⛽ Gas Prices / Preços de Combustível\n\nRun: python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --summary"
  },
  "sessionTarget": "main"
}
```

## Parameters / Parâmetros

| Parameter | Description | Descrição | Default | Exemplo |
|-----------|-------------|-------------|----------|---------|
| `--zip` | ZIP code for location / CEP para localização | none | `--zip 43215` |
| `--lat` | Latitude / Latitude | 39.9612 | `--lat 40.7128` |
| `--lon` | Longitude / Longitude | -82.9988 | `--lon -74.0060` |
| `--radius` | Search radius in miles / Raio de busca em milhas | 20 | `--radius 15` |
| `--fuel` | Fuel type / Tipo de combustível (87, 89, 91, diesel) | 87 | `--fuel 91` |
| `--base-price` | Base price for estimation / Preço base para estimativa | 2.89 | `--base-price 3.15` |
| `--output` | Output file / Arquivo de saída | gas_prices.json | `--output results.json` |
| `--summary` | Print human-readable summary / Imprimir resumo legível | false | `--summary` |

## Example Output / Exemplo de Saída

```
⛽ Gas Prices (87 Octane) - Columbus, OH
⛽ Preços de Gasolina (87 Octanos) - Columbus, OH

💰 Best Prices Available (3 with prices)
💰 Melhores Preços Disponíveis (3 com preços)

• Costco Gas - $2.69 (est.)
  📍 5000 Morse Rd, Columbus, OH 43213 (7.9 miles) ⭐

• Costco Gas - $2.69 (est.)
  📍 1350 Hilliard Rome Rd, Columbus, OH 43228 (8.2 miles) ⭐

📍 Nearest Stations (Top 10 by distance)
📍 Postos Mais Próximos (Top 10 por distância)

1. Speedway (1.6 miles)
2. GetGo (2.2 miles)
3. Sunoco (2.3 miles)
4. Shell (2.8 miles)
5. Circle K (2.8 miles)

... and 129 more stations within 20 miles
... e 129 postos a mais dentro de 20 milhas

💡 Tips / Dicas:
• Costco typically has gas $0.15-0.25 below market average
• Costco geralmente tem gasolina $0.15-0.25 abaixo da média do mercado
• For exact prices, check GasBuddy.com or station's app
• Para preços exatos, verifique GasBuddy.com ou o app do posto
• Total stations found: 137
• Total de postos encontrados: 137
```

## How It Works / Como Funciona

1. **Geocoding:** Converts ZIP code to precise coordinates / Converte CEP para coordenadas precisas
2. **OpenStreetMap Search:** Finds all gas stations within radius / Encontra todos os postos de gasolina dentro do raio
3. **Costco Detection:** Identifies Costco stations (typically cheapest) / Identifica postos Costco (tipicamente mais baratos)
4. **Price Estimation:** Estimates Costco prices based on market averages / Estima preços da Costco baseado em médias de mercado
5. **Distance Calculation:** Uses geodesic distance for accurate mileage / Usa distância geodésica para milhas precisas
6. **Smart Filtering:** Removes duplicates and sorts by relevance / Remove duplicatas e ordena por relevância

## Limitations / Limitações

- **Real-time prices:** Uses estimated prices for Costco. For exact prices, check GasBuddy.com or station apps.
- **Preços em tempo real:** Usa preços estimados para Costco. Para preços exatos, verifique GasBuddy.com ou apps dos postos.
- **API availability:** OpenStreetMap/Overpass API may experience timeouts (try again later).
- **Disponibilidade de API:** API do OpenStreetMap/Overpass pode ter timeouts (tente mais tarde).
- **Coverage quality:** Depends on OpenStreetMap data completeness for your area.
- **Qualidade de cobertura:** Depende da completude dos dados do OpenStreetMap para sua área.

## Use Cases / Casos de Uso

### Daily Commuter / Deslocamento Diário
Check gas prices before your morning commute to find the cheapest station on your route.
Verifique preços de gasolina antes de seu deslocamento matinal para encontrar o posto mais barato na sua rota.

### Road Trip / Viagem
Find cheap gas along your route when traveling to a new city.
Encontre gasolina barata ao longo de sua rota quando viajar para uma nova cidade.

### Costco Shopper / Cliente Costco
Costco members can find the best time to fill up while shopping for groceries.
Membros da Costco podem encontrar o melhor momento para abastecer enquanto compram mantimentos.

## Contributing / Contribuindo

To add more Costco locations or improve the skill:
Para adicionar mais locais da Costco ou melhorar a skill:

1. Edit `scripts/gas_alternative.py`
2. Add locations to `search_costco_locations()` / Adicionar locais na função `search_costco_locations()`
3. Submit a pull request / Envie um pull request

## License / Licença

MIT License - Use freely for personal and commercial purposes.
Licença MIT - Use livremente para fins pessoais e comerciais.

## Credits / Créditos

Created by **Gustavo (GustavoZiaugra)** with OpenClaw
Criado por **Gustavo (GustavoZiaugra)** com OpenClaw

- OpenStreetMap for station data / OpenStreetMap para dados de postos
- Geopy for geocoding / Geopy para geocodificação
- Requests for HTTP handling / Requests para manipulação HTTP

---

**Find this and more OpenClaw skills at ClawHub.com**
**Encontre este e mais skills do OpenClaw em ClawHub.com**

⭐ **Star this repository if you find it useful!**
**⭐ Dê uma estrela neste repositório se você achar útil!**

🇧🇷 **Disponível em português e inglês!**
