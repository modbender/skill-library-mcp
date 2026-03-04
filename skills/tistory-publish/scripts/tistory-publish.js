/**
 * tistory-publish.js — 티스토리 매경 신문 리뷰 발행 자동화
 * 
 * 사용법: browser evaluate에서 이 스크립트의 함수들을 순서대로 호출
 * 
 * 전제조건:
 *   - 티스토리 로그인 완료 상태
 *   - https://bongman.tistory.com/manage/newpost 페이지에 있어야 함
 *   - 대표이미지용 배너 파일이 로컬에 준비되어 있어야 함
 * 
 * 순서:
 *   0. (사전) node mk-banner.js -c  — 매경 1면 1150x630 배너 생성 + 클립보드
 *   1. setCategory()           — 카테고리 "신문 리뷰" 선택
 *   2. setTitle(title)          — 제목 입력
 *   3. (에디터 맨 위 Cmd+V)     — 배너 이미지 붙여넣기
 *   4. insertContent(html)      — 본문 HTML 삽입 (OG placeholder 포함)
 *   5. getOGPlaceholders()      — OG URL 목록 추출
 *   6. replaceOGPlaceholder(url) × N — 각 URL에 OG 카드 생성 (2초 간격)
 *   7. setRepresentImage()      — 대표이미지 설정
 *   8. setTags(tags)            — 태그 입력
 *   9. clickComplete() → clickPublish() — 완료 → 공개 발행
 */

// ============================================================
// 1. HTML 생성 헬퍼
// ============================================================

/**
 * 기사 배열로부터 전체 블로그 HTML을 생성
 * 
 * @param {Object} params
 * @param {string} params.intro - 들어가며 본문 (여러 <p> 태그)
 * @param {Array} params.articles - [{title, url, body}] 배열
 *   - title: h2 제목 (예: "1. 삼성전자, HBM4 세계 최초 양산 출하")
 *   - url: 매경 기사 URL
 *   - body: 기사 본문 HTML (<p> 태그들)
 * @param {string} params.comment - 가리봉뉘우스의 한마디 본문
 * @returns {string} 완성된 HTML
 */
function buildBlogHTML({ intro, articles }) {
  const HR = '<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style1">';
  
  let html = '';
  
  // 들어가며
  html += '<h2 data-ke-size="size26">들어가며</h2>\n';
  html += intro + '\n';
  html += HR + '\n';
  
  // 각 기사 (코멘트는 각 기사 안에 포함)
  articles.forEach((article, i) => {
    html += `<h2 data-ke-size="size26">${article.title}</h2>\n`;
    // OG카드 자리: insertOGCard()로 에디터 네이티브 마크업 생성 (모바일 겹침 방지)
    // TinyMCE가 HTML 주석을 삭제할 수 있어서 data 속성 placeholder 사용
    html += `<p data-ke-size="size16" data-og-placeholder="${article.url}">&#8203;</p>\n`;
    html += article.body + '\n';
    // 코멘트: 각 기사 안에 삽입
    html += `<p data-ke-size="size16"><b>가리봉뉘우스의 한마디</b> - ${article.comment}`;
    // 마지막 기사면 "끝." 붙이기
    if (i === articles.length - 1) {
      html += ' 끝.</p>\n';
    } else {
      html += '</p>\n';
      html += HR + '\n';
    }
  });
  
  return html;
}


// ============================================================
// 2. 에디터 조작 함수들
// ============================================================

/**
 * 카테고리 선택 (셀렉트 박스에서 이름으로 선택)
 * @param {string} name - 카테고리 이름 (기본: "신문 리뷰")
 */
function setCategory(name = '신문 리뷰') {
  const select = document.getElementById('category');
  if (!select) return { success: false, error: 'category select not found' };
  
  const option = Array.from(select.options).find(o => o.text.trim() === name);
  if (!option) return { success: false, error: `category "${name}" not found` };
  
  select.value = option.value;
  select.dispatchEvent(new Event('change', { bubbles: true }));
  return { success: true, category: name };
}

