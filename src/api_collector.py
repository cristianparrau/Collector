import json
import logging
from typing import Any, Dict, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Configurar el sistema de registros
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ResilientAPIDataCollector:

  def __init__(self, base_endpoint: str):
    self.base_endpoint = base_endpoint
    self.session = self._create_resilient_session()

  def _create_resilient_session(self) -> requests.Session:
    """Configura una sesión HTTP con políticas de reintento automático (backoff)."""
    session = requests.Session()

    # Definimos la estrategia de reintentos
    retries = Retry(
        total=3,  # Número máximo de reintentos
        backoff_factor=1,  # Tiempo de espera entre intentos (1s, 2s, 4s...)
        status_forcelist=[
            500,
            502,
            503,
            504,
        ],  # Códigos HTTP que disparan un reintento
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

  def fetch_paginated_data(
      self, limit_per_page: int = 5
  ) -> List[Dict[str, Any]]:
    """Paso 1 (Modificado): Consumir la API pública aplicando Paginación y Reintentos."""
    all_data = []
    page = 1

    while True:
      # Simulación común de paginación mediante parámetros _page y _limit
      params = {"_page": page, "_limit": limit_per_page}

      try:
        logging.info(
            f"Consultando página {page} en el endpoint: {self.base_endpoint}"
        )
        response = self.session.get(
            self.base_endpoint, params=params, timeout=10
        )
        response.raise_for_status()

        data = response.json()

        # Si la API devuelve una lista vacía, significa que llegamos al final de la paginación
        if not data:
          logging.info("Se han recorrido todas las páginas disponibles.")
          break

        all_data.extend(data)
        page += 1

      except requests.exceptions.RequestException as e:
        logging.error(f"Error crítico al conectar con la API en la página {page}: {e}")
        break

    logging.info(
        f"Recolección completa. Total de registros obtenidos: {len(all_data)}"
    )
    return all_data

  def validate_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Paso 2: Validación de datos obligatorios."""
    valid_records = []
    for record in records:
      if all(
          key in record and record[key]
          for key in ["id", "name", "email", "company"]
      ):
        valid_records.append(record)
      else:
        logging.warning(
            f"Registro descartado por falta de campos obligatorios ID: {record.get('id', 'Desconocido')}"
        )
    logging.info(
        f"Registros validados con éxito: {len(valid_records)} de {len(records)}"
    )
    return valid_records

  def transform_data(
      self, records: List[Dict[str, Any]]
  ) -> List[Dict[str, Any]]:
    """Paso 3: Transformación y normalización de la estructura."""
    transformed_records = []
    for record in records:
      transformed = {
          "user_id": record.get("id"),
          "full_name": record.get("name").strip().title(),
          "email": record.get("email").lower(),
          "company_name": record.get("company", {}).get("name", "N/A"),
          "status": "Active",
      }
      transformed_records.append(transformed)
    logging.info("Transformación aplicada correctamente.")
    return transformed_records

  def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> None:
    """Paso 4: Exportar a un archivo JSON."""
    try:
      with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
      logging.info(f"Datos guardados exitosamente en '{filename}'")
    except IOError as e:
      logging.error(f"Error al escribir el archivo JSON: {e}")

  def run(self, output_filename: str = "paginated_collected_data.json"):
    """Ejecuta el pipeline completo."""
    raw_data = self.fetch_paginated_data(limit_per_page=3)
    if not raw_data:
      logging.warning("Proceso detenido: No se obtuvieron datos.")
      return

    validated_data = self.validate_data(raw_data)
    if not validated_data:
      logging.warning("Proceso detenido: Ningún registro pasó la validación.")
      return

    final_data = self.transform_data(validated_data)
    self.save_to_json(final_data, output_filename)


if __name__ == "__main__":
  API_URL = "https://jsonplaceholder.typicode.com/users"
  collector = ResilientAPIDataCollector(API_URL)
  collector.run("usuarios_paginados_procesados.json")