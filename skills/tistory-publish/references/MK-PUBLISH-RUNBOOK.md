# 매경 리뷰 발행 런북 (Ruth용)

> 이 문서대로 위에서 아래로 순서대로 실행하면 됨. 판단 불필요.
> 문제 생기면 멈추고 Eli에게 보고.
> **최종 수정**: 2026-02-27 — OG 카드: prepareOGPlaceholder(JS) + Playwright Enter 조합으로 변경 (isTrusted 해결)

---

## 사전 조건
- 티스토리 로그인 완료 (Kakao 계정)
  - 로그인이 풀렸을 경우: 암호화된 credential 파일 참조 (경로는 내부 관리)
- `profile="openclaw"` 브라우저 사용

---

## -1단계: 원고 작성 (Ruth 담당, 발행 전 필수)

> ⚠️ **초안 작성은 Ruth 담당.** Eli가 하는 것이 아님.
> 크론이 깨어나면 발행 전에 반드시 원고부터 작성해야 함.

### 📅 일요일 특이사항
일요일은 매일경제 종이신문이 발행되지 않음.
**발행은 정상 진행**, 단 **배너 이미지 삽입(0단계)은 스킵**.

```bash
date "+%A"
```
출력이 `Sunday`면 → 0단계(배너 생성/삽입) 스킵. 나머지 단계(-1단계, 1단계~)는 그대로 진행.
대표이미지도 별도 설정 없이 발행.

---

0. **날짜/요일 확인 먼저** (제목에 틀린 요일 들어가는 사고 방지):
   ```bash
   date "+%Y년 %m월 %d일 (%A)"
   ```
   출력 예시: `2026년 02월 25일 (Wednesday)` → 제목엔 한국어로: `(수)`
   요일 영→한 변환: Mon=월, Tue=화, Wed=수, Thu=목, Fri=금, Sat=토, Sun=일
   **이 명령 결과를 기준으로 제목 작성. 추측 금지.**

1. 오늘 날짜 매경 1면 URL: `https://www.mk.co.kr/`에서 주요 기사 4개 선정
   - **중요**: 요일 확인 필수 (달력/시스템 날짜 대조). 기계적 추론 금지.
2. 각 기사 본문 읽고 요약 + "가리봉뉘우스의 한마디" 작성
   - **문단 규칙**: 문장 6~7개 이상이면 단락 나눔. 문장 하나씩 독립 문단 금지.
3. 아래 형식으로 원고 파일 저장:
   - 파일명: `~/.openclaw/workspace-ruth/blog-drafts/mk-review-YYYY-MM-DD.md`
   - 형식: `TEMPLATE-mk-review.md` 참조 (`~/.openclaw/workspace-ruth/blog-drafts/TEMPLATE-mk-review.md`)
4. 저장 확인 후 0단계로 진행

```
# 원고 파일 최소 구성 요소:
- title: [매경] YYYY.MM.DD(요일) - 키워드1, 키워드2, 키워드3
- intro: 들어가며 (2~4문장)
- articles: 4개 [{title, url, body, comment}]
- tags: 10개
```

---

## 0단계: 배너 생성

```bash
node ~/.openclaw/workspace-ruth/scripts/mk-banner.js
# 결과: /tmp/mk-banner-YYYY-MM-DD.jpg (1150×630)
# base64 분할은 더 이상 불필요 (v3: Playwright upload 사용)
```

---

## 1단계: 새 글 페이지 열기

```
browser navigate → https://bongman.tistory.com/manage/newpost
```

---

## 2단계: 카테고리 + 제목 설정

```javascript
// browser evaluate (tistory-publish.js 로드 후):
setCategory('신문 리뷰')
setTitle('[매경] 2026.MM.DD(요일) - 핵심키워드1, 키워드2, 키워드3')
```

---

## 3단계: 본문 삽입

```javascript
// 원고 파일에서 buildBlogHTML() 파라미터 구성 후:
const html = buildBlogHTML({ intro, articles });
insertContent(html);
// 검증: style1Count, hrCount, contentLength 확인
// 기대값: style1Count=4, hrCount=4, contentLength ≥ 4000
```

---

## 4단계: OG 카드 교체 (JS + Playwright 조합 필수)

> ⚠️ **JS 단독으로 OG 카드 생성 불가** — Tistory OG 파서는 `isTrusted=true` Enter만 인식.
> 반드시 `prepareOGPlaceholder()` (JS) → `browser press Enter` (Playwright) 순서로 실행.

```javascript
// 1. URL 목록 추출
const urls = getOGPlaceholders();
// urls = ["https://mk.co.kr/...", "https://mk.co.kr/...", ...]
```

각 URL에 대해 아래 3단계를 반복 (2~3초 간격):

```javascript
// 2-a. JS: placeholder를 URL 텍스트로 교체 + 커서 배치
prepareOGPlaceholder(urls[0])
// 반환: { success: true, editorFocused: true }
```

```
// 2-b. Playwright: 진짜 Enter 키 입력 → OG 파서 트리거
browser(action="act", profile="openclaw", request={kind:"press", key:"Enter"})
```

```
// 2-c. 3초 대기 후 OG 카드 렌더 확인
// (3초 대기)
```

```javascript
// 2-d. JS: OG 카드 확인 + URL 텍스트 잔여물 정리
verifyOGCard(urls[0])
// 반환: { found: true, ogCardCount: N, cleaned: true }
// found=false면 Enter가 안 먹힌 것 → 한 번 더 시도
```

> 4개 URL 모두 처리 후:
```javascript
cleanupOGResiduals()
// 최종 확인: { ogCards: 4, pendingRemoved: 0, rawUrlsRemoved: 0 }
// ogCards < 4면 필수 항목 실패 → 9-B단계(비공개 발행)로 진행
```

