from fastapi import FastAPI, HTTPException
import time
import random
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor
# The connection string will be automatically read from the APPLICATIONINSIGHTS_CONNECTION_STRING environment variable
try:
    configure_azure_monitor()
except Exception as e:
    print(f"Failed to configure Azure Monitor: {e}")

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/slow")
async def slow_endpoint():
    # Random delay between 100ms and 3000ms
    delay = random.randint(100, 3000) / 1000.0
    time.sleep(delay)
    return {"message": "Sorry for the delay", "delay_seconds": delay}

@app.get("/error")
async def error_endpoint():
    # Fails 30% of the time
    if random.random() < 0.3:
        raise HTTPException(status_code=500, detail="Random failure occurred")
    return {"message": "Success!"}
