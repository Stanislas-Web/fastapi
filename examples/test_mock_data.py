"""
Exemple d'utilisation des données mockées NI
"""
import asyncio
from app.utils.mock_data import get_mock_ni_response, MOCK_CARDS, MOCK_WEBHOOKS
from app.infra.ni_client import NIClient
from app.core.config import settings

async def test_mock_responses():
    """Test des réponses mockées"""
    print("=" * 60)
    print("🧪 Test des données mockées NI")
    print("=" * 60)
    print()
    
    # Test direct des réponses mockées
    print("1. Test direct des réponses mockées:")
    print("-" * 60)
    
    operations = ["activate", "block", "unblock", "oppose"]
    for op in operations:
        response = get_mock_ni_response(op, card_id=12345, pan_alias="CMSPARTNER-12345")
        print(f"   {op:10} -> success={response.success}, status={response.status}")
    
    print()
    print("2. Test avec NIClient en mode mock:")
    print("-" * 60)
    
    # Activer le mode mock temporairement
    original_use_mock = settings.ni_use_mock
    settings.ni_use_mock = True
    
    try:
        client = NIClient()
        
        # Test activation
        response = await client.activate_card_in_ni(12345, "CMSPARTNER-12345")
        print(f"   Activation -> success={response.success}, status={response.status}")
        
        # Test blocage
        response = await client.block_card_in_ni(12346, "CMSPARTNER-12346")
        print(f"   Blocage    -> success={response.success}, status={response.status}")
        
    finally:
        settings.ni_use_mock = original_use_mock
    
    print()
    print("3. Cartes de test disponibles:")
    print("-" * 60)
    for i, card in enumerate(MOCK_CARDS, 1):
        print(f"   Carte {i}:")
        print(f"      - cardId: {card['cardId']}")
        print(f"      - panAlias: {card['panAlias']}")
        print(f"      - status: {card['status']}")
        print(f"      - cardType: {card['cardType']}")
        print(f"      - accountId: {card['accountId']}")
        print()
    
    print("4. Webhooks de test disponibles:")
    print("-" * 60)
    for event_name, webhook in MOCK_WEBHOOKS.items():
        print(f"   {event_name.upper()}:")
        print(f"      - cardId: {webhook['data']['cardId']}")
        print(f"      - panAlias: {webhook['data']['panAlias']}")
        print(f"      - event: {webhook['event']}")
        print(f"      - webhookId: {webhook['webhookId']}")
        print()
    
    print("=" * 60)
    print()
    print("📋 RÉSUMÉ DES CARTES DE TEST:")
    print("=" * 60)
    print("   Carte 1: cardId=12345, panAlias=CMSPARTNER-12345 (PENDING, VIRTUAL)")
    print("   Carte 2: cardId=12346, panAlias=CMSPARTNER-12346 (ACTIVE, PHYSICAL)")
    print("   Carte 3: cardId=12347, panAlias=CMSPARTNER-12347 (BLOCKED, VIRTUAL)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mock_responses())

