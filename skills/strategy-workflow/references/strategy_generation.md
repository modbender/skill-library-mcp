# MTF EMA Group Feat Dynamic Slope Logic + Heiken Ashi Candles + Volume  Weighted Bollinger Band TP Targets  Selected by Stochastic Commodity Channel Index Levels & PVSRA Volume

## Base Strategy Description

This strategy catches and holds the appropriate market movement based on clear momentum signals within a multi time frame analysis of multiple data points present by select group of indicators, as well as mathematically derived logic off those indicators to determine intuitive levels used to engage trailing stop & tp levels.

Directional position bias & gating is done by HTF EMA Group which consists of two exponential moving averages.

Upon directional bias approved by HTF EMA Group, Execution TF group EMA's also print in the same direction for one candle

Dynamic TP's are set with volume weighted Bollinger Bands, that adjust their standard deviation dynamically from 1.5 to 4 as a function of PVSRA candle logic and Stochastic CCI

## Stochastic CCI:

### Long

- Crosses above overbought level = BB level 4
- Crosses under overbought level = BB level 2
- Value decreases > [10] from recent high = -1 level

### Short

- Crosses above underbought level = BB Level 2
- Crosses under underbought level = BB Level 4
- Value increases > [10] from recent level = -1 level

## PVSRA Volume:

From the past 3 periods:

- Increase in [3] period volume MA from previous bar = + 1 level
- Decrease in volume for 1 perod = - 1 level
- Decrease in volume for 2 periods = -2 levels

Trades open on level 4 and remain there for 2 periods by default and adjust accordingly thereafter, no TP's for a set period is a variable setting within the strategy.

## Trading View Scripts for Python Conversion

