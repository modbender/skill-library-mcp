"""
KIS API 공통 모듈 - 인증, 설정, API 호출
"""
import os
import sys
import json
import time
import configparser
import requests
from datetime import datetime
from typing import Optional, Dict

# API 호출 속도 제한
_last_api_call_time = None
_MIN_API_INTERVAL = 0.06  # 60ms (초당 ~16건, KIS 제한: 20건)

def load_config(config_path: str) -> dict:
    """설정 파일 로드"""
    config_path = os.path.expanduser(config_path)
    if not os.path.exists(config_path):
        print(f"❌ 설정 파일을 찾을 수 없습니다: {config_path}")
        print(f"📝 설정 파일을 생성하세요:")
        print(f"   mkdir -p ~/.kis-trading")
        print(f"   cp config.ini.example ~/.kis-trading/config.ini")
        sys.exit(1)

    cp = configparser.ConfigParser()
    cp.read(config_path, encoding='utf-8')

    if 'KIS' not in cp:
        print("❌ 설정 파일에 [KIS] 섹션이 없습니다.")
        sys.exit(1)

    section = cp['KIS']
    required = ['APP_KEY', 'APP_SECRET', 'ACCOUNT_NO']
    for key in required:
        if not section.get(key):
            print(f"❌ 설정값 누락: {key}")
            sys.exit(1)

    acct = section['ACCOUNT_NO'].replace('-', '')
    return {
        'app_key': section['APP_KEY'],
        'app_secret': section['APP_SECRET'],
        'account_no': acct[:8],
        'product_code': acct[8:10] if len(acct) >= 10 else '01',
        'base_url': section.get('BASE_URL', 'https://openapi.koreainvestment.com:9443'),
    }


# 토큰 캐시
_token_cache = {'token': None, 'expired': None}
_TOKEN_FILE = os.path.expanduser('~/.kis-trading/token.json')


def _save_token(token: str, expired: str):
    """토큰 파일 저장 (권한 600)"""
    os.makedirs(os.path.dirname(_TOKEN_FILE), exist_ok=True)
    with open(_TOKEN_FILE, 'w') as f:
        json.dump({'token': token, 'expired': expired}, f)
    try:
        os.chmod(_TOKEN_FILE, 0o600)
    except OSError:
        pass


def _load_token() -> Optional[str]:
    """토큰 파일 로드 (유효한 경우만)"""
    try:
        with open(_TOKEN_FILE) as f:
            data = json.load(f)
        if data.get('expired') and datetime.strptime(data['expired'], '%Y-%m-%d %H:%M:%S') > datetime.now():
            return data['token']
    except:
        pass
    return None


def get_token(cfg: dict) -> str:
    """액세스 토큰 발급/캐시"""
    # 캐시 확인
    cached = _load_token()
    if cached:
        return cached

    url = f"{cfg['base_url']}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": cfg['app_key'],
        "appsecret": cfg['app_secret'],
    }
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=body, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"❌ 토큰 발급 실패: {resp.status_code} {resp.text}")
        sys.exit(1)

    result = resp.json()
    token = result['access_token']
    expired = result['access_token_token_expired']
    _save_token(token, expired)
    return token


def _wait_rate_limit():
    """API 호출 속도 제한"""
    global _last_api_call_time
    now = time.time()
    if _last_api_call_time and (now - _last_api_call_time) < _MIN_API_INTERVAL:
        time.sleep(_MIN_API_INTERVAL - (now - _last_api_call_time))
    _last_api_call_time = time.time()


def api_get(cfg: dict, token: str, path: str, tr_id: str, params: dict,
            _retried: bool = False) -> Optional[dict]:
    """GET API 호출 (토큰 만료 시 자동 재발급)"""
    _wait_rate_limit()
    tr_id = resolve_tr_id(cfg, tr_id)
    url = f"{cfg['base_url']}{path}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": cfg['app_key'],
        "appsecret": cfg['app_secret'],
        "tr_id": tr_id,
        "custtype": "P",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    if resp.status_code != 200:
        print(f"❌ API 오류: {resp.status_code} {resp.text[:200]}")
        return None
    data = resp.json()
    # 토큰 만료 감지 → 재발급 후 재시도
    if data.get('msg_cd') in ('EGW00123', 'EGW00121') and not _retried:
        new_token = _force_refresh_token(cfg)
        return api_get(cfg, new_token, path, tr_id, params, _retried=True)
    if data.get('rt_cd') != '0':
        print(f"❌ API 오류: [{data.get('msg_cd')}] {data.get('msg1')}")
        return None
    # 연속조회 키를 data에 포함
    data['_tr_cont'] = resp.headers.get('tr_cont', '')
    return data


