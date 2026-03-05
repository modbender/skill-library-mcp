import urllib.parse

def print_hltb_info(game_name: str):
    """
    Genera un enlace de búsqueda a HowLongToBeat.
    Nota: La API de scraping de HLTB está protegida por Cloudflare/Anti-bot, 
    por lo que ofrecemos un enlace directo para garantizar la utilidad.
    """
    encoded_name = urllib.parse.quote(game_name)
    url = f"https://howlongtobeat.com/?q={encoded_name}"

    print(f"--- Duración (HowLongToBeat) ---")
    print(f"Debido a restricciones de la API, puedes ver la duración aquí:")
    print(f"{url}")
