FROM python:3.12.3-slim

WORKDIR /app

# Copiar el archivo de dependencias y luego instalarlas
COPY app/ .

RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar el script de inicialización
CMD ["python", "crearDB_poo.py"]

# CMD ["tail", "-f", "/dev/null"]