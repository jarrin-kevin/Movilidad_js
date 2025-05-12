# Movilidad de Estudiantes entre Campus

## Descripción

Este proyecto permite monitorear la movilidad de estudiantes entre diferentes campus de la universidad, capturando eventos de inicio de sesión vía syslog y procesando los datos para determinar **conexiones** y **movilizaciones**.

Dos scripts principales:

- **receiver**: recibe logs de syslog, aplica expresiones regulares para extraer usuario, AP y timestamp, descarta duplicados y empuja mensajes JSON a Redis. :contentReference
- **processor**: consume la cola de Redis, normaliza datos, compara campus anterior vs. actual del usuario, encola registros en MySQL y notifica movimientos por UDP. :contentReference. 

La orquestación se realiza con **Docker Compose**, que levanta contenedores para MySQL, Redis, receiver, processor (Node.js) y un init-job para crear la base de datos.


## Tabla de Contenidos

- [Estructura del Proyecto](#estructura-del-proyecto)  
- [Requisitos Previos](#requisitos-previos)  
- [Instalación y Despliegue](#instalación-y-despliegue)  
- [Configuración](#configuración)  
- [Uso](#uso)  
- [Detalles de Componentes](#detalles-de-componentes)  
- [Recomendaciones Adicionales](#recomendaciones-adicionales)  
- [Cómo funciona un README](#cómo-funciona-un-readme)  

## Estructura del Proyecto
```text
├── .env                # Variables de entorno (MySQL, Redis, puertos)
├── docker-compose.yml  # Orquestación de servicios
├── dbinit/             # Init-container: crea BD y tablas
│   ├── Dockerfile
│   └── app/
│       ├── crearDB_poo.py
│       └── CrearTablasDb.py
├── mysql-init/         # SQL de inicialización de usuarios
│   └── init.sql
├── receiver/           # Contenedor de captura UDP + parsing syslog
│   ├── Dockerfile
│   ├── rsyslog.conf
│   └── app/
│       ├── config.py
│       ├── receiver.py    # Lógica de extracción y push a Redis
│       └── requirements.txt
├── nodejs/             # Contenedor Node.js (processor)
│   ├── Dockerfile
│   └── app/
│       ├── package.json
│       └── processor.js   # Lógica de batching, MySQL, detección de género, UDP
├── processor/          # Versión Python del processor (no usada)
│   ├── Dockerfile
│   └── processor.py
└── rsyslogproxy/       # (Obsoleto: merged into receiver)
    ├── Dockerfile
    └── rsyslog.conf
```

## Requisitos Previos
* Docker instalado en el equipo
* Python ≥ 3.12 (para **receiver**)
* Node.js ≥ 18 (para **processor**)
* Redis y MySQL accesibles (configurados vía `.env`)

## Instalación y Despliegue
1. Clonar el repositorio.
2. Crear archivo `.env` con las credenciales necesarias.
3. Ejecutar en dos pasos:

   ```bash
   docker compose up -d mysql
   docker compose up -d
   ```

## Configuración
* **`.env`**: centraliza credenciales y puertos.
* **`docker-compose.yml`**: define límites de recursos, *healthchecks* y redes internas.

## Uso:

* **receiver** escucha en **514/udp** y empuja a la lista `socket_messages` de Redis.
* **processor** lee de `socket_messages`, agrupa en batches y:

  1. Inserta / actualiza la tabla **conexiones**.
  2. Registra en la tabla **movimientos**.
  3. Envía notificaciones de movilización por UDP.

## Detalles de Componentes

### Receiver (Python)

#### Archivos auxiliares

| Archivo         | Función breve                                                         |
| --------------- | --------------------------------------------------------------------- |
| `entrypoint.sh` | Lanza `rsyslog` y mantiene vivo el contenedor.                        |
| `rsyslog.conf`  | Habilita entrada UDP 514 y filtra mensajes que contengan un correo.   |
| `config.py`     | Centraliza host, puerto y contraseña de Redis, TTL y nombre de lista. |


#### Clases y responsabilidades

| Clase                    | Propósito (conciso)                                                                                                              | Métodos clave                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `DataReceiver` *(ABC)*   | Define la interfaz que cualquier receptor debe implementar.                                                                      | `receiver_data(data, addr)`                                                              |
| `RedisNotAvailableError` | Excepción propia cuando Redis no responde al `PING`.                                                                             | —                                                                                        |
| `receiver_udp`           | Lógica real del servidor UDP: abre el socket, extrae **correo/AP/timestamp**, deduplica en Redis y publica en `socket_messages`. | `__init__()` · `inicializar_servidor()` · `receiver_data()` · `process_syslog_message()` |
| `UDPServerProtocol`      | Adaptador `asyncio.DatagramProtocol` que pasa cada datagrama a `receiver_udp.receiver_data()`.                                   | `connection_made()` · `datagram_received()`                                              |


#### Pseudocódigo 
```text
main():
  cfg  = load_config()
  srv  = receiver_udp(cfg.host, cfg.port, cfg.redis_url)
  asyncio.run( srv.inicializar_servidor() )

receiver_udp.inicializar_servidor():
  await verificar_redis()                          # levanta RedisNotAvailableError si falla
  create_datagram_endpoint(UDPServerProtocol(self))
  while True:                                      # mantener vivo
      await asyncio.sleep(3600)

receiver_udp.receiver_data(data, addr):
  if data == b'ping': transport.sendto(b'pong', addr); return
  record = process_syslog_message(data.decode())
  if record is None: return                        # campos faltantes o duplicado
  redis.rpush('socket_messages', json.dumps(record))

receiver_udp.process_syslog_message(txt):
  email = email_re.search(txt)
  ap    = ap_re.search(txt)
  ts    = ts_re.search(txt)
  if not (email and ap and ts): return None
  key = f"{ts.group()}|{ap.group()}|{email.group()}"
  if not redis.set(key, 1, nx=True, ex=120): return None
  return {"user": email.group(), "ap": ap.group(), "timestamp": ts.group()}
  ```
### Processor (Node.js)

| Clase              | Propósito (conciso)                                                                                                            | Métodos clave                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `RedisConnector`   | Leer de `socket_messages` con `BLPOP` y mantener caché TTL (último campus / hora).                                             | `connect()` · `getMessage()` · `cacheLastCampus()` · `cacheLastTime()`                     |
| `DBHandler`        | Pool MySQL y operaciones **por lote** (conexiones y movimientos).                                                              | `bulkUpsertConexiones()` · `bulkInsertMovimientos()` · `getLastCampus()` · `getLastTime()` |
| `MovementNotifier` | Enviar eventos de movilización por UDP en formato JSON.                                                                        | `notifyMovement(event)`                                                                    |
| `DataProcessor`    | Orquestar todo: clasificar mensaje como **conexión** / **movimiento**, actualizar caché y decidir cuándo vaciar lotes a MySQL. | `processMessage(raw)` · `_flushBatches()`                                                  |

#### Pseudocódigo 
```text
main():
  redis     = new RedisConnector();   await redis.connect()
  db        = new DBHandler()
  notifier  = new MovementNotifier()
  logic     = new DataProcessor(db, notifier, redis)

  while true:
    raw = redis.getMessage('socket_messages', 1)     # BLPOP 1 s
    if raw === null: continue
    logic.processMessage(raw)

DataProcessor.processMessage(raw):
  msg        = JSON.parse(raw)
  campusNew  = normalizarCampus(msg.ap)
  campusOld  = redis.cacheLastCampus(msg.hash) ?? db.getLastCampus(msg.hash)

  connQueue.push( buildConexion(msg, campusNew) )    # siempre

  if campusOld && campusOld !== campusNew:           # movimiento
      movEvent = buildMovimiento(msg, campusOld, campusNew)
      movQueue.push(movEvent)
      notifier.notifyMovement(movEvent)

  redis.cacheLastCampus(msg.hash,  campusNew, 300)
  redis.cacheLastTime(msg.hash,    msg.timestamp, 300)

  if (connQueue.length + movQueue.length) >= 2000 || timeout_expiró():
      db.bulkUpsertConexiones(connQueue.splice(0))
      db.bulkInsertMovimientos(movQueue.splice(0))
```

