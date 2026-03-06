import tkinter as tk
from datetime import datetime, timezone, timedelta
import platform
import random

class WOPRClock:
    def __init__(self, root):
        self.root = root
        self.os_type = platform.system()
        self.root.title("W.O.P.R. TERMINAL")
        self.root.geometry("700x450")
        self.root.configure(bg="black")
        
        # Cross-platform Always-on-top
        self.root.attributes("-topmost", True)
        if self.os_type == "Darwin": # MacOS specific boost
            try:
                self.root.tk.call('wm', 'attributes', '.', '-topmost', '1')
            except:
                pass
        
        # WOPR Phosphor Green
        self.phosphor_green = "#33ff33"
        
        # Target Date: March 6th, 2026 at 00:00 (GMT+8)
        self.target_date = datetime(2026, 3, 6, 0, 0, 0, tzinfo=timezone(timedelta(hours=8)))

        # Fonts - Using standard monospaced fonts for that terminal feel
        mono_font = "Courier" if self.os_type == "Windows" else "Menlo"

        # --- UI Elements ---
        
        # Header Info
        self.header = tk.Label(root, text="[ DEFCON 1 ] - STRATEGIC AIR COMMAND", 
                              fg=self.phosphor_green, bg="black", font=(mono_font, 14, "bold"))
        self.header.pack(pady=20)

        # Simulation Data
        self.target_label = tk.Label(root, text="CURRENT SIMULATION: GLOBAL THERMONUCLEAR WAR", 
                                   fg=self.phosphor_green, bg="black", font=(mono_font, 10))
        self.target_label.pack(pady=5)

        # Grid/ASCII Decoration
        self.grid_deco = tk.Label(root, text="+" + "-"*55 + "+", 
                                fg=self.phosphor_green, bg="black", font=(mono_font, 14))
        self.grid_deco.pack()

        # The Big Real-time Countdown
        self.time_var = tk.StringVar(value="00:00:00:00")
        self.display = tk.Label(root, textvariable=self.time_var, 
                              fg=self.phosphor_green, bg="black", font=(mono_font, 55, "bold"))
        self.display.pack(pady=20)

        self.grid_deco2 = tk.Label(root, text="+" + "-"*55 + "+", 
                                 fg=self.phosphor_green, bg="black", font=(mono_font, 14))
        self.grid_deco2.pack()

        # TACO branding at bottom
        self.taco_label = tk.Label(root, text="TACO", 
                                 fg=self.phosphor_green, bg="black", font=(mono_font, 24, "bold"))
        self.taco_label.pack(pady=10)

        # Status Line
        self.status_var = tk.StringVar(value="STATUS: REAL-TIME TRACKING ACTIVE")
        self.status_label = tk.Label(root, textvariable=self.status_var, 
                                   fg=self.phosphor_green, bg="black", font=(mono_font, 10))
        self.status_label.pack(side="bottom", pady=10)

        # Start the logic
        self.update_countdown()
        self.flicker_effect()

    def flicker_effect(self):
        # Subtle CRT flicker
        if random.random() > 0.98:
            self.display.config(fg="#ffffff") 
        else:
            self.display.config(fg=self.phosphor_green)
        self.root.after(100, self.flicker_effect)

    def update_countdown(self):
        # Get current time in UTC
        now = datetime.now(timezone.utc)
        
        # Calculate remaining time
        remaining = self.target_date - now
        
        if remaining.total_seconds() > 0:
            days = remaining.days
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            time_str = f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.time_var.set(time_str)
            
            # Note: Removed winsound.Beep for MacOS compatibility 
            # (MacOS requires different sound libraries)
                
            self.root.after(1000, self.update_countdown)
        else:
            self.time_var.set("00:00:00:00")
            self.status_var.set("SIMULATION COMPLETE. TACO STATUS: FINAL.")
            self.display.config(fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = WOPRClock(root)
    root.mainloop()
