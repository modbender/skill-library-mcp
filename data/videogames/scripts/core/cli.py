import argparse
import sys
from . import steam
from . import cheapshark
from . import protondb
from . import hltb
from . import config

def main():
    parser = argparse.ArgumentParser(description="Herramienta unificada para videojuegos (Steam y CheapShark)")
    
    # Argumentos Globales de Configuración
    parser.add_argument("--lang", type=str, help="Idioma (ej: spanish, english, french)", default=None)
    parser.add_argument("--currency", type=str, help="Moneda (ej: EUR, USD, GBP)", default=None)
    parser.add_argument("--region", type=str, help="Código de país/región (ej: ES, US, GB)", default=None)

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Steam Commands ---
    
    search_parser = subparsers.add_parser("search", help="Buscar un juego en Steam")
    search_parser.add_argument("term", type=str, help="Término de búsqueda")
    search_parser.set_defaults(func=lambda args: steam.search_game(args.term))

    details_parser = subparsers.add_parser("details", help="Obtener detalles de Steam por ID")
    details_parser.add_argument("appid", type=int, help="AppID del juego")
    details_parser.set_defaults(func=lambda args: steam.get_game_details(args.appid))

    offers_parser = subparsers.add_parser("offers", help="Ver ofertas destacadas de Steam")
    offers_parser.set_defaults(func=lambda args: steam.get_specials())

    players_parser = subparsers.add_parser("players", help="Ver jugadores actuales (Steam)")
    players_parser.add_argument("appid", type=int, help="AppID del juego")
    players_parser.set_defaults(func=lambda args: steam.get_player_count(args.appid))

    news_parser = subparsers.add_parser("news", help="Ver noticias de un juego (Steam)")
    news_parser.add_argument("appid", type=int, help="AppID del juego")
    news_parser.set_defaults(func=lambda args: steam.get_news(args.appid))

    trends_parser = subparsers.add_parser("trends", help="Ver tendencias de Steam")
    trends_parser.set_defaults(func=lambda args: steam.get_trends())

    top_parser = subparsers.add_parser("top", help="Ver juegos con más jugadores en Steam")
    top_parser.set_defaults(func=lambda args: steam.get_most_played())

    ach_parser = subparsers.add_parser("achievements", help="Ver logros globales (Steam)")
    ach_parser.add_argument("appid", type=int, help="AppID del juego")
    ach_parser.set_defaults(func=lambda args: steam.get_achievements(args.appid))

    rev_parser = subparsers.add_parser("reviews", help="Ver resumen de reseñas (Steam)")
    rev_parser.add_argument("appid", type=int, help="AppID del juego")
    rev_parser.set_defaults(func=lambda args: steam.get_reviews(args.appid))

    rec_parser = subparsers.add_parser("recommendations", help="Ver recomendaciones basadas en un juego (Steam)")
    rec_parser.add_argument("appid", type=int, help="AppID del juego")
    rec_parser.set_defaults(func=lambda args: steam.get_recommendations(args.appid))

    # --- New Integrations Commands ---

    proton_parser = subparsers.add_parser("compatibility", help="Ver compatibilidad Linux/Steam Deck (ProtonDB)")
    proton_parser.add_argument("appid", type=int, help="AppID del juego")
    proton_parser.set_defaults(func=lambda args: protondb.get_proton_details(args.appid))

    hltb_parser = subparsers.add_parser("duration", help="Ver duración estimada (HowLongToBeat)")
    hltb_parser.add_argument("name", type=str, help="Nombre del juego")
    hltb_parser.set_defaults(func=lambda args: hltb.print_hltb_info(args.name))

    # --- CheapShark Commands ---

    deal_parser = subparsers.add_parser("deals", help="Buscar mejores ofertas en todas las tiendas (CheapShark)")
    deal_parser.add_argument("term", type=str, help="Nombre del juego")
    deal_parser.set_defaults(func=lambda args: cheapshark.search_deals(args.term))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Aplicar configuración global
    config.set_config(language=args.lang, currency=args.currency, cc=args.region)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
