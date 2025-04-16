# ThreatLog-AI-generate-logs

Pequeña aplicacion para generar logs de un servidor ficticio y enviarlo al AWS.

Consiste en una pequeña aplicación utilizando Python que sea capaz de generar logs ficticios de Outlook cada cierto tiempo y que los envíe directamente y de forma automatizada por AWS S3 para tenerlo almacenado

## Entorno de desarrollo

Prepara el entorno virtual local para instalar los paquetes necesarios.

### Requisitos previos

1. **Instalar Python**:
   - Asegúrate de tener Python instalado en tu sistema. Puedes descargarlo desde la [página oficial de Python](https://www.python.org/downloads/).
   - Durante la instalación, marca la opción **"Add Python to PATH"** para facilitar el uso de Python desde la terminal.

2. **Instalar el módulo `venv`**:
   - El módulo `venv` viene incluido en las versiones modernas de Python (3.3+). Si no está disponible, asegúrate de que tu instalación de Python incluye las herramientas necesarias.
   - En sistemas basados en Linux, puedes instalarlo con:

     ```bash
     sudo apt install python3-venv
     ```

3. **Gestionar múltiples versiones de Python** (opcional):
   - Si necesitas trabajar con diferentes versiones de Python, puedes usar herramientas como:
     - [pyenv](https://github.com/pyenv/pyenv): Una herramienta para instalar y gestionar múltiples versiones de Python.
     - [Anaconda](https://www.anaconda.com/): Una distribución de Python para ciencia de datos que incluye herramientas para gestionar entornos.

### Crear y activar el entorno virtual

Sigue estos pasos para configurar el entorno virtual:

1. **Crear el entorno virtual**:

   ```bash
   python -m venv .venv
   ```

2. **Activar el entorno virtual**:
   - En Windows:

     ```bash
     .venv\Scripts\activate
     ```

   - En macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

3. **Instalar las dependencias**:

   ```bash
   pip install -e .[dev]
   ```

### Recursos adicionales

- [Guía oficial de Python sobre entornos virtuales](https://docs.python.org/3/library/venv.html)
- [Cómo instalar Python en tu sistema](https://realpython.com/installing-python/)
- [Gestión de múltiples versiones de Python con pyenv](https://realpython.com/intro-to-pyenv/)

### Docker compose

Si se quiere ejecutar un entorno en local ya que no se dispone de una conexión con un servidor kafka.

```bash
docker compose up -d
```
`docker-compose.yml` file for setting up the local environment.

### Variables de entorno

A continuación, se listan todas las variables de entorno utilizadas en el proyecto:

- `KAFKA_HOST`: Dirección del broker de Kafka (por ejemplo, `broker:9093`).
- `RUNNER_INTERVAL_SECONDS`: Intervalo (en segundos) en el que el runner envía logs.
- `KAFKA_NODE_ID`: ID del nodo Kafka.
- `KAFKA_LISTENERS`: Lista de listeners configurados para Kafka.
- `KAFKA_ADVERTISED_LISTENERS`: Lista de listeners anunciados para Kafka.
- `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP`: Mapa de protocolos de seguridad para los listeners.
- `KAFKA_PROCESS_ROLES`: Roles del proceso Kafka (por ejemplo, `broker,controller`).
- `KAFKA_CONTROLLER_QUORUM_VOTERS`: Configuración de quorum para el controlador.
- `KAFKA_CONTROLLER_LISTENER_NAMES`: Nombres de los listeners del controlador.
- `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`: Factor de replicación para el topic de offsets.
- `KAFKA_INTER_BROKER_LISTENER_NAME`: Listener utilizado para la comunicación entre brokers.
- `DYNAMIC_CONFIG_ENABLED`: Habilita la configuración dinámica en Kafka UI.
- `KAFKA_CLUSTERS_0_NAME`: Nombre del cluster Kafka en Kafka UI.
- `KAFKA_CLUSTERS_0_BOOTSTRAP_SERVERS`: Dirección del bootstrap server para Kafka UI.

## Consumir el servicio en otros proyectos

Para consumir el servicio en otros proyectos, simplemente

```yaml
# Docker compose
services:  
  log-producer:
    image: ghcr.io/deathlockers/tlsender
    depends_on:
      - broker
    environment:
      - KAFKA_HOST=broker:9093
      - RUNNER_INTERVAL_SECONDS=15
    volumes:
    - ./src/data:/data
```

The `log-producer` service generates and sends logs to the Kafka broker.

```yaml
# Full sample
services:
  # Kafka broker
  broker:
    image: apache/kafka-native
    container_name: kafka
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 700M
          cpus: '0.8'
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENERS: "CONTROLLER://localhost:9091,HOST://0.0.0.0:9092,DOCKER://0.0.0.0:9093"
      KAFKA_ADVERTISED_LISTENERS: "HOST://localhost:9092,DOCKER://broker:9093"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,DOCKER:PLAINTEXT,HOST:PLAINTEXT"
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@localhost:9091"
      KAFKA_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      # required for single node cluster
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      # broker to broker listener
      KAFKA_INTER_BROKER_LISTENER_NAME: DOCKER
    ports: 
    - "9092:9092"
    
  # UI para ver administrar kafka
  kafka-ui:
    image: ghcr.io/kafbat/kafka-ui:latest
    container_name: kafka-ui
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 300M
          cpus: '0.5'
    depends_on: 
    - broker
    environment:
      DYNAMIC_CONFIG_ENABLED: "true"
      KAFKA_CLUSTERS_0_NAME: "aws-kafka"
      KAFKA_CLUSTERS_0_BOOTSTRAP_SERVERS: "broker:9093"
    ports: 
    - "8080:8080"

  # Crea topics nuevos al iniciar el contenedor
  kafka-init-topics:
    image: confluentinc/cp-kafka:7.2.1
    depends_on:
      - broker
    command: "bash -c 'echo Waiting for Kafka to be ready... && \
               cub kafka-ready -b broker:9093 1 30 && \
               kafka-topics --create --topic customer_logs --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server broker:9093 && \
               kafka-topics --create --topic alert_logs --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server broker:9093'"

  log-producer:
    image: ghcr.io/deathlockers/tlsender
    depends_on:
      - broker
    environment:
      - KAFKA_HOST=broker:9093
      - RUNNER_INTERVAL_SECONDS=15
    volumes:
    - ./src/data:/data
networks:
  default:
    name: kafka_network
