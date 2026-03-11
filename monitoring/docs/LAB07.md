# Lab 7 – Observability with Loki, Promtail and Grafana

## 1. Objective

The objective of this lab was to deploy a centralized logging system using Grafana Loki and Promtail and visualize logs in Grafana.

## 2. Monitoring Stack

The following services were deployed using Docker Compose:

* **Grafana** – visualization and dashboards
* **Loki** – log aggregation system
* **Promtail** – log collector for Docker containers

The stack was defined in:

```
monitoring/docker-compose.yml
```

## 3. Loki Configuration

Loki was configured with a local filesystem storage backend.

Configuration file:

```
monitoring/loki/config.yml
```

Key features:

* HTTP API on port 3100
* filesystem storage
* TSDB schema

## 4. Promtail Configuration

Promtail collects logs directly from Docker containers:

```
/var/lib/docker/containers/*/*-json.log
```

Configuration file:

```
monitoring/promtail/config.yml
```

Promtail sends logs to Loki using:

```
http://loki:3100/loki/api/v1/push
```

## 5. Grafana Setup

Grafana was exposed on:

```
http://<VM_IP>:3000
```

Default credentials:

```
admin / admin
```

A Loki datasource was added using:

```
http://loki:3100
```

## 6. Log Visualization

Logs from Docker containers were visible in Grafana Explore using the query:

```
{job="docker"}
```

This includes logs from the deployed Python application container.

## 7. Result

The monitoring stack successfully collected and visualized logs from Docker containers using Loki, Promtail, and Grafana.
