# Litmus Chaos Engineering Lab

> **Practice chaos experiments and troubleshoot failures in a safe Docker Desktop Kubernetes environment.**

## Quick Access

| Item | Value |
|------|-------|
| **Dashboard URL** | `http://localhost:9091` |
| **Username** | `admin` |
| **Password** | `litmus` |
| **Target Namespace** | `litmus-lab` |
| **Target App** | `nginx-target` (3 replicas) |

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Docker Desktop Kubernetes (4 nodes)                  │
│                                                        │
│  litmus namespace:                                     │
│  ├── chaoscenter-litmus-frontend (NodePort:30000)     │
│  ├── chaoscenter-litmus-server (GraphQL + MongoDB)    │
│  ├── chaoscenter-litmus-auth-server                   │
│  ├── chaos-operator-ce                                │
│  └── mongodb-0 (replica set)                          │
│                                                        │
│  litmus-lab namespace:                                 │
│  ├── nginx-target (3 replicas - chaos target)         │
│  └── chaosengines (experiment runners)                │
└──────────────────────────────────────────────────────┘
```

## Available Chaos Experiments

| Experiment | What It Does | Impact |
|-----------|--------------|--------|
| `pod-delete` | Randomly kills pods | Pod restart, brief downtime |
| `pod-network-latency` | Adds network delay | Slower responses, timeouts |
| `pod-cpu-hog` | CPU stress test | High CPU, throttling |
| `pod-memory-hog` | Memory stress test | High memory, OOM kills |
| `pod-network-corruption` | Corrupts packets | Connection failures |
| `pod-io-stress` | Disk I/O stress | Slow disk operations |
| `pod-dns-failure` | Blocks DNS resolution | DNS lookup failures |

## Troubleshooting Labs

### Lab 1: Pod Deletion Recovery

**Hypothesis:** Our nginx deployment with 3 replicas can survive single pod deletion.

```bash
# 1. Watch the target pods
kubectl get pods -n litmus-lab -w

# 2. Apply pod-delete experiment
kubectl apply -f chaos-experiments.yaml

# 3. Check the chaos engine status
kubectl get chaosengine pod-delete-experiment -n litmus-lab
kubectl describe chaosengine pod-delete-experiment -n litmus-lab

# 4. Watch chaos results
kubectl get chaosresult -n litmus-lab

# 5. Check if deployment self-healed
kubectl get pods -n litmus-lab -o wide
```

**What to observe:**
- Pod gets terminated (status: Terminating)
- New pod gets scheduled and starts (status: ContainerCreating → Running)
- Deployment controller maintains 3 replicas
- Service endpoints update automatically

### Lab 2: Network Latency Impact

**Hypothesis:** 200ms network latency won't cause our health checks to fail.

```bash
# 1. Apply network latency experiment
kubectl apply -f chaos-experiments.yaml

# 2. Monitor from another terminal
kubectl exec -it <pod-name> -n litmus-lab -- curl -w "@-" -o /dev/null -s http://nginx-target.litmus-lab.svc.cluster.local

# 3. Check chaos results
kubectl get chaosresult -n litmus-lab -o yaml | grep -A5 "experimentStatus"
```

### Lab 3: CPU Hog Analysis

**Hypothesis:** CPU-intensive workloads don't affect other pods on the same node.

```bash
# 1. Apply CPU hog experiment
kubectl apply -f chaos-experiments.yaml

# 2. Monitor node resource usage
kubectl top nodes
kubectl top pods -n litmus-lab

# 3. Check if other pods are affected
kubectl get pods -n litmus-lab
kubectl describe pods -n litmus-lab | grep -A5 "Conditions"
```

### Lab 4: DNS Failure Recovery

**Hypothesis:** DNS failures are isolated and don't cascade to other services.

```bash
# 1. Apply DNS failure experiment
kubectl apply -f chaos-experiments.yaml

# 2. Test DNS resolution from affected pods
kubectl exec -it <pod-name> -n litmus-lab -- nslookup kubernetes.default

# 3. Check if internal service discovery still works
kubectl exec -it <pod-name> -n litmus-lab -- nslookup nginx-target.litmus-lab.svc.cluster.local
```

## Troubleshooting Commands

### Check Experiment Status

```bash
# List all chaos engines
kubectl get chaosengine -A

# Get chaos result details
kubectl get chaosresult -n litmus-lab -o yaml

# Check chaos operator logs
kubectl logs -l name=chaos-operator -n litmus --tail=100

# Check experiment pod logs
kubectl get pods -n litmus-lab -l chaos-type=experiment
kubectl logs -l chaos-type=experiment -n litmus-lab
```

### Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Experiment stuck in Running | RBAC missing | Check `litmus-admin` ClusterRole |
| Pod not targeted | Wrong label | Verify `appinfo.applabel` matches |
| Chaos pod CrashLoopBackOff | Wrong container runtime | Set `CONTAINER_RUNTIME=containerd` |
| Network experiments fail | Missing capabilities | Add `NET_ADMIN` to service account |
| Dashboard shows "Self-Agent Pending" | Subscriber not connected | Restart subscriber pod |

### Check Litmus Components

```bash
# Verify all Litmus pods are healthy
kubectl get pods -n litmus

# Check MongoDB health
kubectl exec mongodb-0 -n litmus -- mongosh --eval 'rs.status()' --quiet

# Check frontend service
kubectl get svc chaoscenter-litmus-frontend-service -n litmus

# Port-forward to dashboard if NodePort doesn't work
kubectl port-forward svc/chaoscenter-litmus-frontend-service -n litmus 8080:9091
```

## Cleanup

```bash
# Remove all chaos experiments
kubectl delete chaosengine --all -n litmus-lab

# Remove target application
kubectl delete deployment nginx-target -n litmus-lab
kubectl delete svc nginx-target -n litmus-lab

# Full cleanup (removes Litmus)
helm uninstall chaoscenter -n litmus
kubectl delete ns litmus litmus-lab
```

## Related Files

- `chaos-experiments.yaml` - All experiment definitions
- `check-setup.sh` - Setup health check script
- `../chaos-engineering.md` - Chaos engineering concepts
