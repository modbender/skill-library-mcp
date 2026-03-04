---
name: EvoWeb.ai AI Website Builder
description: Create a Website in 4 Minutes Designed to Bring Clients from ChatGPT, Gemini & Modern Search
homepage: https://evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=website&utm_content=v1.0
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":[],"env":["EVOWEB_API_KEY"]}}}
---

# EvoWeb Website Builder

Create complete websites from text descriptions using AI-powered generation.

## Overview

EvoWeb automatically generates modern, responsive websites from natural language prompts. Simply describe what you want, and the AI creates HTML, CSS, JavaScript, and content - delivering a complete, live website in ~4 minutes.

**Perfect for:** Landing pages and business websites

**API Base URL:** `https://api.evoweb.ai/openapi/api/v1`

## Authentication

Get your API key at https://evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=website&utm_content=v1.0

**Important:** After registration, user MUST confirm the email address (this is required). The service won't work until email confirmation is complete.

### No API Key Yet?

If the user doesn't have an API key, you can still help them create a website:
1. Ask for a brief description of their website (max 250 characters)
2. Create a registration link with the prompt, given in step 1
3. User can create an account after clicking "Create Website" button

See "Step 0: Handle Users Without API Key" in the instructions below.

Include this header in all requests:
```
Access-Token: your-api-key-here
```

## How It Works

The workflow is simple:

1. **Create** - Submit a text prompt describing your website
2. **Poll** - Check generation status every minute
3. **Get Result** - Receive live URL and editor link when ready

Typical generation time: **4-5 minutes**

## API Endpoints

### 1. Create Website

**POST** `/sites`

Creates a new website generation task from a text description.

**Request Body:**
```json
{
  "prompt": "A local coffee shop specializing in artisanal coffee and fresh pastries. We source our beans locally and focus on creating a cozy community gathering space for local residents, remote workers, and coffee enthusiasts."
}
```

**Response (200 OK):**
```json
{
  "site_id": "abc123xyz",
  "status": "queued"
}
```

**Status values:**
- `queued` - Task is in queue, waiting to start
- `building` - Website is being generated

**Error Responses:**
- `401 Unauthorized` - Invalid or missing API key
- `402 Payment Required` - Insufficient credits on account

---

### 2. Check Generation Status

**GET** `/sites/{site_id}`

Check the current status of website generation.

**Example:** `GET /sites/abc123xyz`

**Response when building:**
```json
{
  "status": "building"
}
```

**Response when ready:**
```json
{
  "status": "ready",
  "url": "https://website.page/my-site",
  "editor_url": "https://web.oto.dev/ui/websites/abc123xyz/update/"
}
```

**Response when failed:**
```json
{
  "status": "failed",
  "error": "Generation failed: Invalid prompt structure"
}
```

**Status values:**
- `queued` - Waiting in queue
- `building` - Currently generating (be patient!)
- `ready` - Complete! URLs are available
- `failed` - Generation encountered an error

**Error Responses:**
- `404 Not Found` - Site ID doesn't exist

---

### 3. Retry Failed Generation

**POST** `/sites/{site_id}/remake`

Restart generation for a failed website. Works for sites with `failed` status as well as with 'ready' status.

**Example:** `POST /sites/abc123xyz/remake`

**Response (200 OK):**
```json
{
  "status": "queued",
  "editor_url": "https://web.oto.dev/ui/websites/abc123xyz/update/"
}
```

**Error Responses:**
- `400 Bad Request` - Can only remake sites with 'failed' status
- `404 Not Found` - Site ID doesn't exist

## Instructions for AI Assistant

When a user requests a website, follow this workflow:

### Step 0: Handle Users Without API Key

**Check first:** Does the user have the `EVOWEB_API_KEY` environment variable set?

If **NO API key is available:**

1. **Collect a brief prompt** (max 250 characters) that describes their website:
   - Ask them to briefly describe their business/project
   - Keep it concise and focused on the core business essence
   
