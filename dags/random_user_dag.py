from datetime import datetime, timedelta
import requests
import json
import pandas as pd
import time
from kafka import KafkaProducer
from json import dumps

from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'random_user_data_processor',
    default_args=default_args,
    description='A DAG to fetch and stream Random User API data to Kafka',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'random_users'

def fetch_and_format_user_data(**kwargs):
    """
    Fetch data from Random User API and format it into a clean structure
    """
    # Number of users to fetch
    num_users = 20
    
    # Make API request
    response = requests.get(f'https://randomuser.me/api/?results={num_users}')
    
    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()
        users = data['results']
        
        # Create a structured format for the users
        formatted_users = []
        for user in users:
            formatted_user = {
                'id': user['login']['uuid'],
                'name': f"{user['name']['first']} {user['name']['last']}",
                'gender': user['gender'],
                'email': user['email'],
                'username': user['login']['username'],
                'age': user['dob']['age'],
                'phone': user['phone'],
                'country': user['location']['country'],
                'city': user['location']['city'],
                'picture': user['picture']['large'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            formatted_users.append(formatted_user)
        
        # Convert to DataFrame for better visualization
        users_df = pd.DataFrame(formatted_users)
        
        # Print formatted data
        print("Fetched and formatted user data:")
        print(users_df.to_string())
        
        # Return formatted users for the next task
        return formatted_users
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def send_to_kafka(**kwargs):
    """
    Send the formatted user data to Kafka
    """
    # Get the data from the previous task
    ti = kwargs['ti']
    formatted_users = ti.xcom_pull(task_ids='fetch_and_format_user_data')
    
    if not formatted_users:
        raise Exception("No data received from previous task")
    
    # Initialize Kafka producer with retry mechanism
    max_retries = 5
    retry_delay = 5  # seconds
    
    for retry in range(max_retries):
        try:
            # Configure producer with JSON serialization
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                value_serializer=lambda x: dumps(x).encode('utf-8')
            )
            
            print(f"Successfully connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            break
        except Exception as e:
            if retry < max_retries - 1:
                print(f"Failed to connect to Kafka (attempt {retry+1}/{max_retries}): {str(e)}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to connect to Kafka after {max_retries} attempts: {str(e)}")
    
    # Send each user as a separate message
    for i, user in enumerate(formatted_users):
        try:
            # Send to Kafka topic
            future = producer.send(KAFKA_TOPIC, value=user)
            # Wait for the message to be delivered
            record_metadata = future.get(timeout=10)
            
            print(f"Sent user {i+1}/{len(formatted_users)} to Kafka topic {KAFKA_TOPIC}")
            print(f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
            
        except Exception as e:
            print(f"Error sending user {user['id']} to Kafka: {str(e)}")
    
    # Flush and close the producer
    producer.flush()
    producer.close()
    
    print(f"Successfully sent {len(formatted_users)} users to Kafka topic {KAFKA_TOPIC}")
    
    return len(formatted_users)

# Define the task to fetch and format user data
fetch_user_task = PythonOperator(
    task_id='fetch_and_format_user_data',
    python_callable=fetch_and_format_user_data,
    provide_context=True,
    dag=dag,
)

# Define the task to send data to Kafka
kafka_task = PythonOperator(
    task_id='send_to_kafka',
    python_callable=send_to_kafka,
    provide_context=True,
    dag=dag,
)

# Set up task dependencies
fetch_user_task >> kafka_task 