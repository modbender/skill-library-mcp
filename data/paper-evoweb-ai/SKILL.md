---
name: Scientific Article PDF Generator
description: Generate publication-ready scientific articles in PDF format with AI-powered research and citations
homepage: https://paper.evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=paper&utm_content=v1.0.0
metadata: {"clawdbot":{"emoji":"📄","requires":{"bins":[],"env":["EVOWEB_API_KEY"]}}}
---

# Paper.EvoWeb.ai Scientific Article PDF Generator

Generate scientific articles in PDF format with AI-powered content enrichment, citations, and professional formatting.

## Overview

Paper.EvoWeb.ai transforms draft text and product information into publication-ready scientific articles. The system enriches your content with research, adds proper citations, generates visualizations, and exports a professionally formatted PDF document.

**Perfect for:** Scientific papers, product research articles, white papers, technical documentation

**API Base URL:** `https://paper.evoweb.ai`

## Authentication

Get your API key at https://hub.oto.dev/app/register?utm_source=claw&utm_medium=skill&utm_campaign=paper&utm_content=v1.0.0

**Important:** After registration, user MUST confirm the email.

The API Key will be displayed in the Dashboard under the "API Key Settings" section.

Include this header in all requests:
```
Access-Token: your-api-key-here
```

## How It Works

The workflow is straightforward:

1. **Submit** - Send article parameters including title, product info, and draft text
2. **Generate** - AI enriches content with research, citations, and formatting
3. **Download** - Receive PDF file automatically

Typical generation time: **2-5 minutes**

## API Endpoints

### Generate Scientific Article PDF

**POST** `/`

Generates a scientific article in PDF format from provided text and product information. The PDF file will be returned as a binary response with automatic browser download.

**Request Headers:**
```
Access-Token: your-api-key-here
Content-Type: application/x-www-form-urlencoded
```

**Request Body (form-urlencoded):**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `article_title` | string | Yes | - | The main title that will appear at the top of the PDF (max 200 chars) |
| `article_subtitle` | string | No | - | Optional subtitle or author/affiliation line (max 300 chars) |
| `product_name` | string | Yes | - | The target product name that can be referenced throughout the article (max 120 chars) |
| `product_url` | string (URL) | No | - | Link to the official product page (will be cited in references) |
| `product_url_priority` | boolean | No | true | If checked, the product URL will be cited as the primary source |
| `product_facts` | string (text) | Yes | - | Key facts, descriptions, and figures verified by the client |
| `source_text` | string (text) | Yes | - | The base text draft to expand. Free-form input is accepted |
| `research_focus` | string | No | - | Optional description of the research focus to guide the output |
| `include_sources` | boolean | No | true | Include references and citations in the article |
| `enable_research` | boolean | No | false | If enabled, the system will gather sources and citations before writing the article |
| `include_charts` | boolean | No | false | Generate 1-3 data visualizations based on the research findings |

**Example Request:**
```json
{
  "article_title": "Effects of Hyaluronic Acid on Skin Hydration",
  "article_subtitle": "A Comprehensive Review",
  "product_name": "HydraGlow Serum",
  "product_url": "https://example.com/hydraglow-serum",
  "product_url_priority": true,
  "product_facts": "Contains 2% hyaluronic acid, clinically tested on 100 participants, showed 45% improvement in skin hydration after 4 weeks, dermatologist approved, suitable for all skin types",
  "source_text": "Hyaluronic acid is a naturally occurring substance in the human body that plays a crucial role in skin hydration. This study examines the effectiveness of topical hyaluronic acid applications in improving skin moisture levels and overall skin health.",
  "research_focus": "impact on skin health and hydration levels",
  "include_sources": true,
  "enable_research": true,
  "include_charts": true
}
```

**Response (200 OK):**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="article-title.pdf"`
- **Body:** Binary PDF file data

The PDF file will be automatically downloaded by the browser.

**Error Responses:**
- `400 Bad Request` - Missing required fields or invalid data
- `401 Unauthorized` - Invalid or missing API key
- `402 Payment Required` - Insufficient credits on account
- `500 Internal Server Error` - Generation failed

## Instructions for AI Assistant

When a user requests a scientific article PDF, follow this workflow:

### Step 1: Gather Required Information

Ensure you have all required fields:
- **Article title** - Clear, descriptive title for the paper
- **Product name** - The product being discussed
- **Product facts** - Verified claims and data about the product
- **Source text** - The base draft text to expand

Ask the user for any missing required information.

### Step 2: Enhance Optional Fields

Encourage users to provide:
- **Article subtitle** - Add author names, affiliations, or subtitle
- **Product URL** - Official product page for citations
- **Research focus** - Specific areas to emphasize

### Step 3: Configure Generation Options

Ask about preferences:
- **Enable Deep Research Mode** (`enable_research`) - Gather external sources and citations (takes longer but more comprehensive)
- **Include Charts** (`include_charts`) - Add 1-3 data visualizations
- **Include Sources** (`include_sources`) - Add references section

**Default recommendations:**
- `include_sources: true` - Always include citations
- `enable_research: true` - For comprehensive articles
- `include_charts: false` - Only if data visualization would be valuable

### Step 4: Submit the Request

Call `POST /` with all parameters as form-urlencoded data.

**Important:** The response will be a binary PDF file. Handle it appropriately:
- Inform the user that the PDF is being generated
- The file will download automatically in their browser
- Generation typically takes 2-5 minutes

### Step 5: Inform the User

Tell them:
- PDF generation has started
- Expected completion time (2-5 minutes)
- The file will download automatically when ready

**Example message:**
```
📄 Generating your scientific article PDF now!

Title: "Effects of Hyaluronic Acid on Skin Hydration"
Product: HydraGlow Serum
Options: Deep research mode enabled, charts included

