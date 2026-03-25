# Lab 09 — Kubernetes (namespace `lab09`)

Declarative manifests for the **DevOps Info Service** (Lab 2 image) plus optional **bonus**: second app and **Ingress with TLS**.

## 1. Architecture overview

Traffic can reach the main app in two ways:

- **NodePort** — `devops-info-service` exposes port **80** in the cluster and **30080** on the node (maps to container **5000**).
- **Ingress (bonus)** — NGINX Ingress terminates **HTTPS** for `local.example.com` and routes **`/app1`** → Flask app, **`/app2`** → `nginxdemos/hello`.

```mermaid
flowchart LR
  subgraph cluster[Cluster namespace lab09]
    ING[Ingress nginx]
    SVC1[Service devops-info-service]
    SVC2[Service hello-demo-service]
    P1[Pods Flask x3]
    P2[Pods hello x2]
    ING --> SVC1
    ING --> SVC2
    SVC1 --> P1
    SVC2 --> P2
  end
  User([User / curl]) --> ING
  User --> NodePort[NodePort :30080]
  NodePort --> SVC1
```

**Resource strategy:** Flask pods request **128Mi / 100m CPU**, limit **256Mi / 200m** — enough for a small Flask app and keeps the scheduler informed. The demo hello app uses lower requests (**64Mi / 50m**).

---

## 2. Manifest files

| File | Purpose |
|------|---------|
| `namespace.yml` | Isolates all Lab 09 objects in `lab09`. |
| `deployment.yml` | **3 replicas**, RollingUpdate (**maxSurge: 1**, **maxUnavailable: 0**), probes, resources, non-root pod security context, image `pakmengamer/devops-info-service:1.0.1`. |
| `service.yml` | **NodePort** for the Flask Deployment; selector `app: devops-info-service`. |
| `deployment-app2.yml` | Second workload: **`nginxdemos/hello`** (2 replicas) for Ingress bonus. |
| `service-app2.yml` | **ClusterIP** for the hello app (only reached via Ingress or `port-forward`). |
| `ingress.yml` | Path-based rules + **TLS** secret `tls-secret`; regex rewrite so backends receive `/`. |

**Why 3 replicas?** Lab minimum; improves availability during node or pod failures.

**Why separate liveness vs readiness?** Liveness hits **`/health`** (process up). Readiness hits **`/ready`** so traffic is only sent when the app should serve requests (same app today; you can later extend `/ready` with dependency checks).

---

## 3. Deployment evidence

Run against your cluster after applying manifests (see section 4). **Replace the samples below** with your own output for submission.

```bash
kubectl config set-context --current --namespace=lab09
kubectl get all
kubectl get pods,svc -o wide
kubectl describe deployment devops-info-deployment
```

Example shape (not from a live cluster):

```text
NAME                                        READY   STATUS    RESTARTS   AGE
pod/devops-info-deployment-xxxxxxxx-xxxxx   1/1     Running   0          2m
...
NAME                        TYPE        CLUSTER-IP      PORT(S)
service/devops-info-service NodePort      10.96.x.x       80:30080/TCP
```

**App responds (NodePort):**

- Minikube: `minikube service devops-info-service -n lab09 --url` then `curl -s <url>/health | jq .`
- kind / Docker Desktop: `kubectl port-forward -n lab09 svc/devops-info-service 8080:80` then `curl -s http://127.0.0.1:8080/`

---

## 4. Operations performed

### 4.1 Install tools and start a cluster

See **«Пошагово на твоей машине»** at the end of this file for condensed steps.

### 4.2 Build and publish the app image (before first deploy)

The Deployment expects **`pakmengamer/devops-info-service:1.0.1`** (matches `SERVICE_VERSION` in `app_python/app.py`). Push via GitHub Actions (push to `master` with `app_python/**` changes) **or** build locally and push to Docker Hub.

