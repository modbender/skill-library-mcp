# 카카오 i 오픈빌더 v2 API 레퍼런스

> 출처: https://i.kakao.com/docs/skill-response-format  
> 이 문서는 `kakaotalk` 스킬에 필요한 핵심 부분만 요약한 것입니다.

---

## 웹훅 수신 형식 (Request)

카카오 오픈빌더가 스킬 서버로 전송하는 요청:

```json
{
  "bot": {
    "id": "봇 ID",
    "name": "봇 이름"
  },
  "intent": {
    "id": "블록 ID",
    "name": "폴백 블록"
  },
  "action": {
    "id": "액션 ID",
    "name": "액션 이름",
    "params": {},
    "clientExtra": {}
  },
  "userRequest": {
    "timezone": "Asia/Seoul",
    "params": {},
    "block": { "id": "블록 ID", "name": "블록 이름" },
    "utterance": "사용자가 입력한 텍스트",
    "lang": "ko",
    "user": {
      "id": "사용자 고유 ID (세션 관리에 활용)",
      "type": "botUserKey",
      "properties": {
        "plusfriendUserKey": "채널 친구 키 (카카오 채널 연결 시)"
      }
    }
  }
}
```

### 핵심 필드
| 필드 | 설명 |
|------|------|
| `userRequest.utterance` | 사용자 입력 텍스트 |
| `userRequest.user.id` | 사용자 고유 키 (세션 관리용) |
| `intent.name` | 어떤 블록에서 왔는지 (폴백 블록 등) |

---

## 응답 형식 (Response)

### 기본 구조

```json
{
  "version": "2.0",
  "template": {
    "outputs": [ /* 출력 컴포넌트 배열, 최대 3개 */ ],
    "quickReplies": [ /* 빠른 응답 버튼, 선택사항, 최대 10개 */ ]
  }
}
```

### SimpleText (텍스트 응답)

```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "simpleText": {
          "text": "응답 텍스트 (최대 1000자)"
        }
      }
    ]
  }
}
```

### QuickReplies (빠른 응답 버튼)

```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      { "simpleText": { "text": "응답 텍스트" } }
    ],
    "quickReplies": [
      {
        "label": "버튼 표시 텍스트",
        "action": "message",
        "messageText": "버튼 클릭 시 전송될 텍스트"
      }
    ]
  }
}
```

#### quickReplies action 종류
| action | 설명 |
|--------|------|
| `message` | 클릭 시 messageText를 발화로 전송 |
| `block`   | 특정 블록으로 이동 (blockId 필요) |
| `webLink` | 외부 URL 열기 (webLinkUrl 필요) |

### SimpleImage (이미지 응답)

```json
{
  "simpleImage": {
    "imageUrl": "https://example.com/image.jpg",
    "altText": "이미지 설명"
  }
}
```

### BasicCard (카드형 응답)

```json
{
  "basicCard": {
    "title": "카드 제목",
    "description": "카드 설명",
    "thumbnail": {
      "imageUrl": "https://example.com/thumb.jpg"
    },
    "buttons": [
      {
        "label": "버튼",
        "action": "webLink",
        "webLinkUrl": "https://example.com"
      }
    ]
  }
}
```

---

## 제약 사항

| 항목 | 제한 |
|------|------|
| 응답 시간 | **5초 이내** (초과 시 오픈빌더 자체 오류 메시지 표시) |
| simpleText 길이 | **최대 1000자** (kakaotalk 스킬은 900자로 안전 마진) |
| outputs 개수 | **최대 3개** |
| quickReplies 개수 | **최대 10개** |
| HTTP 상태 코드 | 반드시 **200** (에러도 200 + simpleText로 처리) |

---

## 오픈빌더 스킬 서버 등록 방법

1. [카카오 i 오픈빌더](https://i.kakao.com) 접속
2. 봇 선택 → **스킬** 메뉴
3. **스킬 추가** → 스킬 서버 URL 입력:
   ```
   https://<ngrok_or_server>/kakao
   ```
4. **저장** 후 **시나리오** → **폴백 블록** → **스킬 연결**

---

## 서명 검증 (선택)

카카오는 요청 시 `X-Kakao-Signature` 헤더에 HMAC-SHA1 서명을 포함합니다.

```
X-Kakao-Signature: <hex_digest>
```

검증 방식:
```python
import hmac, hashlib
expected = hmac.new(
    secret.encode("utf-8"),
    body_bytes,          # raw request body
    hashlib.sha1,
).hexdigest()
valid = hmac.compare_digest(expected, received_signature)
```

`KAKAO_CALLBACK_SECRET` 환경변수가 없으면 검증을 건너뜁니다.

---

## 헬스체크 엔드포인트

```
GET http://localhost:8401/health
```

응답:
```json
{
  "status": "ok",
  "port": 8401,
  "active_sessions": 3,
  "pending_responses": 0
}
```

---

## 테스트 curl 예시

```bash
# 기본 대화 테스트
curl -s -X POST http://localhost:8401/kakao \
  -H "Content-Type: application/json" \
  -d '{
    "userRequest": {
      "utterance": "TIPS 신청하려면 어떻게 해야 해?",
      "user": {"id": "test_user_001"}
    },
    "bot": {"id": "test_bot"},
    "intent": {"name": "폴백 블록"}
  }' | python3 -m json.tool

# 세션 초기화
curl -s -X POST http://localhost:8401/kakao \
  -H "Content-Type: application/json" \
  -d '{
    "userRequest": {"utterance": "처음으로", "user": {"id": "test_user_001"}},
    "bot": {"id": "test_bot"},
    "intent": {"name": "폴백 블록"}
  }' | python3 -m json.tool

# "다시 물어보기" (LLM 타임아웃 후 재조회)
curl -s -X POST http://localhost:8401/kakao \
  -H "Content-Type: application/json" \
  -d '{
    "userRequest": {"utterance": "다시 물어보기", "user": {"id": "test_user_001"}},
    "bot": {"id": "test_bot"},
    "intent": {"name": "폴백 블록"}
  }' | python3 -m json.tool
```
