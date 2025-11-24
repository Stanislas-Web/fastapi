import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.schemas.webhook import SkaleetCardEvent
from app.schemas.ni import NIResponse


@pytest.fixture
def activation_webhook_payload():
    """Payload de webhook pour activation de carte"""
    return {
        "id": "2401597",
        "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
        "type": "card",
        "event": "card.status.activation_requested",
        "data": {
            "cardId": 12345,
            "panAlias": "CMSPARTNER-12345"
        }
    }


def test_webhook_activation_endpoint(client, activation_webhook_payload):
    """Test que l'endpoint webhook activation fonctionne correctement"""
    
    # Mock des appels externes et des fonctions d'idempotence
    with patch('app.utils.idempotency.is_webhook_processed', new_callable=AsyncMock, return_value=False), \
         patch('app.utils.idempotency.mark_webhook_started', new_callable=AsyncMock) as mock_mark_started, \
         patch('app.utils.idempotency.mark_webhook_finished', new_callable=AsyncMock) as mock_mark_finished, \
         patch('app.domain.services.NIClient') as mock_ni_class, \
         patch('app.domain.services.send_card_operation_result', new_callable=AsyncMock) as mock_skaleet:
        
        # Configurer les mocks
        mock_ni_instance = MagicMock()
        mock_ni_instance.activate_card_in_ni = AsyncMock(
            return_value=NIResponse(
                success=True,
                status="success",
                details={}
            )
        )
        mock_ni_class.return_value = mock_ni_instance
        
        mock_skaleet.return_value = None
        
        mock_operation = MagicMock()
        mock_operation.id = "test-operation-id"
        mock_mark_started.return_value = mock_operation
        mock_mark_finished.return_value = None
        
        # Faire la requête
        response = client.post(
            "/api/v1/webhooks/skaleet/card",
            json=activation_webhook_payload
        )
        
        # Vérifications
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["event"] == "card.status.activation_requested"


def test_webhook_activation_idempotent(client, activation_webhook_payload):
    """Test que l'endpoint webhook gère l'idempotence"""
    
    # Mock pour simuler un webhook déjà traité
    with patch('app.utils.idempotency.is_webhook_processed', new_callable=AsyncMock, return_value=True):
        
        response = client.post(
            "/api/v1/webhooks/skaleet/card",
            json=activation_webhook_payload
        )
        
        # Le webhook devrait être traité comme idempotent
        assert response.status_code == 200
        data = response.json()
        # Le service retourne toujours ok: true même si idempotent
        assert data.get("ok") is True

