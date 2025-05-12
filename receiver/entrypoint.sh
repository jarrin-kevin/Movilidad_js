#!/bin/bash

set -e

# Eliminar archivo PID si existe
rm -f /run/rsyslogd.pid

# Inicia rsyslog en segundo plano
rsyslogd

# Ejecuta tu aplicación Python
#exec python receiver.py
exec su -s /bin/bash -c "python /app/receiver.py" appuser