/**
 * 제목 입력
 * @param {string} title - 글 제목
 */
function setTitle(title) {
  const titleEl = document.getElementById('post-title-inp');
  if (!titleEl) return { success: false, error: 'title input not found' };
  
  titleEl.textContent = title;
  titleEl.dispatchEvent(new Event('input', { bubbles: true }));
  return { success: true, title };
}

/**
 * TinyMCE에 data-ke 속성을 허용하도록 schema 등록
 * 반드시 setContent 전에 호출!
 */
function registerSchema() {
  const editor = tinymce.activeEditor;
  const schema = editor.schema;
  schema.addValidElements('hr[contenteditable|data-ke-type|data-ke-style]');
  return 'schema registered';
}

/**
 * HTML 본문을 에디터에 삽입
 * CodeMirror + TinyMCE 양쪽 모두 설정
 * 
 * @param {string} html - 삽입할 HTML
 */
function insertContent(html) {
  // 1. schema 등록 (data-ke 속성 보존)
  registerSchema();
  
  // 2. TinyMCE에 설정 (비주얼 에디터)
  const editor = tinymce.activeEditor;
  editor.setContent(html);
  editor.setDirty(true);
  editor.fire('change');
  editor.save(); // → hidden textarea에 동기화
  
  // 3. CodeMirror에 설정 (저장 시 원본 소스)
  const cm = document.querySelector('.CodeMirror');
  if (cm && cm.CodeMirror) {
    cm.CodeMirror.setValue(editor.getContent());
  }
  
  // 4. hidden textarea 직접 업데이트 (안전장치)
  document.querySelectorAll('textarea').forEach(t => {
    if (t.value.length > 5000) t.value = editor.getContent();
  });
  
  // 5. 검증
  const content = editor.getContent();
  const style1Count = (content.match(/data-ke-style="style1"/g) || []).length;
  const hrCount = (content.match(/<hr[^>]*>/gi) || []).length;
  
  return {
    success: true,
    style1Count,
    hrCount,
    contentLength: content.length
  };
}

/**
 * 완료 버튼 클릭 → 발행 다이얼로그 열기
 */
function clickComplete() {
  const btns = document.querySelectorAll('button');
  for (const btn of btns) {
    if (btn.textContent.trim() === '완료') {
      btn.click();
      return 'clicked 완료';
    }
  }
  return 'button not found';
}

/**
 * 공개 발행 버튼 클릭 (발행 다이얼로그에서)
 */
function clickPublish() {
  // 공개 라디오 선택 확인
  const publicRadio = document.querySelector('input[type="radio"][value="20"], input[type="radio"]');
  // 공개 발행 버튼 클릭 시도
  const publishBtn = document.querySelector('.btn_publish');
  if (publishBtn) {
    publishBtn.click();
    return 'clicked .btn_publish';
  }
  const btns = document.querySelectorAll('button');
  for (const btn of btns) {
    if (btn.textContent.includes('공개 발행')) {
      btn.click();
      return 'clicked 공개 발행';
    }
  }
  return 'publish button not found';
}


// ============================================================
// 3. 대표이미지 설정
// ============================================================

/**
 * 에디터 iframe 내 첫 번째 이미지를 클릭하고 대표이미지 버튼 활성화
 * (이미지는 미리 클립보드 붙여넣기로 삽입되어 있어야 함)
 */
function setRepresentImage() {
  // iframe 내 첫 번째 figure > img 클릭
  const iframe = document.querySelector('iframe');
  if (!iframe) return 'no iframe';
  
  const img = iframe.contentDocument.querySelector('figure img');
  if (!img) return 'no image in editor';
  
  img.click();
  
  // main document에서 대표이미지 버튼 찾기
  setTimeout(() => {
    const repBtn = document.querySelector('.mce-represent-image-btn');
    if (repBtn) {
      repBtn.click();
      return 'represent image set';
    }
  }, 500);
  
  return 'image clicked, waiting for represent button';
}


// ============================================================
// 4. 이미지 테두리 적용
// ============================================================

