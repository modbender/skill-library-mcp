#!/bin/bash
# Script para obtener tasas de cambio BCV y P2P de Binance
# Fuente: BCV (oficial) y Binance P2P (USDT)

echo "🇻🇪 TASAS DE CAMBIO VENEZUELA"
echo "=============================="
echo ""

# Obtener tasa BCV
echo "📊 Consultando tasa BCV..."
BCV_RATE=$(curl -s "https://api.exchangerate-api.com/v4/latest/USD" | jq -r '.rates.VES' 2>/dev/null)

if [ -z "$BCV_RATE" ] || [ "$BCV_RATE" = "null" ]; then
    # Fallback a valor aproximado si la API falla
    BCV_RATE="420"
    echo "⚠️ Usando valor de respaldo"
fi

echo "✅ Tasa BCV: $BCV_RATE Bs/USD"
echo ""

# Obtener datos de Binance P2P
echo "📊 Consultando USDT Binance P2P..."

# Configurar headers para Binance
BINANCE_HEADERS='{"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}'

# Query para compra (buy) - usuarios que venden USDT
BUY_JSON=$(curl -s -X POST "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search" \
  -H "Content-Type: application/json" \
  -d '{
    "fiat": "VES",
    "page": 1,
    "rows": 10,
    "tradeType": "SELL",
    "asset": "USDT",
    "countries": [],
    "proMerchantAds": false,
    "shieldMerchantAds": false,
    "filterType": "tradable"
  }' 2>/dev/null)

# Query para venta (sell) - usuarios que compran USDT  
SELL_JSON=$(curl -s -X POST "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search" \
  -H "Content-Type: application/json" \
  -d '{
    "fiat": "VES",
    "page": 1,
    "rows": 10,
    "tradeType": "BUY",
    "asset": "USDT",
    "countries": [],
    "proMerchantAds": false,
    "shieldMerchantAds": false,
    "filterType": "tradable"
  }' 2>/dev/null)

# Calcular promedios
# Check if we got valid data
BUY_VALID=$(echo "$BUY_JSON" | jq -r '.data | length' 2>/dev/null)
SELL_VALID=$(echo "$SELL_JSON" | jq -r '.data | length' 2>/dev/null)

if [ -n "$BUY_VALID" ] && [ "$BUY_VALID" != "0" ] && [ "$BUY_VALID" != "null" ] && [ "$BUY_VALID" -gt 0 ] 2>/dev/null; then
    BUY_AVG=$(echo "$BUY_JSON" | jq -r '[.data[].adv.price | tonumber] | add / length' 2>/dev/null)
    BUY_MIN=$(echo "$BUY_JSON" | jq -r '[.data[].adv.price | tonumber] | min' 2>/dev/null)
    BUY_MAX=$(echo "$BUY_JSON" | jq -r '[.data[].adv.price | tonumber] | max' 2>/dev/null)
    BUY_COUNT="$BUY_VALID"
else
    # Fallback values based on typical market rate (BCV + 45%)
    BUY_AVG=$(echo "scale=2; $BCV_RATE * 1.45" | bc)
    BUY_MIN=$(echo "scale=2; $BCV_RATE * 1.42" | bc)
    BUY_MAX=$(echo "scale=2; $BCV_RATE * 1.48" | bc)
    BUY_COUNT="0 (estimado)"
fi

if [ -n "$SELL_VALID" ] && [ "$SELL_VALID" != "0" ] && [ "$SELL_VALID" != "null" ] && [ "$SELL_VALID" -gt 0 ] 2>/dev/null; then
    SELL_AVG=$(echo "$SELL_JSON" | jq -r '[.data[].adv.price | tonumber] | add / length' 2>/dev/null)
    SELL_MIN=$(echo "$SELL_JSON" | jq -r '[.data[].adv.price | tonumber] | min' 2>/dev/null)
    SELL_MAX=$(echo "$SELL_JSON" | jq -r '[.data[].adv.price | tonumber] | max' 2>/dev/null)
    SELL_COUNT="$SELL_VALID"
else
    # Fallback values based on typical market rate (BCV + 46%)
    SELL_AVG=$(echo "scale=2; $BCV_RATE * 1.46" | bc)
    SELL_MIN=$(echo "scale=2; $BCV_RATE * 1.43" | bc)
    SELL_MAX=$(echo "scale=2; $BCV_RATE * 1.49" | bc)
    SELL_COUNT="0 (estimado)"
fi

# Calcular promedio general
P2P_AVG=$(echo "scale=2; ($BUY_AVG + $SELL_AVG) / 2" | bc)

echo "✅ USDT P2P (venta): $BUY_AVG Bs/USDT (rango: $BUY_MIN - $BUY_MAX, $BUY_COUNT ofertas)"
echo "✅ USDT P2P (compra): $SELL_AVG Bs/USDT (rango: $SELL_MIN - $SELL_MAX, $SELL_COUNT ofertas)"
echo "✅ USDT P2P (promedio): $P2P_AVG Bs/USDT"
echo ""

# Calcular brecha
echo "📈 BRECHA CAMBIARIA:"
echo "===================="
DIFF=$(echo "scale=2; $P2P_AVG - $BCV_RATE" | bc)
GAP_BCV_REF=$(echo "scale=2; ($P2P_AVG - $BCV_RATE) / $BCV_RATE * 100" | bc)

echo "Diferencia: $DIFF Bs"
echo "Brecha: +$GAP_BCV_REF%"
echo "→ El paralelo está $GAP_BCV_REF% más caro que el oficial"
echo ""

# NUEVA SECCIÓN: Conversión $100 BCV a USDT
echo "💰 CONVERSIÓN: $100 USD (BCV) a USDT"
echo "====================================="
BS_100_USD=$(echo "scale=2; 100 * $BCV_RATE" | bc)
USDT_EQUIV=$(echo "scale=2; $BS_100_USD / $P2P_AVG" | bc)
USDT_PERDIDOS=$(echo "scale=2; 100 - $USDT_EQUIV" | bc)

echo "\$100 a tasa BCV = $BS_100_USD Bs"
echo "Equivalen a: $USDT_EQUIV USDT (a tasa P2P)"
echo ""
echo "📊 En otras palabras:"
echo "   Por \$100 en dólares BCV, obtienes $USDT_EQUIV USDT"
echo "   (Pierdes $USDT_PERDIDOS USDT por la brecha cambiaria)"
echo ""

echo "=============================="
echo "Actualizado: $(date '+%Y-%m-%d %H:%M')"
