# Inline Volumes & Volume Types

> **Category:** Storage

## What It Is

An **inline volume** is a volume defined **inside** a Pod's `.spec.volumes` — its lifecycle is **tied to the Pod**. When the Pod is deleted, so is the volume (unless it mounts an external PV/PVC). These are the simplest storage option.

## Why They Exist

Pod storage is ephemeral by default, but some workloads need:
- **Cache storage** that can be shared within a Pod (between containers)
- **Configuration/secrets** mounted as files (not env vars)
- **Node-local** scratch space

Inline volumes provide these **without** the PV/PVC indirection — they're declared right in the Pod spec.

## Inline Volume Types

| Volume | Description | Persistent? | Ephemeral? |
|--------|-------------|-------------|------------|
| `emptyDir` | Empty disk (Pod-scoped) | ❌ | ✅ |
| `hostPath` | A path **on the Node** | ❌ (Node-local) | ✅ (tied to Node) |
| `configMap` | Inject a ConfigMap as files | ❌ | ✅ |
| `secret` | Inject a Secret as files | ❌ | ✅ |
| `downwardAPI` | Pod metadata as files | ❌ | ✅ |
| `persistentVolumeClaim` | An existing PVC (binds to PV) | ✅ | ❌ |
| `csi` | A CSI volume directly in the Pod spec | ✅ | ❌ |
| `projected` | Combines multiple volume sources | ❌ | ✅ |
| `ephemeral` | **CSI ephemeral** (K8s 1.23+) | ❌ | ✅ |

## emptyDir

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
    - name: cache
      mountPath: /cache
  volumes:
  - name: cache
    emptyDir: {}         # Empty dir on the node (in /var/lib/kubelet/pods/<uid>/)
```

- Empty initially — **shared** between containers in the Pod
- Deleted when the Pod is deleted
- Can use a backing medium: `emptyDir: { medium: Memory }` for tmpfs (RAM-backed)

## hostPath

Mounts a **directory from the Node** into the Pod. **Tightly couples the Pod to its Node.**

```yaml
volumes:
- name: logs
  hostPath:
    path: /var/log/pods       # Path on the Node
    type: Directory           # Directory | File | Socket | CharDevice | BlockDevice
```

- **Not portable** — Pod can only run where this path exists
- **Security risk** — Pod can read/write Node filesystem
- Often used for **logging agents** (DaemonSets that tail host files)

## ConfigMap & Secret Volumes

Mount configuration/secrets **as files** (not env vars):

```yaml
# ConfigMap as a volume
volumes:
- name: config-vol
  configMap:
    name: my-config

# Secret as a volume
volumes:
- name: secret-vol
  secret:
    secretName: my-secret
```

```yaml
containers:
- volumeMounts:
  - name: config-vol
    mountPath: /etc/config       # All keys become files in /etc/config/
  - name: secret-vol
    mountPath: /etc/secret
    readOnly: true
```

- Keys in the ConfigMap/Secret become **files** in the mount path
- Updates to the source ConfigMap/Secret take ~60-100s to reflect (via `configMapUpdated` refresh)
- For Secrets: **never log files** mounted from secrets! (they contain the raw secret)

## Downward API

```yaml
volumes:
- name: downward
  downwardAPI:
    items:
    - path: "pod-name"
      fieldRef:
        fieldPath: metadata.name
    - path: "pod-cpu"
      resourceFieldRef:
        containerName: app
        resource: limits.cpu
```

Exposes Pod metadata **as files** — e.g., the Pod name, the Node name, the CPU limit.

## Projected Volumes

A **projected** volume combines several sources **into one mount point**:

```yaml
volumes:
- name: combined
  projected:
    sources:
    - configMap:
        name: my-config
    - secret:
        name: my-key
    - downwardAPI:
        items:
        - path: "namespace"
          fieldRef:
            fieldPath: metadata.namespace
```

All keys from ConfigMap, Secret, and DownwardAPI are merged into one directory (`/combined`).

## ephemeral (CSI Ephemeral, Dynamic Inline)

A newer feature (K8s 1.23+) — lets a CSI driver provision a **temporary volume** inline in the Pod:

```yaml
volumes:
- name: ebs
  ephemeral:
    volumeAttributes:
      size: "5Gi"
      type: "gp3"
    # No csi: block — the driver is chosen via CSIDriver