/**
 * 이미지 편집 → 테두리 → 아래에서 4번째 스타일 선택 → 완료
 * (이미지가 선택된 상태에서 호출)
 */
function applyImageBorder() {
  // 1. 인라인 툴바에서 "이미지 편집" 클릭
  const editBtns = document.querySelectorAll('.mce-inline-toolbar-grp button');
  for (const btn of editBtns) {
    if (btn.textContent.includes('이미지 편집') || btn.getAttribute('aria-label')?.includes('편집')) {
      btn.click();
      break;
    }
  }
  
  // 2~4는 타이밍 이슈로 별도 호출 필요
  return 'edit mode opened - call selectBorderStyle() next after 1s delay';
}

function selectBorderStyle() {
  // "테두리" 탭 클릭
  const tabs = document.querySelectorAll('nav li a.link_gnb');
  for (const tab of tabs) {
    if (tab.textContent.includes('테두리')) {
      tab.click();
      break;
    }
  }
  
  setTimeout(() => {
    // 아래에서 4번째 스타일 선택
    const items = document.querySelectorAll('button.cont_img');
    if (items.length >= 4) {
      items[items.length - 4].click();
    }
    
    setTimeout(() => {
      // 완료 버튼
      const doneBtn = document.querySelector('[role="contentinfo"] button');
      if (doneBtn) doneBtn.click();
    }, 500);
  }, 500);
  
  return 'border style selection initiated';
}


// ============================================================
// 5. OG 링크 카드 생성
// ============================================================

/**
 * URL을 에디터에 삽입하고 Enter를 쳐서 OG 카드 자동 생성
 * 
 * @param {string} url - 기사 URL
 * @param {Element} editor - tinymce editor instance
 */
/**
 * insertContent() 후 호출: data-og-placeholder 요소를 찾아 OG 카드 URL 목록 반환
 * Ruth가 이 목록을 순서대로 insertOGCard()에 넘기면 됨
 */
function getOGPlaceholders() {
  const editor = tinymce.activeEditor;
  const placeholders = editor.getBody().querySelectorAll('[data-og-placeholder]');
  return Array.from(placeholders).map(el => el.getAttribute('data-og-placeholder'));
}

/**
 * 특정 placeholder를 찾아서 커서를 거기로 이동시킨 뒤 OG 카드 삽입
 * @param {string} url - 기사 URL (data-og-placeholder 값과 매칭)
 */
/**
 * prepareOGPlaceholder(url) — placeholder를 URL 텍스트로 교체 + 커서 배치
 * 
 * 전략 (v3 — 2026-02-27):
 *   이 함수는 URL 텍스트 삽입 + 커서 배치만 함.
 *   Enter 키는 Playwright browser(press Enter)로 별도 입력해야 OG 파서가 트리거됨.
 *   (JS dispatchEvent/execCommand로는 isTrusted=false → Tistory OG 파서 무반응)
 * 
 * 사용법 (런북 4단계):
 *   1. evaluate: prepareOGPlaceholder(url)  ← 커서 배치
 *   2. browser: press Enter (Playwright)     ← 진짜 Enter → OG 카드 생성
 *   3. 2~3초 대기
 *   4. evaluate: verifyOGCard(url)           ← OG 카드 렌더 확인
 * 
 * @param {string} url - 기사 URL (data-og-placeholder 값과 매칭)
 * @returns {object} { success, url, editorFocused }
 */
function prepareOGPlaceholder(url) {
  const editor = tinymce.activeEditor;
  const placeholder = editor.getBody().querySelector(`[data-og-placeholder="${url}"]`);
  if (!placeholder) return { success: false, error: `placeholder not found for ${url}` };

  // 1. placeholder를 URL 전용 <p>로 교체 (인접 <p> 보존)
  const newP = editor.dom.create('p', { 'data-ke-size': 'size16' }, url);
  newP.setAttribute('data-og-url-pending', url);
  editor.dom.replace(newP, placeholder);

  // 2. 커서를 URL 텍스트 끝으로 이동
  const range = editor.dom.createRng();
  const textNode = newP.firstChild;
  if (textNode) {
    range.setStart(textNode, textNode.length);
    range.setEnd(textNode, textNode.length);
    editor.selection.setRng(range);
  }

  // 3. 에디터에 포커스 (Playwright Enter가 에디터로 가도록)
  editor.focus();

  return {
    success: true,
    url,
    editorFocused: true,
    note: 'Cursor placed at end of URL text. Now press Enter via Playwright browser tool.'
  };
}

