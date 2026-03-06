import urllib.parse
from .network import make_request
from .config import get_language, get_currency, get_country_code
from .style import Color, print_header, print_key_value

STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/?term={term}&l={lang}&cc={cc}"
STEAM_DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={appid}&l={lang}&cc={cc}"
STEAM_FEATURED_URL = "https://store.steampowered.com/api/featuredcategories/?l={lang}&cc={cc}"
STEAM_PLAYERS_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count=3&maxlength=300&format=json"
STEAM_MOST_PLAYED_URL = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
STEAM_ACHIEVEMENTS_URL = "https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}"
STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}?json=1&language={lang}&purchase_type=all&filter=summary"

def search_game(term: str):
    lang = get_language()
    cc = get_country_code()
    encoded_term = urllib.parse.quote(term)
    url = STEAM_SEARCH_URL.format(term=encoded_term, lang=lang, cc=cc)
    
    data = make_request(url)
    if not data or 'items' not in data or not data['items']:
        print(f"No se encontraron juegos para '{term}'.")
        return

    print(f"Resultados en Steam para '{term}':")
    for item in data['items']:
        price = "Gratis"
        if item.get('price'):
            price = f"{item['price']['final'] / 100:.2f} {item['price']['currency']}"
        print(f"- {item['name']} (ID: {item['id']}) - {price}")

def get_game_details(appid: int):
    lang = get_language()
    cc = get_country_code()
    url = STEAM_DETAILS_URL.format(appid=appid, lang=lang, cc=cc)
    
    data = make_request(url)
    
    if not data or str(appid) not in data or not data[str(appid)]['success']:
        print(f"No se pudieron obtener detalles para el AppID {appid}.")
        return

    game_data = data[str(appid)]['data']
    name = game_data.get('name', 'Desconocido')
    desc = game_data.get('short_description', 'Sin descripción.')
    devs = ", ".join(game_data.get('developers', []))
    publishers = ", ".join(game_data.get('publishers', []))
    
    price_overview = game_data.get('price_overview')
    price = "Gratis/Desconocido"
    if price_overview:
        price = price_overview.get('final_formatted', 'N/A')
    elif game_data.get('is_free'):
        price = "Gratis"

    metacritic = "N/A"
    if 'metacritic' in game_data:
        metacritic = game_data['metacritic'].get('score', 'N/A')

    release_date_data = game_data.get('release_date', {})
    release_date = release_date_data.get('date', 'Desconocida')
    coming_soon = release_date_data.get('coming_soon', False)
    status = " (Próximamente)" if coming_soon else ""

    # Parseo de Requisitos (Minimos)
    pc_reqs = game_data.get('pc_requirements', {})
    req_str = "No disponibles"
    if isinstance(pc_reqs, dict) and 'minimum' in pc_reqs:
        # Limpieza más cuidadosa
        cleaned = pc_reqs['minimum']
        
        # Tags que rompen línea
        for tag in ['<br>', '<br/>', '<li>', '<ul>', '</ul>', '<p>', '</p>']:
            cleaned = cleaned.replace(tag, '\n')
            
        # Tags que solo dan formato (negrita, etc) -> eliminar sin romper línea
        for tag in ['<strong>', '</strong>', '<b>', '</b>']:
            cleaned = cleaned.replace(tag, '')

        # Eliminar tags HTML restantes y clases
        cleaned = cleaned.replace('<ul class="bb_ul">', '')

        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        
        # Filtrar y reconstruir
        # Buscamos líneas que tengan contenido relevante.
        # A veces "Procesador:" queda en una línea y el valor en otra si el HTML original era así.
        # Intentamos unir si una línea termina en ":" y la siguiente no.
        final_lines = []
        for i, line in enumerate(lines):
            # Filtro básico de interés
            if any(k in line.lower() for k in ['os', 'so', 'windows', 'processor', 'procesador', 'memory', 'memoria', 'graphics', 'gráficos', 'storage', 'almacenamiento', 'directx']):
                 final_lines.append(line)
        
        if final_lines:
            req_str = "\n  ".join(final_lines[:5])

    # Fase 2: Idiomas
    supported_langs = game_data.get('supported_languages', '')
    lang_summary = "Desconocido"
    
    # Debug: descomentar para ver qué llega
    # print(f"DEBUG LANGS: {supported_langs}")

    if supported_langs:
        # La API devuelve los idiomas en inglés ("Spanish") o localizados ("Español") según el parámetro 'l'.
        # Como usamos l=spanish por defecto, es probable que llegue "Español".
        # Buscamos ambas variantes para ser robustos.
        normalized_langs = supported_langs.lower()
        has_spanish = "spanish" in normalized_langs or "español" in normalized_langs or "castellano" in normalized_langs
        
        if has_spanish:
            lang_summary = "Español disponible"
            if "spain" in normalized_langs or "españa" in normalized_langs:
                 lang_summary = "Español (España)"
            elif "latin" in normalized_langs or "latino" in normalized_langs:
                 lang_summary = "Español (Latam)"
            
            # Chequeo de audio
            # La API suele poner "<strong>*</strong>languages with full audio support" al final
            # O marca con asterisco el idioma: "Español<strong>*</strong>"
            if "<strong>*</strong>" in supported_langs:
                 # Check simple: si hay asterisco, asumimos que ALGUN idioma tiene audio.
                 # Es difícil saber cuál exactamente sin parsear complejo, pero es un buen proxy.
                 lang_summary += " (Posible Audio Completo)"
        else:
            lang_summary = "No incluye Español"

    # Fase 2: Controller & Multiplayer (Categories)
    categories = game_data.get('categories', [])
    cat_ids = {c['id']: c['description'] for c in categories}
    
    controller = "No / Teclado y Ratón"
    if 28 in cat_ids: controller = "Total (Mando)"
    elif 18 in cat_ids: controller = "Parcial (Mando)"
    
    mp_modes = []
    if 1 in cat_ids: mp_modes.append("Multijugador")
    if 9 in cat_ids: mp_modes.append("Cooperativo")
    if 24 in cat_ids: mp_modes.append("Pantalla Partida")
    mp_str = ", ".join(mp_modes) if mp_modes else "Un jugador"

    # Fase 2: DRM y Legal
    drm_notice = game_data.get('drm_notice', '')
    legal = game_data.get('legal_notice', '')
    drm_alert = ""
    if "Denuvo" in drm_notice or "Denuvo" in legal:
        drm_alert = " [⚠️ USA DENUVO]"
    elif "3rd-party account" in drm_notice or "account" in legal:
        # Simplificación para detectar launchers
        pass 

    print_header(f"--- Detalles de {name} ---")
    print_key_value("ID", appid)
    print_key_value("Precio", f"{Color.GREEN}{price}{Color.END}")
    print_key_value("Lanzamiento", f"{release_date}{status}")
    
    meta_color = Color.GREEN
    try:
        if int(metacritic) < 60: meta_color = Color.RED
        elif int(metacritic) < 80: meta_color = Color.YELLOW
    except: pass
    print_key_value("Metacritic", f"{meta_color}{metacritic}{Color.END}")
    
    print_key_value("Idioma", lang_summary)
    print_key_value("Input", controller)
    print_key_value("Modos", mp_str)
    print_key_value("Desarrolladores", devs)
    print_key_value("Publishers", publishers)
    
    print(f"\n{Color.BOLD}--- Requisitos Mínimos ---{Color.END}")
    print(f"  {req_str}")
    
    print(f"\n{Color.BOLD}--- Descripción ---{Color.END}")
    print(f"{desc}")
    if drm_notice:
        print(f"\n{Color.BOLD}{Color.RED}--- DRM / Aviso Legal ---{Color.END}")
        print(f"{Color.RED}{drm_notice}{Color.END}")
    
    print(f"\n{Color.BOLD}--- Enlaces Útiles ---{Color.END}")
    print(f"PCGamingWiki: {Color.BLUE}https://www.pcgamingwiki.com/api/appid.php?appid={appid}{Color.END}")
    print(f"SteamDB: {Color.BLUE}https://steamdb.info/app/{appid}/{Color.END}")

