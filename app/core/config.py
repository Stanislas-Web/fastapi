from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()


class Settings(BaseSettings):
    # App
    app_name: str = "card-connector"
    debug: bool = False
    env: str = "dev"  # dev, int, prod
    
    # Database
    database_url: str
    
    # Skaleet Admin API
    skaleet_admin_base_url: str
    skaleet_admin_client_id: str
    skaleet_admin_client_secret: str
    
    # NI Processor
    ni_base_url: str
    ni_api_key: str
    ni_use_mock: bool = False  # Si True, utilise les données mockées au lieu d'appeler l'API réelle
    
    # Webhook
    webhook_secret: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

