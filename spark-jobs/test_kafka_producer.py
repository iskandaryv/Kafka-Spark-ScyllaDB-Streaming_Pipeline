from kafka import KafkaProducer
from json import dumps
import time
import uuid
import random
from datetime import datetime

# Configure Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

# Names, countries and cities for test data
first_names = ["John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Ava", "Alexander", "Isabella"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
countries = ["USA", "Canada", "UK", "Australia", "Germany", "France", "Japan", "Brazil", "India", "Italy"]
cities = {
    "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Ottawa"],
    "UK": ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
    "Germany": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
    "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Sapporo"],
    "Brazil": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo"]
}

def generate_random_user():
    """Generate a random user for testing"""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    country = random.choice(countries)
    city = random.choice(cities[country])
    
    return {
        "id": str(uuid.uuid4()),
        "name": f"{first_name} {last_name}",
        "gender": random.choice(["male", "female"]),
        "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
        "username": f"{first_name.lower()}{random.randint(1, 999)}",
        "age": random.randint(18, 80),
        "phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "country": country,
        "city": city,
        "picture": f"https://randomuser.me/api/portraits/{'men' if random.random() > 0.5 else 'women'}/{random.randint(1, 99)}.jpg",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Send test data to Kafka
def send_test_data(num_records=100, delay=0.5):
    """Send test data to Kafka topic"""
    for i in range(num_records):
        user = generate_random_user()
        producer.send('random_users', value=user)
        print(f"Sent record {i+1}/{num_records}: {user['name']} from {user['city']}, {user['country']}")
        time.sleep(delay)
    
    producer.flush()
    print(f"Successfully sent {num_records} records to Kafka topic 'random_users'")

if __name__ == "__main__":
    # Wait a bit for Kafka to be ready
    print("Waiting for Kafka to be ready...")
    time.sleep(10)
    
    # Send test data
    send_test_data(num_records=50, delay=1) 