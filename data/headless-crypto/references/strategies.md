# Trading Strategies Reference

Detailed implementation guides for automated trading strategies.

## Table of Contents

1. [Limit Orders](#limit-orders)
2. [Dollar Cost Averaging (DCA)](#dollar-cost-averaging-dca)
3. [Stop-Loss / Take-Profit](#stop-loss--take-profit)
4. [Arbitrage](#arbitrage)
5. [Grid Trading](#grid-trading)
6. [Momentum Trading](#momentum-trading)

---

## Limit Orders

Execute trades when price reaches target levels.

### Buy Limit

```python
from scripts.get_price import get_token_price
from scripts.swap import execute_swap
import time

def buy_limit(
    chain: str,
    token: str,
    target_price: float,
    amount: float,
    quote_token: str = "native",
    check_interval: int = 60
):
    """
    Buy when price drops to or below target.
    """
    print(f"🎯 Buy limit order: {token} at {target_price} {quote_token}")
    
    while True:
        current_price = get_token_price(chain, token, quote_token)
        print(f"Current: {current_price} | Target: {target_price}")
        
        if current_price <= target_price:
            print(f"✅ Target reached! Executing buy...")
            result = execute_swap(
                chain=chain,
                input_token=quote_token,
                output_token=token,
                amount=amount,
                slippage=1.0
            )
            
            if result and result["success"]:
                print(f"🎉 Buy executed: {result['output_amount']} {token}")
                return result
            else:
                print("❌ Buy failed, retrying...")
        
        time.sleep(check_interval)
```

### Sell Limit

```python
def sell_limit(
    chain: str,
    token: str,
    target_price: float,
    amount: float,
    quote_token: str = "native",
    check_interval: int = 60
):
    """
    Sell when price rises to or above target.
    """
    print(f"🎯 Sell limit order: {token} at {target_price} {quote_token}")
    
    while True:
        current_price = get_token_price(chain, token, quote_token)
        print(f"Current: {current_price} | Target: {target_price}")
        
        if current_price >= target_price:
            print(f"✅ Target reached! Executing sell...")
            result = execute_swap(
                chain=chain,
                input_token=token,
                output_token=quote_token,
                amount=amount,
                slippage=1.0
            )
            
            if result and result["success"]:
                print(f"🎉 Sold: {result['output_amount']} {quote_token}")
                return result
            else:
                print("❌ Sell failed, retrying...")
        
        time.sleep(check_interval)
```

---

## Dollar Cost Averaging (DCA)

Buy fixed amounts at regular intervals.

### Simple DCA

```python
import schedule
import time

def dca_strategy(
    chain: str,
    token: str,
    amount_per_buy: float,
    quote_token: str = "SOL",
    frequency: str = "daily",
    time_of_day: str = "09:00"
):
    """
    Buy fixed amount on schedule.
    
    Args:
        frequency: "daily", "weekly", or "hourly"
        time_of_day: Time to execute (for daily/weekly)
    """
    def execute_dca():
        print(f"💰 DCA Buy: {amount_per_buy} {quote_token} → {token}")
        result = execute_swap(
            chain=chain,
            input_token=quote_token,
            output_token=token,
            amount=amount_per_buy,
            slippage=1.0
        )
        
        if result and result["success"]:
            print(f"✅ Bought {result['output_amount']} {token}")
        else:
            print("❌ DCA failed")
    
    # Schedule based on frequency
    if frequency == "daily":
        schedule.every().day.at(time_of_day).do(execute_dca)
    elif frequency == "weekly":
        schedule.every().monday.at(time_of_day).do(execute_dca)
    elif frequency == "hourly":
        schedule.every().hour.do(execute_dca)
    
    print(f"📅 DCA scheduled: {frequency} at {time_of_day}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
```

### Smart DCA (Price-Based)

```python
def smart_dca(
    chain: str,
    token: str,
    base_amount: float,
    moving_average_days: int = 7,
    check_interval: int = 3600  # 1 hour
):
    """
    Buy more when price is below moving average.
    """
    price_history = []
    
    while True:
        current_price = get_token_price(chain, token)
        price_history.append(current_price)
        
        # Keep only last N days
        max_samples = moving_average_days * 24  # Hourly samples
        if len(price_history) > max_samples:
            price_history = price_history[-max_samples:]
        
        # Calculate moving average
        if len(price_history) >= 24:  # At least 1 day of data
            ma = sum(price_history) / len(price_history)
            
            # Buy more if price is below MA
            if current_price < ma:
                discount = ((ma - current_price) / ma) * 100
                buy_amount = base_amount * (1 + discount / 100)
                
                print(f"📉 Price {discount:.1f}% below MA, buying {buy_amount}")
                execute_swap(chain, "SOL", token, buy_amount, 1.0)
            else:
                print(f"📈 Price above MA, buying base amount {base_amount}")
                execute_swap(chain, "SOL", token, base_amount, 1.0)
        
        time.sleep(check_interval)
```

---

## Stop-Loss / Take-Profit

Automatically exit positions at target levels.

### Stop-Loss

```python
def stop_loss(
    chain: str,
    token: str,
    entry_price: float,
    stop_loss_percent: float,
    amount: float,
    check_interval: int = 60
):
    """
    Sell when price drops below threshold.
    """
    stop_price = entry_price * (1 - stop_loss_percent / 100)
    print(f"🛡️ Stop-loss at {stop_price} ({stop_loss_percent}% below entry)")
    
    while True:
        current_price = get_token_price(chain, token)
        loss_percent = ((entry_price - current_price) / entry_price) * 100
        
        print(f"Price: {current_price} | Loss: {loss_percent:.2f}%")
        
        if current_price <= stop_price:
            print(f"🚨 Stop-loss triggered! Selling...")
            result = execute_swap(chain, token, "USDC", amount, 2.0)
            
            if result and result["success"]:
                print(f"🛑 Position closed: {result['output_amount']} USDC")
                return result
        
        time.sleep(check_interval)
```

### Take-Profit

```python
def take_profit(
    chain: str,
    token: str,
    entry_price: float,
    take_profit_percent: float,
    amount: float,
    check_interval: int = 60
):
    """
    Sell when price rises to profit target.
    """
    target_price = entry_price * (1 + take_profit_percent / 100)
    print(f"🎯 Take-profit at {target_price} ({take_profit_percent}% profit)")
    
    while True:
        current_price = get_token_price(chain, token)
        profit_percent = ((current_price - entry_price) / entry_price) * 100
        
        print(f"Price: {current_price} | Profit: {profit_percent:.2f}%")
        
        if current_price >= target_price:
            print(f"🎉 Take-profit triggered! Selling...")
            result = execute_swap(chain, token, "USDC", amount, 1.0)
            
            if result and result["success"]:
                print(f"💰 Profit taken: {result['output_amount']} USDC")
                return result
        
        time.sleep(check_interval)
```

### Combined Stop-Loss + Take-Profit

```python
def bracket_order(
    chain: str,
    token: str,
    entry_price: float,
    stop_loss_percent: float,
    take_profit_percent: float,
    amount: float
):
    """
    Exit position at either stop-loss or take-profit.
    """
    import threading
    
    result = {"executed": False}
    
    def monitor_stop_loss():
        stop_price = entry_price * (1 - stop_loss_percent / 100)
        while not result["executed"]:
            price = get_token_price(chain, token)
            if price <= stop_price:
                result["executed"] = True
                execute_swap(chain, token, "USDC", amount, 2.0)
                print(f"🛑 Stop-loss triggered at {price}")
                break
            time.sleep(30)
    
    def monitor_take_profit():
        target_price = entry_price * (1 + take_profit_percent / 100)
        while not result["executed"]:
            price = get_token_price(chain, token)
            if price >= target_price:
                result["executed"] = True
                execute_swap(chain, token, "USDC", amount, 1.0)
                print(f"🎉 Take-profit triggered at {price}")
                break
            time.sleep(30)
    
    # Run both monitors concurrently
    threading.Thread(target=monitor_stop_loss).start()
    threading.Thread(target=monitor_take_profit).start()
```

---

## Arbitrage

Profit from price differences across DEXs or chains.

### Cross-DEX Arbitrage (Same Chain)

```python
def arbitrage_opportunity(
    chain: str,
    token: str,
    dex_a_price: float,
    dex_b_price: float,
    min_profit_percent: float = 1.0
):
    """
    Check if arbitrage is profitable.
    """
    price_diff = abs(dex_a_price - dex_b_price)
    profit_percent = (price_diff / min(dex_a_price, dex_b_price)) * 100
    
    # Account for fees (0.25% per swap × 2 = 0.5%)
    net_profit = profit_percent - 0.5
    
    return net_profit >= min_profit_percent
```

---

## Grid Trading

Place buy/sell orders at fixed price intervals.

### Simple Grid

```python
def grid_trading(
    chain: str,
    token: str,
    base_price: float,
    grid_levels: int = 5,
    grid_spacing: float = 2.0,  # % between levels
    order_size: float = 10.0
):
    """
    Grid trading: buy low, sell high at intervals.
    """
    # Create grid
    buy_levels = []
    sell_levels = []
    
    for i in range(1, grid_levels + 1):
        buy_price = base_price * (1 - (grid_spacing * i / 100))
        sell_price = base_price * (1 + (grid_spacing * i / 100))
        buy_levels.append(buy_price)
        sell_levels.append(sell_price)
    
    print(f"📊 Grid Trading Setup:")
    print(f"Buy levels: {buy_levels}")
    print(f"Sell levels: {sell_levels}")
    
    filled_orders = set()
    
    while True:
        current_price = get_token_price(chain, token)
        
        # Check buy levels
        for level in buy_levels:
            if current_price <= level and level not in filled_orders:
                print(f"💚 Buy at {level}")
                execute_swap(chain, "USDC", token, order_size, 1.0)
                filled_orders.add(level)
        
        # Check sell levels
        for level in sell_levels:
            if current_price >= level and level not in filled_orders:
                print(f"💰 Sell at {level}")
                execute_swap(chain, token, "USDC", order_size, 1.0)
                filled_orders.add(level)
        
        time.sleep(60)
```

---

## Momentum Trading

Follow price trends.

### Simple Momentum

```python
def momentum_strategy(
    chain: str,
    token: str,
    lookback_hours: int = 24,
    momentum_threshold: float = 5.0,  # % gain to trigger
    amount: float = 10.0
):
    """
    Buy when momentum is positive above threshold.
    """
    price_history = []
    
    while True:
        current_price = get_token_price(chain, token)
        price_history.append(current_price)
        
        # Keep only lookback period
        max_samples = lookback_hours
        if len(price_history) > max_samples:
            price_history = price_history[-max_samples:]
        
        if len(price_history) >= 2:
            start_price = price_history[0]
            momentum = ((current_price - start_price) / start_price) * 100
            
            print(f"📈 Momentum: {momentum:.2f}%")
            
            if momentum >= momentum_threshold:
                print(f"🚀 Strong momentum! Buying...")
                execute_swap(chain, "USDC", token, amount, 1.0)
                
                # Reset after buy
                price_history = []
        
        time.sleep(3600)  # Check every hour
```

---

## Best Practices

### Risk Management

1. **Position Sizing:** Never risk more than 1-2% per trade
2. **Diversification:** Don't put all capital in one token
3. **Stop-Losses:** Always use protective stops
4. **Slippage:** Account for fees and slippage in profit calculations

### Monitoring

```python
def log_trade(trade_result: dict):
    """Log all trades to file."""
    import json
    from datetime import datetime
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "trade": trade_result
    }
    
    with open("trades.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### Backtesting

Test strategies on historical data before live trading:

```python
def backtest_strategy(
    historical_prices: list,
    strategy_func,
    initial_capital: float = 100.0
):
    """
    Simulate strategy on historical data.
    """
    capital = initial_capital
    
    for i, price in enumerate(historical_prices):
        # Simulate strategy logic
        # Track P&L
        pass
    
    return capital - initial_capital  # Total profit/loss
```
