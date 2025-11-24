import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    """Test que l'endpoint /health retourne le bon statut"""
    client = TestClient(app)
    
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_with_client_fixture(client):
    """Test de l'endpoint /health avec la fixture client"""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