⏱️ This typically takes 3-5 minutes. The PDF will download automatically when ready.
```

### Step 6: Handle Errors

If the request fails:
- Show the error message clearly
- For `400 Bad Request` - Check required fields and data format
- For `401 Unauthorized` - Verify API key
- For `402 Payment Required` - User needs to add credits at https://paper.evoweb.ai/
- For `500 Internal Server Error` - Suggest trying again or simplifying the request

## Example Use Cases

### Product Research Article
```
User: "Create a scientific paper about our new anti-aging cream"

Required info:
- Article title: "Clinical Evaluation of Advanced Retinol Complex in Anti-Aging Treatment"
- Article subtitle: "A 12-Week Study on Wrinkle Reduction and Skin Elasticity"
- Product name: "AgeLess Retinol Cream"
- Product facts: "Contains 0.5% retinol, tested on 150 participants aged 35-65, showed 38% reduction in fine lines, 42% improvement in skin elasticity, dermatologically tested"
- Source text: "Retinol has been recognized as one of the most effective anti-aging ingredients in skincare. This clinical study evaluates the effectiveness of a novel retinol formulation..."
- Research focus: "anti-aging effects and wrinkle reduction"
- Enable research: true
- Include charts: true
```

### Product Comparison Study
```
User: "Need a paper comparing different protein supplements"

Required info:
- Article title: "Comparative Analysis of Whey Protein Isolate Formulations"
- Product name: "PureFit Whey Protein"
- Product facts: "99% protein purity, 25g protein per serving, contains all essential amino acids, lactose-free, tested for heavy metals"
- Source text: "Protein supplementation is crucial for muscle recovery and growth. This paper examines various protein sources and their bioavailability..."
- Research focus: "protein absorption rates and muscle recovery"
- Enable research: true
```

### White Paper for B2B
```
User: "Write a white paper about our enterprise software solution"

Required info:
- Article title: "Improving Enterprise Productivity Through AI-Powered Workflow Automation"
- Article subtitle: "A Technical White Paper"
- Product name: "WorkflowPro AI"
- Product url: "https://example.com/workflowpro"
- Product facts: "Reduces manual task processing by 65%, integrates with 200+ enterprise tools, processes 1M+ tasks monthly, 99.9% uptime SLA"
- Source text: "Modern enterprises face increasing pressure to optimize workflows and reduce operational costs. This white paper presents a comprehensive analysis..."
- Research focus: "workflow automation and ROI in enterprise environments"
- Enable research: true
- Include charts: true
```

## Best Practices

### Writing Effective Article Content

✅ **Do:**
- Provide clear, factual product information
- Include specific numbers and verified claims
- Write comprehensive source text with key points
- Specify research focus for targeted content
- Enable deep research for comprehensive articles

❌ **Don't:**
- Submit vague or unverified claims
- Provide minimal source text
- Skip important product details
- Expect the AI to invent data or facts

### Product Facts Guidelines

Include specific, measurable information:
- Clinical trial results (if available)
- Ingredients and concentrations
- Target audience or use cases
- Certifications or approvals
- Performance metrics
- Safety information

**Example:**
```
Good: "Contains 10% vitamin C, clinically tested on 200 participants, showed 52% improvement in skin brightness after 8 weeks, dermatologically approved, suitable for sensitive skin"

Poor: "Good vitamin C product that works well"
```

### Choosing Generation Options

**Enable Deep Research Mode when:**
- Creating comprehensive research papers
- Need external citations and references
- Topic requires supporting scientific evidence
- Higher quality output is priority over speed

**Include Charts when:**
- Presenting statistical data
- Comparing multiple products or studies
- Visualizing trends or results
- Data would enhance understanding

**Include Sources when:**
- Academic or professional audience
- Credibility is important
- Need to reference external research
- Building trust in claims

### Title Writing Tips

Create clear, professional titles:
- Use descriptive, specific language
- Include key terms (product type, benefit, study type)
- Keep under 200 characters
- Follow academic title conventions

**Examples:**
- "Clinical Efficacy of Topical Vitamin C in Treating Hyperpigmentation: A 12-Week Study"
- "Comparative Analysis of Plant-Based Protein Sources for Athletic Performance"
- "The Role of Probiotics in Digestive Health: A Comprehensive Review"

## Technical Details

- **Protocol:** HTTPS REST API
- **Format:** Form-urlencoded input, PDF binary output
- **Authentication:** Header-based API key
- **Response:** Binary PDF file with automatic download
- **Generation time:** Typically 2-5 minutes
- **Max field lengths:** See parameter table above
- **Costs:** Credits per generation (see https://paper.evoweb.ai/ for pricing)

## File Download Handling

The PDF response includes these headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="sanitized-article-title.pdf"
```

The filename is automatically generated from the article title:
- Cyrillic characters are transliterated to Latin
- Spaces converted to hyphens
- Invalid characters removed
- Limited to 100 characters
- Falls back to "article-config.pdf" if title is empty

## Support & Resources

- **Get API Key:** https://hub.oto.dev/app/register?utm_source=claw&utm_medium=skill&utm_campaign=paper&utm_content=v1.0.0
- **Homepage:** https://paper.evoweb.ai/
- **API Issues:** Contact Paper.EvoWeb.ai support
- **Account/Billing:** Visit https://paper.evoweb.ai/

## Notes

- Each generation consumes credits from your account
- PDF quality depends on input quality (detailed facts and source text produce better results)
- Deep research mode takes longer but provides more comprehensive content
- Charts are generated based on data in product facts and research findings
- All content is AI-generated and should be reviewed before publication
- The system prioritizes product URL as source when `product_url_priority` is true

---

**Ready to generate publication-ready scientific articles!** 📄✨