/**
 * verifyOGCard(url) — OG 카드가 렌더됐는지 확인 + URL 텍스트 잔여물 정리
 * prepareOGPlaceholder() + Playwright Enter 후 2~3초 대기 뒤 호출
 * 
 * @param {string} url - 확인할 URL
 * @returns {object} { found, ogCardCount, cleaned }
 */
function verifyOGCard(url) {
  const editor = tinymce.activeEditor;
  const body = editor.getBody();

  // OG 카드 확인
  const ogCards = body.querySelectorAll(
    'figure[data-ke-type="opengraph"], .og-container, [data-og-host]'
  );

  // URL 텍스트 잔여물 정리
  let cleaned = false;
  const pending = body.querySelector(`[data-og-url-pending="${url}"]`);
  if (pending) {
    const text = pending.textContent.trim();
    if (text === url || text.startsWith('http')) {
      pending.remove();
      cleaned = true;
    } else {
      pending.innerHTML = pending.innerHTML.replace(url, '').trim();
      pending.removeAttribute('data-og-url-pending');
      if (!pending.textContent.trim()) { pending.remove(); cleaned = true; }
    }
  }

  return {
    found: ogCards.length > 0,
    ogCardCount: ogCards.length,
    cleaned,
    note: ogCards.length > 0 ? 'OG card rendered successfully' : 'OG card NOT found — Enter may not have triggered'
  };
}

/**
 * replaceOGPlaceholder(url) — 하위호환용 래퍼 (v2 방식, JS-only)
 * ⚠️ 이 함수는 OG 파서 트리거가 안 될 수 있음 (isTrusted 이슈)
 * 가능하면 prepareOGPlaceholder() + Playwright Enter 조합 사용 권장
 */
function replaceOGPlaceholder(url) {
  const result = prepareOGPlaceholder(url);
  if (!result.success) return result.error;

  // fallback: execCommand으로 줄바꿈 시도 (OG 파서 트리거 안 될 수 있음)
  const editor = tinymce.activeEditor;
  editor.execCommand('mceInsertNewLine');

  setTimeout(() => {
    try { verifyOGCard(url); } catch (e) {}
  }, 2000);

  return `OG placeholder prepared for ${url}. execCommand fallback used — OG card may NOT render.`;
}

/**
 * OG 카드 삽입 후 검증: 남아있는 URL 텍스트 잔여물 정리 + 카드 수 확인
 * 모든 replaceOGPlaceholder() 호출 완료 후 3초 대기 뒤 호출
 * 
 * @returns {object} { ogCards: number, pendingRemoved: number, rawUrlsRemoved: number }
 */
function cleanupOGResiduals() {
  const editor = tinymce.activeEditor;
  const body = editor.getBody();

  // 1. 아직 남아있는 data-og-url-pending <p> 제거
  const pendings = body.querySelectorAll('[data-og-url-pending]');
  let pendingRemoved = 0;
  pendings.forEach(p => {
    const text = p.textContent.trim();
    if (!text || text.startsWith('http')) {
      p.remove();
      pendingRemoved++;
    } else {
      // URL만 제거하고 나머지 보존
      const url = p.getAttribute('data-og-url-pending');
      p.innerHTML = p.innerHTML.replace(url, '').trim();
      p.removeAttribute('data-og-url-pending');
      if (!p.textContent.trim()) { p.remove(); pendingRemoved++; }
    }
  });

  // 2. 본문에 남은 naked URL 텍스트 제거 (mk.co.kr 패턴)
  let rawUrlsRemoved = 0;
  const allPs = body.querySelectorAll('p');
  allPs.forEach(p => {
    const text = p.textContent.trim();
    if (/^https?:\/\/[^\s]+$/.test(text) && text.includes('mk.co.kr')) {
      p.remove();
      rawUrlsRemoved++;
    }
  });

  // 3. OG 카드 수 확인
  const ogCards = body.querySelectorAll(
    'figure[data-ke-type="opengraph"], .og-container, [data-og-host]'
  ).length;

  editor.setDirty(true);
  editor.save();

  return { ogCards, pendingRemoved, rawUrlsRemoved };
}

