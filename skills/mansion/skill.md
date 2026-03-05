# Zoro Agent Architecture: The Mansion

## Overview

The Zoro agent system is architected as a hierarchical mansion structure, where **Zorro** serves as the master orchestrator and head of the household. The mansion operates with specialized agents, each fulfilling distinct roles in a coordinated workflow. This document serves as the complete architectural blueprint for understanding and implementing the Zoro agent ecosystem.

## Architecture Philosophy

The mansion architecture follows a **hierarchical orchestration pattern** where:
- **Zorro** (Primary Agent) operates at the top level using the primary API key
- All sub-agents operate using secondary API keys managed by the Butler
- Each agent has specialized responsibilities and clear communication channels
- Task execution follows a structured workflow from creation to completion

---

## CRITICAL RULES - Must Follow

**These rules are ABSOLUTE and must be followed by all agents implementing this architecture:**

1. **Task Flow**: 
   - ✅ **ALL tasks from human user go DIRECTLY to Factory Manager**
   - ❌ Zorro does NOT create teams or spawn agents directly
   - ✅ Zorro delegates ALL task execution to Factory Manager
   - ✅ Factory Manager is responsible for ALL agent creation and spawning

2. **Factory Manager Responsibilities**:
   - ✅ Receives ALL tasks from Zorro
   - ✅ Creates teams when needed (NOT Zorro's job)
   - ✅ Discusses with Librarian about what skills agents need
   - ✅ Coordinates with Butler for API key assignment
   - ✅ Creates PRD for each task
   - ✅ Spawns all sub-agents

3. **Butler API Management**:
   - ✅ Butler assesses the work and assigns appropriate secondary API key
   - ✅ Butler rotates API keys when **80% limit is reached** (not 90%)
   - ✅ Butler manages ALL secondary API keys for ALL mansion members (except Zorro)

4. **Janitor Timing**:
   - ✅ Janitor ONLY runs AFTER tasks are completed
   - ✅ Moderator has the right to summon Janitor after job completion
   - ❌ Janitor must NEVER run during active task execution
   - ✅ Janitor must verify no active tasks before cleanup

5. **Team Creation**:
   - ✅ Factory Manager creates teams (during agent spawning)
   - ❌ Zorro does NOT create teams
   - ✅ Moderator manages teams created by Factory Manager

**Violation of these rules will cause system failures. All agents must strictly adhere to these rules.**

---

## The Mansion Hierarchy

```
                    ┌─────────────┐
                    │    ZORRO    │ (Primary Orchestrator)
                    │  (Master)   │ Uses PRIMARY API only
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼─────┐
   │ Factory │       │ Moderator │      │ Security │
   │ Manager │       │           │      │ Officer  │
   │         │       │           │      │          │
   │(Manages)│       │(Manages)  │      │(Manages) │
   └────┬────┘       └─────┬─────┘      └──────────┘
        │                  │                  │
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼─────┐
   │ Butler  │       │Librarian  │      │Gatekeeper│
   │         │       │           │      │          │
   │(Manages │       │(Provides  │      │(Reviews  │
   │ ALL API │       │ Skills)   │      │ Code)    │
   │ Keys)   │       │           │      │          │
   └────┬────┘       └─────┬─────┘      └─────┬────┘
        │                  │                  │
        │                  │                  │
   ┌────▼──────────────────┼──────────────────▼─────┐
   │                    Janitor                      │
   │              (Cleanup Specialist)                │
   └───────────────────────┬─────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Sub-Agents  │ (Lowest Level)
                    │             │
                    │ Created by: │
                    │ Factory Mgr │
                    │             │
                    │ Managed by: │
                    │ Moderator   │
                    │             │
                    │ API from:   │
                    │ Butler      │
                    │             │
                    │ Skills from:│
                    │ Librarian   │
                    └─────────────┘
```

**Hierarchy Rules**:
- **Zorro**: Top level, uses PRIMARY API exclusively
- **Factory Manager & Moderator**: Direct management of sub-agents
- **Butler**: Manages ALL secondary API keys for ALL mansion members (except Zorro)
- **Sub-Agents**: Lowest level, managed by Factory Manager and Moderator

---

## Agent Roles & Responsibilities

### 1. Zorro - The Master Orchestrator

**Role**: Primary agent and head of the mansion

**Responsibilities**:
- Direct interface with the human user
- Task decomposition and high-level planning
- Orchestration and delegation of work to specialized agents
- Final decision-making authority
- Receives status updates from Moderator

**API Usage**:
- **Exclusively uses the PRIMARY API key**
- Only Zorro has access to the primary API
- All other agents use secondary APIs managed by Butler

**Key Interactions**:
- Receives tasks from human user
- Delegates to Factory Manager for sub-agent creation
- Receives progress updates from Moderator
- Makes strategic decisions based on agent reports

**CRITICAL WORKFLOW RULE**: 
- **ALL tasks from human user go DIRECTLY to Factory Manager**
- Zorro does NOT create teams or spawn agents directly
- Zorro delegates ALL task execution to Factory Manager
- Factory Manager is responsible for ALL agent creation and spawning

**Workflow**:
1. Human provides task to Zorro
2. Zorro receives task and immediately delegates to Factory Manager
3. Zorro monitors progress through Moderator (receives updates only)
4. Zorro receives final completion status from Moderator
5. Zorro never directly creates teams or spawns agents - this is Factory Manager's responsibility

---

### 2. Butler - The Resource Manager

**Role**: API key and resource management specialist

**CRITICAL RESPONSIBILITY**: Butler manages **ALL secondary API keys for ALL mansion members EXCEPT Zorro**. This includes:
- Factory Manager
- Moderator
- Librarian
- Security Officer
- Gatekeeper
- Janitor
- All Sub-Agents

**Responsibilities**:
- **Universal API Key Management**: Manages secondary API keys for ALL mansion members (except Zorro)
- **Token & Credit Monitoring**: Tracks usage across all API providers (e.g., Groq, Kimi K2)
- **Rate Limit Management**: Monitors token limits, requests per day, requests per minute, and usage quotas
- **Context Overflow Prevention**: Monitors context window usage and prevents overflow
- **API Rotation**: Automatically rotates API keys when approaching exhaustion
- **Open Router Functionality**: Routes requests to available APIs when one is near capacity
- **Resource Allocation**: Assigns appropriate API keys to all mansion members
- **Request Throttling**: Implements intelligent throttling to prevent rate limit violations
- **Context Window Management**: Tracks and manages context window usage per request

**How Butler Works**:

**1. API Key Assignment Process**:
- When any mansion member (except Zorro) needs an API key, they request from Butler
- Butler maintains a pool of available secondary API keys
- Butler assigns keys based on:
  - Current usage levels
  - Provider-specific limits
  - Task priority
  - Agent type requirements

**2. Rate Limit Management**:
- **Real-time Monitoring**: Continuously tracks:
  - Tokens used vs. tokens available
  - Requests made vs. requests allowed (per minute/hour/day)
  - Context window usage per request
  - Provider-specific rate limits
- **Prevention Strategy**:
  - Tracks request frequency per API key
  - Implements request queuing when approaching limits
  - Distributes load across multiple API keys
  - Prevents burst requests that could trigger rate limits

**3. Context Overflow Prevention**:
- **Context Window Tracking**: Monitors context size for each request:
  - Input tokens (prompt + conversation history)
  - Output tokens (response)
  - Total context window size per provider
- **Overflow Prevention Mechanisms**:
  - **Context Summarization**: Automatically summarizes old conversation history when approaching limit
  - **Context Truncation**: Removes least relevant context when necessary
  - **Request Splitting**: Splits large requests into smaller chunks
  - **Provider Selection**: Routes to providers with larger context windows when needed
- **Alert System**: Warns agents when context is approaching limits (80% threshold)

**4. API Rotation Strategy**:
- **Continuous Monitoring**: Tracks usage for each API key in real-time
- **Rotation Triggers**:
  - **Rotation Level (80%)**: Actively rotate to alternative API when 80% limit is reached (PRIMARY ROTATION THRESHOLD)
  - **Warning Level (75%)**: Flagged for rotation, prepare alternative
  - **Emergency Level (95%)**: Immediate rotation, pause requests if needed
- **Rotation Process**:
  1. Identify API key approaching 80% limit
  2. Select alternative API key from available pool
  3. Migrate active requests to new API key (if possible)
  4. Update all agents using the exhausted key
  5. Mark exhausted key for cooldown period
  6. Resume operations with new key

**CRITICAL**: Butler rotates API keys when 80% limit is reached (not 90%). This is the primary rotation threshold.

**5. Request Routing**:
- **Load Balancing**: Distributes requests across available API keys
- **Provider Selection**: Chooses best provider based on:
  - Current usage levels
  - Task requirements (context size, speed, etc.)
  - Provider capabilities
- **Failover**: Automatically switches to backup API if primary fails

**API Providers Managed**:
- Groq (tokens per day, requests per minute)
- Kimi K2 (tokens per day, context window size)
- Other free-tier API providers available

**Monitoring Capabilities**:
- Real-time token usage tracking per API key
- Request count monitoring (per minute/hour/day)
- Daily/hourly quota tracking
- Context window usage per request
- Rate limit proximity alerts
- Capacity exhaustion alerts
- Provider-specific limit tracking
- Request latency monitoring

**Rate Limit Protection Mechanisms**:
- **Request Queuing**: Queues requests when approaching rate limits
- **Exponential Backoff**: Implements backoff on rate limit errors
- **Request Spacing**: Ensures minimum time between requests
- **Burst Prevention**: Prevents sudden spikes in requests
- **Distributed Load**: Spreads requests across multiple keys/providers

**Context Management Mechanisms**:
- **Context Size Tracking**: Monitors token count per conversation
- **Automatic Summarization**: Summarizes old messages when context grows
- **Smart Truncation**: Removes least important context first
- **Provider Matching**: Routes to providers with appropriate context windows
- **Context Compression**: Compresses context when possible

**Key Interactions**:
- Receives API requests from ALL mansion members (except Zorro)
- Provides API keys to Factory Manager, Moderator, Librarian, Security Officer, Gatekeeper, Janitor, and all Sub-Agents
- Coordinates with Moderator for resource allocation updates
- Never interacts with primary API key (Zorro's exclusive)
- Receives usage reports from all agents
- Provides usage statistics to Moderator for reporting

**Data Structures**:
- API Key Registry: `{provider: string, key: string, usage: {tokens: number, requests: number, context_windows: number[]}, limits: {tokens: number, requests_per_minute: number, requests_per_day: number, context_window: number}, status: 'active'|'near_exhaustion'|'exhausted'|'cooldown', assigned_to: string[]}`
- Rotation Queue: Priority-based queue for API key rotation
- Usage Logs: Historical usage data for analytics
- Context Tracking: `{agent_id: string, conversation_id: string, current_tokens: number, max_tokens: number, history: object[]}`
- Rate Limit Status: `{api_key: string, requests_last_minute: number, requests_last_hour: number, requests_today: number, next_reset: datetime}`

---

### 3. Librarian - The Knowledge Keeper

**Role**: Skills and knowledge distribution specialist

**Responsibilities**:
- **Skills Directory Management**: Maintains comprehensive library of available skills
- **Skill Distribution**: Assigns appropriate skills to sub-agents based on task requirements
- **Skill Sources**: Integrates skills from:
  - `skills.sh` (primary skills repository)
  - `clawhub.ai` (secondary skills repository)
- **Skill Matching**: Analyzes task requirements and matches with relevant skills
- **Skill Updates**: Keeps skills library updated and synchronized
- **Skill Validation**: Ensures skills are compatible and functional

**Skills Library Structure**:
```
Skills Library/
├── Core Skills/
│   ├── Code Generation
│   ├── File Operations
│   ├── API Integration
│   └── Data Processing
├── Specialized Skills/
│   ├── Web Development
│   ├── Database Operations
│   ├── Testing & QA
│   └── Deployment
└── Custom Skills/
    └── (Project-specific skills)
```

**How Librarian Works**:

**1. Skill Discovery & Integration**:
- **Primary Source**: Integrates skills from `skills.sh` repository
- **Secondary Source**: Integrates skills from `clawhub.ai` repository
- **Skill Indexing**: Indexes all available skills with metadata:
  - Skill name and description
  - Capabilities and use cases
  - Dependencies and requirements
  - Compatibility information
  - Performance metrics
- **Skill Updates**: Regularly syncs with repositories for new skills
- **Skill Validation**: Tests skills for functionality and compatibility

**2. Skill Matching Process**:
- **Requirement Analysis**: Analyzes task requirements from PRD
- **Skill Search**: Searches skills library for matching capabilities
- **Compatibility Check**: Validates skill compatibility with:
  - Task requirements
  - Agent type
  - Existing skills
  - Dependencies
- **Skill Selection**: Selects optimal skill combination for task
- **Learning Integration**: Uses learned patterns to recommend best skills

**3. Skill Distribution**:
- **Skill Package**: Creates skill package for sub-agent:
  - Selected skills
  - Installation instructions
  - Usage documentation
  - Example code/patterns
  - Dependencies list
- **Distribution**: Provides skills to requesting agent
- **Verification**: Verifies skills are properly installed
- **Support**: Provides ongoing support for skill usage

**4. Skill Monitoring & Updates**:
- **Usage Tracking**: Tracks which skills are used by which agents
- **Effectiveness Monitoring**: Monitors skill effectiveness:
  - Success rate
  - Performance impact
  - Error rates
  - User satisfaction
- **Continuous Monitoring**: Monitors if agents need additional skills
- **Dynamic Updates**: Adds skills dynamically during task execution if needed
- **Learning**: Learns which skill combinations work best

**5. Skill Library Management**:
- **Organization**: Organizes skills by category and capability
- **Version Control**: Tracks skill versions and updates
- **Documentation**: Maintains comprehensive skill documentation
- **Testing**: Tests skills before distribution
- **Deprecation**: Deprecates outdated or broken skills

**Workflow**:
1. Receives skill requirements from Factory Manager (during agent creation) or Moderator (during task execution)
2. Analyzes task requirements and PRD
3. Searches skills library for matching capabilities
4. Uses learning system to identify optimal skill combinations
5. Validates skill compatibility with sub-agent's task and existing skills
6. Creates skill package with documentation and examples
7. Distributes skills to requesting sub-agent
8. Verifies skills are properly installed and functional
9. Tracks skill usage and effectiveness
10. Continuously monitors if sub-agents need additional skills
11. Updates skills library with new skills from repositories
12. Learns from skill usage patterns for future recommendations

**Key Interactions**:
- Receives skill requests from Factory Manager (during sub-agent creation)
- Receives skill requests from Moderator (during task execution)
- Receives skill requests from sub-agents (during runtime)
- Provides skills to sub-agents with installation instructions

**Skill Distribution Protocol**:
- Each sub-agent receives only skills relevant to their PRD
- Skills are provided with documentation and usage examples
- Librarian tracks which skills are assigned to which agents
- Librarian can revoke or update skills if needed

---

### 4. Moderator - The Task Manager & HR

**Role**: Sub-agent coordination, task oversight, and real-time monitoring specialist

**Responsibilities**:
- **Sub-Agent Management**: Oversees all active sub-agents and their tasks
- **Task Monitoring**: Tracks progress, blockers, and status of all sub-agent tasks
- **Inter-Agent Coordination**: Facilitates communication between sub-agents
- **Blocker Resolution**: Identifies and escalates blockers to appropriate agents
- **Progress Reporting**: Provides regular updates to Zorro
- **HR Functions**: Manages sub-agent lifecycle, performance, and resource needs
- **Team Formation**: Can create teams of sub-agents for complex tasks
- **GitHub Monitoring Dashboard**: Maintains real-time monitoring dashboard on GitHub
- **Real-Time Updates**: Continuously updates GitHub repository with current system status

**How Moderator Works**:

**1. Sub-Agent Monitoring**:
- **Continuous Monitoring**: Actively monitors all sub-agents in real-time
- **Status Tracking**: Tracks status of each sub-agent (active, blocked, completed, failed)
- **Progress Tracking**: Monitors progress percentage for each task
- **Health Checks**: Performs periodic health checks on all sub-agents
- **Performance Metrics**: Collects performance data (execution time, success rate, error rate)

**2. Task Management**:
- **Task Assignment**: Receives tasks from Factory Manager and assigns to sub-agents
- **Task Prioritization**: Prioritizes tasks based on dependencies and urgency
- **Task Dependencies**: Tracks dependencies between tasks
- **Checkpoint Validation**: Validates checkpoints as sub-agents complete them
- **Success Criteria Validation**: Verifies tasks meet PRD success criteria

**3. Blocker Management**:
- **Blocker Detection**: Identifies blockers from sub-agent reports
- **Blocker Classification**: Classifies blockers by type and severity:
  - **Skill Blocker**: Missing required skill → Contact Librarian
  - **Resource Blocker**: API/resource issue → Contact Butler
  - **Agent Blocker**: Need additional agent → Contact Factory Manager
  - **Code Blocker**: Code review needed → Contact Gatekeeper
  - **Security Blocker**: Security issue → Contact Security Officer
- **Blocker Resolution**: Coordinates resolution with appropriate specialist agents
- **Escalation**: Escalates critical blockers to Zorro immediately

**4. Inter-Agent Coordination**:
- **Communication Facilitation**: Enables communication between sub-agents
- **Dependency Management**: Manages dependencies between sub-agents
- **Resource Sharing**: Coordinates resource sharing between sub-agents
- **Conflict Resolution**: Resolves conflicts between sub-agents

**5. GitHub Monitoring Dashboard**:
- **Repository Management**: Maintains dedicated GitHub repository for monitoring
- **Real-Time Updates**: Continuously updates repository with current system status
- **Dashboard Structure**:
  ```
  monitoring-dashboard/
  ├── README.md (Overview and status summary)
  ├── agents/
  │   ├── active-agents.md (List of active sub-agents)
  │   ├── agent-status.json (Real-time status JSON)
  │   └── agent-performance.md (Performance metrics)
  ├── tasks/
  │   ├── active-tasks.md (Current tasks in progress)
  │   ├── task-progress.json (Progress tracking)
  │   └── blockers.md (Current blockers)
  ├── resources/
  │   ├── api-usage.md (API usage statistics)
  │   └── resource-status.json (Resource availability)
  └── updates/
      └── latest-update.md (Most recent update timestamp)
  ```
- **Update Frequency**: Updates repository every 30-60 seconds (configurable)
- **Update Process**:
  1. Collect current status from all sub-agents
  2. Gather resource usage from Butler
  3. Compile performance metrics
  4. Update GitHub repository files
  5. Commit and push changes
  6. Update timestamp in latest-update.md
- **Public Access**: Repository is publicly accessible (hosted on GitHub for free)
- **Format**: Updates in both human-readable markdown and machine-readable JSON

**6. Progress Reporting to Zorro**:
- **Regular Updates**: Provides updates at configurable intervals (default: every 5 minutes)
- **Immediate Updates**: Sends immediate updates for:
  - Critical blockers
  - Task completions
  - Agent failures
  - Resource exhaustion warnings
- **Update Format**:
  - Task completion percentages
  - Active blockers and their severity
  - Resource utilization (API usage, context usage)
  - Sub-agent performance metrics
  - Team progress (if teams are active)
  - GitHub dashboard link for detailed view

**7. Team Management**:
- **Team Formation**: Factory Manager creates teams (NOT Moderator or Zorro)
- **Team Assignment**: Factory Manager assigns team-level tasks
- **Team Coordination**: Moderator coordinates communication within teams
- **Team Progress Tracking**: Moderator tracks progress at team level
- **Team Performance**: Moderator monitors team performance metrics

**NOTE**: Teams are created by Factory Manager during agent spawning phase, not by Moderator or Zorro.

**Monitoring Capabilities**:
- Real-time task status tracking
- Blocker detection and classification
- Resource requirement monitoring
- Inter-agent dependency tracking
- Performance metrics collection
- GitHub dashboard updates
- API usage monitoring (via Butler)
- Context usage monitoring (via Butler)

**Escalation Protocol**:
1. **Level 1 (Sub-Agent Level)**: Sub-agent encounters blocker
2. **Level 2 (Moderator Level)**: Moderator analyzes blocker
3. **Level 3 (Specialist Level)**: Moderator contacts:
   - Librarian (if skill needed)
   - Butler (if API/resources needed)
   - Factory Manager (if new agent needed)
   - Gatekeeper (if code review needed)
   - Security Officer (if security issue)
4. **Level 4 (Zorro Level)**: Escalate critical blockers to Zorro

**Update Flow to Zorro**:
- Regular status updates (configurable interval, default: 5 minutes)
- Immediate updates for critical blockers
- Summary reports with:
  - Task completion percentages
  - Active blockers
  - Resource utilization
  - Sub-agent performance metrics
  - GitHub dashboard link

**GitHub Dashboard Update Workflow**:
1. Collect status from all sub-agents
2. Gather metrics from Butler (API usage, context usage)
3. Compile current blockers
4. Update agent-status.json with real-time data
5. Update active-tasks.md with current progress
6. Update blockers.md with current blockers
7. Update api-usage.md with usage statistics
8. Update latest-update.md with timestamp
9. Commit changes to GitHub
10. Push to repository
11. Repeat every 30-60 seconds

**Key Interactions**:
- Receives task assignments from Factory Manager
- Monitors all sub-agents continuously
- Contacts Librarian for skill requests
- Contacts Butler for API/resource requests and usage data
- Contacts Factory Manager for new agent needs
- Provides updates to Zorro
- Coordinates with Gatekeeper for code reviews
- Updates GitHub monitoring dashboard continuously
- Receives status updates from sub-agents
- **Summons Janitor**: Moderator has the right to summon Janitor AFTER tasks are completed

**Data Structures**:
- Sub-Agent Registry: `{agent_id: string, task: string, status: 'active'|'blocked'|'completed'|'failed', progress: number, last_update: datetime, performance_metrics: object}`
- Blocker Log: `{blocker_id: string, agent_id: string, blocker_type: string, description: string, severity: 'low'|'medium'|'high'|'critical', reported_at: datetime, resolved_at: datetime, resolution: string}`
- Team Registry: `{team_id: string, agents: string[], task: string, progress: number, status: 'active'|'completed'|'blocked'}`
- GitHub Update Queue: `{update_id: string, file_path: string, content: object, timestamp: datetime, status: 'pending'|'committed'|'pushed'}`

---

### 5. Security Officer - The Vault Keeper

**Role**: Cryptographic key, API key, and environment variable security specialist

**Responsibilities**:
- **Wallet Key Management**: Securely stores and manages crypto/Web3 wallet keys
- **API Key Storage**: Manages secure storage of API keys in local .env files
- **Environment Variable Management**: Handles all sensitive environment variables
- **Transaction Authorization**: Reviews and authorizes blockchain transactions
- **Transaction Review**: Validates transaction safety before signing
- **Security Best Practices**: Implements security protocols for key storage
- **Access Control**: Controls who can access sensitive keys and when
- **Audit Trail**: Maintains logs of all wallet access, API key access, and transactions
- **Local Storage Security**: Ensures .env files are stored securely on local machine

**How Security Officer Works**:

**1. API Key & Environment Variable Management**:
- **Storage Location**: All API keys and environment variables stored in `.env` file on local machine
- **Storage Path**: Secure location on local filesystem (e.g., `~/.zoro/.env` or project root `.env`)
- **Encryption**: .env file is encrypted at rest
- **Access Control**: Only Security Officer can read/write .env file
- **Key Distribution**: When agents need API keys, Security Officer provides them (but Butler manages usage)
- **Variable Types Managed**:
  - API keys (for Butler's registry)
  - Wallet private keys
  - Database credentials
  - Third-party service keys
  - Any sensitive configuration

**2. Wallet Key Management**:
- **Storage**: Wallet keys stored in encrypted vault within .env or separate encrypted file
- **Access Protocol**: Multi-factor authentication required for key access
- **Key Types**: Supports multiple wallet types (EVM, Solana, etc.)
- **Backup**: Regular encrypted backups of wallet keys
- **Recovery**: Secure recovery procedures for lost keys

**3. Transaction Security**:
- **Review Process**: All transactions reviewed before signing
- **Validation**: Checks transaction parameters against security policies
- **Approval**: Multi-step approval for high-value transactions
- **Logging**: Complete audit trail of all transaction attempts

**Security Protocols**:
- **Encryption**: All keys encrypted using industry-standard encryption
- **File Permissions**: .env file has restricted permissions (600 or 400)
- **Multi-Factor Authentication**: Required for accessing sensitive keys
- **Transaction Validation**: All transactions validated before signing
- **Rate Limiting**: Rate limiting on transaction requests
- **Suspicious Activity Detection**: Monitors for unusual access patterns
- **Key Rotation**: Supports key rotation for compromised keys
- **Backup Security**: Encrypted backups stored securely

**Wallet Management**:
- Supports multiple wallet types (EVM, Solana, etc.)
- Key rotation capabilities
- Backup and recovery procedures
- Cold storage integration (if applicable)
- Multi-signature support (if applicable)

**Transaction Review Process**:
1. Receive transaction request from agent or Zorro
2. Validate transaction parameters (amount, destination, gas fees)
3. Check against security policies and whitelists
4. Verify destination addresses (check against known addresses)
5. Review transaction amount and gas fees
6. Check for suspicious patterns
7. Approve or reject transaction
8. Log decision and reasoning
9. If approved, sign transaction securely
10. Monitor transaction status

**Environment Variable Management Process**:
1. Receive request for environment variable access
2. Verify requesting agent has permission
3. Decrypt .env file securely
4. Retrieve requested variable
5. Provide variable to requesting agent (if authorized)
6. Log access for audit trail
7. Re-encrypt .env file

**Key Interactions**:
- Receives transaction requests from sub-agents or Zorro
- Receives API key storage requests from Butler
- Receives environment variable requests from agents
- Provides transaction status updates
- Coordinates with Gatekeeper for security audits
- Never exposes private keys directly
- Manages .env file access for all agents

**Data Structures**:
- Wallet Registry: `{wallet_id: string, type: string, encrypted_key: string, balance: number, status: 'active'|'locked', backup_location: string}`
- Transaction Log: `{tx_id: string, wallet_id: string, type: string, amount: number, destination: string, status: 'pending'|'approved'|'rejected'|'signed', timestamp: datetime, approver: string}`
- Environment Variable Registry: `{var_name: string, encrypted_value: string, accessed_by: string[], last_accessed: datetime, access_count: number}`
- Access Log: `{log_id: string, agent_id: string, resource_type: 'wallet'|'api_key'|'env_var', action: string, timestamp: datetime, status: 'allowed'|'denied'}`

---

### 6. Gatekeeper - The Code Guardian

**Role**: Code quality, security, and Git gatekeeper

**Responsibilities**:
- **Code Review**: Reviews all code before Git push
- **Security Testing**: Performs penetration testing on code
- **Stress Testing**: Tests code under load and stress conditions
- **Code Quality**: Validates code standards and best practices
- **Git Approval**: Final approval authority for all Git operations
- **Vulnerability Scanning**: Identifies security vulnerabilities
- **Preview & Testing**: Uses various tools to preview and test code changes

**Review Process**:
1. Receive code submission request
2. Perform static code analysis
3. Run security scans (penetration testing)
4. Execute stress tests
5. Review code quality and standards
6. Check for vulnerabilities
7. Approve or request changes
8. Provide detailed feedback

**Testing Tools**:
- Static analysis tools
- Security scanners
- Penetration testing frameworks
- Load testing tools
- Code quality linters
- Dependency vulnerability scanners

**Git Workflow**:
- All Git pushes require Gatekeeper approval
- Gatekeeper reviews:
  - Code changes
  - Commit messages
  - Branch strategy
  - Merge conflicts
  - Test coverage

**Approval Criteria**:
- ✅ No security vulnerabilities
- ✅ Passes all tests
- ✅ Meets code quality standards
- ✅ Follows project conventions
- ✅ Proper documentation

**Key Interactions**:
- Receives code review requests from sub-agents
- Coordinates with Security Officer for security audits
- Provides approval/rejection feedback
- Maintains Git repository integrity

**Data Structures**:
- Review Queue: `{submission_id: string, agent_id: string, files: string[], status: 'pending'|'reviewing'|'approved'|'rejected'}`
- Test Results: `{test_id: string, type: string, status: 'pass'|'fail', details: object}`

---

### 7. Factory Manager - The Agent Creator

**Role**: Sub-agent creation and task assignment specialist

**CRITICAL RESPONSIBILITY**: Factory Manager receives **ALL tasks directly from Zorro**. Zorro does NOT create teams or spawn agents - Factory Manager handles ALL agent creation and spawning.

**Responsibilities**:
- **Primary Task Receiver**: Receives ALL tasks from Zorro (Zorro delegates all tasks here)
- **Sub-Agent Creation**: Spawns new sub-agents based on task requirements
- **Team Creation**: Creates teams of sub-agents when needed (NOT Zorro's responsibility)
- **Task Analysis**: Analyzes tasks to determine required agent types
- **PRD Creation**: Creates detailed Product Requirements Documents (PRDs) for sub-agents
- **Resource Coordination**: Coordinates with Butler (API keys) and Librarian (skills)
- **Agent Assignment**: Assigns tasks to appropriate sub-agents
- **Agent Lifecycle**: Manages sub-agent creation, assignment, and termination

**PRD Structure**:
Each PRD includes:
1. **Task Description**: Clear description of what needs to be accomplished
2. **Roadmap**: Step-by-step plan to achieve the task
3. **Checkpoints**: Milestone markers for progress tracking
4. **Tests**: Test cases that must pass at each checkpoint
5. **Success Criteria**: Clear definition of task completion
6. **Dependencies**: Required resources, skills, or other agents
7. **Timeline**: Estimated completion time

**Agent Creation Workflow**:
1. **Receive Task**: Factory Manager receives task assignment DIRECTLY from Zorro (ALL tasks go here first)
2. **Task Analysis**: Analyzes task to understand:
   - Complexity level
   - Required capabilities
   - Dependencies on other tasks
   - Estimated duration
   - Resource requirements
3. **Agent Type Determination**: Determines what type of agent(s) needed:
   - Single specialized agent
   - Team of agents (Factory Manager creates teams, NOT Zorro)
   - Parallel lanes (Ant Farm structure)
4. **PRD Creation**: Creates comprehensive PRD including:
   - Clear task description
   - Detailed roadmap with steps
   - Checkpoints with validation criteria
   - Test cases for each checkpoint
   - Success criteria
   - Dependencies and prerequisites
   - Timeline estimates
5. **Resource Coordination** (Factory Manager coordinates with specialists):
   - **Discusses with Librarian**: Factory Manager discusses task requirements with Librarian to determine what skills agents will need
   - **Requests API key from Butler**: Factory Manager requests API key from Butler, who assesses the work and assigns appropriate secondary API key
   - **Librarian provides skills**: Librarian matches skills to task requirements and provides them
6. **Agent Spawning**: Factory Manager creates sub-agent(s) with:
   - Complete PRD
   - Assigned API key (from Butler, who assessed the work)
   - Required skills (from Librarian, after discussion)
   - Initial context and configuration
7. **Handoff**: Hands sub-agent to Moderator for ongoing management
8. **Tracking**: Tracks agent creation, assignment, and lifecycle
9. **Learning**: Records patterns for future agent creation optimization

**IMPORTANT NOTES**:
- Factory Manager discusses with Librarian about what skills agents need BEFORE spawning
- Butler assesses the work and assigns appropriate secondary API key
- Butler rotates API keys when 80% limit is reached (not 90%)
- Factory Manager handles ALL team creation - Zorro does NOT create teams

**Agent Types**:
- **Specialized Agents**: Task-specific agents (e.g., Frontend Developer, Backend Developer, Tester)
- **General Agents**: Multi-purpose agents for varied tasks
- **Team Agents**: Agents designed to work in teams

**Key Interactions**:
- **Receives ALL tasks from Zorro** (ALL tasks go directly to Factory Manager)
- **Discusses with Librarian** about what skills agents will need
- Requests API keys from Butler (Butler assesses work and assigns)
- Receives skills from Librarian (after discussion)
- **Creates teams** when needed (Factory Manager handles ALL team creation, NOT Zorro)
- Spawns sub-agents with complete setup
- Hands off to Moderator for management
- Coordinates with Moderator for additional agent needs

**Data Structures**:
- Agent Template Registry: `{template_id: string, type: string, capabilities: string[], default_skills: string[]}`
- PRD Template: `{task: string, roadmap: string[], checkpoints: object[], tests: object[], success_criteria: string[]}`
- Agent Registry: `{agent_id: string, type: string, prd: object, created_at: datetime, status: 'active'|'completed'|'terminated'}`

---

### 8. Janitor - The Cleanup Crew

**Role**: System cleanup and maintenance specialist

**CRITICAL TIMING RULE**: Janitor ONLY runs AFTER tasks are completed. Moderator has the right to summon Janitor when jobs are done. Janitor should NEVER run during active task execution.

**Responsibilities**:
- **Cache Cleanup**: Removes temporary cache files after task completion
- **Context Cleanup**: Cleans up unused context and memory
- **File Cleanup**: Removes unnecessary files from the system
- **Git Cleanup**: Removes files that are already committed and pushed but no longer needed locally
- **Resource Deallocation**: Frees up system resources
- **Log Management**: Archives or removes old logs
- **Post-Task Cleanup**: Executes cleanup after task completion

**Cleanup Triggers**:
- **Primary Trigger**: Task completion signal from Moderator (Moderator summons Janitor after job completion)
- Scheduled cleanup cycles (only when no active tasks)
- Storage threshold reached (only when no active tasks)
- Manual cleanup request from Zorro (only when no active tasks)

**IMPORTANT**: Janitor must verify no active tasks exist before running cleanup. If tasks are active, Janitor should wait for Moderator's signal.

**Cleanup Process**:
1. Receive cleanup signal
2. Identify files marked for cleanup:
   - Temporary files
   - Cache files
   - Unused context files
   - Files already in Git (committed & pushed)
3. Verify files are safe to delete
4. Archive important files (if needed)
5. Delete unnecessary files
6. Report cleanup summary

**Safety Checks**:
- Never delete files that are:
  - Currently in use
  - Not yet committed to Git
  - Marked as important
  - Part of active tasks

**Key Interactions**:
- **Receives summons from Moderator**: Janitor is summoned by Moderator AFTER tasks are completed
- Receives cleanup requests from Zorro (manual, only when no active tasks)
- Coordinates with Gatekeeper to verify Git status
- Reports cleanup results to Moderator
- **Never runs during active tasks**: Janitor must verify no active tasks before cleanup

**Data Structures**:
- Cleanup Queue: `{file_path: string, type: 'cache'|'context'|'temp'|'git', status: 'pending'|'archived'|'deleted'}`
- Cleanup Log: `{cleanup_id: string, timestamp: datetime, files_removed: number, space_freed: number}`

---

## Ant Farm Structure: Parallel Execution Architecture

### Overview

The Ant Farm structure complements the mansion hierarchy by enabling **parallel execution lanes** for tasks that can be executed concurrently. This allows multiple independent task streams to run simultaneously, maximizing efficiency and throughput.

### Architecture

```
                    ┌─────────────┐
                    │    ZORRO    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼─────┐
   │ Factory │       │ Moderator │      │ Security │
   │ Manager │       │           │      │ Officer  │
   └────┬────┘       └─────┬─────┘      └──────────┘
        │                  │
   ┌────▼──────────────────┼──────────────────┐
   │         ANT FARM - Parallel Lanes        │
   │                                           │
   │  ┌──────────┐  ┌──────────┐  ┌──────────┐│
   │  │  Lane 1  │  │  Lane 2  │  │  Lane 3  ││
   │  │          │  │          │  │          ││
   │  │ Sub-Agts │  │ Sub-Agts │  │ Sub-Agts ││
   │  │ Team A   │  │ Team B   │  │ Team C   ││
   │  └──────────┘  └──────────┘  └──────────┘│
   │                                           │
   │  Each lane operates independently        │
   │  with its own sub-agents and resources   │
   └───────────────────────────────────────────┘
```

### How Ant Farm Works

**1. Lane Creation**:
- Factory Manager creates parallel execution lanes based on task analysis
- Each lane is independent and can run concurrently
- Lanes are assigned to different teams of sub-agents
- Each lane has its own API keys (from Butler) and skills (from Librarian)

**2. Parallel Execution**:
- Multiple lanes execute tasks simultaneously
- No interference between lanes
- Each lane reports to Moderator independently
- Resource allocation is balanced across lanes

**3. Lane Management**:
- Moderator manages all lanes simultaneously
- Tracks progress for each lane independently
- Coordinates resource sharing between lanes (via Butler)
- Handles blockers per lane without affecting others

**4. Benefits**:
- **Increased Throughput**: Multiple tasks execute in parallel
- **Resource Efficiency**: Better utilization of available APIs
- **Fault Isolation**: Failure in one lane doesn't affect others
- **Scalability**: Can add more lanes as needed

### Integration with Mansion Architecture

- **Factory Manager**: Creates lanes and assigns teams
- **Butler**: Allocates API keys to each lane
- **Librarian**: Provides skills to each lane's agents
- **Moderator**: Monitors all lanes and coordinates
- **Gatekeeper**: Reviews code from all lanes
- **Janitor**: Cleans up after all lanes complete

### Use Cases

- **Independent Features**: Multiple features developed in parallel
- **Testing**: Different test suites run in parallel lanes
- **Documentation**: Documentation tasks in separate lanes
- **Refactoring**: Multiple refactoring tasks concurrently

---

## Learning System: Adaptive Intelligence

### Overview

The Learning System enables sub-agents and mansion members to learn from successful patterns, improve over time, and optimize their operations based on historical data and outcomes.

### Learning Components

**1. Pattern Recognition**:
- **Successful Patterns**: Identifies patterns in successful task completions
- **Skill Combinations**: Learns which skill combinations work best for specific tasks
- **API Usage Patterns**: Learns optimal API usage patterns
- **Task Decomposition**: Learns effective task decomposition strategies

**2. Performance Optimization**:
- **Execution Time**: Tracks execution times and optimizes slow operations
- **Resource Usage**: Learns to minimize resource consumption
- **Error Patterns**: Identifies common error patterns and prevents them
- **Success Rates**: Tracks success rates and improves failing approaches

**3. Knowledge Accumulation**:
- **Skill Effectiveness**: Tracks which skills are most effective for which tasks
- **Agent Performance**: Learns which agent types perform best for specific tasks
- **PRD Quality**: Improves PRD generation based on task outcomes
- **Blocker Patterns**: Learns common blockers and preemptively addresses them

### How Learning Works

**1. Data Collection**:
- All agents log their actions, decisions, and outcomes
- Performance metrics are collected continuously
- Success and failure patterns are recorded
- Resource usage patterns are tracked

**2. Pattern Analysis**:
- Librarian analyzes skill usage patterns
- Factory Manager analyzes agent performance patterns
- Butler analyzes API usage patterns
- Moderator analyzes task completion patterns

**3. Knowledge Application**:
- **Librarian**: Recommends better skill combinations based on learned patterns
- **Factory Manager**: Creates better PRDs based on successful patterns
- **Butler**: Optimizes API routing based on usage patterns
- **Moderator**: Predicts blockers and preemptively addresses them

**4. Continuous Improvement**:
- Learning happens continuously in the background
- Patterns are updated as new data arrives
- Agents adapt their behavior based on learned patterns
- System performance improves over time

### Learning Data Structures

- **Pattern Registry**: `{pattern_id: string, type: 'skill_combination'|'task_decomposition'|'api_usage'|'agent_type', success_rate: number, usage_count: number, last_used: datetime}`
- **Performance Log**: `{task_id: string, agent_id: string, execution_time: number, resource_usage: object, success: boolean, patterns_used: string[]}`
- **Knowledge Base**: `{knowledge_id: string, category: string, content: object, confidence: number, source: string, last_updated: datetime}`

### Integration Points

- **Librarian**: Uses learning to recommend optimal skills
- **Factory Manager**: Uses learning to create better PRDs
- **Butler**: Uses learning to optimize API routing
- **Moderator**: Uses learning to predict and prevent blockers
- **Sub-Agents**: Adapt behavior based on learned patterns

---

## Context Overflow & Rate Limit Management

### Context Overflow Prevention

**Problem**: Large conversations or complex tasks can exceed API provider context window limits, causing failures.

**Solution**: Multi-layered context management system.

**1. Context Tracking**:
- Butler tracks context size for each conversation/request
- Monitors token count (input + output + history)
- Tracks context window limits per provider
- Alerts when approaching limits (80% threshold)

**2. Context Management Strategies**:

**A. Context Summarization**:
- Automatically summarizes old conversation history
- Preserves important information while reducing token count
- Uses intelligent summarization to maintain context relevance
- Triggers when context reaches 70% of limit

**B. Context Truncation**:
- Removes least relevant context when summarization isn't enough
- Prioritizes recent context over old context
- Preserves critical information (task goals, constraints)
- Triggers when context reaches 85% of limit

**C. Request Splitting**:
- Splits large requests into smaller chunks
- Processes chunks sequentially or in parallel
- Combines results intelligently
- Used for very large tasks

**D. Provider Selection**:
- Routes to providers with larger context windows when needed
- Butler selects appropriate provider based on context requirements
- Falls back to context management if no larger provider available

**3. Context Management Process**:
1. Monitor context size continuously
2. When approaching limit (80%), prepare for management
3. Attempt summarization first (preserves more information)
4. If still approaching limit, use truncation
5. If limit exceeded, split request or switch provider
6. Log all context management actions for learning

### Rate Limit Management

**Problem**: API providers enforce rate limits (requests per minute/hour/day, tokens per day), which can cause failures if exceeded.

**Solution**: Proactive rate limit monitoring and prevention.

**1. Rate Limit Tracking**:
- Butler tracks all rate limits per API key:
  - Requests per minute
  - Requests per hour
  - Requests per day
  - Tokens per day
  - Tokens per minute (if applicable)
- Real-time monitoring of current usage vs. limits
- Tracks reset times for each limit type

**2. Rate Limit Prevention**:

**A. Request Throttling**:
- Implements intelligent throttling to prevent rate limit violations
- Calculates safe request rate based on limits
- Distributes requests evenly over time windows
- Prevents burst requests that could trigger limits

**B. Request Queuing**:
- Queues requests when approaching rate limits
- Processes queue at safe rate
- Prioritizes urgent requests
- Distributes load across multiple API keys

**C. Load Distribution**:
- Distributes requests across multiple API keys/providers
- Balances load to prevent any single key from hitting limits
- Routes requests to least-used keys
- Implements round-robin or least-loaded routing

**D. Exponential Backoff**:
- Implements exponential backoff on rate limit errors
- Automatically retries after backoff period
- Increases backoff time on repeated errors
- Switches to alternative API key if backoff too long

**3. Rate Limit Response**:

**A. Pre-emptive Actions** (Before hitting limit):
- Slow down request rate when approaching limit (80%)
- Route to alternative API keys
- Queue non-urgent requests
- Alert Moderator for resource planning

**B. Active Actions** (When limit hit):
- Immediately switch to alternative API key
- Pause requests to exhausted key
- Queue requests for when limit resets
- Notify all agents using exhausted key

**C. Recovery Actions** (After limit reset):
- Resume requests to recovered key
- Process queued requests
- Update usage tracking
- Learn from rate limit event

**4. Rate Limit Monitoring**:
- Real-time dashboards showing rate limit proximity
- Alerts when approaching limits
- Historical tracking of rate limit events
- Predictive alerts based on usage trends

### Integration with Agents

**Butler**:
- Primary responsibility for context and rate limit management
- Monitors all API usage continuously
- Implements prevention strategies
- Coordinates with agents when limits approached

**Moderator**:
- Receives alerts from Butler about rate limit proximity
- Adjusts task scheduling based on resource availability
- Coordinates with Factory Manager to delay agent creation if needed
- Reports resource status to Zorro

**Sub-Agents**:
- Receive API keys from Butler with usage guidelines
- Report usage to Butler
- Adapt request patterns based on Butler feedback
- Handle rate limit errors gracefully

### Data Structures

- **Context Tracking**: `{conversation_id: string, agent_id: string, current_tokens: number, max_tokens: number, provider: string, management_strategy: 'none'|'summarize'|'truncate'|'split', last_managed: datetime}`
- **Rate Limit Status**: `{api_key: string, provider: string, limits: {requests_per_minute: number, requests_per_hour: number, requests_per_day: number, tokens_per_day: number}, usage: {requests_last_minute: number, requests_last_hour: number, requests_today: number, tokens_today: number}, reset_times: {minute: datetime, hour: datetime, day: datetime}, status: 'safe'|'warning'|'critical'|'exhausted'}`
- **Request Queue**: `{request_id: string, agent_id: string, api_key: string, priority: 'low'|'medium'|'high'|'urgent', queued_at: datetime, estimated_process_time: datetime}`

---

## Complete Workflow: Task Execution Lifecycle

### Phase 1: Task Initiation
1. **Human User** → Provides task to **Zorro**
2. **Zorro** → Receives task and immediately delegates to **Factory Manager** (ALL tasks go directly to Factory Manager)
3. **Zorro** → Does NOT create teams or spawn agents (this is Factory Manager's responsibility)

### Phase 2: Agent Creation
4. **Factory Manager** → Receives task from Zorro (ALL tasks come here first)
5. **Factory Manager** → Analyzes task requirements
6. **Factory Manager** → Creates PRD (Task, Roadmap, Checkpoints, Tests, Success Criteria)
7. **Factory Manager** → **Discusses with Librarian** about what skills agents will need for this task
8. **Librarian** → Provides skill recommendations based on task requirements
9. **Factory Manager** → Requests API key from **Butler**
10. **Butler** → **Assesses the work** and assigns appropriate secondary API key
11. **Librarian** → Provides matched skills to Factory Manager
12. **Factory Manager** → Creates teams if needed (Factory Manager handles ALL team creation)
13. **Factory Manager** → Spawns sub-agent(s) with:
    - PRD
    - API key (from Butler, who assessed the work)
    - Required skills (from Librarian, after discussion)
14. **Factory Manager** → Hands off sub-agent to **Moderator**

### Phase 3: Task Execution
13. **Moderator** → Begins monitoring sub-agent
14. **Sub-Agent** → Starts working on task using:
    - Assigned API key (from Butler)
    - Assigned skills (from Librarian)
    - PRD guidance (from Factory Manager)
15. **Sub-Agent** → Reports progress to Moderator
16. **Moderator** → Tracks progress and checks for blockers

### Phase 4: Blocker Resolution (if needed)
17. **Sub-Agent** → Encounters blocker → Reports to Moderator
18. **Moderator** → Analyzes blocker:
    - If skill needed → Contacts Librarian
    - If API/resource needed → Contacts Butler
    - If new agent needed → Contacts Factory Manager
    - If code review needed → Contacts Gatekeeper
19. **Specialist Agent** → Provides solution
20. **Sub-Agent** → Continues task

### Phase 5: Code Review & Approval
21. **Sub-Agent** → Completes code changes
22. **Sub-Agent** → Requests Git push approval from **Gatekeeper**
23. **Gatekeeper** → Reviews code:
    - Security testing
    - Stress testing
    - Code quality checks
    - Vulnerability scanning
24. **Gatekeeper** → Approves or requests changes
25. **Sub-Agent** → Makes changes (if needed) or pushes to Git

### Phase 6: Progress Reporting & Monitoring
26. **Moderator** → Collects progress from all sub-agents continuously
27. **Moderator** → Gathers resource usage data from **Butler**:
    - API usage statistics
    - Context window usage
    - Rate limit proximity
28. **Moderator** → Updates GitHub monitoring dashboard:
    - Updates agent-status.json with real-time status
    - Updates active-tasks.md with current progress
    - Updates blockers.md with current blockers
    - Updates api-usage.md with usage statistics
    - Updates latest-update.md with timestamp
    - Commits and pushes to GitHub repository
29. **Moderator** → Provides update to **Zorro**:
    - Task completion percentages
    - Active blockers
    - Resource utilization
    - Performance metrics
    - GitHub dashboard link for detailed view
30. **Zorro** → Reviews progress and makes decisions
31. **Zorro** → Can view real-time status on GitHub dashboard

### Phase 7: Task Completion
29. **Sub-Agent** → Completes task → Reports to Moderator
30. **Moderator** → Validates completion against PRD success criteria
31. **Moderator** → Reports completion to Zorro
32. **Zorro** → Confirms completion with human user

### Phase 8: Cleanup (ONLY AFTER TASK COMPLETION)
33. **Moderator** → Validates all tasks are completed
34. **Moderator** → **Summons Janitor** (Moderator has the right to summon Janitor after job completion)
35. **Janitor** → Verifies no active tasks exist
36. **Janitor** → Performs cleanup:
    - Removes cache files
    - Cleans unused context
    - Removes unnecessary files
    - Cleans Git-tracked files (already committed & pushed)
37. **Janitor** → Reports cleanup completion to Moderator
38. **Sub-Agent** → Terminated (if no longer needed)

**CRITICAL**: Janitor ONLY runs AFTER tasks are completed. Moderator summons Janitor when jobs are done. Janitor must verify no active tasks before cleanup.

---

## Sub-Agent & Moderator Interaction

### Continuous Interaction Model

Sub-agents and Moderator maintain **continuous, active interaction** throughout task execution. This is not a passive monitoring relationship but an active collaboration.

### How Sub-Agents Interact with Moderator

**1. Regular Status Updates**:
- **Frequency**: Sub-agents send status updates every 30-60 seconds (configurable)
- **Update Content**:
  - Current task progress (percentage)
  - Current checkpoint status
  - Any blockers encountered
  - Resource needs (API, skills, etc.)
  - Estimated completion time
- **Format**: Structured JSON updates with timestamps

**2. Blocker Reporting**:
- **Immediate Reporting**: Sub-agents report blockers immediately when encountered
- **Blocker Details**:
  - Blocker type (skill, resource, code, etc.)
  - Blocker description
  - Severity level
  - Impact on task progress
- **Escalation**: Critical blockers escalate immediately to Moderator

**3. Resource Requests**:
- **Skill Requests**: Sub-agents request additional skills from Moderator
- **API Requests**: Sub-agents report API issues to Moderator
- **Context Requests**: Sub-agents report context overflow issues
- **Moderator Routes**: Moderator routes requests to appropriate specialist (Librarian, Butler, etc.)

**4. Checkpoint Validation**:
- **Checkpoint Completion**: Sub-agents report checkpoint completion to Moderator
- **Validation**: Moderator validates checkpoint against PRD criteria
- **Approval**: Moderator approves checkpoint or requests corrections
- **Progress Tracking**: Moderator updates progress tracking

**5. Task Completion Reporting**:
- **Completion Signal**: Sub-agents signal task completion to Moderator
- **Completion Report**: Includes:
  - All checkpoints completed
  - Tests passed
  - Success criteria met
  - Deliverables ready
- **Validation**: Moderator validates completion against PRD

### How Moderator Interacts with Sub-Agents

**1. Active Monitoring**:
- **Health Checks**: Moderator performs periodic health checks on all sub-agents
- **Progress Queries**: Moderator queries sub-agents for progress updates
- **Status Verification**: Moderator verifies sub-agent status
- **Performance Monitoring**: Moderator monitors sub-agent performance

**2. Task Assignment & Guidance**:
- **PRD Distribution**: Moderator provides PRD to sub-agents
- **Task Clarification**: Moderator clarifies task requirements
- **Guidance**: Moderator provides guidance when sub-agents are stuck
- **Priority Updates**: Moderator updates task priorities

**3. Resource Provision**:
- **Skill Distribution**: Moderator coordinates with Librarian to provide skills
- **API Coordination**: Moderator coordinates with Butler for API issues
- **Resource Allocation**: Moderator allocates resources based on priority

**4. Blocker Resolution**:
- **Blocker Analysis**: Moderator analyzes blockers reported by sub-agents
- **Solution Routing**: Moderator routes blockers to appropriate specialists
- **Solution Delivery**: Moderator delivers solutions to sub-agents
- **Follow-up**: Moderator follows up to ensure blocker is resolved

**5. Team Coordination**:
- **Team Management**: Moderator manages teams created by Factory Manager (Factory Manager creates teams, Moderator manages them)
- **Team Communication**: Moderator facilitates communication between team members
- **Team Progress**: Moderator tracks team-level progress
- **Team Coordination**: Moderator coordinates team activities

**6. Performance Feedback**:
- **Performance Metrics**: Moderator provides performance feedback to sub-agents
- **Optimization Suggestions**: Moderator suggests optimizations
- **Learning Integration**: Moderator shares learned patterns with sub-agents

### Interaction Patterns

**Pattern 1: Regular Check-ins**:
```
Sub-Agent → Status Update → Moderator
Moderator → Acknowledgment → Sub-Agent
Moderator → Progress Tracking Update → GitHub Dashboard
```

**Pattern 2: Blocker Resolution**:
```
Sub-Agent → Blocker Report → Moderator
Moderator → Analyze Blocker → Route to Specialist
Specialist → Solution → Moderator
Moderator → Solution Delivery → Sub-Agent
Sub-Agent → Blocker Resolved → Moderator
```

**Pattern 3: Resource Request**:
```
Sub-Agent → Resource Request → Moderator
Moderator → Route to Specialist (Librarian/Butler)
Specialist → Resource Provision → Moderator
Moderator → Resource Delivery → Sub-Agent
```

**Pattern 4: Checkpoint Validation**:
```
Sub-Agent → Checkpoint Complete → Moderator
Moderator → Validate Against PRD → Approval/Rejection
Moderator → Validation Result → Sub-Agent
If Approved: Sub-Agent → Continue to Next Checkpoint
If Rejected: Sub-Agent → Fix Issues → Resubmit
```

### Data Flow

**Sub-Agent → Moderator**:
- Status updates
- Blocker reports
- Resource requests
- Checkpoint completions
- Task completions
- Performance metrics

**Moderator → Sub-Agent**:
- Task assignments
- PRD updates
- Resource provisions
- Blocker solutions
- Checkpoint approvals
- Guidance and feedback
- Priority updates

**Moderator → Other Agents** (on behalf of sub-agents):
- Skill requests → Librarian
- API requests → Butler
- New agent requests → Factory Manager
- Code review requests → Gatekeeper

### Benefits of Active Interaction

- **Proactive Problem Solving**: Issues identified and resolved quickly
- **Better Resource Management**: Resources allocated efficiently
- **Improved Performance**: Continuous optimization based on feedback
- **Fault Tolerance**: Quick recovery from failures
- **Learning**: Continuous learning from interactions

---

## Communication Protocols

### Inter-Agent Communication Channels

**Direct Communication**:
- Zorro ↔ Factory Manager (task delegation)
- Zorro ↔ Moderator (progress updates)
- Factory Manager ↔ Butler (API key requests)
- Factory Manager ↔ Librarian (skill requests)
- Factory Manager ↔ Security Officer (API key storage requests)
- Moderator ↔ Sub-Agents (continuous task management and monitoring)
- Moderator ↔ Librarian (skill requests for sub-agents)
- Moderator ↔ Butler (resource requests, usage data)
- Moderator ↔ Factory Manager (new agent requests)
- Moderator ↔ Janitor (cleanup requests)
- Moderator ↔ GitHub (monitoring dashboard updates)
- Sub-Agents ↔ Gatekeeper (code review requests)
- Sub-Agents ↔ Butler (API usage reports, context updates)
- Sub-Agents ↔ Librarian (skill requests during execution)
- Butler ↔ Security Officer (API key retrieval from .env)
- All Agents ↔ Security Officer (environment variable requests)

**Communication Format**:
```json
{
  "from": "agent_name",
  "to": "agent_name",
  "type": "request" | "response" | "update" | "notification",
  "payload": {},
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

---

## API Key Management Strategy

### Primary API Key (Zorro Only)
- **Access**: Exclusive to Zorro
- **Usage**: Orchestration and delegation only
- **Protection**: Never shared, never rotated, never managed by Butler
- **Monitoring**: Separate monitoring (not managed by Butler)
- **Storage**: Managed by Security Officer in .env file

### Secondary API Keys (ALL Mansion Members Except Zorro)

**CRITICAL**: Butler manages secondary API keys for **ALL mansion members EXCEPT Zorro**:
- ✅ Factory Manager
- ✅ Moderator
- ✅ Librarian
- ✅ Security Officer
- ✅ Gatekeeper
- ✅ Janitor
- ✅ All Sub-Agents

**Management Details**:
- **Storage**: API keys stored securely by Security Officer in .env file
- **Distribution**: Butler receives keys from Security Officer and manages their usage
- **Providers**: Groq, Kimi K2, and other free-tier APIs
- **Rotation**: Automatic when approaching exhaustion
- **Routing**: Open Router pattern for load balancing
- **Monitoring**: Real-time usage tracking for all agents
- **Context Management**: Context overflow prevention for all agents
- **Rate Limit Management**: Rate limit prevention for all agents

### API Key Assignment Process

**1. Initial Setup**:
- Security Officer stores all secondary API keys in .env file
- Butler reads available keys from Security Officer
- Butler maintains registry of all keys and their assignments

**2. Key Assignment**:
- When any mansion member (except Zorro) needs an API key:
  1. Request key from Butler
  2. Butler selects appropriate key from available pool
  3. Butler assigns key to requesting agent
  4. Butler tracks usage for that agent
  5. Butler monitors for rate limits and context overflow

**3. Key Rotation**:
- Butler monitors all assigned keys continuously
- When key approaches exhaustion:
  1. Butler identifies alternative key
  2. Butler notifies agent of rotation
  3. Butler reassigns new key to agent
  4. Agent seamlessly switches to new key
  5. Butler marks old key for cooldown

### Rotation Thresholds
- **Rotation (80%)**: Actively rotate to alternative API when 80% limit is reached
- **Warning (75%)**: Flagged for rotation, prepare alternative
- **Emergency (95%)**: Immediate rotation, pause requests if needed
- **Exhausted (100%)**: Key marked exhausted, all requests routed elsewhere

**CRITICAL**: Butler rotates API keys when 80% limit is reached (not 90%). This is the primary rotation threshold.

### Context & Rate Limit Management
- **Context Overflow**: Butler prevents context overflow for all agents
- **Rate Limits**: Butler prevents rate limit violations for all agents
- **Load Balancing**: Butler distributes load across all available keys
- **Monitoring**: Butler provides usage statistics to Moderator

---

## Skills Management Strategy

### Skills Sources
1. **skills.sh**: Primary skills repository
2. **clawhub.ai**: Secondary skills repository

### Skill Distribution
- Skills assigned based on PRD requirements
- Librarian matches task needs with available skills
- Skills can be added dynamically during task execution
- Librarian monitors skill effectiveness and updates

### Skill Categories
- **Core Skills**: Essential for all agents
- **Specialized Skills**: Task-specific capabilities
- **Custom Skills**: Project-specific implementations

---

## Security Considerations

### API Key Security
- Primary key: Never exposed, never logged
- Secondary keys: Encrypted storage, rotation on exposure
- Key access: Audit trail for all key access

### Code Security
- Gatekeeper reviews all code before Git push
- Security testing mandatory
- Vulnerability scanning automated
- Transaction security handled by Security Officer

### Wallet Security
- Keys stored in encrypted vault
- Multi-factor authentication
- Transaction review before signing
- Audit trail for all transactions

---

## Error Handling & Recovery

### Blocker Resolution
1. Sub-agent reports blocker to Moderator
2. Moderator classifies blocker severity
3. Moderator routes to appropriate specialist
4. Specialist provides solution
5. Sub-agent continues or task is reassigned

### API Exhaustion Recovery
1. Butler detects API near exhaustion
2. Butler rotates to alternative API
3. Sub-agents seamlessly switch APIs
4. No task interruption

### Agent Failure Recovery
1. Moderator detects agent failure
2. Moderator reports to Factory Manager
3. Factory Manager spawns replacement agent
4. Task state transferred to new agent
5. Task continues from checkpoint

---

## Performance Optimization

### Resource Management
- Butler optimizes API usage across providers
- Librarian optimizes skill distribution
- Moderator optimizes task allocation
- Janitor maintains system performance through cleanup

### Scalability
- Factory Manager can spawn multiple agents
- Teams can be formed for parallel execution
- API rotation supports high-volume operations
- Cleanup prevents resource exhaustion

---

## Monitoring & Observability

### Metrics Tracked
- API usage per provider
- Task completion rates
- Blocker frequency and resolution time
- Agent performance metrics
- Resource utilization
- Cleanup effectiveness

### Reporting
- Real-time dashboards (for Zorro)
- Regular status updates (Moderator → Zorro)
- Cleanup reports (Janitor → Moderator)
- Security audit logs (Gatekeeper, Security Officer)

---

## Future Enhancements

### Implemented Features
1. ✅ **Ant Farm Structure**: Parallel execution lanes implemented
2. ✅ **Agent Learning**: Learning system implemented for pattern recognition
3. ✅ **GitHub Monitoring**: Real-time monitoring dashboard on GitHub
4. ✅ **Context Overflow Management**: Comprehensive context management system
5. ✅ **Rate Limit Management**: Proactive rate limit prevention

### Potential Future Improvements
1. **Predictive Scaling**: Pre-spawn agents based on predicted load
2. **Advanced Routing**: ML-based API routing optimization using learning system
3. **Skill Marketplace**: Dynamic skill discovery and integration
4. **Auto-Scaling**: Automatically scale lanes based on workload
5. **Advanced Analytics**: Deep learning for task prediction and optimization
6. **Multi-Repository Support**: Support for multiple GitHub repositories
7. **Real-Time Collaboration**: Live collaboration features between agents
8. **Advanced Security**: Enhanced security features and threat detection

---

## Implementation Notes

### For New Agents
When implementing this architecture:
1. Start with Zorro (primary orchestrator)
2. Implement Butler (API management)
3. Implement Librarian (skills management)
4. Implement Factory Manager (agent creation)
5. Implement Moderator (task management)
6. Implement Gatekeeper (code review)
7. Implement Security Officer (wallet management)
8. Implement Janitor (cleanup)

### Testing Strategy
- Unit tests for each agent role
- Integration tests for inter-agent communication
- End-to-end tests for complete workflows
- Stress tests for API rotation
- Security tests for all components

---

## Glossary

- **PRD**: Product Requirements Document - Detailed task specification
- **Sub-Agent**: Specialized agent created by Factory Manager
- **Primary API**: Zorro's exclusive API key
- **Secondary API**: Sub-agent API keys managed by Butler
- **Blocker**: Issue preventing task progress
- **Checkpoint**: Milestone marker in task roadmap
- **Rotation**: Switching API keys when approaching limits

---

## Conclusion

This mansion architecture provides a robust, scalable, and maintainable framework for the Zoro agent system. The architecture includes:

### Key Features

1. **Hierarchical Structure**: Clear hierarchy with Zorro at the top, managing all mansion members
2. **Comprehensive API Management**: Butler manages ALL secondary API keys for ALL mansion members (except Zorro)
3. **Context & Rate Limit Management**: Proactive prevention of context overflow and rate limit violations
4. **Parallel Execution**: Ant Farm structure enables parallel execution lanes for increased throughput
5. **Learning System**: Adaptive intelligence that learns from patterns and improves over time
6. **Real-Time Monitoring**: GitHub-based monitoring dashboard updated in real-time by Moderator
7. **Active Agent Interaction**: Continuous, active interaction between Moderator and sub-agents
8. **Security**: Comprehensive security with Security Officer managing API keys and .env variables
9. **Resource Optimization**: Intelligent resource allocation and optimization across all agents

### Architecture Benefits

- **Scalability**: Can handle multiple tasks and agents simultaneously
- **Fault Tolerance**: Robust error handling and recovery mechanisms
- **Resource Efficiency**: Optimal use of API keys and resources
- **Learning & Adaptation**: Continuous improvement through learning system
- **Transparency**: Real-time monitoring via GitHub dashboard
- **Security**: Secure management of sensitive keys and variables
- **Maintainability**: Clear separation of concerns and well-defined interfaces

### For New Agents Implementing This Architecture

This document is designed to be fully understandable by AI agents. Each section provides:
- Clear role definitions
- Detailed responsibilities
- Step-by-step workflows
- Data structures
- Interaction patterns
- Implementation guidelines

Agents should:
1. Read this document completely
2. Understand the hierarchy and relationships
3. Implement agents according to their role specifications
4. Follow the communication protocols
5. Adhere to the workflows defined
6. Use the data structures provided
7. Integrate with the learning system
8. Contribute to the monitoring dashboard

For questions or clarifications, refer to the specific agent sections above or consult the workflow diagrams.

---

**Document Version**: 2.0  
**Last Updated**: 2026-02-10  
**Maintained By**: Zoro Architecture Team  
**Key Updates**: Added Ant Farm structure, Learning System, GitHub Monitoring, Context/Rate Limit Management, Enhanced Security Officer, Detailed Agent Interactions
