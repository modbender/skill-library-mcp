# KIS Stock Expert

한국투자증권 API를 활용하여 국내 주식 시세 조회, 계좌 잔고 확인 및 매매 주문을 수행합니다.

## Configuration

이 스킬을 사용하려면 다음 환경 변수가 설정되어 있어야 합니다:
- `KIS_APP_KEY`: 한국투자증권 앱 키
- `KIS_APP_SECRET`: 한국투자증권 앱 시크릿
- `KIS_ACCOUNT_NO`: 계좌번호 (8자리-2자리)
- `KIS_TRADE_SCRIPT_PATH`: `kis_trade.py` 파일이 위치한 로컬 경로

## Instructions

1. 모든 매매 주문(`execute_order`)을 실행하기 전, 반드시 사용자에게 종목명, 수량, 가격을 다시 한번 확인받아야 합니다.
2. 사용자의 명확한 승인(예: "응, 주문해줘") 없이는 절대로 주문 도구를 호출하지 마십시오.
3. 시세 조회 및 잔고 확인은 사용자의 요청 시 즉시 수행합니다.

## Tools

### get_my_portfolio
내 계좌의 총 자산, 예수금, 수익률 및 현재 보유 중인 종목 리스트를 조회합니다.

**Command:**
python "{{KIS_TRADE_SCRIPT_PATH}}" balance

### get_stock_price
특정 종목의 현재가를 조회합니다.
- `symbol` (string): 6자리 종목코드 (예: '005930')

**Command:**
python "{{KIS_TRADE_SCRIPT_PATH}}" price {{symbol}}

### execute_order
주식을 매수하거나 매도합니다. **반드시 사전에 사용자의 확답을 받으세요.**
- `symbol` (string): 종목코드
- `qty` (number): 수량
- `price` (number): 주문 가격
- `side` (string): 'BUY' 또는 'SELL'

**Command:**
python "{{KIS_TRADE_SCRIPT_PATH}}" order {{symbol}} {{qty}} {{price}} {{side}}