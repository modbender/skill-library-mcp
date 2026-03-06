const { PlaywrightCrawler } = require('crawlee');

const args = process.argv.slice(2);
const targetUrl = args.find(a => a.startsWith('http'));
const maxPages = parseInt(args.find((a, i) => args[i-1] === '--pages') || '1');

if (!targetUrl) {
    console.error('Usage: node assets/amazon_handler.js <AMAZON_URL> [--pages N]');
    process.exit(1);
}

function detectPageType(url) {
    if (url.includes('/zgbs/') || url.includes('/bestsellers/')) return 'bestsellers';
    if (url.includes('/zg/new-releases/')) return 'new-releases';
    if (url.includes('/zg/movers-and-shakers/')) return 'movers-shakers';
    if (url.includes('/dp/') || url.includes('/gp/product/')) return 'product-detail';
    if (url.includes('/s?') || url.includes('/s/')) return 'search';
    return 'generic';
}

const pageType = detectPageType(targetUrl);

const crawler = new PlaywrightCrawler({
    launchContext: { launchOptions: { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] } },
    maxRequestRetries: 2,
    requestHandlerTimeoutSecs: 300,
    async requestHandler({ page, log }) {
        log.info(`Amazon Scraper [${pageType}] => ${targetUrl}`);
        const context = page.context();
        await context.clearCookies();
        await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

        let allProducts = [];

        for (let pg = 1; pg <= maxPages; pg++) {
            let url = targetUrl;
            if (pg > 1) url = targetUrl.includes('?') ? `${targetUrl}&pg=${pg}` : `${targetUrl}?pg=${pg}`;

            log.info(`Page ${pg}/${maxPages}: ${url}`);
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
            await page.waitForTimeout(3000);
            await page.evaluate(async () => {
                for (let i = 0; i < 5; i++) { window.scrollBy(0, window.innerHeight); await new Promise(r => setTimeout(r, 500)); }
                window.scrollTo(0, 0);
            });

            let products = [];

            if (pageType === 'bestsellers' || pageType === 'new-releases' || pageType === 'movers-shakers') {
                products = await page.evaluate(() => {
                    const items = [];
                    const cards = document.querySelectorAll('[data-asin]');

                    if (cards.length > 0) {
                        cards.forEach(card => {
                            try {
                                const rankEl = card.querySelector('.zg-bdg-text, [class*="zg-badge"]');
                                const titleEl = card.querySelector('a span, ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y, .p13n-sc-truncate');
                                const ratingEl = card.querySelector('[class*="a-icon-alt"]');
                                const reviewEl = card.querySelector('[class*="a-size-small"]');
                                const priceEl = card.querySelector('.p13n-sc-price, ._cDEzb_p13n-sc-price_3mJ9Z, .a-price .a-offscreen');
                                const imgEl = card.querySelector('img');
                                const linkEl = card.querySelector('a[href*="/dp/"]');
                                const asin = card.getAttribute('data-asin') || (linkEl && linkEl.href && linkEl.href.match(/\/dp\/([A-Z0-9]{10})/) ? linkEl.href.match(/\/dp\/([A-Z0-9]{10})/)[1] : null);

                                // bought in past month
                                const allSpans = card.querySelectorAll('span');
                                let boughtPastMonth = null;
                                allSpans.forEach(s => {
                                    const t = s.textContent.trim();
                                    if (t.match(/bought in past month/i)) {
                                        const m = t.match(/([\d,.]+[KkMm]?\+?)\s*bought/i);
                                        boughtPastMonth = m ? m[1] : t;
                                    }
                                });

                                const rank = rankEl ? parseInt(rankEl.textContent.replace('#', '')) : null;
                                const title = titleEl ? titleEl.textContent.trim() : null;
                                const rating = ratingEl ? parseFloat(ratingEl.textContent) : null;
                                const reviews = reviewEl ? parseInt(reviewEl.textContent.replace(/[^0-9]/g, '')) : null;
                                const priceText = priceEl ? priceEl.textContent.trim() : null;
                                const price = priceText ? parseFloat(priceText.replace(/[^0-9.]/g, '')) : null;
                                const image = imgEl ? imgEl.src : null;
                                const url = linkEl ? linkEl.href : null;

                                if (title) {
                                    items.push({ rank, title, rating, reviews, price, priceStr: priceText, asin, image, url, boughtPastMonth });
                                }
                            } catch (e) {}
                        });
                    }

                    if (items.length === 0) {
                        // Fallback: text-based parsing
                        const text = document.body.innerText;
                        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
                        let currentRank = null;
                        let currentProduct = {};

                        for (const line of lines) {
                            const rankMatch = line.match(/^#(\d+)$/);
                            if (rankMatch) {
                                if (currentRank && currentProduct.title) items.push(currentProduct);
                                currentRank = parseInt(rankMatch[1]);
                                currentProduct = { rank: currentRank };
                                continue;
                            }
                            if (currentRank) {
                                if (line.match(/^([\d.]+) out of 5 stars$/)) {
                                    currentProduct.rating = parseFloat(line);
                                } else if (line.match(/^\$([\d,.]+)$/)) {
                                    currentProduct.price = parseFloat(line.replace(/[$,]/g, ''));
                                    currentProduct.priceStr = line;
                                } else if (line.match(/^\s*[\d,]+\s*$/) && !currentProduct.reviews && currentProduct.rating) {
                                    currentProduct.reviews = parseInt(line.replace(/,/g, ''));
                                } else if (line.match(/bought in past month/i)) {
                                    const m = line.match(/([\d,.]+[KkMm]?\+?)\s*bought/i);
                                    currentProduct.boughtPastMonth = m ? m[1] : line;
                                } else if (!currentProduct.title && line.length > 10
                                    && !line.includes('out of 5') && !line.includes('Best Seller')
                                    && !line.includes('Previous page') && !line.includes('Next page')) {
                                    currentProduct.title = line;
                                }
                            }
                        }
                        if (currentRank && currentProduct.title) items.push(currentProduct);
                    }
                    return items;
                });

            } else if (pageType === 'product-detail') {
                products = await page.evaluate(() => {
                    const title = (document.querySelector('#productTitle') || {}).textContent?.trim();
                    const priceEl = document.querySelector('.a-price .a-offscreen, #priceblock_ourprice, #priceblock_dealprice');
                    const priceStr = priceEl ? priceEl.textContent.trim() : null;
                    const price = priceStr ? parseFloat(priceStr.replace(/[^0-9.]/g, '')) : null;
                    const ratingEl = document.querySelector('#acrPopover .a-icon-alt');
                    const rating = ratingEl ? parseFloat(ratingEl.textContent) : null;
                    const reviewsEl = document.querySelector('#acrCustomerReviewText');
                    const reviews = reviewsEl ? parseInt(reviewsEl.textContent.replace(/[^0-9]/g, '')) : null;
                    const asin = (document.querySelector('[data-asin]') || {}).getAttribute?.('data-asin') || (window.location.pathname.match(/\/dp\/([A-Z0-9]{10})/) || [])[1];
                    const brand = (document.querySelector('#bylineInfo') || {}).textContent?.trim();
                    const image = (document.querySelector('#landingImage, #imgBlkFront') || {}).src;
                    const bsrMatch = document.body.innerText.match(/Best Sellers Rank.*?#([\d,]+)/);
                    const bsr = bsrMatch ? parseInt(bsrMatch[1].replace(/,/g, '')) : null;
                    const breadcrumbs = Array.from(document.querySelectorAll('#wayfinding-breadcrumbs_feature_div a')).map(a => a.textContent.trim());
                    const bullets = Array.from(document.querySelectorAll('#feature-bullets li span')).map(s => s.textContent.trim()).filter(Boolean);

                    // bought in past month
                    let boughtPastMonth = null;
                    const boughtMatch = document.body.innerText.match(/([\d,.]+[KkMm]?\+?)\s*bought in past month/i);
                    if (boughtMatch) boughtPastMonth = boughtMatch[1];

                    // Date first available
                    const dateMatch = document.body.innerText.match(/Date First Available\s*[:\n]\s*([A-Za-z]+ \d+,? \d{4})/);
                    const dateFirstAvailable = dateMatch ? dateMatch[1] : null;

                    const details = {};
                    document.querySelectorAll('#productDetails_techSpec_section_1 tr, #detailBullets_feature_div li').forEach(row => {
                        const key = (row.querySelector('th, .a-text-bold') || {}).textContent?.trim()?.replace(/[:\s]+$/, '');
                        const val = (row.querySelector('td, span:not(.a-text-bold)') || {}).textContent?.trim();
                        if (key && val) details[key] = val;
                    });

                    return [{ title, price, priceStr, rating, reviews, asin, brand, image, bsr, boughtPastMonth, dateFirstAvailable, category: breadcrumbs, bullets, details }];
                });

            } else if (pageType === 'search') {
                products = await page.evaluate(() => {
                    const items = [];
                    document.querySelectorAll('[data-component-type="s-search-result"]').forEach(card => {
                        try {
                            const asin = card.getAttribute('data-asin');
                            const titleEl = card.querySelector('h2 a span');
                            const priceEl = card.querySelector('.a-price .a-offscreen');
                            const ratingEl = card.querySelector('.a-icon-alt');
                            const reviewEl = card.querySelector('[class*="s-link-style"] .a-size-base');
                            const imgEl = card.querySelector('.s-image');
                            const linkEl = card.querySelector('h2 a');
                            const sponsoredEl = card.querySelector('.s-label-popover-default');

                            let boughtPastMonth = null;
                            card.querySelectorAll('span').forEach(s => {
                                const t = s.textContent.trim();
                                if (t.match(/bought in past month/i)) {
                                    const m = t.match(/([\d,.]+[KkMm]?\+?)\s*bought/i);
                                    boughtPastMonth = m ? m[1] : t;
                                }
                            });

                            items.push({
                                asin,
                                title: titleEl ? titleEl.textContent.trim() : null,
                                price: priceEl ? parseFloat(priceEl.textContent.replace(/[^0-9.]/g, '')) : null,
                                priceStr: priceEl ? priceEl.textContent.trim() : null,
                                rating: ratingEl ? parseFloat(ratingEl.textContent) : null,
                                reviews: reviewEl ? parseInt(reviewEl.textContent.replace(/[^0-9]/g, '')) : null,
                                image: imgEl ? imgEl.src : null,
                                url: linkEl ? 'https://www.amazon.com' + linkEl.getAttribute('href') : null,
                                boughtPastMonth,
                                sponsored: !!sponsoredEl
                            });
                        } catch (e) {}
                    });
                    return items;
                });

            } else {
                // Generic fallback
                const title = await page.title();
                const content = await page.evaluate(() => document.body.innerText);
                console.log(JSON.stringify({ status: 'SUCCESS', type: 'GENERIC', title, data: content.substring(0, 10000) }));
                return;
            }

            // Deduplicate by ASIN
            products = products.filter((p, i, arr) => {
                if (!p.asin) return true;
                const firstIdx = arr.findIndex(x => x.asin === p.asin);
                if (firstIdx !== i) {
                    // Merge rank into first occurrence if missing
                    if (p.rank && !arr[firstIdx].rank) arr[firstIdx].rank = p.rank;
                    if (p.boughtPastMonth && !arr[firstIdx].boughtPastMonth) arr[firstIdx].boughtPastMonth = p.boughtPastMonth;
                    return false;
                }
                return true;
            });

            allProducts.push(...products);
            if (pg < maxPages) await page.waitForTimeout(2000);
        }

        const metadata = await page.evaluate(() => {
            const title = document.title;
            const breadcrumbs = Array.from(document.querySelectorAll('#zg_browseRoot a, .zg-breadcrumb a')).map(a => a.textContent.trim());
            return { title, breadcrumbs };
        });

        console.log(JSON.stringify({
            status: 'SUCCESS',
            type: pageType,
            url: targetUrl,
            category: metadata.title?.replace('Amazon Best Sellers: Best ', '').replace('Amazon.com : ', ''),
            breadcrumbs: metadata.breadcrumbs,
            totalProducts: allProducts.length,
            pages: maxPages,
            scrapedAt: new Date().toISOString(),
            products: allProducts
        }));
    },
});

crawler.run([targetUrl]);