function insertOGCard(url) {
  const editor = tinymce.activeEditor;

  // 1) 반드시 블록 시작(새 문단)에서 URL을 넣는 걸 추천
  // URL 텍스트 삽입
  editor.execCommand('mceInsertContent', false, url);

  // 2) iframe body에 Enter 키 이벤트 디스패치 → OG 카드 생성 트리거
  const body = editor.getBody();
  ['keydown', 'keypress', 'keyup'].forEach(type => {
    body.dispatchEvent(new KeyboardEvent(type, {
      key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
    }));
  });

  // 3) 모바일에서 OG카드 아래로 본문이 "겹쳐" 보이는 케이스 방지용:
  // OG 카드 생성 후 커서를 확실히 다음 블록으로 내려줌 (빈 문단 삽입)
  setTimeout(() => {
    try {
      editor.execCommand('mceInsertContent', false, '<p data-ke-size="size16"><br></p>');
    } catch (e) {}
  }, 1200);

  return 'URL inserted + Enter dispatched. Wait ~2s for OG card generation.';
}


// ============================================================
// 6. 태그 입력
// ============================================================

/**
 * 태그를 개별적으로 입력 + Enter로 등록
 * 티스토리 에디터의 #tagText input에 하나씩 넣고 Enter 쳐야 칩(chip)으로 등록됨
 * 
 * @param {string[]} tags - 태그 배열 (예: ["매경", "신문리뷰", "트럼프관세"])
 * @returns {Promise<object>} 결과
 */
async function setTags(tags) {
  const input = document.getElementById('tagText');
  if (!input) return { success: false, error: 'tagText input not found' };

  // nativeSetter: React/Tistory 라이브러리가 isTrusted 이벤트를 요구하므로
  // HTMLInputElement.prototype.value setter를 직접 호출해야 인식됨
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;

  const results = [];
  for (const tag of tags) {
    input.focus();

    // 네이티브 setter로 값 설정 → InputEvent 발생
    nativeSetter.call(input, tag);
    input.dispatchEvent(new InputEvent('input', {
      bubbles: true, cancelable: true, inputType: 'insertText', data: tag
    }));

    await new Promise(r => setTimeout(r, 200));

    // Enter 키 이벤트 (keydown + keypress + keyup)
    ['keydown', 'keypress', 'keyup'].forEach(type => {
      input.dispatchEvent(new KeyboardEvent(type, {
        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
      }));
    });

    await new Promise(r => setTimeout(r, 350));
    results.push(tag);
  }

  // 등록된 태그 칩 수 확인 (실제 DOM 셀렉터: 2026-02-22 확인)
  // 칩: .editor_tag .txt_tag  |  삭제 버튼: .editor_tag .txt_tag .btn_delete
  await new Promise(r => setTimeout(r, 400));
  const chips = document.querySelectorAll('.editor_tag .txt_tag');

  return {
    success: true,
    requested: tags.length,
    registered: chips.length,
    tags: results
  };
}

/**
 * 기존 태그 전부 삭제
 * @returns {object} 결과
 */
function clearTags() {
  // 실제 DOM 셀렉터: .editor_tag .txt_tag .btn_delete (2026-02-22 확인)
  const removeBtns = document.querySelectorAll('.editor_tag .txt_tag .btn_delete');
  let count = 0;
  removeBtns.forEach(btn => { btn.click(); count++; });
  return { success: true, removed: count };
}