---

## 5단계: 배너 업로드 (Playwright upload 방식)

> v3: base64 청크 주입 폐지 → Playwright `upload` 액션으로 직접 파일 업로드.
> Tistory가 자동으로 서버(daumcdn.net)에 올려줌.

### 5-1. 업로드 입력 활성화
```javascript
// evaluate: 첨부 → 사진 메뉴 클릭 → input#openFile 활성화
await openBannerUploadInput()
// 반환: { success: true, note: 'Photo menu clicked...' }
```

### 5-2. Playwright로 파일 업로드
```
browser(action="upload", profile="openclaw", selector="#openFile", paths=["/tmp/mk-banner-YYYY-MM-DD.jpg"])
```

### 5-3. 업로드 확인 (3초 대기 후)
```javascript
// evaluate: 서버 업로드 확인
verifyBannerUpload()
// 성공: { success: true, isServer: true, src: 'https://img1.daumcdn.net/...' }
// 실패: { success: false, isBlob: true } 또는 { isData: true }
```

### 5-4. 실패 시
배너 업로드 실패 → **건너뛰지 말 것**. 실패 사유를 기록해두고 6단계로 진행.
발행 전 체크리스트(8단계 직전)에서 누락 항목으로 집계됨.

---

## 6단계: 대표이미지 설정

```javascript
// 배너가 에디터에 있는 경우:
setRepresentImageFromEditor()
// 성공 시: { success: true, imageUrl: 'https://...' }
// 실패 시: representFailed 변수에 기록. 건너뛰지 말 것.
```

---

## 7단계: 태그 입력

```javascript
setTags(["매경", "매일경제", "신문리뷰", "태그4", "태그5", "태그6", "태그7", "태그8", "태그9", "태그10"])
// 태그는 원고 파일 하단에 명시
// registered가 0이더라도 note: 'del buttons not found, assuming all tags registered'면 정상
```

> **태그 한 덩어리로 들어갔을 때**: `clearTags()` 후 `setTags()` 다시 실행.

---

## 8단계: 발행 전 체크리스트 (핵심 — 절대 생략 금지)

발행 전에 아래 항목을 직접 확인. 누락 항목에 따라 공개/비공개 결정.

```
필수 항목 (이 중 하나라도 실패 → 비공개 발행 + Eli 검수 요청):
  [ ] OG 카드 4개 렌더링 확인 (cleanupOGResiduals() 결과 ogCards === 4)
  [ ] 배너 이미지 에디터에 존재 (uploadBannerFromWindow() success === true)

권장 항목 (누락 시 Eli에게 알리되 발행은 진행 가능):
  [ ] 대표이미지 설정됨
  [ ] 태그 10개 칩 등록됨
  [ ] HR 구분선 4개 있음
```

### 판단 기준

**모든 필수 항목 통과** → 9-A단계(공개 발행)로 진행  
**필수 항목 1개 이상 실패** → 9-B단계(비공개 발행 + 검수 요청)로 진행

---

## 9-A단계: 공개 발행

```javascript
clickComplete()
// 1초 대기
clickPublish()  // 공개(20) 선택 확인 후 클릭
// 발행 완료 후 URL 확인 (https://bongman.tistory.com/NNNN)
```

발행 후 이 채널(#매경-리뷰-포스트-발행)에 결과 보고:
```
✅ [매경] 리뷰 발행 완료 — {URL}
체크리스트: OG×4 ✅ | 배너 ✅ | 대표이미지 ✅ | 태그10 ✅ | HR×4 ✅
```

---

## 9-B단계: 비공개 발행 + Eli 검수 요청

필수 항목 실패 시 — **공개 발행 금지**. 비공개(1)로 발행 후 Eli에게 검수 요청.

```javascript
clickComplete()
// 1초 대기
// 발행 다이얼로그에서 "비공개(1)" 선택 후 발행
clickPublish()  // 비공개 상태로 발행
```

발행 후 `sessions_send`로 Eli 메인 세션에 검수 요청:
```
sessions_send(
  agentId: "main",
  message: "📋 [매경 리뷰 검수 요청] {날짜}
  URL: {비공개 URL}
  누락 항목: {실패한 필수 항목 목록}
  초안 파일: ~/.openclaw/workspace-ruth/blog-drafts/mk-review-{날짜}.md
  → 확인 후 공개 전환 또는 수정 지시 부탁드립니다."
)
```

이 채널(#매경-리뷰-포스트-발행)에도 동시 보고:
```
⚠️ [매경] 리뷰 비공개 발행 — 검수 필요 — {URL}
누락: {항목}
Eli 검수 요청 전송 완료
```

---

## 문제 발생 시

| 증상 | 조치 |
|------|------|
| OG 카드 0개 | 필수 항목 실패 → 9-B단계로 |
| 배너 업로드 실패 | 필수 항목 실패 → 9-B단계로 |
| OG 카드 1~3개 (부분 성공) | 필수 항목 실패로 간주 → 9-B단계로 |
| 태그 한 덩어리 | `clearTags()` 후 `setTags()` 재실행 |
| 발행 버튼 안 보임 | `clickComplete()` 후 스냅샷 확인 |
| 기타 | **멈추고 Eli에게 Discord 보고** |

---

## 참고

- **베스트 프랙티스 포스트**: https://bongman.tistory.com/1299
- **스크립트 경로**: `~/.openclaw/workspace-ruth/scripts/tistory-publish.js`
- **배너 스크립트**: `~/.openclaw/workspace-ruth/scripts/mk-banner.js`
- **태그 목록 (매경 리뷰 공통)**: 원고 파일 하단 `tags:` 섹션 참조
- **tistory-publish.js 수정**: Eli만 가능
