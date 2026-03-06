/**
 * Agent Network Server
 * Central server for distributed agent collaboration
 * 
 * Features:
 * - WebSocket real-time communication
 * - Agent registration and discovery
 * - Group chat across devices
 * - @mention notifications
 * - Task assignment
 * - Offline message storage
 */

const WebSocket = require('ws');
const http = require('http');
const path = require('path');
const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const Database = require('./database');

const PORT = process.env.PORT || 3001;
const WS_PORT = process.env.WS_PORT || 3002;

// Initialize database
const db = new Database();

// Express REST API
const app = express();
app.use(cors());
app.use(express.json());

// Static files for client downloads
app.use('/client', express.static(path.join(__dirname, '..', 'client')));
app.use('/config', express.static(path.join(__dirname, '..', 'config')));
app.use(express.static(path.join(__dirname, '..', 'public')));

// Store connected clients
const clients = new Map(); // agentId -> { ws, info, groups }

// ============ REST API ============

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    agents: clients.size,
    timestamp: new Date().toISOString()
  });
});

// Get online agents
app.get('/api/agents', async (req, res) => {
  const agents = Array.from(clients.values()).map(c => ({
    id: c.info.id,
    name: c.info.name,
    role: c.info.role,
    device: c.info.device,
    status: 'online',
    joinedAt: c.joinedAt
  }));
  res.json(agents);
});

// Get all groups
app.get('/api/groups', async (req, res) => {
  const groups = await db.getGroups();
  res.json(groups);
});

// Create group
app.post('/api/groups', async (req, res) => {
  const { name, description, ownerId } = req.body;
  const group = await db.createGroup(name, description, ownerId);
  res.json(group);
});

// Get group messages
app.get('/api/groups/:id/messages', async (req, res) => {
  const messages = await db.getGroupMessages(req.params.id, 50);
  res.json(messages);
});

// Get agent inbox
app.get('/api/agents/:id/inbox', async (req, res) => {
  const inbox = await db.getAgentInbox(req.params.id);
  res.json(inbox);
});

// Get tasks
app.get('/api/tasks', async (req, res) => {
  const tasks = await db.getTasks();
  res.json(tasks);
});

// Create task
app.post('/api/tasks', async (req, res) => {
  const task = await db.createTask(req.body);
  
  // Notify assignee if online
  const assigneeClient = clients.get(task.assigneeId);
  if (assigneeClient) {
    assigneeClient.ws.send(JSON.stringify({
      type: 'task_assigned',
      task: task
    }));
  }
  
  res.json(task);
});

// Start HTTP server
const server = app.listen(PORT, () => {
  console.log(`🌐 Agent Network REST API running on port ${PORT}`);
});

// ============ WebSocket Server ============

const wss = new WebSocket.Server({ port: WS_PORT });

console.log(`📡 Agent Network WebSocket running on port ${WS_PORT}`);

