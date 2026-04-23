## LAB 15 — StatefulSets and Persistent Storage

Primary detailed report: [`k8s/STATEFULSET.md`](../STATEFULSET.md).

---

### 1. Completed Tasks

| Task | Status | Notes |
|------|--------|-------|
| StatefulSet concepts | Done | Differences vs Deployment documented in `k8s/STATEFULSET.md`. |
| Convert to StatefulSet | Done | Added `templates/statefulset.yaml` with `serviceName` + `volumeClaimTemplates`. |
| Headless Service | Done | Added `templates/service-headless.yaml` (`clusterIP: None`). |
| Per-pod PVCs verified | Done | Three bound PVCs (`...-0`, `...-1`, `...-2`) observed. |
| DNS identity test | Done | Pod-specific DNS resolution tested via `getent hosts` from pod-0. |
| Storage isolation test | Done | Different `/visits` counts per pod (2/1/3). |
| Persistence test | Done | Deleting pod-0 preserved visits count after recreation. |
| Documentation | Done | `k8s/STATEFULSET.md` created with outputs. |

Bonus update-strategy exploration was not implemented.

---

### 2. Main Files

| Path | Purpose |
|------|---------|
| `k8s/devops-info-chart/templates/statefulset.yaml` | StatefulSet workload with per-pod storage template. |
| `k8s/devops-info-chart/templates/service-headless.yaml` | Headless DNS service for StatefulSet pods. |
| `k8s/devops-info-chart/templates/pvc.yaml` | Guarded for non-stateful mode; StatefulSet now uses `volumeClaimTemplates`. |
| `k8s/devops-info-chart/templates/rollout.yaml` | Kept for reference, enabled only in rollout mode. |
| `k8s/devops-info-chart/values-statefulset.yaml` | Lab 15 profile (`workload.kind=statefulset`). |
| `k8s/STATEFULSET.md` | Full required documentation and evidence. |

---

### 3. Validation Snapshot

- StatefulSet `stateful-app-devops-info-chart` healthy with pods `-0/-1/-2`.
- Headless service and pod DNS identities confirmed.
- Per-pod isolated visits counters confirmed.
- Data in pod-0 survived pod deletion and restart.
