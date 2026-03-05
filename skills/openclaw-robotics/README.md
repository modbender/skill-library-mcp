<p align="center">
  <a href="https://github.com/LooperRobotics/OpenClaw-Robotics">
    <img src="https://img.shields.io/github/stars/LooperRobotics/OpenClaw-Robotics?style=social" alt="Stars">
  </a>
  <a href="https://github.com/LooperRobotics/OpenClaw-Robotics/fork">
    <img src="https://img.shields.io/github/forks/LooperRobotics/OpenClaw-Robotics?style=social" alt="Forks">
  </a>
  <img src="https://img.shields.io/github/license/LooperRobotics/OpenClaw-Robotics?style=social" alt="License">
  <img src="https://img.shields.io/pypi/v/openclaw-robotics?style=social" alt="PyPI">
</p>

<!-- SEO Meta Tags -->
<meta name="description" content="OpenClaw Robotics Skill - Control robots via instant messaging. Supports all robot types: quadrupeds, bipedals, wheeled, drones. Connect AI to the physical world.">
<meta name="keywords" content="robotics, robot control, instant messaging, openclaw, embodied AI, quadruped robot, bipedal robot, humanoid robot, wheeled robot, drone, computer vision, visual SLAM, navigation, python, ROS">

<meta property="og:title" content="OpenClaw Robotics - Connect AI to the Physical World">
<meta property="og:description" content="Control robots via messaging apps. The most easy-to-use OpenClaw skill for connecting AI to physical robots.">
<meta property="og:url" content="https://github.com/LooperRobotics/OpenClaw-Robotics">
<meta property="og:type" content="project">

<h1 align="center">🤖 OpenClaw Robotics Skill</h1>

---

## Our Vision

**We believe robots should be as easy to control as sending a text message.**

This skill bridges the gap between AI (OpenClaw) and the physical world. Whether you're a researcher, educator, hobbyist, or enterprise - you can now control robots through platforms you already use every day.

```
You (WhatsApp/WeChat/DingTalk) 
        │
        ▼
   ┌──────────┐
   │ OpenClaw │ ← AI Brain
   └────┬─────┘
        │
        ▼
   ┌──────────┐
   │  Robot   │ ← Physical World
   └──────────┘
```

---

## 🎯 What We Do

| Goal | How We Achieve It |
|------|-------------------|
| **Universal Control** | One skill controls ANY robot type |
| **Zero Learning Curve** | Use natural language, no coding required |
| **Instant Deployment** | Install via ClawHub in one command |
| **Future-Proof** | Plugin architecture for new robots |

---

## ✅ What's Working Now

### Supported Robot Types

| Type | Robots | Use Case |
|------|--------|----------|
| **Quadruped** | Unitree GO1, GO2 | Inspection, exploration |
| **Bipedal/Humanoid** | Unitree G1, H1 | Service, manipulation |

### Supported IM Platforms

| Platform | Code | Region |
|----------|------|--------|
| WeCom | `wecom` | China |
| Feishu | `feishu` | China |
| DingTalk | `dingtalk` | China |
| WhatsApp | `whatsapp` | Global |

### Commands Work Right Now

```
forward 1m        → Robot walks forward 1 meter
turn left 45      → Robot turns left 45 degrees
stand             → Robot stands up
sit               → Robot sits down
wave              → Robot waves hand
go to 5,3         → Robot navigates to position
```

---

## 🔜 What's Coming

We're building the most comprehensive robot control skill:

| Feature | Status | Description |
|---------|--------|-------------|
| **Insight9 Camera** | 🔜 | Looper AI Stereo Camera for VSLAM |
| **TinyNav** | 🔜 | Open-source navigation library |
| **Wheeled Robots** | 🔜 | Indoor/outdoor platforms |
| **Aerial Robots** | 🔜 | Drones and UAVs |
| **Surface Vehicles** | 🔜 | Boats, rovers |
| **Multi-Robot** | 🔜 | Coordinate multiple robots |

---

## 🚀 Quick Start

### Install (One Command)

```bash
npx skills add LooperRobotics/OpenClaw-Robotics
```

### Or Manual Install

```bash
git clone https://github.com/LooperRobotics/OpenClaw-Robotics.git
cp -r OpenClaw-Robotics ~/.openclaw/skills/unitree-robot
```

### Use It

