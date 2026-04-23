# Lab 16 - Kubernetes Monitoring and Init Containers

## 1. Stack Components

### Prometheus Operator

Reconciles monitoring CRDs and manages Prometheus/Alertmanager lifecycle (config, StatefulSets, secrets, rules).

### Prometheus

Scrapes cluster and application metrics, stores time series, and provides query API (PromQL).

### Alertmanager

Receives alerts from Prometheus, groups/silences/routes notifications, and exposes active alerts API/UI.

### Grafana

Visualization layer for Prometheus metrics using dashboards and panels.

### kube-state-metrics

Exports Kubernetes object state metrics (pods, deployments, PVCs, etc.) from the API server.

### node-exporter

Exports host/node OS metrics (CPU, memory, filesystem, network) for each node.

## 2. Installation Evidence

### kube-prometheus stack install

In this environment, direct Helm repository access timed out, so kube-prometheus-stack was installed from a local clone of the official `prometheus-community/helm-charts` repository with local chart dependencies.

Install command used:

```bash
KUBECONFIG=.kube/kind-config helm upgrade --install monitoring /tmp/helm-charts/charts/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --set grafana.enabled=false \
  --set windowsMonitoring.enabled=false
```

Then Grafana was deployed in-cluster as `monitoring-grafana` service with default credentials `admin/prom-operator` and Prometheus datasource provisioning.

Resource verification:

```text
pod/alertmanager-monitoring-kube-prometheus-alertmanager-0   2/2 Running
pod/monitoring-kube-prometheus-operator-...                  1/1 Running
pod/monitoring-kube-state-metrics-...                        1/1 Running
pod/monitoring-prometheus-node-exporter-...                  1/1 Running
pod/prometheus-monitoring-kube-prometheus-prometheus-0       2/2 Running
pod/monitoring-grafana-...                                   1/1 Running

service/monitoring-kube-prometheus-prometheus   9090/TCP
service/monitoring-kube-prometheus-alertmanager 9093/TCP
service/monitoring-grafana                       80/TCP
```

Grafana access:

```bash
KUBECONFIG=.kube/kind-config kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# login: admin / prom-operator
```

Alertmanager access:

```bash
KUBECONFIG=.kube/kind-config kubectl port-forward svc/monitoring-kube-prometheus-alertmanager -n monitoring 9093:9093
```

## 3. Dashboard Questions (Prometheus/Grafana Data)

Source app for analysis: StatefulSet `monitor-app-devops-info-chart` in `default` namespace.

Metrics were collected via Prometheus API and correspond to standard Grafana dashboard panels.

### Q1. Pod resources (StatefulSet CPU/memory)

CPU (cores):

```text
monitor-app-devops-info-chart-0: 0.0019515891
monitor-app-devops-info-chart-1: 0.0011939561
monitor-app-devops-info-chart-2: 0.0011888633
```

Memory (bytes):

```text
monitor-app-devops-info-chart-0: 30834688
monitor-app-devops-info-chart-1: 24375296
monitor-app-devops-info-chart-2: 24268800
```

### Q2. Namespace analysis (default most/least CPU)

From default namespace pods:

- highest CPU: `monitor-app-devops-info-chart-0`
- lowest CPU: `monitor-app-devops-info-chart-2`

### Q3. Node metrics (memory and CPU cores)

```text
node memory used: 5371.078125 MB
node memory usage: 68.93820812279961%
node cpu cores: 20
```

### Q4. Kubelet pods/containers managed

```text
sum(kubelet_running_pods) = 51
sum(kubelet_running_containers) = 80
```

### Q5. Network traffic (default namespace pods)

Receive bytes/sec:

```text
monitor-app-devops-info-chart-0: 74.70465434121226
monitor-app-devops-info-chart-1: 61.18342025367697
monitor-app-devops-info-chart-2: 42.16666666666666
```

Transmit bytes/sec:

```text
monitor-app-devops-info-chart-0: 40.801792651532885
monitor-app-devops-info-chart-1: 34.562870058021865
monitor-app-devops-info-chart-2: 15.940000000000003
```

### Q6. Active alerts (Alertmanager)

```text
active alerts: 1
```

## 4. Init Containers

Init container implementation was added to StatefulSet mode in chart:

- `init-download`: downloads file with `wget` to shared `emptyDir`
- `wait-for-service`: waits for DNS/service availability before app start
- shared volume mounted into main container at `/init-data`

Values profile:

- `k8s/devops-info-chart/values-monitoring.yaml`

### Runtime proof

Deployed app:

```bash
KUBECONFIG=.kube/kind-config helm upgrade --install monitor-app k8s/devops-info-chart \
  -n default -f k8s/devops-info-chart/values-monitoring.yaml --set image.tag=1.0.1
```

Init status:

```text
init-download:Completed
wait-for-service:Completed
```

Init logs:

```text
init-download:
  '/init-data/index.html' saved

wait-for-service:
  Name: monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local
  Address: 10.96.193.169
```

Main container file access:

```text
/init-data/index.html exists and is readable from main container
```

This confirms both required patterns:

1. download file to shared volume before app start;
2. wait-for-service gate before main container launch.
