from datetime import datetime, timedelta
import backtrader as bt
import os
import math

# Create a subclass of Strategy to define the indicators and logic
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,
        pslow=30,
        stop_loss=0.05, # 5% stop loss
    )

    def __init__(self):
        # Indicators:
        sma1 = bt.ind.SMA(period=self.p.pfast)
        sma2 = bt.ind.SMA(period=self.p.pslow)

        # Crossover signal:
        self.crossover = bt.ind.CrossOver(sma1, sma2)

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.stop_order = None # Track stop loss order
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
                # Set stop loss price
                stop_price = self.buyprice * (1.0 - self.p.stop_loss)
                self.log(f'STOP LOSS SET at: {stop_price:.2f}')
                self.stop_order = self.sell(exectype=bt.Order.Stop, price=stop_price)

            elif order.issell():
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                
                # If sell was triggered (either by signal or stop loss), clear any pending stop orders
                if self.stop_order:
                    self.cancel(self.stop_order)
                    self.stop_order = None

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset main order tracking (but keep stop_order tracking if position is open)
        if not self.position:
             self.order = None
        else:
             self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        current_close = self.datas[0].close[0]

        if not self.position:
            if self.crossover > 0:
                self.log(f'BUY CREATE, {current_close:.2f}')
                self.order = self.buy()
        else:
            # If we are in a position, we check for exit signal.
            # Note: Stop loss is handled automatically by the broker via the order submitted in notify_order
            if self.crossover < 0:
                self.log(f'SELL CREATE, {current_close:.2f}')
                # We need to cancel the stop loss order before selling manually to avoid double selling
                if self.stop_order:
                    self.cancel(self.stop_order)
                    self.stop_order = None
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

def generate_sine_wave_data(filename, days=365):
    """Generates synthetic sine wave data for testing crossovers."""
    with open(filename, 'w') as f:
        f.write("date,open,high,low,close,volume,openinterest\n")
        base_price = 100
        start_date = datetime(2023, 1, 1)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # Sine wave pattern: Amplitude 20, Period ~180 days
            # Add a sudden drop to test stop loss?
            change = 20 * math.sin(2 * math.pi * i / 180)
            
            trend = i * 0.1
            
            # Simulate a crash at day 100 to trigger stop loss
            shock = 0
            if 95 < i < 105:
                shock = -15 # Sudden drop
            
            close_price = base_price + change + trend + shock
            
            # Construct OHLC data around the close
            open_price = close_price - 1
            high_price = close_price + 2
            low_price = close_price - 2
            
            dt_str = date.strftime('%Y-%m-%d')
            line = f"{dt_str},{open_price:.2f},{high_price:.2f},{low_price:.2f},{close_price:.2f},1000,0\n"
            f.write(line)

# --- Main execution part ---
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    # Generate synthetic data
    temp_file = 'temp_data.csv'
    generate_sine_wave_data(temp_file, days=400)

    # Parse the data
    data = bt.feeds.GenericCSVData(
        dataname=temp_file,
        fromdate=datetime(2023, 1, 1),
        todate=datetime(2024, 2, 1),
        nullvalue=0.0,
        dtformat='%Y-%m-%d',
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=6
    )
    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    if os.path.exists(temp_file):
        os.remove(temp_file)