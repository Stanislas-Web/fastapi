import httpx
from app.core.config import settings
from app.schemas.ni import NIRequest, NIResponse
import logging

logger = logging.getLogger(__name__)


class NIClient:
    def __init__(self):
        self.base_url = settings.ni_base_url
        self.api_key = settings.ni_api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_card(self, card_id: str, metadata: dict = None) -> NIResponse:
        request_data = NIRequest(
            card_id=card_id,
            action="create",
            metadata=metadata
        )
        return await self._make_request(request_data)
    
    async def activate_card(self, card_id: str) -> NIResponse:
        request_data = NIRequest(
            card_id=card_id,
            action="activate"
        )
        return await self._make_request(request_data)
    
    async def block_card(self, card_id: str) -> NIResponse:
        request_data = NIRequest(
            card_id=card_id,
            action="block"
        )
        return await self._make_request(request_data)
    
    async def unblock_card(self, card_id: str) -> NIResponse:
        request_data = NIRequest(
            card_id=card_id,
            action="unblock"
        )
        return await self._make_request(request_data)
    
    async def activate_card_in_ni(self, card_id: int, pan_alias: str | None) -> NIResponse:
        """
        Active une carte dans NI
        """
        # Utiliser panAlias si disponible, sinon cardId en string
        card_reference = pan_alias if pan_alias else str(card_id)
        
        payload = {
            "cardReference": card_reference
        }
        
        url = f"{self.base_url}/cards/activate"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
                
                # Adapter la réponse pour correspondre au schéma NIResponse
                return NIResponse(
                    success=response_data.get("success", True),
                    status=response_data.get("status", "success"),
                    details=response_data.get("details")
                )
            except httpx.HTTPError as e:
                logger.error(f"NI API error when activating card {card_id}: {e}")
                # Retourner une réponse d'erreur
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected error when activating card {card_id}: {e}", exc_info=True)
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
    
    async def block_card_in_ni(self, card_id: int, pan_alias: str | None) -> NIResponse:
        """
        Bloque une carte dans NI
        """
        # Utiliser panAlias si disponible, sinon cardId en string
        card_reference = pan_alias if pan_alias else str(card_id)
        
        payload = {
            "cardReference": card_reference
        }
        
        url = f"{self.base_url}/cards/block"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
                
                # Adapter la réponse pour correspondre au schéma NIResponse
                return NIResponse(
                    success=response_data.get("success", True),
                    status=response_data.get("status", "success"),
                    details=response_data.get("details")
                )
            except httpx.HTTPError as e:
                logger.error(f"NI API error when blocking card {card_id}: {e}")
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected error when blocking card {card_id}: {e}", exc_info=True)
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
    
    async def unblock_card_in_ni(self, card_id: int, pan_alias: str | None) -> NIResponse:
        """
        Débloque une carte dans NI
        """
        # Utiliser panAlias si disponible, sinon cardId en string
        card_reference = pan_alias if pan_alias else str(card_id)
        
        payload = {
            "cardReference": card_reference
        }
        
        url = f"{self.base_url}/cards/unblock"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
                
                # Adapter la réponse pour correspondre au schéma NIResponse
                return NIResponse(
                    success=response_data.get("success", True),
                    status=response_data.get("status", "success"),
                    details=response_data.get("details")
                )
            except httpx.HTTPError as e:
                logger.error(f"NI API error when unblocking card {card_id}: {e}")
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected error when unblocking card {card_id}: {e}", exc_info=True)
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
    
    async def oppose_card_in_ni(self, card_id: int, pan_alias: str | None) -> NIResponse:
        """
        Oppose une carte dans NI
        """
        # Utiliser panAlias si disponible, sinon cardId en string
        card_reference = pan_alias if pan_alias else str(card_id)
        
        payload = {
            "cardReference": card_reference
        }
        
        url = f"{self.base_url}/cards/oppose"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
                
                # Adapter la réponse pour correspondre au schéma NIResponse
                return NIResponse(
                    success=response_data.get("success", True),
                    status=response_data.get("status", "success"),
                    details=response_data.get("details")
                )
            except httpx.HTTPError as e:
                logger.error(f"NI API error when opposing card {card_id}: {e}")
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected error when opposing card {card_id}: {e}", exc_info=True)
                return NIResponse(
                    success=False,
                    status="error",
                    details={"error": str(e)}
                )
    
    async def _make_request(self, request: NIRequest) -> NIResponse:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/cards",
                    json=request.dict(),
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                response_data = response.json()
                return NIResponse(
                    success=response_data.get("success", True),
                    status=response_data.get("status", "success"),
                    details=response_data.get("details")
                )
            except httpx.HTTPError as e:
                logger.error(f"NI API error: {e}")
                raise

