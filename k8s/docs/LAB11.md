## LAB 11 — Kubernetes Secrets and HashiCorp Vault

This lab extends the Helm chart from Lab 10 with **native Kubernetes Secrets** and **HashiCorp Vault** (KV v2, Kubernetes auth, Vault Agent sidecar injection). Implementation lives on branch **`11lab`**.

**Full evidence** (commands, YAML snippets, cluster output): [`k8s/SECRETS.md`](../SECRETS.md). The course assignment also names `k8s/SECRETS.md` as the primary deliverable for Task 4.

---

### 1. What was implemented

| Task | Summary |
|------|---------|
| **Task 1 — K8s Secrets** | Created `app-credentials` with `kubectl create secret generic`; inspected YAML; decoded base64; documented encoding vs encryption. |
| **Task 2 — Helm secrets** | Added `templates/secrets.yaml`, `serviceAccount`, `envFrom.secretRef` in Deployment; placeholders in `values.yaml`; verified env vars in pod without leaking values in `describe`. |
| **Task 3 — Vault** | Vault installed with Helm from cloned `hashicorp/vault-helm` (HashiCorp Helm repo returned HTTP 403 in this environment); KV path, Kubernetes auth, policy, role; injector annotations; secret file under `/vault/secrets/config`. |
| **Task 4 — Docs** | [`k8s/SECRETS.md`](../SECRETS.md) with all required sections. |

**Bonus** (Vault Agent templates, named env helper blocks): not implemented.

---

### 2. Repository layout (Lab 11)

| Path | Purpose |
|------|---------|
| `k8s/devops-info-chart/templates/secrets.yaml` | Helm-managed `Secret` (`stringData`, labels). |
| `k8s/devops-info-chart/templates/serviceaccount.yaml` | Dedicated ServiceAccount for Vault role binding. |
| `k8s/devops-info-chart/templates/deployment.yaml` | `envFrom` + optional Vault injector annotations. |
| `k8s/devops-info-chart/templates/_helpers.tpl` | `secretName`, `serviceAccountName` helpers. |
| `k8s/devops-info-chart/values.yaml` | `secret.*`, `vault.*`, `serviceAccount.*` defaults. |
| `k8s/devops-info-chart/values-vault.yaml` | Profile: enable Vault injection, disable Helm Secret env when using Vault-only flow. |
| `k8s/SECRETS.md` | Detailed lab report and terminal evidence. |

---

### 3. Quick commands (reference)

```bash
# Task 1 — imperative secret (example namespace lab11)
kubectl create secret generic app-credentials -n lab11 \
  --from-literal=username=devuser --from-literal=password='S3cr3t!Pass'

# Helm app (Kubernetes Secret env injection)
./bin/helm upgrade --install lab11-app k8s/devops-info-chart -n lab11

# Vault profile (injector + file)
./bin/helm upgrade lab11-app k8s/devops-info-chart -n lab11 -f k8s/devops-info-chart/values-vault.yaml
```

---

### 4. Checklist (`labs/lab11.md`)

| Item | Location |
|------|----------|
| kubectl secret create / view / decode | [`k8s/SECRETS.md`](../SECRETS.md) §1 |
| Helm `secrets.yaml`, values, Deployment | [`k8s/SECRETS.md`](../SECRETS.md) §2 + chart files |
| Resource requests/limits | [`k8s/SECRETS.md`](../SECRETS.md) §3 |
| Vault install, KV, auth, policy, role, injection | [`k8s/SECRETS.md`](../SECRETS.md) §4 |
| Security analysis | [`k8s/SECRETS.md`](../SECRETS.md) §5 |
