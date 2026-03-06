"""
ClawBack - Trade Execution Engine
Scales congressional trades to user's account size and manages execution
Includes trailing stop-loss and risk management features
"""
import json
import logging
import os
import time
from datetime import datetime, time as dt_time, timedelta
from decimal import ROUND_DOWN, Decimal
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class Position:
    """Represents an open position with stop-loss tracking"""

    def __init__(self, symbol: str, quantity: int, entry_price: float,
                 entry_date: datetime, congressional_trade_id: int = None):
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.congressional_trade_id = congressional_trade_id

        # Stop-loss tracking
        self.highest_price = entry_price  # For trailing stop
        self.stop_loss_price = None
        self.trailing_stop_active = False
        self.trailing_stop_percent = 0.05  # 5% trailing stop

    def update_price(self, current_price: float):
        """Update position with current price, adjust trailing stop"""
        if current_price > self.highest_price:
            self.highest_price = current_price

            # If trailing stop is active, update stop price
            if self.trailing_stop_active:
                self.stop_loss_price = self.highest_price * (1 - self.trailing_stop_percent)

    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop-loss has been triggered"""
        if self.stop_loss_price and current_price <= self.stop_loss_price:
            return True
        return False

    def get_unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L"""
        return (current_price - self.entry_price) * self.quantity

    def get_unrealized_pnl_percent(self, current_price: float) -> float:
        """Calculate unrealized P&L as percentage"""
        return (current_price - self.entry_price) / self.entry_price

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'entry_date': self.entry_date.isoformat(),
            'highest_price': self.highest_price,
            'stop_loss_price': self.stop_loss_price,
            'trailing_stop_active': self.trailing_stop_active,
            'congressional_trade_id': self.congressional_trade_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create Position from dictionary"""
        pos = cls(
            symbol=data['symbol'],
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            entry_date=datetime.fromisoformat(data['entry_date']),
            congressional_trade_id=data.get('congressional_trade_id')
        )
        pos.highest_price = data.get('highest_price', pos.entry_price)
        pos.stop_loss_price = data.get('stop_loss_price')
        pos.trailing_stop_active = data.get('trailing_stop_active', False)
        return pos


class TradeEngine:
    """Calculates and executes scaled trades with risk management"""

    def __init__(self, broker_client, config):
        self.broker = broker_client
        self.config = config

        # Trading parameters
        trading_config = config.get('trading', {})
        self.trade_scale = Decimal(str(trading_config.get('tradeScalePercentage', 0.02)))  # Reduced from 5% to 2%
        self.max_position_pct = Decimal(str(trading_config.get('maxPositionPercentage', 0.02)))  # Reduced from 5% to 2%
        self.max_positions = trading_config.get('maxPositions', 20)
        self.daily_loss_limit = Decimal(str(trading_config.get('dailyLossLimit', 0.05)))  # Increased from 3% to 5%

        # Risk management parameters
        risk_config = config.get('riskManagement', {})
        self.position_stop_loss = Decimal(str(risk_config.get('positionStopLoss', 0.08)))
        self.trailing_stop_activation = Decimal(str(risk_config.get('trailingStopActivation', 0.10)))
        self.trailing_stop_percent = Decimal(str(risk_config.get('trailingStopPercent', 0.05)))
        self.max_drawdown = Decimal(str(risk_config.get('maxDrawdown', 0.15)))
        self.consecutive_loss_limit = risk_config.get('consecutiveLossLimit', 3)
        
        # Research-based risk management improvements
        self.sector_exposure_limits = risk_config.get('sectorExposureLimits', {
            'technology': 0.25,
            'healthcare': 0.25,
            'financials': 0.25,
            'consumer': 0.25,
            'industrial': 0.25,
            'energy': 0.25,
            'utilities': 0.25,
            'realEstate': 0.25,
            'materials': 0.25,
            'communication': 0.25
        })
        self.correlation_limit = Decimal(str(risk_config.get('correlationLimit', 0.70)))
        self.liquidity_requirement = risk_config.get('liquidityRequirement', 1000000)  # Minimum daily volume
        self.volatility_filter = risk_config.get('volatilityFilter', True)
        self.kelly_fraction = Decimal(str(risk_config.get('kellyFraction', 0.50)))  # Use 50% of full Kelly

        # Strategy parameters
        strategy_config = config.get('strategy', {})
        self.entry_delay_days = strategy_config.get('entryDelayDays', 3)
        self.holding_period_days = strategy_config.get('holdingPeriodDays', 30)
        
        # Research-based improvements
        self.leadership_weight = Decimal(str(strategy_config.get('leadershipWeight', 2.0)))  # 2x weight for leadership trades
        self.minimum_market_cap = strategy_config.get('minimumMarketCap', 1000000000)  # $1B minimum
        self.sector_tracking = strategy_config.get('sectorTracking', True)
        self.performance_benchmark = strategy_config.get('performanceBenchmark', 'SPX')

        # Market hours (NYSE operates in America/New_York timezone)
        self.market_hours_only = config['trading'].get('marketHoursOnly', True)
        self.market_timezone = ZoneInfo(config['trading'].get('marketTimezone', 'America/New_York'))
        self.market_open = self._parse_time(config['trading'].get('marketOpen', '09:30'))
        self.market_close = self._parse_time(config['trading'].get('marketClose', '16:00'))

        # State tracking
        self.daily_pnl = Decimal('0')
        self.positions: dict[str, Position] = {}  # symbol -> Position
        self.trade_history = []
        self.consecutive_losses = 0
        self.peak_portfolio_value = None

        # Load saved positions
        self._load_positions()

        logger.info("Initialized trade engine with risk management")

    def _parse_time(self, time_str):
        """Parse time string like '09:30' to time object"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return dt_time(hour, minute)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid time format: {time_str}, using default 09:30")
            return dt_time(9, 30)

    def is_market_open(self):
        """Check if current time is within NYSE market hours"""
        if not self.market_hours_only:
            return True

        # Get current time in market timezone (NYSE = America/New_York)
        now_market = datetime.now(self.market_timezone)
        current_time = now_market.time()

        # Check if weekday (Mon-Fri)
        if now_market.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False

        # Check time
        return self.market_open <= current_time <= self.market_close

    def get_next_market_open(self):
        """Get the next market open time as a datetime in local timezone"""
        now_market = datetime.now(self.market_timezone)
        local_tz = datetime.now().astimezone().tzinfo

        # Start with today's market open
        next_open = now_market.replace(
            hour=self.market_open.hour,
            minute=self.market_open.minute,
            second=0,
            microsecond=0
        )

        # If market already opened today, move to tomorrow
        if now_market.time() >= self.market_open:
            next_open += timedelta(days=1)

        # Skip weekends
        while next_open.weekday() >= 5:
            next_open += timedelta(days=1)

        # Convert to local timezone for scheduling
        return next_open.astimezone(local_tz)

    def seconds_until_market_open(self):
        """Get seconds until next market open"""
        next_open = self.get_next_market_open()
        now = datetime.now(next_open.tzinfo)
        delta = next_open - now
        return max(0, delta.total_seconds())

    def calculate_scaled_trade(self, congress_trade, account_balance):
        """
        Calculate scaled trade based on congressional trade amount with research-based improvements
        Returns: symbol, quantity, action, estimated_cost
        """
        try:
            symbol = congress_trade['ticker'].upper()
            action = 'BUY' if congress_trade['transaction_type'] == 'purchase' else 'SELL'
            congress_amount = Decimal(str(congress_trade['amount']))
            
            # Apply leadership weighting if applicable
            politician_weight = Decimal(str(congress_trade.get('politician_weight', 1.0)))
            if congress_trade.get('is_leadership', False):
                politician_weight = self.leadership_weight
                logger.info(f"Applying leadership weight {self.leadership_weight}x for {symbol}")

            # Get current quote for price
            quote = self.broker.get_quote(symbol)
            if not quote:
                logger.warning(f"No quote available for {symbol}")
                return None

            current_price = Decimal(str(quote['last_price']))
            
            # Apply research-based filters
            if not self._passes_research_filters(symbol, quote, congress_trade):
                logger.info(f"Trade {symbol} failed research filters")
                return None

            # Calculate target investment amount with Kelly Criterion optimization
            # Scale congressional trade by configured percentage, adjusted by politician weight
            base_target_amount = account_balance * self.trade_scale
            weighted_target_amount = base_target_amount * politician_weight
            
            # Apply Kelly fraction (professional practice uses 25-75% of full Kelly)
            kelly_adjusted_amount = weighted_target_amount * self.kelly_fraction

            # Calculate quantity (round down to whole shares)
            quantity = (kelly_adjusted_amount / current_price).quantize(Decimal('1.'), rounding=ROUND_DOWN)

            # Ensure minimum of 1 share
            if quantity < 1:
                logger.info(f"Target amount too small for {symbol}: ${kelly_adjusted_amount:.2f} at ${current_price:.2f}")
                return None

            estimated_cost = quantity * current_price

            logger.info(f"Calculated trade: {action} {quantity} shares of {symbol} at ~${current_price:.2f} (${estimated_cost:.2f})")
            logger.info(f"  Base target: ${base_target_amount:.2f}, Weighted: ${weighted_target_amount:.2f}, Kelly-adjusted: ${kelly_adjusted_amount:.2f}")

            return {
                'symbol': symbol,
                'quantity': int(quantity),
                'action': action,
                'estimated_price': float(current_price),
                'estimated_cost': float(estimated_cost),
                'congress_amount': float(congress_amount),
                'scale_factor': float(self.trade_scale),
                'politician_weight': float(politician_weight),
                'kelly_fraction': float(self.kelly_fraction),
                'is_leadership': congress_trade.get('is_leadership', False)
            }

        except Exception as e:
            logger.error(f"Error calculating scaled trade: {e}")
            return None

    def _passes_research_filters(self, symbol, quote, congress_trade):
        """Apply research-based filters to trades"""
        try:
            # Market cap filter (minimum $1B)
            market_cap = quote.get('market_cap', 0)
            if market_cap < self.minimum_market_cap:
                logger.info(f"Filtered {symbol}: Market cap ${market_cap:,.0f} < ${self.minimum_market_cap:,.0f}")
                return False
            
            # Liquidity filter (minimum daily volume)
            volume = quote.get('volume', 0)
            avg_volume = quote.get('avg_volume', volume)
            if avg_volume < self.liquidity_requirement:
                logger.info(f"Filtered {symbol}: Avg volume {avg_volume:,.0f} < {self.liquidity_requirement:,.0f}")
                return False
            
            # Volatility filter (if enabled)
            if self.volatility_filter:
                volatility = quote.get('volatility', 0)
                if volatility > 0.5:  # 50% annualized volatility threshold
                    logger.info(f"Filtered {symbol}: Volatility {volatility:.1%} > 50%")
                    return False
            
            # Sector exposure check (if sector tracking enabled)
            if self.sector_tracking:
                sector = quote.get('sector', 'unknown')
                if not self._check_sector_exposure(symbol, sector, quote.get('market_value', 0)):
                    return False
            
            logger.info(f"Trade {symbol} passed all research filters")
            return True
            
        except Exception as e:
            logger.error(f"Error applying research filters for {symbol}: {e}")
            return True  # Allow trade if filter check fails
    
    def _check_sector_exposure(self, symbol, sector, position_value):
        """Check sector exposure limits"""
        try:
            sector_limit_pct = self.sector_exposure_limits.get(sector.lower(), 0.25)
            
            # Get total portfolio value
            balance = self.broker.get_account_balance()
            if not balance:
                return True  # Skip if can't get balance
            
            total_value = Decimal(str(balance['total_value']))
            
            # Calculate current sector exposure
            # This is simplified - in production, you'd track all positions by sector
            current_sector_exposure = Decimal('0')
            positions = self.broker.get_positions()
            for pos in positions:
                if pos.get('sector', '').lower() == sector.lower():
                    current_sector_exposure += Decimal(str(pos.get('market_value', 0)))
            
            # Add new position value
            new_sector_exposure = current_sector_exposure + Decimal(str(position_value))
            sector_exposure_pct = new_sector_exposure / total_value
            
            if sector_exposure_pct > Decimal(str(sector_limit_pct)):
                logger.warning(f"Sector limit exceeded for {sector}: {sector_exposure_pct:.1%} > {sector_limit_pct:.1%}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking sector exposure: {e}")
            return True  # Allow trade if check fails
    
    def check_position_limits(self, symbol, quantity, action, account_value):
        """Check if trade violates position limits with research-based improvements"""
        try:
            # Get current positions
            positions = self.broker.get_positions()

            # Find existing position for this symbol
            current_position = 0
            for pos in positions:
                if pos['symbol'] == symbol:
                    current_position = pos['quantity']
                    break

            # Calculate new position
            if action == 'BUY':
                new_position = current_position + quantity
            else:  # SELL
                new_position = current_position - quantity

            # Get current quote for value calculation
            quote = self.broker.get_quote(symbol)
            if not quote:
                logger.warning(f"No quote for {symbol}, skipping limit check")
                return True

            current_price = Decimal(str(quote['last_price']))
            position_value = abs(new_position) * current_price

            # Check max position percentage (reduced from 5% to 2%)
            max_position_value = account_value * self.max_position_pct

            if position_value > max_position_value:
                logger.warning(
                    f"Position limit exceeded: ${position_value:.2f} > ${max_position_value:.2f} "
                    f"({float(self.max_position_pct)*100:.1f}% of account)"
                )
                return False

            # Check if selling more than owned
            if action == 'SELL' and quantity > current_position:
                logger.warning(f"Attempting to sell {quantity} shares but only own {current_position}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return False

    def check_daily_loss_limit(self):
        """Check if daily loss limit has been exceeded"""
        # Note: This is a simplified check
        # In production, you'd want more sophisticated P&L tracking
        if self.daily_pnl < -abs(self.daily_loss_limit):
            logger.error(f"Daily loss limit exceeded: ${self.daily_pnl:.2f}")
            return False
        return True

    def execute_trade(self, trade_calculation):
        """Execute a calculated trade"""
        try:
            # Check market hours
            if not self.is_market_open():
                logger.warning("Market is closed, skipping trade execution")
                return False

            # Check daily loss limit
            if not self.check_daily_loss_limit():
                logger.warning("Daily loss limit exceeded, skipping trade")
                return False

            # Get account balance for limit checks
            balance_info = self.broker.get_account_balance()
            if not balance_info:
                logger.error("Could not get account balance")
                return False

            account_value = Decimal(str(balance_info['total_value']))

            # Check position limits
            if not self.check_position_limits(
                trade_calculation['symbol'],
                trade_calculation['quantity'],
                trade_calculation['action'],
                account_value
            ):
                logger.warning("Trade violates position limits")
                return False

            # Prepare order details
            order_details = {
                'symbol': trade_calculation['symbol'],
                'quantity': trade_calculation['quantity'],
                'action': trade_calculation['action'],
                'price_type': 'MARKET',  # Start with market orders
                'order_type': 'EQ'
            }

            # Execute order
            if not self.broker.account_id:
                logger.error("No account ID configured - cannot place order")
                return False
            success = self.broker.place_order(
                self.broker.account_id,
                order_details
            )

            if success:
                # Record trade
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': trade_calculation['symbol'],
                    'action': trade_calculation['action'],
                    'quantity': trade_calculation['quantity'],
                    'estimated_price': trade_calculation['estimated_price'],
                    'estimated_cost': trade_calculation['estimated_cost'],
                    'congress_amount': trade_calculation.get('congress_amount'),
                    'scale_factor': trade_calculation.get('scale_factor'),
                    'status': 'executed'
                }

                self.trade_history.append(trade_record)
                logger.info(f"Trade executed successfully: {trade_calculation['action']} "
                          f"{trade_calculation['quantity']} {trade_calculation['symbol']}")

                # Track position for stop-loss management
                if trade_calculation['action'] == 'BUY':
                    self.add_position(
                        symbol=trade_calculation['symbol'],
                        quantity=trade_calculation['quantity'],
                        entry_price=trade_calculation['estimated_price'],
                        congressional_trade_id=trade_calculation.get('congressional_trade_id')
                    )
                    self.consecutive_losses = 0  # Reset on successful buy
                elif trade_calculation['action'] == 'SELL':
                    self.remove_position(
                        symbol=trade_calculation['symbol'],
                        quantity=trade_calculation['quantity']
                    )

                return True
            else:
                logger.error("Failed to execute trade")
                return False

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False

    def process_congressional_trades(self, congress_trades):
        """Process multiple congressional trades"""
        try:
            # Get current account balance
            balance_info = self.broker.get_account_balance()
            if not balance_info:
                logger.error("Could not get account balance")
                return []

            account_balance = Decimal(str(balance_info['cash_available']))
            logger.info(f"Processing trades with account balance: ${account_balance:.2f}")

            executed_trades = []

            for congress_trade in congress_trades:
                # Calculate scaled trade
                trade_calc = self.calculate_scaled_trade(congress_trade, account_balance)

                if not trade_calc:
                    continue

                # Execute trade
                if self.execute_trade(trade_calc):
                    executed_trades.append(trade_calc)

                    # Update account balance for next calculation
                    # This is approximate - real balance would update after trade
                    account_balance -= Decimal(str(trade_calc['estimated_cost']))

                    # Small delay between trades
                    time.sleep(2)

            logger.info(f"Executed {len(executed_trades)} trades")
            return executed_trades

        except Exception as e:
            logger.error(f"Error processing congressional trades: {e}")
            return []

    def save_trade_history(self, filename='trade_history.json'):
        """Save trade history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.trade_history, f, indent=2, default=str)

            logger.info(f"Saved {len(self.trade_history)} trades to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error saving trade history: {e}")
            return False

    def load_trade_history(self, filename='trade_history.json'):
        """Load trade history from file"""
        try:
            with open(filename) as f:
                self.trade_history = json.load(f)

            logger.info(f"Loaded {len(self.trade_history)} trades from {filename}")
            return True

        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Could not load trade history from {filename}")
            self.trade_history = []
            return False
        except Exception as e:
            logger.error(f"Error loading trade history: {e}")
            return False

    def get_trade_summary(self):
        """Get summary of trading activity"""
        total_trades = len(self.trade_history)
        buy_trades = sum(1 for t in self.trade_history if t['action'] == 'BUY')
        sell_trades = total_trades - buy_trades

        total_cost = sum(t.get('estimated_cost', 0) for t in self.trade_history)

        return {
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'total_estimated_cost': total_cost,
            'last_trade': self.trade_history[-1] if self.trade_history else None,
            'daily_pnl': float(self.daily_pnl),
            'open_positions': len(self.positions),
            'consecutive_losses': self.consecutive_losses
        }

    # ==================== POSITION MANAGEMENT ====================

    def _load_positions(self):
        """Load saved positions from file"""
        positions_file = 'data/positions.json'
        try:
            if os.path.exists(positions_file):
                with open(positions_file) as f:
                    data = json.load(f)
                for symbol, pos_data in data.items():
                    self.positions[symbol] = Position.from_dict(pos_data)
                logger.info(f"Loaded {len(self.positions)} positions from file")
        except Exception as e:
            logger.warning(f"Could not load positions: {e}")

    def _save_positions(self):
        """Save positions to file"""
        positions_file = 'data/positions.json'
        try:
            os.makedirs('data', exist_ok=True)
            data = {symbol: pos.to_dict() for symbol, pos in self.positions.items()}
            with open(positions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save positions: {e}")

    def add_position(self, symbol: str, quantity: int, entry_price: float,
                    congressional_trade_id: int = None):
        """Add or update a position"""
        if symbol in self.positions:
            # Average into existing position
            existing = self.positions[symbol]
            total_qty = existing.quantity + quantity
            avg_price = ((existing.entry_price * existing.quantity) +
                        (entry_price * quantity)) / total_qty
            existing.quantity = total_qty
            existing.entry_price = avg_price
        else:
            # Create new position
            pos = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=entry_price,
                entry_date=datetime.now(),
                congressional_trade_id=congressional_trade_id
            )
            # Set initial stop-loss (fixed percentage below entry)
            pos.stop_loss_price = entry_price * (1 - float(self.position_stop_loss))
            self.positions[symbol] = pos

        self._save_positions()
        logger.info(f"Added position: {quantity} {symbol} @ ${entry_price:.2f}")

    def remove_position(self, symbol: str, quantity: int = None):
        """Remove or reduce a position"""
        if symbol not in self.positions:
            return

        pos = self.positions[symbol]
        if quantity is None or quantity >= pos.quantity:
            del self.positions[symbol]
        else:
            pos.quantity -= quantity

        self._save_positions()

    # ==================== STOP-LOSS MANAGEMENT ====================

    def check_stop_losses(self) -> list:
        """Check all positions for stop-loss triggers, return symbols to sell"""
        triggered = []

        for symbol, pos in self.positions.items():
            try:
                quote = self.broker.get_quote(symbol)
                if not quote:
                    continue

                current_price = quote['last_price']

                # Update position with current price (adjusts trailing stop)
                pos.update_price(current_price)

                # Check if trailing stop should be activated
                gain_pct = pos.get_unrealized_pnl_percent(current_price)
                if gain_pct >= float(self.trailing_stop_activation) and not pos.trailing_stop_active:
                    pos.trailing_stop_active = True
                    pos.trailing_stop_percent = float(self.trailing_stop_percent)
                    pos.stop_loss_price = pos.highest_price * (1 - pos.trailing_stop_percent)
                    logger.info(f"Trailing stop activated for {symbol} at ${pos.stop_loss_price:.2f}")

                # Check if stop-loss triggered
                if pos.check_stop_loss(current_price):
                    triggered.append({
                        'symbol': symbol,
                        'quantity': pos.quantity,
                        'current_price': current_price,
                        'stop_price': pos.stop_loss_price,
                        'entry_price': pos.entry_price,
                        'pnl_percent': gain_pct * 100
                    })
                    logger.warning(f"STOP-LOSS TRIGGERED: {symbol} at ${current_price:.2f} "
                                  f"(stop: ${pos.stop_loss_price:.2f})")

            except Exception as e:
                logger.error(f"Error checking stop-loss for {symbol}: {e}")

        self._save_positions()
        return triggered

    def execute_stop_loss(self, stop_info: dict) -> bool:
        """Execute a stop-loss sell order"""
        try:
            symbol = stop_info['symbol']
            quantity = stop_info['quantity']

            logger.info(f"Executing stop-loss: SELL {quantity} {symbol}")

            order_details = {
                'symbol': symbol,
                'quantity': quantity,
                'action': 'SELL',
                'price_type': 'MARKET',
                'order_type': 'EQ'
            }

            success = self.broker.place_order(
                self.broker.account_id,
                order_details
            )

            if success:
                # Record the trade
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'trigger': 'STOP_LOSS',
                    'stop_price': stop_info['stop_price'],
                    'entry_price': stop_info['entry_price'],
                    'pnl_percent': stop_info['pnl_percent'],
                    'status': 'executed'
                }
                self.trade_history.append(trade_record)

                # Update consecutive losses
                if stop_info['pnl_percent'] < 0:
                    self.consecutive_losses += 1
                else:
                    self.consecutive_losses = 0

                # Remove position
                self.remove_position(symbol)

                return True
            else:
                logger.error(f"Failed to execute stop-loss for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error executing stop-loss: {e}")
            return False

    def run_stop_loss_monitor(self):
        """Run a single cycle of stop-loss monitoring"""
        if not self.is_market_open():
            return []

        triggered = self.check_stop_losses()
        executed = []

        for stop_info in triggered:
            if self.execute_stop_loss(stop_info):
                executed.append(stop_info)

        return executed

    # ==================== HOLDING PERIOD MANAGEMENT ====================

    def check_holding_periods(self) -> list:
        """Check for positions that have exceeded holding period"""
        to_sell = []
        target_hold = timedelta(days=self.holding_period_days)

        for symbol, pos in self.positions.items():
            hold_duration = datetime.now() - pos.entry_date
            if hold_duration >= target_hold:
                try:
                    quote = self.broker.get_quote(symbol)
                    current_price = quote.get('last_price', pos.entry_price) if quote else pos.entry_price

                    to_sell.append({
                        'symbol': symbol,
                        'quantity': pos.quantity,
                        'current_price': current_price,
                        'entry_price': pos.entry_price,
                        'hold_days': hold_duration.days,
                        'pnl_percent': pos.get_unrealized_pnl_percent(current_price) * 100
                    })
                    logger.info(f"Position {symbol} exceeded holding period ({hold_duration.days} days)")
                except Exception as e:
                    logger.error(f"Error checking holding period for {symbol}: {e}")

        return to_sell

    # ==================== PORTFOLIO RISK MANAGEMENT ====================

    def check_portfolio_risk(self) -> dict:
        """Check overall portfolio risk metrics with research-based improvements"""
        try:
            balance = self.broker.get_account_balance()
            if not balance:
                return {'status': 'unknown', 'message': 'Could not get balance'}

            total_value = Decimal(str(balance['total_value']))

            # Track peak value for drawdown
            if self.peak_portfolio_value is None or total_value > self.peak_portfolio_value:
                self.peak_portfolio_value = total_value

            # Calculate drawdown
            drawdown = (self.peak_portfolio_value - total_value) / self.peak_portfolio_value

            # Research-based risk checks
            warnings = []
            halt_trading = False

            # Daily loss limit check (increased from 3% to 5%)
            if self.daily_pnl < -abs(self.daily_loss_limit):
                warnings.append(f"DAILY LOSS LIMIT EXCEEDED: {self.daily_pnl:.1%}")
                halt_trading = True

            if drawdown >= self.max_drawdown:
                warnings.append(f"MAX DRAWDOWN EXCEEDED: {drawdown*100:.1f}%")
                halt_trading = True

            if self.consecutive_losses >= self.consecutive_loss_limit:
                warnings.append(f"CONSECUTIVE LOSS LIMIT: {self.consecutive_losses} losses")
                halt_trading = True

            if len(self.positions) >= self.max_positions:
                warnings.append(f"MAX POSITIONS REACHED: {len(self.positions)}")

            # Sector concentration check
            sector_warnings = self._check_sector_concentration()
            warnings.extend(sector_warnings)

            # Correlation check (simplified)
            if self._check_portfolio_correlation():
                warnings.append("HIGH PORTFOLIO CORRELATION DETECTED")

            # Performance benchmarking
            benchmark_performance = self._get_benchmark_performance()
            
            return {
                'status': 'halt' if halt_trading else 'ok',
                'total_value': float(total_value),
                'peak_value': float(self.peak_portfolio_value),
                'drawdown': float(drawdown) * 100,
                'open_positions': len(self.positions),
                'consecutive_losses': self.consecutive_losses,
                'daily_pnl': float(self.daily_pnl),
                'daily_loss_limit': float(self.daily_loss_limit) * 100,
                'benchmark_performance': benchmark_performance,
                'warnings': warnings
            }

        except Exception as e:
            logger.error(f"Error checking portfolio risk: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _check_sector_concentration(self):
        """Check for excessive sector concentration"""
        warnings = []
        try:
            positions = self.broker.get_positions()
            if not positions:
                return warnings
            
            # Group positions by sector
            sector_values = {}
            total_value = Decimal('0')
            
            for pos in positions:
                sector = pos.get('sector', 'unknown')
                market_value = Decimal(str(pos.get('market_value', 0)))
                sector_values[sector] = sector_values.get(sector, Decimal('0')) + market_value
                total_value += market_value
            
            # Check each sector against limits
            for sector, sector_value in sector_values.items():
                sector_pct = sector_value / total_value if total_value > 0 else Decimal('0')
                sector_limit = Decimal(str(self.sector_exposure_limits.get(sector.lower(), 0.25)))
                
                if sector_pct > sector_limit:
                    warnings.append(f"SECTOR CONCENTRATION: {sector} {sector_pct:.1%} > {sector_limit:.1%}")
        
        except Exception as e:
            logger.error(f"Error checking sector concentration: {e}")
        
        return warnings
    
    def _check_portfolio_correlation(self):
        """Check portfolio correlation (simplified implementation)"""
        # In production, this would calculate correlation matrix
        # For now, return False (no high correlation detected)
        return False
    
    def _get_benchmark_performance(self):
        """Get benchmark performance comparison"""
        try:
            # Simplified - in production, fetch actual benchmark data
            return {
                'benchmark': self.performance_benchmark,
                'vs_benchmark': 'N/A',  # Would calculate actual performance
                'tracking': True
            }
        except Exception as e:
            logger.error(f"Error getting benchmark performance: {e}")
            return {'benchmark': self.performance_benchmark, 'error': str(e)}

    def get_position_summary(self) -> list:
        """Get summary of all open positions"""
        summary = []

        for symbol, pos in self.positions.items():
            try:
                quote = self.broker.get_quote(symbol)
                current_price = quote['last_price'] if quote else pos.entry_price

                summary.append({
                    'symbol': symbol,
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': current_price,
                    'market_value': current_price * pos.quantity,
                    'unrealized_pnl': pos.get_unrealized_pnl(current_price),
                    'pnl_percent': pos.get_unrealized_pnl_percent(current_price) * 100,
                    'stop_loss': pos.stop_loss_price,
                    'trailing_active': pos.trailing_stop_active,
                    'days_held': (datetime.now() - pos.entry_date).days
                })
            except Exception as e:
                logger.error(f"Error getting summary for {symbol}: {e}")

        return sorted(summary, key=lambda x: x.get('pnl_percent', 0), reverse=True)
