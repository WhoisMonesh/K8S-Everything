# Lab: Build a Secure, Observable App (end-to-end)

> Walk through the full lifecycle: deploy a Pod, expose it, add autoscaling, lock it down with a NetworkPolicy, attach a secret, and mount storage. Mirrors the [CKA/CKAD/CKS walkthrough](../../16-interview-prep/exam-walkthrough.md).

## Setup
```bash
export k=kubectl
# 1. Create a fresh namespace
k create ns lab
k config set-context --current --namespace=lab
```

## Step 1 — Run the app
```bash
# Use a real image that listens on 80
k create deployment web --image=nginx:1.25 --port=80
k scale deploy web --replicas=3
k get pods -o wide
```

## Step 2 — Expose it inside the cluster, then outside
```bash
k expose deploy web --port=80 --target-port=80 --name web-svc
k get svc,ep web-svc                 # confirm endpoints are non-empty
# Outside (local kind/minikube clusters):
k expose deploy web --type=NodePort --port=80 --name web-node --dry-run=client -o yaml | k apply -f -
```

## Step 3 — Add TLS + Ingress
```bash
k create secret tls web-tls --cert=tls.crt --key=tls.key   # self-signed for the lab
# apply examples/common-patterns/ingress.yaml (update host + secret name)
k apply -f ../networking/../../examples/common-patterns/ingress.yaml
```

## Step 4 — Autoscale it
```bash
k apply -f examples/scheduling/hpa.yaml           # CPU>60% scales out
# watch:
k get hpa -w
```

## Step 5 — Lock down (NetworkPolicy)
```bash
# default deny all, then allow:
k apply -f examples/security/network-policy-egress.yaml
k get netpol
```

## Step 6 — Attach config + secret
```bash
k apply -f examples/common-patterns/configmap-secret.yaml
k exec -it deploy/web -- env | grep -E 'LOG_LEVEL|USERNAME'
```

## Step 7 — Attach storage
```bash
k apply -f examples/storage/pvc-deployment.yaml
k get pvc
```

## Step 8 — Inspect & debug
```bash
k describe pod <pod>              # read Events
k logs -f deploy/web              # or k logs -p <pod>
k get events -n lab --sort-by=.lastTimestamp
k top pods                         # needs metrics-server
k port-forward svc/web-svc 8080:80
curl -s localhost:8080 | head
```

## Lab 2 — Troubleshooting (CKA-style)

```bash
# Create a broken deployment
k create ns broken
k config set-context --current --namespace=broken

# Task 1: Fix CrashLoopBackOff
cat <<EOF | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: broken
  template:
    metadata:
      labels:
        app: broken
    spec:
      containers:
      - name: app
        image: nginx:1.25
        command: ["sh","-c","echo hello && exit 1"]  # crashes immediately
# Your task: fix the command so pods stay Running (hint: use "nginx -g 'daemon off;'")
```

```bash
# Task 2: Fix Pending pod (resource constraints)
cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: huge-pod
spec:
  containers:
  - name: app
    image: nginx:1.25
    resources:
      requests:
        cpu: "999"
        memory: "999Gi"
# Your task: reduce requests to something the cluster can satisfy, or delete and recreate
```

```bash
# Task 3: Fix Service endpoint mismatch
cat <<EOF | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: mismatch-svc
spec:
  selector:
    app: wrong-label     # no pods have this label
  ports:
  - port: 80
# Your task: fix the selector to match the broken-app pods (label: app=broken)
```

## Lab 3 — RBAC (CKA-style)

```bash
k create ns rbac-lab

# Create a ServiceAccount
k create sa dev-sa -n rbac-lab

# Task 1: Give dev-sa read-only access to pods in rbac-lab
cat <<EOF | k apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: rbac-lab
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: rbac-lab
subjects:
- kind: ServiceAccount
  name: dev-sa
  namespace: rbac-lab
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

# Task 2: Verify — should succeed
k auth can-i list pods -n rbac-lab --as=system:serviceaccount:rbac-lab:dev-sa

# Task 3: Verify — should fail
k auth can-i delete pods -n rbac-lab --as=system:serviceaccount:rbac-lab:dev-sa
```

## Lab 4 — Helm (package management)

```bash
# Task 1: Add bitnami repo and install nginx
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install my-nginx bitnami/nginx -n helm-lab --create-namespace

# Task 2: Check what was deployed
helm list -n helm-lab
helm get manifest my-nginx -n helm-lab

# Task 3: Upgrade with custom values
helm upgrade my-nginx bitnami/nginx -n helm-lab \
  --set service.type=ClusterIP \
  --set replicaCount=3

# Task 4: Rollback
helm rollback my-nginx 1 -n helm-lab

# Task 5: Uninstall
helm uninstall my-nginx -n helm-lab
```

## Lab 5 — GitOps (ArgoCD)

```bash
# Task 1: Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Task 2: Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Task 3: Create an Application (point to a Git repo)
cat <<EOF | k apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/WhoisMonesh/K8S-Everything.git
    targetRevision: main
    path: examples/common-patterns
  destination:
    server: https://kubernetes.default.svc
    namespace: gitops-lab
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

# Task 4: Watch sync status
kubectl get applications -n argocd -w
```

## Teardown

```bash
k delete ns lab broken rbac-lab helm-lab gitops-lab 2>/dev/null
helm uninstall my-nginx -n helm-lab 2>/dev/null
kubectl delete namespace argocd 2>/dev/null
```

## Expected outcomes

### Lab 1
- `web-svc` resolves inside the cluster (`nslookup web-svc`).
- `k get endpoints web-svc` shows **3** addresses (one per pod).
- Scaling traffic up drives the HPA from 3 → more pods.
- NetPol blocks egress to `redis` and the internet, but allows DNS + same-namespace.

### Lab 2
- All CrashLoopBackOff pods transition to Running.
- `huge-pod` transitions from Pending to Running.
- `mismatch-svc` endpoints are populated (non-empty).

### Lab 3
- `can-i list pods` returns `yes`.
- `can-i delete pods` returns `no`.

### Lab 4
- Helm release `my-nginx` exists in `helm-lab`.
- Upgrade changes replicaCount to 3.
- Rollback restores original state.

### Lab 5
- ArgoCD shows `nginx-app` as `Synced` and `Healthy`.
- Pods running in `gitops-lab`.

## Related

- [Troubleshooting Encyclopedia](../../14-troubleshooting/troubleshooting-encyclopedia.md) · [Exam walkthrough](../../16-interview-prep/exam-walkthrough.md) · [FinOps](../../08-cluster-operations/finops.md)
- [Incident Case Studies](../../14-troubleshooting/incidents/README.md) · [Glossary](../../cheat-sheets/glossary.md)
EOFMARKER