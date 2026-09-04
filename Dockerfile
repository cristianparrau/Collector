# Usamos una imagen oficial de Python ligera y optimizada
FROM python:3.10-slim

# Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias si alguna librería lo requiere
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero el archivo de requisitos para aprovechar el caché de capas de Docker
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente del proyecto
COPY . .

# Exponemos el puerto en el que corre Uvicorn
EXPOSE 8000

# Comando por defecto para arrancar la aplicación apuntando al host de red y puerto correctos
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]