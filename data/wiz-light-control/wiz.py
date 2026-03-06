import sys
import argparse
import asyncio
import time

# Try to import pywizlight
try:
    from pywizlight import wizlight, PilotBuilder
except ImportError:
    print("\n❌ CRITICAL ERROR: 'pywizlight' is not installed.")
    print("👉 Please install dependencies defined in requirements.txt")
    sys.exit(1)

# 🔥 Workaround for pywizlight + Python 3.12 shutdown bug
if hasattr(wizlight, "__del__"):
    wizlight.__del__ = lambda self: None

async def control_wiz(ip: str, action: str, red: int = 0, green: int = 0, blue: int = 0, duration: int = 0):
    print(f"\n🔌 Connecting to Wiz Bulb at {ip}...")
    
    try:
        light = wizlight(ip)
        
        if action == "on":
            print("💡 Turning light ON...")
            await light.turn_on(PilotBuilder(brightness=255))
        
        elif action == "off":
            print("🌑 Turning light OFF...")
            await light.turn_off()
        
        elif action == "color":
            print(f"🎨 Setting color to RGB({red}, {green}, {blue})...")
            await light.turn_on(PilotBuilder(rgb=(red, green, blue), brightness=255))
        
        elif action == "disco":
            print(f"🕺 STARTING DISCO MODE! (Duration: {duration}s)")
            colors = [
                (255, 0, 0),    # Red
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (255, 255, 0),  # Yellow
                (0, 255, 255),  # Cyan
                (255, 0, 255)   # Magenta
            ]
            
            start_time = time.time()
            i = 0
            while True:
                # Check duration
                if duration > 0 and (time.time() - start_time) > duration:
                    print(f"🛑 Disco mode finished after {duration} seconds.")
                    break
                
                # Cycle through colors
                current_color = colors[i % len(colors)]
                await light.turn_on(PilotBuilder(rgb=current_color, brightness=255))
                
                # Wait before next color (0.8s beat)
                await asyncio.sleep(0.8) 
                i += 1

        print("✅ Command executed successfully!")

    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print(f"⚠️  TROUBLESHOOTING:")
        print(f"1. Is the IP '{ip}' correct? (Check your router)")
        print(f"2. Is the light switch turned ON?")
        print(f"3. Are you on the same WiFi network?")

def main():
    parser = argparse.ArgumentParser(description="Control Wiz Smart Light via CLI")
    
    parser.add_argument("--ip", type=str, required=True, help="IP address of the bulb")
    parser.add_argument("--action", type=str, choices=["on", "off", "color", "disco"], required=True, help="Action to perform")
    
    # Optional arguments
    parser.add_argument("--r", type=int, default=0, help="Red (0-255)")
    parser.add_argument("--g", type=int, default=0, help="Green (0-255)")
    parser.add_argument("--b", type=int, default=0, help="Blue (0-255)")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds for disco mode")

    args = parser.parse_args()

    try:
        asyncio.run(control_wiz(args.ip, args.action, args.r, args.g, args.b, args.duration))
    except KeyboardInterrupt:
        print("\n👋 Process interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()