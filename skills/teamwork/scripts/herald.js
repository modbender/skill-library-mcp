#!/usr/bin/env node

class Herald {
  constructor(model, provider) {
    this.model = model;
    this.provider = provider;
    this.pollingInterval = 30000;
    this.timeoutThreshold = 300000;
    this.messageQueue = [];
    this.teamStatus = {};
    this.taskProgress = {};
  }

  initializeTeam(team) {
    for (const member of team) {
      this.teamStatus[member.model] = {
        role: member.role,
        status: 'ready',
        lastHeartbeat: new Date().toISOString(),
        currentSubtask: null,
        progress: 0
      };
    }
  }

  broadcast(message, excludeSender = null) {
    const recipients = Object.keys(this.teamStatus).filter(m => m !== excludeSender);
    
    const broadcastMessage = {
      id: `msg-${Date.now()}`,
      timestamp: new Date().toISOString(),
      from: this.model,
      type: 'broadcast',
      content: message,
      recipients: recipients
    };
    
    this.messageQueue.push(broadcastMessage);
    return broadcastMessage;
  }

  sendDirectMessage(to, message, from) {
    const directMessage = {
      id: `msg-${Date.now()}`,
      timestamp: new Date().toISOString(),
      from: from,
      to: to,
      type: 'direct',
      content: message
    };
    
    this.messageQueue.push(directMessage);
    return directMessage;
  }

  updateProgress(model, subtaskId, progress, status) {
    if (!this.teamStatus[model]) {
      throw new Error(`Model ${model} not in team`);
    }
    
    this.teamStatus[model].currentSubtask = subtaskId;
    this.teamStatus[model].progress = progress;
    this.teamStatus[model].status = status;
    this.teamStatus[model].lastHeartbeat = new Date().toISOString();
    
    return this.getTeamStatus();
  }

  getTeamStatus() {
    const status = {
      timestamp: new Date().toISOString(),
      members: []
    };
    
    for (const [model, data] of Object.entries(this.teamStatus)) {
      status.members.push({
        model: model,
        role: data.role,
        status: data.status,
        progress: data.progress,
        currentSubtask: data.currentSubtask,
        lastHeartbeat: data.lastHeartbeat
      });
    }
    
    return status;
  }

  checkTimeouts() {
    const now = new Date();
    const timeouts = [];
    
    for (const [model, data] of Object.entries(this.teamStatus)) {
      const lastHeartbeat = new Date(data.lastHeartbeat);
      const elapsed = now - lastHeartbeat;
      
      if (elapsed > this.timeoutThreshold) {
        timeouts.push({
          model: model,
          role: data.role,
          elapsed: elapsed,
          status: 'timeout'
        });
      }
    }
    
    return timeouts;
  }

  pollTeam() {
    const pollRequest = {
      id: `poll-${Date.now()}`,
      timestamp: new Date().toISOString(),
      type: 'status_request',
      from: this.model
    };
    
    return pollRequest;
  }

  reportToHost(status) {
    const report = {
      id: `report-${Date.now()}`,
      timestamp: new Date().toISOString(),
      from: this.model,
      to: 'host',
      type: 'status_report',
      content: {
        teamStatus: this.getTeamStatus(),
        taskProgress: this.taskProgress,
        issues: this.checkTimeouts()
      }
    };
    
    return report;
  }

  notifyFailure(model, error, context) {
    const failureNotification = {
      id: `fail-${Date.now()}`,
      timestamp: new Date().toISOString(),
      from: model,
      to: this.model,
      type: 'failure',
      content: {
        error: error,
        context: context,
        subtask: this.teamStatus[model]?.currentSubtask
      }
    };
    
    return failureNotification;
  }

  notifyCompletion(model, result) {
    const completionNotification = {
      id: `complete-${Date.now()}`,
      timestamp: new Date().toISOString(),
      from: model,
      to: this.model,
      type: 'completion',
      content: {
        result: result,
        subtask: this.teamStatus[model]?.currentSubtask
      }
    };
    
    this.teamStatus[model].status = 'completed';
    this.teamStatus[model].progress = 100;
    
    return completionNotification;
  }

  getOverallProgress() {
    const members = Object.values(this.teamStatus);
    const totalProgress = members.reduce((sum, m) => sum + m.progress, 0);
    const avgProgress = members.length > 0 ? totalProgress / members.length : 0;
    
    return {
      overall: avgProgress,
      completed: members.filter(m => m.status === 'completed').length,
      inProgress: members.filter(m => m.status === 'in_progress').length,
      pending: members.filter(m => m.status === 'ready' || m.status === 'pending').length,
      failed: members.filter(m => m.status === 'failed').length
    };
  }

  getMessageQueue() {
    return this.messageQueue;
  }

  clearMessageQueue() {
    this.messageQueue = [];
  }
}

module.exports = Herald;
