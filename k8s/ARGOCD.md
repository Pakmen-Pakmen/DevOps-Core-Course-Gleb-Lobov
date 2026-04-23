# Lab 13 - GitOps with ArgoCD

## 1. ArgoCD Setup

### Installation

ArgoCD was installed with Helm into namespace `argocd`.

Network access to the public Argo Helm repository timed out in this environment, so the official chart source was cloned locally and installed from `charts/argo-cd`:

```bash
git clone https://github.com/argoproj/argo-helm.git /tmp/argo-helm
KUBECONFIG=.kube/kind-config kubectl create namespace argocd
KUBECONFIG=.kube/kind-config helm upgrade --install argocd /tmp/argo-helm/charts/argo-cd -n argocd --set redis-ha.enabled=false
```

Verification:

```text
argocd-application-controller-0 ... Running
argocd-repo-server-... ... Running
argocd-server-... ... Running
```

### UI access method

```bash
KUBECONFIG=.kube/kind-config kubectl -n argocd port-forward svc/argocd-server 18080:443
```

Initial password:

```bash
KUBECONFIG=.kube/kind-config kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

### CLI setup

```bash
./bin/argocd version --client
./bin/argocd login localhost:18080 --username admin --password <password> --insecure
./bin/argocd app list
```

Client version used:

```text
argocd: v3.3.8+7ae7d2c
```

## 2. Application Configuration

Directory created: `k8s/argocd/`

Files:

- `application.yaml` - manual sync baseline app (`lab13` namespace)
- `application-dev.yaml` - dev app (`dev` namespace), auto-sync enabled
- `application-prod.yaml` - prod app (`prod` namespace), manual sync

Common source:

- `repoURL`: `https://github.com/Pakmen-Pakmen/DevOps-Core-Course-Gleb-Lobov.git`
- `targetRevision`: `lab12` (remote branch exists and contains chart)
- `path`: `k8s/devops-info-chart`

All apps set Helm parameter `service.type=ClusterIP` to avoid NodePort collisions in shared local cluster.

## 3. Multi-Environment Deployment

Namespaces:

```bash
kubectl create namespace dev
kubectl create namespace prod
```

Policy split:

- **dev**: `automated.prune=true`, `automated.selfHeal=true`
- **prod**: manual sync only

Observed differences:

```text
dev deployment replicas: 1  (values-dev.yaml)
prod deployment replicas: 5 (values-prod.yaml)
```

App list evidence:

```text
argocd/devops-info-dev  ... SYNCPOLICY Auto-Prune ...
argocd/devops-info-prod ... SYNCPOLICY Manual ...
```

## 4. Self-Healing Evidence

### 4.1 Manual scale drift test (dev)

Command:

```bash
kubectl scale deployment/devops-info-dev-devops-info-chart -n dev --replicas=5
```

Observed:

```text
SCALE_TEST_START:2026-04-23T13:30:06+03:00
before replicas=1
deployment ... scaled
after-manual-scale replicas=1
SCALE_TEST_END:2026-04-23T13:30:19+03:00
```

ArgoCD reconciled drift back to Git-defined replicas.

### 4.2 Pod deletion test (dev)

Command:

```bash
kubectl delete pod -n dev <pod-name>
kubectl wait --for=condition=Ready pod -n dev -l app.kubernetes.io/instance=devops-info-dev --timeout=180s
```

Observed:

```text
old_pod=devops-info-dev-devops-info-chart-...-6hfwt
new_pod=devops-info-dev-devops-info-chart-...-6mbjc
```

This behavior is Kubernetes self-healing (ReplicaSet/Deployment controller), not ArgoCD.

### 4.3 Configuration drift test (dev)

Label-only metadata drift remained and was not reverted (ArgoCD still reported Synced for this case), so a spec-level drift was tested:

```bash
kubectl patch deployment devops-info-dev-devops-info-chart -n dev \
  --type='json' \
  -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/image\",\"value\":\"nginx:1.27\"}]'
```

Observed:

```text
image-now=nginx:1.27
2026-04-23T13:34:59+03:00 image=pakmengamer/devops-info-service:1.0.1
```

ArgoCD self-heal reverted the image to Git state.

### 4.4 Sync behavior notes

- Kubernetes heals failed/missing pods to match deployment spec.
- ArgoCD heals config drift to match Git desired state.
- ArgoCD default reconciliation interval is typically around 3 minutes; webhooks or manual sync can make it immediate.

## 5. Application Access and Status

Manual app sync:

```bash
argocd app sync devops-info-manual
argocd app wait devops-info-manual --health --timeout 180
```

Status:

```text
Sync Status: Synced to lab12
Health Status: Healthy
```

Service checks (port-forward):

```text
DEV_HEALTH:{"status":"healthy",...}
PROD_HEALTH:{"status":"healthy",...}
```
