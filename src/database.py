import os
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class ExecutionRunModel(Base):
  __tablename__ = "execution_runs"

  id = Column(Integer, primary_key=True, autoincrement=True)
  received = Column(Integer, default=0)
  valid = Column(Integer, default=0)
  processed = Column(Integer, default=0)
  failed = Column(Integer, default=0)
  status = Column(String(50), default="PENDING")
  limit_val = Column(Integer, default=0)
  timestamp = Column(DateTime, default=datetime.utcnow)

  records = relationship("RecordModel", back_populates="execution")


class RecordModel(Base):
  __tablename__ = "records"

  id = Column(Integer, primary_key=True, autoincrement=True)
  execution_id = Column(Integer, ForeignKey("execution_runs.id"))
  user_id = Column(Integer)
  full_name = Column(String(255))
  email = Column(String(255))
  company_name = Column(String(255))
  status = Column(String(50))

  execution = relationship("ExecutionRunModel", back_populates="records")


def get_db_engine(config_manager):
  # Prioriza variable de entorno si existe, de lo contrario lee del config.ini
  db_url = os.getenv("DB_URL")
  if not db_url:
    try:
      db_url = config_manager.config.get("DATABASE", "db_url")
    except Exception:
      db_url = "postgresql://postgres:postgres@localhost:5432/datacollector_db"

  return create_engine(db_url)