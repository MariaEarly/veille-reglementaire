from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_dashboard():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Veille Aggregator MVP' in response.text
