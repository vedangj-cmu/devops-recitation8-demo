#!/bin/bash

URL="http://monitoring-demo-vedang.eastus.azurecontainer.io:8000"
DURATION=180 # 3 minutes in seconds
START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))

echo "Starting traffic generation..."
echo "Target: $URL"
echo "Duration: 3 minutes"

while [ $(date +%s) -lt $END_TIME ]; do
  echo "------------------------------------------------"
  echo "[$(date '+%H:%M:%S')] Sending requests..."
  
  echo -n "GET /health: "
  curl -s "$URL/health"
  echo ""

  echo -n "GET /slow:   "
  curl -s "$URL/slow"
  echo ""

  echo -n "GET /error:  "
  curl -s "$URL/error"
  echo ""

  sleep 1
done

echo "Test completed."