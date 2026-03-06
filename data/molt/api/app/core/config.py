import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    env: str = "development"
    
    # Database
    database_url_dev: str = "sqlite+aiosqlite:///./data/dev.db"
    database_url_prod: str = "sqlite+aiosqlite:///./data/prod.db"
    
    # Security
    secret_key: str = "change-me-in-production-use-a-real-secret-key"
    api_key_salt: str = "change-me-salt"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # Magic Link
    magic_link_expire_minutes: int = 15
    
    # CORS
    frontend_url: str = "http://localhost:5173"
    
    # Site URL for absolute URLs (OG tags, canonical links)
    site_url: str = "https://moltfundme.com"
    
    # Email (optional for MVP)
    resend_api_key: str = ""
    from_email: str = "noreply@moltfundme.com"
    
    # Blockchain APIs
    blockcypher_api_token: str = ""  # Optional, increases rate limits
    helius_api_key: str = ""
    alchemy_api_key: str = ""  # Optional, for Base/USDC queries
    base_rpc_url: str = "https://mainnet.base.org"  # Public Base RPC endpoint
    balance_poll_interval_seconds: int = 120

    # Rate limiting
    agent_registration_rate_limit: int = 5
    agent_registration_rate_window_seconds: int = 3600

    @property
    def database_url(self) -> str:
        if self.env == "production":
            return self.database_url_prod
        return self.database_url_dev
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from pathlib import Path
        Path("./data").mkdir(exist_ok=True)
        
        # Validate production security settings
        if self.env == "production":
            if self.secret_key == "change-me-in-production-use-a-real-secret-key":
                raise ValueError(
                    "SECRET_KEY must be changed from default value in production. "
                    "Set a secure random string via environment variable."
                )
            if self.api_key_salt == "change-me-salt":
                raise ValueError(
                    "API_KEY_SALT must be changed from default value in production. "
                    "Set a secure random string via environment variable."
                )
            if not self.frontend_url or self.frontend_url == "http://localhost:5173":
                raise ValueError(
                    "FRONTEND_URL must be set to your production frontend URL. "
                    "Cannot use localhost in production."
                )
    
    class Config:
        # Load .env from project root (molt/.env), one level above api/
        _project_root = Path(__file__).resolve().parent.parent.parent.parent
        env_file = str(_project_root / ".env")
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
