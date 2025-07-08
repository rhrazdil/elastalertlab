#!/usr/bin/env python3
"""
Script to populate Elasticsearch with sample log data that will trigger ElastAlert rules.
This script creates various types of log entries including errors that will trigger the frequency rule.
"""

import json
import time
from datetime import datetime, timedelta
import requests
from elasticsearch import Elasticsearch
import random

# Elasticsearch connection
ES_HOST = "localhost"
ES_PORT = 9200
INDEX_NAME = "logs-2024.01.01"

def create_index_mapping(es_client):
    """Create the index with proper mapping for log data."""
    # # Delete existing index if it exists
    # try:
    #     es_client.indices.delete(index=INDEX_NAME)
    #     print(f"Deleted existing index: {INDEX_NAME}")
    # except Exception:
    #     pass  # Index doesn't exist, which is fine
    
    mapping = {
        "mappings": {
            "_doc": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "service": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "ip_address": {"type": "ip"},
                    "response_time": {"type": "float"},
                    "status_code": {"type": "integer"}
                }
            }
        }
    }
    
    try:
        es_client.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Created index: {INDEX_NAME}")
    except Exception as e:
        print(f"Error creating index: {e}")

def generate_log_entry(timestamp, level="info", service="web-server"):
    """Generate a sample log entry."""
    messages = {
        "info": [
            "User login successful",
            "Request processed successfully",
            "Database connection established",
            "Cache hit for key: user_profile_123",
            "File uploaded successfully",
            "Email sent to user@example.com",
            "API rate limit check passed",
            "Session created for user",
            "Configuration loaded successfully",
            "Health check passed"
        ],
        "warning": [
            "High memory usage detected",
            "Database connection pool running low",
            "Slow query detected",
            "Cache miss rate increasing",
            "Disk space running low",
            "API response time above threshold",
            "Too many failed login attempts",
            "Rate limit approaching",
            "Backup job running longer than usual",
            "SSL certificate expiring soon"
        ],
        "error": [
            "Database connection failed",
            "Authentication failed for user",
            "File not found: /var/log/app.log",
            "Invalid JSON format in request",
            "Timeout while processing request",
            "Memory allocation failed",
            "Network connection refused",
            "Permission denied for file access",
            "Service unavailable",
            "Internal server error occurred"
        ]
    }
    
    return {
        "@timestamp": timestamp.replace(microsecond=0).isoformat() + "Z",
        "level": level,
        "message": random.choice(messages[level]),
        "service": service,
        "user_id": f"user_{random.randint(1000, 9999)}",
        "ip_address": f"192.168.1.{random.randint(1, 254)}",
        "response_time": random.uniform(0.1, 5.0),
        "status_code": random.choice([200, 201, 400, 401, 403, 404, 500, 502, 503])
    }

def populate_data(es_client, num_entries=6):
    """Populate Elasticsearch with sample log data to trigger ElastAlert."""
    print(f"Populating {num_entries} error log entries within the last minute (UTC)...")
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=1)
    
    bulk_data = []
    for i in range(num_entries):
        # Distribute timestamps evenly within the last minute
        timestamp = start_time + timedelta(seconds=(i * (60 // num_entries)))
        log_entry = generate_log_entry(timestamp, level="error")
        bulk_data.append({"index": {"_index": INDEX_NAME, "_type": "_doc"}})
        bulk_data.append(log_entry)
    
    es_client.bulk(body=bulk_data)
    print(f"Successfully populated {num_entries} error log entries (UTC)")

def wait_for_elasticsearch():
    """Wait for Elasticsearch to be ready."""
    print("Waiting for Elasticsearch to be ready...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(f"http://{ES_HOST}:{ES_PORT}/_cluster/health")
            if response.status_code == 200:
                health = response.json()
                if health["status"] in ["green", "yellow"]:
                    print("Elasticsearch is ready!")
                    return True
        except requests.exceptions.ConnectionError:
            pass
        
        retry_count += 1
        time.sleep(2)
        print(f"Waiting for Elasticsearch... ({retry_count}/{max_retries})")
    
    print("Elasticsearch is not ready after maximum retries")
    return False

def main():
    """Main function to populate data."""
    print("Starting data population script...")
    
    # Wait for Elasticsearch
    if not wait_for_elasticsearch():
        print("Failed to connect to Elasticsearch. Make sure it's running.")
        return
    
    # Connect to Elasticsearch
    try:
        es_client = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
        print("Connected to Elasticsearch")
    except Exception as e:
        print(f"Failed to connect to Elasticsearch: {e}")
        return
    
    # Create index with mapping
    create_index_mapping(es_client)
    
    # Populate data
    populate_data(es_client, num_entries=6)
    
    # Verify data
    try:
        count_response = es_client.count(index=INDEX_NAME)
        if count_response and 'count' in count_response:
            print(f"Total documents in index: {count_response['count']}")
        
        # Show some sample documents
        search_response = es_client.search(
            index=INDEX_NAME,
            body={
                "query": {"match_all": {}},
                "size": 5,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
        )
        
        if search_response and 'hits' in search_response and 'hits' in search_response['hits']:
            print("\nSample documents:")
            for hit in search_response['hits']['hits']:
                if '_source' in hit:
                    print(f"  {hit['_source']['@timestamp']} - {hit['_source']['level']}: {hit['_source']['message']}")
            
    except Exception as e:
        print(f"Error verifying data: {e}")
    
    print("\nData population completed!")
    print("The ElastAlert frequency rule should trigger if there are more than 5 error events in a 5-minute window.")

if __name__ == "__main__":
    main() 