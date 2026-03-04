#!/usr/bin/env node
/**
 * insta-cli/post.js — Instagram 게시물 자동 업로드
 * 
 * puppeteer-core로 OpenClaw 브라우저(CDP 18800) 연결
 * 이미지 업로드 → 캡션 입력 → 게시물 공유
 * 
 * 사용법:
 *   node post.js --images "img1.jpg,img2.jpg" --caption "캡션 텍스트"
 * 
 * 주의:
 * - OpenClaw 브라우저 실행 필요 (포트 18800)
 * - JPG만 지원 (PNG는 Instagram 에러 발생)
 * - input[type=file][2]가 게시물 업로드용 input
 */

const puppeteer = require('puppeteer-core');
const { program } = require('commander');
const path = require('path');
const fs = require('fs');

const BROWSER_PORT = process.env.BROWSER_PORT || '18800';
const CDP_URL = `http://127.0.0.1:${BROWSER_PORT}`;
const INSTAGRAM_URL = 'https://www.instagram.com/';

async function connectBrowser() {
  try {
    const browser = await puppeteer.connect({
      browserURL: CDP_URL,
      defaultViewport: null
    });
    return browser;
  } catch (e) {
    throw new Error(`브라우저 연결 실패 (포트 ${BROWSER_PORT}): ${e.message}`);
  }
}

