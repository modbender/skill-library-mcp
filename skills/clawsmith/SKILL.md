---
name: clawsmith
description: Create, audit and publish production-ready OpenClaw skills with one command. 10 modes included.
version: "1.0.0"
metadata: {"openclaw":{"emoji":"hammer","requires":{"bins":["clawhub","git"]},"install":[{"kind":"node","package":"clawhub","bins":["clawhub"],"label":"Install ClawHub CLI"}]}}
---

# ClawSmith v1.0 - The Skill That Builds All Skills

ClawSmith is your personal skill creation assistant for OpenClaw. Tell it what skill you want, and it generates a complete, publish-ready SKILL.md with correct frontmatter, validated metadata, optimized descriptions, and security-checked instructions. No guesswork. No rejected submissions. No suspicious flags.

Built after the ClawHavoc crisis where 341 malicious skills were discovered on ClawHub, ClawSmith ensures every skill it generates has proper metadata declarations that match its actual behavior.

## When to Use This Skill

Use ClawSmith whenever you or the user says anything like:

- "Create a new skill" or "Build me a skill for X"
- "Help me write a SKILL.md"
- "I want to publish a skill on ClawHub"
- "Scaffold a new OpenClaw skill project"
- "Optimize my existing skill" or "Improve my skill"
- "Check if my skill metadata is correct"
- "Generate a skill from this idea"
- "Create multiple skills from a list"
- "What skills are missing on ClawHub?"
- "Make my skill pass ClawHub security review"
- "Convert my script into an OpenClaw skill"
- "Create a skill template for a specific category"
- "Review my skill for publishing issues"
- "I need a skill that does X, build the whole thing"
- "Help me publish my skill to ClawHub"

If the user wants to create, optimize, validate, or publish any OpenClaw skill, ClawSmith handles it.

## Advanced Modes

ClawSmith includes 10 specialized modes covering every stage from idea to published skill:

**Mode 1: Security Guardian Pro**
Validates any SKILL.md against ClawHub security requirements. Checks that every binary mentioned in instructions is declared in metadata requires.bins. Checks that every environment variable referenced is declared in requires.env. Flags blind curl-to-bash patterns, hardcoded credentials, eval calls, and undeclared network tool usage. Generates a safety score from 0 to 100. Auto-suggests fixes for every issue found.

**Mode 2: ClawHub Intelligence**
Analyzes what skills currently exist on ClawHub for a given category. Identifies gaps where no skill exists, categories with outdated skills, and trending topics with high demand. Helps you decide what to build next for maximum installs and visibility.

**Mode 3: Interactive Skill Architect**
Wizard mode that walks you through skill creation with smart questions. Asks what the skill does, who the target user is, what binaries it needs, what environment variables it requires, and what the step-by-step instructions should be. Outputs a complete SKILL.md at the end.

**Mode 4: Skill Optimizer 10x**
Takes an existing SKILL.md and improves it. Rewrites the description for better ClawHub search ranking. Adds any missing frontmatter fields. Restructures instructions for clearer agent comprehension. Ensures metadata declarations match instruction content. Reduces token count while keeping clarity.

**Mode 5: Multi-Language Code Genie**
Generates helper scripts in Node.js, Python, TypeScript, or Bash that a skill can reference. Adds proper shebang lines, error handling, and exit codes. Ensures generated code does not contain eval, blind downloads, or hardcoded secrets. Declares all required binaries in the skill frontmatter.

**Mode 6: Template Factory**
Provides 25 production-tested SKILL.md templates organized by category. Categories include Productivity, DevOps, Communication, Finance, AI and ML, Data Processing, Security, Smart Home, Social Media, Content Creation, Developer Tools, System Admin, API Integration, Monitoring, and Education. Each template has correct frontmatter and example instructions.

**Mode 7: Auto Marketing Machine**
Generates promotional content for your published skill. Creates a ClawHub-optimized description with search-friendly keywords. Writes a GitHub README with badges and install commands. Drafts an X and Twitter launch thread. Creates a Product Hunt style description. All generated from your SKILL.md content.

**Mode 8: One-Click Full Pipeline**
Give it one sentence describing your skill idea. ClawSmith generates the complete folder structure, writes the SKILL.md with proper frontmatter, validates all metadata declarations, checks security requirements, generates a README, and provides the exact publish command. Idea to publish-ready in one interaction.

