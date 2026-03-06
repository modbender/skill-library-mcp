#!/usr/bin/env python3
"""
Naver Shopping Plus - 한국형 쇼핑 검색 스킬
네이버 쇼핑 API + 쿠팡/11번가 웹 스크래핑 통합
"""

import os
import sys
import json
import argparse
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("⚠️  의존성 설치 필요: pip install requests beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)


class ProductSearcher:
    def __init__(self):
        self.naver_client_id = os.getenv('NAVER_Client_ID')
        self.naver_client_secret = os.getenv('NAVER_Client_Secret')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def search_naver(self, query: str, display: int = 3) -> List[Dict]:
        """네이버 쇼핑 API 검색"""
        if not self.naver_client_id or not self.naver_client_secret:
            return []
        
        enc_query = urllib.parse.quote(query)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={enc_query}&display={display}&sort=asc"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.naver_client_id.strip())
        request.add_header("X-Naver-Client-Secret", self.naver_client_secret.strip())
        
        try:
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return self._parse_naver_results(data.get('items', []))
        except Exception as e:
            print(f"⚠️  네이버 API 에러: {e}", file=sys.stderr)
        
        return []
    
    def _parse_naver_results(self, items: List[Dict]) -> List[Dict]:
        """네이버 API 결과 파싱"""
        results = []
        for item in items:
            # HTML 태그 제거
            title = re.sub(r'<[^>]+>', '', item.get('title', ''))
            price = int(item.get('lprice', 0))
            
            # 네이버는 배송비 정보가 API에 없으므로 0으로 가정
            shipping = 0
            
            results.append({
                'platform': '네이버쇼핑',
                'title': title,
                'price': price,
                'shipping': shipping,
                'total': price + shipping,
                'url': item.get('link', ''),
                'image': item.get('image', ''),
                'mall': item.get('mallName', ''),
                'brand': item.get('brand', ''),
                'category': item.get('category1', ''),
            })
        
        return results
    
    def search_coupang(self, query: str, display: int = 3) -> List[Dict]:
        """쿠팡 웹 스크래핑"""
        results = []
        try:
            url = f"https://www.coupang.com/np/search?q={urllib.parse.quote(query)}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                return results
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 쿠팡 상품 리스트 파싱 (실제 셀렉터는 사이트 구조에 따라 조정 필요)
            products = soup.select('li.search-product')[:display]
            
            for product in products:
                try:
                    # 제목
                    title_elem = product.select_one('.name')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # 가격
                    price_elem = product.select_one('.price-value')
                    if not price_elem:
                        continue
                    price_text = price_elem.get_text(strip=True).replace(',', '')
                    price = int(re.sub(r'\D', '', price_text))
                    
                    # 배송비 (로켓배송은 무료, 일반은 2,500원 가정)
                    is_rocket = product.select_one('.badge-rocket')
                    shipping = 0 if is_rocket else 2500
                    
                    # URL
                    link_elem = product.select_one('a')
                    url = 'https://www.coupang.com' + link_elem.get('href', '') if link_elem else ''
                    
                    results.append({
                        'platform': '쿠팡',
                        'title': title,
                        'price': price,
                        'shipping': shipping,
                        'total': price + shipping,
                        'url': url,
                        'is_rocket': bool(is_rocket),
                    })
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"⚠️  쿠팡 스크래핑 에러: {e}", file=sys.stderr)
        
        return results
    
    def search_11st(self, query: str, display: int = 3) -> List[Dict]:
        """11번가 웹 스크래핑"""
        results = []
        try:
            url = f"https://search.11st.co.kr/Search.tmall?kwd={urllib.parse.quote(query)}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                return results
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 11번가 상품 리스트 파싱 (실제 셀렉터는 사이트 구조에 따라 조정 필요)
            products = soup.select('div.c_card')[:display]
            
            for product in products:
                try:
                    # 제목
                    title_elem = product.select_one('.c_card__title')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # 가격
                    price_elem = product.select_one('.c_card__price strong')
                    if not price_elem:
                        continue
                    price_text = price_elem.get_text(strip=True).replace(',', '')
                    price = int(re.sub(r'\D', '', price_text))
                    
                    # 배송비 (일반적으로 2,500원, 무료배송 표시 확인)
                    free_shipping = product.select_one('.c_card__delivery:contains("무료")')
                    shipping = 0 if free_shipping else 2500
                    
                    # URL
                    link_elem = product.select_one('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = 'https://www.11st.co.kr' + url
                    
                    results.append({
                        'platform': '11번가',
                        'title': title,
                        'price': price,
                        'shipping': shipping,
                        'total': price + shipping,
                        'url': url,
                    })
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"⚠️  11번가 스크래핑 에러: {e}", file=sys.stderr)
        
        return results
    
    def search_all(self, query: str, platforms: List[str], display: int) -> List[Dict]:
        """모든 플랫폼 검색 및 병합"""
        all_results = []
        
        if 'naver' in platforms:
            all_results.extend(self.search_naver(query, display))
        
        if 'coupang' in platforms:
            all_results.extend(self.search_coupang(query, display))
        
        if '11st' in platforms:
            all_results.extend(self.search_11st(query, display))
        
        return all_results


