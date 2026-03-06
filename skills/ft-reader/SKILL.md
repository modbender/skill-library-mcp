---
name: Financial Times Deep Reader (ft-reader)
description: Use this skill to perform deep, structured, and bilingual analysis
  of top articles from Financial Times (ft.com). This skill automates login,
  article selection, and high-quality summarization suita...
---

# Financial Times Deep Reader (ft-reader)

Use this skill to perform deep, structured, and bilingual analysis of top articles from Financial Times (ft.com). This skill automates login, article selection, and high-quality summarization suitable for academic and professional use.

## Capabilities
- **Automated Access**: Logs into FT.com using stored credentials via Browser tool.
- **Strategic Selection**: Identifies "Most Read" based on user preference.
- **Bilingual Synthesis**: Provides high-fidelity English-Chinese summaries with a focus on core arguments.
- **Academic Rigor**: Extracts specific data, quotes, and important charts in the article.

## Configuration & Credentials
- **Browser Profile**: Use `openclaw` profile to maintain session persistence.
- **Credentials**:
  - User: `xxxxxx`
  - Pass: `xxxxxx`

## Workflow (Mandatory Steps)

### Phase 1: Authentication & Navigation
1. Open `https://www.ft.com/login`.
2. Enter email and password.
3. Navigate to the homepage or a specific section requested by the user.

### Phase 2: Content Extraction
1. Use `evaluate` to identify the top N articles from the homepage (targeting `.o-teaser__heading` or most-read sections).

2. For each target article:
   - Navigate to the article URL.
   
   - Use `evaluate` with the following JavaScript to extract clean content:
     ```javascript
     () => {
       const title = document.querySelector('h1')?.innerText;
       const standfirst = document.querySelector('div[class*="standfirst"]')?.innerText;
       const paragraphs = Array.from(document.querySelectorAll('div[class*="article-body"] p, article p'))
         .map(p => p.innerText.trim())
         .filter(text => text.length > 0);
       return { title, summary: standfirst, content: paragraphs.join('\n\n') };
     }
     ```

### Phase 3: Analysis & Reporting
For each article, generate a report (around 600 words) using the following structure:
- **Title (Bilingual)**
- **Core Opinion (Bilingual)**
- **Arguments (Bilingual)**
- **Conclusion (Bilingual)**

## Constraints
- **Style**: Professional, academic, and fluff-free (follow SOUL.md).
- **Language**: Always provide both English and Chinese translations for technical terms and core ideas.
- **Independent Reading**: Treat each article as a standalone piece unless cross-analysis is requested.
- **Token Management**: If many articles are requested, split the delivery into multiple turns to avoid truncation.

## Usage Examples
- "Lulu, use ft-reader to analyze the top 3 Most Read articles from today."
- "Perform a deep dive into the top story on FT regarding AI productivity using the ft-reader skill."
