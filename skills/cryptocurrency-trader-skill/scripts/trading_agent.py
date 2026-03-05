#!/usr/bin/env python3
"""
AI Trading Agent - Main Interactive Module
Prevents hallucinations, identifies opportunities, guides beginner traders
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import warnings
warnings.filterwarnings('ignore')


class TradingAgent:
    """Main trading agent with anti-hallucination and beginner-friendly interface"""
    
    def __init__(self, balance: float, exchange_name: str = 'binance'):
        """
        Initialize trading agent
        
        Args:
            balance: Account balance in USD
            exchange_name: Exchange to use (default: binance)
        """
        self.balance = balance
        self.exchange_name = exchange_name
        self.exchange = self._initialize_exchange()
        
        # Market categories for systematic analysis
        self.categories = {
            'Major Coins': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'],
            'AI Tokens': ['RENDER/USDT', 'FET/USDT', 'AGIX/USDT', 'OCEAN/USDT', 'TAO/USDT'],
            'Layer 1': ['ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'ATOM/USDT'],
            'Layer 2': ['MATIC/USDT', 'ARB/USDT', 'OP/USDT'],
            'DeFi': ['UNI/USDT', 'AAVE/USDT', 'LINK/USDT', 'MKR/USDT'],
            'Meme': ['DOGE/USDT', 'SHIB/USDT', 'PEPE/USDT']
        }
        
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            return exchange
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.exchange_name}: {str(e)}")
    
    def fetch_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        Fetch real-time OHLCV data with validation
        
        Returns DataFrame or None if data is invalid
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Anti-hallucination: Validate data
            validation = self._validate_market_data(df, symbol)
            if not validation['valid']:
                print(f"⚠️ DATA WARNING for {symbol}: {validation['issues']}")
                return None
                
            return df
            
        except Exception as e:
            print(f"❌ Failed to fetch {symbol}: {str(e)}")
            return None
    
    def _validate_market_data(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Validate market data to prevent hallucinations"""
        issues = []
        
        # Check for negative or zero prices
        if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
            issues.append("Contains negative or zero prices")
        
        # Check for missing data
        if df.isnull().any().any():
            issues.append("Contains missing values")
        
        # Check OHLC logic
        if not ((df['high'] >= df['low']).all() and 
                (df['high'] >= df['open']).all() and 
                (df['high'] >= df['close']).all()):
            issues.append("OHLC logic violated")
        
        # Check data freshness (< 5 minutes old)
        latest_time = df['timestamp'].iloc[-1]
        age = (datetime.now() - latest_time.to_pydatetime()).total_seconds()
        if age > 300:
            issues.append(f"Stale data: {age/60:.1f} minutes old")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'data_age_seconds': age
        }
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators with validation"""
        try:
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(14).mean()
            
            # Bollinger Bands
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            bb_upper = sma + (std * 2)
            bb_lower = sma - (std * 2)
            
            indicators = {
                'rsi': rsi.iloc[-1],
                'macd': macd.iloc[-1],
                'macd_signal': signal.iloc[-1],
                'atr': atr.iloc[-1],
                'bb_upper': bb_upper.iloc[-1],
                'bb_lower': bb_lower.iloc[-1],
                'current_price': df['close'].iloc[-1]
            }
            
            # Validate indicator ranges
            if not (0 <= indicators['rsi'] <= 100):
                return {'error': 'Invalid RSI value'}
            if indicators['atr'] < 0:
                return {'error': 'Invalid ATR value'}
                
            return indicators
            
        except Exception as e:
            return {'error': f'Indicator calculation failed: {str(e)}'}
    
    def analyze_opportunity(self, symbol: str, timeframes: List[str] = ['15m', '1h', '4h']) -> Dict:
        """
        Comprehensive multi-timeframe analysis with anti-hallucination
        
        Returns analysis with confidence score and recommendations
        """
        print(f"\n🔍 Analyzing {symbol}...")
        
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'safe_to_use': False,
            'warnings': [],
            'timeframe_data': {}
        }
        
        # Multi-timeframe analysis
        valid_timeframes = 0
        for tf in timeframes:
            df = self.fetch_market_data(symbol, tf)
            if df is not None:
                indicators = self.calculate_indicators(df)
                if 'error' not in indicators:
                    analysis['timeframe_data'][tf] = indicators
                    valid_timeframes += 1
        
        # Anti-hallucination: Require minimum data quality
        if valid_timeframes < 2:
            analysis['warnings'].append("Insufficient valid timeframes")
            analysis['recommendation'] = "⛔ DO NOT TRADE - Insufficient data"
            return analysis
        
        # Calculate consensus
        if analysis['timeframe_data']:
            analysis.update(self._calculate_consensus(analysis['timeframe_data']))
        else:
            analysis['action'] = 'WAIT'
            analysis['confidence'] = 0
            analysis['current_price'] = None
        
        # Apply circuit breakers
        analysis = self._apply_circuit_breakers(analysis)
        
        # Calculate position sizing
        if analysis['safe_to_use']:
            analysis['position_sizing'] = self._calculate_position_size(
                analysis['entry_price'],
                analysis['stop_loss'],
                self.balance
            )
        
        return analysis
    
    def _calculate_consensus(self, timeframe_data: Dict) -> Dict:
        """Calculate trading signals from multi-timeframe analysis"""
        signals = []
        rsi_values = []
        macd_signals = []
        
        for tf, data in timeframe_data.items():
            rsi_values.append(data['rsi'])
            
            # RSI signals
            if data['rsi'] < 30:
                signals.append('OVERSOLD')
            elif data['rsi'] > 70:
                signals.append('OVERBOUGHT')
            
            # MACD signals
            if data['macd'] > data['macd_signal']:
                macd_signals.append('BULLISH')
            else:
                macd_signals.append('BEARISH')
        
        avg_rsi = np.mean(rsi_values)
        
        # Determine action
        bullish_count = macd_signals.count('BULLISH')
        bearish_count = macd_signals.count('BEARISH')
        
        if bullish_count > bearish_count and avg_rsi < 60:
            action = 'LONG'
            confidence = int(min(95, (bullish_count / len(macd_signals)) * 100))
        elif bearish_count > bullish_count and avg_rsi > 40:
            action = 'SHORT'
            confidence = int(min(95, (bearish_count / len(macd_signals)) * 100))
        else:
            action = 'WAIT'
            confidence = 0
        
        # Get current price from most recent timeframe
        current_price = list(timeframe_data.values())[0]['current_price']
        atr = list(timeframe_data.values())[0]['atr']
        
        # Calculate entry, stop loss, take profit
        if action == 'LONG':
            entry_price = current_price
            stop_loss = current_price - (2 * atr)
            take_profit = current_price + (3 * atr)
        elif action == 'SHORT':
            entry_price = current_price
            stop_loss = current_price + (2 * atr)
            take_profit = current_price - (3 * atr)
        else:
            entry_price = current_price
            stop_loss = None
            take_profit = None
        
        # Calculate risk/reward (with validation)
        if stop_loss and take_profit:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward = round(reward / risk, 1) if risk > 0 else 0
        else:
            risk_reward = 0
        
        return {
            'action': action,
            'confidence': confidence,
            'current_price': round(current_price, 2),
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2) if stop_loss else None,
            'take_profit': round(take_profit, 2) if take_profit else None,
            'risk_reward': risk_reward,
            'avg_rsi': round(avg_rsi, 1)
        }
    
    def _apply_circuit_breakers(self, analysis: Dict) -> Dict:
        """Apply mandatory trade blocks and warnings"""
        
        # Mandatory blocks
        blocks = []
        
        if analysis['action'] == 'WAIT':
            blocks.append("⛔ No clear signal")
        
        if analysis['confidence'] < 40:
            blocks.append("⛔ Confidence too low")
        
        if analysis.get('risk_reward', 0) < 1.5:
            blocks.append("⛔ Poor risk/reward ratio")
        
        if len(analysis['timeframe_data']) < 2:
            blocks.append("⛔ Insufficient timeframes")
        
        # Warnings (don't block trade)
        if analysis['confidence'] > 90:
            analysis['warnings'].append("⚠️ Unrealistically high confidence - be cautious")
        
        if analysis.get('risk_reward', 0) > 8:
            analysis['warnings'].append("⚠️ Unrealistic risk/reward - verify manually")
        
        # Determine if safe to use
        analysis['blocks'] = blocks
        analysis['safe_to_use'] = len(blocks) == 0
        
        if analysis['safe_to_use']:
            analysis['recommendation'] = f"✅ {analysis['action']} at ${analysis['entry_price']}"
        else:
            analysis['recommendation'] = "⛔ DO NOT TRADE - " + "; ".join(blocks)
        
        return analysis
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float, balance: float) -> Dict:
        """
        Calculate position size with 2% max risk rule
        
        Anti-hallucination: Always include trading fees
        """
        max_risk_usd = balance * 0.02  # Risk max 2% of account
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return {'error': 'Invalid stop loss'}
        
        # Calculate position size
        position_size_coin = max_risk_usd / price_risk
        position_value_usd = position_size_coin * entry_price
        
        # Ensure position doesn't exceed 10% of account
        max_position = balance * 0.10
        if position_value_usd > max_position:
            position_value_usd = max_position
            position_size_coin = position_value_usd / entry_price
        
        # Calculate fees (0.2% minimum)
        trading_fees = position_value_usd * 0.002
        
        return {
            'position_size_coin': round(position_size_coin, 6),
            'position_value_usd': round(position_value_usd, 2),
            'risk_usd': round(max_risk_usd, 2),
            'risk_percent': 2.0,
            'trading_fees': round(trading_fees, 2)
        }
    
    def scan_market(self) -> List[Dict]:
        """
        Scan all market categories for top opportunities
        
        Returns top 5 opportunities ranked by expected value
        """
        print("\n" + "="*60)
        print("🔬 MARKET SCANNER - Finding Top 5 Opportunities")
        print("="*60)
        
        all_opportunities = []
        
        for category, symbols in self.categories.items():
            print(f"\n📊 Scanning {category}...")
            
            for symbol in symbols:
                try:
                    analysis = self.analyze_opportunity(symbol, timeframes=['15m', '1h'])
                    
                    if analysis['safe_to_use']:
                        # Calculate expected value score
                        ev_score = (analysis['confidence'] / 100) * analysis['risk_reward']
                        analysis['ev_score'] = round(ev_score, 2)
                        analysis['category'] = category
                        all_opportunities.append(analysis)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"  ⚠️ Skipping {symbol}: {str(e)}")
        
        # Sort by expected value and return top 5
        all_opportunities.sort(key=lambda x: x['ev_score'], reverse=True)
        return all_opportunities[:5]
    
    def display_opportunity(self, analysis: Dict, rank: int = None):
        """Display opportunity in beginner-friendly format"""
        
        if rank:
            print(f"\n{'='*60}")
            print(f"#{rank} OPPORTUNITY: {analysis['symbol']} ({analysis['category']})")
            print(f"{'='*60}")
        
        # Handle missing price data
        if analysis.get('current_price') is None:
            print(f"\n❌ Unable to fetch data for {analysis['symbol']}")
            print(f"📊 RECOMMENDATION: {analysis.get('recommendation', '⛔ DO NOT TRADE')}")
            if analysis.get('warnings'):
                print(f"\n⚠️ WARNINGS:")
                for warning in analysis['warnings']:
                    print(f"   {warning}")
            return
        
        print(f"\n💰 CURRENT PRICE: ${analysis['current_price']}")
        print(f"📈 RECOMMENDATION: {analysis['recommendation']}")
        
        if analysis['safe_to_use']:
            print(f"\n🎯 ACTION: {analysis['action']}")
            print(f"📊 CONFIDENCE: {analysis['confidence']}% (NOT a guarantee)")
            print(f"💵 ENTRY PRICE: ${analysis['entry_price']}")
            print(f"🛑 STOP LOSS: ${analysis['stop_loss']}")
            print(f"🎁 TAKE PROFIT: ${analysis['take_profit']}")
            print(f"⚖️ RISK/REWARD: 1:{analysis['risk_reward']}")
            
            if 'position_sizing' in analysis:
                ps = analysis['position_sizing']
                print(f"\n💼 POSITION SIZING (for ${self.balance} account):")
                print(f"   • Buy Amount: {ps['position_size_coin']} coins")
                print(f"   • Position Value: ${ps['position_value_usd']}")
                print(f"   • Risk Amount: ${ps['risk_usd']} (2% of account)")
                print(f"   • Trading Fees: ${ps['trading_fees']}")
            
            if 'ev_score' in analysis:
                print(f"\n⭐ OPPORTUNITY SCORE: {analysis['ev_score']}/10")
        
        if analysis['warnings']:
            print(f"\n⚠️ WARNINGS:")
            for warning in analysis['warnings']:
                print(f"   {warning}")
        
        if not analysis['safe_to_use'] and 'blocks' in analysis:
            print(f"\n🚫 TRADE BLOCKED:")
            for block in analysis['blocks']:
                print(f"   {block}")


def interactive_session():
    """Main interactive trading session"""
    print("\n" + "="*60)
    print("🤖 AI TRADING AGENT - Beginner-Friendly Edition")
    print("="*60)
    print("\nThis AI helps prevent common trading mistakes by:")
    print("✓ Analyzing real market data (no hallucinations)")
    print("✓ Finding the best opportunities automatically")
    print("✓ Explaining everything in simple terms")
    print("✓ Protecting you from bad trades\n")
    
    # Step 1: Get account balance
    while True:
        try:
            balance_input = input("💵 Enter your account balance in USD (e.g., 1000): $")
            balance = float(balance_input)
            if balance <= 0:
                print("⚠️ Balance must be positive. Try again.")
                continue
            break
        except ValueError:
            print("⚠️ Please enter a valid number.")
    
    # Initialize agent
    agent = TradingAgent(balance)
    
    # Step 2: Choose mode
    print("\n" + "="*60)
    print("CHOOSE YOUR MODE:")
    print("="*60)
    print("1. 🎯 Analyze specific coin (e.g., BTC/USDT)")
    print("2. 🔬 Scan entire market for top 5 opportunities")
    
    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ['1', '2']:
            break
        print("⚠️ Please enter 1 or 2.")
    
    if choice == '1':
        # Specific coin analysis
        symbol = input("\n💱 Enter trading pair (e.g., BTC/USDT): ").strip().upper()
        
        print("\n" + "="*60)
        print(f"ANALYZING {symbol}")
        print("="*60)
        
        analysis = agent.analyze_opportunity(symbol, timeframes=['15m', '1h', '4h'])
        agent.display_opportunity(analysis)
        
    else:
        # Market scan
        top_opportunities = agent.scan_market()
        
        if not top_opportunities:
            print("\n⚠️ No safe trading opportunities found at this time.")
            print("This is normal - most of the time, the best action is to WAIT.")
            return
        
        print("\n" + "="*60)
        print("🏆 TOP 5 OPPORTUNITIES (Ranked by Expected Value)")
        print("="*60)
        
        for i, opp in enumerate(top_opportunities, 1):
            agent.display_opportunity(opp, rank=i)
    
    print("\n" + "="*60)
    print("📚 BEGINNER'S REMINDER:")
    print("="*60)
    print("• This AI analyzes data, but markets are unpredictable")
    print("• NEVER risk more than you can afford to lose")
    print("• ALWAYS use stop losses to protect your account")
    print("• Start small and learn as you go")
    print("• Past performance does NOT guarantee future results")
    print("="*60 + "\n")


if __name__ == "__main__":
    interactive_session()
