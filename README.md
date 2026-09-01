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