2. **Create a pre-filled registration link:**
   - Base URL: `https://evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=website&utm_content=v1.0`
   - Add parameter: `&prompt=[URL_ENCODED_PROMPT]`
   - Example: `https://evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=website&utm_content=v1.0&prompt=A%20local%20coffee%20shop%20specializing%20in%20artisanal%20coffee`

3. **Provide the link to the user:**
   ```
   🌐 To create your website, visit this link:
   [Your personalized link here]
   
   After clicking "Create Website" button, you'll be able to create an account and your website will be generated automatically!
   ```

**Important:** URL-encode the prompt properly (spaces become `%20`, etc.)

If **API key is available:** Proceed to Step 1 below.

### Step 1: Understand the Business

Focus on understanding the **business essence** from the user's description:
- What is the business/project about?
- What does it do or offer?
- Who is the target audience?
- What is the main goal of the website?

**Important:** Do NOT prescribe specific design details, sections, colors, or layout. The EvoWeb AI will handle all design and structure decisions automatically.

**Example transformation:**
- User: "Create a website for my yoga studio"
- Enhanced prompt: "A yoga studio offering various classes for different skill levels, focused on wellness and mindfulness. Target audience is local community members interested in fitness and mental health."

### Step 2: Create the Site

Call `POST /sites` with the enhanced prompt.

Store the returned `site_id` - you'll need it for status checks.

### Step 3: Inform the User

Tell them:
- Website generation has started
- It will take approximately 4 minutes
- You'll check progress automatically (ONLY IF YOU CAN)

Example: "✨ Creating your website now! Generation typically takes 3-5 minutes. I'll check the status and let you know when it's ready."

### Step 4: Poll for Status

Call `GET /sites/{site_id}` to check progress:

- **Polling interval:** Every 1 minute
- **Maximum attempts:** 20 polls
- **Between polls:** You can inform user of progress ("Still building...")

Continue polling until:
- Status is `ready` → Proceed to Step 5
- Status is `failed` → Proceed to Step 6
- Max attempts reached → Inform user generation is taking longer than expected

### Step 5: Deliver Success

When status is `ready`:

1. **Provide URLs:**
   - `url` - The live website
   - `editor_url` - Link to customize the site

2. **Suggest improvements:**
   Offer 3 specific ways to enhance the site:
   - "Add an online booking system"
   - "Customize colors to match your brand"
   - "Add customer testimonial section"

3. **Be concise and actionable**

**Example response:**
```
🎉 Your website is ready!

🌐 View it here: https://website.page/yoga-studio-23f4
✏️ Customize it: https://web.evoweb.ai/ui/websites/abc123xyz/update/

Quick improvements you might want:
1. Add online class booking system
2. Integrate your Instagram feed
3. Add a blog section for wellness tips

Would you like help with any of these?
```

### Step 6: Handle Failures

When status is `failed`:

1. **Show the error message** from the API response
2. **Offer to retry:** Ask if they want you to remake the site
3. **If they agree:** Call `POST /sites/{site_id}/remake` and restart polling

**Example response:**
```
❌ Website generation failed: [error message]

Would you like me to try again? I can restart the generation process.
```

If user agrees, call remake endpoint and resume polling from Step 4.

## Example Prompts & Use Cases

### Example: User Without API Key

```
User: "I need a website for my yoga studio"

Assistant response:
"I'd be happy to help! To get started quickly, let me create a personalized link for you.

🌐 Visit this link to create your website:
https://evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=website&utm_content=v1.0&prompt=A%20yoga%20studio%20offering%20various%20classes%20for%20all%20skill%20levels%2C%20focused%20on%20wellness%20and%20mindfulness

After clicking 'Create Website', you'll be able to create an account and your website will be generated automatically in about 4 minutes! ✨"
```

