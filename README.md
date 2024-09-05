# ETL Pipeline Framework

This project provides a complete ETL (Extract, Transform, Load) pipeline framework. It includes a frontend for configuring and visualizing Kafka topics and pipelines, a backend for managing configurations, and independent workers that listen to Kafka topics for data enrichment and processing.

## Project Structure

### 1. `configuration`
This folder contains the services needed for configuring and managing the pipeline:
- **kafka-workers-visualizer**: A React-based frontend that provides a visual representation of Kafka topics, workers, and their interconnections.
- **service-kafka-pipeline-editor**: A Python-based backend service that allows users to create and manage Kafka pipelines, including the configuration of workers and their connections to Kafka topics.
- **docker-compose.yml**: Docker Compose file to orchestrate the frontend, backend, and MySQL database.

### 2. `workers`
This folder contains examples of workers and a template for creating new workers:
- **worker-template**: A template for creating new Kafka workers. Each worker listens to one or more Kafka topics, processes the data, and then publishes the results to one or more output topics.
- **example-worker**: Example worker implementations that demonstrate how to process data from Kafka topics and enrich or transform it.

## How It Works

### Kafka Workers Visualizer (Frontend)
The **kafka-workers-visualizer** is a React application that provides a visual overview of the workers and their Kafka topic connections. You can view the current configuration of workers and topics, and easily understand the data flow between them.

### Kafka Pipeline Editor (Backend)
The **service-kafka-pipeline-editor** is a Python Flask application that handles the creation, updating, and deletion of Kafka worker pipelines. This service interacts with a MySQL database to persist pipeline configurations and worker states. The backend exposes a REST API that the frontend communicates with to manage the configurations.

### Workers
Workers are Python-based services that:
- Subscribe to one or more Kafka topics.
- Process the incoming data (perform ETL operations).
- Publish the processed data to one or more output Kafka topics.

Each worker is a standalone service and can be created from the **worker-template** provided in the `workers` folder.

## Requirements

To run this project, you need:
- **Docker** and **Docker Compose**
- **Kafka** setup (can be handled externally or through Docker Compose if needed)
- **MySQL** (included in Docker Compose setup)

## Quick Start

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/etl-pipeline-framework.git
    cd etl-pipeline-framework
    ```

2. **Build and run the services**:
    Navigate to the `configuration` directory and run the following command to start the frontend, backend, and MySQL services:
    ```bash
    docker-compose up --build
    ```

3. **Access the Frontend**:
    Once the services are running, access the Kafka Workers Visualizer at `http://localhost:3000`.

4. **Create New Workers**:
    To create a new worker, navigate to the `workers` directory, copy the `worker-template`, and modify `worker.py` based on your needs.

5. **Deploy Workers**:
    After creating a new worker, you can run it as an independent Docker service or include it in the `docker-compose.yml` for orchestration.

## Example Worker

Here's a basic outline of how an example worker might look:

```python
from kafka import KafkaConsumer, KafkaProducer

# Subscribe to Kafka topics
consumer = KafkaConsumer('input-topic', bootstrap_servers='localhost:9092')
producer = KafkaProducer(bootstrap_servers='localhost:9092')

for message in consumer:
    # Perform data processing (ETL)
    processed_data = message.value.upper()  # Example transformation

    # Send processed data to output topic
    producer.send('output-topic', processed_data)
```

## Docker Compose Services

In this ETL pipeline framework, the `docker-compose.yml` defines several key services:

- **Backend Service (`service-kafka-pipeline-editor`)**: This is a Python Flask-based service responsible for managing Kafka pipelines and worker configurations. The backend interacts with a MySQL database to persist configuration data. It's configured using environment variables for database connection details such as the host, port, database name, username, and password. The backend runs in development mode by default and waits for the database to become healthy before starting.

- **Frontend Service (`kafka-workers-visualizer`)**: A React-based frontend service that provides a graphical interface to visualize Kafka topics and workers, as well as configure pipelines. It depends on the backend service to provide the necessary configuration data and interacts with it via REST APIs. The service is configured using a `.env` file for environment variables.

- **MySQL Database**: A MySQL 8.0 database is used to store pipeline configurations, worker details, and any other relevant metadata. The database is secured using a root password, with a separate user account and database for development. The service includes a health check to ensure it is fully operational before the backend service attempts to connect.

Each service runs in Docker containers, and the `docker-compose.yml` file uses the `network_mode: host` option to allow communication between the services without needing to define specific Docker networks.

### Database Configuration
The MySQL database is configured with the following:
- A root user and password for administrative tasks.
- A dedicated user and database for the application (`dev` by default).
- The MySQL service uses `mysql_native_password` authentication to ensure compatibility with various clients.
- The database is bound to all interfaces (`0.0.0.0`) so it can be accessed by the backend on the host network.

The health check ensures that the database is ready before the backend service starts, avoiding issues where the backend fails to connect if the database isn't fully initialized.

### Extending the `docker-compose.yml`
You can extend the `docker-compose.yml` file to include more services, such as new Kafka workers or additional databases, depending on your use case. Workers can be created and managed independently, and once they are connected to the appropriate Kafka topics, they can either be added to the Docker Compose configuration or run as standalone services.
