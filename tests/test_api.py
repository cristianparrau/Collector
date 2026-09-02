from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api import app

client = TestClient(app)


def test_health_check():
  """Caso 1: Valida el endpoint de salud (liveness)."""
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "healthy"}


@patch("src.api_collector.ResilientAPIDataCollector.run")
def test_collect_success(mock_run):
  """Caso 2: Valida una ejecución exitosa de /collect con métricas en JSON."""
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
  assert data["metrics"]["received"] == 5


@patch("src.api_collector.ResilientAPIDataCollector.run")
def test_collect_source_error(mock_run):
  """Caso 3: Valida el manejo de errores reales (HTTP 502) si la fuente falla."""
  mock_run.return_value = {
      "received": 0,
      "valid": 0,
      "processed": 0,
      "failed": 0,
      "status": "FAILED",
  }

  response = client.post("/collect")
  assert response.status_code == 502
  assert "falló" in response.json()["detail"]


def test_get_status():
  """Valida la consulta del estado actual de las métricas (/status)."""
  response = client.get("/status")
  assert response.status_code == 200
  # Verifica que la respuesta contenga las llaves principales del diccionario de métricas
  metrics = response.json()
  assert "status" in metrics
  assert "received" in metrics
  assert "failed" in metrics