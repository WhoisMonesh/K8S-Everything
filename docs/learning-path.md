# Kubernetes Learning Path — Zero to Expert

> **Category:** Learning / Roadmap
> A structured, sequential learning path through this repository. Follow the phases in order — each builds on the previous.

## How to Use This Path

1. **Start with Phase 1** — don't skip foundations
2. **Read the doc**, then **run the examples** (every concept has YAML in `examples/`)
3. **Do the labs** at the end of each phase
4. **Track progress** — check off items as you go
5. **Time estimates** — each phase is ~2 weeks at 1-2 hours/day

---

## Phase 1: Foundations (Week 1-2)

> **Goal:** Understand what K8s is, deploy your first app, expose it to the internet.

### Week 1: Core Concepts

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 1 | What is Kubernetes? | [01-core-concepts/kubernetes.md](../01-core-concepts/kubernetes.md) | 30 min |
| 2 | Architecture (control plane + workers) | [02-architecture/architecture.md](../02-architecture/architecture.md) | 45 min |
| 3 | Pods | [01-core-concepts/pods.md](../01-core-concepts/pods.md) | 30 min |
| 4 | Pod Lifecycle | [01-core-concepts/pod-lifecycle.md](../01-core-concepts/pod-lifecycle.md) | 30 min |
| 5 | ReplicaSets | [01-core-concepts/replicasets.md](../01-core-concepts/replicasets.md) | 20 min |
| 6 | Deployments | [01-core-concepts/deployments.md](../01-core-concepts/deployments.md) | 45 min |
| 7 | **Lab:** Deploy nginx, scale it, rollout undo | [Lab 1](#lab-1) | 45 min |

### Week 2: Networking + Config

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 8 | Services (ClusterIP, NodePort, LoadBalancer) | [04-networking/services.md](../04-networking/services.md) | 45 min |
| 9 | Ingress + Ingress Controllers | [04-networking/ingress.md](../04-networking/ingress.md) | 45 min |
| 10 | CoreDNS | [04-networking/coredns.md](../04-networking/coredns.md) | 30 min |
| 11 | ConfigMaps | [01-core-concepts/configmaps.md](../01-core-concepts/configmaps.md) | 30 min |
| 12 | Secrets | [01-core-concepts/secrets.md](../01-core-concepts/secrets.md) | 30 min |
| 13 | Volumes + PVCs | [01-core-concepts/volumes.md](../01-core-concepts/volumes.md) | 45 min |
| 14 | **Lab:** Expose nginx with Service + Ingress | [Lab 2](#lab-2) | 45 min |

### Phase 1 Checkpoint

```bash
# Can you do all of these?
kubectl create deployment nginx --image=nginx:1.25 --replicas=3
kubectl expose deployment nginx --port=80 --type=ClusterIP
kubectl get svc,ep nginx
kubectl get ingress
curl http://<external-ip>
```

---

## Phase 2: Production Ready (Week 3-4)

> **Goal:** Secure, scale, and operate apps in production.

### Week 3: Security

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 15 | Namespaces | [01-core-concepts/namespaces.md](../01-core-concepts/namespaces.md) | 20 min |
| 16 | Labels & Selectors | [01-core-concepts/labels-selectors.md](../01-core-concepts/labels-selectors.md) | 30 min |
| 17 | RBAC | [06-security/rbac.md](../06-security/rbac.md) | 45 min |
| 18 | Service Accounts | [06-security/service-accounts.md](../06-security/service-accounts.md) | 30 min |
| 19 | Pod Security Standards | [06-security/pod-security-context.md](../06-security/pod-security-context.md) | 45 min |
| 20 | Network Policies | [04-networking/network-policies.md](../04-networking/network-policies.md) | 45 min |
| 21 | **Lab:** Lock down nginx with RBAC + NetPol | [Lab 3](#lab-3) | 45 min |

### Week 4: Scaling + Operations

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 22 | Resource Quotas + LimitRanges | [01-core-concepts/resource-quotas.md](../01-core-concepts/resource-quotas.md) | 30 min |
| 23 | HPA | [03-workloads/hpa.md](../03-workloads/hpa.md) | 45 min |
| 24 | VPA | [03-workloads/vpa.md](../03-workloads/vpa.md) | 30 min |
| 25 | PDB | [03-workloads/pdb.md](../03-workloads/pdb.md) | 30 min |
| 26 | Deployment Strategies | [03-workloads/deployment-strategies.md](../03-workloads/deployment-strategies.md) | 45 min |
| 27 | Health Probes | [03-workloads/pods.md](../03-workloads/pods.md#health-checks) | 30 min |
| 28 | **Lab:** Add HPA + PDB + resource limits | [Lab 4](#lab-4) | 45 min |

### Phase 2 Checkpoint

```bash
kubectl get clusterrolebinding,rolebinding -A
kubectl get networkpolicy -A
kubectl get hpa,pdb -A
kubectl describe pod <pod> | grep -A5 "Limits"
```

---

## Phase 3: Operations (Week 5-6)

> **Goal:** Monitor, troubleshoot, and recover from incidents.

### Week 5: Cluster Operations

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 29 | kubeadm (bootstrap) | [08-cluster-operations/kubeadm.md](../08-cluster-operations/kubeadm.md) | 45 min |
| 30 | etcd | [02-architecture/etcd.md](../02-architecture/etcd.md) | 45 min |
| 31 | Upgrades | [08-cluster-operations/upgrades.md](../08-cluster-operations/upgrades.md) | 45 min |
| 32 | Backup & DR | [08-cluster-operations/backup-disaster-recovery.md](../08-cluster-operations/backup-disaster-recovery.md) | 45 min |
| 33 | FinOps | [08-cluster-operations/finops.md](../08-cluster-operations/finops.md) | 30 min |

### Week 6: Observability + Troubleshooting

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 34 | Prometheus | [13-observability/prometheus.md](../13-observability/prometheus.md) | 45 min |
| 35 | Grafana | [13-observability/grafana.md](../13-observability/grafana.md) | 30 min |
| 36 | Logging (Loki) | [13-observability/logging.md](../13-observability/logging.md) | 30 min |
| 37 | Troubleshooting Encyclopedia | [14-troubleshooting/troubleshooting-encyclopedia.md](../14-troubleshooting/troubleshooting-encyclopedia.md) | 60 min |
| 38 | Disaster Cases | [14-troubleshooting/disaster-cases.md](../14-troubleshooting/disaster-cases.md) | 45 min |
| 39 | Incident Case Studies (39 real outages) | [14-troubleshooting/incidents/README.md](../14-troubleshooting/incidents/README.md) | 60 min |
| 40 | **Lab:** Troubleshoot broken deployments | [Lab 5](#lab-5) | 60 min |

### Phase 3 Checkpoint

```bash
kubectl top nodes
kubectl top pods -A --sort-by=memory
kubectl get events --sort-by=.metadata.creationTimestamp -A | tail -20
curl http://<prometheus>:9090/api/v1/query?query=up
```

---

## Phase 4: Advanced (Week 7-8)

> **Goal:** Service mesh, GitOps, supply chain, and certification prep.

### Week 7: Service Mesh + GitOps

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 41 | Service Mesh Overview | [12-service-mesh/service-mesh.md](../12-service-mesh/service-mesh.md) | 30 min |
| 42 | Istio (install, mTLS, VirtualService) | [12-service-mesh/istio.md](../12-service-mesh/istio.md) | 60 min |
| 43 | ArgoCD | [11-ci-cd-gitops/argo-cd.md](../11-ci-cd-gitops/argo-cd.md) | 45 min |
| 44 | Flux | [11-ci-cd-gitops/flux.md](../11-ci-cd-gitops/flux.md) | 45 min |
| 45 | **Tutorial:** Deploy nginx + Istio mesh | [Tutorial 2](../examples/tutorials/tutorial-nginx-istio.md) | 90 min |

### Week 8: Supply Chain + Certification

| # | Topic | Doc | Time |
|---|-------|-----|------|
| 46 | Cosign (image signing) | [11-supply-chain/cosign.md](../11-supply-chain/cosign.md) | 45 min |
| 47 | SBOM | [11-supply-chain/sbom.md](../11-supply-chain/sbom.md) | 30 min |
| 48 | Image Scanning (Trivy) | [11-supply-chain/image-scanning.md](../11-supply-chain/image-scanning.md) | 30 min |
| 49 | CRDs | [15-advanced-patterns/crds.md](../15-advanced-patterns/crds.md) | 45 min |
| 50 | Operators | [15-advanced-patterns/operators.md](../15-advanced-patterns/operators.md) | 45 min |
| 51 | Chaos Engineering | [15-advanced-patterns/chaos-engineering.md](../15-advanced-patterns/chaos-engineering.md) | 30 min |
| 52 | **Exam Prep:** CKA/CKAD/CKS walkthrough | [16-interview-prep/exam-walkthrough.md](../16-interview-prep/exam-walkthrough.md) | 60 min |

### Phase 4 Checkpoint

```bash
istioctl proxy-status
argocd app list
cosign verify --key cosign.pub <image>
kubectl get crd | grep -c "stable.example.com"
```

---

## Lab Instructions

### Lab 1: Deploy and Scale Nginx

```bash
# Deploy
kubectl create deployment nginx --image=nginx:1.25 --replicas=3
kubectl get pods -o wide

# Scale
kubectl scale deployment nginx --replicas=5
kubectl get pods -w  # watch new pods appear

# Rollout
kubectl set image deployment/nginx nginx=nginx:1.26
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx

# Cleanup
kubectl delete deployment nginx
```

### Lab 2: Expose with Service + Ingress

```bash
# Deploy
kubectl create deployment nginx --image=nginx:1.25 --replicas=3

# ClusterIP Service
kubectl expose deployment nginx --port=80 --type=ClusterIP
kubectl get svc,ep nginx

# Test from inside cluster
kubectl run curl --rm -it --image=curlimages/curl -- sh
curl http://nginx.default.svc.cluster.local

# Ingress (requires ingress controller installed)
cat <<EOF | k apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: nginx.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port: { number: 80 }
kubectl get ingress nginx
```

### Lab 3: Security Lockdown

```bash
# Create namespace
kubectl create ns secure-app

# Network Policy (deny all, allow DNS + nginx)
cat <<EOF | k apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: secure-app
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: secure-app
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to: []
    ports:
    - protocol: UDP
      port: 53
kubectl get netpol -n secure-app

# RBAC
kubectl create sa app-sa -n secure-app
kubectl create role app-reader --verb=get,list,watch --resource=pods -n secure-app
kubectl create rolebinding app-reader --role=app-reader --serviceaccount=secure-app:app-sa -n secure-app
kubectl auth can-i list pods -n secure-app --as=system:serviceaccount:secure-app:app-sa
kubectl auth can-i delete pods -n secure-app --as=system:serviceaccount:secure-app:app-sa
```

### Lab 4: HPA + PDB + Resources

```bash
# Deploy with resource requests
cat <<EOF | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  selector:
    matchLabels: { app: nginx }
  template:
    metadata:
      labels: { app: nginx }
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        resources:
          requests: { cpu: 100m, memory: 128Mi }
          limits: { cpu: 500m, memory: 256Mi }

# HPA
kubectl autoscale deployment nginx --cpu-percent=70 --min=3 --max=10
kubectl get hpa -w

# PDB
cat <<EOF | k apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nginx-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels: { app: nginx }
kubectl get pdb
```

### Lab 5: Troubleshooting

```bash
# Create broken deployments
kubectl create ns broken

# Task 1: Fix CrashLoopBackOff
cat <<EOF | k apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken
  namespace: broken
spec:
  replicas: 2
  selector:
    matchLabels: { app: broken }
  template:
    metadata:
      labels: { app: broken }
    spec:
      containers:
      - name: app
        image: nginx:1.25
        command: ["sh","-c","exit 1"]
# Fix: change command to ["sh","-c","nginx -g 'daemon off;'"]

# Task 2: Fix Pending pod
cat <<EOF | k apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: huge
  namespace: broken
spec:
  containers:
  - name: app
    image: nginx:1.25
    resources:
      requests: { cpu: "999", memory: "999Gi" }
# Fix: reduce requests

# Task 3: Fix Service endpoints
cat <<EOF | k apply -f -
apiVersion: v1
kind: Service
metadata:
  name: orphan
  namespace: broken
spec:
  selector: { app: wrong }
  ports:
  - port: 80
# Fix: change selector to { app: broken }

# Verify
kubectl get pods -n broken
kubectl get endpoints orphan -n broken
```

---

## Related

- [Glossary](../cheat-sheets/glossary.md) — all K8s terms
- [Troubleshooting Cheat Sheet](../cheat-sheets/troubleshooting.md) — 90-second commands
- [Incident Case Studies](../14-troubleshooting/incidents/README.md) — 39 real outages