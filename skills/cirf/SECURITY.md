# Security & Permissions

## Overview

**CIRF (Crypto Interactive Research Framework)** is a prompt engineering framework designed for conducting comprehensive crypto market research with AI assistance.

---

## What is CIRF?

CIRF is **NOT a traditional software application** - it is a **prompt engineering framework** written entirely in natural language (YAML + Markdown files, zero code).

### Core Components

```
framework/
├── agents/*.yaml           # AI persona definitions
├── workflows/*/           # Research methodologies
│   ├── objectives.md      # What to research
│   └── template.md        # How to format output
└── components/*.md        # Execution protocols
```

**How it works:**
1. User activates an AI agent (e.g., Research Analyst)
2. AI reads YAML/Markdown files to understand persona and methodology
3. AI conducts research following structured instructions
4. AI generates formatted research outputs

**Think of it as:** Research SOPs (Standard Operating Procedures) that AI assistants follow to conduct professional-grade crypto analysis.

---

## Required Permissions

### 1. File System Access - READ

**Scope:**
```
framework/agents/*.yaml
framework/workflows/**/*.md
framework/components/*.md
framework/guides/*.md
framework/core-config.yaml
framework/_workspace.yaml
```

**Purpose:**
- Read AI agent persona definitions
- Read research methodology instructions
- Read output templates
- Load user preferences and configuration

**Why needed:**
CIRF is a prompt engineering framework - AI must read these instruction files to understand how to conduct research. This is the core functionality.

**Data flow:**
```
Framework files → AI reads → AI understands how to work
```

### 2. File System Access - WRITE

**Scope:**
```
workspaces/{project-id}/workspace.yaml
workspaces/{project-id}/documents/
workspaces/{project-id}/outputs/**/*.md
```

**Purpose:**
- Create isolated workspace for each research project
- Save research outputs (reports, analyses)
- Manage project configuration

**Why needed:**
Research framework must save outputs somewhere. All writes are confined to `workspaces/` directory within the project.

**Data flow:**
```
AI conducts research → Generates report → Saves to workspaces/{project}/outputs/
```

### 3. Network Access - WebSearch

**Purpose:**
- Search for current crypto market data
- Find news, trends, and market developments
- Gather information for research

**Example queries:**
- "Bitcoin ETF approval news 2024"
- "Ethereum scaling roadmap"
- "DeFi TVL statistics"

**Why needed:**
Cannot conduct crypto market research without access to current market data, news, and public information.

**Data flow:**
```
Research question → WebSearch → Public data → Synthesized into report
```

### 4. Network Access - WebFetch

**Purpose:**
- Fetch specific documents (whitepapers, documentation, blog posts)
- Read protocol specifications
- Access public blockchain data sources

**Example URLs:**
- Protocol documentation sites
- GitHub repositories (for technical analysis)
- Official project blogs
- Public blockchain explorers

**Why needed:**
Crypto research requires reading primary sources like whitepapers, technical docs, and official announcements.

**Data flow:**
```
Document URL → WebFetch → Content → Analyzed for research
```

---

## What CIRF Does NOT Do

### ❌ No Data Exfiltration
- Does not send user data to unauthorized external servers
- Does not transmit research outputs to third parties
- All outputs saved locally in `workspaces/` directory
- WebSearch/WebFetch only used for gathering PUBLIC research data

### ❌ No System Modifications
- Does not modify system files
- Does not install background processes
- Does not create persistence mechanisms
- Only operates within project directory

### ❌ No Remote Control
- Does not connect to command & control servers
- Does not receive remote commands
- Does not establish backdoors
- All instructions come from LOCAL framework files

### ❌ No Credential Harvesting
- Does not collect API keys, passwords, or credentials
- Does not access sensitive system data
- Does not scan for private information

### ❌ No Obfuscation
- All framework files are plain text (YAML/Markdown)
- Zero binary code
- Zero encryption or obfuscation
- Fully readable and modifiable by users

---

## Transparency & Verification

### All Code is Readable

Every instruction in CIRF is plain text:

```
framework/agents/research-analyst.yaml  ← AI persona definition (YAML)
framework/workflows/*/objectives.md     ← Research methodology (Markdown)
framework/components/*.md               ← Execution protocols (Markdown)
```

**Anyone can:**
- Read every instruction
- Understand what AI will do
- Modify behavior by editing files
- Verify no malicious content

### No Hidden Behavior

Unlike malware that:
- ❌ Hides code in encrypted binaries
- ❌ Obfuscates logic
- ❌ Uses stealth techniques

CIRF:
- ✅ All instructions in plain text
- ✅ Fully transparent design
- ✅ User-modifiable
- ✅ Open source

### Data Flow is Transparent

```
User request
  ↓
AI reads framework files (LOCAL)
  ↓
AI conducts research (WebSearch/WebFetch PUBLIC data)
  ↓
AI generates report
  ↓
Output saved to workspaces/ (LOCAL)
```

