# Pod Disruption Budget

> **Category:** Workload / Availability  
> **See also:** Detailed version in [Core Concepts: Pod Disruption Budget](../01-core-concepts/pod-disruption-budgets.md)

## What It Is

A **Pod Disruption Budget (PDB)** limits the number of **simultaneously unavailable pods** (i.e., pods that are voluntarily evicted or drained) during voluntary disruptions — such as node drains, cluster upgrades, or scale-downs. It does **not** protect against involuntary failures (crashes, node losses).

## Why It Exists

Without a PDB:
- Draining a node kills all pods on it → **service outage**
- Autoscaler or CA scale-down can take down too many pods
- Rolling updates can exceed tolerance → downtime

With a PDB:
- You **guarantee** a minimum number (or percentage) of pods stay running
- You control **availability vs. operability** trade-off

## Spec

```yaml
apiVersion: policy/v1         # v1 since K8s 1.25+, v1beta1 for older
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  # Pick one of: minAvailable | maxUnavailable
  minAvailable: 2              # At least 2 pods must be up (during voluntary disruption)
  # maxUnavailable: 1           # At most 1 pod can be unavailable
  selector:
    matchLabels:
      app: myapp
---
# Alternative: percentage
spec:
  minAvailable: 80%            # At least 80% pods up
---
# Alternative: maxUnavailable
spec:
  maxUnavailable: 1            # At least N-1 pods up
```

## How PDB Works

The scheduler enforces PDBs by **blocking** voluntary evictions that would push the workload below the minimum.

### Eviction Flow

1. A voluntary eviction is requested (drain node, upgrade, CA scale-down)
2. The PDB controller checks: "Will evicting this pod violate the PDB?"
3. If **yes**, eviction is delayed/queued → **safe for the app**
4. If **no**, eviction proceeds → new pod starts

### PDB + Eviction

PDBs work by **blocking `eviction` subresource calls** (not deletion). The `kubectl drain` command uses evictions.

```bash
# Drain will respect PDB — may take a while
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data
# Will wait / timeout if PDB blocks eviction
```

### maxUnavailable vs minAvailable

| Selector | Meaning | Use Case |
|----------|---------|----------|
| `minAvailable` | Minimum pods that must be running | "Always keep 2 pods up" |
| `maxUnavailable` | Maximum pods that can be unavailable | "Max 1 down at a time" (i.e., keep all-but-one up) |

> You must specify exactly one of `minAvailable` or `maxUnavailable`.

## PDB Status

```yaml
status:
  observedGeneration: 1
  disruptionsAllowed: 1      # How many disruptions can happen
  currentHealthy: 3          # Current healthy pods
  expectedPods: 3            # Total pods
  conditions:
  - type: SyncFailed
    ...
```

## Commands

```bash
# List
kubectl get pdb
kubectl get pdb <name> -n <namespace>

# Describe (shows disruptionsAllowed)
kubectl describe pdb <name>

# Apply
kubectl apply -f pdb.yaml

# Delete
kubectl delete pdb <name>

# Force a drain (ignore PDB — dangerous)
kubectl drain <node> --ignore-daemonsets --delete-local-data --force
```

## Common Issues

### `disruptionsAllowed: 0`
```bash
kubectl describe pdb <name>
# "disruptionsAllowed: 0" — eviction is blocked
# Cause: minAvailable > current healthy pods
# Fix: scale up pods, or lower minAvailable
```

### Drain hangs
```bash
kubectl drain node-1
# Stuck at " pod X: PodDisruptionBudget is not satisfied"
# Cause: PDB prevents eviction of remaining pods
# Options:
# 1. Delete PDB temporarily (kubectl delete pdb myapp-pdb)
# 2. Scale up replicas so PDB can tolerate the drain
# 3. Force: kubectl drain --force --disable-eviction (skips PDB checks)
```

### PDB + HPA conflict
If HPA scales pods down to the `minAvailable` threshold, **no voluntary evictions** can happen.

## PDB + Cluster Autoscaler

- CA won't scale-down a node if it can't **safely evict** the pods on it (respecting PDBs)
- PDBs + CA = safe node lifecycle management

## Best Practices

1. **Define `minAvailable`** = `N-1` (or percentage) so 1 pod can be evicted for maintenance
2. **Use `maxUnavailable` for tight control** (e.g., `maxUnavailable: 1` for small apps)
3. **Keep PDB selector matching pod labels** — if it doesn't match any pods, the PDB is **ineffective**
4. **Don't make PDB too restrictive** — otherwise `drain`, `upgrade`, and `CA` scale-down get stuck
5. **Test draining** before relying on PDBs in production
6. **Use `--timeout` on drain** — to avoid indefinite hangs

## Interview Questions

**Q: Does PDB protect against node failures?**
A: No — PDBs only protect against **voluntary disruptions** (drains, rolling updates, scale-down). Involuntary failures (crash, power loss) bypass PDBs.

**Q: Can you set both `minAvailable` and `maxUnavailable`?**
A: No — exactly one must be set.

**Q: How do you unblock a stuck drain?**
A: Options: (1) temporarily delete the PDB, (2) add more pods/replicas so PDB can tolerate eviction, (3) use `--disable-eviction` (risky).

## Related Resources

- Detailed: [Pod Disruption Budgets (Core Concepts)](../01-core-concepts/pod-disruption-budgets.md)
- [Priority Classes](priority-classes.md)
- [Rollouts/Deployments](deployments.md)
- [Cluster Autoscaler](cluster-autoscaler.md)