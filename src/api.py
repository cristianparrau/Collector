from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from src.collector import ConfigManager, ResilientAPIDataCollector
from src.database import get_db_engine, RecordModel, ExecutionRunModel
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="Resilient API Data Collector Service", version="1.2")

config = ConfigManager("config.ini")
collector = ResilientAPIDataCollector(config)

engine = get_db_engine(config)
SessionLocal = sessionmaker(bind=engine)


def get_db():
  db = SessionLocal()
  try:
    yield db
  except Exception as e:
    raise HTTPException(
        status_code=503,
        detail=f"Base de datos no disponible o error de conexión: {e}",
    )
  finally:
    db.close()


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


@app.get("/status", summary="Consulta el estado de la última ejecución")
def get_status():
  return collector.metrics


@app.get("/records", summary="Lista los registros persistidos con paginación")
def list_records(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
  """Devuelve una lista paginada de registros almacenados en la base de datos."""
  records = (
      db.query(RecordModel).offset(offset).limit(limit).all()
  )
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