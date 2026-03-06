# Cetus SDK Skill for OpenClaw

OpenClaw skill for integrating all Cetus Protocol SDK v2 modules on Sui.
OpenClaw 技能包，整合 Sui 鏈上 Cetus Protocol SDK v2 全部模組。

## Install 安裝

```bash
npx clawhub install cetus
```

## Modules 模組

CLMM, DLMM, Vaults, Farms, xCETUS, Limit, Burn, DCA, Zap, Aggregator

## Usage 使用方式

See [SKILL.md](./SKILL.md) for full API reference and code examples.
完整 API 參考與範例請見 [SKILL.md](./SKILL.md)。

## Contact 聯繫
+ Github repo: https://github.com/k66inthesky/cetus
+ Author: @k66inthesky https://github.com/k66inthesky/

---
## AI tool Desclaimer AI工具聲明
+ 參加Sui vibe Hackathon
+ 開發工具: 只用Claude Code CLI
+ 模型：只用Opus 4.6
+ 對話：
```
(在Claude Code CLI下使用/compact)
 Compact summary
  ⎿  This session is being continued from a previous conversation that ran out of context. The summary below covers the
     earlier portion of the conversation.

     Analysis:
     Let me analyze the conversation chronologically:

     1. This is a continued session from a previous conversation that ran out of context. The summary from the previous
     conversation provides the bulk of the history.

     2. From the previous conversation summary:
        - User wanted to build an OpenClaw SKILL.md integrator for Cetus Protocol SDK v2 on Sui blockchain
        - Covers 11 SDK modules: clmm, vaults, farms, xcetus, limit, burn, dca, zap, dlmm, aggregator, common
        - User provided all GitHub README URLs for each SDK
        - All 11 READMEs were fetched and consolidated into a single SKILL.md
        - A bilingual README.md was also created
        - Both files are complete
3. Files and Code Sections:
        - `/Users/k66/cetus/SKILL.md` (17,271 bytes, ~760 lines)
          - Core deliverable: consolidated English-only API reference for all 11 Cetus SDK modules
          - Contains: installation, initialization, API methods, code examples, common patterns, and package reference
     table
          - Was fetched from 11 separate GitHub raw README URLs and merged
        - `/Users/k66/cetus/README.md` (659 bytes)
          - Bilingual (EN/CN) project README
          - Each language section under 100 words
          - Install command: `npx clawhub install cetus`
          - Lists all modules and links to SKILL.md for full reference
          - Content:
            ```
            # Cetus SDK Skill for OpenClaw
            OpenClaw skill for integrating all Cetus Protocol SDK v2 modules on Sui.
            ## Install
            npx clawhub install cetus
            ## Modules
            CLMM, DLMM, Vaults, Farms, xCETUS, Limit, Burn, DCA, Zap, Aggregator
            ## Usage
            See SKILL.md for full API reference and code examples.
            ---
            # Cetus SDK Skill for OpenClaw (中文)
            OpenClaw 技能包，整合 Sui 鏈上 Cetus Protocol SDK v2 全部模組。
            ## 安裝
            npx clawhub install cetus
            ## 模組
            CLMM、DLMM、Vaults、Farms、xCETUS、Limit、Burn、DCA、Zap、Aggregator
            ## 使用方式
            完整 API 參考與範例請見 SKILL.md。
            ```
        - `/Users/k66/cetus/.claude/settings.local.json` (147 bytes)
          - Claude Code local project permissions
          - Allows `git status` in this directory and WebFetch from `raw.githubusercontent.com`
          - Content:
            ```json
            {
              "permissions": {
                "allow": [
                  "Bash(git -C /Users/k66/cetus status:*)",
                  "WebFetch(domain:raw.githubusercontent.com)"
                ]
              }
            }
            ```

     4. Errors and fixes:
        - In the previous session, web search was rejected by user — user then directly provided all GitHub README URLs
     instead
        - Directory was empty initially — no code to explore, all content sourced from GitHub READMEs
        - SKILL.md was already fully in English when user requested English-only conversion, so no changes were needed

     5. Problem Solving:
        - Fetched all 11 README files in parallel via WebFetch from raw GitHub URLs
        - Consolidated disparate SDK docs into unified SKILL.md with consistent structure
        - Created bilingual README.md meeting all constraints (word count, install command, summary)
        - All requested tasks have been completed successfully

     6. All user messages:
        - (From previous session) "將對話打包的指令叫什麼" — asking about compact command
        - (From previous session) "share 呢" — asking about share command
        - (From previous session) "我想做一個cetus的OpenClaw SKILL.md的整合器..." — initial project request
        - (From previous session) Provided all 11 GitHub README URLs and said:
     "請你讀這些sdk的readme把它們只寫進一個SKILL.md"
        - (From previous session) "1.請寫一個READMD.md(中英文版都要，摘要一句話中英文，安裝寫npx clawhub install
     cetus，中文或英文總內文不要超過100字) 請將SKILL.md內容全改成英文"
        - (From previous session) "將我跟你的對話/compact打包"
        - (Current session) Ran `ls -la` command
        - (Current session) ".claude有什麼東西" — asking what's inside the .claude directory
