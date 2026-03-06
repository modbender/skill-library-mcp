# 🎛️ Mission Control Dashboard

**Professional AI agent management dashboard with department-based hierarchy**

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Start the dashboard
node server.js
# Or with PM2:
pm2 start server.js --name momo-dashboard

# 4. Access dashboard
# Open http://localhost:3000
# Default login: admin / admin123 (change immediately!)
```

## Features

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
- **Rate Limiting:** Prevent brute-force attacks
- **Cloudflare Tunnel:** Optional secure public access

### Beautiful UI
- **Cream/Beige Theme:** Professional Mission Control aesthetic
- **Responsive Design:** Works on desktop, tablet, mobile
- **3-Phase Polish:** Refined spacing, colors, interactions
- **Department Icons:** Visual hierarchy with emoji indicators

## Configuration

### Environment Variables (.env)

```env
# Server
PORT=3000
NODE_ENV=production

# Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
JWT_SECRET=your_secret_key_here

# Optional: Cloudflare Tunnel
TUNNEL_URL=https://your-tunnel.trycloudflare.com
```

### Department Configuration (agents.json)

```json
{
  "departments": {
    "BOT": {
      "name": "Trading Bots",
      "emoji": "🤖",
      "agents": [
        {
          "id": "strategy-researcher",
          "name": "Strategy Researcher",
          "emoji": "🔬",
          "status": "active"
        }
      ]
    }
  }
}
```

## Architecture

```
mission-control-dashboard/
├── server.js           # Main Express server
├── package.json        # Dependencies
├── .env.example        # Environment template
├── public/
│   ├── index.html      # Dashboard UI
│   └── login.html      # Login page
└── agents/
    └── agents.json     # Department/agent config
```

## API Endpoints

### Authentication
- `POST /api/login` - Login with username/password
- `GET /api/validate` - Validate JWT token

### Dashboard Data
- `GET /api/agents` - Get all departments/agents
- `GET /api/system` - Get system stats (CPU, memory, disk, GPU)
- `POST /api/agents/update` - Update agent status/tasks

### Credits Tracking
- `GET /api/credits` - Get usage and cost data
- `POST /api/credits/log` - Log new usage event

## Customization

### Adding New Departments

Edit `agents/agents.json`:

```json
{
  "departments": {
    "YOUR_DEPT": {
      "name": "Your Department Name",
      "emoji": "🎯",
      "description": "What this department does",
      "agents": []
    }
  }
}
```

### Changing Theme Colors

Edit `public/index.html` CSS variables:

```css
:root {
  --bg-primary: #f5f5dc;    /* Cream background */
  --bg-secondary: #fffef9;  /* Light cream */
  --text-primary: #2c3e50;  /* Dark blue-gray */
  --accent: #d4a574;        /* Brown accent */
}
```

### Adding Sub-Agents

Each department can have sub-agents in `agents.json`:

```json
{
  "agents": [
    {
      "id": "sub-agent-id",
      "name": "Sub-Agent Name",
      "emoji": "🔬",
      "status": "active",
      "tasks": [
        { "name": "Task 1", "status": "in-progress" }
      ]
    }
  ]
}
```

## Production Deployment

### With PM2 (Recommended)

```bash
# Install PM2 globally
npm install -g pm2

# Start dashboard
pm2 start server.js --name mission-control

# Enable startup script
pm2 startup
pm2 save

# Monitor logs
pm2 logs mission-control
```

### With Cloudflare Tunnel (Public Access)

```bash
# Install cloudflared
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Start tunnel
cloudflared tunnel --url http://localhost:3000

# Copy the *.trycloudflare.com URL
# Update TUNNEL_URL in .env
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Security Best Practices

1. **Change Default Password:** Immediately update `ADMIN_PASSWORD` in `.env`
2. **Strong JWT Secret:** Use a random 32+ character string for `JWT_SECRET`
3. **HTTPS:** Always use HTTPS in production (Cloudflare Tunnel or Let's Encrypt)
4. **Rate Limiting:** Built-in rate limiting prevents brute-force attacks
5. **Environment Variables:** Never commit `.env` to version control

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 3000
lsof -ti:3000
# Kill it
kill -9 $(lsof -ti:3000)
# Or use a different port in .env
```

### GPU Not Detected
```bash
# Check if nvidia-smi is available
nvidia-smi
# If not found, GPU monitoring will be disabled (CPU/RAM/Disk still work)
```

### Can't Login
```bash
# Reset to default credentials
# Edit .env:
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
# Restart server
pm2 restart mission-control
```

## Support

- **Documentation:** See `docs/` folder for detailed guides
- **Issues:** Check logs with `pm2 logs mission-control`
- **Updates:** Pull latest version and restart server

## License

MIT License - Use freely in personal and commercial projects

---

**Built by Momo 🍑** | For OpenClaw AI agents