def get_recommendations(appid: int):
    """
    Intenta obtener recomendaciones basadas en tags o categorías (simulado usando 'More Like This' endpoint o similar).
    Nota: Steam no tiene un endpoint público oficial de 'recommendations' simple. 
    Usaremos una estrategia alternativa: Obtener detalles y listar categorías/géneros para sugerir búsquedas.
    """
    lang = get_language()
    cc = get_country_code()
    url = STEAM_DETAILS_URL.format(appid=appid, lang=lang, cc=cc)
    data = make_request(url)
    
    if not data or str(appid) not in data or not data[str(appid)]['success']:
        print(f"No se pudieron obtener datos para recomendaciones del ID {appid}.")
        return

    game_data = data[str(appid)]['data']
    name = game_data.get('name')
    genres = [g['description'] for g in game_data.get('genres', [])]
    categories = [c['description'] for c in game_data.get('categories', [])]
    
    print_header(f"--- Si te gusta '{name}', busca por estos géneros/etiquetas ---")
    print_key_value("Géneros", f"{Color.CYAN}{', '.join(genres)}{Color.END}")
    print_key_value("Características", f"{', '.join(categories[:5])}")
    print(f"(Prueba: python3 scripts/game_tool.py search \"{genres[0] if genres else 'RPG'}\")")

