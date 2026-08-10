# DaemonSet

> **Category:** Workload / Node-level
> **Also known as:** Kubernetes DaemonSet

## What It Is

A **DaemonSet** ensures that **all (or some) Nodes** run a copy of a **Pod**. When a new node is added to the cluster, the DaemonSet ensures a Pod is scheduled onto it. When a node is removed, the Pod is garbage-collected.

## Why It Exists

You need certain agents or daemons running on **every node** (or a subset):
- **Logging agents** (Fluentd, Filebeat) — collect logs from every node
- **Monitoring agents** (Prometheus Node Exporter) — gather node metrics
- **Networking agents** (Calico, Cilium) — install/maintain CNI
- **Security agents** (Falco) — monitor for threats
- **Node storage** (local PV provisioner)

DaemonSets handle the **node-level scheduling and lifecycle** of these agents.

## Architecture

```mermaid
graph TD
    A[DaemonSet Controller] --> B[Node 1\nPod: fluent-bit]
    A --> C[Node 2\nPod: fluent-bit]
    A --> D[Node 3\nPod: fluent-bit]
    A --> E[Node 4\n(new node)\nPod: fluent-bit]

    subgraph "All Nodes"
        B
        C
        D
        E
    end

    subgraph "DaemonSet"
        A
    end

    subgraph "Pod Template"
        F[Image: fluent/fluent-bit:2.1]
        G[hostPath: /var/log]
        H[hostPath: /var/lib/kubelet]
    end
```

## DaemonSet Spec

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: kube-logging
spec:
  selector:
    matchLabels:
      name: fluent-bit
  updateStrategy:
    type: RollingUpdate          # RollingUpdate | OnDelete
    rollingUpdate:
      maxUnavailable: 1          # How many pods can be unavailable during update
  template:
    metadata:
      labels:
        name: fluent-bit
    spec:
      serviceAccountName: fluent-bit
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.1
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker.containers
        securityContext:
          readOnlyRootFilesystem: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      tolerations:                # Often needed to run on control-plane nodes
      - key: node-role.kubernetes.io/control-plane
        effect: NoSchedule
        operator: Exists
```

## Scheduling DaemonSet Pods

### Node Affinity (Target specific nodes)

```yaml
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: disktype
                operator: In
                values: ["ssd"]
      # Only run on nodes with disktype=ssd
```

### Tolerations (Run on tainted nodes)

```yaml
spec:
  template:
    spec:
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "logging"
        effect: "NoSchedule"
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Exists"
        effect: "NoSchedule"
      # Without this, DaemonSet pods won't run on control-plane nodes
```

## Update Strategies

| Strategy | Description |
|----------|-------------|
| **RollingUpdate** | Replace old pods with new ones — `maxUnavailable` controls rollout |
| **OnDelete** | Old pods are NOT automatically deleted; manually deleted to trigger replacement |

```bash
# Rolling update (default)
kubectl set image ds/fluent-bit fluent-bit=fluent/fluent-bit:3.0

# OnDelete strategy (manual)
kubectl apply -f ds-new.yaml  # Creates new version but won't roll unless old pods are deleted
kubectl delete pod ds-old-node-1  # Only then is a new pod created
```

## Commands

```bash
# Create from file
kubectl apply -f daemonset.yaml

# Get
kubectl get ds                          # All DaemonSets
kubectl get ds -o wide                  # Show node placement
kubectl get pod -l name=fluent-bit      # Pods managed by this DS

# Describe
kubectl describe ds fluent-bit
kubectl describe node <node>           # Shows DaemonSet pods on node

# Scale (not applicable — DS manages one pod per node)
# But you can scale with maxNodesTotal (Enterprise only)

# Check status
kubectl get ds fluent-bit -o jsonpath='{.status}'
# desiredNumberScheduled: 3
# currentNumberScheduled: 3
# numberMisscheduled: 0
# updatedNumberScheduled: 3
# numberReady: 3

# Update image (rolling)
kubectl set image ds/fluent-bit fluent-bit=fluent/fluent-bit:2.2

# Rollback
kubectl rollout undo ds/fluent-bit

# Force update on specific node
kubectl delete pod fluent-bit-abcde -n node-worker-2

