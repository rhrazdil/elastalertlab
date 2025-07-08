# ElastAlert Lab

This project sets up a complete ElastAlert testing environment with Elasticsearch 6.8, Kibana, and ElastAlert using Docker Compose. It includes a data population script that creates sample log data to trigger ElastAlert rules.

## Components

- **Elasticsearch 6.8.23**: Single-node Elasticsearch cluster
- **Kibana 6.8.23**: Web interface for Elasticsearch
- **ElastAlert 0.2.4**: Alerting tool for Elasticsearch
- **Data Population Script**: Python script to create sample log data

## Prerequisites

- Docker and Docker Compose
- Python 3.6+ (for the data population script)
- At least 4GB of available RAM

## Quick Start

1. **Start the services:**
   ```bash
   docker compose up -d
   ```

2. **Wait for services to be ready:**
   - Elasticsearch: http://localhost:9200
   - Kibana: http://localhost:5601
   - ElastAlert: Runs in background, logs to console

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Populate Elasticsearch with sample data:**
   ```bash
   python populate_data.py
   ```

5. **Monitor ElastAlert:**
   ```bash
   docker compose logs -f elastalert
   ```

## Services

### Elasticsearch
- **URL**: http://localhost:9200
- **Health Check**: http://localhost:9200/_cluster/health
- **Data**: Stored in Docker volume `elasticsearch_data`

### Kibana
- **URL**: http://localhost:5601
- **Features**: 
  - Index management
  - Data visualization
  - Discover interface for log exploration

### ElastAlert
- **Configuration**: `elastalert_config/config.yaml`
- **Rules**: `elastalert_rules/`
- **Logs**: Available via `docker compose logs elastalert`

## ElastAlert Rules

### Example Frequency Rule
Located in `elastalert_rules/example_frequency_rule.yaml`:

- **Trigger**: More than 5 error events in a 5-minute window
- **Filter**: Only error level logs
- **Alert**: Debug output (logs to console)
- **Realert**: 5 minutes

## Data Population Script

The `populate_data.py` script creates realistic log data with the following characteristics:

- **Index**: `logs-2024.01.01`
- **Log Levels**: info, warning, error
- **Fields**: timestamp, level, message, service, user_id, ip_address, response_time, status_code
- **Error Concentration**: Creates more error logs in a specific time window to trigger the frequency rule

### Running the Script

```bash
python populate_data.py
```

The script will:
1. Wait for Elasticsearch to be ready
2. Create the index with proper mapping
3. Populate 200 log entries over the last hour
4. Create a concentration of error logs in a 5-minute window
5. Verify the data was inserted correctly

## Monitoring and Testing

### Check ElastAlert Status
```bash
# View ElastAlert logs
docker compose logs elastalert

# Follow logs in real-time
docker compose logs -f elastalert
```

### Check Elasticsearch Data
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health

# Count documents in the logs index
curl http://localhost:9200/logs-*/_count

# Search for error logs
curl -X GET "localhost:9200/logs-*/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "level": "error"
    }
  },
  "size": 10,
  "sort": [
    {
      "@timestamp": {
        "order": "desc"
      }
    }
  ]
}'
```

### View Data in Kibana
1. Open http://localhost:5601
2. Go to Management → Index Patterns
3. Create index pattern for `logs-*`
4. Go to Discover to view and search logs

## Troubleshooting

### Services Not Starting
- Check available memory (Elasticsearch needs at least 2GB)
- Ensure ports 9200, 5601 are not in use
- Check Docker logs: `docker compose logs`

### ElastAlert Not Triggering
- Verify data exists in Elasticsearch
- Check ElastAlert configuration
- Ensure index pattern matches rule configuration
- Check ElastAlert logs for errors

### Data Population Issues
- Ensure Elasticsearch is running and healthy
- Check Python dependencies are installed
- Verify network connectivity to localhost:9200

## Customization

### Adding New Rules
1. Create new YAML file in `elastalert_rules/`
2. Follow ElastAlert rule format
3. Restart ElastAlert: `docker compose restart elastalert`

### Modifying Data Generation
Edit `populate_data.py` to:
- Change log message templates
- Modify error concentration timing
- Add new log fields
- Adjust data volume

### Configuration Changes
- Edit `elastalert_config/config.yaml` for ElastAlert settings
- Modify `docker-compose.yml` for service configuration
- Update environment variables as needed

## Cleanup

To stop and remove all services:
```bash
docker compose down -v
```

This will remove containers, networks, and volumes.

## License

This project is for educational and testing purposes. 