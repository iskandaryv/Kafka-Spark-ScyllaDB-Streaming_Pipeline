# Data Streaming Pipeline with Airflow, Kafka, Spark, and ScyllaDB

![GitHub](https://img.shields.io/github/license/iskandaryv/streaming-pipeline)
![Docker Pulls](https://img.shields.io/docker/pulls/iskandaryv/streaming-pipeline)

A complete end-to-end data streaming pipeline built with Apache Airflow, Apache Kafka, Apache Spark, and ScyllaDB. This project demonstrates how to build a scalable and distributed data processing system using containerized services.

## 🚀 Architecture

The pipeline follows this workflow:
1. Apache Airflow fetches data from Random User API
2. Data is published to Kafka topics
3. Spark Streaming consumes the Kafka topics
4. Processed data is stored in ScyllaDB
5. The entire workflow is containerized using Docker

![Architecture Diagram](https://your-repo-url/architecture-diagram.png)

## ✨ Features

- **Orchestration**: Scheduled and monitored data pipelines with Airflow
- **Stream Processing**: Real-time data processing with Spark Streaming
- **Messaging**: Reliable data streaming with Kafka
- **Storage**: Fast, scalable NoSQL database with ScyllaDB
- **Containerization**: Easy deployment with Docker and Docker Compose
- **Monitoring**: Kafka Control Center for monitoring streams

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- At least 8GB of RAM allocated to Docker

## 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/iskandaryv/streaming-pipeline.git
cd streaming-pipeline
```

2. Start all services using Docker Compose:

```bash
docker-compose up -d
```

3. Check that all services are running:

```bash
docker-compose ps
```

## 🖥️ Web Interfaces

Once all services are up and running, you can access:

- **Airflow**: [http://localhost:8080](http://localhost:8080) (user: admin, password: admin)
- **Spark Master UI**: [http://localhost:8090](http://localhost:8090)
- **Kafka Control Center**: [http://localhost:9021](http://localhost:9021)

## 📊 Using the Pipeline

### Starting the Data Pipeline

1. Open the Airflow web interface
2. Navigate to the DAGs page
3. Activate the `random_user_data_processor` DAG
4. Trigger a DAG run or wait for the scheduler to run it

### Viewing the Results

To verify that data is flowing through the pipeline:

1. Check Kafka Control Center to see messages on the `random_users` topic
2. Connect to ScyllaDB and query the database:

```bash
docker-compose exec scylla cqlsh -u cassandra -p cassandra

# In the CQL shell
USE spark_streaming;
SELECT * FROM users LIMIT 10;
```

### Manual Testing

To test components individually:

**Generate test data for Kafka:**
```bash
docker-compose exec spark-master bash -c "cd /opt/spark-jobs && python test_kafka_producer.py"
```

**Test ScyllaDB connection:**
```bash
docker-compose exec spark-master bash -c "cd /opt/spark-jobs && python test_scylla_connection.py"
```

## �� Project Structure
├── dags/ # Airflow DAG definitions
│ └── random_user_dag.py # DAG for random user data processing
├── spark-jobs/ # Spark application code
│ ├── kafka_to_cassandra.py # Spark streaming job
│ ├── test_kafka_producer.py# Test script for Kafka
│ └── test_scylla_connection.py # Test script for ScyllaDB
├── scripts/ # Helper scripts
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt # Python dependencies for Airflow
├── requirements_spark.txt # Python dependencies for Spark
├── spark-defaults.conf # Spark configuration
└── README.md # Project documentation

