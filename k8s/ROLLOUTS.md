# Lab 14 - Progressive Delivery with Argo Rollouts

## 1. Argo Rollouts Setup

### Controller and dashboard installation

```bash
KUBECONFIG=.kube/kind-config kubectl create namespace argo-rollouts
KUBECONFIG=.kube/kind-config kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
KUBECONFIG=.kube/kind-config kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/dashboard-install.yaml
KUBECONFIG=.kube/kind-config kubectl get pods -n argo-rollouts
```

Verification:

```text
argo-rollouts-...             1/1 Running
argo-rollouts-dashboard-...   1/1 Running
```

### kubectl plugin

Installed local plugin binary:

```bash
./bin/kubectl-argo-rollouts version
```

```text
kubectl-argo-rollouts: v1.9.0+838d4e7
```

### Dashboard access

```bash
KUBECONFIG=.kube/kind-config kubectl -n argo-rollouts port-forward svc/argo-rollouts-dashboard 3100:3100
```

Check:

```text
HTTP/1.1 302 Found
Location: /rollouts/
```

Open `http://localhost:3100`.

### Rollout vs Deployment

Main differences:

- `kind: Rollout` instead of `kind: Deployment`
- strategy supports `canary` or `blueGreen`
- progressive steps (`setWeight`, `pause`, manual promote)
- abort/retry/undo operations through Rollouts controller
- preview/active service switching for blue-green

## 2. Canary Deployment

### Configuration

Chart conversion:

- Deployment template converted to Rollout and moved to `k8s/devops-info-chart/templates/rollout.yaml`
- canary strategy steps configured:
  - 20% -> pause manual
  - 40% -> pause 30s
  - 60% -> pause 30s
  - 80% -> pause 30s
  - 100%

Canary values file:

- `k8s/devops-info-chart/values-rollout-canary.yaml`

### Deployment and progression

```bash
KUBECONFIG=.kube/kind-config helm upgrade --install canary-app k8s/devops-info-chart -n rollout-canary -f k8s/devops-info-chart/values-rollout-canary.yaml --set image.tag=1.0.1
KUBECONFIG=.kube/kind-config helm upgrade canary-app k8s/devops-info-chart -n rollout-canary -f k8s/devops-info-chart/values-rollout-canary.yaml --set image.tag=1.0.2
KUBECONFIG=.kube/kind-config kubectl-argo-rollouts get rollout canary-app-devops-info-chart -n rollout-canary
KUBECONFIG=.kube/kind-config kubectl-argo-rollouts promote canary-app-devops-info-chart -n rollout-canary
```

Observed:

```text
Step 0/9 setWeight 20
... promoted ...
Step 3/9 setWeight 40
Step 5/9 setWeight 60
Step 7/9 setWeight 80
Step 9/9 setWeight 100
Status: Healthy
stable image: pakmengamer/devops-info-service:1.0.2
```

### Abort test

During rollout to `1.0.3`:

```bash
kubectl-argo-rollouts abort canary-app-devops-info-chart -n rollout-canary
```

Observed:

```text
Status: Degraded
Message: RolloutAborted: Rollout aborted update to revision 3
stable image reverted to pakmengamer/devops-info-service:1.0.2
canary ReplicaSet scaled down
```

## 3. Blue-Green Deployment

### Configuration

Blue-green values file:

- `k8s/devops-info-chart/values-rollout-bluegreen.yaml`

Chart resources:

- active service: `{{ fullname }}`
- preview service: `{{ fullname }}-preview` (template `service-preview.yaml`)
- rollout strategy:
  - `activeService`
  - `previewService`
  - `autoPromotionEnabled: false`

### Flow test

Initial deploy with `1.0.2`:

```text
Images: ...:1.0.2 (stable, active)
```

Trigger update to `1.0.4`:

```bash
kubectl-argo-rollouts set image bluegreen-app-devops-info-chart devops-info-service=pakmengamer/devops-info-service:1.0.4 -n rollout-bg
```

Before promotion:

```text
Status: Paused
Message: BlueGreenPause
Images: 1.0.2 (stable, active) + 1.0.4 (preview)
```

Promote:

```bash
kubectl-argo-rollouts promote bluegreen-app-devops-info-chart -n rollout-bg
```

After promotion:

```text
Images: 1.0.4 (stable, active)
```

### Active vs preview services

```bash
kubectl -n rollout-bg port-forward svc/bluegreen-app-devops-info-chart 19100:80
kubectl -n rollout-bg port-forward svc/bluegreen-app-devops-info-chart-preview 19101:80
```

Both endpoints were reachable during blue-green phase:

```text
ACTIVE:{"status":"healthy",...}
PREVIEW:{"status":"healthy",...}
```

### Instant rollback

```bash
kubectl-argo-rollouts undo bluegreen-app-devops-info-chart -n rollout-bg
```

Observed:

```text
Images: 1.0.2 (stable, active)
```

Traffic switched back to previous stable revision immediately.

## 4. Strategy Comparison

### Canary

Pros:

- gradual risk exposure
- good for observing behavior under partial traffic
- can stop mid-rollout

Cons:

- slower rollout process
- more operational steps/monitoring

### Blue-Green

Pros:

- clear active vs preview split
- instant cutover and instant rollback
- easy pre-production validation on preview

Cons:

- needs more temporary resources (old + new stacks together)
- all-or-nothing promotion

### Recommendation

- use **canary** for high-risk changes where progressive confidence is needed.
- use **blue-green** for fast cutover/rollback requirements and straightforward validation.

## 5. CLI Commands Reference

```bash
# Inspect rollout
kubectl-argo-rollouts get rollout <name> -n <ns>

# Promote next step
kubectl-argo-rollouts promote <name> -n <ns>

# Abort running rollout
kubectl-argo-rollouts abort <name> -n <ns>

# Retry aborted rollout
kubectl-argo-rollouts retry rollout <name> -n <ns>

# Undo to previous stable revision
kubectl-argo-rollouts undo <name> -n <ns>

# Update image directly
kubectl-argo-rollouts set image <name> <container>=<image> -n <ns>
```
