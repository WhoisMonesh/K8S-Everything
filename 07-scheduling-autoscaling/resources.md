# Resource Requests & Limits

> **Category:** Scheduling / Performance

## What It Is

Every container can declare **requests** (guaranteed CPU/memory the scheduler must find) and **limits** (the max the container is allowed to use):

```yaml
resources:
  requests:
    memory: "64Mi"     # Scheduler ensures 64Mi is available
    cpu: "250m"        # Scheduler ensures 0.25 CPU is available
  limits:
    memory: "128Mi"    # Container is killed (OOM) if it exceeds this
    cpu: "500m"        # CPU is throttled above this
```

## Why It Exists

- **Requests** tell the **scheduler** "I need this much" — so it packs Pods safely without over-committing a node.
- **Limits** cap a container's usage — a "noisy neighbor" can't starve others.
- They define **Quality of Service (QoS)** classes (Guaranteed, Burstable, BestEffort) and **eviction priority**.

## How the Scheduler Uses Requests

When scheduling a Pod, the scheduler checks each Node's **allocatable capacity minus already-committed requests**:

```
Node allocatable memory:  8 GiB
Already committed (requests): 5 GiB
This Pod request:         1 GiB    → Fits! (5 + 1 <= 8)
```

A Pod is **only scheduled** if every node can satisfy **all** container requests combined.

## CPU Units

| Unit | Meaning |
|------|---------|
| `1` | 1 full core (1000m) |
| `500m` | Half a core |
| `250m` | Quarter of a core |
| `0.25` | 0.25 cores (same as 250m) |

CPU is a **soft** limit — if idle capacity is available, a container can burst above its limit (for CPU). But if the node is busy, CPU is **throttled** (limited) at the limit.

Memory is a **hard** limit — exceeding it triggers an **OOM kill**.

## Limits: CPU vs Memory Behavior

| Resource | Exceeding the limit | Reclaimable? |
|----------|---------------------|--------------|
| **CPU** | Throttled (slowed) | Yes (burstable) |
| **Memory** | Killed (OOMKilled) | No |

### Example: CPU throttling
- Pod limit: 500m
- Burst: Pod tries to use 1000m
- If the node is idle: Pod may briefly use 1000m
- If the node is busy: kernel **throttles** the Pod down to 500m

### Example: Memory OOM kill
- Pod limit: 128Mi
- Pod uses 200Mi → **killed** (OOMKilled), Pod restarts

## Quality of Service (QoS) Classes

Pods are grouped into QoS tiers based on their requests/limits. This decides the **eviction order** under memory pressure:

| QoS Tier | Condition | Eviction Priority |
|----------|-----------|-------------------|
| **Guaranteed** | Every container has `request == limit` | Last |
| **Burstable** | Requests and limits are set, but unequal (or only requests set) | Medium |
| **BestEffort** | No requests or limits set | First |

Eviction under pressure: BestEffort → Burstable → Guaranteed.

### Setting Guaranteed QoS

```yaml
containers:
- name: app
  resources:
    requests:
      memory: "128Mi"
      cpu: "1"
    limits:
      memory: "128Mi"      # Same as request
      cpu: "1"             # Same as request
```

## How to Set Requests/Limits

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

### Common mistake: no requests
```yaml
containers:
- name: app
  image: myapp
  # No resources set!
```
→ This Pod is **BestEffort**. The scheduler has **no idea** how much it needs — it gets placed on a node with any free resources, and is **evicted first** under pressure.

## Resource Units

| Resource | Unit | Format |
|----------|------|--------|
| CPU | Cores | `500m` (0.5 cores) or `1` |
| Memory | Bytes | `128Mi` (128 MiB = 134,217,728 bytes), `1Gi`, `128M` (decimal) |
| Ephemeral storage | Bytes | `1Gi` (disk used by container logs/tmp) |
| Huge pages | Bytes | `2Mi`, `1Gi` |

Use `Mi`/`Gi` (binary) or `M`/`G` (decimal). Kubernetes is strict: `1G = 1,000,000,000` vs `1Gi = 1,073,741,824`.

## LimitRange (Namespace-wide defaults)

Define **default requests/limits** and **bounds** for a namespace:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limits
  namespace: default
spec:
  limits:
  - default:                # Default if a Pod omits resources
      cpu: "200m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:                    # Cap a container can set
      cpu: "2"
      memory: "2Gi"
    min:                    # Minimum a container can request
      cpu: "50m"
      memory: "64Mi"
    type: Container
```

If a Pod sets a value outside `[min, max]`, it's **rejected**.

## Resource Quotas (Namespace-wide caps)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: default
spec:
  hard:
    requests.cpu: "10"      # Total CPU requests across the namespace
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    pods: "100"            # Max 100 Pods
```

## Common Mistakes

### 1. No requests
- Pod is **BestEffort**, evicted first, can cause OOM chaos
- Scheduler can't pack efficiently → node over-commit and thrashing

### 2. CPU limits too low
- App gets throttled even when node has spare capacity
- CPU-bound apps can appear slow despite idle nodes

### 3. Memory limits too high (or none)
- App can OOM-kill, but it's hard to debug
- Noisy neighbors can be starved by over-sized pods

### 4. Requests == Limits everywhere (no burst)
- Pods can't use spare node CPU → poor utilization
- But guaranteed stability (no noisy-neighbor)

