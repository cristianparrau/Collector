from unittest.mock import patch, MagicMock
import requests
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check():
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "healthy"}


@patch("src.collector.ResilientAPIDataCollector.run")
def test_collect_success(mock_run):
  mock_run.return_value = {
      "received": 5,
      "valid": 5,
      "processed": 5,
      "failed": 0,
      "status": "SUCCESS",
  }
  response = client.post("/collect?max_records=5")
  assert response.status_code == 200
  assert response.json()["metrics"]["status"] == "SUCCESS"


@patch("src.collector.ResilientAPIDataCollector.run")
def test_collect_db_or_source_error(mock_run):
  """Valida respuesta 502 cuando el pipeline falla."""
  mock_run.return_value = {
      "received": 0,
      "valid": 0,
      "processed": 0,
      "failed": 0,
      "status": "FAILED",
  }
  response = client.post("/collect")
  assert response.status_code == 502


@patch("src.api.SessionLocal")
def test_list_records_success(mock_session_local):
  """Valida el endpoint GET /records mockeando la sesión de base de datos."""
  mock_session = MagicMock()
  mock_session_local.return_value = mock_session

  # Simulamos registros devueltos por la BD
  mock_record = MagicMock()
  mock_record.id = 1
  mock_record.user_id = 101
  mock_record.full_name = "Jane Doe"
  mock_record.email = "jane@example.com"
  mock_record.company_name = "Tech Corp"
  mock_record.status = "PROCESSED"

  mock_session.query().offset().limit().all.return_value = [mock_record]

  response = client.get("/records?limit=5&offset=0")
  assert response.status_code == 200
  data = response.json()
  assert data["total_returned"] == 1
  assert data["data"][0]["full_name"] == "Jane Doe"


@patch("src.api.SessionLocal")
def test_database_connection_failure(mock_session_local):
  """Valida el manejo de errores de base de datos (respuesta 503)."""
  mock_session_local.side_effect = Exception("Connection refused")

  response = client.get("/records")
  assert response.status_code == 503
  assert "Base de datos no disponible" in response.json()["detail"]