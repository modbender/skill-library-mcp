const puppeteer = require('puppeteer');

const url = process.argv[2];

if (!url) {
  console.error("Please provide a URL to a tweet.");
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    defaultViewport: { width: 1280, height: 800 }
  });

  try {
    const page = await browser.newPage();
    
    // Set a standard user agent to avoid immediate blocks
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    // Navigate to the tweet URL
    console.log("Navigating to:", url);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log("Page loaded, waiting for tweet...");

    // Wait for tweet content to load
    try {
      // Wait for either a standard tweet OR an Article (Note) container
      // X Articles often appear in [data-testid="article.content"] or similar, but let's look broadly first.
      await page.waitForSelector('article[data-testid="tweet"]', { timeout: 10000 });
      console.log("Tweet found.");
    } catch (e) {
      // If blocked or not found, try waiting for login wall or error
      const content = await page.content();
      if (content.includes("Something went wrong")) {
        console.error("X/Twitter blocked the request (generic error).");
        process.exit(1);
      }
      if (content.includes("Log in")) {
        console.error("Login wall encountered. This skill only supports public tweets currently.");
        process.exit(1);
      }
      console.error("Could not find tweet content. The page structure may have changed.");
      process.exit(1);
    }

    // Extract tweet data
    const debugInfo = await page.evaluate(() => {
        const firstArticle = document.querySelector('article[data-testid="tweet"]');
        return firstArticle ? firstArticle.innerText : "No article found";
    });
    console.log("DEBUG TEXT:", debugInfo.substring(0, 2000));

    const tweets = await page.evaluate(() => {
      // Check for X Article (Long form post) content which might be separate from tweetText
      const articleContent = document.querySelector('[data-testid="article.content"]');
      let articleText = "";
      if (articleContent) {
          articleText = "\n\n**X ARTICLE CONTENT:**\n" + articleContent.innerText;
      }
      
      // Try to find ANY text if tweetText is missing
      // Sometimes X puts text in other weird places for media posts
      
      // Get all tweets on the page (main + replies)
      const articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
      
      // If we found an article content but NO tweets (e.g. specialized Article page), construct a fake tweet
      if (articles.length === 0 && articleText) {
         return [{
             user: "X Article",
             handle: "unknown",
             text: articleText,
             cardUrl: "",
             cardTitle: "",
             time: "",
             media: [],
             isMain: true
         }];
      }

      return articles.slice(0, 4).map((article, index) => {
        const userElement = article.querySelector('[data-testid="User-Name"]');
        const textElement = article.querySelector('[data-testid="tweetText"]');
        
        // Extract user info early so heuristics below can use it
        let userName = "Unknown";
        let userHandle = "unknown";
        if (userElement) {
           const parts = userElement.innerText.split('\n');
           if (parts.length >= 2) {
             userName = parts[0];
             userHandle = parts[1];
           } else {
             userName = userElement.innerText;
           }
        }

        let text = textElement ? textElement.innerText : "";

        // If no text, check if it's a "mixed media" post where text might be in a description or similar
        // Or check for "Show more" spans that might have been collapsed
        if (!text) {
             // Heuristic: if main text is empty, maybe it's in ALT text or just a media post
             // Fallback: Use the full article text but strip known noise
             const rawText = article.innerText;
             // Split by newlines
             const lines = rawText.split('\n');
             // Filter out lines that match username, handle, time, stats
             // This is custom logic for this specific layout
             const filteredLines = lines.filter(line => {
                 if (line === userName) return false;
                 if (line === userHandle) return false;
                 if (line === "·") return false;
                 // Filter out stat numbers if they are just digits or simple (like 16, 96, 268K)
                 // This is risky but "AI Edge" example had "16 96 760 268K" as stats lines
                 if (/^[\d\.KMB]+$/.test(line)) return false; 
                 return true;
             });
             text = filteredLines.join('\n').trim();
        }

        // Extract links (cards)
        const cardElement = article.querySelector('[data-testid="card.wrapper"] a');
        let cardUrl = "";
        let cardTitle = "";
        if (cardElement) {
            cardUrl = cardElement.href;
            const titleEl = article.querySelector('[data-testid="card.layoutLarge.detail"] span') || 
                            article.querySelector('[data-testid="card.layoutSmall.detail"] span');
            if (titleEl) cardTitle = titleEl.innerText;
        }

        const timeElement = article.querySelector('time');
        
        // Extract media (images/videos)
        const mediaElements = article.querySelectorAll('img[src*="pbs.twimg.com/media"]');
        const mediaUrls = Array.from(mediaElements).map(img => {
            // Check for ALT text on images
            const alt = img.getAttribute('alt');
            return {
                src: img.src,
                alt: alt || ""
            };
        });

        // Append article content if this is the main tweet and we found an Article container
        if (index === 0 && articleText) {
            text += articleText;
        }

        const time = timeElement ? timeElement.getAttribute('datetime') : "";
        
        const isMain = index === 0;

        return {
            user: userName,
            handle: userHandle,
            text: text,
            cardUrl: cardUrl,
            cardTitle: cardTitle,
            time: time,
            media: mediaUrls, // Now an array of objects
            isMain: isMain
        };
      });
    });

    if (tweets.length === 0) {
      console.log("No tweets found. Trying full page text...");
      const bodyText = await page.evaluate(() => document.body.innerText);
      console.log(bodyText.substring(0, 500));
    } else {
      console.log(`## Tweet Thread Summary\nSource: ${url}\n`);
      tweets.forEach(tweet => {
        const role = tweet.isMain ? "**MAIN TWEET**" : "Reply";
        console.log(`### ${role} by ${tweet.user} (${tweet.handle})`);
        console.log(`*${tweet.time || 'Unknown time'}*\n`);
        console.log(tweet.text);
        if (tweet.cardUrl) {
            console.log(`\n**Linked Article:** [${tweet.cardTitle || tweet.cardUrl}](${tweet.cardUrl})`);
        }
        if (tweet.media.length > 0) {
            console.log(`\n**Media:**`);
            tweet.media.forEach(m => {
                const src = m.src.replace('name=small', 'name=large');
                console.log(`- ![](${src})`);
                if (m.alt) console.log(`  > **ALT:** ${m.alt}`);
            });
        }
        console.log(`\n---\n`);
      });
    }

  } catch (error) {
    console.error("Error reading tweet:", error.message);
  } finally {
    await browser.close();
  }
})();