// ============================================================
// 7. 배너 업로드
// ============================================================

// ---- v3 방식 (2026-02-27): Playwright upload 사용 ----
// 
// 순서 (런북 5단계):
//   1. node mk-banner.js → /tmp/mk-banner-YYYY-MM-DD.jpg 생성
//   2. evaluate: openBannerUploadInput()  ← "첨부 → 사진" 클릭, input#openFile 활성화
//   3. browser(upload, paths=["/tmp/mk-banner-YYYY-MM-DD.jpg"])  ← Playwright가 파일 주입
//   4. Tistory가 자동으로 서버 업로드 (daumcdn.net URL)
//   5. evaluate: verifyBannerUpload()  ← 이미지 src 확인
//
// base64 청크 방식(v2)은 제거됨.

/**
 * "첨부 → 사진" 메뉴를 클릭해서 input#openFile을 활성화
 * Playwright upload 전에 호출 필수
 */
function openBannerUploadInput() {
  // 커서를 에디터 맨 위로 이동 (배너가 글 상단에 삽입되도록)
  try {
    const editor = tinymce.activeEditor;
    const body = editor.getBody();
    const firstChild = body.firstChild;
    if (firstChild) {
      editor.selection.setCursorLocation(firstChild, 0);
      editor.focus();
    }
  } catch (e) { /* ignore */ }

  // 첨부 버튼 찾기
  const attachBtn = document.querySelector('button[class*="attach"], .btn_file, [aria-label*="첨부"]');
  if (!attachBtn) {
    // 툴바 버튼 중에서 찾기
    const btns = document.querySelectorAll('.mce-toolbar button, .editor-toolbar button');
    for (const btn of btns) {
      if (btn.textContent.includes('첨부') || btn.getAttribute('aria-label')?.includes('첨부')) {
        btn.click();
        break;
      }
    }
  } else {
    attachBtn.click();
  }

  // 사진 메뉴아이템 클릭 (약간의 딜레이 후)
  return new Promise(resolve => {
    setTimeout(() => {
      const menuItems = document.querySelectorAll('[role="menuitem"], .mce-menu-item');
      for (const item of menuItems) {
        if (item.textContent.includes('사진')) {
          item.click();
          resolve({ success: true, note: 'Photo menu clicked. input#openFile should now be active. Use browser(upload) next.' });
          return;
        }
      }
      resolve({ success: false, error: 'Photo menu item not found' });
    }, 500);
  });
}

/**
 * 배너 업로드 후 이미지가 서버에 올라갔는지 확인
 * Playwright upload 후 2~3초 대기 뒤 호출
 */
function verifyBannerUpload() {
  const editor = tinymce.activeEditor;
  const firstImg = editor.getBody().querySelector('img');
  if (!firstImg) return { success: false, error: 'no image in editor' };

  const src = firstImg.src;
  const isServer = src.startsWith('https://') && !src.startsWith('https://bongman.tistory.com/manage');
  const isBlob = src.startsWith('blob:');
  const isData = src.startsWith('data:');

  return {
    success: isServer,
    src: src.substring(0, 120),
    isServer,
    isBlob,
    isData,
    width: firstImg.naturalWidth,
    height: firstImg.naturalHeight,
    note: isServer ? 'Banner uploaded to server successfully' :
          isBlob ? 'Still blob URL — server upload pending' :
          isData ? 'Still data URL — server upload failed' :
          'Unknown state'
  };
}

// ---- 하위호환: base64 청크 방식 (deprecated) ----

/**
 * @deprecated v3에서 Playwright upload로 대체됨. 하위호환용으로만 유지.
 */
function injectBannerChunk(chunk, isFirst = false) {
  if (isFirst) {
    window._b64 = chunk;
  } else {
    window._b64 = (window._b64 || '') + chunk;
  }
  return { ok: true, totalLength: window._b64 ? window._b64.length : 0 };
}

