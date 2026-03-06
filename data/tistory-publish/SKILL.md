---
name: tistory-publish
description: Automate Tistory blog publishing via browser automation (Playwright). Use when publishing posts to Tistory blogs — handles TinyMCE editor manipulation, OG card insertion, banner upload, tag registration, category setting, and representative image selection. Works around Tistory's isTrusted event filtering. Requires OpenClaw with Playwright browser profile.
---

# Tistory Publish

티스토리 블로그 자동 발행 스킬. Tistory Open API 종료(2024.02) 이후 유일한 자동화 경로인 브라우저 자동화를 제공합니다.

## 전제 조건

- OpenClaw + Playwright 브라우저 프로필 (`profile="openclaw"`)
- 티스토리 블로그 (Kakao 계정 로그인 완료)
- Node.js 18+ (`@napi-rs/canvas` — 배너 생성용)

## 핵심 파일

| 파일 | 용도 |
|------|------|
| `scripts/tistory-publish.js` | 에디터 조작 함수 모음 (browser evaluate로 로드) |
| `scripts/mk-banner.js` | 배너 이미지 생성 (1150×630) |
| `blog-drafts/MK-PUBLISH-RUNBOOK.md` | 발행 순서 런북 (전체 워크플로우) |
| `blog-drafts/TEMPLATE-mk-review.md` | 원고 작성 템플릿 |

## 발행 워크플로우 (요약)

전체 순서는 [MK-PUBLISH-RUNBOOK.md](blog-drafts/MK-PUBLISH-RUNBOOK.md) 참조.

```
-1. 원고 작성 (기사 선정 → 요약 → 코멘트)
 0. 배너 생성: node scripts/mk-banner.js
 1. 새 글 페이지: browser navigate → /manage/newpost
 2. 카테고리 + 제목: setCategory() + setTitle()
 3. 본문 삽입: buildBlogHTML() → insertContent()
 4. OG 카드: prepareOGPlaceholder() → Playwright Enter → verifyOGCard()
 5. 배너 업로드: openBannerUploadInput() → browser upload
 6. 대표이미지: setRepresentImageFromEditor()
 7. 태그: setTags([...])
 8. 체크리스트 확인 (필수: OG×4, 배너 / 권장: 대표이미지, 태그)
 9. 발행 (A: 공개 / B: 비공개+검수 요청)
```

## 주요 함수 (`tistory-publish.js`)

모든 함수는 `browser evaluate`로 실행. 스크립트를 먼저 페이지에 로드한 뒤 호출.

### 콘텐츠 삽입
- `buildBlogHTML({intro, articles})` — HTML 생성 (OG placeholder 포함)
- `insertContent(html)` — TinyMCE에 HTML 삽입 (CodeMirror 동기화)
- `registerSchema()` — `data-ke-*` 속성 허용 등록 (insertContent 전 호출)

### OG 카드 (isTrusted 우회 필수)
- `getOGPlaceholders()` — placeholder URL 목록 반환
- `prepareOGPlaceholder(url)` — placeholder를 URL 텍스트로 교체 + 커서 위치
- `verifyOGCard(url)` — OG 카드 렌더링 확인 + URL 잔여물 정리
- `cleanupOGResiduals()` — 남은 URL 텍스트 전체 정리

> ⚠️ OG 카드는 JS 단독 불가. `prepareOGPlaceholder()` 후 반드시 `browser press Enter` (Playwright)로 isTrusted=true 이벤트를 보내야 Tistory OG 파서가 트리거됨.

### 배너
- `openBannerUploadInput()` — 커서를 에디터 상단으로 이동 후 첨부 메뉴 활성화
- `verifyBannerUpload()` — 업로드된 이미지가 서버 URL인지 확인

### 메타데이터
- `setCategory(name)` — 카테고리 셀렉트 박스에서 선택
- `setTitle(title)` — 제목 입력
- `setTags(tags[])` — 태그 등록 (nativeSetter + InputEvent + KeyboardEvent)
- `clearTags()` — 기존 태그 전체 삭제

### 대표이미지
- `setRepresentImageFromEditor()` — 에디터 내 첫 번째 서버 이미지를 대표이미지로 설정

### 발행
- `clickPublish()` — 발행 버튼 클릭

## 설정 커스터마이징

이 스킬은 매경 리뷰를 예시로 포함하고 있지만, 다른 용도로도 사용 가능합니다:

1. `blog-drafts/TEMPLATE-mk-review.md`를 복사해서 자신의 템플릿 작성
2. `buildBlogHTML()`에 전달하는 `{intro, articles}` 구조만 맞추면 어떤 콘텐츠든 발행 가능
3. `setCategory()`, `setTitle()`, `setTags()`로 메타데이터 설정
4. 배너는 `mk-banner.js`를 수정하거나 직접 이미지 파일 준비

## 알려진 제약

- Tistory 에디터가 `isTrusted=false` 이벤트를 무시 → OG/태그에 우회 로직 필요
- 배너 파일 다이얼로그를 JS로 제어 불가 → Playwright upload 액션 사용
- 대표이미지 셀렉터가 Tistory 업데이트마다 변경될 수 있음 (v2에서 10가지 변형 대응)
