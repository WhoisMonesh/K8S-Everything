# Chaos Engineering on Kubernetes

> **Category:** Advanced Patterns / SRE
> Systematically inject failures to build confidence in your system's resilience.

## What is Chaos Engineering?

Chaos Engineering is the discipline of experimenting on a system to build confidence in its ability to withstand turbulent conditions in production. The goal is **not to break things randomly**, but to find weaknesses before they cause outages.

## Chaos Engineering Principles

1. **Start with a hypothesis** — "Our system can tolerate X failure"
2. **Design the experiment** — Define the blast radius and steady state
3. **Run the experiment** — Inject the failure
4. **Verify the hypothesis** — Did the system behave as expected?
5. **Automate** — Continuously test to prevent regression

## Chaos Tools for Kubernetes

| Tool | Type | Scope | Source |
|------|------|-------|--------|
| **Chaos Mesh** | Full platform | Pods, nodes, networks, time, IO | CNCF (Chaos Mesh) |
| **Litmus Chaos** | Full platform | Pods, nodes, networks, DNS | CNCF (Litmus) |
| **Chaos Toolkit** | Framework | Anything with an API | chaosToolkit |
| **PowerfulSeal** | Cluster testing | Pods, nodes | Bloomberg |
| **kube-monkey** | Pod deletion | Random pod kills | Netflix-inspired |

## Common Chaos Experiments

### Pod Deletion (Chaos Mesh)

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-delete
  namespace: default
spec:
  action: pod-delete
  mode: one
  selector:
    namespaces:
      - default
    labelSelectors:
      app: my-app
  duration: "30s"
  scheduler:
    cron: "@every 1h"
```

### Network Latency

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-latency
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - default
    labelSelectors:
      app: my-app
  delay:
    latency: "100ms"
    jitter: "20ms"
  duration: "5m"
```

### CPU Stress

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: cpu-stress
spec:
  mode: one
  selector:
    namespaces:
      - default
  stressors:
    cpu:
      workers: 2
      load: 80
  duration: "3m"
```

## Chaos with Pod Disruption Budgets

Always pair chaos experiments with a **PDB** to ensure minimum availability:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2  # at least 2 pods must always be running
  selector:
    matchLabels:
      app: my-app
```

## Chaos Maturity Model

| Level | Description | Example |
|-------|-------------|---------|
| 1 | Manual chaos | Engineer manually kills a pod |
| 2 | Scheduled chaos | CronJob runs chaos experiments weekly |
| 3 | Automated chaos | Chaos platform integrates with CI/CD |
| 4 | Continuous chaos | Automated experiments run daily, with guardrails |
| 5 | Game day | Full-scale simulations with stakeholders |

## Best Practices

1. **Start small** — Kill one pod, not a whole node pool
2. **Use PDBs** — Always have a Pod Disruption Budget
3. **Monitor** — Watch dashboards during experiments
4. **Time-box** — Set `duration` on all experiments
5. **Notify** — Alert the team before running chaos
6. **Learn** — Document findings and fix weaknesses
7. **Automate** — Schedule recurring experiments

## Interview Angle

> "How do you build confidence that your Kubernetes system can tolerate failures? Walk me through a chaos engineering experiment you'd run in production."

## Related

- [PDB](../03-workloads/pdb.md)
- [Disaster Cases](../14-troubleshooting/disaster-cases.md)
- [Incident Case Studies](../14-troubleshooting/incidents/README.md)
- [Netflix Chaos Cascade](../14-troubleshooting/incidents/netflix-chaos-cascade.md)