/**
 * window._b64에 누적된 base64를 이미지로 변환해 에디터에 삽입 + 서버 업로드
 * 
 * 전략:
 *   A) TinyMCE images_upload_url이 설정된 경우 → FormData POST로 직접 업로드
 *   B) 없는 경우 → data URL로 에디터에 삽입 후 editorUpload.uploadImages() 호출
 * 
 * @param {string} mimeType - MIME 타입 (기본: 'image/jpeg')
 * @returns {Promise<object>} 결과
 */
async function uploadBannerFromWindow(mimeType = 'image/jpeg') {
  if (!window._b64 || window._b64.length === 0) {
    return { success: false, error: 'window._b64 is empty — inject chunks first' };
  }

  const editor = tinymce.activeEditor;
  if (!editor) return { success: false, error: 'no editor' };

  try {
    // base64 → Blob
    const byteStr = atob(window._b64);
    const bytes = new Uint8Array(byteStr.length);
    for (let i = 0; i < byteStr.length; i++) {
      bytes[i] = byteStr.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: mimeType });

    // A) 직접 업로드 시도 (TinyMCE upload URL 사용)
    const uploadUrl = editor.settings && editor.settings.images_upload_url;
    if (uploadUrl) {
      const fd = new FormData();
      fd.append('file', blob, 'banner.jpg');

      const resp = await fetch(uploadUrl, { method: 'POST', body: fd, credentials: 'include' });
      const data = await resp.json();
      const serverUrl = data.location || data.url || data.src || data.fileUrl;

      if (serverUrl) {
        const current = editor.getContent();
        editor.setContent(
          `<p data-ke-size="size16"><img src="${serverUrl}" width="1150" /></p>\n${current}`
        );
        editor.setDirty(true);
        editor.save();
        window._b64 = null;
        return { success: true, method: 'directUpload', url: serverUrl };
      }
    }

    // B) fallback: data URL 삽입 → uploadImages() 호출
    const dataUrl = `data:${mimeType};base64,${window._b64}`;
    const current = editor.getContent();
    editor.setContent(
      `<p data-ke-size="size16"><img src="${dataUrl}" width="1150" /></p>\n${current}`
    );
    editor.setDirty(true);

    // uploadImages()가 data URL img를 서버로 업로드하고 src 교체
    await new Promise(r => setTimeout(r, 500));
    const uploadResult = await editor.editorUpload.uploadImages();
    await new Promise(r => setTimeout(r, 2000));

    const firstImg = editor.getBody().querySelector('img');
    const finalUrl = firstImg ? firstImg.src : null;
    const uploaded = finalUrl && !finalUrl.startsWith('data:');

    window._b64 = null;
    return {
      success: uploaded,
      method: 'uploadImages',
      url: finalUrl,
      uploadResult,
      note: uploaded ? 'ok' : 'image may still be data URL — check editor'
    };

  } catch (e) {
    return { success: false, error: e.message };
  }
}

/**
 * 에디터의 첫 번째 이미지를 대표이미지로 설정 (업로드 후 호출)
 * 
 * 전략 (v2 — 2026-02-25):
 *   1. 에디터 iframe 내 첫 번째 img 클릭 → 인라인 툴바 활성화
 *   2. 여러 셀렉터로 대표이미지 버튼 탐색 (main doc + iframe 모두)
 *   3. 못 찾으면 버튼 목록 디버그 반환 (silent fail 방지)
 */
