from unittest.mock import patch
import requests
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check():
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "healthy"}


@patch("src.api_collector.requests.Session.get")
def test_collect_source_error_real_failure(mock_get):
  """Valida el fallo real de la fuente interceptando session.get."""
  mock_get.side_effect = requests.exceptions.ConnectionError(
      "Connection error"
  )

  response = client.post("/collect")
  assert response.status_code == 502
  assert "falló" in response.json()["detail"]


@patch("src.api_collector.ResilientAPIDataCollector.run")
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
  data = response.json()
  assert data["message"] == "Proceso ejecutado con éxito"
  assert data["metrics"]["status"] == "SUCCESS"


def test_get_status():
  response = client.get("/status")
  assert response.status_code == 200
  metrics = response.json()
  assert "status" in metrics
  assert "received" in metrics
  assert "failed" in metrics