# Delete all pods (and let DS recreate)
kubectl delete pod -l name=fluent-bit
```

## DaemonSet Status

| Status Field | Meaning |
|--------------|---------|
| `desiredNumberScheduled` | Total nodes that should have the pod |
| `currentNumberScheduled` | Nodes currently running the pod |
| `numberMisscheduled` | Nodes running pods that shouldn't |
| `numberReady` | Nodes where pod is ready |
| `numberAvailable` | Nodes where pod is Available (ready > minReadySeconds) |
| `updatedNumberScheduled` | Nodes running the latest template |
| `observedGeneration` | Last generation the controller processed |

```bash
# Monitor rollout status
kubectl rollout status ds/fluent-bit
```

## Common Issues & Solutions

### DaemonSet pods stuck in "Pending"
```bash
# Check node selectors, tolerations
kubectl describe pod <pod-name> -n <namespace>
# Look for: "node(s) had taint", "didn't match node selector", "Insufficient" resources

# Ensure tolerations for control-plane taints
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.taints}{"\n"}{end}'
```

### Wrong nodes targeted
```bash
# Check nodeAffinity — does it match any nodes?
kubectl get nodes --show-labels
kubectl describe ds <name>  # Shows selector and template
```

### DaemonSet pods not recreated after deletion
```bash
# Check if the DaemonSet still exists
kubectl get ds -A
# If deleted, recreate it; if pods are stuck
kubectl delete pod <pod> --force --grace-period=0
```

### Resource conflict (each pod runs on every node)
```bash
# If the DaemonSet uses too many resources, it impacts node performance
# Check resource usage:
kubectl top pods -l name=fluent-bit -A
# Limit resources:
kubectl patch ds fluent-bit -p '{"spec":{"template":{"spec":{"containers":[{"name":"fluent-bit","resources":{"limits":{"cpu":"200m","memory":"128Mi"}}}]}}}}'
```

### Update hangs (maxUnavailable: 0)
```yaml
# Rolling update with maxUnavailable: 0 means all must be available
# On a 3-node cluster, this means nothing can be updated
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1      # Allow 1 node at a time (default)
```

## DaemonSet vs Deployment — When to Use Which

| Use Case | DaemonSet | Deployment |
|----------|-----------|------------|
| Run on every node | ✅ | ❌ |
| Run on subset of nodes | ✅ (with nodeAffinity) | ✅ (with nodeSelector/affinity) |
| One pod per node (not per replica) | ✅ | ❌ |
| Stable identity | ❌ | ❌ (use StatefulSet) |
| Stateful | ❌ | ❌ |
| Scaling | Tied to node count | Manual |
| Auto-scaling | ❌ | ✅ (HPA) |

## Best Practices

1. **Always add tolerations** — for control-plane taint (otherwise pods won't schedule on master nodes)
2. **Set resource limits** — DaemonSets run on every node, resource impact is multiplied
3. **Use `maxUnavailable: 1`** — for rolling updates in the strategy
4. **Use node affinity** — to target only the nodes you need (e.g., `k8s-app: kube-dns` only on infra nodes)
5. **Mount hostPaths safely** — use `readOnly: true` whenever possible
6. **Use `updateStrategy: OnDelete`** — when you need manual control over rollouts
7. **Check for scheduling issues** — `kubectl get pods -o wide` and `kubectl describe node`
8. **Limit to necessary nodes** — use tolerations + node affinity + `maxUnavailable` to minimize impact

## Interview Questions

**Q: When would you use a DaemonSet?**
A: When you need a pod running on every node (or subset), like logging agents (Fluentd), monitoring agents (Prometheus Node Exporter), or CNI plugins (Calico).

**Q: How does a DaemonSet handle control-plane nodes?**
A: By default, control-plane nodes have a `NoSchedule` taint — so DaemonSet pods need **tolerations** to run on them.

**Q: Can you limit a DaemonSet to specific nodes?**
A: Yes — use `nodeSelector` or `affinity.nodeAffinity` in the pod template.

**Q: What happens when a new node joins the cluster?**
A: The DaemonSet controller creates a corresponding Pod on the new node within ~1 minute.

**Q: What's the difference between OnDelete and RollingUpdate strategy?**
A: RollingUpdate (default) automatically replaces pods one-by-one. OnDelete requires manual pod deletion to trigger an update — useful for stateful workloads where you want control.

## Related Resources

- [Deployment](deployments.md)
- [StatefulSet](statefulsets.md)
- [Taints & Tolerations](../07-scheduling-autoscaling/taints-tolerations.md)
- [Node Affinity](../07-scheduling-autoscaling/node-affinity.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
