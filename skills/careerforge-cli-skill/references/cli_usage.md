# CareerForge CLI Usage Guide

## Overview

CareerForge CLI generates tailored CVs using Google's Gemini 2.5 Pro with a Writer+Judge pattern for high-quality, ATS-optimized resumes.

## Installation

```bash
cd careerforge-cli
npm install
```

## Configuration

Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
GEMINI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

Create a job JSON file:
```json
{
  "title": "Data Analyst",
  "company": "Example Corp",
  "description": "Full job description here..."
}
```

Run the CLI:
```bash
node generate_cv_from_json.js job.json
```

### Output

CVs are saved to:
- `cvs/AlonTevet_Res_[Company].html`
- `cvs/AlonTevet_Res_[Company].pdf`

## How It Works

### Step 1: Writer (Gemini 2.5 Pro)
Generates initial CV based on:
- Your master resume
- Job description
- One-page A4 format requirement
- ATS optimization

### Step 2: Judge (Gemini 2.5 Pro)
Refines the CV by:
- Checking for completeness
- Injecting relevant keywords
- Removing fluff words
- Ensuring proper HTML structure

### Step 3: PDF Conversion
Converts HTML to PDF using Playwright

## Cost

~$0.04-0.05 per CV (Writer + Judge)

## Tips

1. **Job Description Quality**: Better job descriptions = better CVs
2. **Master Resume**: Keep it updated with latest achievements
3. **Review**: Always review generated CVs before sending
4. **Customization**: Edit the HTML directly for final tweaks

## Troubleshooting

### "Missing required arguments"
- Check that job.json has all required fields: title, company, description

### "No Gemini API key found"
- Set GEMINI_API_KEY environment variable
- Or create .env file with the key

### PDF conversion fails
- Ensure Playwright is installed: `npm install`
- Install browser binaries: `npx playwright install chromium`