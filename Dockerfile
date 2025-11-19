# Imagen oficial de python ligera
FROM python:3.10-slim

# creacion de la carpeta app dentro del contenedor
WORKDIR /app

# copia del archivo requirements-api.txt
COPY requirements-api.txt .

# intalacion de dependencias
# paquetes de linux
# librerias del sistema
RUN apt-get update && apt-get install

# instalacion de dependencias de python
# no guarda cache dentro del directorio
RUN pip install --no-cache-dir -r requirements-api.txt

# copia todo el proyecto local
# al WORKDIR (/app) dentro del contenedor
COPY . .

# comando de arranque para ejecutar la app cuando el contenedor se inicia
CMD ["uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]