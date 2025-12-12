# Continuous Monitoring Demo

This repository contains a demonstration of continuous monitoring using FastAPI, Azure Application Insights, Docker, GitHub Actions, and Terraform.

## Application Overview

The FastAPI application (`app/main.py`) exposes three endpoints to demonstrate different monitoring scenarios:
- `GET /health`: Returns 200 OK (Availability check).
- `GET /slow`: Random delay 100ms-3000ms (Performance monitoring).
- `GET /error`: Fails 30% of the time with 500 Error (Failure tracking).

The app is instrumented with **Azure Monitor OpenTelemetry** to automatically collect requests, exceptions, and performance metrics.

## Setup & Deployment

1.  **CI/CD**: The GitHub Actions workflow automatically builds the Docker image and pushes it to DockerHub (`vedangj044/monitoring-demo:latest`) on every push to the `main` branch.
2.  **Infrastructure**:
    - Navigate to the `terraform/` directory.
    - Run `terraform init`.
    - Run `terraform apply` to create the Resource Group, Application Insights, and **Azure Kubernetes Service (AKS)** cluster.
    - The output will provide the `aks_app_url`.

## Verification & Insights

Once deployed and running, you can verify the continuous monitoring layout in the Azure Portal:

### 1. Generating Traffic
Use `curl` or a browser to hit the endpoints repeatedly to generate data:
```bash
# Get the URL from terraform output or Azure Portal (e.g., Load Balancer IP)
URL="http://<your-aks-loadbalancer-ip>"

# Run a loop to generate traffic
while true; do
  curl -I $URL/health
  curl -I $URL/slow
  curl -I $URL/error
  sleep 1
done
```

### 2. Viewing Insights in Azure Portal
Go to your **Application Insights** resource in the Azure Portal:

- **Live Metrics**:
    - Click on "Live metrics" in the left sidebar.
    - You should see incoming requests, failure rates, and duration graphs moving in real-time as you hit the endpoints.

- **Failures**:
    - Click on "Failures".
    - You will see the 500 errors from the `/error` endpoint.
    - Click on a specific failure count to drill down into the stack trace / Live Trace.

- **Performance**:
    - Click on "Performance".
    - Check the `/slow` endpoint to see the distribution of response times (100ms vs 3000ms).

- **Application Map**:
    - Shows the components and their dependencies. You should see your AKS deployment making calls (if any external dependencies existed, they would show here).
