// Heartbeat Monitor Template
import { HeartbeatMonitor } from 'checkly/constructs'

new HeartbeatMonitor('app-heartbeat-monitor', {
  name: 'App Heartbeat Monitor',
  period: 300, // Expect ping every 5 minutes
  periodUnit: 'seconds',
  grace: 60,   // Allow 60 second grace period
  tags: ['heartbeat', 'infrastructure'],
})

// Your application should ping:
// POST https://ping.checklyhq.com/heartbeats/{heartbeat-id}
