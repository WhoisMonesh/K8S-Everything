# CKAD Mock Exam

> **Category:** Interview Prep / Certification
> Simulated CKAD exam scenarios with solutions.

## Exam Format

| Detail | Value |
|--------|-------|
| Duration | 2 hours |
| Questions | 15-20 |
| Pass score | 67% |
| Format | Performance-based (hands-on) |
| Environment | Real Kubernetes cluster |
| Resources | Kubernetes docs + kubernetes.io/docs allowed |

---

## Mock Exam 1: Application Design & Build (20%)

### Task 1: Multi-Container Pod

**Question:** Create a pod `multi-app` with two containers: `app` (nginx:1.25) and `sidecar` (busybox:1.36) that shares a volume at `/shared`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: multi-app
spec:
  containers:
  - name: app
    image: nginx:1.25
    volumeMounts:
    - name: shared
      mountPath: /shared
  - name: sidecar
    image: busybox:1.36
    command: ["sh", "-c", "while true; do echo \$(date) > /shared/log.txt; sleep 5; done"]
    volumeMounts:
    - name: shared
      mountPath: /shared
  volumes:
  - name: shared
    emptyDir: {}
EOF
```

### Task 2: Init Container

**Question:** Create a pod `web-app` with an init container that waits for a service `backend` to be ready, then starts the main container `nginx`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: web-app
spec:
  initContainers:
  - name: wait-for-backend
    image: busybox:1.36
    command: ['sh', '-c', 'until nc -z backend-service 80; do echo waiting for backend; sleep 2; done']
  containers:
  - name: nginx
    image: nginx:1.25
EOF
```

### Task 3: Dockerfile Best Practices

**Question:** Write a Dockerfile for a Node.js app that runs as non-root user.

```dockerfile
# Solution
FROM node:18-alpine

# Create non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

# Switch to non-root user
USER appuser

EXPOSE 3000

CMD ["node", "server.js"]
```

---

## Mock Exam 2: Application Deployment (20%)

### Task 4: Deployment with Rolling Update

**Question:** Create a deployment `api` with 3 replicas, rolling update (maxSurge: 25%, maxUnavailable: 25%), and resource limits.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: nginx:1.25
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
EOF
```

### Task 5: Rollback

**Question:** The deployment `api` is failing. Roll back to the previous revision.

```bash
# Solution
kubectl rollout undo deployment api

# Check status
kubectl rollout status deployment api

# View history
kubectl rollout history deployment api
```

### Task 6: CronJob

**Question:** Create a CronJob `backup` that runs every hour and executes `backup.sh`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup
spec:
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: busybox:1.36
            command: ["sh", "-c", "/scripts/backup.sh"]
          restartPolicy: Never
      backoffLimit: 3
EOF
```

---

## Mock Exam 3: Application Troubleshooting (20%)

### Task 7: Debug CrashLoopBackOff

**Question:** Pod `debug-me` is in CrashLoopBackOff. Find and fix the issue.

```bash
# Solution
# Check pod status
kubectl describe pod debug-me

# Check logs
kubectl logs debug-me --previous

# Common fixes:
# 1. Image not found - fix image name
# 2. Command failing - check command args
# 3. Missing config - check ConfigMap/Secret mounts
```

### Task 8: Debug Service Connectivity

**Question:** Pods can't reach service `api-service`. Debug and fix.

```bash
# Solution
# Check service exists
kubectl get svc api-service

# Check endpoints
kubectl get endpoints api-service

# Check pod labels match service selector
kubectl get pods --show-labels
kubectl describe svc api-service

# Test from inside a pod
kubectl run debug --rm -it --image=busybox -- sh
wget -qO- http://api-service:80
```

### Task 9: Debug Pending Pod

**Question:** Pod `pending-pod` is stuck in Pending state.

```bash
# Solution
# Check events
kubectl describe pod pending-pod

# Common causes:
# 1. No node with matching labels
kubectl get nodes --show-labels

# 2. Resource quota exceeded
kubectl get resourcequota -n <namespace>

# 3. PVC not bound
kubectl get pvc
```

---

## Mock Exam 4: Application Extension & Maintenance (20%)

### Task 10: ConfigMap

**Question:** Create a ConfigMap `app-config` with keys `DB_HOST=mysql` and `DB_PORT=3306`. Mount it in a pod.

```bash
# Solution
kubectl create configmap app-config \
  --from-literal=DB_HOST=mysql \
  --from-literal=DB_PORT=3306

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "env"]
    envFrom:
    - configMapRef:
        name: app-config
EOF
```

### Task 11: Secret

**Question:** Create a Secret `db-secret` with `username=admin` and `password=supersecret`. Mount as volume.

```bash
# Solution
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=supersecret

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secret
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "ls /secret && cat /secret/*"]
    volumeMounts:
    - name: secret-volume
      mountPath: /secret
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
EOF
```

### Task 12: Resource Quota

**Question:** Create a ResourceQuota `compute-quota` in namespace `dev` that limits CPU to 4 cores and memory to 8Gi.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
EOF
```

---

## Mock Exam 5: Security (20%)

### Task 13: ServiceAccount

**Question:** Create a service account `app-sa` with a token that expires after 1 hour.

```bash
# Solution
kubectl create serviceaccount app-sa

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: app-sa-token
  annotations:
    kubernetes.io/service-account.name: app-sa
type: kubernetes.io/service-account-token
data: {}
EOF
```

### Task 14: Network Policy

**Question:** Create a network policy that denies all ingress traffic to pods with label `app=secure` except from pods with label `app=trusted`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-untrusted
spec:
  podSelector:
    matchLabels:
      app: secure
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: trusted
EOF
```

### Task 15: Pod Security Standards

**Question:** Enforce restricted Pod Security Standards on namespace `production`.

```bash
# Solution
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

---

## Time Management

| Strategy | Description |
|----------|-------------|
| Read first | Scan all questions, mark easy ones |
| Quick wins | Do easy questions first (5 min each) |
| Medium | Spend 10-15 min on medium questions |
| Hard | Skip and come back if time permits |
| Review | Reserve 5 min for verification |

## Key Commands

```bash
# Quick YAML generation
kubectl run nginx --image=nginx --dry-run=client -o yaml

# Debug pod issues
kubectl describe pod <name>
kubectl logs <name> --previous
kubectl exec -it <name> -- sh

# Check service endpoints
kubectl get endpoints <service-name>

# Verify network policy
kubectl describe networkpolicy <name>
```

## Related

- [CKAD Certification](ckad.md)
- [CKA Mock Exam](cka-mock-exam.md)
- [CKS Mock Exam](cks-mock-exam.md)
- [Debugging Commands](debugging-commands.md)