## Tuning Strategy

| Strategy | Requests | Limits | Use case |
|----------|----------|--------|----------|
| **Guaranteed** | = Limits | = Requests | Latency-sensitive, DB, predictable workloads |
| **Burstable** (typical) | < Limits | > Requests | General apps, bursty traffic, good efficiency |
| **None** | none set | none set | **Avoid** (BestEffort, evicted first) |

A good rule of thumb:
- **Requests** ~ average usage (so the scheduler packs well)
- **Limits** ~ 2-3x the request (allow headroom)
- For memory, since OOM kills, limit ≈ peak usage + margin

## How to Find the Right Numbers

```bash
# Use the Kubernetes Metrics API (metrics-server)
kubectl top pods        # Actual usage (CPU/Mem)
kubectl top nodes

# Use VerticalPodAutoscaler to recommend:
kubectl describe vpa my-vpa
# Status.recommendation.target gives you suggested requests/limits

# Or use Goldilocks (a tool that runs VPA in recommend-only mode):
kubectl -n goldilocks get all
```

Then tune: `requests` based on typical usage, `limits` based on peak + margin.

## Commands

```bash
# Set resources inline
kubectl set resources deployment myapp --requests=cpu=200m,memory=256Mi
kubectl set resources deployment myapp --limits=cpu=1,memory=512Mi

# Check usage
kubectl top pods
kubectl top nodes
kubectl top pod <pod-name> --containers

# Check QoS class
kubectl get pod <pod> -o jsonpath='{.status.qosClass}'

# Debug OOM
kubectl describe pod <pod-name>
# State: "terminated" with reason "OOMKilled"

# Check Limits in place
kubectl get deploy <name> -o jsonpath='{.spec.template.spec.containers[*].resources}'
```

## Common Issues

### Pods OOMKilled
```bash
kubectl describe pod <name>
# State reason: OOMKilled
# Fix: raise memory limit (and/or request), check for memory leaks
```

### Pods throttled (CPU)
```bash
# Check via metrics — the Pod's CPU is close to its limit
kubectl top pods
# Fix: raise CPU limit or request more headroom
```

### "OOM killed" vs throttled — hard to tell?
```bash
# OOM = killed (State.Terminated.Reason = OOMKilled)
# Throttling = slow (State.Running)
# Check container metrics / cgroup cpu.stat for throttling counters
```

### Scheduler "insufficient CPU"
```bash
kubectl describe pod <name>
# "0/x nodes are available: x Insufficient cpu."
# Fix: lower the pod's CPU request, or add nodes (Cluster Autoscaler)
```

### Pod scheduled on a crowded node despite a low request
```bash
# Check: did the Pod set a request?
kubectl get pod <name> -o jsonpath='{.status.qosClass}'   # BestEffort if no requests
```

## Resource Requests & Scheduling

The scheduler uses requests to **bin-pack** — it picks nodes that satisfy requests first (best fit / least waste). Setting **accurate requests** leads to better density.

- Under-requesting → pods get placed but may OOM/thrash later
- Over-requesting → nodes are underutilized (waste)

**VPA and HPA** both depend on resource requests (VPA sets/recommends them; HPA measures usage against them).

## Interview Questions

**Q: What is the difference between a request and a limit?**
A: A **request** is a **guarantee** — the scheduler ensures the node has that much free; it's the baseline for CPU% (HPA) and QoS. A **limit** is the **maximum** the container can use — exceeding it causes CPU throttling or an OOM kill.

**Q: What happens when a container exceeds its CPU limit?**
A: It gets **throttled** (CPU shares are rate-limited) — the container slows down but is NOT killed. CPU is a "soft" limit.

**Q: What happens when a container exceeds its memory limit?**
A: It is **OOM-killed** (Out of Memory) by the kernel — the container restarts. Memory is a "hard" limit.

**Q: What is the Quality of Service (QoS) of a Pod with no resource requests?**
A: **BestEffort** — the scheduler has no baseline, the Pod is the first evicted under memory pressure, and it can use whatever CPU/mem is free. Avoid for production.

**Q: What's the difference between Guaranteed and Burstable QoS?**
A: **Guaranteed**: request == limit (or no limit set and request set, but generally means request == limit). **Burstable**: request and limit are set but not equal. Guaranteed pods are evicted last under memory pressure.

**Q: How does the scheduler use requests?**
A: It sums the requests of all pending+running Pods on a Node and checks it against the Node's `allocatable` capacity — only scheduling if every request can be satisfied.

**Q: Should you set CPU limits?**
A: It is **disrecommended** by Google/the Kubernetes community to set tight CPU limits (they cause throttling without much benefit, since CPU is already shared). Set **requests** always; set limits only if you want strict CPU capping — otherwise let Pods burst and use CPU-based **HPA** to control scale.

**Q: How do LimitRange and ResourceQuota differ?**
A: LimitRange sets **per-container defaults + bounds** (and can assign a default QoS). ResourceQuota sets **per-namespace totals** (sum across all Pods in the namespace).

## Related Resources

- [Limit Ranges](limit-ranges.md)
- [Resource Quotas](resource-quotas.md)
- [Priority Classes](priority-classes.md)
- [HPA](../03-workloads/hpa.md)
- [VPA](../03-workloads/vpa.md)
- [Pod](../03-workloads/pods.md)
