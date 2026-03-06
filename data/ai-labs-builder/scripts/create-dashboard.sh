#!/bin/bash
# Crea dashboard con widget system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$SKILL_DIR/templates/dashboard"
ASSETS_DIR="$SKILL_DIR/assets"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
PROJECT_NAME=""
TYPE="analytics"

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ailabs create dashboard <name> --type <analytics|admin|personal>"
            exit 0
            ;;
        *)
            if [[ -z "$PROJECT_NAME" ]]; then
                PROJECT_NAME="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$PROJECT_NAME" ]]; then
    log_error "Nome progetto richiesto"
    exit 1
fi

if [[ ! "$TYPE" =~ ^(analytics|admin|personal)$ ]]; then
    log_error "Tipo non valido. Usa: analytics, admin, personal"
    exit 1
fi

log_info "Creazione Dashboard: $PROJECT_NAME (tipo: $TYPE)"

# Crea directory progetto
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Inizializza progetto Next.js
log_info "Inizializzazione Next.js 15..."
echo "my-app" | npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes 2>/dev/null || true

# Installa dipendenze
log_info "Installazione dipendenze..."
npm install recharts framer-motion lucide-react date-fns
npm install next-themes

# Installa shadcn/ui
log_info "Setup shadcn/ui..."
npx shadcn@latest init -y -d
npx shadcn@latest add button card input tabs badge avatar dropdown-menu -y

# Crea struttura
cat > app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 224.3 76.3% 48%;
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* Widget Styles */
.widget {
  @apply bg-card rounded-xl border p-6 shadow-sm transition-all duration-200;
}

.widget:hover {
  @apply shadow-md -translate-y-1;
}

.widget-wide {
  @apply col-span-2;
}

.widget-header {
  @apply flex items-center justify-between mb-4;
}

.widget-title {
  @apply text-lg font-semibold flex items-center gap-2;
}

.widget-content {
  @apply space-y-4;
}

/* Dashboard Grid */
.dashboard-grid {
  @apply grid gap-6;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .dashboard-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
EOF

# Crea theme provider
cat > components/theme-provider.tsx << 'EOF'
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
EOF

# Crea widget components
cat > components/widgets/stats-widget.tsx << 'EOF'
'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface StatsWidgetProps {
  title: string
  value: string | number
  change?: number
  description?: string
  icon?: React.ReactNode
}

