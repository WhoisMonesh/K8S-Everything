# Priority Classes (Scheduling Reference)

> **Category:** Scheduling
> See also: [Priority Classes in Workloads](../03-workloads/priority-classes.md)

This is the same concept covered in detail in [../03-workloads/priority-classes.md](../03-workloads/priority-classes.md).

A **PriorityClass** assigns a **priority** to a Pod. Higher-priority Pods can be scheduled first and can **evict (preempt)** lower-priority Pods if the cluster is full.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "Critical workloads"
preemptionPolicy: PreemptLowerPriority   # or Never
```

## Quick Reference

| Topic | Detail |
|-------|--------|
| `value` | Higher = scheduled first + can preempt |
| `preemptionPolicy` | `PreemptLowerPriority` (default) \| `Never` |
| Built-in | `system-cluster-critical` (2000000000), `system-node-critical` (2000000000+1) — non-preemptable |
| Preemption | High-priority Pod evicts the lowest-priority Pod on the best-fit Node |
| Used by | HPA / VPA / Cluster Autoscaler to ensure critical workloads get capacity |

See the full guide in the linked document.
