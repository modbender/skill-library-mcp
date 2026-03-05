import urllib.request
import urllib.error
import json
import sys
import time
import os
import hashlib
from typing import Optional, Any

# Configuración de Caché
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".openclaw", "skills", "videogames", ".cache")
CACHE_EXPIRATION = 86400  # 24 horas en segundos

def _get_cache_path(url: str) -> str:
    """Genera una ruta de archivo única basada en el hash de la URL."""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.json")

def _load_from_cache(url: str) -> Optional[Any]:
    """Carga datos desde el caché si existe y es válido."""
    try:
        cache_path = _get_cache_path(url)
        if os.path.exists(cache_path):
            file_age = time.time() - os.path.getmtime(cache_path)
            if file_age < CACHE_EXPIRATION:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception:
        pass # Fallo silencioso en cache lectura
    return None

def _save_to_cache(url: str, data: Any):
    """Guarda los datos en el caché."""
    try:
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR, exist_ok=True)
        
        cache_path = _get_cache_path(url)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        # print(f"Warning: No se pudo guardar en caché: {e}", file=sys.stderr)
        pass

def make_request(url: str, retries: int = 3, backoff_factor: float = 1.0) -> Optional[Any]:
    """
    Realiza una petición HTTP GET y devuelve el JSON decodificado.
    Incluye caché local (24h) y lógica de reintentos.
    """
    # Intentar cargar desde caché primero
    cached_data = _load_from_cache(url)
    if cached_data:
        return cached_data

    attempt = 0
    while attempt < retries:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    _save_to_cache(url, data)
                    return data
        except urllib.error.HTTPError as e:
            # Reintentar en errores 5xx (servidor), fallar en 4xx (cliente) excepto 429
            if 500 <= e.code < 600 or e.code == 429:
                # print(f"Error {e.code} en {url}. Reintentando ({attempt + 1}/{retries})...", file=sys.stderr)
                time.sleep(backoff_factor * (2 ** attempt))
                attempt += 1
            else:
                print(f"Error HTTP {e.code} al conectar con {url}: {e.reason}", file=sys.stderr)
                return None
        except urllib.error.URLError as e:
            # print(f"Error de red al conectar con {url}: {e.reason}. Reintentando ({attempt + 1}/{retries})...", file=sys.stderr)
            time.sleep(backoff_factor * (2 ** attempt))
            attempt += 1
        except json.JSONDecodeError as e:
            print(f"Error al decodificar respuesta JSON de {url}: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error inesperado al consultar {url}: {e}", file=sys.stderr)
            return None
            
    # print(f"Fallo al conectar con {url} después de {retries} intentos.", file=sys.stderr)
    return None
