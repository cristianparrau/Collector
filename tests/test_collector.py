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
    self.config_mock.retries = 3
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

@patch("src.api_collector.Retry")
@patch("src.api_collector.HTTPAdapter")
def test_retry_configuration(self, mock_retry, mock_adapter):
    # Aseguramos que el mock use el nombre exacto 'retries'
    self.config_mock.retries = 3

    # Instanciamos usando el self de la clase de pruebas
    ResilientAPIDataCollector(self.config_mock)

    # Validamos que Retry se inicialice con el valor correcto de retries
    mock_retry.assert_called_once_with(
        total=self.config_mock.retries,
        backoff_factor=self.config_mock.backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )

    # Validamos que el adaptador HTTP reciba la estrategia generada
    mock_adapter.assert_called_once_with(max_retries=mock_retry.return_value)

@patch("src.api_collector.requests.Session")
def test_max_records_normal_limit(self, mock_session_class):
    """Tarea 3: Límite normal (ej. 3 registros con páginas de 5)"""
    self.config_mock.max_records = 3
    collector = ResilientAPIDataCollector(self.config_mock)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "User 1", "email": "u1@test.com", "company": {"name": "C"}},
        {"id": 2, "name": "User 2", "email": "u2@test.com", "company": {"name": "C"}},
        {"id": 3, "name": "User 3", "email": "u3@test.com", "company": {"name": "C"}},
        {"id": 4, "name": "User 4", "email": "u4@test.com", "company": {"name": "C"}},
        {"id": 5, "name": "User 5", "email": "u5@test.com", "company": {"name": "C"}},
    ]
    mock_session_class.return_value.get.return_value = mock_response
    collector.session = mock_session_class.return_value

    data = collector.fetch_paginated_data()
    self.assertEqual(len(data), 3)

@patch("src.api_collector.requests.Session")
def test_max_records_unlimited(self, mock_session_class):
    """Tarea 3: Sin límite (max_records = 0) trae todas las páginas"""
    self.config_mock.max_records = 0
    collector = ResilientAPIDataCollector(self.config_mock)

    # Simulamos 2 páginas: la primera con 2 elementos y la segunda vacía para cortar
    mock_resp_1 = MagicMock()
    mock_resp_1.status_code = 200
    mock_resp_1.json.return_value = [
        {"id": 1, "name": "U1", "email": "u1@test.com", "company": {"name": "C"}},
        {"id": 2, "name": "U2", "email": "u2@test.com", "company": {"name": "C"}},
    ]

    mock_resp_2 = MagicMock()
    mock_resp_2.status_code = 200
    mock_resp_2.json.return_value = []

    mock_session = mock_session_class.return_value
    mock_session.get.side_effect = [mock_resp_1, mock_resp_2]
    collector.session = mock_session

    data = collector.fetch_paginated_data()
    self.assertEqual(len(data), 2)

@patch("src.api_collector.requests.Session")
def test_max_records_mid_page_limit(self, mock_session_class):
    """Tarea 3: Límite alcanzado en mitad de página (ej. pedir 3 de una página de 5)"""
    self.config_mock.max_records = 3
    collector = ResilientAPIDataCollector(self.config_mock)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "User 1", "email": "u1@test.com", "company": {"name": "C"}},
        {"id": 2, "name": "User 2", "email": "u2@test.com", "company": {"name": "C"}},
        {"id": 3, "name": "User 3", "email": "u3@test.com", "company": {"name": "C"}},
        {"id": 4, "name": "User 4", "email": "u4@test.com", "company": {"name": "C"}},
        {"id": 5, "name": "User 5", "email": "u5@test.com", "company": {"name": "C"}},
    ]
    mock_session_class.return_value.get.return_value = mock_response
    collector.session = mock_session_class.return_value

    data = collector.fetch_paginated_data()
    self.assertEqual(len(data), 3)
    self.assertEqual(data[0]["id"], 1)
    self.assertEqual(data[2]["id"], 3)

if __name__ == "__main__":
  unittest.main()