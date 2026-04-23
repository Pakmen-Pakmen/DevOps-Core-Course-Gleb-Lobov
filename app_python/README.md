# DevOps Info Service

## Overview
A Python Flask service that provides system/runtime information and a persistent visits counter.

## Prerequisites
- Python 3.11+
- pip

## Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
python app.py
```

Endpoints:

- `GET /` - service and system info, increments visits counter
- `GET /visits` - returns current visits count
- `GET /health` - health endpoint
- `GET /ready` - readiness endpoint
- `GET /metrics` - Prometheus metrics

## Docker

### Building the Image
```bash
docker build -t <your-tag> .
```

### Run container
```bash
docker run -p 5000:5000 <your-tag>
```
### Run from Docker Hub
```bash
docker pull <your-dockerhub-username>/devops-info-service:latest
docker run -p 5000:5000 <your-dockerhub-username>/devops-info-service:latest
```

## Docker Compose (Persistent Visits File)

From `app_python/`:

```bash
docker compose up -d --build
curl -s http://127.0.0.1:5000/
curl -s http://127.0.0.1:5000/visits
cat ./data/visits
docker compose restart app
curl -s http://127.0.0.1:5000/visits
```

`docker-compose.yml` mounts `./data` into `/data` and the app stores visits in `/data/visits` (`VISITS_FILE` env var).

![CI](https://github.com/Pakmen-Pakmen/DevOps-Core-Course-Gleb-Lobov/actions/workflows/python-ci.yml/badge.svg)
