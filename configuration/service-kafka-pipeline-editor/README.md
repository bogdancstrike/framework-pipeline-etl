# ETL Kafka Workers Framework

This project provides a comprehensive framework for creating Kafka consumers (workers) that aggregate messages from multiple Kafka topics, process them, and publish the results to one or more output Kafka topics. It includes a backend configuration API, a React-based frontend for visualizing Kafka workers, and a template for creating new workers with customizable processing logic.

## Table of Contents
- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Kafka Workers](#kafka-workers)
  - [Scope of the Project](#scope-of-the-project)
  - [Project Structure](#project-structure)
  - [Database Configuration](#database-configuration)
  - [Worker Process Function](#worker-process-function)
- [Kafka Workers Visualizer](#kafka-workers-visualizer)
- [Service Kafka Pipeline Editor](#service-kafka-pipeline-editor)
- [Setup and Installation](#setup-and-installation)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Introduction

The project is a framework designed to streamline the development and management of ETL pipelines using Kafka. It includes a React-based frontend for visualizing Kafka topics and workers, a Flask-based backend API for managing configurations, and several Kafka worker templates for message aggregation and processing.

---

## Project Structure

```plaintext
.
├── configuration
│   ├── kafka-workers-visualizer    # React-based frontend to visualize workers and topics
│   ├── service-kafka-pipeline-editor # Flask backend API for managing worker configurations
│   └── docker-compose.yml          # Docker Compose setup for MySQL, backend, and frontend
├── workers
│   ├── worker-generator-rezumat    # Worker for summarizing data
│   ├── worker-language-detector    # Worker for language detection
│   ├── worker-raw-data             # Worker for handling raw data
│   └── worker-template             # Template for creating new workers
└── README.md
```


### Architecture Overview

The architecture of the project is designed for modularity, allowing seamless integration and extensibility of Kafka workers. The system includes the following components:

1. **Kafka Consumer (Worker)**: 
    - Listens to one or more input Kafka topics, aggregating messages based on a common identifier (e.g., `id`).
    - The consumer is designed to be extendable and flexible, allowing you to plug in your custom processing logic.
    
2. **Message Aggregation**: 
    - Messages from multiple topics are aggregated based on a common identifier (e.g., `id`) before processing, ensuring all required data for an event is available.
    
3. **Kafka Producer**: 
    - After processing, the consumer forwards the transformed message to one or more output Kafka topics.
    
4. **Database-Driven Configuration**: 
    - Consumer configurations, such as input/output topics and metadata, are stored in a MySQL database, allowing dynamic reconfiguration without changing code.

5. **Timeout Mechanism**: 
    - Incomplete message aggregations are discarded after a configurable timeout period to avoid stale data being processed.

6. **Frontend Visualization**: 
    - A React-based frontend for visualizing the connections between Kafka workers and topics in a dynamic graph structure.

7. **Backend API**: 
    - A Flask-based API to manage consumer configurations, including creating, updating, and deleting Kafka workers and their associated topics.

---

## Kafka Workers

### Scope of the Project

This part of the framework provides a **boilerplate for Kafka consumers** that process data in an ETL pipeline. The workers can be customized by modifying the `process()` function in `worker.py` to define how messages are processed once aggregated.

### Database Configuration

The workers retrieve their configuration from a MySQL database. Here is an example configuration stored in the database:

| id | consumer_name | topics_input    | topics_output   | kafka_bootstrap_server | metadatas |
|----|---------------|-----------------|-----------------|------------------------|-----------|
| 1  | worker1       | input_topic_1   | output_topic_1  | 172.17.12.80:9092       | <null>    |
| 2  | worker2       | input_topic_2   | output_topic_2  | 172.17.12.80:9092       | <null>    |

- **`consumer_name`**: A unique identifier for the consumer.
- **`topics_input`**: The input Kafka topics for the consumer to listen to (comma-separated).
- **`topics_output`**: The output Kafka topics where processed messages are sent (comma-separated).
- **`kafka_bootstrap_server`**: Kafka broker to connect to.
- **`metadatas`**: Optional metadata for the worker configuration.

### Worker Process Function

In the worker template (`worker.py`), the `process()` function is where custom processing logic is implemented. Here’s an example:

```python
def process(message, consumer_name, metadatas):
    if "text" in message["content"]:
        try:
            # Example API call
            input_request = [{"content": message['content']['text'], "language": "EMPTY"}]
            response = requests.post(API_URL, json=input_request)

            if response.status_code == 200:
                api_result = response.json()

                # Enrich message with the API result
                message["content"]["language"] = api_result[0]['language']
                save_to_elasticsearch(message, consumer_name)
            else:
                logger.error(f"{consumer_name}: API call failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"{consumer_name}: API call failed with exception {e}")

    return message
```


## Kafka Workers Visualizer

### Features

- **Node and Edge Creation**: Dynamically add Kafka workers and topics, and connect them through draggable edges to visualize the flow of data between Kafka topics and workers.
- **Node Editing**: Easily edit the labels of Kafka workers (nodes) and topics, or delete them directly from the user interface.
- **Graph Layout**: Adjust the layout of the graph either horizontally or vertically, depending on your visualization needs. Users can control node separation and spacing with sliders to create a clear view of the topology.
- **Save Configuration**: You can generate and save the configuration of the Kafka pipeline as a JSON structure representing the current state of nodes (workers) and edges (topic relationships).

## Project Structure

The key parts of the visualizer are as follows:

```plaintext
kafka-workers-visualizer/
│
├── src/                     # Main source code for the React application
│   ├── App.js               # Main component of the React application
│   ├── App.test.js          # Test file for App.js
│   ├── index.js             # Entry point for ReactDOM, renders the app
│   ├── network.js           # Manages network requests (likely to interact with the backend)
│   ├── reportWebVitals.js   # Used for measuring and reporting app performance
│   ├── setupTests.js        # Test setup file (used by Jest for testing)
│   ├── logo.svg             # Logo for the app
│   └── index.css            # Global CSS file for the app
│
├── public/                  # Public folder for static assets
│
├── .env                     # Environment variables file (holds API URLs and other config)
├── .gitignore               # Specifies files to ignore in version control
├── Dockerfile               # Dockerfile for containerizing the frontend
├── package.json             # Holds dependencies and scripts for the React app
├── package-lock.json        # Dependency tree lock file for npm/yarn
└── README.md                # Project documentation (this file)
```

## Kafka Workers Visualizer

### Usage

- **Add Worker**: Click the "Add Worker" button to create a new Kafka consumer (worker) node on the canvas.
- **Add Topic**: Click the "Add Topic" button to create a new Kafka topic node on the canvas.
- **Create Connections**: Drag from the small circular handle on a worker node to a topic node (or vice versa) to create a connection between them, representing the flow of messages from one to the other.
- **Edit Labels**: Double-click on the label of any node (either a worker or topic) to edit its name.
- **Delete Nodes or Edges**: To delete a worker, topic, or connection (edge), click the red "×" button that appears when you hover over the element.
- **Adjust Layout**: Use the "Vertical Layout" or "Horizontal Layout" buttons to automatically rearrange the graph in a more readable manner. You can adjust the separation between nodes using the provided sliders to customize the appearance further.
- **Save Configuration**: Click the "Save" button to generate and log the current topology of workers and topics as a JSON object, which can be used to replicate the configuration elsewhere.

### Example JSON Output

```json
{
  "workers": [
    {
      "id": "worker1",
      "name": "Worker 1",
      "input_topics": ["input_topic_1"],
      "output_topics": ["output_topic_1"]
    },
    {
      "id": "worker2",
      "name": "Worker 2",
      "input_topics": ["input_topic_2"],
      "output_topics": ["output_topic_2"]
    }
  ],
  "topics": [
    {
      "id": "input_topic_1",
      "name": "Input Topic 1"
    },
    {
      "id": "output_topic_1",
      "name": "Output Topic 1"
    }
  ]
}
```

This output JSON structure represents the current state of workers (Kafka consumers) and topics in the visualizer and can be used to replicate the same setup in a different environment.


## Service Kafka Pipeline Editor

### Introduction

The **Kafka Pipeline Editor** is a Flask-based API that manages Kafka consumer configurations. This API allows developers and users to create, retrieve, update, and delete Kafka consumer settings dynamically without having to modify the code directly. The configurations are stored in a MySQL database, making it flexible for managing multiple workers and pipelines.

This API is essential for managing the entire ETL pipeline by defining which topics Kafka workers consume from and where the processed messages are sent.

### Features

- **CRUD Operations**: Create, read, update, and delete Kafka consumer configurations.
- **MySQL Integration**: Configurations are stored in a MySQL database, allowing dynamic changes to Kafka workers without modifying the application code.
- **Logging**: The service logs all actions and errors for easier debugging and tracking.
- **CORS Support**: Cross-Origin Resource Sharing (CORS) is enabled, allowing the frontend visualizer to interact seamlessly with the API.

### API Endpoints

1. **GET /api/consumer_configs**  
   Retrieves all Kafka consumer configurations from the database.

   **Example Response:**
   ```json
   [
     {
       "id": 1,
       "consumer_name": "worker1",
       "topics_input": "input_topic_1",
       "topics_output": "output_topic_1",
       "kafka_bootstrap_server": "172.17.12.80:9092"
     },
     {
       "id": 2,
       "consumer_name": "worker2",
       "topics_input": "input_topic_2",
       "topics_output": "output_topic_2",
       "kafka_bootstrap_server": "172.17.12.80:9092"
     }
   ]
```

2. **POST /api/consumer_configs**  
   Creates or updates Kafka consumer configurations. You can provide multiple configurations in a single request.

   **Example Request Body:**
   ```json
   [
     {
       "consumer_name": "worker1",
       "topics_input": "input_topic_1",
       "topics_output": "output_topic_1",
       "kafka_bootstrap_server": "172.17.12.80:9092"
     },
     {
       "consumer_name": "worker2",
       "topics_input": "input_topic_2",
       "topics_output": "output_topic_2",
       "kafka_bootstrap_server": "172.17.12.80:9092"
     }
   ]
```

### Database Schema

The API interacts with a MySQL database that stores Kafka consumer configuration data. The configurations are stored in a table named `consumer_configs`, and each row represents one Kafka worker’s configuration.

| id | consumer_name | topics_input   | topics_output  | kafka_bootstrap_server |
|----|---------------|----------------|----------------|------------------------|
| 1  | worker1       | input_topic_1  | output_topic_1 | 172.17.12.80:9092       |
| 2  | worker2       | input_topic_2  | output_topic_2 | 172.17.12.80:9092       |

- **id**: A unique auto-incremented identifier for each configuration.
- **consumer_name**: The unique name identifying the Kafka consumer.
- **topics_input**: A comma-separated list of input Kafka topics that the worker listens to.
- **topics_output**: A comma-separated list of output Kafka topics where the processed messages are published.
- **kafka_bootstrap_server**: The address of the Kafka broker(s) that the worker connects to.

---

### Logging

The **Kafka Pipeline Editor** API includes comprehensive logging for all actions, errors, and important events. Logging is done both to the console and a log file in the `logs/` directory. The logging level can be configured to capture various levels of granularity (e.g., `DEBUG`, `INFO`, `ERROR`). This allows for easy debugging and monitoring of API activities.

---

### CORS

The API supports **Cross-Origin Resource Sharing (CORS)**, allowing external applications (such as the **Kafka Workers Visualizer**) to make requests to the API without facing cross-origin restrictions. This is enabled by default for all routes but can be restricted to specific origins if needed.

---

## Setup and Installation

### Prerequisites

Before running the project, ensure you have the following software installed:

- **Python 3.7+** (for running the backend API)
- **Node.js & npm/yarn** (for running the frontend React application)
- **Kafka Broker** (can be configured using Docker Compose or run separately)
- **MySQL Database** (for storing Kafka consumer configurations)

### Installation Steps

1. **Clone the Repository**  
   Clone the project repository to your local machine:
   ```bash
   git clone https://github.com/bogdancstrike/framework-pipeline-etl
   cd framework-pipeline-etl
```

### Set Up Backend (Service Kafka Pipeline Editor)

1. **Navigate to the Backend Directory**  
   Move into the backend API directory:
   ```bash
   cd configuration/service-kafka-pipeline-editor
```

2. **Create and Activate a Virtual Environment (optional but recommended)**
It’s recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python Dependencies**
Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

4. **Set Up MySQL Database**
Create a MySQL database to store Kafka consumer configurations. Once the database is set up, create a `config.py` file in the root directory to provide database credentials:

```bash
# config.py
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'your_database_name'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
```

5. **Run Database Migrations**
Use an ORM or direct SQL commands to create the consumer_configs table in the MySQL database. The table structure is outlined in the Database Schema section of this documentation.

6. **Start the Flask Application**
Start the Flask server to serve the API:

```bash
python main.py
```

The Flask server should now be running at http://localhost:5000.

### Set Up Frontend (Kafka Workers Visualizer)

1. **Navigate to the Frontend Directory**  
   Move into the directory that contains the React-based frontend application:

```bash
   cd configuration/kafka-workers-visualizer
```

2. **Install Dependencies**
Use npm or yarn to install all the necessary dependencies for the frontend:

```bash
npm install
```

3. **Start the Development Server**
Start the React development server by running:

```bash
npm start
```

This will launch the application, and you can access it at http://localhost:3000. The React application provides a visual interface where you can manage and visualize Kafka consumers (workers) and Kafka topics, and create connections between them.

4. **Environment Configuration**
If you need to configure environment-specific variables for the frontend, you can create a .env file in the root of the kafka-workers-visualizer directory. Example:

```bash
REACT_APP_API_URL=http://localhost:5000/api
```

This environment variable allows the frontend to connect to the backend API, where the Kafka worker configurations are managed.

### Docker Compose Setup (Optional)

If you'd prefer to use Docker Compose to manage all services (frontend, backend, MySQL, and Kafka), follow these steps:

1. **Navigate to the Configuration Directory**  
   Ensure you are in the directory where the `docker-compose.yml` file is located:

```bash
   cd configuration
```

2. **Run Docker Compose**
Run the following command to start all the services:

```bash
docker-compose up
```

This command will build and run all the services defined in the `docker-compose.yml` file, including:

- **MySQL**:  
  - Running on port `3306`, MySQL is used to store Kafka worker configurations in the `consumer_configs` table. The database persists all consumer-related data, allowing for dynamic reconfiguration of Kafka workers without code changes.

- **Kafka Broker**:  
  - Running on port `9092`, this service manages the message brokering, enabling Kafka consumers (workers) to subscribe to input topics and publish results to output topics. Kafka allows asynchronous message passing and ensures reliability and fault tolerance in data processing pipelines.

- **Backend (Flask API - Kafka Pipeline Editor)**:  
  - Running on port `5000`, this Flask-based backend API handles Kafka worker configuration through various API endpoints. The API allows for creating, updating, retrieving, and deleting consumer configurations stored in the MySQL database. It also provides CRUD operations to dynamically change Kafka consumer settings without altering the source code.

- **Frontend (React Application - Kafka Workers Visualizer)**:  
  - Running on port `3000`, the frontend provides a visual interface for managing Kafka consumers (workers) and topics. Using this UI, users can add, modify, and delete Kafka workers and their associated topics, as well as view and edit the connections between them.

---

### Verify Services

Once all services are running, you can access the following:

- **Frontend (Kafka Workers Visualizer)**:  
  Access the visualizer at `http://localhost:3000`. Here, you can interact with the Kafka topics and workers, adding new ones or modifying existing configurations in the system.

- **Backend API (Kafka Pipeline Editor)**:  
  The API is available at `http://localhost:5000`. You can use this API to programmatically manage Kafka consumer configurations (CRUD operations). API documentation can be added for better integration with the frontend and other services.

### Shut Down Services

To stop all running services and clean up resources, use the following command:
```bash
docker-compose down
```

This command will gracefully stop and remove all containers associated with the project, ensuring no unnecessary resources are consumed after shutting down the pipeline.

## Future Enhancements

1. **Support for More Databases**:  
   Extend the backend to support additional databases like PostgreSQL, SQLite, or NoSQL databases such as MongoDB. This would increase flexibility for different deployment environments and allow teams to use the database technology that best suits their needs.

2. **Monitoring and Metrics**:  
   Integrate monitoring tools such as Prometheus and Grafana to track the performance of Kafka consumers, including message processing rates, consumer lag, errors, and system health. These metrics would provide better visibility into the system’s operations and allow for proactive performance management.

3. **Advanced Error Handling**:  
   Implement more sophisticated error handling mechanisms, such as:
   - **Retry logic**: Automatically retry failed message processing attempts a configurable number of times.
   - **Dead-letter queues (DLQs)**: Set up Kafka dead-letter topics where unprocessable messages are sent for manual review or reprocessing.
   - **Alerting**: Integrate with systems like Slack, email, or PagerDuty to notify the team immediately when critical failures occur in message processing.

4. **Worker Deployment and Scaling**:  
   Use container orchestration systems like Kubernetes or Docker Swarm to enable automatic scaling and high availability of Kafka consumers. This would allow for horizontal scaling of consumers based on the incoming message load, ensuring that the system can handle peak loads without manual intervention.

5. **UI Enhancements**:  
   Improve the Kafka Workers Visualizer by adding:
   - **Real-time Kafka metrics**: Display real-time Kafka consumer and topic metrics directly in the visualizer UI.
   - **Worker health status**: Show whether each Kafka worker is healthy, processing messages correctly, and maintaining connectivity with Kafka brokers.
   - **Dynamic reconfiguration**: Allow users to modify worker configurations, such as changing input/output topics or Kafka settings, directly from the visualizer interface, with changes automatically reflected in the backend without requiring a restart.

6. **Security and Authentication**:  
   Add user authentication and authorization to the system to restrict access to the API and frontend. Implement OAuth2 or JWT-based authentication to ensure only authorized users can modify Kafka worker configurations.

7. **Improved Logging and Tracing**:  
   Enhance logging capabilities to include distributed tracing, which would allow tracking message flow across multiple Kafka workers and topics. Tools like Zipkin or Jaeger can be integrated for better debugging and monitoring of end-to-end message processing.

8. **Pluggable Processing Logic**:  
   Allow users to define pluggable or modular processing logic that can be swapped in or out at runtime. This would enable flexible data transformation or enrichment strategies, allowing users to plug in custom code for message processing without changing the core application.

This section outlines potential future enhancements to the project, focusing on scalability, security, error handling, and user interface improvements. It also suggests adding monitoring and metrics for better system observability. Let me know if you'd like to expand on any of these ideas or need further modifications!

---

## License

This project is licensed under the MIT License.