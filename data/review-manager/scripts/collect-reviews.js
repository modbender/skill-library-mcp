#!/usr/bin/env node
/**
 * collect-reviews.js
 * 네이버/구글/배민/쿠팡 리뷰 수집 스크립트
 */

const fs = require('fs');
const path = require('path');

// 설정 로드
function loadConfig() {
  const configPath = path.join(process.env.HOME, '.openclaw/workspace/skills/review-manager/config.json');
  if (!fs.existsSync(configPath)) {
    console.error('❌ config.json 파일이 없습니다. config.template.json을 복사하세요.');
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
}

// 데이터 디렉토리 생성
function ensureDataDir(config) {
  const dataDir = config.dataDir.replace('~', process.env.HOME);
  const reviewsDir = path.join(dataDir, 'reviews');
  if (!fs.existsSync(reviewsDir)) {
    fs.mkdirSync(reviewsDir, { recursive: true });
  }
  return reviewsDir;
}

// 네이버 플레이스 리뷰 수집 (mock)
async function collectNaverReviews(storeId, url) {
  console.log(`📍 네이버 플레이스 리뷰 수집 중: ${storeId}`);
  // TODO: 실제 구현은 browser tool 또는 puppeteer 사용
  // 예시 데이터
  return [
    {
      platform: 'naver',
      reviewId: 'naver_001',
      author: '김**',
      rating: 5,
      content: '분위기 좋고 커피 맛있어요!',
      date: new Date().toISOString(),
      replied: false
    },
    {
      platform: 'naver',
      reviewId: 'naver_002',
      author: '이**',
      rating: 2,
      content: '직원이 불친절했습니다. 실망이에요.',
      date: new Date().toISOString(),
      replied: false
    }
  ];
}

// 구글 리뷰 수집 (mock)
async function collectGoogleReviews(storeId, placeId) {
  console.log(`🌍 구글 리뷰 수집 중: ${storeId}`);
  // TODO: Google Places API 또는 스크래핑
  return [
    {
      platform: 'google',
      reviewId: 'google_001',
      author: 'John D.',
      rating: 4,
      content: 'Good coffee, friendly staff',
      date: new Date().toISOString(),
      replied: false
    }
  ];
}

// 배민 리뷰 수집 (mock)
async function collectBaeminReviews(storeId, url) {
  console.log(`🛵 배민 리뷰 수집 중: ${storeId}`);
  // TODO: 로그인 필요, browser tool 활용
  return [];
}

// 쿠팡 리뷰 수집 (mock)
async function collectCoupangReviews(storeId, url) {
  console.log(`📦 쿠팡 리뷰 수집 중: ${storeId}`);
  // TODO: 로그인 필요, browser tool 활용
  return [];
}

// 리뷰 저장
function saveReviews(reviewsDir, storeId, platform, reviews) {
  const now = new Date();
  const month = now.toISOString().slice(0, 7); // YYYY-MM
  const filename = `${storeId}-${platform}-${month}.json`;
  const filepath = path.join(reviewsDir, filename);
  
  let existing = [];
  if (fs.existsSync(filepath)) {
    existing = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
  }
  
  // 중복 제거 (reviewId 기준)
  const existingIds = new Set(existing.map(r => r.reviewId));
  const newReviews = reviews.filter(r => !existingIds.has(r.reviewId));
  
  const merged = [...existing, ...newReviews];
  fs.writeFileSync(filepath, JSON.stringify(merged, null, 2));
  
  console.log(`💾 저장 완료: ${filename} (새 리뷰 ${newReviews.length}개)`);
  return newReviews.length;
}

// 메인
async function main() {
  const args = process.argv.slice(2);
  const storeFilter = args.includes('--store') ? args[args.indexOf('--store') + 1] : null;
  const platformFilter = args.includes('--platform') ? args[args.indexOf('--platform') + 1] : null;
  
  const config = loadConfig();
  const reviewsDir = ensureDataDir(config);
  
  let totalNew = 0;
  
  for (const store of config.stores) {
    if (storeFilter && store.id !== storeFilter) continue;
    
    console.log(`\n🏪 ${store.name} (${store.id})`);
    
    if ((!platformFilter || platformFilter === 'naver') && store.platforms.naver) {
      const reviews = await collectNaverReviews(store.id, store.platforms.naver);
      totalNew += saveReviews(reviewsDir, store.id, 'naver', reviews);
    }
    
    if ((!platformFilter || platformFilter === 'google') && store.platforms.google) {
      const reviews = await collectGoogleReviews(store.id, store.platforms.google);
      totalNew += saveReviews(reviewsDir, store.id, 'google', reviews);
    }
    
    if ((!platformFilter || platformFilter === 'baemin') && store.platforms.baemin) {
      const reviews = await collectBaeminReviews(store.id, store.platforms.baemin);
      totalNew += saveReviews(reviewsDir, store.id, 'baemin', reviews);
    }
    
    if ((!platformFilter || platformFilter === 'coupang') && store.platforms.coupang) {
      const reviews = await collectCoupangReviews(store.id, store.platforms.coupang);
      totalNew += saveReviews(reviewsDir, store.id, 'coupang', reviews);
    }
  }
  
  console.log(`\n✅ 수집 완료! 새 리뷰 총 ${totalNew}개`);
}

main().catch(err => {
  console.error('❌ 오류:', err.message);
  process.exit(1);
});