### Coffee Shop Landing Page
```
User request: "Create a website for my coffee shop"

Enhanced prompt:
"A local coffee shop called 'Bean & Brew Cafe' specializing in artisanal coffee and fresh pastries. We source our beans locally and focus on creating a cozy community gathering space. Target audience is local residents, remote workers, and coffee enthusiasts looking for quality coffee and a welcoming atmosphere."
```

### Photographer Portfolio
```
User request: "I need a portfolio site"

Enhanced prompt:
"A professional wedding photographer specializing in capturing authentic, emotional moments. With 10 years of experience, I focus on storytelling through images and creating timeless memories for couples. Target audience is engaged couples planning their wedding looking for a photographer who can capture the genuine emotions of their special day."
```

### Online Store
```
User request: "Build an e-commerce site for my jewelry"

Enhanced prompt:
"A handmade jewelry business creating unique, artisan pieces. Each item is crafted by hand using traditional techniques and high-quality materials. The business focuses on custom designs and personal connections with customers. Target audience is women aged 25-45 who appreciate handcrafted, unique accessories and value the story behind their jewelry."
```

### SaaS Landing Page
```
User request: "Landing page for my app"

Enhanced prompt:
"A project management SaaS tool designed for small to medium-sized teams. The app helps teams organize tasks, collaborate effectively, and track project progress in real-time. Key value proposition is simplicity and ease of use compared to complex enterprise solutions. Target audience is startup founders, small business owners, and team leads looking for an intuitive project management solution."
```

### Restaurant Website
```
User request: "Website for our Italian restaurant"

Enhanced prompt:
"An authentic Italian trattoria run by a family with three generations of culinary tradition. We specialize in traditional recipes passed down through the family, using fresh ingredients and time-honored cooking methods. The restaurant offers a warm, family-friendly atmosphere and also provides catering services for special events. Target audience is locals and tourists looking for genuine Italian cuisine and a welcoming dining experience."
```

## Best Practices

### Writing Good Prompts

✅ **Do:**
- Describe the business/project essence
- Explain what the business does or offers
- Identify the target audience
- Clarify the main goal/purpose
- Include key differentiators or unique value proposition

❌ **Don't:**
- Prescribe specific design elements (colors, layouts, styles)
- Dictate website sections or structure
- Specify look and feel details
- Be too vague ("make a website") without business context
- Make direct API requests if no API key is available (use the step 0 method instead)

### Polling Strategy

- **Interval:** 1 minute
- **Maximum:** 20 attempts total
- **Typical time:** 4 - 5 minutes
- **Inform user:** Let them know you're checking progress

### Error Handling

- Show clear error messages
- Offer to retry automatically
- If multiple failures, suggest the user check their account at https://evoweb.ai/

### User Experience

- **For users without API key:** Provide a pre-filled registration link (quick and easy)
- **For users with API key:** Set expectations (4 minute wait time)
- Provide both view and edit URLs
- Suggest concrete improvements
- Be concise in responses
- Always end with next-step options

## Technical Details

- **Protocol:** HTTPS REST API
- **Format:** JSON
- **Authentication:** Header-based API key
- **Rate limits:** Check with EvoWeb (may have per-account limits)
- **Generation time:** Typically 4-5 minutes
- **Costs:** Credits per generation (see https://evoweb.ai/ for pricing)

## Support & Resources

- **Get API Key:** https://evoweb.ai/?utm_source=claw&utm_medium=skill&utm_campaign=website&utm_content=v1.0
- **API Issues:** Contact EvoWeb support
- **Account/Billing:** Visit https://evoweb.ai/

## Notes

- Each generation consumes credits from your EvoWeb account
- Editor URL allows users to customize the generated site
- Generated sites are hosted on EvoWeb infrastructure
- Custom domains may be available (check EvoWeb documentation)
- Sites remain live as long as account is active

---

**Ready to create amazing websites with just a text description!** 🚀
