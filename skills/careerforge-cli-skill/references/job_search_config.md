# Job Search Configuration

## Default Filters

### Location
- **Primary:** Tel Aviv, Israel
- **Backup:** Israel (if no Tel Aviv results)

### Job Title Keywords
Default search terms:
- AI project manager
- AI automation
- AI enabler
- AI product manager
- AI technical lead
- AI implementation
- AI operations
- AI specialist
- AI coordinator
- Data analyst
- Marketing analyst
- Product analyst
- Business analyst

### Experience Level
- **Target:** 2-4 years
- **Filter out:** Senior, Lead, Head, Director, Principal positions

### Work Mode
- **Default:** In-person only (not remote)
- **Options:** Remote, Hybrid, In-person

### Exclusions

**Keywords to exclude:**
- Sales
- Account executive
- Business development
- SDR/BDR
- Account manager

**Companies to exclude (reposters):**
- Dialog
- Gotfriends
- Malamteam / מלם תים / מלם

## Cron Schedule

### Default
- **Hours:** 8:00 - 18:00 (Israel time)
- **Days:** Sunday - Thursday (0-4)
- **Timezone:** Asia/Jerusalem
- **Frequency:** Hourly

### Customization Options
Users can customize:
- Active hours (e.g., 9-17 for 9 AM - 5 PM)
- Days of week (e.g., 1-5 for Monday-Friday)
- Timezone

## LLM Configuration

### Default
- **Provider:** Google
- **Model:** Gemini 2.5 Pro
- **API Key:** GEMINI_API_KEY environment variable

### Alternative Options
Users can configure:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Custom API endpoints

## Output

### Job Listings
Jobs are sent to Telegram group with:
- Job title
- Company name
- Location
- Job URL
- Instructions to reply "CV" for tailored resume

### CV Generation
When user replies "CV":
1. Extract job details
2. Run CareerForge CLI
3. Generate tailored CV (~$0.04-0.05 cost)
4. Send PDF to user

## File Locations

```
workspace/
├── careerforge_config.json     # User's configuration
├── CV_Master/
│   └── master_resume.md        # User's master resume
├── cvs/                        # Generated CVs
└── applications.json           # Application tracking
```