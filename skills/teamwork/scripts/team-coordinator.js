#!/usr/bin/env node

const path = require('path');
const init = require('./init.js');
const configManager = require('./config-manager.js');
const scoreManager = require('./score-manager.js');

class TeamCoordinator {
  constructor() {
    this.config = null;
    this.roles = null;
    this.scores = null;
    this.currentTask = null;
    this.team = [];
    this.herald = null;
  }

  load() {
    this.config = init.readJSON(init.PROVIDERS_FILE);
    this.roles = init.readJSON(init.ROLES_FILE);
    this.scores = init.readJSON(init.SCORES_FILE);
    
    if (!this.config || !this.roles || !this.scores) {
      throw new Error('Configuration not initialized. Please run initialization first.');
    }
  }

  getAvailableModels() {
    const models = configManager.getAvailableModels(this.config);
    return models.filter(m => m.status === 'available');
  }

  selectHerald() {
    const availableModels = this.getAvailableModels();
    
    if (availableModels.length === 0) {
      throw new Error('No available models for herald role');
    }
    
    const modelsWithScores = availableModels.map(m => {
      const score = this.scores.scores[m.model];
      return {
        ...m,
        response_speed: score ? score.dimensions.response_speed : 5.0,
        response_frequency: score ? score.dimensions.response_frequency : 5.0
      };
    });
    
    modelsWithScores.sort((a, b) => {
      const aScore = (a.response_speed + a.response_frequency) / 2;
      const bScore = (b.response_speed + b.response_frequency) / 2;
      return bScore - aScore;
    });
    
    this.herald = modelsWithScores[0];
    return this.herald;
  }

  assignRoles(requiredRoles) {
    const assignments = [];
    const availableModels = this.getAvailableModels();
    
    for (const roleName of requiredRoles) {
      const role = this.roles.roles[roleName];
      if (!role) {
        console.warn(`Role ${roleName} not found in configuration`);
        continue;
      }
      
      const candidates = availableModels.filter(m => {
        const hasCapability = role.required_capabilities.some(cap => 
          m.capabilities.includes(cap)
        );
        return hasCapability;
      });
      
      if (candidates.length === 0) {
        console.warn(`No suitable model found for role ${roleName}`);
        continue;
      }
      
      const scoredCandidates = candidates.map(c => {
        const score = this.scores.scores[c.model];
        const roleFit = score && score.role_fit_history[roleName] 
          ? score.role_fit_history[roleName].average 
          : (score ? score.overall_score : 5.0);
        
        return {
          ...c,
          roleFit,
          combinedScore: this.calculateCombinedScore(c, roleFit)
        };
      });
      
      scoredCandidates.sort((a, b) => b.combinedScore - a.combinedScore);
      
      assignments.push({
        role: roleName,
        model: scoredCandidates[0].model,
        provider: scoredCandidates[0].provider,
        score: scoredCandidates[0].combinedScore
      });
      
      const idx = availableModels.findIndex(m => m.model === scoredCandidates[0].model);
      if (idx > -1) {
        availableModels.splice(idx, 1);
      }
    }
    
    this.team = assignments;
    return assignments;
  }

  calculateCombinedScore(model, roleFit) {
    const score = this.scores.scores[model.model];
    const capabilityScore = score ? score.overall_score : 5.0;
    
    let costScore = 0.5;
    const provider = this.config.providers.find(p => p.name === model.provider);
    if (provider) {
      const modelConfig = provider.models.find(m => m.name === model.model);
      if (modelConfig) {
        if (modelConfig.pricing_model === 'subscription') {
          costScore = 1.0;
        } else if (modelConfig.pricing_model === 'tiered_usage') {
          costScore = 0.7;
        } else {
          costScore = 0.4;
        }
      }
    }
    
    return (capabilityScore * 0.4) + (roleFit * 0.3) + (costScore * 0.2) + (0.1);
  }

  createTaskPlan(userRequest) {
    const plan = {
      task_id: `task-${Date.now()}`,
      created_at: new Date().toISOString(),
      user_request: userRequest,
      phases: [
        {
          phase_id: 'phase-1',
          name: 'Requirement Analysis',
          status: 'pending',
          subtasks: []
        },
        {
          phase_id: 'phase-2',
          name: 'Task Decomposition',
          status: 'pending',
          subtasks: []
        },
        {
          phase_id: 'phase-3',
          name: 'Planning and Design',
          status: 'pending',
          subtasks: []
        },
        {
          phase_id: 'phase-4',
          name: 'Execution',
          status: 'pending',
          subtasks: []
        },
        {
          phase_id: 'phase-5',
          name: 'Testing and Validation',
          status: 'pending',
          subtasks: []
        },
        {
          phase_id: 'phase-6',
          name: 'Iteration and Refinement',
          status: 'pending',
          subtasks: []
        },
        {
          phase_id: 'phase-7',
          name: 'Final Review and Delivery',
          status: 'pending',
          subtasks: []
        }
      ],
      team: this.team,
      herald: this.herald,
      status: 'planned'
    };
    
    this.currentTask = plan;
    return plan;
  }

  generateMeetingAgenda(meetingType) {
    const agendas = {
      'team_assembly': [
        'Review task requirements and objectives',
        'Discuss required roles and capabilities',
        'Present model availability and scores',
        'Role assignment and conflict resolution',
        'Confirm team composition and responsibilities'
      ],
      'progress_review': [
        'Review completed subtasks',
        'Discuss current blockers',
        'Evaluate progress against timeline',
        'Adjust assignments if needed',
        'Plan next steps'
      ],
      'completion_review': [
        'Present final deliverables',
        'Review task completion metrics',
        'Conduct model performance evaluations',
        'Discuss lessons learned',
        'Update model scores'
      ],
      'failure_analysis': [
        'Present failure details',
        'Analyze root cause',
        'Discuss contributing factors',
        'Propose remediation strategies',
        'Plan next steps or iterations'
      ]
    };
    
    return agendas[meetingType] || [];
  }

  generateEvaluationForms() {
    const forms = [];
    
    for (const assignment of this.team) {
      for (const other of this.team) {
        if (assignment.model !== other.model) {
          forms.push({
            evaluator: assignment.model,
            evaluatee: other.model,
            task_id: this.currentTask?.task_id,
            role_played: other.role,
            dimensions: {},
            role_fit: null,
            status: 'pending'
          });
        }
      }
    }
    
    return forms;
  }

  generateReport() {
    if (!this.currentTask) {
      throw new Error('No current task to report on');
    }
    
    return {
      task_id: this.currentTask.task_id,
      timestamp: new Date().toISOString(),
      status: this.currentTask.status,
      team: this.team,
      herald: this.herald,
      phases: this.currentTask.phases,
      created_at: this.currentTask.created_at
    };
  }
}

module.exports = TeamCoordinator;
