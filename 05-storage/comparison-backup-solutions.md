# Velero vs Kasten vs Stash

> **Category:** Storage / Comparisons
> Decision guide for Kubernetes backup solutions.

## Overview

| Feature | Velero | Kasten (Veeam) | Stash |
|---------|--------|----------------|-------|
| **Type** | Backup/DR | Backup/DR | Backup/DR |
| **Storage** | S3, GCS, Azure | S3, Azure, on-prem | S3, GCS, local |
| **Snapshot** | Volume snapshot | Volume snapshot | Volume snapshot |
| **Backups** | Full cluster | Full cluster | Workload-specific |
| **Restore** | Full/partial | Full/partial | Full/partial |
| **UI** | CLI only | Yes (Kasten K10) | CLI only |
| **Cost** | Free (OSS) | $$$ (Enterprise) | Free (OSS) |
| **Complexity** | Medium | Low | Low |

## When to Use What

### Use Velero When:

- You want **open source** backup
- You need **disaster recovery** (backup/restore to new cluster)
- You want **cloud-native** storage (S3, GCS, Azure)
- You need **scheduled backups**

```bash
# Example: Install Velero
velero install \
  --provider aws \
  --bucket my-bucket \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1

# Example: Create backup
velero backup create my-backup --include-namespaces production

# Example: Restore backup
velero restore create --from-backup my-backup
```

### Use Kasten When:

- You want **enterprise** backup solution
- You need **application-aware** backups
- You want **built-in UI**
- You need **compliance** features

```bash
# Example: Install Kasten K10
helm install k10 kasten/k10 --namespace kasten-io --create-namespace

# Example: Create backup via UI
# Access K10 UI: kubectl port-forward svc/gateway -n kasten-io 8080:80
```

### Use Stash When:

- You want **workload-specific** backups
- You need **database-aware** backups
- You prefer **CRD-based** configuration
- You want **incremental** backups

```bash
# Example: Install Stash
helm install stash appscode/stash --namespace stash --create-namespace

# Example: Create backup
kubectl apply -f - <<EOF
apiVersion: stash.appscode.com/v1beta1
kind: BackupConfiguration
metadata:
  name: my-backup
spec:
  schedule: "0 */6 * * *"
  repository:
    name: local-backend
  target:
    ref:
      apiVersion: apps/v1
      kind: Deployment
      name: my-app
EOF
```

## Comparison Matrix

| Criteria | Velero | Kasten | Stash |
|----------|--------|--------|-------|
| **Backup types** | Full, incremental | Full, incremental, differential | Full, incremental |
| **Volume snapshots** | Yes | Yes | Yes |
| **Application-aware** | No (plugins) | Yes | Yes |
| **Database backup** | No (plugins) | Yes | Yes |
| **Scheduled backups** | Yes | Yes | Yes |
| **Cross-cluster restore** | Yes | Yes | Yes |
| **UI dashboard** | No | Yes | No |
| **RBAC** | Yes | Yes | Yes |
| **Encryption** | Yes | Yes | Yes |
| **Retention policy** | Yes | Yes | Yes |

## Pricing Comparison

| Solution | Free Tier | Paid Plans |
|----------|-----------|------------|
| **Velero** | Unlimited (OSS) | N/A (OSS) |
| **Kasten** | Limited trial | Enterprise licensing |
| **Stash** | Unlimited (OSS) | N/A (OSS) |

## Decision Tree

```
Do you need enterprise support?
├─ Yes → Kasten
└─ No
   ├─ Do you want application-aware backups?
   │  ├─ Yes → Stash
   │  └─ No
   │     ├─ Do you need disaster recovery (cross-cluster)?
   │     │  ├─ Yes → Velero
   │     │  └─ No
   │     │     ├─ Do you prefer CRD-based config?
   │     │     │  ├─ Yes → Stash
   │     │     │  └─ No → Velero
```

## Migration Guide

### Velero to Kasten

```bash
# 1. Install Kasten K10
helm install k10 kasten/k10 --namespace kasten-io --create-namespace

# 2. Create Velero backup location in Kasten
# (via K10 UI: Settings -> Backup Locations)

# 3. Migrate existing backups
# (Kasten can import Velero backups)

# 4. Remove Velero
velero uninstall
```

### Kasten to Velero

```bash
# 1. Install Velero
velero install \
  --provider aws \
  --bucket my-bucket \
  --backup-location-config region=us-east-1

# 2. Export Kasten backups (if needed)
# (Use K10 API to export backup metadata)

# 3. Create Velero backups
velero backup create my-backup --include-namespaces production

# 4. Remove Kasten
helm uninstall k10 -n kasten-io
kubectl delete namespace kasten-io
```

## Best Practices

| Solution | Practice |
|----------|----------|
| Velero | Use `--wait` flag for restore verification |
| Kasten | Use application blueprints for complex apps |
| Stash | Use `BackupSession` for one-time backups |

## Related

- [Velero](velero.md)
- [Backup & Restore](../08-cluster-operations/backup-restore.md)
- [Persistent Volumes](../05-storage/persistent-volumes.md)
