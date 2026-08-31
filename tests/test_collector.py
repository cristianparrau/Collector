import unittest
from src.api_collector import ResilientAPIDataCollector


class TestAPIDataCollector(unittest.TestCase):

  def setUp(self):
    # Instanciamos el colector con una URL de prueba
    self.collector = ResilientAPIDataCollector(
        "https://jsonplaceholder.typicode.com/users"
    )

  def test_transform_data(self):
    """Prueba que la transformación limpie nombres y correos correctamente."""
    sample_raw_data = [{
        "id": 1,
        "name": "  leanne graham  ",
        "email": "SENSITIVE@GMAIL.COM",
        "company": {"name": "Romaguera-Crona"},
    }]

    transformed = self.collector.transform_data(sample_raw_data)

    self.assertEqual(len(transformed), 1)
    self.assertEqual(transformed[0]["full_name"], "Leanne Graham")
    self.assertEqual(transformed[0]["email"], "sensitive@gmail.com")
    self.assertEqual(transformed[0]["status"], "Active")


if __name__ == "__main__":
  unittest.main()