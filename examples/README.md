# Kubernetes Examples

> **Category:** Code Examples / Templates

## Overview

This directory contains ready-to-use Kubernetes YAML manifests and configuration examples. Copy, adapt, and deploy them in your cluster.

## Directory Structure

| Directory | Description |
|-----------|-------------|
| [common-patterns/](common-patterns/) | Reusable YAML templates (deployment, service, ingress) |
| [advanced/](advanced/) | Advanced patterns (sidecar, init containers, multi-container) |
| [security/](security/) | RBAC, network policies, PSP examples |
| [storage/](storage/) | PV/PVC, StorageClass, volume snapshot examples |
| [monitoring/](monitoring/) | Prometheus, Grafana, alerting examples |
| [ci-cd/](ci-cd/) | Argo CD, Flux deployment examples |

## Quick Start

```bash
# Deploy the bundled common patterns (Deployment + Service + Ingress + Secret + ConfigMap)
kubectl apply -f common-patterns/common-patterns.md

# Apply everything in this folder at once
kubectl apply -R -f .

# Verify
kubectl get pods,svc,ingress
```

## Common Commands

```bash
# Validate before applying
kubectl apply -f file.yaml --dry-run=client

# Apply and set alias
kubectl apply -f file.yaml --save-config

# Delete from a file
kubectl delete -f file.yaml

# Apply a namespace
kubectl apply -n production -f file.yaml
```
