#!/usr/bin/env python3
"""
Kalshi Autopilot Setup Wizard

Interactive setup for Kalshi trading bot including:
- API key configuration
- Connection testing
- Strategy selection
- Risk parameter configuration
- Optional cron job setup

Usage:
    python setup.py
"""

import os
import sys
import json
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv, set_key
except ImportError:
    print("❌ Missing dependency: python-dotenv")
    print("Install with: pip install python-dotenv")
    sys.exit(1)

# Strategy presets
STRATEGY_PRESETS = {
    "model_follower": {
        "name": "Model Follower",
        "description": "Follow any 3%+ probability edge across all sports. Balanced approach.",
        "config": {
            "strategy": "model_follower",
            "sports": ["cbb", "nba", "nhl", "soccer"],
            "min_edge_pct": 3.0,
            "sizing": {
                "method": "flat_pct",
                "flat_pct": 2.0,
                "kelly_fraction": 0.25,
                "max_position_pct": 5.0
            },
            "risk": {
                "max_daily_loss_pct": 10.0,
                "max_open_positions": 10,
                "max_daily_bets": 15,
                "stop_loss_enabled": True
            },
            "auto_trade": False,
            "dry_run": True,
            "scan_interval_minutes": 30,
            "fuku_api_base": "https://cbb-predictions-api-nzpk.onrender.com"
        }
    },
    "spread_sniper": {
        "name": "Spread Sniper",
        "description": "Focus on spread markets with 2+ point edges. CBB/NBA only.",
        "config": {
            "strategy": "spread_sniper",
            "sports": ["cbb", "nba"],
            "min_edge_pct": 4.0,
            "sizing": {
                "method": "flat_pct",
                "flat_pct": 2.0,
                "kelly_fraction": 0.25,
                "max_position_pct": 5.0
            },
            "risk": {
                "max_daily_loss_pct": 8.0,
                "max_open_positions": 8,
                "max_daily_bets": 10,
                "stop_loss_enabled": True
            },
            "auto_trade": False,
            "dry_run": True,
            "scan_interval_minutes": 30,
            "fuku_api_base": "https://cbb-predictions-api-nzpk.onrender.com"
        }
    },
    "totals_specialist": {
        "name": "Totals Specialist",
        "description": "Target over/under markets with 3+ point edges. CBB/NBA focus.",
        "config": {
            "strategy": "totals_specialist",
            "sports": ["cbb", "nba"],
            "min_edge_pct": 3.5,
            "sizing": {
                "method": "flat_pct",
                "flat_pct": 1.5,
                "kelly_fraction": 0.25,
                "max_position_pct": 4.0
            },
            "risk": {
                "max_daily_loss_pct": 7.0,
                "max_open_positions": 12,
                "max_daily_bets": 12,
                "stop_loss_enabled": True
            },
            "auto_trade": False,
            "dry_run": True,
            "scan_interval_minutes": 30,
            "fuku_api_base": "https://cbb-predictions-api-nzpk.onrender.com"
        }
    },
    "contrarian": {
        "name": "Contrarian",
        "description": "Fade heavily-favored public side when model disagrees. All sports.",
        "config": {
            "strategy": "contrarian",
            "sports": ["cbb", "nba", "nhl", "soccer"],
            "min_edge_pct": 4.0,
            "sizing": {
                "method": "flat_pct",
                "flat_pct": 1.0,
                "kelly_fraction": 0.25,
                "max_position_pct": 3.0
            },
            "risk": {
                "max_daily_loss_pct": 5.0,
                "max_open_positions": 8,
                "max_daily_bets": 8,
                "stop_loss_enabled": True
            },
            "auto_trade": False,
            "dry_run": True,
            "scan_interval_minutes": 30,
            "fuku_api_base": "https://cbb-predictions-api-nzpk.onrender.com"
        }
    },
    "conservative": {
        "name": "Conservative",
        "description": "Only bet 5%+ probability edges with small sizing. Very selective.",
        "config": {
            "strategy": "conservative",
            "sports": ["cbb", "nba", "nhl", "soccer"],
            "min_edge_pct": 5.0,
            "sizing": {
                "method": "flat_pct",
                "flat_pct": 1.0,
                "kelly_fraction": 0.1,
                "max_position_pct": 2.0
            },
            "risk": {
                "max_daily_loss_pct": 3.0,
                "max_open_positions": 5,
                "max_daily_bets": 5,
                "stop_loss_enabled": True
            },
            "auto_trade": False,
            "dry_run": True,
            "scan_interval_minutes": 60,
            "fuku_api_base": "https://cbb-predictions-api-nzpk.onrender.com"
        }
    },
    "custom": {
        "name": "Custom",
        "description": "Configure your own parameters",
        "config": None  # Will be built interactively
    }
}

