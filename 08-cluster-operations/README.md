# 08. Cluster Operations & Observability

> **Category:** Cluster Operations / Observability

This category covers **running, inspecting, and debugging** a Kubernetes cluster: the kubelet, cluster debugging, upgrades, backup/restore, logging, and monitoring.

## Core Topics

| File | Topic |
|------|-------|
| [kubelet.md](kubelet.md) | Kubelet — the node agent (pods, volumes, CRI) |
| [debugging.md](debugging.md) | Debugging Pods & Nodes |
| [kubectl.md](../cheat-sheets/kubectl.md) | kubectl reference |
| [upgrades.md](upgrades.md) | Upgrading clusters (control plane + nodes) |
| [backup-restore.md](backup-restore.md) | etcd backup + Velero |
| [logging.md](../13-observability/logging.md) | Cluster logging (fluentd, fluent-bit, Loki) |
| [cluster-api.md](cluster-api.md) | Cluster API (declarative multi-cluster lifecycle) |
| [monitoring.md](../13-observability/prometheus.md) | Monitoring (Prometheus + kube-state-metrics) |

## Quick Start: Node Inspection

```bash
kubectl get nodes
kubectl describe node <node>            # Capacity, allocatable, taints, conditions
kubectl top nodes                       # Live usage
kubectl -n kube-system get ds -l name=node-problem-detector   # (optional) node health
```

## Cluster State Overview

```bash
kubectl get cs                      # ComponentStatus (deprecated; use kubelet readyz)
kubectl get --raw /healthz          # Overall health
kubectl get --raw /healthz/kubelet  # Kubelet healthz (per node)
kubectl get --raw /metrics          # Metrics endpoint
```

## Related Resources

- [Workloads](../03-workloads/README.md)
- [Security](../06-security/README.md)
- [Networking](../04-networking/README.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
