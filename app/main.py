from fastapi import FastAPI, HTTPException
import asyncio
import os
import random
import logging

# OpenTelemetry Imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

# Azure Monitor Exporters
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorTraceExporter,
    AzureMonitorMetricExporter,
    AzureMonitorLogExporter,
)

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

def setup_otel():
    """
    Configures OpenTelemetry to export Traces, Metrics, and Logs to Azure Application Insights.
    """
    conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not conn_str:
        logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING is not set; telemetry will not export.")
        return

    # 1. Define the Resource
    resource = Resource.create({
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "fastapi-otel-app"),
    })

    # 2. Configure Tracing
    tracer_provider = TracerProvider(resource=resource)

    # Add a span processor to export spans to Azure Monitor
    # A span is the line you see in on tracing tools
    # BatchSpanProcessor groups spans into batches before exporting them to Azure Monitor
    tracer_provider.add_span_processor(
        BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=conn_str))
    )
    trace.set_tracer_provider(tracer_provider)

    # 3. Configure Metrics
    metric_reader = PeriodicExportingMetricReader(
        AzureMonitorMetricExporter(connection_string=conn_str),
        export_interval_millis=60000,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # 4. Configure Logs
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(AzureMonitorLogExporter(connection_string=conn_str))
    )
    
    # Redirect standard Python logging to OpenTelemetry
    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(otel_handler)

try:
    setup_otel()
except Exception as e:
    print(f"Failed to configure OpenTelemetry: {e}")

app = FastAPI()

# Instrument FastAPI to automatically generate spans for processing requests
FastAPIInstrumentor.instrument_app(app)

# Add ASGI Middleware for better trace context propagation
app.add_middleware(OpenTelemetryMiddleware)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/slow")
async def slow_endpoint():
    delay = random.randint(100, 3000) / 1000.0
    await asyncio.sleep(delay)
    return {"message": "Sorry for the delay", "delay_seconds": delay}

@app.get("/error")
async def error_endpoint():
    if random.random() < 0.3:
        raise HTTPException(status_code=500, detail="Random failure occurred")
    return {"message": "Success!"}
