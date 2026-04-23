## LAB 14 — Progressive Delivery with Argo Rollouts

Primary detailed report: [`k8s/ROLLOUTS.md`](../ROLLOUTS.md).

---

### 1. Completed Tasks

| Task | Status | Notes |
|------|--------|-------|
| Task 1 — Fundamentals | Done | Rollouts controller + dashboard installed, plugin installed, dashboard reachable via port-forward. |
| Task 2 — Canary | Done | Helm chart converted from Deployment to Rollout, step-based canary configured, manual promote and abort tested. |
| Task 3 — Blue-Green | Done | Active/preview services configured, promotion tested, rollback via undo verified. |
| Task 4 — Documentation | Done | Full documentation and command evidence in `k8s/ROLLOUTS.md`. |

Bonus automated analysis was not implemented.

---

### 2. Main Files

| Path | Purpose |
|------|---------|
| `k8s/devops-info-chart/templates/rollout.yaml` | Rollout CRD template with canary/blue-green strategy selection. |
| `k8s/devops-info-chart/templates/service-preview.yaml` | Preview service for blue-green. |
| `k8s/devops-info-chart/values-rollout-canary.yaml` | Canary strategy values. |
| `k8s/devops-info-chart/values-rollout-bluegreen.yaml` | Blue-green strategy values. |
| `k8s/ROLLOUTS.md` | Required detailed lab documentation. |

---

### 3. Validation Snapshot

- Rollouts components in `argo-rollouts` are running.
- Canary rollout progressed through configured steps and reached healthy state.
- Canary abort reverted traffic to stable image.
- Blue-green rollout paused in preview, then promoted, then rolled back instantly with `undo`.
