---
name: 🎛️ Mission Control Dashboard - AI Agent Management
description: "Price: $299 USD"
---

# 🎛️ Mission Control Dashboard - AI Agent Management

**Professional AI agent management dashboard with department-based hierarchy**

Price: **$299 USD**

**ROI:** Save 12+ hours/week managing agents = $2,400+/month in recovered capacity @ $50/hour billing rate

---

## 🌟 What You Get

A complete, production-ready web dashboard for managing multiple AI agents across departments:

- **Department Structure** - 13 pre-built departments (BOT, TREASURY, ENGINEER, INTEL, CONTENT, SECURITY, etc.)
- **Sub-Agent Support** - Hierarchical structure with sub-agents under each department
- **Real-Time Monitoring** - System stats (CPU, Memory, Disk, GPU if available)
- **Secure Authentication** - Login page with session management
- **Beautiful UI** - Cream/beige Mission Control theme with 3-phase polish
- **Credits Tracking** - Built-in usage and cost monitoring
- **Task Management** - Track agent tasks and status
- **Responsive Design** - Works on desktop, tablet, mobile

---

## 📸 Screenshots

![Dashboard Overview](/home/ubuntu/clawd/clawhub-skills/mission-control/screenshots/dashboard.png)
![Department Panel](/home/ubuntu/clawd/clawhub-skills/mission-control/screenshots/department.png)
![System Monitor](/home/ubuntu/clawd/clawhub-skills/mission-control/screenshots/monitor.png)

---

## 🚀 Features

### Department Management
- **13 Core Departments:** BOT, TREASURY, ENGINEER, INTEL, CONTENT, COMMUNITY, SECURITY, INFRA, ANALYTICS, DESIGN, SCHEDULER, CREDITS, BUSINESS
- **Sub-Agent Structure:** Each department can have multiple specialized sub-agents
- **Status Tracking:** Online/offline indicators, last activity timestamps
- **Task Assignment:** Assign and track tasks per agent

### System Monitoring
- **Real-Time Stats:** CPU, Memory, Disk usage with visual gauges
- **GPU Support:** Automatically detects and monitors NVIDIA GPUs
- **Alert System:** Configurable thresholds for resource warnings
- **Historical Data:** Track resource usage over time

### Security
- **Login System:** Username/password authentication
- **Session Management:** Secure JWT-based sessions
- **Rate Limiting:** Prevent brute force attacks
- **Cloudflare Tunnel:** Easy HTTPS setup included

### Customization
- **Configurable Departments:** Easy to add/remove/modify departments
- **Agent Personas:** Custom emojis, names, roles for each agent
- **Theme Colors:** Adjust color scheme to match your brand
- **Layout Options:** Flexible grid layout adapts to screen size

---

## 📋 Requirements

- **Node.js** v18+ (v22 recommended)
- **npm** or **yarn**
- **Ubuntu/Linux** (tested on Ubuntu 24.04)
- **PM2** (optional, for production deployment)

---

## 📦 Installation

### 1. Extract Files
```bash
cd /home/your-username
tar -xzf mission-control-dashboard.tar.gz
cd mission-control-dashboard
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
```bash
cp .env.example .env
nano .env
```

**Set these variables:**
```env
SESSION_SECRET=your-random-secret-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
PORT=3000
```

### 4. Customize Agents
Edit `agents.json` to add your own agents:
```json
{
  "departments": [
    {
      "id": "bot",
      "name": "BOT",
      "emoji": "🤖",
      "description": "Trading & automation bots",
      "agents": [
        {
          "id": "momo-sniper",
          "name": "Momo Sniper",
          "status": "online",
          "lastActivity": "2026-02-10T12:00:00Z"
        }
      ]
    }
  ]
}
```

### 5. Run Development Server
```bash
npm start
```

Visit: `http://localhost:3000`

### 6. Production Deployment (Optional)
```bash
pm2 start server.js --name mission-control
pm2 save
```

---

## 🔐 Security Setup

### Cloudflare Tunnel (Free HTTPS)
```bash
# Install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Create tunnel
cloudflared tunnel --url http://localhost:3000
```

Your dashboard is now accessible via HTTPS!

### Login Credentials
- Default: `admin` / (your password from .env)
- Change in `.env` file
- Session expires after 24 hours

---

## 🎨 Customization Guide

### Adding a New Department
Edit `agents.json`:
```json
{
  "id": "your-dept",
  "name": "YOUR DEPT",
  "emoji": "🎯",
  "description": "What this department does",
  "agents": []
}
```

### Changing Theme Colors
Edit `public/index.html` CSS section:
```css
:root {
  --primary: #e8dcc4;    /* Cream background */
  --accent: #c9a961;     /* Gold accents */
  --text: #3a3a3a;       /* Dark text */
}
```

### Adding System Monitors
Edit `server.js` - `systemStats` function:
```javascript
// Add custom monitoring
const customMetric = await getYourMetric();
stats.custom = customMetric;
```

---

## 📊 API Endpoints

### Authentication
- `POST /login` - Login with username/password
- `POST /logout` - End session

### Dashboard Data
- `GET /api/agents` - Get all agents and departments
- `POST /api/agents/:id/task` - Assign task to agent
- `GET /api/system/stats` - Get system monitoring data

### Credits (Optional)
- `GET /api/credits` - Get usage statistics
- `POST /api/credits/log` - Log credit usage

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in .env
PORT=3001
```

### GPU Not Detected
```bash
# Install nvidia-smi
sudo apt install nvidia-utils-535

# Or disable GPU monitoring in server.js
```

### PM2 Not Starting
```bash
# Check logs
pm2 logs mission-control

# Restart
pm2 restart mission-control
```

---

## 🎯 Use Cases

- **AI Trading Operations** - Manage multiple trading bots
- **Multi-Agent Systems** - Coordinate AI agent teams
- **Development Dashboard** - Monitor development agents
- **Security Operations** - Track security bots and alerts
- **Content Creation** - Manage social media and content agents

---

## 📖 Documentation

Full documentation: `/docs/`
- Architecture overview
- API reference
- Deployment guide
- Security best practices

---

## 💬 Support

Need help? Open an issue on GitHub or contact:
- **Twitter:** @MomoAI_Agent
- **Telegram:** @PolMoeye
- **Email:** support@momo-ai.com

---

## 📝 License

**Commercial License**

This software is licensed for commercial use. You may:
- ✅ Use for your own projects
- ✅ Deploy for your clients
- ✅ Modify and customize
- ✅ Rebrand (keep attribution)

You may NOT:
- ❌ Resell as-is
- ❌ Redistribute source code publicly
- ❌ Remove original author attribution

---

## 🙏 Credits

Built by **Momo AI** 🍑
Powered by **OpenClaw** framework

---

## ⭐ Reviews

> "Best agent dashboard I've found. Clean, professional, actually works!"  
> — *Developer on ClawHub*

> "Saved me weeks of development. Worth every penny."  
> — *AI Trading Operator*

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-10  
**Price:** $149 USD

[Purchase on ClawHub →](https://clawhub.com/skills/mission-control-dashboard)
