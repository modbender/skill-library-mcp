# 라온 웹챗 위젯 — 임베드 가이드

## 빠른 시작

k-startup.ai (또는 다른 웹사이트)에 아래 한 줄 추가:

```html
<script src="https://k-startup.ai/widget/raon-chat.min.js" data-api="https://api.k-startup.ai"></script>
```

끝. `</body>` 바로 위에 넣으면 된다.

## 옵션 (data 속성)

| 속성 | 기본값 | 설명 |
|------|--------|------|
| `data-api` | `http://localhost:8400` | raon-os server.py API URL |
| `data-title` | `라온 AI 비서` | 위젯 헤더 제목 |
| `data-model` | `qwen3:8b` | Ollama 모델명 |

## 파일 구성

| 파일 | 용도 |
|------|------|
| `raon-chat.js` | 개발용 (8.7KB, 주석 포함) |
| `raon-chat.min.js` | 프로덕션용 (6.9KB, minified) |
| `raon-chat.html` | 독립 실행 프리뷰 |

## 서버 요구사항

1. **raon-os server.py** 실행 중이어야 함 (port 8400)
2. CORS `*` 설정 완료 (외부 도메인에서 호출 가능)
3. launchd로 상시 구동: `raon.sh install`

## 배포 체크리스트

- [ ] server.py를 프로덕션 서버에 배포 (또는 Mac Studio에서 구동 + 도메인 연결)
- [ ] `data-api` URL을 실제 API 엔드포인트로 변경
- [ ] SSL/HTTPS 적용 (mixed content 방지)
- [ ] raon-chat.min.js를 k-startup.ai에 호스팅
- [ ] 테스트: PDF 업로드, 각 모드(평가/개선/매칭/체크리스트) 동작 확인

## 배포 옵션

### A. 정적 호스팅 (권장)
k-startup.ai가 Vercel/Netlify라면 `public/` 또는 `static/`에 `raon-chat.min.js` 복사.

### B. CDN
npm 퍼블리시 후 unpkg/jsdelivr 사용:
```html
<script src="https://unpkg.com/@yeomyeonggeori/raon-os@latest/widget/raon-chat.min.js" data-api="https://api.k-startup.ai"></script>
```

### C. 인라인
8KB 미만이므로 HTML에 직접 인라인도 가능.

## API 엔드포인트

위젯이 호출하는 API:

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/v1/evaluate` | 사업계획서 평가 |
| POST | `/v1/improve` | 개선안 생성 |
| POST | `/v1/match` | 지원사업 매칭 |
| POST | `/v1/checklist` | 체크리스트 생성 |

Body: `{ "text": "...", "model": "qwen3:8b", "pdf_base64": "..." }`