```python
from unitree_robot_skill import initialize, execute

# Connect robot to your messaging app
initialize(
    robot="unitree_go2",
    robot_ip="192.168.12.1",
    im="wecom"
)

# That's it! Now control via WhatsApp/WeChat/etc.

execute("forward 1m")
execute("turn left 90")
execute("wave")

# Check status anytime
status = get_status()
print(status)
# {'robot': 'Unitree GO2', 'battery': '85%', 'temperature': '35°C'}
```

---

## 📖 Command Reference

### Movement

| Command | Example | Description |
|---------|---------|-------------|
| `forward Xm` | `forward 2m` | Move forward X meters |
| `backward Xm` | `backward 0.5m` | Move backward X meters |
| `turn left X` | `turn left 45` | Turn left X degrees |
| `turn right X` | `turn right 90` | Turn right X degrees |

### Posture

| Command | Description |
|---------|-------------|
| `stand` | Stand up |
| `sit` | Sit down |
| `lie down` | Lie down |

### Actions

| Command | Description |
|---------|-------------|
| `wave` | Wave hand |
| `handshake` | Offer handshake |
| `dance` | Dance |

### Info

| Command | Description |
|---------|-------------|
| `status` | Get robot status |
| `battery` | Get battery level |
| `position` | Get current position |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 IM Platforms                        │
│   WhatsApp  │  WeCom  │  Feishu  │  DingTalk    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              Natural Language Parser                │
│    "forward 1m then turn left" → [actions]        │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐
│  Quadruped  │ │ Bipedal  │ │ Wheeled  │
│   (GO1/2)   │ │  (G1/H1) │ │  (future)│
└─────────────┘ └──────────┘ └──────────┘
         │            │            │
         └────────────┼────────────┘
                      ▼
              ┌─────────────┐
              │   Robots   │
              └─────────────┘
```

---

## 🔧 Add Your Own Robot

We designed this to be extensible. Adding a new robot takes minutes:

```python
from robot_adapters.base import RobotAdapter, RobotType

class MyRobotAdapter(RobotAdapter):
    ROBOT_CODE = "mydrobot_x1"
    ROBOT_NAME = "My Robot X1"
    BRAND = "MyBrand"
    ROBOT_TYPE = RobotType.QUADRUPED
    
    def connect(self) -> bool:
        # Your SDK connection code
        return True
    
    def move(self, x: float, y: float, yaw: float):
        # Your movement code
        return TaskResult(True, "Moved")
    
    # ... implement other methods

# Register it
from robot_adapters.factory import RobotFactory
RobotFactory.register("mydrobot_x1")(MyRobotAdapter)
```

That's it! Now control it via:
```
execute("mydrobot_x1", "forward 1m")
```

---

## 📊 Roadmap

```
2026 Q1 ───────────────────────────────────▶
│
├─ Insight9 Camera Support
│  └─ VSLAM with RGB-Depth
│
├─ Basic Navigation  
│  └─ Point-to-point path planning
│
└─ Wheeled Robot Framework
   └─ First wheeled adapter

2026 Q2 ───────────────────────────────────▶
│
├─ TinyNav Integration
│  └─ A* + DWA obstacle avoidance
│
├─ Multi-Robot Coordination
│  └─ Fleet management
│
└─ Aerial Robot Framework
   └─ Drone adapter

2026 Q3+ ──────────────────────────────────▶
│
├─ Surface Vehicles
├─ Advanced SLAM
└─ Your suggestions!
```

---

## 🤝 Want to Contribute?

We welcome contributors! Here's how:

1. **Star us** ⭐ - Helps discoverability
2. **Fork** - Make your own version  
3. **PR** - Submit improvements
4. **Issue** - Report bugs or request features
5. **Share** - Tell others about us!

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📚 Resources

- [Documentation](docs/) - Detailed guides
- [Examples](examples/) - Usage examples
- [ROADMAP.md](docs/ROADMAP.md) - Long-term plans

---

## 📝 Citation

```bibtex
@software{OpenClaw-Robotics,
  author = {LooperRobotics},
  title = {OpenClaw Robotics Skill - Control Robots via Messaging},
  year = {2025},
  url = {https://github.com/LooperRobotics/OpenClaw-Robotics},
  license = {MIT}
}
```

---

## ⭐ Let's Connect

- **GitHub**: https://github.com/LooperRobotics
- **Website**: https://www.looper-robotics.com
- **Email**: qinrui.yan@looper-robotics.com

---

<p align="center">
  <strong>Built with ❤️ by <a href="https://github.com/LooperRobotics">LooperRobotics</a></strong><br>
  <sub>Making robots accessible to everyone, one message at a time.</sub>
</p>
