#!/usr/bin/env python3
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import time
import sys

def test_connection():
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    
    print("Attempting to connect to ScyllaDB...")
    max_retries = 10
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            cluster = Cluster(['cassandra'], auth_provider=auth_provider, protocol_version=4)
            session = cluster.connect()
            
            # Get cluster information
            rows = session.execute("SELECT cluster_name, release_version FROM system.local")
            for row in rows:
                print(f"Connected to cluster: {row.cluster_name} with version: {row.release_version}")
            
            # List keyspaces
            print("\nAvailable keyspaces:")
            keyspaces = session.execute("SELECT keyspace_name FROM system_schema.keyspaces")
            for keyspace in keyspaces:
                print(f"- {keyspace.keyspace_name}")
            
            # Check if our keyspace exists
            print("\nChecking for our keyspace and table...")
            if 'random_data' in [ks.keyspace_name for ks in keyspaces]:
                print("✅ random_data keyspace exists")
                
                # Check for the users table
                tables = session.execute("SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'random_data'")
                if 'users' in [table.table_name for table in tables]:
                    print("✅ users table exists")
                    
                    # Describe the table
                    print("\nTable structure:")
                    columns = session.execute("SELECT column_name, type FROM system_schema.columns WHERE keyspace_name = 'random_data' AND table_name = 'users'")
                    for column in columns:
                        print(f"- {column.column_name}: {column.type}")
                else:
                    print("❌ users table not found")
            else:
                print("❌ random_data keyspace not found")
            
            print("\n✅ Connection test successful!")
            cluster.shutdown()
            return True
            
        except Exception as e:
            print(f"Connection attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ Max retries reached. Could not connect to ScyllaDB.")
                return False
            
        finally:
            try:
                if 'cluster' in locals():
                    cluster.shutdown()
            except:
                pass

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1) 