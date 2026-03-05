---
name: pine-editor
version: 1.0.0
---

# Pine Editor Skill

TradingView Pine Script v6 - Create indicators, strategies, and automated trading systems.

## Basics

```pine
//@version=6
indicator("Mi Indicador", overlay=true)

// Variables
var float precioEntrada = na
var int conteo = 0

// Inputs
miParametro = input.int(14, "Periodo")
mostrarLinea = input.bool(true, "Mostrar línea")

// Indicators
media = ta.sma(close, miParametro)

// Plot
plot(media, color=color.blue, title="Media Móvil")

// Conditions
alcista = ta.crossover(media, close)
bajista = ta.crossunder(media, close)

// Alerts
alertcondition(alcista, title="Señal Alcista", message="Cruce alcista!")
```

## Tipos de Datos

```pine
int      // Entero: 1, 100, -5
float    // Decimal: 1.5, 3.14
bool     // true/false
string   // Texto: "Hola"
color    // Colores: color.red, #FF0000
```

## Variables con var

```pine
var int contador = 0        // Persiste entre barras
var float maximo = na       // Inicializa solo una vez
var label miLabel = label.new(x, y, text)
```

## Funciones Built-in

```pine
// Moving Averages
ta.sma(close, 20)           // Simple
ta.ema(close, 20)          // Exponential
ta.wma(close, 20)          // Weighted
ta.rma(close, 20)          // Rolling Moving Average

// Oscillators
ta.rsi(close, 14)
ta.macd(close, 12, 26, 9)
ta.stoch(close, high, low, 14)
ta.cci(high, low, close, 20)

// Other
ta.highest(high, 20)
ta.lowest(low, 20)
ta.barssince(condition)
ta.valuewhen(condition, expression, occurrence)
```

## Operadores

```pine
// Comparación
> < >= <= == !=

// Lógico
and or not

// Matemáticos
+ - * / % (módulo)
math.sqrt() math.abs() math.max() math.min()
```

## Condicionales

```pine
if condicion then
    // código
else
    // código

// Múltiples condiciones
if condicion1 then
    // ...
else if condicion2 then
    // ...
else
    // ...
```

## Loops

```pine
for i = 0 to 10
    // ejecutar 11 veces
    
// Con break
for i = 0 to 100
    if condicion then
        break
```

## Plots y Visualización

```pine
// Línea
plot(media, color=color.red, linewidth=2)

// Histograma
plotbar(volumen)

// Relleno entre líneas
plot1 = ta.sma(close, 20)
plot2 = ta.sma(close, 50)
fill(plot1, plot2, color=color.new(color.blue, 80))

// Flechas
plotshape(alcista, style=shape.triangleup, location=location.belowbar, color=color.green)

// Líneas horizontales
line.new(x1, y1, x2, y2, extend=extend.right)

// Cajas
box.new(left, top, right, bottom, bgcolor=color.red)
```

## Strategy (v6)

```pine
strategy("Mi Estrategia", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Entry
if condicionEntrada
    strategy.entry(id="Compra", direction=strategy.long)

if condicionSalida
    strategy.close(id="Compra")

// Stop Loss / Take Profit
strategy.exit("Salida", from_entry="Compra", stop=precioStop, limit=precioTarget)

// Órdenes pendientes
strategy.order(id="Orden", direction=strategy.long, stop=precioStop)

// Cerrar todo
strategy.close_all()
```

## Timeframes

```pine
// Cambiar timeframe
request.security(syminfo.tickerid, "15", close)

// Función de múltiples timeframes
[supertrend, direccion] = ta.supertrend(3, 14)
```

## Funciones Personalizadas

```pine
miFuncion(parametro) =>
    resultado = parametro * 2
    resultado

// Usar
valor = miFuncion(10)
```

## Dibujar Labels

```pine
var label eti = label.new(bar_index, high, text="Alcista", style=label.style_label_down, color=color.red)
label.set_x(eti, bar_index)
label.set_y(eti, high)
label.set_text(eti, "Nuevo texto")
label.delete(eti[1])  // Borrar anterior
```

## Dibujar Lines

```pine
line.new(bar_index - 10, low[10], bar_index, low, color=color.green, width=2)

// Extender línea
line.new(x1, y1, x2, y2, extend=extend.both)

// Mover línea dinámicamente
line.set_y1(miLinea, nuevoY1)
line.set_y2(miLinea, nuevoY2)
```

## Ejemplo: RSI with Signals

```pine
//@version=6
indicator("RSI Signals", overlay=false)

rsi = ta.rsi(close, 14)
overbought = input(70)
oversold = input(30)

plot(rsi, "RSI", color=color.purple)
hline(overbought, "Overbought", color=color.red, linestyle=hline.style_dashed)
hline(oversold, "Oversold", color=color.green, linestyle=hline.style_dashed)

// Señales
senialCompra = ta.crossover(rsi, oversold)
senialVenta = ta.crossunder(rsi, overbought)

plotshape(senialCompra, title="Compra", text="COMPRA", style=shape.labelup, location=location.bottom, color=color.green, textcolor=color.white)
plotshape(senialVenta, title="Venta", text="VENTA", style=shape.labeldown, location=location.top, color=color.red, textcolor=color.white)

// Alerts
alertcondition(senialCompra, "RSI Oversold", "RSI cruzó arriba de 30 - POSSIBLE BUY")
alertcondition(senialVenta, "RSI Overbought", "RSI cruzó debajo de 70 - POSSIBLE SELL")
```

## Ejemplo: Moving Average Crossover Strategy

```pine
//@version=6
strategy("MA Cross", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

rapida = input.int(9, "Rápida")
lenta = input.int(21, "Lenta")

maRapida = ta.sma(close, rapida)
maLenta = ta.sma(close, lenta)

plot(maRapida, color=color.blue, title="MA Rápida")
plot(maLenta, color=color.red, title="MA Lenta")

// Entry
longCondition = ta.crossover(maRapida, maLenta)
shortCondition = ta.crossunder(maRapida, maLenta)

if (longCondition)
    strategy.entry("Compra", strategy.long)

if (shortCondition)
    strategy.entry("Venta", strategy.short)

// Exit
strategy.exit("Salida", "Compra", stop=strategy.position_avg_price * 0.98, limit=strategy.position_avg_price * 1.02)
strategy.exit("Salida", "Venta", stop=strategy.position_avg_price * 1.02, limit=strategy.position_avg_price * 0.98)
```

## Estrategias Creadas

### 1. ILM Strategy
**Archivo:** `estrategias/ilm_strategy.pine`

Estrategia de Inverted Liquidity Model:
- Detecta liquidity sweeps (BSL/SSL)
- Identifica Fair Value Gaps (FVG)
- Señales de entrada cuando hay sweep + FVG
- Requiere configuración manual de swing lookback

### 2. ORB Strategy
**Archivo:** `estrategias/orb_strategy.pine`

Opening Range Breakout:
- Range de 9:30-9:45 NY (15 min)
- Breakout arriba = LONG
- Breakout abajo = SHORT
- Stop Loss: Bajo/alto del rango - 1.5x ATR
- Target: 2:1 Risk:Reward

## Cómo Usar

1. Copia el código del archivo
2. Abre TradingView → Pine Editor
3. Pega el código
4. Ajusta parámetros (inputs)
5. Añade al gráfico

## Recursos
- TradingView Pine Script Docs: https://www.tradingview.com/pine-script-docs/
- Pine Script Reference: https://www.tradingview.com/pine-script-reference/v5/
