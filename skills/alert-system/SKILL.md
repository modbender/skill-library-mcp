---
name: Alert System
description: Smart monitoring with customizable triggers — price alerts (stocks,
  crypto, products), event monitoring, custom condition alerts with Telegram
  notification.
---

# Alert System

Smart monitoring with customizable triggers — price alerts (stocks, crypto, products), event monitoring, custom condition alerts with Telegram notification.

## Usage
```python
from alert_system.alerts import AlertSystem

system = AlertSystem("<username>")
system.add_alert("price", "BTC", "above", 100000)
triggered = system.check_all()
```

## Features
- Price alerts (stocks via yfinance, crypto)
- Website/event change monitoring
- Custom condition triggers
- Cron-integrated checking
- Telegram notifications on trigger
