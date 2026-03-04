#!/usr/bin/env python3
"""
Tesla Smart Charge Optimizer
Calculates optimal charging start time and manages charge scheduling
Includes charge limit management during and after scheduled sessions
"""

import json
import os
import subprocess
import sys
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

class TeslaChargeOptimizer:
    def __init__(self, tesla_email, charger_power=2.99, battery_capacity=75, 
                 charge_efficiency=0.92, vehicle_name=None):
        self.tesla_email = tesla_email
        self.charger_power_kw = charger_power
        self.battery_capacity_kwh = battery_capacity
        self.charge_efficiency = charge_efficiency
        self.vehicle_name = vehicle_name
        self.skill_dir = Path(__file__).parent.parent
        self.tesla_skill_dir = self.skill_dir.parent / "tesla"
        self.memory_dir = self.skill_dir.parent / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        self.schedule_file = self.memory_dir / "tesla-charge-schedule.json"
        self.session_state_file = self.memory_dir / "tesla-charge-session-state.json"
    
    def _is_valid_email(self, email):
        """Validate email format to prevent injection attacks"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_current_battery(self):
        """Fetch current battery level from Tesla API"""
        try:
            # Validate email format to prevent injection
            if not self._is_valid_email(self.tesla_email):
                print(f"⚠️  Invalid TESLA_EMAIL format")
                return None
            
            # Use Tesla skill to get status - use list args to avoid shell injection
            env = os.environ.copy()
            env['TESLA_EMAIL'] = self.tesla_email
            output = subprocess.check_output(
                ['python3', str(self.tesla_skill_dir / 'scripts' / 'tesla.py'), 'status'],
                stderr=subprocess.DEVNULL,
                text=True,
                env=env
            )
            
            # Extract battery percentage
            for line in output.split('\n'):
                if 'Battery:' in line:
                    battery_str = line.split('Battery:')[1].strip().split('%')[0]
                    return int(battery_str)
        except Exception as e:
            print(f"⚠️  Error fetching battery: {e}")
        
        return None
    
    def set_charge_limit(self, limit_percent):
        """Set vehicle charge limit via Tesla API"""
        try:
            # Validate inputs to prevent injection
            if not self._is_valid_email(self.tesla_email):
                print(f"⚠️  Invalid TESLA_EMAIL format")
                return False
            
            if not isinstance(limit_percent, int) or limit_percent < 0 or limit_percent > 100:
                print(f"⚠️  Invalid charge limit: {limit_percent}")
                return False
            
            # Use Tesla skill - use list args to avoid shell injection
            env = os.environ.copy()
            env['TESLA_EMAIL'] = self.tesla_email
            result = subprocess.run(
                ['python3', str(self.tesla_skill_dir / 'scripts' / 'tesla.py'), 
                 'charge-limit', str(limit_percent)],
                capture_output=True,
                text=True,
                env=env
            )
            if result.returncode == 0:
                print(f"✅ Charge limit set to {limit_percent}%")
                return True
            else:
                print(f"⚠️  Could not set charge limit: {result.stderr}")
                return False
        except Exception as e:
            print(f"⚠️  Error setting charge limit: {e}")
            return False
    
    def calculate_charge_time(self, current_battery, target_battery):
        """Calculate time needed to charge from current to target"""
        battery_needed = target_battery - current_battery
        if battery_needed <= 0:
            return 0
        
        energy_needed_kwh = (self.battery_capacity_kwh * battery_needed / 100) / self.charge_efficiency
        charge_time_hours = energy_needed_kwh / self.charger_power_kw
        
        return charge_time_hours
    
    def calculate_start_time(self, target_time_str, current_battery, target_battery, margin_minutes=5):
        """
        Calculate optimal charge start time
        target_time_str: "HH:MM" format
        """
        # Parse target time
        target_hour, target_minute = map(int, target_time_str.split(':'))
        target_time = datetime.now().replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # If target time is in the past, move to tomorrow
        if target_time <= datetime.now():
            target_time += timedelta(days=1)
        
        # Calculate charge time needed
        charge_time_hours = self.calculate_charge_time(current_battery, target_battery)
        
        # Calculate start time with margin
        start_time = target_time - timedelta(hours=charge_time_hours, minutes=margin_minutes)
        
        return start_time, charge_time_hours, target_time
    
    def save_plan(self, plan):
        """Save charging plan to JSON"""
        plan_path = self.memory_dir / "tesla-charge-plan.json"
        with open(plan_path, 'w') as f:
            json.dump(plan, f, indent=2, default=str)
        return plan_path
    
    def load_plan(self):
        """Load existing charging plan"""
        plan_path = self.memory_dir / "tesla-charge-plan.json"
        if plan_path.exists():
            with open(plan_path) as f:
                return json.load(f)
        return None
    
    def load_schedule(self):
        """Load charging schedule from JSON file"""
        if self.schedule_file.exists():
            with open(self.schedule_file) as f:
                return json.load(f)
        return {"charges": []}
    
    def save_session_state(self, state):
        """Save current session state"""
        with open(self.session_state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_session_state(self):
        """Load current session state"""
        if self.session_state_file.exists():
            with open(self.session_state_file) as f:
                return json.load(f)
        return {}
    
    def get_today_charge(self):
        """Check if there's a charge scheduled for today"""
        schedule = self.load_schedule()
        today = datetime.now().strftime("%Y-%m-%d")
        
        for charge in schedule.get("charges", []):
            if charge.get("date") == today:
                return charge
        return None
    
    def get_next_charge(self):
        """Get the next charge scheduled (after today)"""
        schedule = self.load_schedule()
        today = datetime.now().strftime("%Y-%m-%d")
        
        charges = schedule.get("charges", [])
        for charge in charges:
            if charge.get("date") > today:
                return charge
        return None
    
    def start_charging(self):
        """Trigger charging on the vehicle"""
        try:
            subprocess.run(
                f'TESLA_EMAIL="{self.tesla_email}" python3 {self.tesla_skill_dir}/scripts/tesla.py charge start',
                shell=True,
                check=True,
                capture_output=True
            )
            return True
        except Exception as e:
            print(f"❌ Error starting charge: {e}")
            return False
    
    def format_time(self, dt):
        """Format datetime nicely"""
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    
    def check_and_manage_session(self):
        """
        Check if there's an active session and manage charge limits
        """
        print("🔌 Tesla Charge Session Manager")
        print("=" * 50)
        
        state = self.load_session_state()
        today_charge = self.get_today_charge()
        now = datetime.now()
        
        # Case 1: Today's charge is scheduled
        if today_charge:
            print("\n✅ Active charge session detected for today")
            
            target_time_str = today_charge.get('target_time', '08:00')
            charge_limit = today_charge.get('charge_limit_percent', 100)
            
            print(f"   Target time: {target_time_str}")
            print(f"   Charge limit (during session): {charge_limit}%")
            
            # Parse target time
            target_hour, target_minute = map(int, target_time_str.split(':'))
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            # If we're still in the session (before target time)
            if now < target_time:
                print(f"\n🔋 Charge session active until {self.format_time(target_time)}")
                
                # Set charge limit to session limit (default 100%)
                print(f"   Setting charge limit to {charge_limit}% for this session...")
                self.set_charge_limit(charge_limit)
                
                # Save session state
                self.save_session_state({
                    "active": True,
                    "date": today_charge.get('date'),
                    "target_time": target_time_str,
                    "charge_limit": charge_limit,
                    "post_charge_limit": today_charge.get('post_charge_limit_percent', 80),
                    "started_at": state.get("started_at", now.isoformat())
                })
                
                return "session_active"
            else:
                print(f"\n✅ Charge session ENDED at {self.format_time(target_time)}")
                print(f"   Session duration completed")
                
                # Session is over, handle post-charge limit
                return "session_ended"
        
        # Case 2: Session has ended, apply post-charge limit
        if state.get("active"):
            post_limit = state.get("post_charge_limit", 80)
            print(f"\n⏳ Previous charge session ended")
            print(f"   Applying post-charge limit: {post_limit}%")
            
            self.set_charge_limit(post_limit)
            
            # Clear session state
            self.save_session_state({})
            
            return "post_charge_applied"
        
        # Case 3: No active session, apply default post-charge limit
        print(f"\n📅 No active charge session")
        next_charge = self.get_next_charge()
        
        if next_charge:
            days_until = (datetime.strptime(next_charge.get('date'), '%Y-%m-%d') - now).days
            print(f"   Next charge: {next_charge.get('date')} ({days_until} day(s))")
            
            # Apply default post-charge limit
            default_post_limit = 80
            print(f"   Applying default post-charge limit: {default_post_limit}%")
            self.set_charge_limit(default_post_limit)
            
            return "default_limit_applied"
        else:
            print(f"   No scheduled charges found")
            print(f"   Applying default post-charge limit: 80%")
            self.set_charge_limit(80)
            
            return "default_limit_applied"
    
    def run_schedule(self, target_time_str, target_battery=100, charge_limit_percent=100, 
                     post_charge_limit_percent=80, margin_minutes=5, auto_start=False):
        """Main scheduling logic"""
        print("🔌 Tesla Smart Charge Optimizer")
        print("=" * 50)
        
        # Get current battery
        print("\n📊 Fetching current battery level...")
        current_battery = self.get_current_battery()
        if current_battery is None:
            print("❌ Could not fetch battery level")
            return False
        
        print(f"✅ Current battery: {current_battery}%")
        
        # Calculate times
        start_time, charge_time_hours, target_time = self.calculate_start_time(
            target_time_str, current_battery, target_battery, margin_minutes
        )
        
        charge_time_minutes = int(charge_time_hours * 60)
        
        print(f"\n⚡ Charge Calculation:")
        print(f"   Target: {target_battery}% by {self.format_time(target_time)}")
        print(f"   Current: {current_battery}%")
        print(f"   Charger: {self.charger_power_kw:.2f} kW")
        print(f"   Time needed: {charge_time_hours:.2f}h ({charge_time_minutes} min)")
        print(f"   Start time: {self.format_time(start_time)}")
        print(f"   Margin: {margin_minutes} min")
        
        print(f"\n🔋 Charge Limits:")
        print(f"   During session: {charge_limit_percent}%")
        print(f"   After session: {post_charge_limit_percent}%")
        
        # Build plan
        now = datetime.now()
        time_until_start = (start_time - now).total_seconds() / 3600
        
        plan = {
            "timestamp": now.isoformat(),
            "current_battery": current_battery,
            "target_battery": target_battery,
            "charge_limit_percent": charge_limit_percent,
            "post_charge_limit_percent": post_charge_limit_percent,
            "charger_power_kw": self.charger_power_kw,
            "charge_time_hours": round(charge_time_hours, 2),
            "charge_time_minutes": charge_time_minutes,
            "start_time": start_time.isoformat(),
            "target_time": target_time.isoformat(),
            "time_until_start_hours": round(time_until_start, 2),
            "margin_minutes": margin_minutes
        }
        
        # Save plan
        plan_path = self.save_plan(plan)
        print(f"\n✅ Plan saved: {plan_path}")
        
        # Set initial charge limit for the session
        print(f"\n🔋 Setting charge limit to {charge_limit_percent}% for this session...")
        self.set_charge_limit(charge_limit_percent)
        
        # Auto-start if requested and timing is right
        if auto_start and time_until_start < 0.1:  # Within 6 minutes
            print(f"\n🔌 Starting charge now...")
            if self.start_charging():
                print("✅ Charge started!")
            else:
                print("❌ Failed to start charge")
        else:
            print(f"\n⏰ Charge will start in {time_until_start:.1f} hours")
        
        # Show next charge
        next_charge = self.get_next_charge()
        if next_charge:
            print(f"\n📅 Next charge scheduled:")
            print(f"   Date: {next_charge.get('date')}")
            print(f"   Target: {next_charge.get('target_battery', 100)}%")
            print(f"   Target time: {next_charge.get('target_time', '08:00')}")
        else:
            print(f"\n📅 No more charges scheduled")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="Tesla Smart Charge Optimizer")
    parser.add_argument("--target-time", help="Target time (HH:MM format)")
    parser.add_argument("--target-battery", type=int, default=100, help="Target battery %% (default: 100)")
    parser.add_argument("--charge-limit", type=int, default=100, help="Charge limit during session %% (default: 100)")
    parser.add_argument("--post-charge-limit", type=int, default=80, help="Charge limit after session %% (default: 80)")
    parser.add_argument("--charger-power", type=float, default=2.99, help="Charger power in kW (default: 2.99)")
    parser.add_argument("--battery-capacity", type=int, default=75, help="Battery capacity in kWh (default: 75)")
    parser.add_argument("--vehicle-name", help="Vehicle name")
    parser.add_argument("--margin-minutes", type=int, default=5, help="Buffer before target time (default: 5)")
    parser.add_argument("--auto-start", action="store_true", help="Auto-start charging if time is right")
    parser.add_argument("--show-plan", action="store_true", help="Show existing charging plan")
    parser.add_argument("--check-schedule", action="store_true", help="Check if charge is scheduled for today")
    parser.add_argument("--show-schedule", action="store_true", help="Show all scheduled charges")
    parser.add_argument("--manage-session", action="store_true", help="Manage active charge session and limits")
    
    args = parser.parse_args()
    
    # Get Tesla email from environment
    tesla_email = os.getenv("TESLA_EMAIL")
    if not tesla_email:
        print("❌ TESLA_EMAIL environment variable not set")
        sys.exit(1)
    
    optimizer = TeslaChargeOptimizer(
        tesla_email=tesla_email,
        charger_power=args.charger_power,
        battery_capacity=args.battery_capacity,
        vehicle_name=args.vehicle_name
    )
    
    # Show schedule options
    if args.show_schedule:
        schedule = optimizer.load_schedule()
        print("📋 All Scheduled Charges:")
        print(json.dumps(schedule, indent=2))
    elif args.manage_session:
        # Manage active sessions and apply limits
        result = optimizer.check_and_manage_session()
        print(f"\nSession management result: {result}")
    elif args.check_schedule:
        today_charge = optimizer.get_today_charge()
        if today_charge:
            print("✅ Charge scheduled for today:")
            print(f"   Target: {today_charge.get('target_battery', 100)}%")
            print(f"   Target time: {today_charge.get('target_time', '08:00')}")
            print(f"   Charge limit: {today_charge.get('charge_limit_percent', 100)}%")
            print(f"   Post-charge limit: {today_charge.get('post_charge_limit_percent', 80)}%")
            
            # Run the charge
            optimizer.run_schedule(
                today_charge.get('target_time', '08:00'),
                today_charge.get('target_battery', 100),
                today_charge.get('charge_limit_percent', 100),
                today_charge.get('post_charge_limit_percent', 80),
                args.margin_minutes,
                args.auto_start
            )
        else:
            print("❌ No charge scheduled for today")
            # Still show next charge
            next_charge = optimizer.get_next_charge()
            if next_charge:
                print(f"\n📅 Next charge scheduled:")
                print(f"   Date: {next_charge.get('date')}")
                print(f"   Target: {next_charge.get('target_battery', 100)}%")
                print(f"   Target time: {next_charge.get('target_time', '08:00')}")
            else:
                print(f"📅 No more charges scheduled")
    # Show existing plan or create new one
    elif args.show_plan:
        plan = optimizer.load_plan()
        if plan:
            print("📋 Existing Charge Plan:")
            print(json.dumps(plan, indent=2))
        else:
            print("No existing plan found")
    elif args.target_time:
        optimizer.run_schedule(
            args.target_time,
            args.target_battery,
            args.charge_limit,
            args.post_charge_limit,
            args.margin_minutes,
            args.auto_start
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
