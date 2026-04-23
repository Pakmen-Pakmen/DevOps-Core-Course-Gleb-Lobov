## LAB 12 — ConfigMaps and Persistent Volumes

This lab extends the Helm chart with externalized configuration and persistent storage for request visit tracking.

Primary detailed report: [`k8s/CONFIGMAPS.md`](../CONFIGMAPS.md).

---

### 1. Completed Tasks

| Task | Status | Notes |
|------|--------|-------|
| Task 1 — App persistence upgrade | Done | `/` increments persistent counter; `/visits` returns current value; local Docker Compose persistence verified. |
| Task 2 — ConfigMaps | Done | File ConfigMap (`config.json`) + env ConfigMap (`APP_ENV`, `LOG_LEVEL`, `FEATURE_VISITS_COUNTER`) created and mounted/injected. |
| Task 3 — Persistent Volumes | Done | PVC template added, mounted at `/data`, visits data preserved after pod deletion. |
| Task 4 — Documentation | Done | Full evidence in `k8s/CONFIGMAPS.md`. |

Bonus hot reload task was not implemented.

---

### 2. Files Added/Updated

| Path | Purpose |
|------|---------|
| `app_python/app.py` | Visits counter logic, file persistence, `/visits` endpoint. |
| `app_python/tests/test_app.py` | Tests for visits behavior. |
| `app_python/docker-compose.yml` | Local persistence test with `./data:/data`. |
| `app_python/README.md` | Updated local/docker usage and `/visits` docs. |
| `k8s/devops-info-chart/files/config.json` | App config file loaded into ConfigMap. |
| `k8s/devops-info-chart/templates/configmap-file.yaml` | ConfigMap from chart file via `.Files.Get`. |
| `k8s/devops-info-chart/templates/configmap-env.yaml` | ConfigMap for env key-values. |
| `k8s/devops-info-chart/templates/pvc.yaml` | PersistentVolumeClaim template. |
| `k8s/devops-info-chart/templates/deployment.yaml` | ConfigMap mounts, env injection, PVC mount. |
| `k8s/devops-info-chart/values.yaml` | Added `config`, `envConfig`, `persistence`, `VISITS_FILE`. |
| `k8s/devops-info-chart/values-dev.yaml` | Dev overrides for ConfigMap/PVC-related values. |
| `k8s/devops-info-chart/values-prod.yaml` | Prod overrides for ConfigMap/PVC-related values. |
| `k8s/CONFIGMAPS.md` | Full required Lab 12 documentation and evidence. |

---

### 3. Validation Summary

- `helm lint k8s/devops-info-chart` passed.
- Runtime checks confirmed:
  - `kubectl get configmap,pvc` resources present;
  - `/config/config.json` readable in pod;
  - env vars from ConfigMap available in pod;
  - visits counter persisted after deleting app pod.
