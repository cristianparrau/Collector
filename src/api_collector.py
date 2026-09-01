import json
import configparser
import logging
import time
from typing import Any, Dict, List
from unittest.mock import PropertyMock

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Configurar el sistema de registros
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class ConfigManager:
  """Gestiona la lectura del archivo de configuración (RF-01)."""

  def __init__(self, config_path: str = "config.ini"):
    self.config = configparser.ConfigParser()
    self.config.read(config_path)

  @property
  def api_url(self) -> str:
    return self.config.get("DEFAULT", "api_url")

  @property
  def timeout(self) -> int:
    return self.config.getint("DEFAULT", "timeout")

  @property
  def retries(self) -> int:
    return self.config.getint("DEFAULT", "retries")

  @property
  def max_records(self) -> int:
    return self.config.getint("DEFAULT", "max_records")

  @property
  def backoff_factor(self) -> int:
    return self.config.getint("DEFAULT", "backoff_factor")

  @property
  def output_filename(self) -> str:
    return self.config.get("DEFAULT", "output_filename")

class ResilientAPIDataCollector:

  def __init__(self, config: ConfigManager):
    self.config = config
    self.session = self._create_resilient_session()
    self.metrics = {
      "received":0,
      "valid":0,
      "processed":0,
      "failed":0,
      "status":"PENDING",
    }

  def _create_resilient_session(self) -> requests.Session:
    """Configura reintentos automáticos para errores temporales (RF-04)."""
    session = requests.Session()
    retries = Retry(
        total=self.config.retries,
        backoff_factor=self.config.backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

  def fetch_paginated_data(self) -> List[Dict[str, Any]]:
    """Consulta la API externa manejando timeouts, cantidad maxima registros y errores HTTP (RF-02, RF-03)."""
    all_data = []
    page = 1
    records = 0
    limit_per_page = 5
    max = self.config.max_records

    logging.info(f"Inicio del proceso de recolección.")
    logging.info(f"Fuente consultada: {self.config.api_url}")

    while True:
      params = {"_page": page, "_limit": limit_per_page}
      try:
        response = self.session.get(
          self.config.api_url, params=params, timeout=self.config.timeout
        )
        response.raise_for_status()
        data = response.json()

        if not data:
          break

        if max > 0 and (len(all_data) + len(data)) >= max:
          restantes = max - len(all_data)
          all_data.extend(data[:restantes])
          break

        all_data.extend(data)
        page += 1


      except requests.exceptions.Timeout:
        logging.error(
          f"[Componente: fetch_paginated_data] Error: Timeout al conectar"
          f" con la API en la página {page}"
        )
        self.metrics["status"] = "FAILED"
        break
      except requests.exceptions.HTTPError as e:
        logging.error(
          f"[Componente: fetch_paginated_data] Error HTTP: {e}"
        )
        self.metrics["status"] = "FAILED"
        break
      except requests.exceptions.RequestException as e:
        logging.error(
          f"[Componente: fetch_paginated_data] API no disponible o error de"
          f" red: {e}"
        )
        self.metrics["status"] = "FAILED"
        break

    self.metrics["received"] = len(all_data)
    logging.info(f"Cantidad de registros recibidos: {self.metrics['received']}")
    return all_data

  def validate_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Valida los datos descartando registros incompletos (RF-05)."""
    valid_records = []
    for record in records:
      if all(
              key in record and record[key]
              for key in ["id", "name", "email", "company"]
      ):
        valid_records.append(record)
      else:
        self.metrics["failed"] += 1
        logging.warning(
          f"[Componente: validate_data] Registro inválido o incompleto"
          f" descartado. ID: {record.get('id', 'Desconocido')}"
        )

    self.metrics["valid"] = len(valid_records)
    logging.info(f"Cantidad de registros válidos: {self.metrics['valid']}")
    return valid_records

  def transform_data(
          self, records: List[Dict[str, Any]]
  ) -> List[Dict[str, Any]]:
    """Transforma y normaliza los registros válidos."""
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

    self.metrics["processed"] = len(transformed_records)
    logging.info(
      f"Cantidad de registros procesados: {self.metrics['processed']}"
    )

    if self.config.max_records == 0:
      self.metrics["limit"] = 'UNLIMITED'
    else:
      self.metrics["limit"] = self.config.max_records

    return transformed_records

  def save_to_json(self, data: List[Dict[str, Any]]) -> None:
    """Guarda el resultado en archivo con manejo de errores de escritura (RF-02)."""
    try:
      with open(self.config.output_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
      logging.info(f"Datos guardados exitosamente en {self.config.output_filename}")
    except IOError as e:
      logging.error(
        f"[Componente: save_to_json] Error al escribir el archivo JSON: {e}"
      )
      self.metrics["status"] = "FAILED"

  def run(self):
    """Ejecuta el pipeline completo y muestra el resumen (RF-06)."""
    start_time = time.time()

    raw_data = self.fetch_paginated_data()
    if not raw_data and self.metrics["status"] == "FAILED":
      self._print_summary(start_time)
      return

    validated_data = self.validate_data(raw_data)
    if not validated_data and self.metrics["received"] > 0:
      logging.warning("Ningún registro superó la validación.")

    final_data = self.transform_data(validated_data)
    self.save_to_json(final_data)

    if self.metrics["status"] != "FAILED":
      self.metrics["status"] = "SUCCESS"

    logging.info("Finalización del proceso.")
    self._print_summary(start_time)

  def _print_summary(self, start_time: float):
    """Imprime el resumen de ejecución requerido (RF-06)."""
    execution_time = round(time.time() - start_time, 2)
    print("\n=========================")
    print("COLLECTION SUMMARY")
    print("=========================")
    print(f"Records received: {self.metrics['received']}")
    print(f"Records processed: {self.metrics['processed']}")
    print(f"Limit configured: {self.metrics['limit']}")
    print(f"Records valid: {self.metrics['valid']}")
    print(f"Records failed: {self.metrics['failed']}")
    print(f"\nExecution time: {execution_time} seconds")
    print(f"\nStatus: {self.metrics['status']}")
    print("=========================\n")


if __name__ == "__main__":
  config = ConfigManager("config.ini")
  collector = ResilientAPIDataCollector(config)
  collector.run()