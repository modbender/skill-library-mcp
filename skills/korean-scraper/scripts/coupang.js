#!/usr/bin/env node
/**
 * coupang.js - 쿠팡 상품 스크래퍼
 * 
 * Usage:
 *   node coupang.js product "https://www.coupang.com/vp/products/..."
 *   node coupang.js search "무선 이어폰" --limit 20
 */

const {
  createStealthBrowser,
  humanDelay,
  cleanText,
  outputSuccess,
  outputError,
  rateLimit,
  getDomain,
  parseKoreanNumber,
  scrollDown
} = require('../lib/common.js');

const SELECTORS = {
  // 상품 상세
  productName: '.prod-buy-header__title, h1.prod-buy-header__title',
  price: '.total-price strong, .prod-price .total-price',
  originalPrice: '.prod-origin-price, .origin-price',
  discount: '.discount-percentage, .prod-coupon-price .discount-rate',
  rating: '.rating-star-num, .rating-total-review em',
  reviewCount: '.rating-total-review span, .sdp-review__average__total-star',
  rocketBadge: '.rocket-badge, img[alt*="로켓"]',
  seller: '.prod-sale-vendor-name a, .seller-name',
  productImages: '.prod-image__detail img, #thumbnailImg img',
  
  // 검색 결과
  searchItem: 'li.search-product',
  searchTitle: '.name',
  searchPrice: '.price-value',
  searchRating: '.rating',
  searchReviews: '.rating-total-count'
};

async function scrapeProduct(url) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    
    await rateLimit(getDomain(url));
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await humanDelay(3000, 5000);
    
    // 상품 정보 추출
    const data = await page.evaluate((selectors) => {
      const getText = (selector) => {
        const el = document.querySelector(selector);
        return el?.textContent?.trim() || '';
      };
      
      const getNumber = (selector) => {
        const text = getText(selector);
        return text.replace(/[^0-9]/g, '');
      };
      
      return {
        productName: getText(selectors.productName),
        price: getNumber(selectors.price),
        originalPrice: getNumber(selectors.originalPrice),
        discount: getText(selectors.discount),
        rating: getText(selectors.rating),
        reviewCount: getNumber(selectors.reviewCount),
        rocketDelivery: !!document.querySelector(selectors.rocketBadge),
        seller: getText(selectors.seller),
        images: Array.from(document.querySelectorAll(selectors.productImages))
          .map(img => img.src)
          .filter(src => src && !src.includes('icon'))
          .slice(0, 5) // 최대 5개
      };
    }, SELECTORS);
    
    await browser.close();
    
    outputSuccess({
      url,
      productName: data.productName,
      price: parseInt(data.price) || 0,
      originalPrice: parseInt(data.originalPrice) || 0,
      discount: data.discount,
      rating: parseFloat(data.rating) || 0,
      reviewCount: parseInt(data.reviewCount) || 0,
      rocketDelivery: data.rocketDelivery,
      seller: data.seller,
      images: data.images
    });
    
  } catch (error) {
    await browser.close();
    outputError(`Failed to scrape product: ${error.message}`, { url });
    process.exit(1);
  }
}

async function searchProduct(query, limit = 20) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    const searchUrl = `https://www.coupang.com/np/search?q=${encodeURIComponent(query)}`;
    
    await rateLimit('coupang.com');
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await humanDelay(2000, 4000);
    
    // 스크롤로 더 많은 결과 로드
    await scrollDown(page, 2);
    
    // 검색 결과 추출
    const products = await page.$$eval(SELECTORS.searchItem, (items, selectors, limit) => {
      return items.slice(0, limit).map(item => {
        const titleEl = item.querySelector(selectors.searchTitle);
        const priceEl = item.querySelector(selectors.searchPrice);
        const ratingEl = item.querySelector(selectors.searchRating);
        const reviewsEl = item.querySelector(selectors.searchReviews);
        const linkEl = item.querySelector('a.search-product-link');
        
        return {
          name: titleEl?.textContent?.trim() || '',
          price: priceEl?.textContent?.replace(/[^0-9]/g, '') || '0',
          rating: ratingEl?.textContent?.trim() || '0',
          reviews: reviewsEl?.textContent?.replace(/[^0-9]/g, '') || '0',
          url: linkEl?.href || ''
        };
      }).filter(p => p.name);
    }, SELECTORS, limit);
    
    // 데이터 정제
    products.forEach(p => {
      p.price = parseInt(p.price) || 0;
      p.rating = parseFloat(p.rating) || 0;
      p.reviews = parseInt(p.reviews) || 0;
    });
    
    await browser.close();
    
    outputSuccess({
      query,
      count: products.length,
      products
    });
    
  } catch (error) {
    await browser.close();
    outputError(`Failed to search products: ${error.message}`, { query });
    process.exit(1);
  }
}

// CLI 파싱
const args = process.argv.slice(2);
const command = args[0];
const target = args[1];

if (!command || !target) {
  console.error('Usage:');
  console.error('  node coupang.js product "product_url"');
  console.error('  node coupang.js search "query" [--limit N]');
  process.exit(1);
}

const limitIndex = args.indexOf('--limit');
const limit = limitIndex !== -1 ? parseInt(args[limitIndex + 1]) : 20;

if (command === 'product') {
  scrapeProduct(target);
} else if (command === 'search') {
  searchProduct(target, limit);
} else {
  console.error(`Unknown command: ${command}`);
  process.exit(1);
}