**Mode 9: Self-Evolve Mode**
Reviews your published skill and suggests improvements based on ClawHub best practices. Recommends better description keywords, missing features that users might expect, security updates for new ClawHub requirements, and version bump guidance. Helps keep your skill ranking high.

**Mode 10: Bulk Creator**
Takes a list of skill ideas (5, 10, or more) and generates individual SKILL.md files for each one. Each skill gets a unique description, proper frontmatter with correct declarations, and validated metadata. Useful for publishing a batch of related skills to dominate a category.

## How to Use ClawSmith

**Quick Start:**

Step 1: Install ClawSmith.
Run clawhub install clawsmith in your terminal.

Step 2: Tell your OpenClaw agent what skill you want to create.
Example: "Create a skill that manages my Todoist tasks from the command line"

Step 3: ClawSmith generates the complete SKILL.md with frontmatter, instructions, and metadata.

Step 4: Review the output. Check that the description, bins, and env vars are correct for your use case.

Step 5: Save the SKILL.md to your skill folder.
Run mkdir -p ~/.openclaw/skills/your-skill-name and save the file there.

Step 6: Publish to ClawHub.
Run clawhub publish ~/.openclaw/skills/your-skill-name --version 1.0.0

**Detailed Workflow:**

1. Describe your skill idea. Be specific about what it does, who uses it, and what tools or APIs it needs.

2. Choose your mode. Say "create a skill" for quick generation, "clawsmith wizard" for guided creation, or "clawsmith audit" to validate an existing skill.

3. Review the generated SKILL.md. Check the frontmatter for correct name, description under 160 characters, version in quotes, and metadata with all required bins and env vars declared.

4. Validate metadata. ClawSmith automatically checks that every binary and env var mentioned in instructions is declared in the frontmatter. This prevents the "Suspicious" flag on ClawHub.

5. Test locally. Copy the skill to your workspace skills folder and start a new OpenClaw session to verify it loads correctly.

6. Publish. Run clawhub publish with the path to your skill folder. ClawSmith ensures your skill meets all ClawHub format and content requirements before you publish.

## Examples

**Example 1: Creating a Skill from an Idea**

User: Create a skill that monitors server CPU and RAM and alerts via Telegram when usage is high.

ClawSmith generates:

Skill name: server-monitor-alert
Description: Monitor server CPU and RAM usage. Send Telegram alert when thresholds exceeded.
Frontmatter declares: curl in requires.bins, TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in requires.env
Instructions include: step-by-step monitoring commands, threshold configuration, alert message format, and error handling for missing token.
Metadata validation: All bins and env vars match between instructions and frontmatter. No undeclared dependencies.

**Example 2: Validating Existing Skill Metadata**

User: Check if my skill at ~/.openclaw/skills/my-tool has correct metadata.

ClawSmith reads the SKILL.md and reports:
- Line 15 references wget but requires.bins does not include wget. Fix: add wget to bins.
- Line 23 uses API_KEY variable but requires.env does not declare it. Fix: add API_KEY to env.
- Line 8 contains curl piped to bash. Fix: replace with safe download-then-verify pattern.
- Description is 195 characters. Fix: shorten to under 160 characters.
- Validation score: 58 out of 100. After fixes: 97 out of 100.

**Example 3: Finding ClawHub Gaps**

User: What skills are missing on ClawHub for DevOps engineers?

ClawSmith analyzes the DevOps category and reports:
- Terraform drift detection: 0 existing skills, high demand. Recommendation: build first for first-mover advantage.
- Kubernetes pod health alerts: 2 existing but outdated. Recommendation: build modern replacement.
- Docker compose optimizer: 0 existing skills. Recommendation: high value, medium effort.
- CI/CD pipeline analyzer: 1 existing but GitHub Actions only. Recommendation: add GitLab and Jenkins support.

**Example 4: Bulk Creating Skills**

User: Create skills for pomodoro timer, habit tracker, standup generator, meeting summarizer, and code review checklist.

