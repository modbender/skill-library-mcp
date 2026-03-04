# Naver Search Skill for OpenClaw

OpenClaw 에이전트가 네이버의 방대한 데이터를 카테고리별(웹, 뉴스, 쇼핑, 이미지, 비디오, 예약)로 정밀하게 활용할 수 있도록 설계된 스킬입니다. 모든 엔진은 SerpAPI를 기반으로 하며, 독립적인 스크립트 구조를 가져 안정적입니다.

## 🏗️ 전체 구조 (Architecture)

```text
naver-search/
├── .env                  # API 키 (SERPAPI_API_KEY)
├── SKILL.md              # [Agent 전용] 사용 가이드 및 명령어 명세
├── README.md             # [User 전용] 설치 및 정보 요약
├── requirements.txt      # 의존성 패키지 (serpapi)
├── lib/
│   └── naver_base.py     # 공용 통신 및 데이터 정제 엔진
└── scripts/
    ├── naver_search.py   # [Main] 모든 결과를 요약 취합하는 통합 어그리게이터
    ├── naver_web.py      # 웹/지식iN/블로그 검색
    ├── naver_news.py     # 뉴스 (최신순/기간 필터 완벽 지원)
    ├── naver_shopping.py # 쇼핑 (최저가/판매처 상세 정보)
    ├── naver_images.py   # 이미지 (썸네일 및 출처 정보)
    ├── naver_video.py    # 비디오 (YouTube/TikTok 플랫폼 연동)
    └── naver_booking.py  # 예약/장소 (지도 위치 및 예약 상품 정보)
```

## 🚀 빠른 시작 (Quick Start)

가장 권장되는 사용법은 **통합 검색**을 통해 전체적인 흐름을 파악하는 것입니다.

```bash
# 한 번의 실행으로 뉴스, 쇼핑, 이미지, 비디오 요약 결과를 통합 조회
python3 scripts/naver_search.py "검색어"
```

## 🛠️ 기능별 상세 명령어 (Detailed Usage)

에이전트는 필요에 따라 아래의 전문 엔진을 직접 호출하여 더 깊은 데이터를 확보할 수 있습니다.

| 엔진명 (-e) | 전문 스크립트 | 주요 특징 및 옵션 |
| :--- | :--- | :--- |
| **통합** | `naver_search.py` | 모든 카테고리 톱 결과를 한 뷰에 요약 출력 |
| **뉴스** | `naver_news.py` | `--sort 1`(최신순), `--time 1d`(1일 이내) 옵션으로 정확한 속보 확인 |
| **쇼핑** | `naver_shopping.py` | 가격(`price`), 평점, 판매처 링크 등 이커머스 최적화 데이터 |
| **이미지** | `naver_images.py` | `--num [개수]` 옵션으로 다량의 썸네일 및 출처 확보 |
| **비디오** | `naver_video.py` | 영상 플랫폼(유튜브 등) 링크 및 재생 시간 정보 확인 |
| **예약** | `naver_booking.py` | 업체 위치, 예약 링크, 예약 상품 정보(가격 등) 추출 |

## ⚙️ 설정 (Setup)

1. **의존성 설치**: `pip install -r requirements.txt`
2. **API 키 설정**: 루트의 `.env` 파일에 `SERPAPI_API_KEY=발급받은키` 형식으로 저장하세요.

---

### 💡 에이전트 팁 (Tips for Agents)
- 결과가 너무 많을 때는 `--format full` 대신 기본값인 `compact` 모드를 사용하세요.
- 프로그램 방식으로 데이터를 처리하려면 `--format json` 옵션을 사용하면 분석하기 쉬운 JSON 객체가 반환됩니다.
- 네이버 통합 검색 화면과 가장 유사한 데이터 흐름을 원하신다면 `naver_search.py`를 호출하세요.
