---
description: Run the daily ETH24 digest pipeline
---

# ETH24 Daily Digest

Run the ETH24 pipeline to generate today's digest.

## Steps

1. Run `python3 crawl.py` from the eth24 directory to fetch today's tweets. Wait for it to complete.

2. Read the crawled data from `output/YYYY-MM-DD/crawled.json` (use today's date).

3. Read `config.json` for the topic, brand, and voice settings.

4. Read `SKILL.md` for ranking guidelines.

5. Rank the top 10 tweets by importance for the configured topic. Filter spam. Write one-line commentary for each in the configured voice. If fewer than 10 quality tweets, backfill from the previous day's crawl.

6. Save the result to `output/YYYY-MM-DD/ranked.json`.

7. Generate a thread preview and save to `output/YYYY-MM-DD/thread.txt`. Format:
   - First post: `[brand] - [date]\n\n[tagline]\n\nTLDR:\n[highlights].\n\nDetails below`
   - Posts 1-10: `N/ [commentary]\n\n[tweet_url]`
   - Closer: `[brand] by [account]\n[description]\n\nOpen source: [repo_url]`

8. Print the thread preview for review.
