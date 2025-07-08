#!/usr/bin/env python3
"""
Test script to generate additional error logs to trigger the ElastAlert frequency rule.
This script creates a burst of error logs in a short time window.
"""

import json
import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import random

# Elasticsearch connection
ES_HOST = "localhost"
ES_PORT = 9200
INDEX_NAME = "logs-2024.01.01"

def generate_error_burst(es_client, num_errors=10, burst_duration=60):
    """Generate a burst of error logs to trigger the frequency rule."""
    print(f"Generating {num_errors} error logs over {burst_duration} seconds...")
    
    error_messages = [
        "Database connection timeout",
        "Authentication service unavailable",
        "Memory allocation failed",
        "Network connection refused",
        "File system read error",
        "Service discovery failed",
        "Load balancer health check failed",
        "Cache corruption detected",
        "SSL handshake failed",
        "API rate limit exceeded"
    ]
    
    bulk_data = []
    start_time = datetime.now()
    
    for i in range(num_errors):
        # Distribute errors over the burst duration
        timestamp = start_time + timedelta(
            seconds=random.randint(0, burst_duration)
        )
        
        log_entry = {
            "@timestamp": timestamp.isoformat(),
            "level": "error",
            "message": random.choice(error_messages),
            "service": "web-server",
            "user_id": f"user_{random.randint(1000, 9999)}",
            "ip_address": f"192.168.1.{random.randint(1, 254)}",
            "response_time": random.uniform(0.1, 5.0),
            "status_code": random.choice([500, 502, 503, 504])
        }
        
        bulk_data.append({"index": {"_index": INDEX_NAME}})
        bulk_data.append(log_entry)
    
    # Insert all error logs
    if bulk_data:
        es_client.bulk(body=bulk_data)
        print(f"✅ Inserted {num_errors} error logs")
    
    return start_time

def check_elasticsearch_health():
    """Check if Elasticsearch is healthy."""
    try:
        es_client = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
        health = es_client.cluster.health()
        return es_client, health['status'] in ['green', 'yellow']
    except Exception as e:
        print(f"❌ Failed to connect to Elasticsearch: {e}")
        return None, False

def main():
    """Main function to test the ElastAlert rule."""
    print("🧪 Testing ElastAlert Frequency Rule")
    print("=" * 40)
    
    # Check Elasticsearch health
    es_client, is_healthy = check_elasticsearch_health()
    if not is_healthy:
        print("❌ Elasticsearch is not healthy. Please ensure it's running.")
        return
    
    print("✅ Elasticsearch is healthy")
    
    # Generate error burst
    start_time = generate_error_burst(es_client, num_errors=15, burst_duration=120)
    
    print(f"\n📊 Error burst generated starting at {start_time.strftime('%H:%M:%S')}")
    print("⏳ The ElastAlert frequency rule should trigger within the next few minutes...")
    print("\n📋 Monitor ElastAlert logs:")
    print("  docker-compose logs -f elastalert")
    print("\n📊 Check error logs in Elasticsearch:")
    print("  curl -X GET 'localhost:9200/logs-*/_search' -H 'Content-Type: application/json' -d '{\"query\":{\"term\":{\"level\":\"error\"}},\"size\":10,\"sort\":[{\"@timestamp\":{\"order\":\"desc\"}}]}'")
    
    # Wait a bit and show current error count
    print("\n⏳ Waiting 30 seconds to check error count...")
    time.sleep(30)
    
    try:
        if es_client:
            count_response = es_client.count(
                index=INDEX_NAME,
                body={"query": {"term": {"level": "error"}}}
            )
            error_count = count_response['count']
            print(f"📊 Current error count: {error_count}")
            
            if error_count >= 5:
                print("✅ Sufficient error logs to trigger the frequency rule!")
            else:
                print("⚠️  May need more error logs to trigger the rule")
        else:
            print("❌ No Elasticsearch client available")
            
    except Exception as e:
        print(f"❌ Error checking count: {e}")

if __name__ == "__main__":
    main() 