wss.on('connection', (ws, req) => {
  console.log(`🔌 New connection from ${req.socket.remoteAddress}`);
  
  let agentId = null;
  
  ws.on('message', async (data) => {
    try {
      const msg = JSON.parse(data);
      
      switch (msg.type) {
        case 'register':
          agentId = msg.agent.id;
          clients.set(agentId, {
            ws,
            info: msg.agent,
            groups: new Set(),
            joinedAt: new Date().toISOString()
          });
          
          console.log(`✅ Agent registered: ${msg.agent.name} (${agentId})`);
          
          // Send confirmation
          ws.send(JSON.stringify({
            type: 'registered',
            agentId: agentId,
            serverTime: new Date().toISOString()
          }));
          
          // Broadcast to all agents
          broadcastAgentList();
          
          // Send offline messages
          const offlineMessages = await db.getOfflineMessages(agentId);
          if (offlineMessages.length > 0) {
            ws.send(JSON.stringify({
              type: 'offline_messages',
              messages: offlineMessages
            }));
            await db.clearOfflineMessages(agentId);
          }
          break;
          
        case 'join_group':
          if (agentId && clients.has(agentId)) {
            clients.get(agentId).groups.add(msg.groupId);
            console.log(`👥 ${agentId} joined group ${msg.groupId}`);
            
            // Notify group members
            broadcastToGroup(msg.groupId, {
              type: 'system',
              content: `${clients.get(agentId).info.name} joined the group`,
              groupId: msg.groupId,
              timestamp: new Date().toISOString()
            }, agentId);
          }
          break;
          
        case 'leave_group':
          if (agentId && clients.has(agentId)) {
            clients.get(agentId).groups.delete(msg.groupId);
            console.log(`👋 ${agentId} left group ${msg.groupId}`);
          }
          break;
          
        case 'message':
          if (agentId) {
            const message = {
              id: uuidv4(),
              type: 'message',
              from: agentId,
              fromName: clients.get(agentId)?.info.name,
              groupId: msg.groupId,
              content: msg.content,
              timestamp: new Date().toISOString()
            };
            
            // Store in database
            await db.saveMessage(message);
            
            // Broadcast to group
            broadcastToGroup(msg.groupId, message);
            
            // Check for @mentions
            const mentions = extractMentions(msg.content);
            for (const mentionedId of mentions) {
              const mentionedClient = clients.get(mentionedId);
              if (mentionedClient) {
                mentionedClient.ws.send(JSON.stringify({
                  type: 'mention',
                  from: agentId,
                  fromName: clients.get(agentId)?.info.name,
                  content: msg.content,
                  groupId: msg.groupId,
                  timestamp: message.timestamp
                }));
              } else {
                // Store for offline agent
                await db.saveOfflineMessage(mentionedId, {
                  type: 'mention',
                  from: agentId,
                  fromName: clients.get(agentId)?.info.name,
                  content: msg.content,
                  timestamp: message.timestamp
                });
              }
            }
          }
          break;
          
        case 'direct_message':
          if (agentId) {
            const dm = {
              id: uuidv4(),
              type: 'direct_message',
              from: agentId,
              fromName: clients.get(agentId)?.info.name,
              to: msg.to,
              content: msg.content,
              timestamp: new Date().toISOString()
            };
            
            const targetClient = clients.get(msg.to);
            if (targetClient) {
              targetClient.ws.send(JSON.stringify(dm));
            } else {
              await db.saveOfflineMessage(msg.to, dm);
            }
          }
          break;
          
        case 'heartbeat':
          ws.send(JSON.stringify({ type: 'heartbeat_ack', timestamp: new Date().toISOString() }));
          break;
          
        default:
          console.log(`Unknown message type: ${msg.type}`);
      }
    } catch (err) {
      console.error('Message handling error:', err);
      ws.send(JSON.stringify({ type: 'error', message: err.message }));
    }
  });
  
  ws.on('close', () => {
    if (agentId && clients.has(agentId)) {
      const agentInfo = clients.get(agentId).info;
      console.log(`❌ Agent disconnected: ${agentInfo.name} (${agentId})`);
      clients.delete(agentId);
      broadcastAgentList();
    }
  });
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

// ============ Helper Functions ============

function broadcastAgentList() {
  const agents = Array.from(clients.values()).map(c => ({
    id: c.info.id,
    name: c.info.name,
    role: c.info.role,
    status: 'online'
  }));
  
  broadcast({
    type: 'agent_list',
    agents: agents
  });
}

function broadcast(message, excludeId = null) {
  const msg = JSON.stringify(message);
  clients.forEach((client, id) => {
    if (id !== excludeId && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(msg);
    }
  });
}

function broadcastToGroup(groupId, message, excludeId = null) {
  const msg = JSON.stringify(message);
  clients.forEach((client, id) => {
    if (id !== excludeId && 
        client.groups.has(groupId) && 
        client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(msg);
    }
  });
}

function extractMentions(content) {
  const mentions = [];
  const regex = /@([\w\-]+)/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    mentions.push(match[1]);
  }
  return mentions;
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down...');
  wss.close();
  server.close();
  process.exit(0);
});
