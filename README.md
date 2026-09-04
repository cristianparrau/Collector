# API Data Collector

Proyecto de laboratorio en Python para consumir una API pública de forma resiliente, aplicar validación, transformación de datos y exportación a JSON.

## Estructura del Proyecto
- `src/`: Código fuente principal.
- `tests/`: Pruebas unitarias.

## Requisitos Previos

Asegúrate de tener instalado en tu sistema operativo:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (con el motor de WSL 2 activo en Windows).
- Git (opcional para clonar el repositorio).

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
DataCollector/
│
├── .env                     # Variables de entorno y secretos centralizados
├── .dockerignore            # Archivos excluidos de la imagen de Docker
├── Dockerfile               # Instrucciones para empaquetar la API
├── docker-compose.yml       # Orquestador de contenedores (API + PostgreSQL)
├── config.ini               # Archivo de configuración externa por defecto
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Documentación y guía de despliegue en un comando
├── src/
│   ├── __init__.py
│   ├── api.py               # Aplicación FastAPI y endpoints web
│   ├── api_collector.py     # Lógica principal del colector y transformación
│   ├── config.py            # Gestor centralizado de configuración
│   └── database.py          # Modelos SQLAlchemy y conexión a Postgres
└── tests/
    ├── __init__.py
    └── test_collector.py    # Pruebas automatizadas unitarias e integración

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


## Despliegue Rápido (Un Solo Paso)

No necesitas instalar Python ni configurar bases de datos de forma local. Todo el entorno (API + PostgreSQL) se despliega automáticamente mediante Docker Compose.

1. Clona el repositorio o sitúate en la carpeta raíz del proyecto.
2. Ejecuta el siguiente comando en tu terminal:

   ```bash
   docker compose up --build