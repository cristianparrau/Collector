from fastapi import FastAPI, HTTPException, Query
from src.api_collector import ConfigManager, ResilientAPIDataCollector

app = FastAPI(
    title="Resilient API Data Collector Service",
    version="1.1",
    description=(
        "Servicio HTTP para la extracción y transformación resiliente de datos."
    ),
)

# Inicializamos la configuración y el colector globalmente
config = ConfigManager("config.ini")
collector = ResilientAPIDataCollector(config)


@app.get("/health", summary="Healthcheck simple")

def health_check():
  """Verifica que el servicio esté activo y operando."""
  return {"status": "healthy"}


@app.post("/collect", summary="Dispara el pipeline de recolección")
def trigger_collection(
    max_records: int = Query(
        None, description="Sobrescribe el límite de registros"
    )
):
  """Ejecuta la extracción, validación, transformación y guardado."""
  metrics = collector.run(max_records_override=max_records)

  # Manejo de errores real: si la fuente falla, devolvemos un código 502/500
  if metrics.get("status") == "FAILED":
    raise HTTPException(
        status_code=502,
        detail=(
            "El pipeline falló al intentar comunicarse con la fuente externa"
            " de datos."
        ),
    )

  return {
      "message": "Proceso ejecutado con éxito",
      "metrics": metrics,
  }


@app.get(
    "/status", summary="Consulta el estado de la última ejecución"
)
def get_status():
  """Devuelve el diccionario de métricas de la última ejecución registrada."""
  return collector.metrics