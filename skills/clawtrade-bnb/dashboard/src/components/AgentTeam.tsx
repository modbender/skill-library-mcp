import React from 'react';
import { 
  IconStrategy, IconRisk, IconExecution, IconLearning, IconNarrator,
  IconActive
} from '../icons';

interface AgentTeamProps {
  isActive: boolean;
  lastCycle: any;
}

export function AgentTeam({ isActive, lastCycle }: AgentTeamProps) {
  const agents = [
    { 
      name: 'Strategy', 
      icon: IconStrategy,
      role: 'Vault Monitor',
      message: 'Analyzing APR deltas...', 
      status: 'active' // Always active now
    },
    { 
      name: 'Risk', 
      icon: IconRisk,
      role: 'Risk Manager',
      message: 'Validating risk profile...', 
      status: 'active' // Always active now
    },
    { 
      name: 'Execution', 
      icon: IconExecution,
      role: 'TX Processor',
      message: lastCycle ? 'Transaction sent...' : 'Waiting for cycle...',
      status: lastCycle ? 'executing' : 'active'
    },
    { 
      name: 'Learning', 
      icon: IconLearning,
      role: 'Optimizer',
      message: 'Training models...', 
      status: 'learning'
    },
    { 
      name: 'Narrator', 
      icon: IconNarrator,
      role: 'Explainer',
      message: 'Generating insights...', 
      status: 'active' // Always active now
    }
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Agent Team</h3>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          {agents.filter(a => a.status === 'active').length} Active
        </span>
      </div>
      <div className="agent-team-grid">
        {agents.map((agent, i) => {
          const Icon = agent.icon;
          return (
            <div key={i} className={`agent-card status-${agent.status}`}>
              <div className="agent-header">
                <div className="agent-icon">
                  <Icon size={24} color="var(--primary-light)" />
                </div>
                <div>
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-role">{agent.role}</div>
                </div>
              </div>
              <div className="agent-message">{agent.message}</div>
              <div className={`agent-status ${agent.status}`}>
                {agent.status === 'active' && (
                  <>
                    <IconActive size={8} color="var(--success)" style={{ marginRight: '4px' }} /> Active
                  </>
                )}
                {agent.status === 'idle' && 'Idle'}
                {agent.status === 'executing' && 'Executing'}
                {agent.status === 'learning' && 'Learning'}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
