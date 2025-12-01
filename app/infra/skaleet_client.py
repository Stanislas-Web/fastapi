import httpx
from app.core.config import settings
from app.schemas.skaleet import SkaleetCardRequest, SkaleetCardResponse
import logging

logger = logging.getLogger(__name__)


async def get_admin_token() -> str:
    """
    Obtient un token d'accès admin Skaleet via OAuth2 client credentials
    """
    # Try several possible token endpoints and auth methods to be tolerant with test environments
    candidate_paths = [
        "/oauth/token",
        "/oauth2/token",
        "/token"
    ]

    candidate_urls = []
    base = settings.skaleet_admin_base_url.rstrip('/')
    # If base already contains path like /api/v2/admin, keep it and also try shorter prefixes
    candidate_urls.append(f"{base}/oauth/token")
    candidate_urls.append(f"{base}/oauth2/token")
    candidate_urls.append(f"{base}/token")
    # Try removing common suffixes
    if "/admin" in base:
        prefix = base.replace('/admin', '')
        candidate_urls.append(f"{prefix}/oauth/token")
        candidate_urls.append(f"{prefix}/oauth2/token")
        candidate_urls.append(f"{prefix}/token")

    # De-duplicate
    candidate_urls = list(dict.fromkeys(candidate_urls))

    async with httpx.AsyncClient() as client:
        last_exc = None
        for url in candidate_urls:
            # 1) Try form body client credentials
            try:
                logger.info(f"Attempting to get admin token via form POST: {url}")
                response = await client.post(
                    url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": settings.skaleet_admin_client_id,
                        "client_secret": settings.skaleet_admin_client_secret,
                        "scope": "CardUpdate"
                    },
                    timeout=15.0
                )
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    if access_token:
                        logger.info(f"Obtained admin token from {url} (form)")
                        return access_token
                else:
                    logger.info(f"Form POST to {url} returned status {response.status_code}")
            except Exception as e:
                logger.debug(f"Form POST to {url} failed: {e}")
                last_exc = e

            # 2) Try HTTP Basic auth with grant_type in body
            try:
                logger.info(f"Attempting to get admin token via Basic auth POST: {url}")
                auth = (settings.skaleet_admin_client_id, settings.skaleet_admin_client_secret)
                response = await client.post(
                    url,
                    data={"grant_type": "client_credentials", "scope": "CardUpdate"},
                    auth=auth,
                    timeout=15.0
                )
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    if access_token:
                        logger.info(f"Obtained admin token from {url} (basic)")
                        return access_token
                else:
                    logger.info(f"Basic auth POST to {url} returned status {response.status_code}")
            except Exception as e:
                logger.debug(f"Basic auth POST to {url} failed: {e}")
                last_exc = e

        # If we reach here, no candidate succeeded
        logger.error("Failed to obtain admin token from candidate URLs")
        if last_exc:
            raise last_exc
        raise RuntimeError("Unable to obtain admin token from configured Skaleet Admin base URL")


async def send_card_operation_result(
    card_id: int, 
    operation_type: str, 
    result: str,
    pan_alias: str | None = None,
    visa_card_number: str | None = None,
    ni_details: dict | None = None
):
    """
    Envoie le résultat d'une opération carte à Skaleet Admin API
    
    Format de la requête selon le contrat Skaleet:
    POST {baseUrl}/cards/{id}/operation/{operation_type}/{result}
    
    Body:
    {
        "pan_alias": "string",
        "pan_display": "string",
        "external_id": "EXT123",
        "exp_month": 1,
        "exp_year": 1970
    }
    
    Args:
        card_id: ID de la carte Skaleet
        operation_type: Type d'opération (card_activation, card_blocking, card_unblocking, 
                       card_opposition, card_creation, card_suppression, etc.)
        result: Résultat de l'opération ("accept" ou "error")
        pan_alias: Alias PAN de la carte (ex: "CMS PARTNER-12345")
        visa_card_number: Numéro de carte VISA généré par NI (16 chiffres)
        ni_details: Détails supplémentaires de la réponse NI (optionnel)
    """
    token = await get_admin_token()
    # URL selon le format Skaleet: baseUrl/tagpay/cards/{id}/operation/{operation_type}/{result}
    # Certains environnements exposent le chemin 'tagpay' après le base admin path
    url = f"{settings.skaleet_admin_base_url}/tagpay/cards/{card_id}/operation/{operation_type}/{result}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Préparer le body selon le format Skaleet
    body = {}
    
    # pan_alias (obligatoire si disponible)
    if pan_alias:
        body["pan_alias"] = pan_alias
    
    # pan_display: numéro PAN complet (non masqué)
    if visa_card_number:
        body["pan_display"] = visa_card_number
    elif pan_alias:
        body["pan_display"] = pan_alias
    
    # external_id: ID externe (peut être le niCardId ou un identifiant unique)
    if ni_details and "niCardId" in ni_details:
        body["external_id"] = ni_details["niCardId"]
    else:
        body["external_id"] = f"NI-{card_id}"
    
    # exp_month et exp_year: extraire de expiryDate ou utiliser des valeurs par défaut
    if ni_details and "expiryDate" in ni_details:
        # Format attendu: "MM/YYYY" ou "12/2028"
        expiry_date = ni_details["expiryDate"]
        if "/" in expiry_date:
            parts = expiry_date.split("/")
            if len(parts) == 2:
                body["exp_month"] = int(parts[0])
                body["exp_year"] = int(parts[1])
    else:
        # Valeurs par défaut (3 ans à partir de maintenant)
        from datetime import datetime
        current_year = datetime.now().year
        body["exp_month"] = 12
        body["exp_year"] = current_year + 3
    
    logger.info(f"Sending operation result to Skaleet Admin: url={url}, card_id={card_id}, operation={operation_type}, result={result}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=body,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(
                f"Successfully sent operation result to Skaleet: "
                f"card_id={card_id}, operation={operation_type}, result={result}, "
                f"pan_alias={pan_alias}, pan_display={'***' + body.get('pan_display', '')[-4:] if body.get('pan_display') else 'N/A'}"
            )
        except httpx.HTTPError as e:
            logger.error(f"Skaleet API error when sending operation result: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
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

