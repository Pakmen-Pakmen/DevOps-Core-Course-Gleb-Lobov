# Lab 10 - Helm Package Manager

This document contains the Lab 10 implementation for packaging the Lab 9 Kubernetes app with Helm.

## 1. Chart Overview

### Helm fundamentals and value proposition

- **Chart**: reusable package of Kubernetes manifests with templating.
- **Release**: deployed chart instance (with its own revision history).
- **Values**: environment-specific configuration without duplicating YAML files.

Why Helm helps in this project:

- avoids manifest duplication between dev/prod;
- supports safe upgrades and rollbacks with revision history;
- keeps health checks and resource settings configurable but always enabled;
- supports lifecycle hooks for pre/post install checks.

### Helm setup evidence

```bash
./bin/helm version
./bin/helm show chart oci://registry-1.docker.io/bitnamicharts/nginx
```

```text
version.BuildInfo{Version:"v4.0.0", ...}
Pulled: registry-1.docker.io/bitnamicharts/nginx:22.6.10
apiVersion: v2
appVersion: 1.29.7
dependencies:
- name: common
  repository: oci://registry-1.docker.io/bitnamicharts
```

### Chart structure

Chart path: `k8s/devops-info-chart`

- `Chart.yaml` - metadata, chart type/version, appVersion.
- `values.yaml` - default configuration (replicas, image, service, resources, probes, hooks).
- `values-dev.yaml` - dev overrides (1 replica, relaxed resources, NodePort).
- `values-prod.yaml` - prod overrides (5 replicas, stronger resources, LoadBalancer-ready).
- `templates/deployment.yaml` - templated Deployment with strategy, probes, security contexts.
- `templates/service.yaml` - templated Service (NodePort or LoadBalancer depending on values).
- `templates/_helpers.tpl` - helper templates for naming and labels.
- `templates/hooks/pre-install-job.yaml` - pre-install hook.
- `templates/hooks/post-install-job.yaml` - post-install hook.
- `templates/NOTES.txt` - post-install usage hints.

## 2. Configuration Guide

### Important values

- `replicaCount` - number of Pod replicas.
- `image.repository`, `image.tag`, `image.pullPolicy` - container image config.
- `service.type`, `service.port`, `service.targetPort`, `service.nodePort` - service exposure.
- `resources.requests/limits` - CPU and memory planning.
- `livenessProbe`, `readinessProbe` - health checks (`/health`, `/ready`).
- `strategy.rollingUpdate` - rollout behavior (`maxSurge: 1`, `maxUnavailable: 0`).
- `hooks.preInstall` / `hooks.postInstall` - hook toggles and weights.

### Multi-environment strategy

- **Development (`values-dev.yaml`)**
  - `replicaCount: 1`
  - `service.type: NodePort` (`30081`)
  - smaller resources
  - faster probe startup timings
- **Production (`values-prod.yaml`)**
  - `replicaCount: 5`
  - `service.type: LoadBalancer`
  - higher requests/limits
  - more conservative probe startup timings

### Example installs

```bash
# Dev
KUBECONFIG=.kube/kind-config ./bin/helm install demo-dev k8s/devops-info-chart -n lab10 --create-namespace -f k8s/devops-info-chart/values-dev.yaml

# Upgrade to Prod profile
KUBECONFIG=.kube/kind-config ./bin/helm upgrade demo-dev k8s/devops-info-chart -n lab10 -f k8s/devops-info-chart/values-prod.yaml
```

## 3. Hook Implementation

Implemented two hooks with `hook-succeeded,before-hook-creation` cleanup policy:

1. **Pre-install hook** (`pre-install-job.yaml`)
   - annotation: `"helm.sh/hook": pre-install`
   - weight: `-5`
   - purpose: lightweight validation/log marker before main resources are created.
2. **Post-install hook** (`post-install-job.yaml`)
   - annotation: `"helm.sh/hook": post-install`
   - weight: `5`
   - purpose: smoke-check/log marker after release install.

Execution order is controlled by weight (`-5` first, `5` second).

