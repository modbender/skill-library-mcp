"""
auth.py — OAuth2 Gmail con token cifrado (Fernet).
Reutilizado por todos los scripts Python.

Variables de entorno:
  GMAIL_CREDENTIALS_PATH  (default: credentials.json)
  GMAIL_TOKEN_PATH        (default: token.json)
"""
import os, json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from cryptography.fernet import Fernet

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
]
CREDS = os.environ.get("GMAIL_CREDENTIALS_PATH", "credentials.json")
TOKEN = os.environ.get("GMAIL_TOKEN_PATH", "token.json")
KEY   = os.environ.get("GMAIL_KEY_PATH",   "token.key")


def _key():
    if os.path.exists(KEY):
        return open(KEY, "rb").read()
    k = Fernet.generate_key()
    open(KEY, "wb").write(k)
    os.chmod(KEY, 0o600)
    return k

def _save(creds):
    f = Fernet(_key())
    open(TOKEN, "wb").write(f.encrypt(creds.to_json().encode()))
    os.chmod(TOKEN, 0o600)

def _load():
    if not os.path.exists(TOKEN): return None
    try:
        f = Fernet(_key())
        return Credentials.from_authorized_user_info(
            json.loads(f.decrypt(open(TOKEN, "rb").read()).decode()), SCOPES)
    except Exception:
        # Intentar leer token sin cifrar (compatibilidad con gmail_reader.py original)
        try:
            return Credentials.from_authorized_user_file(TOKEN, SCOPES)
        except Exception:
            return None

def authenticate():
    creds = _load()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS):
                raise FileNotFoundError(
                    f"No se encontró '{CREDS}'.\n"
                    "Descárgalo: Google Cloud Console → APIs & Services → Credentials\n"
                    f"export GMAIL_CREDENTIALS_PATH=/ruta/credentials.json")
            print("🌐 Abriendo OAuth en navegador...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES)
            creds = flow.run_local_server(port=0)
        _save(creds)
    return creds

if __name__ == "__main__":
    authenticate()
    print("✅ Autenticación exitosa. Token guardado.")
