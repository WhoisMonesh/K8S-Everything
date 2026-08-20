# CKA Mock Exam

> **Category:** Interview Prep / Certification
> Simulated CKA exam scenarios with solutions.

## Exam Format

| Detail | Value |
|--------|-------|
| Duration | 2 hours |
| Questions | 15-20 |
| Pass score | 67% |
| Format | Performance-based (hands-on) |
| Environment | Real Kubernetes cluster |
| Resources | Kubernetes docs allowed |

---

## Mock Exam 1: Cluster Administration (25%)

### Task 1: etcd Backup and Restore

**Question:** Backup the etcd snapshot to `/var/lib/etcd/snapshot.db` and verify the backup was successful.

```bash
# Solution
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /var/lib/etcd/snapshot.db

# Verify
ETCDCTL_API=3 etcdctl snapshot status /var/lib/etcd/snapshot.db --write-out=table
```

### Task 2: Upgrade Control Plane

**Question:** Upgrade the control plane to version `v1.29.0`.

```bash
# Solution
# On control plane node
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.29.0

# Drain worker node first
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# Upgrade kubelet
sudo apt-get update && sudo apt-get install -y kubelet=1.29.0-00 kubectl=1.29.0-00
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# Uncordon
kubectl uncordon node-1
```

### Task 3: RBAC Configuration

**Question:** Create a user `dev-user` with full access to only the `development` namespace.

```bash
# Solution
# Create Role
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: development
  name: dev-user-full-access
rules:
- apiGroups: ["", "apps", "batch", "extensions", "networking.k8s.io"]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["roles", "rolebindings"]
  verbs: ["*"]
EOF

# Create RoleBinding
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-user-binding
  namespace: development
subjects:
- kind: User
  name: dev-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: dev-user-full-access
  apiGroup: rbac.authorization.k8s.io
EOF
```

---

## Mock Exam 2: Workloads & Scheduling (25%)

### Task 4: Create Deployment with Strategy

**Question:** Create a deployment `nginx` with 3 replicas using rolling update strategy (maxSurge: 1, maxUnavailable: 0).

```bash
# Solution
kubectl create deployment nginx --image=nginx:1.25 --replicas=3

kubectl patch deployment nginx -p '
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
'
```

### Task 5: HPA Configuration

**Question:** Create an HPA for the `nginx` deployment targeting 70% CPU with min 2, max 10 replicas.

```bash
# Solution
kubectl autoscale deployment nginx --cpu-percent=70 --min=2 --max=10
```

### Task 6: Pod Scheduling

**Question:** Create a pod `db` that can only run on nodes with label `disk=ssd`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: db
spec:
  containers:
  - name: db
    image: postgres:15
  nodeSelector:
    disk: ssd
EOF
```

---

## Mock Exam 3: Networking (25%)

### Task 7: Network Policy

**Question:** Create a network policy that allows only pods with label `role=frontend` to access pods with label `role=backend` on port 8080.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8080
EOF
```

### Task 8: Service Configuration

**Question:** Create a service `web` that exposes pods with label `app=web` on port 80, targeting port 8080.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
EOF
```

### Task 9: Ingress Configuration

**Question:** Create an ingress for `app.example.com` routing `/api` to service `api-service:8080` and `/web` to service `web-service:80`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
EOF
```

---

## Mock Exam 4: Storage (25%)

### Task 10: PersistentVolume

**Question:** Create a 5Gi PersistentVolume with access mode `ReadWriteOnce` and storageClassName `manual`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
EOF
```

### Task 11: PersistentVolumeClaim

**Question:** Create a 2Gi PersistentVolumeClaim that binds to the PV created above.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  storageClassName: manual
  volumeName: my-pv
EOF
```

### Task 12: StatefulSet

**Question:** Create a StatefulSet `web` with 3 replicas, each with a 1Gi PVC.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  replicas: 3
  serviceName: web
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
EOF
```

---

## Time Management Tips

| Section | Time | Tips |
|---------|------|------|
| Read all questions | 10 min | Mark easy ones first |
| Easy questions | 40 min | Get quick wins |
| Medium questions | 50 min | Most questions |
| Hard questions | 15 min | Only if time permits |
| Review | 5 min | Verify solutions |

## Key Commands

```bash
# Quick context switch
kubectl config use-context <context>

# Generate YAML quickly
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Debug pods
kubectl describe pod <name>
kubectl logs <name> --previous

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Related

- [CKA Certification](cka.md)
- [CKAD Mock Exam](ckad-mock-exam.md)
- [CKS Mock Exam](cks-mock-exam.md)
- [Exam Walkthrough](exam-walkthrough.md)