async function setRepresentImageFromEditor() {
  const editor = tinymce.activeEditor;
  const body = editor.getBody();
  const firstImg = body.querySelector('img');
  if (!firstImg) return { success: false, error: 'no image in editor' };

  const imgUrl = firstImg.src;
  if (imgUrl.startsWith('data:')) {
    return { success: false, error: 'image not uploaded yet (still data URL)' };
  }

  // 이미지 클릭 (에디터 내부)
  firstImg.click();
  await new Promise(r => setTimeout(r, 1000));

  // 대표이미지 버튼 셀렉터 목록 (가능한 모든 패턴)
  const candidates = [
    '.mce-represent-image-btn',
    '[class*="represent"]',
    '[class*="thumbnail"]',
    'button[aria-label*="대표"]',
    'button[title*="대표"]',
    'button[data-tooltip*="대표"]',
    '.btn_represent',
    '.represent_img',
    '[class*="RepresentImg"]',
    '[class*="representImg"]',
  ];

  // main document에서 탐색
  for (const sel of candidates) {
    const btn = document.querySelector(sel);
    if (btn) {
      btn.click();
      return { success: true, method: 'main-doc', selector: sel, imageUrl: imgUrl };
    }
  }

  // iframe 내부에서도 탐색
  try {
    const iframe = document.querySelector('iframe[id*="mce"], iframe[class*="editor"]');
    if (iframe && iframe.contentDocument) {
      for (const sel of candidates) {
        const btn = iframe.contentDocument.querySelector(sel);
        if (btn) {
          btn.click();
          return { success: true, method: 'iframe', selector: sel, imageUrl: imgUrl };
        }
      }
    }
  } catch (e) {}

  // 못 찾으면 현재 떠있는 버튼 목록 반환 (디버그용)
  const visibleBtns = Array.from(document.querySelectorAll('button')).filter(b => {
    const style = window.getComputedStyle(b);
    return style.display !== 'none' && style.visibility !== 'hidden' && b.offsetWidth > 0;
  }).map(b => ({
    text: b.textContent.trim().slice(0, 30),
    cls: b.className.slice(0, 60),
    ariaLabel: b.getAttribute('aria-label') || '',
  }));

  return {
    success: false,
    error: 'represent button not found',
    imageUrl: imgUrl,
    hint: '아래 버튼 중 대표이미지 버튼 찾아서 Eli에게 셀렉터 알려줘',
    visibleButtons: visibleBtns.slice(0, 20),
  };
}


// ============================================================
// 8. 배너 업로드 디버그/헬퍼
// ============================================================

/**
 * 현재 페이지(및 에디터 iframe)에서 input[type=file] 목록을 덤프
 * 배너 업로드가 안 될 때 "진짜" file input이 뭔지 확인용
 */
function dumpFileInputs() {
  const top = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
    id: i.id || null,
    name: i.name || null,
    accept: i.accept || null,
    multiple: !!i.multiple,
    disabled: !!i.disabled,
    hidden: !!i.hidden,
    style: (i.getAttribute('style') || '').slice(0, 160),
    className: i.className || null,
    parent: i.parentElement ? (i.parentElement.id || i.parentElement.className || i.parentElement.tagName) : null,
  }));

  let iframe = [];
  try {
    const fr = document.querySelector('iframe');
    const doc = fr?.contentDocument;
    if (doc) {
      iframe = Array.from(doc.querySelectorAll('input[type="file"]')).map(i => ({
        id: i.id || null,
        name: i.name || null,
        accept: i.accept || null,
        multiple: !!i.multiple,
        disabled: !!i.disabled,
        hidden: !!i.hidden,
        style: (i.getAttribute('style') || '').slice(0, 160),
        className: i.className || null,
      }));
    }
  } catch (e) {}

  return { topCount: top.length, top, iframeCount: iframe.length, iframe };
}

/**
 * 에디터 본문에 배너 이미지가 들어왔는지 빠르게 체크
 */
function getEditorImageCount() {
  const editor = tinymce.activeEditor;
  if (!editor) return { ok: false, error: 'no editor' };
  const imgs = editor.getBody().querySelectorAll('img');
  return { ok: true, imgCount: imgs.length };
}


// ============================================================
// 설정값 (매일 바뀌지 않는 고정값)
// ============================================================

const CONFIG = {
  separator: '<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style1">',
  category: '신문 리뷰',
  author: '가리봉뉘우스',
  mkImageUrlPattern: 'https://file2.mk.co.kr/mkde/{YYYY}/{MM}/{DD}/page/01_01_ORG.jpg',
  bannerCropSize: { width: 1150, height: 630 },
  topicEconomy: '경제',
};
