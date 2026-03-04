# Figma Skill for OpenClaw

A specialized AgentSkill for [OpenClaw](https://github.com/openclaw/openclaw) that enables agents to interact with the Figma REST API. This skill allows the agent to navigate team structures, read design data, export assets, and track discussions.

## Features

- **Identity Verification**: Retrieve authenticated user information.
- **Team Navigation**: List projects within a team and files within a project.
- **File Inspection**: Fetch full document JSON trees to analyze pages, frames, and layers.
- **Asset Export**: Export specific layers or components as PNG, JPG, SVG, or PDF at custom scales.
- **Collaboration Tracking**: Retrieve recent comments from any design file.

## Setup

### Prerequisites
1. A **Figma Personal Access Token (PAT)**. You can generate one in your Figma account settings.
2. Python 3 installed on the host machine.

### Configuration
The skill **requires** the Figma token to be available in the environment:
```bash
export FIGMA_TOKEN="your_figma_pat_here"
```

**⚠️ Security Note:** The `FIGMA_TOKEN` is a sensitive API credential. The skill uses it to authenticate with the Figma API and download images from URLs returned by Figma. Ensure:
- Only install this skill from trusted sources
- Do not share your `FIGMA_TOKEN` with untrusted users
- The token should be treated like a password

## Usage

The core functionality is provided by `scripts/figma_tool.py`.

### 1. Get Current User Info
```bash
python scripts/figma_tool.py get-me
```

### 2. List Projects in a Team
```bash
python scripts/figma_tool.py get-team-projects <team_id>
```

### 3. List Files in a Project
```bash
python scripts/figma_tool.py get-project-files <project_id>
```

### 4. Read File Content
```bash
python scripts/figma_tool.py get-file <file_key>
```

### 5. Get File Comments
```bash
python scripts/figma_tool.py get-comments <file_key>
```

### 6. Export Layers
```bash
python scripts/figma_tool.py export <file_key> --ids <layer_id1,layer_id2> --format png --scale 2.0
```

## Important Behavioral Notes

**File Writing:** When exporting layers or components, the skill writes image files to the current working directory with names like `figma_export_<layer_id>.<format>`. Users should be aware of:
- Where exported files will be written
- That file exports will follow image URLs provided by the Figma API
- Regular cleanup of exported files to avoid disk clutter

**API Scope:** This skill communicates only with the official Figma API (`api.figma.com`). It does not:
- Read unrelated files from your system
- Write data to arbitrary endpoints
- Modify Figma files (read-only operations)
- Request additional credentials or environment variables

## Integration with OpenClaw

This repository follows the AgentSkill structure. When integrated into an OpenClaw instance, the agent can automatically trigger these tools based on natural language requests such as:
- "Check if there are any new comments on the CherishCRM design."
- "Export the login button from the Figma file `uxkr...` as an SVG."
- "List all files in my team project."

## License
MIT
