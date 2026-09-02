# API Data Collector

Proyecto de laboratorio en Python para consumir una API pública de forma resiliente, aplicar validación, transformación de datos y exportación a JSON.

## Estructura del Proyecto
- `src/`: Código fuente principal.
- `tests/`: Pruebas unitarias.

## Explicacion código
Api_collector.py -> Archivo principal del proyecto que contiene las clases y funciones para la ejecución del objeto del proyecto
- class ConfigManager:
  """Gestiona la lectura del archivo de configuración
- class ResilientAPIDataCollector:
  """Gestiona las funciones para hacer resiliente el codigo y controlar fallos como:"

Funciones para control de errores
  - Fallas en el consumo de API
  - Fallas en la estructura de los datos
  - Errores de Timeout

Funciones para control de información a procesar
  - Se agrega una funcionalidad para controlar cantidad de registros a procesar desde una variable parametrizable

Funciones para adecuación de la información
- Paginanación de la información para mejorar el consumo de la misma
- Realiza la transformación de los datos al formato esperado
- Creación del JSon con la información resultante
- Creación de resumen de ejeución


## 📁 Estructura del Proyecto

```text
api_collector/
│
├── config.ini               # Archivo de configuración externa
├── requirements.txt         # Dependencias del proyecto
├── src/
│   ├── __init__.py
│   └── api_collector.py         # Código fuente principal (Lógica y clases)
└── tests/
    ├── __init__.py
    └── test_collector.py    # Pruebas automatizadas unitarias

Servicio HTTP (FastAPI)

Para levantar la API localmente con recarga automática:

PowerShell
python -m uvicorn src.api:app --reload
Endpoints Disponibles

GET /health — Healthcheck liveness del servicio.

GET /status — Devuelve las métricas de la última ejecución en formato JSON.

POST /collect — Dispara el pipeline completo. Acepta parámetro opcional ?max_records=N. Retorna 200 OK con métricas o 502 Bad Gateway ante fallos de la fuente.

Documentación interactiva en navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Instalación postgress
docker run --name postgres_collector -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=datacollector_db -p 5432:5432 -d postgres:latest