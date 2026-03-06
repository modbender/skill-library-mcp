import os

# Configuración por defecto
DEFAULT_LANGUAGE = "spanish"
DEFAULT_CURRENCY = "EUR"
DEFAULT_CC = "ES"

# Variable global de estado para la configuración en tiempo de ejecución
_RUNTIME_CONFIG = {
    "language": os.environ.get("STEAM_LANGUAGE", DEFAULT_LANGUAGE),
    "currency": os.environ.get("STEAM_CURRENCY", DEFAULT_CURRENCY),
    "cc": os.environ.get("STEAM_CC", DEFAULT_CC),
}

def set_config(language: str = None, currency: str = None, cc: str = None):
    """Actualiza la configuración en tiempo de ejecución."""
    if language:
        _RUNTIME_CONFIG["language"] = language
    if currency:
        _RUNTIME_CONFIG["currency"] = currency
    if cc:
        _RUNTIME_CONFIG["cc"] = cc

def get_language() -> str:
    """Obtiene el idioma configurado."""
    return _RUNTIME_CONFIG["language"]

def get_currency() -> str:
    """Obtiene la moneda configurada."""
    return _RUNTIME_CONFIG["currency"]

def get_country_code() -> str:
    """Obtiene el código de país configurado."""
    return _RUNTIME_CONFIG["cc"]