export function StatsWidget({ title, value, change, description, icon }: StatsWidgetProps) {
  const getTrendIcon = () => {
    if (!change) return <Minus className="w-4 h-4" />
    if (change > 0) return <TrendingUp className="w-4 h-4 text-green-500" />
    return <TrendingDown className="w-4 h-4 text-red-500" />
  }

  return (
    <Card className="widget">
      <CardHeader className="widget-header">
        <CardTitle className="widget-title text-sm font-medium">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          {title}
        </CardTitle>
        {change !== undefined && (
          <div className="flex items-center gap-1 text-sm">
            {getTrendIcon()}
            <span className={change >= 0 ? 'text-green-500' : 'text-red-500'}>
              {Math.abs(change)}%
            </span>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}
EOF

cat > components/widgets/chart-widget.tsx << 'EOF'
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface ChartWidgetProps {
  title: string
  data: any[]
  type?: 'line' | 'area' | 'bar'
  dataKey: string
  xAxisKey?: string
  color?: string
}

export function ChartWidget({
  title,
  data,
  type = 'line',
  dataKey,
  xAxisKey = 'name',
  color = '#3b82f6',
}: ChartWidgetProps) {
  const renderChart = () => {
    switch (type) {
      case 'area':
        return (
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey={xAxisKey} className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              fillOpacity={1}
              fill={`url(#gradient-${dataKey})`}
            />
          </AreaChart>
        )
      case 'bar':
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey={xAxisKey} className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip />
            <Bar dataKey={dataKey} fill={color} />
          </BarChart>
        )
      default:
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey={xAxisKey} className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        )
    }
  }

  return (
    <Card className="widget widget-wide">
      <CardHeader>
        <CardTitle className="widget-title">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          {renderChart()}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
EOF

cat > components/widgets/activity-widget.tsx << 'EOF'
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { formatDistanceToNow } from 'date-fns'

interface Activity {
  id: string
  user: string
  action: string
  target?: string
  timestamp: Date
}

interface ActivityWidgetProps {
  title?: string
  activities: Activity[]
}

export function ActivityWidget({ title = 'Recent Activity', activities }: ActivityWidgetProps) {
  return (
    <Card className="widget">
      <CardHeader>
        <CardTitle className="widget-title">{title}</CardTitle>
      </CardHeader>
      <CardContent className="widget-content">
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3">
              <Avatar className="w-8 h-8">
                <AvatarFallback className="text-xs">
                  {activity.user.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm">
                  <span className="font-medium">{activity.user}</span>{' '}
                  {activity.action}
                  {activity.target && (
                    <span className="text-muted-foreground"> {activity.target}</span>
                  )}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
EOF

cat > components/widgets/list-widget.tsx << 'EOF'
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface ListItem {
  id: string
  title: string
  subtitle?: string
  status?: 'active' | 'pending' | 'completed' | 'error'
  value?: string | number
}

interface ListWidgetProps {
  title: string
  items: ListItem[]
}

const statusColors = {
  active: 'bg-green-500',
  pending: 'bg-yellow-500',
  completed: 'bg-blue-500',
  error: 'bg-red-500',
}

export function ListWidget({ title, items }: ListWidgetProps) {
  return (
    <Card className="widget">
      <CardHeader>
        <CardTitle className="widget-title">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <div className="flex items-center gap-3">
                {item.status && (
                  <div className={`w-2 h-2 rounded-full ${statusColors[item.status]}`} />
                )}
                <div>
                  <p className="font-medium text-sm">{item.title}</p>
                  {item.subtitle && (
                    <p className="text-xs text-muted-foreground">{item.subtitle}</p>
                  )}
                </div>
              </div>
              {item.value && (
                <Badge variant="secondary">{item.value}</Badge>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
EOF

# Crea dashboard layout
cat > app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Analytics Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
EOF

# Crea pagina dashboard
cat > app/page.tsx << 'EOF'
'use client'

import { useState, useEffect } from 'react'
import { BarChart3, Users, DollarSign, Activity, Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import { StatsWidget } from '@/components/widgets/stats-widget'
import { ChartWidget } from '@/components/widgets/chart-widget'
import { ActivityWidget } from '@/components/widgets/activity-widget'
import { ListWidget } from '@/components/widgets/list-widget'

// Sample data
const chartData = [
  { name: 'Mon', value: 400 },
  { name: 'Tue', value: 300 },
  { name: 'Wed', value: 600 },
  { name: 'Thu', value: 800 },
  { name: 'Fri', value: 500 },
  { name: 'Sat', value: 900 },
  { name: 'Sun', value: 700 },
]

const activities = [
  {
    id: '1',
    user: 'John Doe',
    action: 'created a new project',
    target: 'Website Redesign',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: '2',
    user: 'Jane Smith',
    action: 'completed task',
    target: 'Update Documentation',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: '3',
    user: 'Mike Johnson',
    action: 'commented on',
    target: 'Q4 Planning',
    timestamp: new Date(Date.now() - 1000 * 60 * 60),
  },
]

const projects = [
  { id: '1', title: 'Website Redesign', subtitle: 'Design Team', status: 'active' as const, value: '75%' },
  { id: '2', title: 'Mobile App', subtitle: 'Development', status: 'pending' as const, value: '30%' },
  { id: '3', title: 'API Integration', subtitle: 'Backend', status: 'completed' as const, value: '100%' },
  { id: '4', title: 'Database Migration', subtitle: 'DevOps', status: 'error' as const, value: 'Failed' },
]

function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  if (!mounted) return null

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
    </Button>
  )
}

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-primary" />
              <h1 className="text-xl font-bold">Analytics Dashboard</h1>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Row */}
        <div className="dashboard-grid mb-8">
          <StatsWidget
            title="Total Revenue"
            value="$45,231"
            change={12.5}
            description="+20.1% from last month"
            icon={<DollarSign className="w-4 h-4" />}
          />
          <StatsWidget
            title="Active Users"
            value="2,345"
            change={8.2}
            description="+180 new users this week"
            icon={<Users className="w-4 h-4" />}
          />
          <StatsWidget
            title="Conversion Rate"
            value="3.24%"
            change={-2.1}
            description="-0.5% from last month"
            icon={<Activity className="w-4 h-4" />}
          />
          <StatsWidget
            title="Active Sessions"
            value="12,234"
            change={15.3}
            description="+1,234 from yesterday"
            icon={<BarChart3 className="w-4 h-4" />}
          />
        </div>

        {/* Charts Row */}
        <div className="dashboard-grid mb-8">
          <ChartWidget
            title="Revenue Overview"
            data={chartData}
            type="area"
            dataKey="value"
            color="#3b82f6"
          />
          <ChartWidget
            title="Daily Visitors"
            data={chartData}
            type="bar"
            dataKey="value"
            color="#8b5cf6"
          />
        </div>

        {/* Activity & Lists Row */}
        <div className="dashboard-grid">
          <ActivityWidget activities={activities} />
          <ListWidget title="Projects" items={projects} />
        </div>
      </main>
    </div>
  )
}
EOF

# Crea .env.example
cat > .env.example << 'EOF'
# Dashboard Configuration
NEXT_PUBLIC_APP_NAME=Dashboard
NEXT_PUBLIC_API_URL=http://localhost:3000/api
EOF

# Crea README
cat > README.md << EOF
# $PROJECT_NAME

Dashboard creata con AI Labs Builder

## Features

- Widget system con 4 tipi di widget
- Charts interattivi con Recharts
- Dark/Light mode
- Responsive layout
- Real-time data ready
- TypeScript + Next.js 15

## Widgets Disponibili

### StatsWidget
Visualizza metriche con trend indicator

### ChartWidget
Grafici Line, Area, Bar con Recharts

### ActivityWidget
Feed attività recenti

### ListWidget
Liste con status indicator

## Getting Started

\`\`\`bash
npm install
npm run dev
\`\`\`

## Customizzazione

Modifica i widget in \`components/widgets/\`
Aggiungi nuovi widget seguendo il pattern esistente.
EOF

log_success "Dashboard creata con successo!"
log_info "Tipo: $TYPE"
log_info "Per iniziare:"
echo "  cd $PROJECT_NAME"
echo "  npm install"
echo "  npm run dev"