## 4. Installation Evidence

### Lint/template/dry-run

```bash
./bin/helm lint k8s/devops-info-chart
./bin/helm template demo-dev k8s/devops-info-chart -f k8s/devops-info-chart/values-dev.yaml
./bin/helm install --dry-run --debug demo-dev k8s/devops-info-chart -n lab10 --create-namespace -f k8s/devops-info-chart/values-dev.yaml
```

```text
==> Linting k8s/devops-info-chart
1 chart(s) linted, 0 chart(s) failed

HOOKS:
# Source: devops-info-chart/templates/hooks/post-install-job.yaml
...
# Source: devops-info-chart/templates/hooks/pre-install-job.yaml
...
```

### Release and cluster resources

```bash
KUBECONFIG=.kube/kind-config ./bin/helm list -n lab10
KUBECONFIG=.kube/kind-config kubectl get all -n lab10
```

```text
NAME      NAMESPACE REVISION STATUS   CHART                   APP VERSION
demo-dev  lab10     1        deployed devops-info-chart-0.1.0 1.0.1

NAME                                              READY   STATUS
pod/demo-dev-devops-info-chart-7cc4958946-9tllq   0/1     Running
...
service/demo-dev-devops-info-chart   NodePort   ...   80:30081/TCP
```

### Hook evidence and deletion policy

```bash
KUBECONFIG=.kube/kind-config ./bin/helm get hooks demo-dev -n lab10
KUBECONFIG=.kube/kind-config kubectl get jobs -n lab10
```

```text
"helm.sh/hook": pre-install
"helm.sh/hook-weight": "-5"
"helm.sh/hook-delete-policy": hook-succeeded,before-hook-creation

"helm.sh/hook": post-install
"helm.sh/hook-weight": "5"
"helm.sh/hook-delete-policy": hook-succeeded,before-hook-creation

No resources found in lab10 namespace.
```

### Dev vs prod profile evidence

```bash
KUBECONFIG=.kube/kind-config ./bin/helm upgrade demo-dev k8s/devops-info-chart -n lab10 -f k8s/devops-info-chart/values-prod.yaml
KUBECONFIG=.kube/kind-config kubectl get deploy,svc -n lab10
```

```text
deployment.apps/demo-dev-devops-info-chart   1/5   1   1
service/demo-dev-devops-info-chart   LoadBalancer   ...   <pending>   80:30081/TCP
```

## 5. Operations

### Install

```bash
KUBECONFIG=.kube/kind-config ./bin/helm install demo-dev k8s/devops-info-chart -n lab10 --create-namespace -f k8s/devops-info-chart/values-dev.yaml
```

### Upgrade

```bash
KUBECONFIG=.kube/kind-config ./bin/helm upgrade demo-dev k8s/devops-info-chart -n lab10 -f k8s/devops-info-chart/values-prod.yaml
```

### Rollback

```bash
KUBECONFIG=.kube/kind-config ./bin/helm rollback demo-dev 1 -n lab10
KUBECONFIG=.kube/kind-config ./bin/helm history demo-dev -n lab10
```

```text
Rollback was a success! Happy Helming!
REVISION ... 3 ... deployed ... Rollback to 1
```

### Uninstall

```bash
KUBECONFIG=.kube/kind-config ./bin/helm uninstall demo-dev -n lab10
```

## 6. Testing and Validation

### Chart validation

```text
helm lint: passed (0 failures)
helm template: rendered service/deployment/hooks with expected values
helm install --dry-run --debug: showed computed values + hook manifests
```

### Application accessibility check

```bash
KUBECONFIG=.kube/kind-config kubectl -n lab10 port-forward svc/demo-dev-devops-info-chart 18080:80
curl -s http://127.0.0.1:18080/health
curl -s http://127.0.0.1:18080/ready
```

```text
{"status":"healthy","timestamp":"2026-04-02T13:03:35.690504+00:00","uptime_seconds":57}
{"status":"ready","timestamp":"2026-04-02T13:03:35.698276+00:00"}
```