No step involves:
- Sending user data to unauthorized servers
- Hidden network connections
- Unauthorized data access

---

## Security Best Practices

### For Users

1. **Review framework files** before use
   - All instructions are readable YAML/Markdown
   - Verify no unauthorized endpoints
   - Check workspace paths are correct

2. **Monitor workspace directory**
   - All outputs saved to `workspaces/`
   - Review what's being saved
   - Delete projects when done

3. **Understand permissions**
   - Framework needs file read/write for workspace management
   - Framework needs network access for research
   - All permissions are for stated functionality

### For Platform Reviewers

1. **This is a prompt engineering framework**
   - "Prompt injection" detection is a FALSE POSITIVE
   - Instructions for AI are the framework's PURPOSE
   - Designed to GUIDE AI behavior, not HIJACK it

2. **Network access is essential**
   - Crypto research requires market data access
   - WebSearch/WebFetch used for PUBLIC data gathering
   - No unauthorized data transmission

3. **File operations are legitimate**
   - Workspace management for research projects
   - Similar to any productivity tool
   - All operations within project scope

4. **Verify by inspection**
   - All code is plain text YAML/Markdown
   - No binary executables
   - No obfuscation
   - Fully transparent design

---

## Framework Architecture

### Design Principles

1. **Transparency First**
   - All instructions in human-readable format
   - No hidden logic or obfuscated code
   - Users can audit everything

2. **Least Privilege**
   - Only accesses necessary files
   - Workspace writes confined to `workspaces/`
   - Network access only for research purposes

3. **User Control**
   - Users can modify any instruction
   - Users decide when to activate framework
   - Users control what research is conducted

4. **No Persistence**
   - Framework only active during AI session
   - No background processes
   - No system-level modifications

### Security by Design

```
┌─────────────────────────────────────────────┐
│  User activates framework                   │
│  (explicit action required)                 │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  AI reads LOCAL framework files             │
│  (plain text YAML/Markdown)                 │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  AI conducts research                       │
│  (WebSearch/WebFetch PUBLIC data)           │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  AI saves output to workspaces/             │
│  (user's local directory)                   │
└─────────────────────────────────────────────┘
```

**No step involves:**
- Unauthorized data access
- Hidden network connections
- System modifications
- Remote control

---

## Conclusion

**CIRF is a legitimate research tool that may be flagged by automated security scanners due to its novel architecture as a prompt engineering framework.**

### Key Points

1. ✅ **Not malware** - Framework for AI-assisted crypto research
2. ✅ **Transparent design** - All code is readable plain text
3. ✅ **Required permissions** - File system and network access for research functionality
4. ✅ **No malicious behavior** - No data exfiltration, no system modifications, no remote control
5. ✅ **False positive** - Security scanners don't yet recognize prompt engineering frameworks as legitimate

### Safe to Use

CIRF is safe because:
- All behavior is transparent and documented
- No hidden functionality
- Users maintain full control
- Open source and auditable
- Designed for legitimate research purposes

---

**Framework Version:** 1.0.0
**Last Updated:** 2025-02-09
**Created by:** [Kudō](https://x.com/kudodefi)

---

## Appendix: Technical Details

### File Manifest

All framework files and their purposes:

```
framework/
├── core-config.yaml              # User preferences, workflow registry
├── _workspace.yaml               # Workspace template
├── agents/
│   ├── research-analyst.yaml     # Market research persona
│   ├── technology-analyst.yaml   # Technical analysis persona
│   ├── content-creator.yaml      # Content creation persona
│   └── qa-specialist.yaml        # Quality assurance persona
├── workflows/
│   ├── sector-overview/          # Market sector analysis
│   ├── competitive-analysis/     # Competitor comparison
│   ├── project-snapshot/         # Quick project overview
│   └── [14 more workflows]       # Various research methodologies
├── components/
│   ├── agent-init.md             # Agent initialization protocol
│   ├── workflow-init.md          # Workflow setup protocol
│   └── workflow-execution.md     # Research execution protocol
└── guides/
    ├── research-methodology.md   # How to conduct research
    ├── output-standards.md       # Output quality standards
    └── [more guides]             # Best practices and guides
```

**Total files:** ~100 YAML/Markdown files
**Total code:** 0 lines (all natural language)
**Binary files:** 0

### Network Endpoints

CIRF only accesses:
- Public web search (via AI assistant's WebSearch capability)
- Public websites (via AI assistant's WebFetch capability)
- No custom endpoints
- No proprietary servers
- No data collection services

### Data Storage

All data stored locally:
```
workspaces/
└── {project-id}/
    ├── workspace.yaml        # Project configuration
    ├── documents/            # User-provided source materials
    └── outputs/              # Generated research reports
```

**No cloud storage**
**No external databases**
**No telemetry**
