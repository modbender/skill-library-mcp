---
name: mission-control
description: Build a personal dashboard for OpenClaw with task management, memory browser, calendar, team tracking, and GitHub trends. Use when the user wants to create a web-based mission control dashboard for their OpenClaw instance, track tasks, view memories, manage calendar events, or build a custom dashboard interface.
---

# Mission Control Skill

Build your own personal dashboard for OpenClaw - a central command center for tasks, memories, calendar, and team management.

## What You'll Build

A Next.js web dashboard that connects to your OpenClaw instance and provides:

- **Task Board** - Kanban-style task management
- **Memory Browser** - Search and view your OpenClaw memories
- **Calendar View** - See scheduled events and cron jobs
- **Team Status** - Track who's working on what
- **GitHub Trends** - Discover trending repositories

## Architecture Overview

```
┌─────────────────────────────────────┐
│         Next.js Frontend            │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  Task   │ │ Memory  │ │Calendar│ │
│  │  Board  │ │  List   │ │  View  │ │
│  └────┬────┘ └────┬────┘ └───┬────┘ │
│       └───────────┴──────────┘       │
│              │                       │
│       ┌──────┴──────┐                │
│       │   API Routes │               │
│       └──────┬──────┘                │
└──────────────┼───────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────┴──────┐ ┌──────┴──────┐
│ Local JSON  │ │  OpenClaw   │
│   Files     │ │   Memory    │
└─────────────┘ └─────────────┘
```

## Prerequisites

- Node.js 18+
- OpenClaw installed and running
- Basic knowledge of React/Next.js

## Step-by-Step Guide

### Step 1: Initialize Project

```bash
npx create-next-app@latest mission-control --typescript --tailwind
```

### Step 2: Install Dependencies

```bash
cd mission-control
npm install lucide-react
```

### Step 3: Create Data Layer

Create `src/lib/data.ts` for file-based storage:

```typescript
import fs from "fs/promises";
import path from "path";

const DATA_DIR = path.join(process.cwd(), "src", "data");

// Types
export interface Task {
  id: string;
  title: string;
  description: string;
  status: "todo" | "in-progress" | "done";
  assignee: string;
  createdAt: string;
  updatedAt: string;
}

// Initialize data files
async function initDataFile(filename: string, defaultData: unknown) {
  const filepath = path.join(DATA_DIR, filename);
  try {
    await fs.access(filepath);
  } catch {
    await fs.mkdir(DATA_DIR, { recursive: true });
    await fs.writeFile(filepath, JSON.stringify(defaultData, null, 2));
  }
  return filepath;
}

// Tasks
export async function getTasks(): Promise<Task[]> {
  const filepath = await initDataFile("tasks.json", []);
  const data = await fs.readFile(filepath, "utf-8");
  return JSON.parse(data);
}

export async function addTask(task: Omit<Task, "id" | "createdAt" | "updatedAt">): Promise<Task> {
  const tasks = await getTasks();
  const newTask: Task = {
    ...task,
    id: Date.now().toString(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  tasks.push(newTask);
  await fs.writeFile(
    path.join(DATA_DIR, "tasks.json"),
    JSON.stringify(tasks, null, 2)
  );
  return newTask;
}

export async function updateTask(id: string, updates: Partial<Task>): Promise<Task | null> {
  const tasks = await getTasks();
  const index = tasks.findIndex((t) => t.id === id);
  if (index === -1) return null;
  
  tasks[index] = { 
    ...tasks[index], 
    ...updates, 
    updatedAt: new Date().toISOString() 
  };
  await fs.writeFile(
    path.join(DATA_DIR, "tasks.json"),
    JSON.stringify(tasks, null, 2)
  );
  return tasks[index];
}
```

### Step 4: Create API Routes

Create `src/app/api/tasks/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { getTasks, addTask, updateTask } from "@/lib/data";

export async function GET() {
  const tasks = await getTasks();
  return NextResponse.json(tasks);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const task = await addTask(body);
    return NextResponse.json(task, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to create task" },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const { id, ...updates } = await request.json();
    const task = await updateTask(id, updates);
    if (!task) {
      return NextResponse.json({ error: "Task not found" }, { status: 404 });
    }
    return NextResponse.json(task);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to update task" },
      { status: 500 }
    );
  }
}
```

### Step 5: Create Components

**Navigation Component** (`src/components/Navigation.tsx`):

