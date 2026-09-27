def test_read_root(client):
    """Test root endpoint returns correct status code and schema."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "endpoints" in data
    assert data["endpoints"]["models"] == "/api/models"
    assert data["endpoints"]["predict"] == "/api/models/predict"
    assert data["endpoints"]["stocks"] == "/api/stocks/{ticker}"


def test_docs_available(client):
    """Test OpenAPI documentation page is reachable."""
    response = client.get("/docs")
    assert response.status_code == 200
