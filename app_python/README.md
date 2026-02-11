# DevOps Info Service

## Overview
A simple Python web service that provides system, runtime, and request information.
Built as a foundation for DevOps labs covering Docker, CI/CD, monitoring, and Kubernetes.

## Prerequisites
- Python 3.11+
- pip

## Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
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
![CI](https://github.com/Pakmen-Pakmen/DevOps-Core-Course-Gleb-Lobov/actions/workflows/python-ci.yml/badge.svg)
