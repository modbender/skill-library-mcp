# OpenClaw Tutorial

Tutorial for installing ros2-skill and controlling ROS 2 robots with OpenClaw.

## What is OpenClaw?

[OpenClaw](https://github.com/openclaw/openclaw) is a personal AI assistant that runs on your own devices. It works across messaging channels like WhatsApp, Telegram, and Slack, and can be extended with Skills.

## Step 1: Install OpenClaw

```bash
npm install -g openclaw@latest

openclaw onboard --install-daemon
```

The setup wizard will guide you through gateway, workspace, channel, and skill configuration.

## Step 2: Install ros2-skill from ClawHub

[ClawHub](https://docs.openclaw.ai/tools/clawhub) is a public skills registry for OpenClaw. Install the CLI and ros2-skill:

```bash
# Install ClawHub CLI
npm install -g clawhub

# Install ros2-skill
clawhub install ros2-skill
```

By default, skills install into `./skills/` in your working directory. Move it to one of OpenClaw's skill directories:

- `~/.openclaw/skills/` — managed skills (available globally)
- `~/.openclaw/workspace/skills/` — workspace skills (highest priority)

You can also search for it first:

```bash
clawhub search "ros2-skill"
```

To update later:

```bash
clawhub update ros2-skill
```


## Step 3: Run on ROS 2 Robot

ros2-skill communicates with ROS 2 robots directly via rclpy. Run the CLI on a machine with ROS 2 installed:

```bash
# Source ROS 2 environment
source /opt/ros/${ROS_DISTRO}/setup.bash

# Install dependencies
pip install rclpy rosidl-runtime-py

# Run commands
python3 ros2_cli.py topics list
python3 ros2_cli.py nodes list
```

## Step 4: Talk to your robot

Control your robot with natural language in the OpenClaw chat.

### Explore

- "What topics are available?"
- "What nodes are running?"
- "What is the message type of /cmd_vel?"

### Move

- "Move the robot forward 1 meter"
- "Rotate the robot 90 degrees to the left"
- "Move in a square pattern"

### Read sensors

- "Read lidar data from the /scan topic"
- "Monitor IMU sensor data for 5 seconds"

### Services

- "Show available services"
- "Reset the turtlesim position"

## Example: Turtlesim with OpenClaw

Try the full workflow with turtlesim.

### 1. Launch turtlesim

```bash
ros2 run turtlesim turtlesim_node
```

### 2. Chat with OpenClaw

Chat with OpenClaw like this:

- "Connect to ROS and show me what topics are available"
- "Move the turtle forward for 2 seconds"
- "What is the turtle's current position?"
- "Draw a square with the turtle"
- "Change the background color to red"

The agent automatically combines ros2-skill commands to execute your requests.


## Architecture

```text
User (Chat) → OpenClaw → ros2-skill → ros2_cli.py → rclpy → ROS 2
```

OpenClaw understands natural language, translates it into ros2-skill CLI commands, and controls the robot through rclpy.
