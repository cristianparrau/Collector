from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from src.config import ConfigManager
from src.api_collector import ResilientAPIDataCollector
from src.database import init_db, get_session_factory, RecordModel, ExecutionRunModel

app = FastAPI(title="Resilient API Data Collector Service", version="1.3")

config = ConfigManager("config.ini")
engine = init_db(config)  # Se inicializa explícitamente aquí, seguro para tests y arranque
SessionLocal = get_session_factory(engine)

collector = ResilientAPIDataCollector(config)


def get_db():
  """Maneja la sesión atrapando errores de conexión reales dentro del bloque try."""
  try:
    db = SessionLocal()
    yield db
  except Exception as e:
    raise HTTPException(
        status_code=503,
        detail=f"Base de datos no disponible o error de conexión: {e}",
    )
  finally:
    try:
      db.close()
    except UnboundLocalError:
      pass


@app.get("/health", summary="Healthcheck simple")
def health_check():
  return {"status": "healthy"}


@app.post("/collect", summary="Dispara el pipeline y persiste en Postgres")
def trigger_collection(
    max_records: int = Query(
        None, description="Sobrescribe el límite de registros"
    )
):
  try:
    metrics = collector.run(max_records_override=max_records)
  except Exception as e:
    raise HTTPException(
        status_code=502,
        detail=f"El pipeline falló durante la ejecución: {str(e)}",
    )

  if metrics.get("status") == "FAILED":
    raise HTTPException(
        status_code=502,
        detail="El pipeline falló al intentar comunicarse con la fuente externa.",
    )

  return {"message": "Proceso ejecutado y persistido con éxito", "metrics": metrics}


@app.get("/records", summary="Lista los registros persistidos con paginación")
def list_records(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
  records = db.query(RecordModel).offset(offset).limit(limit).all()
  return {
      "limit": limit,
      "offset": offset,
      "total_returned": len(records),
      "data": [
          {
              "id": r.id,
              "user_id": r.user_id,
              "full_name": r.full_name,
              "email": r.email,
              "company_name": r.company_name,
              "status": r.status,
          }
          for r in records
      ],
  }