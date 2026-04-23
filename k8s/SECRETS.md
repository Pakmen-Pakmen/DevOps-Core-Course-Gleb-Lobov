# Lab 11 - Kubernetes Secrets and HashiCorp Vault

Short lab overview: [`k8s/docs/LAB11.md`](docs/LAB11.md).

This file documents the completed Lab 11 implementation on branch `11lab`.

## 1. Kubernetes Secrets

Secret was created with imperative `kubectl` command:

```bash
KUBECONFIG=.kube/kind-config kubectl create secret generic app-credentials \
  -n lab11 \
  --from-literal=username=devuser \
  --from-literal=password='S3cr3t!Pass' \
  --dry-run=client -o yaml | KUBECONFIG=.kube/kind-config kubectl apply -f -
```

Secret output:

```yaml
apiVersion: v1
data:
  password: UzNjcjN0IVBhc3M=
  username: ZGV2dXNlcg==
kind: Secret
metadata:
  name: app-credentials
  namespace: lab11
type: Opaque
```

Decoding:

```bash
echo "ZGV2dXNlcg==" | base64 -d
echo "UzNjcjN0IVBhc3M=" | base64 -d
```

```text
devuser
S3cr3t!Pass
```

Encoding vs encryption:

- Kubernetes Secret values are base64-encoded by default.
- Base64 is not encryption.
- In production, enable etcd encryption at rest and use RBAC least privilege.

## 2. Helm Secret Integration

### Chart structure changes

Added:

- `k8s/devops-info-chart/templates/secrets.yaml`
- `k8s/devops-info-chart/templates/serviceaccount.yaml`
- `k8s/devops-info-chart/values-vault.yaml`

Updated:

- `k8s/devops-info-chart/templates/deployment.yaml`
- `k8s/devops-info-chart/templates/_helpers.tpl`
- `k8s/devops-info-chart/values.yaml`

### Secret values and template

`values.yaml` placeholders:

```yaml
secret:
  enabled: true
  name: ""
  data:
    username: "change-me"
    password: "change-me"
```

Deployment consumes all Secret keys via `envFrom.secretRef`.

Rendered output proof:

```text
kind: Secret
...
envFrom:
  - secretRef:
      name: lab11-app-devops-info-chart-secret
```

### Verification in running pod

```bash
POD=$(KUBECONFIG=.kube/kind-config kubectl get pod -n lab11 -l app.kubernetes.io/instance=lab11-app -o jsonpath='{.items[0].metadata.name}')
KUBECONFIG=.kube/kind-config kubectl exec -n lab11 "$POD" -- sh -c 'env | cut -d= -f1 | sort | grep -E "^(PORT|username|password)$"'
KUBECONFIG=.kube/kind-config kubectl describe pod -n lab11 "$POD" | sed -n '/Environment Variables from:/,/Mounts:/p'
```

```text
PORT
password
username
---
Environment Variables from:
  lab11-app-devops-info-chart-secret  Secret  Optional: false
Environment:
  PORT:  5000
```

Secret values are not shown in `kubectl describe pod`.

## 3. Resource Management

Deployment uses configurable requests/limits:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

`requests` define scheduler-guaranteed minimum.  
`limits` define maximum allowed consumption.

## 4. Vault Integration

### Vault install

Direct access to `https://helm.releases.hashicorp.com` returned `403`, so Vault was installed from the official HashiCorp chart source cloned from GitHub:

```bash
git clone https://github.com/hashicorp/vault-helm.git /tmp/vault-helm
KUBECONFIG=.kube/kind-config ./bin/helm upgrade --install vault /tmp/vault-helm \
  -n vault --create-namespace \
  --set server.dev.enabled=true \
  --set injector.enabled=true
KUBECONFIG=.kube/kind-config kubectl get pods -n vault
```

```text
vault-0                                 1/1 Running
vault-agent-injector-5b7dd85f5c-xjh5v   1/1 Running
```

### Vault configuration

Configured inside `vault-0`:

- stored KV secret at `secret/myapp/config`
- enabled Kubernetes auth
- wrote policy `devops-info-policy`
- created role `devops-info-role` bound to app service account in namespace `lab11`

Key output:

```text
Success! Enabled kubernetes auth method at: kubernetes/
Success! Data written to: auth/kubernetes/config
Success! Uploaded policy: devops-info-policy
```

### App injection with Vault Agent

Vault profile values:

```yaml
vault:
  enabled: true
  role: "devops-info-role"
  secretPath: "secret/data/myapp/config"
  fileName: "config"
secret:
  enabled: false
```

Deployment upgrade:

```bash
KUBECONFIG=.kube/kind-config ./bin/helm upgrade lab11-app k8s/devops-info-chart -n lab11 -f k8s/devops-info-chart/values-vault.yaml
```

Injected pod proof:

```text
containers: devops-info-service vault-agent
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"
  vault.hashicorp.com/agent-inject-status: "injected"
  vault.hashicorp.com/role: "devops-info-role"
```

Injected file proof:

```bash
KUBECONFIG=.kube/kind-config kubectl exec -n lab11 <pod> -c devops-info-service -- ls -la /vault/secrets
KUBECONFIG=.kube/kind-config kubectl exec -n lab11 <pod> -c devops-info-service -- sh -c 'sed -n "1,20p" /vault/secrets/config'
```

```text
/vault/secrets/config exists
data: map[password:vault-pass username:vault-user]
```

Sidecar injection pattern summary:

- Vault injector mutates Pod spec based on annotations.
- It adds Vault Agent sidecar + shared volume.
- Agent authenticates with Kubernetes service account and writes secret file to `/vault/secrets`.

## 5. Security Analysis

Kubernetes Secrets:

- easy native integration;
- suitable for simple cases;
- require etcd encryption at rest + strict RBAC for stronger security.

Vault:

- centralized policy-based access control;
- better auditing and secret lifecycle management;
- recommended for production and multi-service environments.

Production recommendation:

- keep only placeholders in Git;
- inject real secrets at deploy time;
- use Vault for sensitive credentials;
- enforce RBAC and namespace isolation.