```typescript
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { LayoutDashboard, ClipboardList, Menu, X } from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/tasks", label: "Tasks", icon: ClipboardList },
];

export function Navigation() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 bg-gray-800 border-r border-gray-700 flex-col h-screen">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-xl font-bold text-blue-400">Mission Control</h1>
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? "bg-blue-600 text-white"
                        : "text-gray-300 hover:bg-gray-700"
                    }`}
                  >
                    <Icon size={20} />
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center justify-between px-4 py-3">
          <h1 className="text-lg font-bold text-blue-400">Mission Control</h1>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-gray-700"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <aside className="lg:hidden fixed top-[60px] left-0 bottom-0 w-64 bg-gray-800 z-40">
          {/* Same nav as desktop */}
        </aside>
      )}
    </>
  );
}
```

### Step 6: Create Task Board

```typescript
"use client";

import { useState, useEffect } from "react";

interface Task {
  id: string;
  title: string;
  description: string;
  status: "todo" | "in-progress" | "done";
  assignee: string;
}

export function TaskBoard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await fetch("/api/tasks");
      const data = await response.json();
      setTasks(data);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (taskId: string, newStatus: Task["status"]) => {
    await fetch("/api/tasks", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: taskId, status: newStatus }),
    });
    fetchTasks();
  };

  const tasksByStatus = {
    todo: tasks.filter((t) => t.status === "todo"),
    "in-progress": tasks.filter((t) => t.status === "in-progress"),
    done: tasks.filter((t) => t.status === "done"),
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {Object.entries(tasksByStatus).map(([status, statusTasks]) => (
        <div key={status} className="bg-gray-800/50 rounded-xl p-4">
          <h3 className="font-semibold text-gray-300 mb-4 capitalize">{status}</h3>
          <div className="space-y-3">
            {statusTasks.map((task) => (
              <div key={task.id} className="bg-gray-800 p-4 rounded-lg">
                <h4 className="font-medium">{task.title}</h4>
                <select
                  value={task.status}
                  onChange={(e) => handleUpdateStatus(task.id, e.target.value as Task["status"])}
                  className="mt-2 text-sm bg-gray-700 border border-gray-600 rounded px-2 py-1"
                >
                  <option value="todo">To Do</option>
                  <option value="in-progress">In Progress</option>
                  <option value="done">Done</option>
                </select>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Step 7: OpenClaw Memory Sync

Create `src/app/api/sync/route.ts`:

```typescript
import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET() {
  try {
    // Read OpenClaw memory files
    const memoryDir = path.join(process.env.HOME || "", "clawd", "memory");
    const files = await fs.readdir(memoryDir);
    
    const memories = [];
    for (const file of files.filter(f => f.endsWith('.md'))) {
      const content = await fs.readFile(path.join(memoryDir, file), 'utf-8');
      memories.push({
        id: file,
        title: file.replace('.md', ''),
        content: content.slice(0, 500) + '...',
        createdAt: new Date().toISOString(),
      });
    }
    
    return NextResponse.json(memories);
  } catch (error) {
    return NextResponse.json([]);
  }
}
```

### Step 8: Create Layout

```typescript
import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

export const metadata: Metadata = {
  title: "Mission Control",
  description: "Personal dashboard for OpenClaw",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white">
        <div className="flex flex-col lg:flex-row min-h-screen">
          <Navigation />
          <main className="flex-1 overflow-auto pt-[60px] lg:pt-0 p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
```

### Step 9: Start Script

Create `start.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")"
npm run dev
```

Make it executable:

```bash
chmod +x start.sh
```

### Step 10: Run

```bash
./start.sh
```

Open http://localhost:3000

## Extending Mission Control

### Add GitHub Trends

```typescript
// src/app/api/github-trends/route.ts
export async function GET() {
  const response = await fetch(
    "https://api.github.com/search/repositories?q=stars:>1000&sort=stars&per_page=10"
  );
  const data = await response.json();
  return NextResponse.json(data.items);
}
```

### Add Calendar Events

Store events in `src/data/calendar.json` and create similar API routes.

### Add Team Members

Create `src/data/team.json` with member info and current tasks.

## Mobile Responsiveness Tips

1. **Use Tailwind breakpoints**: `lg:` for desktop, default for mobile
2. **Touch targets**: Minimum 40px for buttons
3. **Horizontal scroll**: For Kanban board on mobile
4. **Drawer navigation**: Slide-in menu for mobile

## Security Considerations

- Store personal data in `src/data/` (gitignored)
- Keep template data in the skill
- No authentication included - add your own if needed
- Run locally or behind a VPN

## Troubleshooting

**Port already in use?**
```bash
PORT=3001 ./start.sh
```

**Data not saving?**
Ensure `src/data/` directory exists and is writable.

**OpenClaw sync not working?**
Check that OpenClaw memory path is correct in your environment.

## Resources

- Next.js docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com
- Lucide icons: https://lucide.dev

## License

MIT - Built for the OpenClaw community 🦞
