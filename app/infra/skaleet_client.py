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


async def send_card_operation_result(
    card_id: int, 
    operation_type: str, 
    result: str,
    visa_card_number: str | None = None,
    ni_details: dict | None = None
):
    """
    Envoie le résultat d'une opération carte à Skaleet Admin API
    
    Args:
        card_id: ID de la carte Skaleet
        operation_type: Type d'opération (card_activation, card_blocking, etc.)
        result: Résultat de l'opération ("accept" ou "error")
        visa_card_number: Numéro de carte VISA généré par NI (optionnel)
        ni_details: Détails supplémentaires de la réponse NI (optionnel)
    """
    token = await get_admin_token()
    url = f"{settings.skaleet_admin_base_url}/cards/{card_id}/operation/{operation_type}/{result}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Préparer le body avec les données de la carte VISA si disponibles
    body = {}
    if visa_card_number:
        body["visaCardNumber"] = visa_card_number
        body["panNumber"] = visa_card_number  # Alias pour compatibilité
    if ni_details:
        body["niDetails"] = ni_details
        # Extraire d'autres infos utiles de ni_details
        if "expiryDate" in ni_details:
            body["expiryDate"] = ni_details["expiryDate"]
        if "niCardId" in ni_details:
            body["niCardId"] = ni_details["niCardId"]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=body if body else None,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(
                f"Successfully sent operation result to Skaleet: "
                f"card_id={card_id}, operation={operation_type}, result={result}, "
                f"visaCardNumber={'***' + visa_card_number[-4:] if visa_card_number else 'N/A'}"
            )
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

