#!/bin/bash

# ElastAlert Lab Setup Script
# This script automates the setup of the ElastAlert testing environment

set -e

echo "🚀 Starting ElastAlert Lab Setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "❌ docker compose is not available. Please install Docker Compose and try again."
    exit 1
fi

echo "📦 Starting services with Docker Compose..."
docker compose up -d

echo "⏳ Waiting for Elasticsearch to be ready..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        health=$(curl -s http://localhost:9200/_cluster/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        if [ "$health" = "green" ] || [ "$health" = "yellow" ]; then
            echo "✅ Elasticsearch is ready (status: $health)"
            break
        fi
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for Elasticsearch... ($attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Elasticsearch failed to start within the expected time"
    echo "Check logs with: docker compose logs elasticsearch"
    exit 1
fi

echo "⏳ Waiting for Kibana to be ready..."
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:5601 > /dev/null 2>&1; then
        echo "✅ Kibana is ready"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for Kibana... ($attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Kibana failed to start within the expected time"
    echo "Check logs with: docker compose logs kibana"
    exit 1
fi

echo "⏳ Waiting for ElastAlert to be ready..."
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker compose logs elastalert | grep -q "Starting up"; then
        echo "✅ ElastAlert is ready"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for ElastAlert... ($attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  ElastAlert may still be starting up"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Run data population script
echo "📊 Populating Elasticsearch with sample data..."
python3 populate_data.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Services:"
echo "  • Elasticsearch: http://localhost:9200"
echo "  • Kibana: http://localhost:5601"
echo "  • ElastAlert: Running in background"
echo ""
echo "📊 Monitor ElastAlert:"
echo "  docker compose logs -f elastalert"
echo ""
echo "🧹 To stop all services:"
echo "  docker compose down"
echo ""
echo "🗑️  To stop and remove all data:"
echo "  docker compose down -v" 