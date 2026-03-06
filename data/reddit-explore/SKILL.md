---
name: reddit-explore
description: |
  This skill should be used when the user asks to "search Reddit", "explore Reddit posts", "find Reddit discussions about", "summarize Reddit opinions on", "what does Reddit think about", or wants to gather and summarize community opinions from Reddit on a specific topic.
disable-model-invocation: true
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["python3"], "env": ["APIFY_TOKEN"] },
        "primaryEnv": "APIFY_TOKEN",
      },
  }
---

# Reddit Explore

Search Reddit for posts on any topic using the Apify `trudax/reddit-scraper-lite` actor and produce a structured summary of community sentiment.

## Prerequisites

Before running, verify:

1. **apify-client** is installed: `pip3 install apify-client`
2. **APIFY_TOKEN** is set as an environment variable

If either is missing, refer the user to `references/apify-setup.md` in this skill's directory for setup instructions.

## Workflow

### Step 1: Determine the search topic

The search topic comes from `$ARGUMENTS`. If `$ARGUMENTS` is empty or missing, ask the user what topic they want to search Reddit for.

### Step 2: Run the Reddit search script

Execute the search script with the user's topic:

```bash
python3 ~/.agents/skills/reddit-explore/scripts/reddit_search.py --query "$ARGUMENTS" --max-items 30
```

The script outputs JSON results to stdout. If it fails:
- **"APIFY_TOKEN not found"**: Guide the user through setting up their token (see `references/apify-setup.md`)
- **"apify-client not installed"**: Run `pip3 install apify-client`
- **Other errors**: Show the error message and help troubleshoot

### Step 3: Analyze and summarize results

Read the JSON output. Each item contains:
- `title` - Post title
- `communityName` - Subreddit name
- `upVotes` - Score
- `numberOfComments` - Comment count
- `url` - Link to the post
- `body` - Post text content
- `createdAt` - When it was posted

### Step 4: Produce a structured summary

Present findings in this format:

#### Overview
Brief 2-3 sentence summary of what Reddit thinks about the topic.

#### Community Sentiment
- **Overall tone**: Positive / Mixed / Negative
- **Key subreddits**: List the most active communities discussing this

#### Key Themes

**Positives / Pros:**
- Bullet points of praised aspects, with post references

**Negatives / Cons:**
- Bullet points of criticized aspects, with post references

**Neutral / Informational:**
- Notable factual observations from the community

#### Notable Posts
List 3-5 of the most relevant/upvoted posts with:
- Title, subreddit, score
- Brief summary of the post content
- Link to the post

#### Summary
A concise takeaway of the community consensus.

## Tips

- For broad topics, the script searches with the exact query provided. If results are sparse, suggest the user try alternative phrasings.
- Posts are sorted by relevance by default.
- The script deduplicates results by URL automatically.
- Apify free tier provides $5/month in credits; each search typically costs a few cents.
