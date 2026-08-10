# Core Concepts

> [Back to Index](../README.md)

## Overview

Core Kubernetes abstractions: Pods, workloads, Services, config, and resource governance.

## Component Files

| Concept | File |
|---------|------|
| [Kubernetes](kubernetes.md) | Platform overview |
| [Pod](pods.md) | Smallest deployable unit |
| [Pod Lifecycle](pod-lifecycle.md) | Phases & states |
| [ReplicaSet](replicasets.md) | Pod replication |
| [Deployment](deployments.md) | Declarative updates |
| [DaemonSet](../03-workloads/daemonsets.md) | One pod per node |
| [StatefulSet](../03-workloads/statefulsets.md) | Stateful workloads |
| [Namespace](namespaces.md) | Logical isolation |
| [Service](services.md) | Network abstraction |
| [Label & Selector](labels-selectors.md) | Grouping & selection |
| [Annotation](annotations.md) | Non-identifying metadata |
| [ConfigMap](configmaps.md) | Non-sensitive config |
| [Secret](secrets.md) | Sensitive data |
| [Volume](volumes.md) | Ephemeral storage |
| [PersistentVolume & PVC](persistent-volumes.md) | Persistent storage |
| [Resource Quota](resource-quotas.md) | Namespace resource limits |
| [Limit Range](limit-ranges.md) | Container resource defaults |
| [Pod Disruption Budget](pod-disruption-budgets.md) | Availability during maintenance |

## Quick Start

```bash
# See all Pods across the cluster
kubectl get pods -A

# Create a namespace
kubectl create namespace my-namespace

# Deploy an app
kubectl create deployment web --image=nginx --replicas=3

# Expose it
kubectl expose deployment web --port=80 --type=LoadBalancer

# Check
kubectl get pods,svc
```

## Key Takeaways

1. Pods are created/managed by controllers (Deployments, StatefulSets, DaemonSets)
2. Services provide stable network endpoints for pods
3. ConfigMaps store non-sensitive config, Secrets store sensitive data
4. Namespaces isolate resources and apply quotas
5. ResourceQuotas and LimitRanges enforce governance

[Back to Index](../README.md)