async function findOrCreateInstagramPage(browser) {
  const pages = await browser.pages();
  
  // 기존 Instagram 탭 찾기
  let page = pages.find(p => p.url().includes('instagram.com'));
  
  if (page) {
    await page.bringToFront();
  } else {
    // 새 탭 열기
    page = await browser.newPage();
    await page.goto(INSTAGRAM_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  }
  
  // 로그인 확인 (로그인 페이지면 에러)
  const url = page.url();
  if (url.includes('/accounts/login')) {
    throw new Error('Instagram 로그인이 필요합니다. 브라우저에서 로그인 후 다시 시도해주세요.');
  }
  
  return page;
}

async function waitAndClick(page, selector, timeout = 10000) {
  await page.waitForSelector(selector, { visible: true, timeout });
  await page.click(selector);
  await page.waitForTimeout(1000); // 애니메이션 대기
}

async function uploadPost(images, caption) {
  const browser = await connectBrowser();
  
  try {
    const page = await findOrCreateInstagramPage(browser);
    
    // 1. 홈 페이지로 이동 (게시물 만들기 버튼이 있는 곳)
    if (!page.url().startsWith(INSTAGRAM_URL) || page.url().includes('/direct/')) {
      await page.goto(INSTAGRAM_URL, { waitUntil: 'networkidle2', timeout: 30000 });
    }
    
    // 2. "만들기" 또는 "새 게시물" 버튼 클릭
    // Instagram UI: 사이드바의 "만들기" 링크 또는 + 버튼
    // 여러 셀렉터 시도 (Instagram UI는 자주 바뀜)
    const createSelectors = [
      'a[href="#"]', // "만들기" 링크 (보통 SVG 포함)
      'svg[aria-label="새로운 게시물"]',
      'svg[aria-label="New post"]',
      'svg[aria-label="만들기"]',
      'svg[aria-label="Create"]',
      '[aria-label="새로운 게시물"]',
      '[aria-label="New post"]'
    ];
    
    let createClicked = false;
    for (const selector of createSelectors) {
      try {
        const elem = await page.$(selector);
        if (elem) {
          await elem.click();
          await page.waitForTimeout(1500);
          createClicked = true;
          break;
        }
      } catch (e) {
        // 다음 셀렉터 시도
      }
    }
    
    if (!createClicked) {
      // 폴백: "만들기" 텍스트가 포함된 링크 클릭
      const createLinks = await page.$$('a');
      for (const link of createLinks) {
        const text = await page.evaluate(el => el.innerText, link);
        if (text && (text.includes('만들기') || text.includes('Create'))) {
          await link.click();
          await page.waitForTimeout(1500);
          createClicked = true;
          break;
        }
      }
    }
    
    if (!createClicked) {
      throw new Error('게시물 만들기 버튼을 찾을 수 없습니다. Instagram UI가 변경되었을 수 있습니다.');
    }
    
    // 3. 파일 input 찾기 및 업로드
    // input[type=file][2] (accept에 video 포함된 3번째 input)
    await page.waitForTimeout(2000); // 다이얼로그 로딩 대기
    
    const fileInputs = await page.$$('input[type="file"]');
    
    if (fileInputs.length === 0) {
      throw new Error(`파일 input을 찾을 수 없습니다.`);
    }
    
    // 마지막 file input 사용 (Instagram UI 변경에 대응)
    const fileInput = fileInputs[fileInputs.length - 1];
    
    // 이미지 파일 경로를 절대 경로로 변환
    const imagePaths = images.split(',').map(img => {
      const trimmed = img.trim();
      if (path.isAbsolute(trimmed)) return trimmed;
      return path.resolve(process.cwd(), trimmed);
    });
    
    // 파일 존재 확인
    for (const imgPath of imagePaths) {
      if (!fs.existsSync(imgPath)) {
        throw new Error(`파일을 찾을 수 없습니다: ${imgPath}`);
      }
      // JPG 확인 (권장)
      const ext = path.extname(imgPath).toLowerCase();
      if (ext === '.png') {
        console.warn(`경고: ${path.basename(imgPath)}는 PNG입니다. Instagram은 JPG를 권장합니다.`);
      }
    }
    
    // 파일 업로드
    await fileInput.uploadFile(...imagePaths);
    await page.waitForTimeout(3000); // 업로드 및 미리보기 로딩 대기
    
    // 4. "다음" 버튼 클릭 (크롭/확대 화면)
    const nextSelectors = [
      'button:has-text("다음")',
      'button:has-text("Next")',
      '[role="button"]:has-text("다음")',
      '[role="button"]:has-text("Next")'
    ];
    
    let nextClicked = false;
    for (const selector of nextSelectors) {
      try {
        await page.waitForSelector(selector, { visible: true, timeout: 5000 });
        await page.click(selector);
        await page.waitForTimeout(1500);
        nextClicked = true;
        break;
      } catch (e) {
        // 다음 셀렉터 시도
      }
    }
    
    if (!nextClicked) {
      // 폴백: "다음" 텍스트 버튼 찾기
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.innerText, btn);
        if (text && (text.includes('다음') || text.toLowerCase().includes('next'))) {
          await btn.click();
          await page.waitForTimeout(1500);
          nextClicked = true;
          break;
        }
      }
    }
    
    if (!nextClicked) {
      throw new Error('첫 번째 "다음" 버튼을 찾을 수 없습니다.');
    }
    
    // 5. "다음" 버튼 클릭 (필터 화면 스킵)
    await page.waitForTimeout(1500);
    
    nextClicked = false;
    for (const selector of nextSelectors) {
      try {
        await page.waitForSelector(selector, { visible: true, timeout: 5000 });
        await page.click(selector);
        await page.waitForTimeout(1500);
        nextClicked = true;
        break;
      } catch (e) {
        // 다음 셀렉터 시도
      }
    }
    
    if (!nextClicked) {
      // 폴백
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.innerText, btn);
        if (text && (text.includes('다음') || text.toLowerCase().includes('next'))) {
          await btn.click();
          await page.waitForTimeout(1500);
          nextClicked = true;
          break;
        }
      }
    }
    
    if (!nextClicked) {
      throw new Error('두 번째 "다음" 버튼을 찾을 수 없습니다.');
    }
    
    // 6. 캡션 입력
    await page.waitForTimeout(1500);
    
    const captionSelectors = [
      'textarea[aria-label="문구 입력..."]',
      'textarea[aria-label="Write a caption..."]',
      'textarea[placeholder="문구 입력..."]',
      'textarea[placeholder="Write a caption..."]',
      'textarea'
    ];
    
    let captionInput = null;
    for (const selector of captionSelectors) {
      try {
        captionInput = await page.waitForSelector(selector, { visible: true, timeout: 5000 });
        break;
      } catch (e) {
        // 다음 셀렉터 시도
      }
    }
    
    if (!captionInput) {
      throw new Error('캡션 입력 필드를 찾을 수 없습니다.');
    }
    
    await captionInput.click();
    await page.waitForTimeout(500);
    await captionInput.type(caption, { delay: 50 }); // 자연스러운 타이핑
    await page.waitForTimeout(1000);
    
    // 7. "공유하기" 버튼 클릭
    const shareSelectors = [
      'button:has-text("공유하기")',
      'button:has-text("Share")',
      '[role="button"]:has-text("공유하기")',
      '[role="button"]:has-text("Share")'
    ];
    
    let shareClicked = false;
    for (const selector of shareSelectors) {
      try {
        await page.waitForSelector(selector, { visible: true, timeout: 5000 });
        await page.click(selector);
        await page.waitForTimeout(2000);
        shareClicked = true;
        break;
      } catch (e) {
        // 다음 셀렉터 시도
      }
    }
    
    if (!shareClicked) {
      // 폴백
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.innerText, btn);
        if (text && (text.includes('공유하기') || text.toLowerCase().includes('share'))) {
          await btn.click();
          await page.waitForTimeout(2000);
          shareClicked = true;
          break;
        }
      }
    }
    
    if (!shareClicked) {
      throw new Error('"공유하기" 버튼을 찾을 수 없습니다.');
    }
    
    // 8. 성공 확인 ("게시물이 공유되었습니다" 메시지 대기)
    try {
      await page.waitForFunction(
        () => {
          const text = document.body.innerText;
          return text.includes('게시물이 공유되었습니다') || 
                 text.includes('Post shared') ||
                 text.includes('Your post has been shared');
        },
        { timeout: 15000 }
      );
      
      const result = {
        success: true,
        images: imagePaths.map(p => path.basename(p)),
        caption: caption.substring(0, 100) + (caption.length > 100 ? '...' : ''),
        timestamp: new Date().toISOString()
      };
      
      console.log(JSON.stringify(result, null, 2));
      
    } catch (e) {
      // 성공 메시지를 못 찾아도 일단 시도는 완료
      console.log(JSON.stringify({
        success: 'uncertain',
        message: '게시물 공유 완료 메시지를 확인하지 못했습니다. Instagram 페이지를 직접 확인해주세요.',
        images: imagePaths.map(p => path.basename(p)),
        caption: caption.substring(0, 100),
        warning: e.message
      }, null, 2));
    }
    
    await browser.disconnect();
    
  } catch (error) {
    await browser.disconnect();
    console.log(JSON.stringify({
      success: false,
      error: error.message,
      stack: error.stack?.split('\n').slice(0, 5)
    }, null, 2));
    process.exit(1);
  }
}

// ─── CLI ───

program
  .name('insta-post')
  .description('Instagram 게시물 자동 업로드')
  .version('1.0.0')
  .requiredOption('-i, --images <paths>', '이미지 파일 경로 (쉼표 구분, 예: "img1.jpg,img2.jpg")')
  .requiredOption('-c, --caption <text>', '캡션 텍스트')
  .action((opts) => {
    uploadPost(opts.images, opts.caption);
  });

program.parse();
