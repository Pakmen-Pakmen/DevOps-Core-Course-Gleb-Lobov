## LAB 16 — Kubernetes Monitoring and Init Containers

Primary detailed report: [`k8s/MONITORING.md`](../MONITORING.md).

---

### 1. Completed Tasks

| Task | Status | Notes |
|------|--------|-------|
| Task 1 — Prometheus stack | Done | kube-prometheus stack installed in `monitoring`; components verified running. |
| Task 2 — Dashboard exploration | Done | All 6 required monitoring questions answered with collected metrics. |
| Task 3 — Init containers | Done | Download init container and wait-for-service init pattern implemented and verified in StatefulSet. |
| Task 4 — Documentation | Done | `k8s/MONITORING.md` created with installation evidence, answers, and init proof. |

Bonus ServiceMonitor task was not implemented.

---

### 2. Main Files

| Path | Purpose |
|------|---------|
| `k8s/devops-info-chart/templates/statefulset.yaml` | Added init container logic with shared `emptyDir` and service wait pattern. |
| `k8s/devops-info-chart/values.yaml` | Added configurable `initContainers.*` block. |
| `k8s/devops-info-chart/values-monitoring.yaml` | Lab 16 profile enabling init containers and stateful workload mode. |
| `k8s/monitoring/grafana-datasource-configmap.yaml` | Grafana datasource provisioning for Prometheus. |
| `k8s/monitoring/grafana.yaml` | Grafana deployment and service in `monitoring` namespace. |
| `k8s/MONITORING.md` | Full required documentation and outputs. |

---

### 3. Validation Snapshot

- Monitoring namespace includes Prometheus, Alertmanager, Operator, kube-state-metrics, node-exporter, and Grafana.
- Stateful app in `default` starts only after both init containers complete.
- Downloaded file is present and readable from main container at `/init-data/index.html`.
- Alertmanager and Prometheus endpoints were used to answer required monitoring questions.
