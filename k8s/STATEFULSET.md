# Lab 15 - StatefulSets and Persistent Storage

## 1. StatefulSet Overview

StatefulSet was used for this lab because the app now needs:

- stable pod identity (`pod-0`, `pod-1`, `pod-2`)
- stable per-pod storage (one PVC per pod)
- ordered rollout/scaling semantics

### StatefulSet vs Deployment

| Feature | Deployment | StatefulSet |
|---------|------------|-------------|
| Pod identity | Ephemeral/random suffix | Stable ordinal (`name-0`, `name-1`) |
| Storage model | Shared PVC or ephemeral | Per-pod PVC via `volumeClaimTemplates` |
| DNS identity | Service-level only | Per-pod DNS via headless service |
| Scale/update order | Unordered | Ordered by ordinal |

Use Deployment for stateless services; use StatefulSet for workloads needing sticky identity/storage.

## 2. Resource Verification

Chart changes:

- Added `templates/statefulset.yaml`
- Added `templates/service-headless.yaml`
- Added `values-statefulset.yaml`
- Kept `templates/rollout.yaml` for reference (enabled only when `workload.kind=rollout`)

Deploy command:

```bash
KUBECONFIG=.kube/kind-config helm upgrade --install stateful-app k8s/devops-info-chart \
  -n stateful-lab15 \
  -f k8s/devops-info-chart/values-statefulset.yaml \
  --set image.tag=1.0.1
```

Verification output:

```text
pod/stateful-app-devops-info-chart-0   Running
pod/stateful-app-devops-info-chart-1   Running
pod/stateful-app-devops-info-chart-2   Running

statefulset.apps/stateful-app-devops-info-chart   3/3

service/stateful-app-devops-info-chart            ClusterIP
service/stateful-app-devops-info-chart-headless   ClusterIP None

persistentvolumeclaim/data-volume-stateful-app-devops-info-chart-0   Bound
persistentvolumeclaim/data-volume-stateful-app-devops-info-chart-1   Bound
persistentvolumeclaim/data-volume-stateful-app-devops-info-chart-2   Bound
```

## 3. Network Identity (Headless Service)

Headless service:

- name: `stateful-app-devops-info-chart-headless`
- `clusterIP: None`

DNS checks from pod-0:

```bash
kubectl exec -n stateful-lab15 stateful-app-devops-info-chart-0 -- \
  getent hosts stateful-app-devops-info-chart-1.stateful-app-devops-info-chart-headless
kubectl exec -n stateful-lab15 stateful-app-devops-info-chart-0 -- \
  getent hosts stateful-app-devops-info-chart-2.stateful-app-devops-info-chart-headless
```

Output:

```text
10.244.0.68 stateful-app-devops-info-chart-1.stateful-app-devops-info-chart-headless.stateful-lab15.svc.cluster.local
10.244.0.70 stateful-app-devops-info-chart-2.stateful-app-devops-info-chart-headless.stateful-lab15.svc.cluster.local
```

Pattern confirmed: `<pod-name>.<headless-service>.<namespace>.svc.cluster.local`.

## 4. Per-Pod Storage Evidence

Port-forwarded each pod directly and generated different visit counts:

```bash
kubectl -n stateful-lab15 port-forward pod/stateful-app-devops-info-chart-0 20080:5000
kubectl -n stateful-lab15 port-forward pod/stateful-app-devops-info-chart-1 20081:5000
kubectl -n stateful-lab15 port-forward pod/stateful-app-devops-info-chart-2 20082:5000
```

Observed `/visits` values:

```text
POD0: {"visits":2,...}
POD1: {"visits":1,...}
POD2: {"visits":3,...}
```

File-level confirmation:

```text
pod0=2
pod1=1
pod2=3
```

Each pod keeps independent state in its own PVC.

## 5. Persistence Test

Steps:

1. recorded pod-0 visits/file value (`2`)
2. deleted `stateful-app-devops-info-chart-0`
3. waited for recreated pod-0
4. checked `/visits` and file value again

Commands:

```bash
kubectl delete pod -n stateful-lab15 stateful-app-devops-info-chart-0
kubectl wait --for=condition=Ready pod/stateful-app-devops-info-chart-0 -n stateful-lab15 --timeout=240s
kubectl -n stateful-lab15 port-forward pod/stateful-app-devops-info-chart-0 20090:5000
curl -s http://127.0.0.1:20090/visits
kubectl exec -n stateful-lab15 stateful-app-devops-info-chart-0 -- cat /data/visits
```

Result:

```text
POD0_AFTER: {"visits":2,...}
cat /data/visits -> 2
```

Data persisted across pod recreation, proving PVC continuity for StatefulSet ordinal pod identity.
