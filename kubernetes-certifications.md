# Kubernetes Certifications Guide

> **Category:** Certification / Interview Prep

## Overview

The Cloud Native Computing Foundation (CNCF) offers three Kubernetes certifications that validate your skills in different roles:

| Certification | Level | Focus | Prerequisites |
|--------------|-------|-------|---------------|
| **CKA** | Associate | Cluster Administrator | None |
| **CKAD** | Associate | Application Developer | None (CKA recommended) |
| **CKS** | Specialty | Security Specialist | CKA (must be current) |

---

## CKA — Certified Kubernetes Administrator

### Exam Details
- **Duration**: 3 hours
- **Format**: Hands-on, performance-based labs
- **Cost**: $395
- **Curve**: ~66% passing score required
- **Attempts**: 1 free retake within 1 year
- **Environment**: Killer.sh proctored online environment

### Curriculum (as of v1.31)

| Domain | Weight | Topics |
|--------|--------|--------|
| **Cluster Architecture, Installation & Configuration** | 25% | - Plan deployment<br>- kubeadm install/configure HA control plane<br>- High availability (kubeadm HA)<br>- Version skew policy<br>- Container runtime |
| **Workloads** | 15% | - Deployments, StatefulSets, DaemonSets<br>- Pod management<br>- ConfigMaps & Secrets<br>- Multi-container pods |
| **Services & Networking** | 20% | - Service networking<br>- Ingress controllers<br>- Network policies<br>- CoreDNS configuration |
| **Storage** | 10% | - Storage classes<br>- PV/PVC provisioning<br>- Read/Write modes<br>- Storage drivers |
| **Troubleshooting** | 30% | - kubelet issues<br>- application failures<br>- control plane issues<br>- networking issues |

### Key Skills Tested

```bash
# Cluster setup & maintenance (25%)
kubeadm init
kubeadm join
kubectl config view/set-credentials/set-cluster
kubectl apply -f /etc/kubernetes/manifests/

# Workload management (15%)
kubectl create deploy web --image=nginx
kubectl expose deploy web --port=80
kubectl rollout status deploy/web

# Networking (20%)
kubectl apply -f ingress.yaml
kubectl apply -f network-policy.yaml

# Storage (10%)
kubectl apply -f pv-pvc.yaml
kubectl get sc

# Troubleshooting (30%)
kubectl describe pod <pod>
kubectl logs <pod> --previous
kubectl exec -it <pod> -- /bin/sh
```

---

## CKAD — Certified Kubernetes Application Developer

### Exam Details
- **Duration**: 3 hours
- **Format**: Hands-on labs
- **Cost**: $395
- **Environment**: Linux with kubectl

### Curriculum (as of v1.31)

| Domain | Weight | Topics |
|--------|--------|--------|
| **Application Design & Build** | 20% | - Multi-container pods<br>- Pod affinity/anti-affinity<br>- Sidecar, adapter patterns |
| **Configuration** | 25% | - ConfigMaps, Secrets<br>- Downward API<br>- Service account |
| **State** | 15% | - PV/PVC<br>- StatefulSet<br>- Pod lifecycle (init) |
| **Communication & Production** | 25% | - Service & ingress<br>- Network policy (import/export)<br>- Gateway API |
| **Security** | 15% | - PSP, Network Policies<br>- Security context<br>- Image scanning |

---

## CKS — Certified Kubernetes Security Specialist

### Exam Details
- **Duration**: 2 hours
- **Prerequisites**: Valid CKA certification
- **Cost**: $395

### Curriculum (as of v1.31)

| Domain | Weight | Topics |
|--------|--------|--------|
| **Cluster Security** | 16% | - RBAC<br>- PSP migration<br>- Network policies<br>- Secrets encryption |
| **Supply Chain** | 16% | - Image scanning<br>- Sigstore<br>- Admission controllers<br>- Image signatures |
| **Infrastructure & Control** | 12% | - kube-bench<br>- CIS benchmark<br>- kubescape<br>- kube-hunter |
| **Identity & Authorization** | 12% | - OIDC<br>- JWT tokens<br>- Webhook auth |
| **Application & Data Security** | 20% | - Policy-as-code<br>- Kyverno<br>- OPA/Gatekeeper<br>- SealedSecrets |
| **Security Monitoring & Audit** | 12% | - Audit logging<br>- Runtime security<br>- Falco<br>- kube-audit |
| **Incident Response** | 24% | - Forensics<br>- Log analysis<br>- Security incident handling |

```bash
# Security commands tested
kubectl auth can-i list pods --namespace=prod
kubectl api-resources --namespaced=true
kubectl get secrets -o jsonpath='{.data.token}'

# Policy enforcement
kubectl apply -f kyverno-policy.yaml
kubectl get clusterpolicy -o wide

# Network policies
kubectl apply -f network-policy-default-deny.yaml
kubectl get networkpolicy
```

---

## Study Plan (12 Weeks)

### Weeks 1-2: Foundation
- Read [Core Concepts](01-core-concepts/)
- Practice `kubectl` commands in a playground
- Understand Pods, Deployments, Services

### Weeks 3-4: Architecture & Workloads
- Study [Architecture](02-architecture/)
- Master workload resources (ReplicaSets, StatefulSets, DaemonSets)
- Practice YAML manifests

### Weeks 5-6: Networking & Storage
- Learn Services, Ingress, NetworkPolicies
- Master PV/PVC/StorageClass
- Practice port forwarding and service discovery

### Weeks 7-8: Security & Configuration
- Study [Security](06-security/) — RBAC, ServiceAccounts
- Practice ConfigMaps, Secrets, PSP/PSA
- Learn admission controllers

### Weeks 9-10: Troubleshooting
- Practice [Troubleshooting](14-troubleshooting/) scenarios
- Learn debugging techniques
- Use `kubectl describe`, `kubectl logs`

### Weeks 11-12: Practice Exams
- Use [killer.sh](https://killer.sh) for CKA/CKS practice
- Take full-length mock exams
- Review weak areas

### Resources

| Resource | CKA | CKAD | CKS |
|----------|-----|------|-----|
| [killer.sh](https://killer.sh) | ✅ | ✅ | ✅ |
| [KodeKloud](https://kodekloud.com) | ✅ | ✅ | ✅ |
| [Linux Academy / A Cloud Guru](https://acloudguru.com) | ✅ | ✅ | ✅ |
| [CNCFS Accredited](https://training.linuxfoundation.org) | ✅ | ✅ | ✅ |

---

## Exam Day Tips

1. **Print the docs cheat sheet** — `kubectl explain`, `kubectl api-resources`, `kubectl api-versions` work during exam
2. **Bookmark the Kubernetes documentation** — the exam allows one tab open to kubernetes.io/docs
3. **Use `--save-config`** on all `kubectl apply` so you can easily update
4. **Use context shortcuts** — `kubectl config use-context`
5. **Use `-o yaml`** and `-o json` to debug resources
6. **Time management** — flag hard questions, come back
7. **Copy/paste YAML** — you can save your own YAML files and re-apply them

```bash
# Useful aliases for the exam (add to ~/.bashrc)
alias k='kubectl'
alias kk='kubectl -n'
export DOCKER_API_VERSION=1.39
```

## Related Resources

- [Exam Curriculum](https://github.com/cncf/curriculum)
- [killer.sh](https://killer.sh) — Official practice environment
- [Study Plan](16-interview-prep/study-plan.md)
- [Practice Tests](16-interview-prep/cka-practice.md)
