"""
engine_supervisor.py — Engine Daemon
Biomimetic Mind Engine

Runs as a standalone daemon, executing the five-layer pipeline every TICK_INTERVAL_SEC.
Only persists results when an impulse breaches threshold (should_speak=True),
notifying the Node.js observer for proactive conversation.
"""

import time
import os
import json
import signal
import sys
from engine.config import TICK_INTERVAL_SEC, OUTPUT_DIR
from engine.engine_loop import MindEngine

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# MindCore status file (for OpenClaw Agent to read)
STATUS_FILE = os.path.join(os.path.dirname(__file__), "mindcore_status.json")

class Supervisor:
    def __init__(self):
        self.running = True
        self.engine = MindEngine(enable_circadian=True, save_outputs=True)
        self.start_time = time.time()
        self.last_burst_name = None
        self.last_burst_tick = 0
        
        # State decay table: key → expiry seconds
        self.decay_rules = {
            "heart_racing": 7200,        # 2 hours
            "adrenaline_spike": 3600,    # 1 hour
            "post_workout_high": 7200,   # 2 hours
            "muscle_soreness": 172800,   # 48 hours
            "full_stomach": 10800,       # 3 hours
            "caffeine_high": 14400,      # 4 hours
            "just_praised": 7200,        # 2 hours
            "just_criticized": 14400,    # 4 hours
            "sugar_crash": 3600,         # 1 hour
            "jaw_clenched": 3600,        # 1 hour
            "restless_legs": 3600,       # 1 hour
            "joint_stiffness": 7200,     # 2 hours
        }
        self.decay_timestamps = {}  # key → timestamp when set
        self.sensor_file = os.path.join(os.path.dirname(__file__), "data", "Sensor_State.json")
        self._init_decay_tracking()
        
        # Catch Ctrl-C for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def _init_decay_tracking(self):
        """On startup, scan non-zero decayable states and start timing"""
        try:
            with open(self.sensor_file) as f:
                data = json.load(f)
            for cat in ['body', 'environment', 'social']:
                for k, v in data.get(cat, {}).items():
                    if k in self.decay_rules and isinstance(v, (int, float)) and v > 0:
                        self.decay_timestamps[k] = time.time()
        except Exception:
            pass

    def _check_decay(self):
        """Check and clear expired states"""
        now = time.time()
        expired = []
        for k, set_at in self.decay_timestamps.items():
            if now - set_at >= self.decay_rules[k]:
                expired.append(k)
        if not expired:
            return
        try:
            with open(self.sensor_file) as f:
                data = json.load(f)
            for k in expired:
                for cat in ['body', 'environment', 'social']:
                    if k in data.get(cat, {}):
                        data[cat][k] = 0
                        break
                del self.decay_timestamps[k]
                print(f"[Decay] ⏰ {k} expired, auto-zeroed")
            with open(self.sensor_file, 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Decay] Error: {e}")

    def _track_sensor_changes(self):
        """Detect newly-set decayable states and start timing"""
        try:
            with open(self.sensor_file) as f:
                data = json.load(f)
            for cat in ['body', 'environment', 'social']:
                for k, v in data.get(cat, {}).items():
                    if k in self.decay_rules:
                        if isinstance(v, (int, float)) and v > 0 and k not in self.decay_timestamps:
                            self.decay_timestamps[k] = time.time()
                        elif (not isinstance(v, (int, float)) or v == 0) and k in self.decay_timestamps:
                            del self.decay_timestamps[k]
        except Exception:
            pass

    def _write_status(self, total_ticks, result):
        """Write real-time status file for debugging"""
        uptime_sec = time.time() - self.start_time
        
        # Extract richer internal state
        mood_valence = result["layer1"]["mood_valence"]
        membrane = result["layer2"]["membrane"]
        top_simmering = membrane.get("top_simmering_impulses", [])
        
        status = {
            "name": "MindCore",
            "version": "0.1.1",
            "status": "running",
            "tick": total_ticks,
            "uptime_minutes": round(uptime_sec / 60, 1),
            "current_mood_valence": round(mood_valence, 4),
            "total_bursts": self.engine.total_fires,
            "avg_bursts_per_hour": round(self.engine.total_fires / max(uptime_sec / 3600, 0.01), 1),
            "top_simmering_thoughts": top_simmering,
            "last_burst": {
                "name": self.last_burst_name,
                "tick": self.last_burst_tick
            },
            "engine_health": "ok",
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
    def shutdown(self, signum, frame):
        print("\n[Supervisor] Received termination signal, shutting down...")
        self.running = False
        
    def run(self):
        print("=========================================================")
        print("  🧠 MindCore Supervisor (Subconscious Daemon) Started")
        print(f"  Frequency: {TICK_INTERVAL_SEC} sec/Tick")
        print(f"  Monitor: {OUTPUT_DIR} (writes only when impulse breaches threshold)")
        print(f"  Status: {STATUS_FILE}")
        print("=========================================================\n")
        
        # Clean up old output files to avoid contamination
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".json"):
                try:
                    os.remove(os.path.join(OUTPUT_DIR, f))
                except Exception:
                    pass
                    
        total_ticks = 0
        last_speak_tick = -1
        
        while self.running:
            try:
                start_time = time.time()
                
                # Check for config updates from the LLM (Chat-Driven Config)
                config_cmd_file = os.path.join(OUTPUT_DIR, "config_cmd.json")
                if os.path.exists(config_cmd_file):
                    try:
                        with open(config_cmd_file, "r") as f:
                            cmd_data = json.load(f)
                        if "BURST_BASE_OFFSET" in cmd_data:
                            new_offset = float(cmd_data["BURST_BASE_OFFSET"])
                            # 1. Update running memory
                            import engine.config
                            engine.config.BURST_BASE_OFFSET = new_offset
                            print(f"\n[Supervisor] ⚙️  Config updated via LLM command! BURST_BASE_OFFSET = {new_offset}")
                            
                            # 2. Persist to config.py file
                            config_py_path = os.path.join(os.path.dirname(__file__), "engine", "config.py")
                            with open(config_py_path, "r") as f:
                                cfg_lines = f.readlines()
                            with open(config_py_path, "w") as f:
                                for line in cfg_lines:
                                    if line.startswith("BURST_BASE_OFFSET"):
                                        f.write(f"BURST_BASE_OFFSET = {new_offset}\n")
                                    else:
                                        f.write(line)
                    except Exception as e:
                        print(f"[Supervisor] Failed to process config_cmd.json: {e}")
                    finally:
                        try:
                            os.remove(config_cmd_file)
                        except:
                            pass

                # Check for RL reward feedback from the LLM
                reward_cmd_file = os.path.join(OUTPUT_DIR, "reward_cmd.json")
                if os.path.exists(reward_cmd_file):
                    try:
                        with open(reward_cmd_file, "r") as f:
                            reward_data = json.load(f)
                        impulse_name = reward_data.get("impulse_name")
                        signal = float(reward_data.get("signal", 0))
                        if impulse_name and signal != 0:
                            from engine.layer2_impulses import IMPULSE_NAMES
                            if impulse_name in IMPULSE_NAMES:
                                idx = IMPULSE_NAMES.index(impulse_name)
                                self.engine.reward(idx, signal)
                                print(f"\n[Supervisor] 🧠 RL reward: {impulse_name} {'👍' if signal > 0 else '👎'} (lr={self.engine.layer3._get_learning_rate()})")
                            else:
                                print(f"[Supervisor] ⚠️ Unknown impulse: {impulse_name}")
                    except Exception as e:
                        print(f"[Supervisor] Failed to process reward_cmd.json: {e}")
                    finally:
                        try:
                            os.remove(reward_cmd_file)
                        except:
                            pass
                
                # Execute one complete mental tick
                result = self.engine.tick()
                total_ticks += 1

                # Check state decay and changes every 60 ticks
                if total_ticks % 60 == 0:
                    self._track_sensor_changes()
                    self._check_decay()
                
                layer4 = result["layer4"]
                
                # Console: minimal heartbeat + threshold breach events
                if layer4.get("should_speak"):
                    intensity = layer4["intensity_level"]["level_name"].upper()
                    impulse = layer4["impulses"][0]["name"] if layer4["impulses"] else "unknown"
                    print(f"[Tick {total_ticks:05d}] ⚠️  Impulse breached threshold! [{intensity}] {impulse} -> file written.")
                    last_speak_tick = total_ticks
                    self.last_burst_name = impulse
                    self.last_burst_tick = total_ticks
                    self._write_status(total_ticks, result)

                    # Night silence: 00:00-09:00 no push, or manual sleep mode (flag file)
                    from datetime import datetime as _dt
                    _hour = _dt.now().hour
                    _sleep_flag = os.path.join(os.path.dirname(__file__), "data", "sleep_mode.flag")
                    _is_sleeping = os.path.exists(_sleep_flag)
                    if 0 <= _hour < 9 or _is_sleeping:
                        _reason = "Manual sleep mode" if _is_sleeping else f"Night silence ({_hour}:xx)"
                        print(f"[Tick {total_ticks:05d}] 🌙 {_reason}, impulse recorded but not pushed")
                    else:
                        # Notify OpenClaw Agent, inject impulse for proactive speech
                        try:
                            prompt_injection = layer4.get("system_prompt_injection", "")
                            import subprocess
                            # Let agent process impulse and get reply
                            result = subprocess.run(
                                [
                                    "openclaw", "agent",
                                    "--agent", "main",
                                    "--channel", "telegram",
                                    "--deliver",
                                    "--message", f"[System Message] MindCore impulse triggered:\n{prompt_injection}\n\nBased on this impulse, proactively speak to the user in your personality. Do not mention the system message itself.",
                                    "--json",
                                ],
                                capture_output=True, text=True, timeout=120,
                            )
                            output = result.stdout.strip()
                            try:
                                agent_result = json.loads(output)
                                reply = agent_result.get("reply", "").strip()
                            except json.JSONDecodeError:
                                reply = output.split("\n")[-1].strip() if output else ""
                            
                            if reply and reply != "NO_REPLY" and reply != "HEARTBEAT_OK":
                                print(f"[Tick {total_ticks:05d}] 📤 Sent (--deliver): {reply[:50]}...")
                            else:
                                print(f"[Tick {total_ticks:05d}] 🤐 Agent chose silence")
                        except subprocess.TimeoutExpired:
                            print(f"[Tick {total_ticks:05d}] ⏰ Agent timed out")
                        except Exception as e:
                            print(f"[Tick {total_ticks:05d}] ❌ Failed to notify OpenClaw: {e}")
                elif total_ticks % 60 == 0:
                    # Print alive log every 60 ticks
                    membrane_max = result["layer2"]["membrane"].get("max_instant_power", 0.0)
                    mood = result["layer1"]["mood_valence"]
                    print(f"[Tick {total_ticks:05d}] 💤 Subconscious humming... (Mood: {mood:+.2f}, Power: {membrane_max:.2f})")
                    # Write status file every 60 ticks (1 min)
                    self._write_status(total_ticks, result)

                # If not interrupted, sleep until next tick
                elapsed = time.time() - start_time
                sleep_time = max(0.01, TICK_INTERVAL_SEC - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"\n[Supervisor] Critical error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)  # Don't panic on error, sleep 5s then retry
                
        print(f"[Supervisor] Exiting. Total: {total_ticks} cycles.")
        sys.exit(0)

if __name__ == "__main__":
    supervisor = Supervisor()
    supervisor.run()
