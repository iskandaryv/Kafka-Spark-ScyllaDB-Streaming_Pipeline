from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import time

def init_scylla():
    print("Initializing ScyllaDB connection...")
    for attempt in range(5):  # 5 retries
        try:
            # Create cluster connection
            auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
            cluster = Cluster(
                contact_points=['scylla'],
                port=9042,
                auth_provider=auth_provider
            )
            
            # Connect to system keyspace first
            session = cluster.connect()
            
            # Create keyspace if not exists
            keyspace_query = """
            CREATE KEYSPACE IF NOT EXISTS spark_streaming
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
            """
            session.execute(keyspace_query)
            
            # Switch to our keyspace
            session.set_keyspace('spark_streaming')
            
            # Create table if not exists
            table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id text PRIMARY KEY,
                name text,
                gender text,
                email text,
                username text,
                age int,
                phone text,
                country text,
                city text,
                picture text,
                timestamp timestamp
            )
            """
            session.execute(table_query)
            
            print("✅ ScyllaDB initialized successfully")
            session.shutdown()
            cluster.shutdown()
            return
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < 4:  # Don't sleep on last attempt
                time.sleep(10)
    
    raise Exception("Failed to initialize ScyllaDB after 5 attempts")

def process_batch(batch_df, batch_id):
    if batch_df.isEmpty():
        print(f"⚠️ Batch {batch_id} is empty")
        return
    
    # Convert value column from binary to string
    json_df = batch_df.selectExpr("CAST(value AS STRING)")
    
    # Parse JSON data
    schema = StructType([
        StructField("id", StringType()),
        StructField("name", StringType()),
        StructField("gender", StringType()),
        StructField("email", StringType()),
        StructField("username", StringType()),
        StructField("age", IntegerType()),
        StructField("phone", StringType()),
        StructField("country", StringType()),
        StructField("city", StringType()),
        StructField("picture", StringType()),
        StructField("timestamp", TimestampType())
    ])
    
    # Parse JSON and select fields
    parsed_df = json_df.select(from_json(col("value"), schema).alias("data")).select("data.*")
    
    print(f"⏳ Processing batch {batch_id} with {parsed_df.count()} records")
    parsed_df.show()
    
    try:
        # Write to ScyllaDB
        parsed_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .option("keyspace", "spark_streaming") \
            .option("table", "users") \
            .save()
        print(f"✅ Successfully wrote batch {batch_id} to ScyllaDB")
    except Exception as e:
        print(f"❌ Error writing batch {batch_id} to ScyllaDB: {str(e)}")

def main():
    # Initialize ScyllaDB first
    init_scylla()
    
    # Create Spark Session
    spark = SparkSession.builder \
        .appName("KafkaToScyllaDB") \
        .config("spark.cassandra.connection.host", "scylla") \
        .config("spark.cassandra.connection.port", "9042") \
        .config("spark.cassandra.auth.username", "cassandra") \
        .config("spark.cassandra.auth.password", "cassandra") \
        .getOrCreate()
    
    # Set log level
    spark.sparkContext.setLogLevel("WARN")
    
    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "random_users") \
        .option("startingOffsets", "earliest") \
        .load()
    
    # Process and write to ScyllaDB
    query = df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("update") \
        .start()
    
    print("🚀 Streaming pipeline started!")
    query.awaitTermination()

if __name__ == "__main__":
    main() 