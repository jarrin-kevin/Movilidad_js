FROM python:3.12.3-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y --no-install-recommends \
            gcc \
            rsyslog \
            procps \
            iputils-ping \
            tcpdump && \
            apt clean && \
            rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/false appuser

WORKDIR /app


# Copiar requirements y instalar dependencias
COPY app/ .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R appuser:appuser /app

RUN pip install --no-cache-dir -r requirements.txt



# Configurar permisos adecuados
RUN chmod 644 config.py && chown appuser:appuser config.py && \
    mkdir -p /tmp/cache && \
    chown -R appuser:appuser /tmp/cache && \
    chmod 700 /tmp/cache

    # Crear el archivo de log y asignar permisos
RUN touch /var/log/receiver.log && \
    chown appuser:appuser /var/log/receiver.log && \
    chmod 664 /var/log/receiver.log

EXPOSE 514


ENTRYPOINT ["/entrypoint.sh"]