def api_post(cfg: dict, token: str, path: str, tr_id: str, body: dict,
             use_hashkey: bool = True, _retried: bool = False) -> Optional[dict]:
    """POST API 호출 (토큰 만료 시 자동 재발급)"""
    _wait_rate_limit()
    tr_id = resolve_tr_id(cfg, tr_id)
    url = f"{cfg['base_url']}{path}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": cfg['app_key'],
        "appsecret": cfg['app_secret'],
        "tr_id": tr_id,
        "custtype": "P",
    }

    # 해시키 설정
    if use_hashkey:
        try:
            hk_resp = requests.post(
                f"{cfg['base_url']}/uapi/hashkey",
                headers=headers, json=body, timeout=5
            )
            if hk_resp.status_code == 200:
                headers['hashkey'] = hk_resp.json().get('HASH', '')
        except:
            pass

    resp = requests.post(url, headers=headers, json=body, timeout=10)
    if resp.status_code != 200:
        print(f"❌ API 오류: {resp.status_code} {resp.text[:200]}")
        return None
    data = resp.json()
    # 토큰 만료 감지 → 재발급 후 재시도
    if data.get('msg_cd') in ('EGW00123', 'EGW00121') and not _retried:
        new_token = _force_refresh_token(cfg)
        return api_post(cfg, new_token, path, tr_id, body, use_hashkey, _retried=True)
    if data.get('rt_cd') != '0':
        print(f"❌ API 오류: [{data.get('msg_cd')}] {data.get('msg1')}")
        return None
    return data


def safe_int(v, default=0):
    """문자열→int 변환 (실패 시 default)"""
    try:
        return int(str(v).replace(',', ''))
    except:
        return default


def safe_float(v, default=0.0):
    """문자열→float 변환 (실패 시 default)"""
    try:
        return float(str(v).replace(',', ''))
    except:
        return default


# 모의투자 TR ID 매핑 (실전 → 모의)
VIRTUAL_TR_ID_MAP = {
    # 주문
    'TTTC0012U': 'VTTC0802U',  # 매수
    'TTTC0011U': 'VTTC0801U',  # 매도
    # 잔고/보유종목 조회
    'TTTC8434R': 'VTTC8434R',
    # 일별 주문체결 조회
    'TTTC0081R': 'VTTC0081R',  # 모의투자 TR ID 동일 패턴
}


def resolve_tr_id(cfg: dict, tr_id: str) -> str:
    """모의투자 환경이면 TR ID를 모의투자용으로 변환"""
    if 'openapivts' in cfg.get('base_url', ''):
        return VIRTUAL_TR_ID_MAP.get(tr_id, tr_id)
    return tr_id


def _force_refresh_token(cfg: dict) -> str:
    """토큰 강제 재발급"""
    # 캐시 파일 삭제
    try:
        os.remove(_TOKEN_FILE)
    except OSError:
        pass
    return get_token(cfg)


def fmt_num(n, suffix='') -> str:
    """숫자 포맷 (천단위 쉼표)"""
    try:
        v = int(str(n).replace(',', ''))
        return f"{v:,}{suffix}"
    except:
        return str(n) + suffix


def fmt_rate(n) -> str:
    """수익률 포맷"""
    try:
        v = float(str(n).replace(',', ''))
        sign = '+' if v > 0 else ''
        return f"{sign}{v:.2f}%"
    except:
        return str(n)


def fmt_price(n) -> str:
    """가격 포맷"""
    return fmt_num(n, '원')


def get_stock_name_from_api(cfg: dict, token: str, code: str) -> str:
    """종목명 조회 (search-stock-info API)"""
    params = {"PRDT_TYPE_CD": "300", "PDNO": code}
    data = api_get(cfg, token, '/uapi/domestic-stock/v1/quotations/search-stock-info', 'CTPF1002R', params)
    if data:
        out = data.get('output', {})
        return out.get('prdt_abrv_name', out.get('prdt_name', code))
    return code


def add_common_args(parser):
    """공통 인자 추가"""
    parser.add_argument('--config', '-c', default='~/.kis-trading/config.ini',
                        help='설정 파일 경로 (기본: ~/.kis-trading/config.ini)')
