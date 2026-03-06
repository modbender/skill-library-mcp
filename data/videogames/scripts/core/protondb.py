from typing import Optional, Dict
from .network import make_request

PROTONDB_API_URL = "https://www.protondb.com/api/v1/reports/summaries/{appid}.json"

def get_proton_rating(appid: int) -> Optional[str]:
    """
    Obtiene el tier de compatibilidad de ProtonDB (Platinum, Gold, Silver, Bronze, Borked).
    """
    url = PROTONDB_API_URL.format(appid=appid)
    data = make_request(url, retries=2)
    
    if data and 'tier' in data:
        return data['tier'].capitalize() # e.g., "platinum" -> "Platinum"
    
    return None

def get_proton_details(appid: int) -> Dict[str, str]:
    """
    Obtiene detalles completos de ProtonDB e imprime un resumen.
    """
    url = PROTONDB_API_URL.format(appid=appid)
    data = make_request(url, retries=2)

    if not data:
        print(f"No se encontró información en ProtonDB para AppID {appid}.")
        return {}

    tier = data.get('tier', 'Unknown').capitalize()
    total_reports = data.get('total', 0)
    trending_tier = data.get('trendingTier', 'Unknown').capitalize()
    best_tier = data.get('bestReportedTier', 'Unknown').capitalize()

    print(f"--- Compatibilidad Linux/Steam Deck (ProtonDB) ---")
    print(f"Tier General: {tier}")
    print(f"Tendencia Reciente: {trending_tier}")
    print(f"Mejor Reporte: {best_tier}")
    print(f"Total Reportes: {total_reports}")
    
    return {
        "tier": tier,
        "trending": trending_tier
    }