ClawSmith generates 5 individual SKILL.md files:
1. pomodoro-timer: Timer management with configurable intervals. No external dependencies.
2. habit-tracker: Daily habit logging with streak tracking. Requires local file read and write only.
3. standup-generator: Creates structured standup updates from git log. Declares git in bins.
4. meeting-summarizer: Formats meeting notes into action items. No external dependencies.
5. code-review-checklist: Generates review checklists from diff output. Declares git in bins.
All 5 pass metadata validation with scores of 95 to 100.

**Example 5: Full Pipeline from Idea to Publish Command**

User: Build me a complete skill for translating clipboard text between languages.

ClawSmith runs full pipeline:
1. Generates skill name: clipboard-translator
2. Writes description: Translate clipboard text between languages using the terminal. (64 characters)
3. Creates frontmatter with pbpaste in bins for macOS clipboard access
4. Writes step-by-step instructions for reading clipboard, detecting language, translating, and outputting result
5. Validates all metadata: 100 out of 100
6. Generates README content
7. Provides publish command: clawhub publish ~/.openclaw/skills/clipboard-translator --version 1.0.0

## Security Practices

ClawSmith generates skills that follow ClawHub security requirements:

- Every binary referenced in instructions is declared in metadata requires.bins. This prevents metadata mismatch warnings from ClawHub security analysis.

- Every environment variable referenced in instructions is declared in metadata requires.env. This ensures ClawHub knows what credentials the skill needs.

- No blind curl or wget pipes to bash or sh. Generated instructions use safe patterns where files are downloaded first, verified, then executed separately.

- No hardcoded API keys, tokens, passwords, or secrets anywhere in generated content. All credentials are referenced through environment variable names declared in frontmatter.

- No eval, exec, Function constructor, or subprocess.call with shell equals true in generated helper scripts. Dynamic code execution patterns are avoided.

- No undeclared network access. If instructions reference any tool that makes HTTP requests, that tool is declared in requires.bins.

- Generated skills only read and write within their own skill directory or clearly documented user paths. No access to openclaw configuration files or system directories.

- Descriptions are written as factual trigger phrases, not marketing promises. This prevents the description from claiming capabilities that the metadata does not support.

- All generated frontmatter uses single-line JSON format for the metadata field, which is the format ClawHub parser handles most reliably.

- Version numbers always use semver format with quotes to prevent YAML parsing issues.

## Best Practices in Every Generated Skill

1. Description is a clear trigger phrase under 160 characters. Written in the exact words users type so the OpenClaw skill matcher activates correctly.

2. Frontmatter includes all required fields: name, description, version in quotes, and metadata with emoji, requires listing all bins and env vars.

3. Instructions follow numbered step-by-step format that the LLM can execute without ambiguity.

4. Error handling is included for common failures: missing binary, missing env var, network timeout, invalid input.

5. Token efficiency is prioritized. Descriptions are concise. Instructions use minimal words with maximum clarity to reduce per-turn prompt cost.

6. Each generated skill has single responsibility. One skill does one thing well rather than combining unrelated features.

7. Environment variables include documentation about what they are, where to get them, and how to set them.

8. Version starts at 1.0.0 with proper semver. Guidance is provided for when to bump major, minor, and patch versions.

9. A README template is generated alongside every skill for GitHub publishing.

10. Metadata validation runs automatically before any skill is considered complete. No skill passes ClawSmith review if its metadata does not match its instructions.

## Pro Tips

- Start with wizard mode if you are new to skill creation. Say "clawsmith wizard" and answer the questions. It handles frontmatter, metadata, and validation automatically.

- Always validate before publishing. Say "clawsmith audit" with your skill path to catch metadata mismatches before ClawHub flags them as suspicious.

- Use ClawHub Intelligence before building. Say "clawsmith research" with a topic to find gaps instead of building something that already exists.

- Keep descriptions factual. ClawHub security analysis compares your description against your metadata. If the description promises network access but metadata does not declare network tools, the skill gets flagged.

- Use bulk creator to publish a batch of related skills and establish presence in a category.

- Run optimizer on older published skills to update them with better descriptions and current metadata requirements.

- Generate marketing content after publishing to promote your skill on social media and attract installs.

Built by Manish Pareek. @mkpareek0315 on ClawHub. @Mkpareek19_ on X.
