# Workloads

> [Back to Index](../README.md)

## Overview

Workload resources manage the Pods that run your applications. This section covers the built-in controllers, scaling strategies, and workload management patterns.

## Component Files

| Concept | File |
|---------|------|
| [Pods](pods.md) | Core workload unit |
| [ReplicaSet](replicasets.md) | Ensuring pod replicas |
| [Deployment](deployments.md) | Declarative updates |
| [Deployment Strategies](deployment-strategies.md) | Rolling, Blue/Green, Canary |
| [StatefulSet](statefulsets.md) | Stateful workloads |
| [DaemonSet](daemonsets.md) | One pod per node |
| [Job](jobs.md) | Batch workloads |
| [CronJob](cronjobs.md) | Scheduled tasks |
| [HPA](hpa.md) | Horizontal Pod Autoscaler |
| [VPA](vpa.md) | Vertical Pod Autoscaler |
| [KEDA](keda.md) | Event-driven autoscaling |
| [Cluster Autoscaler](cluster-autoscaler.md) | Node-level scaling |
| [Priority Classes](priority-classes.md) | Pod scheduling priority |
| [Pod Disruption Budget](pdb.md) | Graceful disruption control |

## Quick Reference

| Resource | Purpose | Scaling | Use Case |
|----------|---------|---------|----------|
| Deployment | Stateless apps | HPA, manual | Web frontends |
| StatefulSet | Stateful apps | Scale down last | Databases, queues |
| DaemonSet | One pod per node | Manual | Logging agents |
| Job | Run-to-completion | Manual | Batch processing |
| CronJob | Scheduled | Manual | Periodic tasks |
| HPA | Auto-scale pods | Metrics | Variable traffic |
| VPA | Resize pods | Recommendations | Memory-efficient |
| KEDA | Event-based scaling | External events | Queue-driven |
| PodDisruptionBudget | Availability guarantee | N/A | Maintenance safety |

## Scaling Options

| Scaler | Level | Trigger |
|--------|-------|---------|
| HPA | Pod | CPU, memory, custom metrics |
| VPA | Pod/Container | Memory usage, OOM |
| KEDA | Pod | External events (queue depth, Kafka lag) |
| Cluster Autoscaler | Node | Node pool utilization / scheduling failures |

[Back to Index](../README.md)