Bollinger Bands:
[https://www.tradingview.com/support/solutions/43000501840/](https://)

```
//@version=6
indicator(shorttitle="BB", title="Bollinger Bands", overlay=true, timeframe="", timeframe_gaps=true)

TT_LENGTH  = "The time period to be used in calculating the MA which creates the base for the Upper and Lower Bands."
TT_MA_TYPE = "Determines the type of Moving Average that is applied to the basis plot line."
TT_SOURCE  = "Determines what data from each bar will be used in calculations."
TT_MULT    = "The number of Standard Deviations away from the MA that the Upper and Lower Bands should be."
TT_OFFSET  = "Changing this number will move the Bollinger Bands either Forwards or Backwards relative to the current market."

length = input.int(20,       "Length", minval = 1, tooltip =  TT_LENGTH)
maType = input.string("SMA", "Basis MA Type",      options = ["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"], tooltip = TT_MA_TYPE)
src =    input(close,        "Source", tooltip = TT_SOURCE)
mult =   input.float(2.0,    "StdDev", minval = 0.001, maxval = 50,  tooltip = TT_MULT)
offset = input.int(0,        "Offset", minval = -500,  maxval = 500, tooltip =  TT_OFFSET, display = display.none)

ma(source, length, _type) =>
    switch _type
        "SMA" => ta.sma(source, length)
        "EMA" => ta.ema(source, length)
        "SMMA (RMA)" => ta.rma(source, length)
        "WMA" => ta.wma(source, length)
        "VWMA" => ta.vwma(source, length)

basis = ma(src, length, maType)
dev = mult * ta.stdev(src, length)
upper = basis + dev
lower = basis - dev

plot(basis, "Basis", color=#2962FF, offset = offset)
p1 = plot(upper, "Upper", color=#F23645, offset = offset)
p2 = plot(lower, "Lower", color=#089981, offset = offset)
fill(p1, p2, title = "Background", color=color.rgb(33, 150, 243, 95))
```

CCI Stochastic:

[https://www.tradingview.com/script/XZyG5SOx-CCI-Stochastic-and-a-quick-lesson-on-Scalping-Trading-Systems/](https://)

```
//@version=4
study("CCI Stochastic", shorttitle="CCI_S", overlay=false)

source = input(close)
cci_period = input(28, "CCI Period")
stoch_period = input(28, "Stoch Period")
stoch_smooth_k = input(3, "Stoch Smooth K")
stoch_smooth_d = input(3, "Stoch Smooth D")
d_or_k = input(defval="D", options=["D", "K"])
OB = input(80, "Overbought", type=input.integer)
OS = input(20, "Oversold", type=input.integer)

showArrows = input(true, "Show Arrows")
showArrowsEnter = input(true, "Show Arrows on Enter zone")
showArrowsCenter = input(false, "Show Arrows on Center zone")
showArrowsExit = input(true, "Show Arrows on Exit zone")

cci = cci(source, cci_period)
stoch_cci_k = sma(stoch(cci, cci, cci, stoch_period), stoch_smooth_k)
stoch_cci_d = sma(stoch_cci_k, stoch_smooth_d)

ma = (d_or_k == "D") ? stoch_cci_d : stoch_cci_k

trend_enter = if showArrowsEnter
    if crossunder(ma, OS)
        1
    else
        if crossover(ma, OB)
            -1
  
//plot(trend_enter, title="trend_enter", transp=100)

trend_exit = if showArrowsExit
    if crossunder(ma, OB)
        -1
    else
        if crossover(ma, OS)
            1

trend_center = if showArrowsCenter
    if crossunder(ma, 50)
        -1
    else
        if crossover(ma, 50)
            1

// plot the OB and OS level
overbought = hline(OB, title="Upper Line", linestyle=hline.style_solid, linewidth=1, color=color.red)
oversold = hline(OS, title="Lower Line", linestyle=hline.style_solid, linewidth=1, color=color.lime)
band2 = hline(50, title="Mid Line", linestyle=hline.style_solid, linewidth=1, color=color.gray)

// Plot the moving average
ma_color = ma > OB ? color.red : ma < OS ? color.green : color.gray
plot(ma, "Moving Average", linewidth=3, color=ma_color, transp=0)
maxLevelPlot = hline(100, title="Max Level", linestyle=hline.style_dotted, color=color.new(color.white, 100))
minLevelPlot = hline(0, title="Min Level", linestyle=hline.style_dotted, color=color.new(color.white, 100))
//overbought = hline(OB, title="Hline Overbought", linestyle=hline.style_solid, color=color.new(color.white, 100))
//oversold = hline(OS, title="Hline Oversold", linestyle=hline.style_solid, color=color.new(color.white, 100))

color_fill_os = ma > OB ? color.new(color.red,90) : color.new(color.white, 100)
color_fill_ob = ma < OS ? color.new(color.green,90) : color.new(color.white, 100)
fill(maxLevelPlot, overbought, color=color_fill_os)
fill(minLevelPlot, oversold, color=color_fill_ob)

// Show the arrows
// Trend Enter
plotshape((showArrows and showArrowsEnter and trend_enter == 1) ? 0 : na, color=color.green, transp=20, style=shape.arrowup, size=size.normal,  location=location.absolute, title="Trend Enter Buy")
plotshape((showArrows and showArrowsEnter and trend_enter == -1) ? 100 : na, color=color.red, transp=20, style=shape.arrowdown, size=size.normal, location=location.absolute, title="Trend Enter Sell")

// Trend Center
plotshape((showArrows and showArrowsCenter and trend_center == 1) ? 35 : na, color=color.aqua, transp=20, style=shape.arrowup, size=size.normal, location=location.absolute, title="Trend Center Buy")
plotshape((showArrows and showArrowsCenter and trend_center == -1) ? 65 : na, color=color.fuchsia, transp=20, style=shape.arrowdown, size=size.normal, location=location.absolute, title="Trend Center Sell")

// Trend Exit
plotshape((showArrows and showArrowsExit and trend_exit == 1) ? 0 : na, color=color.orange, transp=20, style=shape.arrowup, size=size.normal, location=location.absolute, title="Trend Exit Buy")
plotshape((showArrows and showArrowsExit and trend_exit == -1) ? 100 : na, color=color.maroon, transp=20, style=shape.arrowdown, size=size.normal, location=location.absolute, title="Trend Exit Sell")

alertcondition((showArrows and showArrowsEnter and trend_enter == 1), message="Trend Enter Buy", title="Trend Enter Buy")
alertcondition((showArrows and showArrowsEnter and trend_enter == -1), message="Trend Enter Sell", title="Trend Enter Sell")
alertcondition((showArrows and showArrowsCenter and trend_center == 1), message="Trend Center Buy", title="Trend Center Buy")
alertcondition((showArrows and showArrowsCenter and trend_center == -1), message="Trend Center Sell", title="Trend Center Sell")
alertcondition((showArrows and showArrowsExit and trend_exit == 1), message="Trend Exit Buy", title="Trend Exit Buy")
alertcondition((showArrows and showArrowsExit and trend_exit == -1), message="Trend Exit Sell", title="Trend Exit Sell")
```

PVSRA Volume:
[https://www.tradingview.com/script/UcbR9FIH-Traders-Reality-PVSRA-Volume-Suite/](https://)

```
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// Original by infernix, library integration by peshocore
// Please note while the code is open source and you are free to use it however you like - the 'Traders Reality' name is not - ie if you produce derivatives of this 
// source code you to name those scripts using "Traders Reality", "Pattern Watchers" or any other name that relates to Traders Reality in any way.

//@version=5
indicator(title = 'Traders Reality PVSRA Volume Suite', shorttitle='TR_PVSRA_VS', format=format.volume)
import TradersReality/Traders_Reality_Lib/1 as trLib


color redVectorColor = input.color(title='Vector: Red', group='PVSRA Colors', defval=color.red, inline='vectors')
color greenVectorColor = input.color(title='Green', group='PVSRA Colors', defval=color.lime, inline='vectors')
color violetVectorColor = input.color(title='Violet', group='PVSRA Colors', defval=color.fuchsia, inline='vectors')
color blueVectorColor = input.color(title='Blue', group='PVSRA Colors', defval=color.blue, inline='vectors', tooltip='Bull bars are green and bear bars are red when the bar is with volume >= 200% of the average volume of the 10 previous bars, or bars where the product of candle spread x candle volume is >= the highest for the 10 previous bars.\n Bull bars are blue and bear are violet when the bar is with with volume >= 150% of the average volume of the 10 previous bars.')
color regularCandleUpColor = input.color(title='Regular: Up Candle', group='PVSRA Colors', defval=#999999, inline='nonVectors')
color regularCandleDownColor = input.color(title='Down Candle', group='PVSRA Colors', defval=#4d4d4d, inline='nonVectors', tooltip='Bull bars are light gray and bear are dark gray when none of the red/green/blue/violet vector conditions are met.')
bool setCandleColors = input.bool(false, title='Set PVSRA candle colors?', group='PVSRA Colors', inline='setCandle')

bool overrideSym = input.bool(group='PVSRA Override', title='Override chart symbol?', defval=false, inline='pvsra')
string pvsraSym = input.string(group='PVSRA Override', title='', defval='INDEX:BTCUSD', tooltip='You can use INDEX:BTCUSD or you can combine multiple feeds, for example BINANCE:BTCUSDT+COINBASE:BTCUSD. Note that adding too many will slow things down.', inline='pvsra')


bool displayMa = input.bool(false, 'Volume MA', inline="vma")
color maColor = input.color(color.blue, "MA Color", inline="vma")
int maPeriod = input.int(20,"MA Period", minval=1, maxval=2000, step=1, inline="vma")


pvsraVolume(overrideSymbolX, pvsraSymbolX, tickerIdX) =>
    request.security(overrideSymbolX ? pvsraSymbolX : tickerIdX, '', volume, barmerge.gaps_off, barmerge.lookahead_off)
pvsraHigh(overrideSymbolX, pvsraSymbolX, tickerIdX) =>
    request.security(overrideSymbolX ? pvsraSymbolX : tickerIdX, '', high, barmerge.gaps_off, barmerge.lookahead_off)
pvsraLow(overrideSymbolX, pvsraSymbolX, tickerIdX) =>
    request.security(overrideSymbolX ? pvsraSymbolX : tickerIdX, '', low, barmerge.gaps_off, barmerge.lookahead_off)
pvsraClose(overrideSymbolX, pvsraSymbolX, tickerIdX) =>
    request.security(overrideSymbolX ? pvsraSymbolX : tickerIdX, '', close, barmerge.gaps_off, barmerge.lookahead_off)
pvsraOpen(overrideSymbolX, pvsraSymbolX, tickerIdX) =>
    request.security(overrideSymbolX ? pvsraSymbolX : tickerIdX, '', open, barmerge.gaps_off, barmerge.lookahead_off)


pvsraVolume = pvsraVolume(overrideSym, pvsraSym, syminfo.tickerid)
pvsraHigh = pvsraHigh(overrideSym, pvsraSym, syminfo.tickerid)
pvsraLow = pvsraLow(overrideSym, pvsraSym, syminfo.tickerid)
pvsraClose = pvsraClose(overrideSym, pvsraSym, syminfo.tickerid)
pvsraOpen = pvsraOpen(overrideSym, pvsraSym, syminfo.tickerid)
[pvsraColor, alertFlag, averageVolume, volumeSpread, highestVolumeSpread] = trLib.calcPvsra(pvsraVolume, pvsraHigh, pvsraLow, pvsraClose, pvsraOpen, redVectorColor, greenVectorColor, violetVectorColor, blueVectorColor, regularCandleDownColor, regularCandleUpColor)

plot(pvsraVolume, style=plot.style_columns, color=pvsraColor,title="PVSRA Volume")
barcolor(setCandleColors ? pvsraColor : na)
alertcondition(alertFlag, title='Vector Candle Alert', message='Vector Candle Alert')

plot(displayMa ? ta.sma(pvsraVolume,maPeriod) : na, title="Volume MA", color=maColor, editable=true)
```

Trader's Reality Pinescript Kit for Session Breaks

[https://www.tradingview.com/script/8zgJTM9u-Traders-Reality-Lib/](https://)

```
//Session                Local Time                       DST OFF (UCT+0)    DST ON (UTC+0)    DST ON 2022      DST OFF 2022    DST ON 2023      DST OFF 2023      DST ON 2024    DST OFF 2024
//London                8am-430pm                       0800-1630        0700-1530        March, 27      October, 30    March, 26      October, 29      March, 31        October, 27
//NewYork                930am-4pm                       1430-2100        1330-2000        March, 13      November, 6    March, 12      November, 5      March, 10        November, 3
//Tokyo                    9am-3pm                           0000-0600        0000-0600        N/A              N/A            N/A              N/A              N/A            N/A
//HongKong                930am-4pm                       0130-0800        0130-0800        N/A              N/A            N/A              N/A              N/A            N/A
//Sydney (NZX+ASX)        NZX start 10am, ASX end 4pm       2200-0600        2100-0500        October, 2      April, 3        October, 1      April, 2          October, 6    April, 7
//EU Brinx                800am-900am                       0800-0900        0700-0800        March, 27      October, 30    March, 26      October, 29      March, 31        October, 27
//US Brinx                900am-10am                       1400-1500        1300-1400        March, 13      November, 6    March, 12      November, 5      March, 10        November, 3
//Frankfurt                800am-530pm                       0700-1630        0600-1530        March, 27      October, 30    March, 26      October, 29      March, 31        October, 27
```

### Trading & Backtesting Framework

Nautilus Trader for Backtests [https://nautilustrader.io/docs/latest](https://)

Optuna + Ray for distribution & parallelization [https://optuna.org/#code_examples](https://)

Ray Tune [https://docs.ray.io/en/latest/index.html#](https://)

Scikit Learn [https://github.com/automl/auto-sklearn](https://)

Auto Pytorch [[https://github.com/automl/Auto-PyTorch](https://)

### Hardware:
Nvidia GH 200
CPU Neoverse ARM 72c

### Prerequisites:
- Full OHLC data from Hyperliquid
- Requires Nautilus Trader ARM edition
- Requires package / dependency manager for
- Ubuntu 22.04
- Python 3.12
- Nautilus Trader (ARM)
- Optuna
- Ray / Ray

### Cloud Compute 
vultr.io
- Compiled Startup Script 

## Indicators

MTF Exponential Moving Average Group with Slope State & Time Period Based Slope Calculations
EMA Cloud

- High Time Frame
  - EMA_HTF_FAST
  - EMA_HTF_SLOW
- Execution Time Frame
  - EMA_EX_FAST
  - EMA_EX_SLOW
    Heiken Ashi Candles
  - HTF_HA
  - EX_HA
    Volume Weighted Bollinger Bands
  - BB_GRP_1 = TP_1
  - BB_GRP_2 = TP_2
  - BB_GRP_3 = TP_3
  - BB_GRP_3 = TP_4
    PVSRA Candles
  - VEC_LVL_1 = > 150% mean of previous 10 candles
  - VEC_LVL_2 = > 300% mean of previous 10 candles
  - VOL_MA = Volume Moving Average

### DEFAULT SETTINGS

EMA_HTF_GROUP
Timeframe = [1h]
EMA_HTF_FAST [17]
EMA_HTF_SLOW [34]
Source [close]

EMA_EX_GROUP
Timeframe = [15m]
EMA_EX_FAST = [4]
EMA_EX_SLOW = [8]
Source [close]

BB_1
Length [6]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [1.5]
Offset [-1]

BB_2
Length [8]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [2]
Offset [-1]

BB_3
Length [8]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [2.5]
Offset [-1]

BB_4
Length [8]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [3]
Offset [-1]

CCI_Stochastic Config 1
Source [close]
CCI Period [6]
Stoch Period [28]
Stoch Smooth K [3]
Stoch Smooth D [2]
D or K [K]
Overbought [80]
Oversold [20]
Optional:
[Y/N] Close Long if CCI < [70]
[Y/N] Close Short if CCI > [30]

Indicator Logic Reporting
MTF EMA:
Condition Based Slope, Previous Candle = [positive/negative]

PVSRA Volume Bars:
Volume Period MA length [3]
Vector Candle Level 1 [150] % > [mean] (mean/stdev) previous 10 periods
Vector Candle Level 2 [200] % > [mean] (mean/stdev) previous 10 periods

Heiken Ashi
Close Color Condition [green/red]
Calculate Indicators on Heiken Ashi [Y]

TRADING LOGIC SETTINGS
Trade Execution on data type [OHLC]
High TF [1h]
Execution TF [15m]
Exchange Venue [hyperliquid]
Fee Level [base]

## Backtesting / Optimizaiton

Assets [BTC, ETH, SOL, XRP, ADA, AVAX, HBAR, WIF, PEPE]

Time Frames
HTF [30m, 1h, 2h, 4h]
EX_TF [5m, 15m, 30m, 1h]

EMA_HTF_GROUP
Timeframe = [30m, 1h, 2h, 4h]
EMA_HTF_FAST [11-33] int
EMA_HTF_SLOW [21-55] int
Source [close]

EMA_EX_GROUP
Timeframe = [5m, 15m, 30m, 1h]
EMA_EX_FAST = [2-11] int
EMA_EX_SLOW = [4-21] int
Source [close]

BB_1
Length [6-9]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [1-2.5] (0.1 Intervals)
Offset [-1,0,1] (test all with 0 offset together)

BB_2
Length [6-9]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [1.5-2.5] (0.1 Intervals)
Offset [-1,0,1]

BB_3
Length [6-9]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [2-3] (0.1 Intervals)
Offset [-1,0,1]

BB_4
Length [6-9]
Basis MA Type [VWMA]
Source [OHLC/4]
StdDev [2.5-3.5] (0.1 Intervals)
Offset [-1,0,1]

CCI_Stochastic
Source [close]
CCI Period [3-12] intervals of 1
Stoch Period [10-30] intervals of 2
Stoch Smooth K [1-9]
Stoch Smooth D [1-9]
D or K [K, D]
Overbought [70-90] (intervals of 5)
Oversold [10-35] (intervals of 5)
Optional:
[Y/N] Close Long if CCI < [60-90] every 5 + on / off (intervals of 5)
[Y/N] Close Short if CCI > [10-40] every 5 + on / off (intervals of 5)
[Y/N] Close Long if CCI decreases from peak by [5-15] intervals of 5
[Y/N] Close Short if CCI increases from valley by [5-15] intervals of 5

### Indicator Logic Reporting

MTF EMA:
Condition Based Slope, Previous Candle = [positive/negative]

PVSRA Volume Bars:
Volume Period MA length [3]
Vector Candle Level 1 [150] % > [mean] (mean/stdev) previous 10 periods
Vector Candle Level 2 [300] % > [mean] (mean/stdev) previous 10 periods
MA Increasing / Decreasing from previous candle
Data feed granularity = [live] live update PVSRA / BB logic = [yes] (if Vector Candle appears mid candle, logic updates to jump levels)

CCI Stochastic:
When crossing above / below overbought / oversold
CCI Peak Value
CCI Value decreased from peak this period = [YES/NO]
CCI Value increased from valley this period = [YES/NO]
Data feed granularity = signal based
Data feed granularity = [Execution Time Frame] live update PVSRA / BB logic = [yes] (logic updates within execution time frame signals)

Heiken Ashi
Close Color Condition [green/red]
Calculate Indicators on Heiken Ashi [Y]

Directional Execution Logic
Long positions are ok to open when HTF_EMA_GROUP condition is:
2 positive slopes

Open Long position if:
HTF_EMA_GROUP  = both slopes positive AND
EX_EMA_GROUP = both slopes positive

Close Directional Position When:
2/2 ema_ex slopes = opposite position1/2 ema_ex slopes = opposite position for [x] bars [default = 2]
BB Take Profit level hit
Close position signal from CCI Stochastic

## Strategy Construction

Use the /strategy-translator and /nautilus-trader / nautilus-trader-hlfix skill to generate the python code in the correct nautilus trader syntax (strategy.py, strategy_config.py) and prepare to backtest with nautilus trader paralellized. reference optuna docs, ray tune, cupy etc...
Run several checks with resource lookup, error checking & handling to verify with user that all proposed strategy logic is put into the backtest and is able to be optimized, and that there is not a single thing left out of the optimization pipeline

## Backtesting Prep

Test XRP on default configs 30m / 1hr first
Utilize Feature Engineering Toolkit / ML pipeline
Prepare a server startup script & backtesting data to import the necessary libs, envs for
Desktop/hyperfrequency (envs + deps) & complete backtesting data parquets from this local machine
Setup remote desktop on that server so we can run CLI direct to the server
Reference vultr docs for ssh & API access
python 3.12-3.13
Nautilus Trader (ARM edition + deps + hyperliquid mod)

- Scikit Learn
- ML Flow
- Raytune
- Optuna
- VectorBT.pro (github account acces)
- XG Boost
- CuPy
- PyTorch auto pytorch
- + any extra I forgot here for feature engineering and ML workflows

## Backtesting Plan

Create a plan for IS / OOS Baysean Optimization with Walk-Forward Analysis. Start with coarse param search on one asset - XRP first 1h / 30m
Try using vectorbt pro parallelized across gpu cores - reference the vectorbt.pro docs & MCP. This will require some planning.
Define Optimization Paths:
Default 70% IS 30% OOS unanchored BO / WFA HPO & Monte Carlo Sim
Adding 75% / 25% IS / OOS unanchored BO / WFA HPO on session & day of week permutations
Plan any further possible HTF / regime classification permutations with me
Perform Optimzation with either vectorized gpu params or nautilus trader high level api distributed via ray across ~90% CPU cores
Use relevant skills available to the LLM:
/backtest-optimize
/nautilus-trader
/

## Optimization Chunking

- In order to reduce massive numbers of configs, start with some settings static and changing a few at a time
- Create a hierarchial importance of features to move and keep static
  Do this in 4-5 stages where appropriate

## Goal Based Workflow

> Categorize by hyperfrequency optimization goals:

- Strategy Returns
- Sharpe
- Win Rate
- Calmar
- Low max dd
- Low MAE
- Month to month consistency - returns
- Month to month consistency - win rate
- Month to month consistency - low MAE
- Month to month consistency - high sharpe
- Returns + low MAE
- Returns + Win Rate + low MAE
- Win Rate + Low max dd
- Configure Optuna to run HPO on those goals + goal combos
- Use the first run for optuna default configs only
- Note relationships between indicator settings and regime
- Begin permutated HPO for Trading Session
  Day of week - Monday, Friday, Weekend, Other
- Generate a multitude of variable strategy configs by those permutations and for the aforementioned strategy optimization goals
- Return 100 top configs in the form of complete code filled MAE optimized strategy tearsheets
  Begin MAE percentile / position sizing / liq buffer sizing optimization & pruning - granular by 1% increments from 99% to 85% - prunes win rate in exchange for leverage
- Return results as complete hyperfrequency tear sheets complete with strat code & strat config code strategies with top static and variable configs with defined param switching in the strat config / strat
- Backup results to mac local machine & cloud

## Insert Strategy & Config code here

Strategy.py

```

```

strategy_config.py

```

Insert Strategy code here
```
