## LAB 13 — GitOps with ArgoCD

GitOps deployment was implemented with ArgoCD using declarative Application manifests in `k8s/argocd/`.

Primary detailed report: [`k8s/ARGOCD.md`](../ARGOCD.md).

---

### 1. Completed Scope

| Task | Status | Notes |
|------|--------|-------|
| Task 1 — Installation & setup | Done | ArgoCD installed via Helm in `argocd`; UI access via port-forward; CLI installed and logged in. |
| Task 2 — Application deployment | Done | `k8s/argocd/application.yaml` created, applied, manually synced, healthy in `lab13`. |
| Task 3 — Multi-environment | Done | `application-dev.yaml` and `application-prod.yaml`; dev auto-sync, prod manual; deployed to separate namespaces. |
| Task 4 — Self-healing tests | Done | Manual scale drift reverted, pod deletion test completed, spec drift (image patch) reverted by ArgoCD. |

Bonus ApplicationSet was not implemented.

---

### 2. Key Manifests

| File | Purpose |
|------|---------|
| `k8s/argocd/application.yaml` | Baseline manual-sync app in `lab13`. |
| `k8s/argocd/application-dev.yaml` | Dev app with `automated.prune` + `selfHeal`. |
| `k8s/argocd/application-prod.yaml` | Prod app with manual sync policy. |
| `k8s/ARGOCD.md` | Full evidence and command outputs. |

---

### 3. Validation Snapshot

- `argocd app list` shows all three apps.
- `dev` deployment uses dev profile replicas (`1`).
- `prod` deployment uses prod profile replicas (`5`).
- `argocd app get` shows healthy synced states after sync operations.
- Drift recovery verified on a spec change (`image` patched to `nginx` then reverted).