```

- Creates **and deletes** a volume on the fly (just like `emptyDir`, but backed by real disks)
- Requires a CSI driver that supports ephemeral volumes (e.g., `ebs.csi.aws.com`)

## ephemeral vs emptyDir

|  | emptyDir | ephemeral |
|--|-----------|-----------|
| Backing | Node disk / RAM | Real CSI disk |
| Size | Limited by node | Configurable |
| Lifecycle | Pod only | Pod only |
| Storage cost | Free | Pays per GB |

## SubPath

Mounts a **subdirectory** of a volume to a path — avoids clobbering other volume mounts:

```yaml
volumeMounts:
- name: data
  mountPath: /etc/nginx/nginx.conf   # Mount a file
  subPath: nginx.conf                # The path INSIDE the volume
```

```yaml
# Mount a configMap key as a file at a specific location
volumeMounts:
- name: config
  mountPath: /etc/app/config.yaml
  subPath: config.yaml
volumes:
- name: config
  configMap:
    name: app-config
```

## Volume Mount Options

| Field | Purpose | Default |
|-------|---------|---------|
| `readOnly` | Mount read-only | false |
| `mountPropagation` | How mounts propagate: `Private` (default) \| `HostToContainer` \| `Bidirectional` | `Private` |
| `subPath` | Mount a subpath (file/subdir) | `""` |
| `recursiveReadOnly` | `true` / `false` (requires K8s 1.27+) | — |

### `mountPropagation`

- `Private`: No propagation (default and safest)
- `HostToContainer`: Host file changes propagate into the Container
- `Bidirectional`: Host → Container and Container → Host (dangerous, needs r/w on host)

## Commands

```bash
# Create a Pod with inline volumes
kubectl apply -f pod.yaml

# Check mounted volumes inside a pod
kubectl exec <pod> -- ls -l /cache /etc/config
kubectl exec <pod> -- df -h

# Describe a Pod — see volume mount info
kubectl describe pod <name> | grep -A5 Volumes

# Check disk size
kubectl exec <pod> -- du -sh /cache

# For hostPath debug:
kubectl debug <pod> --copy-to=debugger --container=debugger
kubectl debug node/<node> --image=busybox:1.28 -- chroot /host
# Now inspect the hostPath:
ls -l /host/var/log/pods
```

## Common Issues

### `hostPath` fails "directory doesn't exist"
```yaml
# Use type: DirectoryOrCreate to auto-create:
hostPath:
  path: /var/log/myapp
  type: DirectoryOrCreate
```

### `subPath` not reflecting ConfigMap updates
```bash
# ConfigMap updates in mounted volumes take ~60 seconds due to kubelet restart
# Use a subPath mount — but it also has delays.
# For live reloading, use an init container that writes the file, or watch the file.
```

### Too-large `emptyDir` (fills node disk)
```yaml
# emptyDir is on the node's disk — it can fill up the Node!
# For large / bursting workloads, mount to /dev/shm (memory):
emptyDir:
  medium: Memory
# Or limit via PVC instead.
```

### Secret volume shows 0644 perms (world-readable)
```bash
# Default secret volume keys are 0644 (world-readable)
# To make them 0640 / readable only by root or a specific group:
apiVersion: v1
kind: Pod
spec:
  securityContext:
    fsGroup: 2000        # Group ID that can read secrets
  containers:
  - volumeMounts:
    - name: secret
      mountPath: /etc/secret
      readOnly: true
```

## Interview Questions

**Q: What is an `emptyDir` volume?**
A: An **ephemeral** volume mounted from the **Node's disk** — it starts empty, is shared between containers in a Pod, and is **deleted when the Pod is deleted**. It's like a temp folder tied to the Pod's lifecycle.

**Q: What's the difference between `emptyDir` and `hostPath`?**
A: `emptyDir` uses the Node's writable layer and is isolated per Pod (unique dir under `/var/lib/kubelet/pods/<uid>`). `hostPath` mounts a **specific, shared path on the Node** — Pod is coupled to the Node, and the data persists beyond Pods.

**Q: Why is `hostPath` risky / not portable?**
A: It **couples the Pod to a specific Node** and requires the path to exist on that Node. Pods are meant to be **node-agnostic**. Use only for DaemonSets (e.g., logging) where the Node context is expected.

**Q: How do you mount a Secret as a file?**
A: Define a `secret` volume referencing the secret name, and mount it with `volumeMounts` — the secret keys become **files** in the mount path.

**Q: What is a `projected` volume?**
A: A projected volume **merges multiple volume sources** (ConfigMap, Secret, DownwardAPI) into **one mount path** — useful for putting config + secrets + Pod metadata in a single directory.

## Related Resources

- [Storage Fundamentals](storage.md)
- [Persistent Volumes](persistent-volumes.md)
- [Storage Classes](storage-classes.md)
- [Secrets (Security)](../06-security/README.md)