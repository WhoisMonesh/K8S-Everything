# Migration Guide: Bare-Metal to Cloud Kubernetes

> **Category:** Migration / Operations
> Step-by-step guide for migrating from bare-metal to cloud Kubernetes.

## Overview

```mermaid
graph LR
    A[Bare-Metal Cluster] --> B[Assess Workloads]
    B --> C[Set Up Cloud Cluster]
    C --> Migrate Workloads
    D[Migrate Workloads] --> E[Validate]
    E --> F[Cut Over]
    F --> G[Decommission]
```

## Phase 1: Assessment

### Workload Inventory

```bash
# Export all workloads
kubectl get deployments,statefulsets,daemonsets,jobs,cronjobs -A -o yaml > workloads.yaml

# Export services and ingresses
kubectl get services,ingresses -A -o yaml > networking.yaml

# Export storage
kubectl get persistentvolumes,persistentvolumeclaims,storageclasses -A -o yaml > storage.yaml

# Export config
kubectl get configmaps,secrets -A -o yaml > config.yaml
```

### Checklist

| Item | Action |
|------|--------|
| Workloads | List all deployments, StatefulSets, DaemonSets |
| Networking | List all services, ingresses, network policies |
| Storage | List all PVs, PVCs, StorageClasses |
| Config | List all ConfigMaps, Secrets |
| Dependencies | Map service dependencies |
| Cloud-specific | Identify cloud provider APIs (S3, RDS, etc.) |

## Phase 2: Set Up Cloud Cluster

### Create Cloud Cluster

```bash
# AWS EKS
eksctl create cluster --name prod --region us-east-1 --nodegroup-name workers --node-type m5.xlarge --nodes 3

# Google GKE
gcloud container clusters create prod --zone us-central1-a --machine-type e2-standard-4 --num-nodes 3

# Azure AKS
az aks create --resource-group myRG --name prod --node-count 3 --node-vm-size Standard_D4s_v3
```

### Configure Access

```bash
# Update kubeconfig
aws eks update-kubeconfig --name prod --region us-east-1
gcloud container clusters get-credentials prod --zone us-central1-a
az aks get-credentials --resource-group myRG --name prod
```

## Phase 3: Migrate Workloads

### 3.1 Migrate Storage

```bash
# Create matching StorageClass
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
EOF

# Migrate PVCs
kubectl get pvc -A -o yaml | sed 's/storageClassName: old-class/storageClassName: gp3/' | kubectl apply -f -
```

### 3.2 Migrate ConfigMaps and Secrets

```bash
# Export from bare-metal
kubectl get configmaps -A -o yaml > configmaps.yaml
kubectl get secrets -A -o yaml > secrets.yaml

# Import to cloud cluster
kubectl apply -f configmaps.yaml
kubectl apply -f secrets.yaml
```

### 3.3 Migrate Workloads

```bash
# Export deployments
kubectl get deployments -A -o yaml > deployments.yaml

# Update image references if needed
sed -i 's|myregistry.com/|newregistry.com/|g' deployments.yaml

# Apply to cloud cluster
kubectl apply -f deployments.yaml
```

## Phase 4: Validate

### Validation Checklist

| Check | Command |
|-------|---------|
| Pods running | `kubectl get pods -A` |
| Services reachable | `kubectl get svc -A` |
| Ingress working | `kubectl get ingress -A` |
| Storage bound | `kubectl get pvc -A` |
| Logs flowing | `kubectl logs -f <pod>` |
| Metrics available | `kubectl top pods -A` |

### Load Testing

```bash
# Run load test
kubectl run loadtest --rm -it --image=loadtest -- /loadtest -c 100 -n 60 http://<service>

# Monitor metrics
kubectl top pods -A --sort-by=cpu
```

## Phase 5: Cut Over

### DNS Migration

```bash
# Update DNS to point to cloud cluster
# Option 1: Update Ingress
kubectl annotate ingress my-ingress external-dns.alpha.kubernetes.io/hostname=app.example.com

# Option 2: Update Route53/Cloud DNS
aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://dns.json
```

### Traffic Switch

```bash
# Blue-green: Switch traffic
kubectl patch svc my-service -p '{"spec":{"selector":{"version":"v2"}}}'

# Canary: Gradually shift
kubectl patch virtualservice my-service -p '{"spec":{"http":[{"route":[{"destination":{"host":"my-service","subset":"v1"},"weight":90},{"destination":{"host":"my-service","subset":"v2"},"weight":10}]}]}}'
```

## Phase 6: Decommission

```bash
# Scale down bare-metal workloads
kubectl scale deployment <name> --replicas=0

# Delete resources
kubectl delete namespace <old-namespace>

# Decommission bare-metal cluster
# (follow your infrastructure provider's process)
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Storage not migrating | Different StorageClass | Create matching StorageClass |
| Secrets missing | Not exported | Re-create with correct values |
| Networking issues | Different CNI | Update NetworkPolicies |
| DNS not resolving | External DNS not configured | Set up external-dns |

## Related

- [EKS Deep Dive](../09-cloud-integrations/eks-deep-dive.md)
- [GKE Deep Dive](../09-cloud-integrations/gke-deep-dive.md)
- [AKS Deep Dive](../09-cloud-integrations/aks-deep-dive.md)
- [Backup & Restore](../08-cluster-operations/backup-restore.md)