### 4.3 Apply manifests

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl rollout status deployment/devops-info-deployment -n lab09
```

### 4.4 Scaling to 5 replicas

**Declarative (preferred):** set `spec.replicas: 5` in `deployment.yml`, then:

```bash
kubectl apply -f k8s/deployment.yml
kubectl get pods -n lab09 -w
```

**Imperative (quick check):**

```bash
kubectl scale deployment/devops-info-deployment -n lab09 --replicas=5
```

(Optional) scale back to **3** before the next section so the file matches the repo.

### 4.5 Rolling update and rollback

1. Change the Deployment (e.g. image tag to a new version, or add a harmless env var), then `kubectl apply -f k8s/deployment.yml`.
2. Watch: `kubectl rollout status deployment/devops-info-deployment -n lab09`
3. History: `kubectl rollout history deployment/devops-info-deployment -n lab09`
4. Roll back: `kubectl rollout undo deployment/devops-info-deployment -n lab09`

With **maxUnavailable: 0** and **maxSurge: 1**, Kubernetes creates new pods before terminating old ones, which avoids dropping below desired capacity during the rollout.

### 4.6 Bonus — Ingress controller, second app, TLS

**Minikube**

```bash
minikube addons enable ingress
kubectl apply -f k8s/deployment-app2.yml
kubectl apply -f k8s/service-app2.yml
```

**kind** (install NGINX Ingress; see [ingress-nginx kind](https://kubernetes.github.io/ingress-nginx/deploy/#kind)) then apply the same two files.

**TLS secret** (run from repo root; keys are gitignored):

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout k8s/tls.key -out k8s/tls.crt \
  -subj "/CN=local.example.com/O=local.example.com"

kubectl create secret tls tls-secret \
  --namespace=lab09 \
  --key=k8s/tls.key \
  --cert=k8s/tls.crt
```

**Ingress**

```bash
kubectl apply -f k8s/ingress.yml
```

**Hosts file:** add `local.example.com` pointing to the Ingress IP (minikube: `minikube ip`; kind: localhost with published ports per install doc).

```bash
curl -sk https://local.example.com/app1/health
curl -sk https://local.example.com/app2/
```

**Why Ingress over NodePort alone:** single entrypoint (often 80/443), name-based and path-based routing, TLS termination, and no fixed high node ports per service — better match for production-style HTTP services.

---

## 5. Production considerations

- **Probes:** Liveness avoids stuck processes; readiness keeps failing pods out of Service endpoints. Startup probes would be added if the app had a long initialization phase.
- **Resources:** Requests/limits protect the cluster and make scheduling predictable; tune using real metrics (CPU/memory), not guesses.
- **Improvements:** Use **Deployments + PDBs**, **HPA**, **Pod Security Standards**, **NetworkPolicies**, **external secrets**, **structured logging**, **ServiceMonitor** for Prometheus, and **distroless** or **minimal** base images with read-only root where possible.
- **Observability:** Keep **`/metrics`** on the Flask app; scrape with Prometheus in-cluster; aggregate logs with Loki/ELK; trace with OpenTelemetry if you add complexity.

---

## 6. Challenges and solutions

| Issue | What to check |
|-------|----------------|
| **ImagePullBackOff** | Image name/tag exists on Docker Hub; `docker pull` works; for minikube local builds: `eval $(minikube docker-env)` then build with the same tag. |
| **CrashLoopBackOff** | `kubectl logs -n lab09 deploy/devops-info-deployment`; `kubectl describe pod -n lab09 <pod>`. |
| **Probe failures** | Paths and ports: container listens on **5000**; Service uses **targetPort** `http` (name). |
| **Ingress 404** | Ingress class name (`nginx`); addon/controller running; host header and TLS secret present. |

**What we learned:** Kubernetes reconciles desired state in YAML with actual state; labels/selectors tie Services to Pods; rolling updates and rollbacks are first-class workflow features.

---

## Пошагово на твоей машине

1. **Установи** `kubectl` и **minikube** или **kind** ([официальная инструкция](https://kubernetes.io/docs/tasks/tools/)).
2. **Запусти кластер** (`minikube start` или `kind create cluster`).
3. **Собери и запушь образ** с эндпоинтом `/ready` и версией **1.0.1** (через CI в `master` или вручную `docker build` + `docker push` в свой Docker Hub как `pakmengamer/devops-info-service:1.0.1`). Если твой Hub username другой — поправь `image:` в `k8s/deployment.yml`.
4. **Примени:** `kubectl apply -f k8s/namespace.yml -f k8s/deployment.yml -f k8s/service.yml`.
5. **Проверь:** `kubectl get pods -n lab09`, затем доступ по NodePort или `port-forward` (команды выше).
6. **Масштабирование и rollout:** выполни команды из §4.4–4.5 и **вставь реальные выводы** в копию этого README или в отчёт к лабе.
7. **Бонус:** включи Ingress, примени `deployment-app2.yml`, `service-app2.yml`, создай TLS secret, примени `ingress.yml`, проверь `curl` по HTTPS.

Если что-то из шагов падает — пришли вывод `kubectl describe pod` / `kubectl logs` для конкретного Pod.
