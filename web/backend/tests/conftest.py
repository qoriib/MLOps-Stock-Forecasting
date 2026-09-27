import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.database_service import DatabaseService


@pytest.fixture
def client():
    """FastAPI TestClient fixture with mocked database lifecycle."""
    with patch.object(DatabaseService, "init_db", new_callable=AsyncMock), \
         patch.object(DatabaseService, "close_db", new_callable=AsyncMock):
        with TestClient(app) as test_client:
            yield test_client
