import httpx
from app.core.config import settings
from app.schemas.skaleet import SkaleetCardRequest, SkaleetCardResponse
import logging

logger = logging.getLogger(__name__)


async def get_admin_token() -> str:
    """
    Obtient un token d'accès admin Skaleet via OAuth2 client credentials
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.skaleet_admin_base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.skaleet_admin_client_id,
                    "client_secret": settings.skaleet_admin_client_secret
                },
                timeout=30.0
            )
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("No access_token in OAuth response")
            return access_token
        except httpx.HTTPError as e:
            logger.error(f"Skaleet OAuth error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting admin token: {e}", exc_info=True)
            raise


async def send_card_operation_result(card_id: int, operation_type: str, result: str):
    """
    Envoie le résultat d'une opération carte à Skaleet Admin API
    """
    token = await get_admin_token()
    url = f"{settings.skaleet_admin_base_url}/cards/{card_id}/operation/{operation_type}/{result}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(f"Successfully sent operation result to Skaleet: card_id={card_id}, operation={operation_type}, result={result}")
        except httpx.HTTPError as e:
            logger.error(f"Skaleet API error when sending operation result: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending operation result: {e}", exc_info=True)
            raise


class SkaleetClient:
    def __init__(self):
        self.base_url = settings.skaleet_admin_base_url
        self.client_id = settings.skaleet_admin_client_id
        self.client_secret = settings.skaleet_admin_client_secret
        self._access_token = None
    
    async def _get_access_token(self) -> str:
        """Obtient un token d'accès via OAuth2 client credentials"""
        if self._access_token:
            return self._access_token
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                return self._access_token
            except httpx.HTTPError as e:
                logger.error(f"Skaleet OAuth error: {e}")
                raise
    
    async def _get_headers(self) -> dict:
        """Retourne les headers avec le token d'accès"""
        token = await self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def create_card(self, card_data: dict) -> SkaleetCardResponse:
        headers = await self._get_headers()
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/cards",
                    json=card_data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return SkaleetCardResponse(**response.json())
            except httpx.HTTPError as e:
                logger.error(f"Skaleet API error: {e}")
                raise
    
    async def get_card(self, card_id: str) -> SkaleetCardResponse:
        headers = await self._get_headers()
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/cards/{card_id}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return SkaleetCardResponse(**response.json())
            except httpx.HTTPError as e:
                logger.error(f"Skaleet API error: {e}")
                raise
    
    async def update_card(self, card_id: str, card_data: dict) -> SkaleetCardResponse:
        headers = await self._get_headers()
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{self.base_url}/cards/{card_id}",
                    json=card_data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return SkaleetCardResponse(**response.json())
            except httpx.HTTPError as e:
                logger.error(f"Skaleet API error: {e}")
                raise

