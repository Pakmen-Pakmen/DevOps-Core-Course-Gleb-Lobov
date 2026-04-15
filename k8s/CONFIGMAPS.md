# Lab 12 - ConfigMaps and Persistent Volumes

## 1. Application Changes

### Visits counter implementation

`app_python/app.py` was updated to persist visits count in a file:

- default path: `/data/visits` (configurable via `VISITS_FILE`)
- `/` increments and stores visits
- `/visits` returns current counter value
- file writes use atomic replace (`.tmp` + `os.replace`)
- access is guarded by a process-level lock

### New endpoint

- `GET /visits` returns:

```json
{
  "visits": 2,
  "timestamp": "..."
}
```

### Local Docker test evidence

File: `app_python/docker-compose.yml` mounts `./data:/data`.

Commands:

```bash
cd app_python
docker compose up -d --build
curl -s http://127.0.0.1:5000/
curl -s http://127.0.0.1:5000/
curl -s http://127.0.0.1:5000/visits
cat ./data/visits
docker compose restart app
curl -s http://127.0.0.1:5000/visits
cat ./data/visits
docker compose down
```

Observed output:

```text
{"timestamp":"2026-04-15T08:29:52.609034+00:00","visits":2}
2
{"timestamp":"2026-04-15T08:29:56.573172+00:00","visits":2}
2
```

Counter value remained `2` after container restart.

## 2. ConfigMap Implementation

### Chart structure

Added in `k8s/devops-info-chart`:

- `files/config.json`
- `templates/configmap-file.yaml`
- `templates/configmap-env.yaml`

### `config.json` content

```json
{
  "applicationName": "devops-info-service",
  "environment": "dev",
  "featureFlags": {
    "visitsCounter": true,
    "metricsEnabled": true
  }
}
```

### File mount

- Config file ConfigMap is mounted into container at `/config`
- resulting file path: `/config/config.json`

### Environment variables via ConfigMap

- second ConfigMap (`*-env`) provides:
  - `APP_ENV`
  - `LOG_LEVEL`
  - `FEATURE_VISITS_COUNTER`
- deployment uses `envFrom.configMapRef`

### Verification outputs

```bash
KUBECONFIG=.kube/kind-config kubectl get configmap,pvc -n lab12
KUBECONFIG=.kube/kind-config kubectl exec -n lab12 <pod> -- cat /config/config.json
KUBECONFIG=.kube/kind-config kubectl exec -n lab12 <pod> -- sh -c 'env | sort | grep -E "^(APP_ENV|LOG_LEVEL|FEATURE_VISITS_COUNTER)="'
```

```text
NAME                                           DATA   AGE
configmap/lab12-app-devops-info-chart-config   1      20s
configmap/lab12-app-devops-info-chart-env      3      20s
...
persistentvolumeclaim/lab12-app-devops-info-chart-data   Bound ...
```

```text
{
  "applicationName": "devops-info-service",
  "environment": "dev",
  "featureFlags": {
    "visitsCounter": true,
    "metricsEnabled": true
  }
}
```

```text
APP_ENV=dev
FEATURE_VISITS_COUNTER=true
LOG_LEVEL=DEBUG
```

## 3. Persistent Volume

### PVC configuration

Template: `templates/pvc.yaml`

- access mode: `ReadWriteOnce`
- requested storage: from values (`persistence.size`, default `100Mi`)
- storage class configurable (`persistence.storageClass`)

Values:

```yaml
persistence:
  enabled: true
  size: 100Mi
  storageClass: ""
  mountPath: /data
```

### Volume mount in Deployment

- PVC mounted as `data-volume` at `/data`
- visits file path: `/data/visits`

### Persistence test evidence

Steps:

1. hit `/` twice
2. read `/visits` (before deletion)
3. delete pod
4. wait for replacement pod
5. read `/visits` again

Commands:

```bash
KUBECONFIG=.kube/kind-config kubectl -n lab12 port-forward svc/lab12-app-devops-info-chart 18080:80
curl -s http://127.0.0.1:18080/
curl -s http://127.0.0.1:18080/
curl -s http://127.0.0.1:18080/visits
KUBECONFIG=.kube/kind-config kubectl delete pod -n lab12 <old-pod>
KUBECONFIG=.kube/kind-config kubectl wait --for=condition=Ready pod -n lab12 -l app.kubernetes.io/instance=lab12-app --timeout=240s
curl -s http://127.0.0.1:18080/visits
KUBECONFIG=.kube/kind-config kubectl exec -n lab12 <new-pod> -- cat /data/visits
```

Output:

```text
BEFORE:{"timestamp":"2026-04-15T08:28:53.540208+00:00","visits":2}
OLD_POD:lab12-app-devops-info-chart-c5676cb6d-gv9zh
NEW_POD:lab12-app-devops-info-chart-c5676cb6d-k89dz
AFTER:{"timestamp":"2026-04-15T08:29:34.937739+00:00","visits":2}
/data/visits -> 2
```

Data survived pod recreation.

## 4. ConfigMap vs Secret

### Use ConfigMap when

- data is non-sensitive
- values can be visible to application operators
- examples: feature flags, app environment, log levels

### Use Secret when

- data is sensitive
- examples: passwords, API keys, tokens, certificates
- requires tighter access control and stronger operational handling

### Key differences

- ConfigMap: plain configuration for apps
- Secret: sensitive values, base64 encoded object with stricter access expectations
- both can be mounted as files or injected via env vars
