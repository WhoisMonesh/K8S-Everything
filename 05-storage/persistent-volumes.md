# Persistent Volumes (PV) and Claims (PVC)

> **Category:** Storage

## What They Are

- **PersistentVolume (PV)**: A piece of storage **in the cluster** that has been provisioned by an administrator (static) or dynamically via a StorageClass. Cluster-scoped resource.
- **PersistentVolumeClaim (PVC)**: A developer's **request for storage** of a given size and access mode. Namespace-scoped. The Pod consumes a PVC.

The PV and PVC **bind** (one-to-one) when they match.

## Why They Exist

Pods are ephemeral — when a Pod dies, its data dies with it (unless it's on a PV). PVs/PVCs decouple:
- **Storage provisioning** (admin/cloud)
- **Storage consumption** (developer/app)

Think of PVC = a "storage request ticket", and PV = the "allocated disk".

## Architecture

```mermaid
graph TD
    A[Developer creates PVC] --> B[StorageClass / PV Provisioner]
    B --> C[PV gets created\nBound to PVC]
    C --> D[Pod mounts PVC]
    D --> E[Container\n/data (persists across restarts)]
```

## PV vs PVC

| Aspect | PersistentVolume (PV) | PersistentVolumeClaim (PVC) |
|--------|----------------------|-----------------------------|
| **Scope** | Cluster-scoped | Namespace-scoped |
| **Creator** | Admin (static) or Provisioner (dynamic) | Developer |
| **Lifecycle** | Independent of Pods | Independent of Pods |
| **Purpose** | The actual storage resource | A "claim ticket" for storage |
| **Binds to** | One PVC | One PV |

## Binding Rules

A claim binds to a PV when:
- **`accessModes`** are compatible (claim's subset is allowed by PV)
- **`storageClassName`** matches (or both are empty)
- **`resources.requests.storage`**: the PV must have ≥ capacity

If **multiple PVs** match, Kubernetes picks the **smallest fit**.

## Access Modes

| Mode | Meaning | RWO? | RWX? | Multiple Nodes? |
|------|---------|------|------|-----------------|
| `ReadWriteOnce` (RWO) | Read-write by one node | Yes | No | No |
| `ReadOnlyMany` (ROX) | Read-only by many nodes | Yes | Yes | Yes |
| `ReadWriteMany` (RWX) | Read-write by many nodes | No | Yes | Yes |
| `ReadWriteOncePod` (RWOP) | Read-write by one Pod (K8s 1.11+) | Yes | No | No |

### Examples

| Backend | RWO | RWX |
|---------|-----|-----|
| AWS EBS | Yes | No |
| AWS EFS | No | Yes |
| GCP PD | Yes | No (use Filestore) |
| NFS | No | Yes |
| Ceph RBD | Yes | Yes |
| HostPath | Yes | No |

## PV States

| State | Meaning |
|-------|---------|
| `Available` | Not bound — free to claim |
| `Bound` | Bound to a PVC |
| `Released` | PVC deleted, but PV exists (Retain policy) |
| `Failed` | Manual failure |

## PVC API

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
  namespace: default
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: fast-ssd    # Must match a StorageClass; empty uses default
```

When the PVC is created and a matching PV is found (or Provisioner creates one), the PVC becomes `Bound`.

## PV API (Static Example)

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-manual
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain   # Retain keeps data after PVC deletion
  storageClassName: fast-ssd
  csi:
    driver: ebs.csi.aws.com
    volumeHandle: vol-0123456789abcdef0
    readOnly: false
    fsType: ext4
  nodeAffinity:   # If the PV must be on a specific node/zone
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values: ["node-2"]
```

## PV + PVC + Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: data
      mountPath: /usr/share/nginx/html   # Mount path in container
      readOnly: false
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-pvc    # The PVC name (same namespace as Pod)
```

### PVC Mount Options

```yaml
volumeMounts:
- name: data
  mountPath: /data
  readOnly: true           # Mount read-only (useful with ROX)
  subPath: sub-directory   # Mount a subdir instead of the root
  mountPropagation: HostToContainer  # Default
```

### subPath

Mounts a **subdirectory** of the volume (useful for sharing one PVC across pods without collision):

```yaml
volumeMounts:
- name: data
  mountPath: /etc/config/config.properties   # File-level mount
  subPath: config.properties                 # The path inside the volume
```

## Lifecycle: Static vs Dynamic

### Static Provisioning

1. Admin creates a PV (pointing to a real disk)
2. Developer creates a PVC (matching the PV)
3. They bind → Pod consumes the PVC

Best for: **pre-existing disks**, strict control over storage.

### Dynamic Provisioning

1. Admin creates a StorageClass
2. Developer creates a PVC referencing the StorageClass
3. Provisioner auto-creates a PV (and underlying disk)

Best for: **self-service storage** (most common)

## PV Reclaim Policies

| Policy | After PVC deletion | Result |
|--------|--------------------|--------|
| `Retain` | PV stays → `Released` | Admin must cleanup → safe (data preserved) |
| `Delete` | PV + disk deleted | Data gone |
| `Recycle` | (Deprecated) PV wiped + set to `Available` | Never used again |

## Read-Only Many (ROX) Example

A PVC claimed as `ReadOnlyMany` lets **many pods** (across nodes) read from it — ideal for config bundles, golden images, or data shared to all nodes.

```yaml
kind: PersistentVolumeClaim
spec:
  accessModes:
  - ReadOnlyMany
  ...
```

## Shared Storage (RWX) Example

```yaml
kind: PersistentVolumeClaim
spec:
  accessModes:
  - ReadWriteMany        # Many pods write to the same volume (NFS, EFS)
```

## Commands

```bash
# List
kubectl get pv
kubectl get pvc
kubectl get pvc -n <ns>

# Detailed
kubectl describe pv <name>            # Shows claim, status, reclaimPolicy, accessModes
kubectl describe pvc <name>           # Shows volume, events, conditions

# Wide shows node affinity (for binding delays with WaitForFirstConsumer)
kubectl get pv -o wide
kubectl get pvc -o wide

# Create
kubectl apply -f pvc.yaml
kubectl apply -f pv.yaml          # (rare for static)

# Delete (triggers reclaimPolicy)
kubectl delete pvc <name>
kubectl delete pv <name>          # Only if Retention / to force cleanup

# Force-bind (for debugging) — manually edit PV/PVC binding
kubectl patch pvc <name> -p 'spec: {volumeName: "my-manual-pv"}'
```

## Common Issues

### PVC stuck "Pending"
```bash
kubectl describe pvc <name>
# Common causes:
# - No StorageClass set and no static PV matches
# - Access mode mismatch (claim RWX, no PV supports RWX)
# - Capacity mismatch (claim 50Gi, max PV is 10Gi)
```

### "Volume is already bound to a different claim"
```bash
kubectl get pv <name> -o yaml | grep claimRef
# A PV can only bind to one PVC.
# Fix: release the PV first (set claimRef to nil, or delete the PVC)
```

### Pod stuck "ContainerCreating" / "MountVolume" errors
```bash
kubectl describe pod <name>
# "MountVolume.SetUp failed" — volume attach or mount problem
kubectl describe pv <pv-name>            # Check if attached to node
kubectl get volumeattachments            # Check VA status
```

### "Stale" volume attachment (node lost, can't detach)
```bash
kubectl get volumeattachments
kubectl delete volumeattachment <va-name>   # Force-remove; may lose data!
```

### Wrong Access Mode on Cloud Disk

- AWS EBS is **RWO only** — can't be `RWX`
- If you try `RWX` on EBS, the PV stays `Pending`

```bash
# Fix: use EFS (for shared filesystem) or rethink the architecture
```

### PV stuck in "Released"
```bash
# With reclaimPolicy: Retain, the PV is not deleted after PVC deletion.
# Manually clean up:
kubectl patch pv <pv-name> -p 'spec: {claimRef: null}'
kubectl delete pv <pv-name>
```

## PVC Size vs Pod Requests

The PV's capacity must be >= the PVC's request — but the Pod doesn't request a PV size directly. If a Pod writes more than the PV's size (and the FS doesn't support resize), the disk can fill up.

```yaml
containers:
- resources:
    requests:
      memory: "64Mi"
      cpu: "250m"
    limits:
      memory: "128Mi"
# This is Pod compute (CPU/memory), NOT storage. Storage is via PVC.
```

## Interview Questions

**Q: What is the difference between a PV and a PVC?**
A: A **PersistentVolume (PV)** is a unit of storage **in the cluster** (cluster-scoped). A **PersistentVolumeClaim (PVC)** is a developer's **request for storage** (namespace-scoped). PVs and PVCs **bind** together, and Pods consume the PVC.

**Q: When does a PV get created?**
A: Either (1) **dynamically** by a StorageClass+provisioner when a PVC is created, or (2) **statically** by an admin beforehand.

**Q: Can multiple Pods mount the same PVC?**
A: Yes — if the access mode is `ReadOnlyMany` (read-only to many) or `ReadWriteMany` (read-write to many). `ReadWriteOnce` mounts on **one node only** (but multiple pods on the same node can share it).

**Q: What happens when you delete a PVC that uses reclaimPolicy: Delete?**
A: The PV and the **underlying storage** (e.g., AWS EBS volume) are deleted.

**Q: What happens when you delete a PVC that uses reclaimPolicy: Retain?**
A: The PV is NOT deleted — it enters `Released` state, preserving the data. An admin must manually delete it (the disk still exists in the cloud).

**Q: What access mode do AWS EBS volumes support?**
A: `ReadWriteOnce` (RWO) only — they are mounted to **one node**. For multi-node read-write, use Amazon EFS or FSx.

## Related Resources

- [Storage Fundamentals](storage.md)
- [Storage Classes](storage-classes.md)
- [Volume Snapshots](volume-snapshots.md)
- [Inline Volumes](inline-volumes.md)
EOF
echo "persistent-volumes.md written"