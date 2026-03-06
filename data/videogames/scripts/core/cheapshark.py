import urllib.parse
from typing import Dict
from .network import make_request
from .style import Color, print_header

CHEAPSHARK_DEALS_URL = "https://www.cheapshark.com/api/1.0/deals?title={term}&limit=10"
CHEAPSHARK_STORES_URL = "https://www.cheapshark.com/api/1.0/stores"

def get_store_map() -> Dict[str, str]:
    """Obtiene un mapa de ID de tienda a Nombre de tienda desde CheapShark."""
    data = make_request(CHEAPSHARK_STORES_URL)
    store_map = {}
    if data:
        for store in data:
            if store.get('isActive') == 1:
                store_map[store['storeID']] = store['storeName']
    return store_map

def search_deals(term: str):
    encoded_term = urllib.parse.quote(term)
    url = CHEAPSHARK_DEALS_URL.format(term=encoded_term)
    
    data = make_request(url)
    if not data:
        print(f"No se encontraron ofertas para '{term}'.")
        return

    stores = get_store_map()

    print_header(f"--- Mejores Ofertas para '{term}' ---")
    for deal in data:
        title = deal.get('title')
        store_id = deal.get('storeID')
        store_name = stores.get(store_id, f"Tienda {store_id}")
        price = float(deal.get('salePrice', 0))
        normal_price = float(deal.get('normalPrice', 0))
        savings = float(deal.get('savings', 0))
        link = f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"
        
        rating_msg = ""
        deal_rating = float(deal.get('dealRating', 0))
        if deal_rating >= 9.0:
            rating_msg = f" {Color.BOLD}{Color.GREEN}[¡OFERTAZA!]{Color.END}"
        elif deal_rating >= 8.0:
            rating_msg = f" {Color.GREEN}[Muy Buena Oferta]{Color.END}"

        if savings > 0:
            price_str = f"{normal_price:.2f} -> {Color.GREEN}{price:.2f} USD{Color.END} ({Color.GREEN}-{savings:.0f}%{Color.END}){rating_msg}"
        else:
            price_str = f"{price:.2f} USD"

        print(f"- {Color.BOLD}{title}{Color.END}")
        print(f"  Tienda: {store_name}")
        print(f"  Precio: {price_str}")
        print(f"  Link: {Color.BLUE}{link}{Color.END}\n")
