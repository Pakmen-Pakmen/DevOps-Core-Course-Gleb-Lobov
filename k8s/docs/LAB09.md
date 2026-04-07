## LAB 09 — Kubernetes Fundamentals

In this lab I deployed the **DevOps Info Service** (Docker image from Lab 2) to a local Kubernetes cluster using declarative manifests: **Namespace**, **Deployment**, **Service (NodePort)**, and optional **Ingress with TLS** for the bonus task. The goal was to learn core Kubernetes concepts (Pods, Deployments, Services, labels, rolling updates) and document production-oriented choices (resource requests/limits, liveness and readiness probes, rolling strategy).

Full command output, manifest walkthrough, and step-by-step reproduction notes are in **`k8s/README.md`**. This file is the short lab report aligned with the course checklist in `labs/lab09.md`.

---

### 1. Local Kubernetes setup (Task 1)

**Tools:** `kubectl` (Kubernetes CLI) and a **kind** cluster named `lab09`.

**Why kind instead of minikube:** I chose **kind** (Kubernetes in Docker) because it is lightweight, starts quickly in Docker, and fits CI-style workflows. On this machine **minikube** hit host/SSH timeouts during VM startup, so **kind** was a reliable alternative for the same learning objectives.

**Verify cluster:**

```bash
export KUBECONFIG=/path/to/repo/.kube/kind-config   # if kubeconfig is not default
kubectl cluster-info
kubectl get nodes -o wide
```

**Example output (local run):**

```text
Kubernetes control plane is running at https://127.0.0.1:36585
CoreDNS is running at https://127.0.0.1:36585/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

```text
NAME                  STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                       KERNEL-VERSION                     CONTAINER-RUNTIME
lab09-control-plane   Ready    control-plane   22m   v1.35.1   172.20.0.2    <none>        Debian GNU/Linux 13 (trixie)   6.6.87.2-microsoft-standard-WSL2   containerd://2.2.1
```

---

### 2. Application deployment (Task 2)

**Manifest:** `k8s/deployment.yml`

- **Image:** `pakmengamer/devops-info-service:1.0.1` (from Lab 2; `SERVICE_VERSION` in `app_python/app.py` matches).
- **Replicas:** at least **3** in the spec; the file is also used to demonstrate **scaling to 5** (Task 4).
- **Resources:** `requests` 128Mi / 100m CPU; `limits` 256Mi / 200m CPU — keeps scheduling predictable for a small Flask app.
- **Probes:** **liveness** `GET /health`, **readiness** `GET /ready` (readiness endpoint added in `app_python/app.py` for this lab).
- **Rolling update:** `RollingUpdate` with `maxUnavailable: 0`, `maxSurge: 1` so updates do not drop below desired replica count during rollout.
- **Security:** non-root container (aligned with the Lab 2 image); labels `app: devops-info-service` for selector wiring.

**Apply:** `kubectl apply -f k8s/namespace.yml -f k8s/deployment.yml` (namespace `lab09`).

---

### 3. Service configuration (Task 3)

**Manifest:** `k8s/service.yml`

- **Type:** `NodePort` — service port **80** → container port **5000** (named port `http`), **nodePort 30080**.
- **Selector:** `app: devops-info-service` — matches Deployment pod labels.

**Access from the host:** `minikube service …` or, on **kind**, often **`kubectl port-forward -n lab09 svc/devops-info-service 8080:80`** for HTTP checks (see evidence in `k8s/README.md`).

---

### 4. Scaling and updates (Task 4)

- **Scale to 5:** `kubectl scale deployment/devops-info-deployment -n lab09 --replicas=5` or set `spec.replicas: 5` in `deployment.yml` and `kubectl apply`.
- **Rolling update:** change image tag or pod template metadata (e.g. annotation), `kubectl apply`, then `kubectl rollout status deployment/devops-info-deployment -n lab09`.
- **Rollback:** `kubectl rollout history …` and `kubectl rollout undo deployment/devops-info-deployment -n lab09`.

With **maxUnavailable: 0**, **maxSurge: 1**, Kubernetes creates new pods before terminating old ones, which supports **zero-downtime** rollouts under normal conditions (see `kubectl describe deployment` in `k8s/README.md`).

---

### 5. Documentation (Task 5)

**Primary documentation:** **`k8s/README.md`** includes:

1. **Architecture** — Mermaid diagram, traffic flow (NodePort + optional Ingress).
2. **Manifest files** — table and rationale for replicas, probes, resources.
3. **Deployment evidence** — `kubectl get all`, pods/services, `kubectl describe deployment` excerpts, `curl` to `/health` and `/ready` via port-forward.
4. **Operations** — apply commands, scaling output, rolling update and rollback history.
5. **Production considerations** — probes, limits, improvements (HPA, PDB, NetworkPolicy, secrets, observability).
6. **Challenges & solutions** — table (ImagePullBackOff, probes, Ingress).

---

### 6. Bonus — Ingress with TLS (optional)

**Manifests:** `k8s/deployment-app2.yml`, `k8s/service-app2.yml` (second app: `nginxdemos/hello`), `k8s/ingress.yml` — path-based routing for **`/app1`** and **`/app2`**, TLS via Secret `tls-secret`.

**Steps:** install or enable an NGINX Ingress controller (minikube addon or [ingress-nginx on kind](https://kubernetes.github.io/ingress-nginx/deploy/#kind)), generate self-signed cert with `openssl`, `kubectl create secret tls tls-secret -n lab09`, apply Ingress, add `local.example.com` to `/etc/hosts` pointing at the Ingress address, then `curl -k https://local.example.com/app1/…` and `/app2/`.

**Why Ingress** over NodePort alone: single HTTP/HTTPS entrypoint, path and host routing, TLS termination — closer to production L7 exposure than a single high node port per service.

---

### Repository files (Lab 9)

| Path | Role |
|------|------|
| `k8s/namespace.yml` | Namespace `lab09` |
| `k8s/deployment.yml` | Main app Deployment |
| `k8s/service.yml` | NodePort Service |
| `k8s/deployment-app2.yml` | Bonus second Deployment |
| `k8s/service-app2.yml` | Bonus Service for app2 |
| `k8s/ingress.yml` | Bonus Ingress + TLS |
| `k8s/README.md` | Detailed evidence and operations |
| `k8s/docs/LAB09.md` | This lab report |

---

## Checklist (labs/lab09.md)

| Task | Status |
|------|--------|
| Task 1 — kubectl + local cluster, cluster-info / nodes | Documented in §1 |
| Task 2 — `deployment.yml`, ≥3 replicas, resources, probes, labels | §2 |
| Task 3 — `service.yml`, NodePort, selectors | §3 |
| Task 4 — scale to 5, rolling update, rollback | §4 + `k8s/README.md` |
| Task 5 — full README sections | `k8s/README.md` |
| Bonus — Ingress + TLS + second app | §6 + manifests |