class SetupWizard:
    """Interactive setup wizard."""
    
    def __init__(self):
        self.skill_dir = os.path.dirname(os.path.dirname(__file__))
        self.env_path = os.path.join(self.skill_dir, ".env")
        self.config_path = os.path.join(self.skill_dir, "config", "config.json")
        
        # Ensure directories exist
        os.makedirs(os.path.join(self.skill_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(self.skill_dir, "logs"), exist_ok=True)
    
    def print_header(self):
        """Print setup wizard header."""
        print("🤖 Kalshi Autopilot Setup Wizard")
        print("=" * 50)
        print("This wizard will help you configure the Kalshi trading bot.")
        print("Your API keys will be stored locally and never transmitted externally.")
        print()
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        print("📋 Checking dependencies...")
        
        try:
            import httpx
            import cryptography
            print("✅ httpx and cryptography installed")
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            print("Install with: pip install httpx cryptography python-dotenv")
            return False
    
    def setup_api_credentials(self) -> bool:
        """Setup Kalshi API credentials."""
        print("🔑 Kalshi API Credentials Setup")
        print("-" * 30)
        
        # Check if credentials already exist
        if os.path.exists(self.env_path):
            load_dotenv(self.env_path)
            existing_key_id = os.getenv("KALSHI_API_KEY_ID")
            existing_private_key = os.getenv("KALSHI_PRIVATE_KEY")
            
            if existing_key_id and existing_private_key:
                print("✅ Existing credentials found")
                use_existing = input("Use existing credentials? (Y/n): ").strip().lower()
                if use_existing in ("", "y", "yes"):
                    return self._test_connection()
        
        print("\nTo get your Kalshi API credentials:")
        print("1. Go to https://kalshi.com/profile/api")
        print("2. Generate an API key")
        print("3. Download the private key file")
        print()
        
        # Get API key ID
        while True:
            api_key_id = input("Enter your Kalshi API Key ID: ").strip()
            if api_key_id:
                break
            print("❌ API Key ID cannot be empty")
        
        # Get private key
        print("\nPrivate Key Setup:")
        print("Option 1: Paste the entire private key (including -----BEGIN/END lines)")
        print("Option 2: Provide path to private key file")
        
        while True:
            key_input = input("\nEnter private key or file path: ").strip()
            if not key_input:
                print("❌ Private key cannot be empty")
                continue
            
            # Check if it's a file path
            if os.path.exists(key_input):
                try:
                    with open(key_input) as f:
                        private_key = f.read().strip()
                    print("✅ Private key loaded from file")
                    break
                except Exception as e:
                    print(f"❌ Error reading file: {e}")
                    continue
            
            # Check if it's the key content
            elif "-----BEGIN" in key_input and "-----END" in key_input:
                private_key = key_input
                break
            
            else:
                print("❌ Invalid private key format. Must include -----BEGIN and -----END lines")
        
        # Save credentials
        try:
            set_key(self.env_path, "KALSHI_API_KEY_ID", api_key_id)
            set_key(self.env_path, "KALSHI_PRIVATE_KEY", private_key)
            print("✅ Credentials saved to .env file")
        except Exception as e:
            print(f"❌ Error saving credentials: {e}")
            return False
        
        return self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test Kalshi API connection."""
        print("\n🧪 Testing connection...")
        
        try:
            # Import here to ensure .env is loaded
            from kalshi_client import KalshiClient
            
            client = KalshiClient()
            
            if not client.is_configured():
                print("❌ Client configuration failed")
                return False
            
            # Test with balance endpoint
            result = client.get_balance()
            
            if result["success"]:
                balance = result["balance_dollars"]
                print(f"✅ Connection successful! Account balance: ${balance:.2f}")
                return True
            else:
                print(f"❌ Connection failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def select_strategy(self) -> Dict:
        """Strategy selection interface."""
        print("\n🎯 Strategy Selection")
        print("-" * 20)
        
        print("Available strategies:")
        strategies = list(STRATEGY_PRESETS.keys())
        
        for i, (key, preset) in enumerate(STRATEGY_PRESETS.items(), 1):
            print(f"  {i}. {preset['name']} - {preset['description']}")
        
        while True:
            try:
                choice = input(f"\nSelect strategy (1-{len(strategies)}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(strategies):
                    strategy_key = strategies[choice_idx]
                    break
                else:
                    print(f"❌ Invalid choice. Enter 1-{len(strategies)}")
            except ValueError:
                print("❌ Please enter a number")
        
        selected = STRATEGY_PRESETS[strategy_key]
        print(f"\n✅ Selected: {selected['name']}")
        
        if strategy_key == "custom":
            return self._configure_custom_strategy()
        else:
            # Show configuration and allow modifications
            config = selected["config"].copy()
            print("\nStrategy configuration:")
            self._print_config(config)
            
            modify = input("\nModify configuration? (y/N): ").strip().lower()
            if modify in ("y", "yes"):
                return self._modify_config(config)
            else:
                return config
    
    def _configure_custom_strategy(self) -> Dict:
        """Configure custom strategy interactively."""
        print("\n🛠️  Custom Strategy Configuration")
        
        config = {
            "strategy": "custom",
            "sports": [],
            "min_edge_pct": 3.0,
            "sizing": {
                "method": "flat_pct",
                "flat_pct": 2.0,
                "kelly_fraction": 0.25,
                "max_position_pct": 5.0
            },
            "risk": {
                "max_daily_loss_pct": 10.0,
                "max_open_positions": 10,
                "max_daily_bets": 15,
                "stop_loss_enabled": True
            },
            "auto_trade": False,
            "dry_run": True,
            "scan_interval_minutes": 30,
            "fuku_api_base": "https://cbb-predictions-api-nzpk.onrender.com"
        }
        
        # Sports selection
        available_sports = ["cbb", "nba", "nhl", "soccer"]
        print("\nSelect sports to trade (space-separated):")
        for sport in available_sports:
            print(f"  {sport.upper()} - {sport}")
        
        while True:
            sports_input = input(f"Sports ({' '.join(available_sports)}): ").strip().lower()
            if not sports_input:
                config["sports"] = available_sports  # Default to all
                break
            
            selected_sports = sports_input.split()
            if all(sport in available_sports for sport in selected_sports):
                config["sports"] = selected_sports
                break
            else:
                print("❌ Invalid sport. Use: cbb, nba, nhl, soccer")
        
        # Edge threshold
        while True:
            try:
                edge = float(input("Minimum edge percentage (3.0): ") or "3.0")
                if 0.5 <= edge <= 20.0:
                    config["min_edge_pct"] = edge
                    break
                else:
                    print("❌ Edge must be between 0.5% and 20%")
            except ValueError:
                print("❌ Please enter a number")
        
        # Position sizing
        sizing_methods = ["flat_pct", "flat_amount", "kelly"]
        print(f"\nPosition sizing methods:")
        for i, method in enumerate(sizing_methods, 1):
            print(f"  {i}. {method}")
        
        while True:
            try:
                choice = int(input("Select sizing method (1): ") or "1")
                if 1 <= choice <= len(sizing_methods):
                    config["sizing"]["method"] = sizing_methods[choice - 1]
                    break
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a number")
        
        # Position size
        if config["sizing"]["method"] == "flat_pct":
            while True:
                try:
                    pct = float(input("Position size percentage (2.0): ") or "2.0")
                    if 0.1 <= pct <= 10.0:
                        config["sizing"]["flat_pct"] = pct
                        break
                    else:
                        print("❌ Position size must be between 0.1% and 10%")
                except ValueError:
                    print("❌ Please enter a number")
        
        elif config["sizing"]["method"] == "flat_amount":
            while True:
                try:
                    amount = float(input("Position size in dollars (100): ") or "100")
                    if 1 <= amount <= 1000:
                        config["sizing"]["flat_amount"] = amount
                        break
                    else:
                        print("❌ Amount must be between $1 and $1000")
                except ValueError:
                    print("❌ Please enter a number")
        
        # Risk limits
        print("\nRisk Management:")
        
        while True:
            try:
                max_loss = float(input("Max daily loss percentage (10.0): ") or "10.0")
                if 1.0 <= max_loss <= 50.0:
                    config["risk"]["max_daily_loss_pct"] = max_loss
                    break
                else:
                    print("❌ Max loss must be between 1% and 50%")
            except ValueError:
                print("❌ Please enter a number")
        
        while True:
            try:
                max_positions = int(input("Max open positions (10): ") or "10")
                if 1 <= max_positions <= 50:
                    config["risk"]["max_open_positions"] = max_positions
                    break
                else:
                    print("❌ Max positions must be between 1 and 50")
            except ValueError:
                print("❌ Please enter a number")
        
        while True:
            try:
                max_bets = int(input("Max daily bets (15): ") or "15")
                if 1 <= max_bets <= 100:
                    config["risk"]["max_daily_bets"] = max_bets
                    break
                else:
                    print("❌ Max bets must be between 1 and 100")
            except ValueError:
                print("❌ Please enter a number")
        
        return config
    
    def _modify_config(self, config: Dict) -> Dict:
        """Allow modification of existing config."""
        while True:
            print("\nWhat would you like to modify?")
            print("1. Sports")
            print("2. Edge threshold")
            print("3. Position sizing")
            print("4. Risk limits")
            print("5. Done")
            
            choice = input("Select option (5): ").strip()
            
            if choice == "1":
                sports = input(f"Sports ({' '.join(config['sports'])}): ").strip().lower()
                if sports:
                    config["sports"] = sports.split()
            
            elif choice == "2":
                try:
                    edge = float(input(f"Edge threshold ({config['min_edge_pct']}): ") or config['min_edge_pct'])
                    config["min_edge_pct"] = edge
                except ValueError:
                    print("❌ Invalid number")
            
            elif choice == "3":
                try:
                    pct = float(input(f"Position size % ({config['sizing']['flat_pct']}): ") or config['sizing']['flat_pct'])
                    config["sizing"]["flat_pct"] = pct
                except ValueError:
                    print("❌ Invalid number")
            
            elif choice == "4":
                try:
                    loss = float(input(f"Max daily loss % ({config['risk']['max_daily_loss_pct']}): ") or config['risk']['max_daily_loss_pct'])
                    config["risk"]["max_daily_loss_pct"] = loss
                except ValueError:
                    print("❌ Invalid number")
            
            else:
                break
        
        return config
    
    def _print_config(self, config: Dict):
        """Print configuration in readable format."""
        print(f"  Strategy: {config['strategy']}")
        print(f"  Sports: {', '.join(config['sports'])}")
        print(f"  Min Edge: {config['min_edge_pct']}%")
        print(f"  Position Size: {config['sizing']['flat_pct']}% of bankroll")
        print(f"  Max Daily Loss: {config['risk']['max_daily_loss_pct']}%")
        print(f"  Max Positions: {config['risk']['max_open_positions']}")
        print(f"  Max Daily Bets: {config['risk']['max_daily_bets']}")
    
    def save_config(self, config: Dict) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def setup_automation(self):
        """Optionally setup cron job for automation."""
        print("\n⏰ Automation Setup (Optional)")
        print("-" * 30)
        
        setup_cron = input("Setup automated scanning? (y/N): ").strip().lower()
        if setup_cron not in ("y", "yes"):
            return
        
        print("\nAutomation options:")
        print("1. Dry run only (safe - just logs opportunities)")
        print("2. Auto-trade (requires approval)")
        print("3. Full auto (trades automatically)")
        
        while True:
            try:
                choice = int(input("Select option (1): ") or "1")
                if 1 <= choice <= 3:
                    break
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a number")
        
        # Generate cron command
        script_path = os.path.join(os.path.dirname(__file__), "executor.py")
        log_path = os.path.join(self.skill_dir, "logs", "trading.log")
        
        if choice == 1:
            cmd = f"cd {os.path.dirname(script_path)} && python executor.py --dry-run"
        elif choice == 2:
            cmd = f"cd {os.path.dirname(script_path)} && python executor.py --approve"
        else:
            cmd = f"cd {os.path.dirname(script_path)} && python executor.py"
        
        cron_entry = f"*/30 9-23 * * * {cmd} >> {log_path} 2>&1"
        
        print(f"\nAdd this line to your crontab (crontab -e):")
        print(f"{cron_entry}")
        print("\nThis will run every 30 minutes from 9 AM to 11 PM")
        print("Logs will be saved to:", log_path)
        
        auto_add = input("\nAttempt to add to crontab automatically? (y/N): ").strip().lower()
        if auto_add in ("y", "yes"):
            try:
                import subprocess
                result = subprocess.run(
                    ["crontab", "-l"],
                    capture_output=True,
                    text=True
                )
                
                existing_cron = result.stdout if result.returncode == 0 else ""
                
                # Check if entry already exists
                if "kalshi-autopilot" in existing_cron or script_path in existing_cron:
                    print("⚠️  Similar cron entry already exists. Please check manually.")
                else:
                    new_cron = existing_cron + f"\n# Kalshi Autopilot\n{cron_entry}\n"
                    
                    proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
                    proc.communicate(new_cron)
                    
                    if proc.returncode == 0:
                        print("✅ Cron job added successfully")
                    else:
                        print("❌ Failed to add cron job. Please add manually.")
                        
            except Exception as e:
                print(f"❌ Error setting up cron: {e}")
                print("Please add the cron entry manually")
    
    def run_setup(self):
        """Run the complete setup process."""
        self.print_header()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Setup API credentials
        if not self.setup_api_credentials():
            print("❌ Setup failed at credential configuration")
            return False
        
        # Strategy selection
        config = self.select_strategy()
        
        # Save configuration
        if not self.save_config(config):
            print("❌ Setup failed at configuration save")
            return False
        
        # Optional automation setup
        self.setup_automation()
        
        # Success message
        print("\n🎉 Setup Complete!")
        print("=" * 20)
        print("Your Kalshi Autopilot is ready to use!")
        print()
        print("Next steps:")
        print("1. Test scanner: python scanner.py")
        print("2. Check portfolio: python portfolio.py")
        print("3. Dry run trading: python executor.py --dry-run")
        print("4. View configuration: cat ../config/config.json")
        print()
        print("Happy trading! 🚀")
        
        return True

def main():
    """Run setup wizard."""
    wizard = SetupWizard()
    success = wizard.run_setup()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()