def format_price(price: int) -> str:
    """가격 포맷팅 (천 단위 쉼표)"""
    return f"{price:,}원"


def format_output(results: List[Dict], sort_by: str = 'price') -> str:
    """결과를 보기 좋게 포맷팅"""
    if not results:
        return "❌ 검색 결과가 없습니다."
    
    # 정렬
    if sort_by == 'price':
        results.sort(key=lambda x: x['total'])
    
    # 최저가 찾기
    min_price = min(r['total'] for r in results)
    
    output = []
    output.append(f"🔍 검색 결과: {len(results)}개 상품\n")
    
    for i, item in enumerate(results, 1):
        platform_icon = {
            '네이버쇼핑': '🛍️',
            '쿠팡': '🛒',
            '11번가': '🏬',
        }.get(item['platform'], '🏪')
        
        # 제목 (너무 길면 자르기)
        title = item['title']
        if len(title) > 60:
            title = title[:57] + '...'
        
        output.append(f"{platform_icon} [{item['platform']}] {title}")
        
        # 가격 정보
        price_line = f"   💰 {format_price(item['price'])}"
        if item['shipping'] > 0:
            price_line += f" (배송비 {format_price(item['shipping'])})"
        else:
            price_line += " (배송비 무료)"
        
        price_line += f" = 총 {format_price(item['total'])}"
        
        # 최저가 표시
        if item['total'] == min_price:
            price_line += " ⭐ 최저가!"
        
        output.append(price_line)
        
        # 추가 정보
        if item.get('is_rocket'):
            output.append("   🚀 로켓배송")
        
        if item.get('mall'):
            output.append(f"   🏪 {item['mall']}")
        
        # URL
        if item.get('url'):
            output.append(f"   🔗 {item['url']}")
        
        output.append("")  # 빈 줄
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='한국형 쇼핑 검색 - 네이버/쿠팡/11번가 통합 검색',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  search.py "갤럭시 버즈"
  search.py "아이폰 16" --platforms naver,coupang --display 5
  search.py "노트북" --max-price 1000000 --sort price
        """
    )
    
    parser.add_argument('query', help='검색어')
    parser.add_argument('--display', type=int, default=3, help='플랫폼당 결과 수 (기본: 3, 최대: 10)')
    parser.add_argument('--platforms', default='naver,coupang,11st', help='검색할 플랫폼 (쉼표 구분)')
    parser.add_argument('--sort', default='price', choices=['price', 'review'], help='정렬 기준')
    parser.add_argument('--max-price', type=int, help='최대 가격 필터 (원 단위)')
    parser.add_argument('--json', action='store_true', help='JSON 형식으로 출력')
    
    args = parser.parse_args()
    
    # 유효성 검사
    if args.display < 1 or args.display > 10:
        print("❌ display는 1-10 사이여야 합니다.", file=sys.stderr)
        sys.exit(1)
    
    platforms = [p.strip() for p in args.platforms.split(',')]
    valid_platforms = {'naver', 'coupang', '11st'}
    platforms = [p for p in platforms if p in valid_platforms]
    
    if not platforms:
        print("❌ 유효한 플랫폼이 없습니다. (naver, coupang, 11st)", file=sys.stderr)
        sys.exit(1)
    
    # 검색 실행
    searcher = ProductSearcher()
    results = searcher.search_all(args.query, platforms, args.display)
    
    # 가격 필터
    if args.max_price:
        results = [r for r in results if r['total'] <= args.max_price]
    
    # 출력
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_output(results, args.sort))


if __name__ == '__main__':
    main()