def get_specials():
    lang = get_language()
    cc = get_country_code()
    url = STEAM_FEATURED_URL.format(lang=lang, cc=cc)
    
    data = make_request(url)
    
    if not data or 'specials' not in data or 'items' not in data['specials']:
        print("No se pudieron obtener ofertas especiales en este momento.")
        return

    print_header("--- Ofertas Destacadas en Steam ---")
    for item in data['specials']['items']:
        discount = item.get('discount_percent', 0)
        orig_price = item.get('original_price')
        final_price = item.get('final_price')
        currency = item.get('currency', get_currency())
        
        price_str = ""
        if orig_price and final_price:
            price_str = f"{orig_price/100:.2f} -> {Color.GREEN}{final_price/100:.2f} {currency}{Color.END} ({Color.GREEN}-{discount}%{Color.END})"
        else:
            price_str = "Gratis/Desconocido"
            
        print(f"- {Color.BOLD}{item['name']}{Color.END} (ID: {item['id']}) - {price_str}")

def get_player_count(appid: int):
    url = STEAM_PLAYERS_URL.format(appid=appid)
    data = make_request(url)
    
    if not data or 'response' not in data or data['response'].get('result') != 1:
        print(f"No se pudo obtener el conteo de jugadores para el ID {appid}.")
        return

    count = data['response'].get('player_count', 0)
    print_header(f"Jugadores actuales para ID {appid}: {Color.GREEN}{count:,}{Color.END}")

def get_news(appid: int):
    url = STEAM_NEWS_URL.format(appid=appid)
    data = make_request(url)
    
    if not data or 'appnews' not in data or not data['appnews'].get('newsitems'):
        print(f"No hay noticias disponibles para el ID {appid}.")
        return

    print_header(f"--- Últimas Noticias para ID {appid} ---")
    for item in data['appnews']['newsitems']:
        print(f"- {Color.BOLD}{item['title']}{Color.END}")
        print(f"  URL: {Color.BLUE}{item['url']}{Color.END}\n")

def get_trends():
    lang = get_language()
    cc = get_country_code()
    url = STEAM_FEATURED_URL.format(lang=lang, cc=cc)
    data = make_request(url)
    
    if not data:
        print("No se pudieron obtener tendencias.")
        return

    if 'top_sellers' in data:
        print_header("--- Lo más vendido en Steam ---")
        for item in data['top_sellers']['items'][:5]:
            print(f"- {Color.BOLD}{item['name']}{Color.END} (ID: {item['id']})")
    
    print_header("--- Nuevos Lanzamientos ---")
    if 'new_releases' in data:
        for item in data['new_releases']['items'][:5]:
            print(f"- {Color.BOLD}{item['name']}{Color.END} (ID: {item['id']})")

def get_most_played():
    url = STEAM_MOST_PLAYED_URL
    data = make_request(url)
    
    if not data or 'response' not in data or 'ranks' not in data['response']:
        print("No se pudieron obtener los juegos más jugados.")
        return

    print_header("--- Top Juegos por Jugadores Online ---")
    for rank in data['response']['ranks'][:10]:
        appid = rank['appid']
        peak = rank.get('peak_in_game', 0)
        print(f"Posición {rank['rank']}: AppID {appid} - Pico de jugadores: {Color.GREEN}{peak:,}{Color.END}")
    
    print("\n(Usa 'details <ID>' para saber el nombre de un juego específico)")

def get_achievements(appid: int):
    url = STEAM_ACHIEVEMENTS_URL.format(appid=appid)
    data = make_request(url)
    
    if not data or 'achievementpercentages' not in data:
        print(f"No hay datos de logros para el ID {appid}.")
        return

    achievements = data['achievementpercentages']['achievements']
    print_header(f"--- Logros más raros para ID {appid} ---")
    sorted_ach = sorted(achievements, key=lambda x: x['percent'])
    for ach in sorted_ach[:5]:
        percent_val = float(ach['percent'])
        color = Color.PURPLE if percent_val < 5.0 else Color.CYAN
        print(f"- {ach['name']}: {color}{percent_val:.2f}%{Color.END} de los jugadores")

def get_reviews(appid: int):
    lang = get_language()
    url = STEAM_REVIEWS_URL.format(appid=appid, lang=lang)
    data = make_request(url)
    
    if not data or 'query_summary' not in data:
        print(f"No se pudo obtener el resumen de reseñas para el ID {appid}.")
        return

    summary = data['query_summary']
    score_desc = summary.get('review_score_desc', 'N/A')
    total_pos = summary.get('total_positive', 0)
    total_rev = summary.get('total_reviews', 0)
    
    percent = (total_pos / total_rev * 100) if total_rev > 0 else 0
    
    color = Color.GREEN if percent > 70 else (Color.YELLOW if percent > 40 else Color.RED)

    print_header(f"--- Resumen de Reseñas para ID {appid} ---")
    print_key_value("Calificación", f"{color}{score_desc}{Color.END}")
    print_key_value("Porcentaje Positivo", f"{color}{percent:.1f}%{Color.END}")
    print_key_value("Total de reseñas", f"{total_rev:,}")
