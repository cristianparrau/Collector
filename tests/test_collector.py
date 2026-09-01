import unittest
from unittest.mock import MagicMock, patch
import requests
from src.api_collector import ConfigManager, ResilientAPIDataCollector


class TestResilientAPIDataCollector(unittest.TestCase):

  def setUp(self):
    # Mock de la configuración para evitar depender de config.ini real en las pruebas
    self.config_mock = MagicMock(spec=ConfigManager)
    self.config_mock.api_url = "https://api.test.com/users"
    self.config_mock.timeout = 5
    self.config_mock.max_retries = 3
    self.config_mock.backoff_factor = 1
    self.config_mock.output_filename = "test_output.json"

    self.collector = ResilientAPIDataCollector(self.config_mock)

  def test_transform_data_valid_input(self):
    """1. Prueba de Transformación: Input válido -> Output esperado"""
    raw_records = [{
        "id": 1,
        "name": "  ana gomez  ",
        "email": "ANA.GOMEZ@TEST.COM",
        "company": {"name": "Innovate SA"},
    }]

    transformed = self.collector.transform_data(raw_records)

    self.assertEqual(len(transformed), 1)
    self.assertEqual(transformed[0]["user_id"], 1)
    self.assertEqual(transformed[0]["full_name"], "Ana Gomez")
    self.assertEqual(transformed[0]["email"], "ana.gomez@test.com")
    self.assertEqual(transformed[0]["company_name"], "Innovate SA")
    self.assertEqual(transformed[0]["status"], "Active")

  def test_validate_data_invalid_input(self):
    """2. Prueba de Datos Inválidos: Input incompleto -> Rechazado"""
    invalid_records = [
        {"id": 2, "name": "Sin email"},  # Falta email y company
        {
            "id": 3,
            "email": "carlos@test.com",
            "company": {"name": "Dev"},
        },  # Falta name
    ]

    valid = self.collector.validate_data(invalid_records)

    self.assertEqual(len(valid), 0)
    self.assertEqual(self.collector.metrics["failed"], 2)

  @patch("src.api_collector.requests.Session")
  def test_api_error_handling(self, mock_session_class):
    """3. Prueba de Error de API: Manejo controlado de excepciones"""
    mock_session_instance = mock_session_class.return_value
    # Simular que la API lanza un RequestException (red caída o no disponible)
    mock_session_instance.get.side_effect = (
        requests.exceptions.RequestException("Connection error")
    )

    self.collector.session = mock_session_instance
    data = self.collector.fetch_paginated_data()

    self.assertEqual(len(data), 0)
    self.assertEqual(self.collector.metrics["status"], "FAILED")

@patch("src.collector.Retry")
@patch("src.collector.HTTPAdapter")
def test_retry_configuration(self, mock_adapter, mock_retry):
    """4. Prueba de Reintentos: Verifica configuración de reintentos en sesión"""
    ResilientAPIDataCollector(self.config_mock)

    mock_retry.assert_called_with(
        total=self.config_mock.max_retries,
        backoff_factor=self.config_mock.backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )


if __name__ == "__main__":
  unittest.main()