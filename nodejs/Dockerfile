# Dockerfile.nodejs
FROM node:18-slim

# Usuario no privilegiado (igual que Python)
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/false appuser

WORKDIR /app


#1) Copiar solo package.json 
COPY app/package*.json ./
# 2) Instalar dependencias de producción (incluye pino)
RUN npm install

# 3) Copiar el resto del código y asignar propietario
COPY --chown=appuser:appuser app/ .
# Cambiar la propiedad del directorio
RUN chown -R appuser:appuser /app

#3) Ajusta permisos y dueño en un solo paso
RUN chmod -R 755 /app \
    && chown -R appuser:appuser /app

USER appuser

# Exponemos el mismo puerto UDP que definiste en compose
EXPOSE 12349/udp

CMD ["npm", "start"]


      