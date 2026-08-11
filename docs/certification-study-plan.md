# Certification Study Plan — CKA / CKAD / CKS

> **Category:** Interview Prep / Certification
> Structured study plan for Kubernetes certifications. 4-6 weeks, 1-2 hours/day.

## Certification Overview

| Certification | Focus | Duration | Questions | Pass Score |
|--------------|-------|----------|-----------|------------|
| **CKA** | Administration | 2 hours | 15-20 | 67% |
| **CKAD** | Application Development | 2 hours | 15-20 | 67% |
| **CKS** | Security | 2 hours | 15-20 | 67% |

## Study Resources

| Resource | Link |
|----------|------|
| Kubernetes Docs | https://kubernetes.io/docs/ |
| Killer.sh (practice) | https://killer.sh/ |
| CKA Curriculum | https://github.com/cncf/curriculum |
| CKAD Exercises | https://github.com/dgkanatsios/CKAD-exercises |
| CKS Curriculum | https://github.com/cncf/curriculum/blob/master/CKS-Curriculum.pdf |

---

## CKA Study Plan (4 weeks)

### Week 1: Cluster Architecture (25%)

| Topic | Weight | Study |
|-------|--------|-------|
| Cluster Architecture | 25% | [02-architecture/](../02-architecture/README.md) |
| etcd backup/restore | — | [backup-restore.md](../08-cluster-operations/backup-restore.md) |
| kubeadm cluster setup | — | [kubeadm.md](../08-cluster-operations/kubeadm.md) |
| TLS certificate management | — | [certificates.md](../06-security/certificates.md) |
| Kubernetes API primitives | — | [api-groups-reference.md](../api-groups-reference.md) |

### Week 2: Workloads & Scheduling (30%)

| Topic | Weight | Study |
|-------|--------|-------|
| Workloads & Scheduling | 30% | [03-workloads/](../03-workloads/README.md) |
| Deployment rolling updates | — | [deployments.md](../03-workloads/deployments.md) |
| HPA/VPA | — | [hpa.md](../03-workloads/hpa.md) |
| Resource quotas/limits | — | [resource-quotas.md](../01-core-concepts/resource-quotas.md) |
| DaemonSets, StatefulSets | — | [daemonsets.md](../03-workloads/daemonsets.md) |
| Jobs, CronJobs | — | [jobs.md](../03-workloads/jobs.md) |

### Week 3: Services & Networking (20%)

| Topic | Weight | Study |
|-------|--------|-------|
| Services & Networking | 20% | [04-networking/](../04-networking/README.md) |
| CoreDNS | — | [coredns.md](../04-networking/coredns.md) |
| Ingress controllers | — | [ingress.md](../04-networking/ingress.md) |
| Network Policies | — | [network-policies.md](../04-networking/network-policies.md) |
| Service types | — | [services.md](../04-networking/services.md) |

### Week 4: Storage & Troubleshooting (25%)

| Topic | Weight | Study |
|-------|--------|-------|
| Storage | 10% | [05-storage/](../05-storage/README.md) |
| Troubleshooting | 15% | [troubleshooting-encyclopedia.md](../14-troubleshooting/troubleshooting-encyclopedia.md) |
| Debugging pods | — | [troubleshooting-patterns.md](../14-troubleshooting/troubleshooting-patterns.md) |
| kubectl debug | — | [kubectl-debug.md](../14-troubleshooting/kubectl-debug.md) |

### CKA Exam Commands

```bash
# Cluster setup
kubeadm init --pod-network-cidr=10.244.0.0/16
kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>

# etcd backup/restore
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db

# Debugging
kubectl describe pod <pod>
kubectl logs <pod> --previous
kubectl exec -it <pod> -- /bin/sh
kubectl get events --sort-by=.metadata.creationTimestamp

# RBAC
kubectl auth can-i list pods --as=system:serviceaccount:default:my-sa

# Network
kubectl get networkpolicy -A
kubectl describe networkpolicy <policy>
```

---

## CKAD Study Plan (4 weeks)

### Week 1: Core Concepts (25%)

| Topic | Weight | Study |
|-------|--------|-------|
| Application Deployment | 25% | [deployments.md](../01-core-concepts/deployments.md) |
| Pod design | — | [pods.md](../01-core-concepts/pods.md) |
| ReplicaSets | — | [replicasets.md](../01-core-concepts/replicasets.md) |
| Namespaces | — | [namespaces.md](../01-core-concepts/namespaces.md) |

### Week 2: Configuration & Security (20%)

| Topic | Weight | Study |
|-------|--------|-------|
| ConfigMaps & Secrets | 20% | [configmaps.md](../01-core-concepts/configmaps.md), [secrets.md](../01-core-concepts/secrets.md) |
| Resource quotas | — | [resource-quotas.md](../01-core-concepts/resource-quotas.md) |
| LimitRanges | — | [limit-ranges.md](../01-core-concepts/limit-ranges.md) |
| Service Accounts | — | [service-accounts.md](../06-security/service-accounts.md) |

### Week 3: Services & Networking (20%)

| Topic | Weight | Study |
|-------|--------|-------|
| Services | 20% | [services.md](../04-networking/services.md) |
| Ingress | — | [ingress.md](../04-networking/ingress.md) |
| Network Policies | — | [network-policies.md](../04-networking/network-policies.md) |

### Week 4: Storage & Observability (20%)

| Topic | Weight | Study |
|-------|--------|-------|
| Volumes & PVCs | 20% | [volumes.md](../01-core-concepts/volumes.md), [persistent-volumes.md](../01-core-concepts/persistent-volumes.md) |
| Debugging | — | [troubleshooting-patterns.md](../14-troubleshooting/troubleshooting-patterns.md) |

### CKAD Exam Commands

```bash
# Pod design
kubectl run <name> --image=<image> --dry-run=client -o yaml > pod.yaml
kubectl expose pod <name> --port=80 --type=ClusterIP

# Config
kubectl create configmap <name> --from-literal=key=value
kubectl create secret generic <name> --from-literal=key=value

# Networking
kubectl run test --rm -it --image=curlimages/curl -- curl http://<service>

# Storage
kubectl get pvc
kubectl describe pvc <name>
```

---

## CKS Study Plan (4 weeks)

### Week 1: Cluster Setup (10%)

| Topic | Weight | Study |
|-------|--------|-------|
| Kubernetes API server security | 10% | [security.md](../06-security/security.md) |
| etcd encryption | — | [etcd.md](../02-architecture/etcd.md) |
| TLS certificates | — | [certificates.md](../06-security/certificates.md) |

### Week 2: Cluster Hardening (25%)

| Topic | Weight | Study |
|-------|--------|-------|
| RBAC | 25% | [rbac.md](../06-security/rbac.md) |
| Pod Security Standards | — | [pod-security-context.md](../06-security/pod-security-context.md) |
| Network Policies | — | [network-policies.md](../04-networking/network-policies.md) |
| Admission Controllers | — | [admission-controllers.md](../06-security/admission-controllers.md) |

### Week 3: System Hardening (25%)

| Topic | Weight | Study |
|-------|--------|-------|
| Container runtime security | 25% | [container-runtimes.md](../02-architecture/container-runtimes.md) |
| Seccomp | — | [pod-security-context.md](../06-security/pod-security-context.md) |
| AppArmor | — | [pod-security-context.md](../06-security/pod-security-context.md) |
| OS-level security | — | [cks-hardening.yaml](../examples/security/cks-hardening.yaml) |

### Week 4: Supply Chain & Monitoring (25%)

| Topic | Weight | Study |
|-------|--------|-------|
| Image scanning | 25% | [image-scanning.md](../11-supply-chain/image-scanning.md) |
| Cosign | — | [cosign.md](../11-supply-chain/cosign.md) |
| SBOM | — | [sbom.md](../11-supply-chain/sbom.md) |
| Audit logging | — | [observability.md](../13-observability/observability.md) |
| Falco | — | [security.md](../06-security/security.md) |

### CKS Exam Commands

```bash
# Pod Security
kubectl label ns <ns> pod-security.kubernetes.io/enforce=restricted

# RBAC
kubectl auth can-i list pods --as=system:serviceaccount:default:my-sa

# Network Policy
kubectl get networkpolicy -A
kubectl describe networkpolicy <policy>

# Image scanning
trivy image --severity HIGH,CRITICAL <image>

# Audit
kubectl logs -n kube-system kube-apiserver-<node> | grep audit
```

---

## Practice Strategy

| Phase | Focus | Duration |
|-------|-------|----------|
| 1 | Read docs + take notes | Week 1-2 |
| 2 | Hands-on labs | Week 3-4 |
| 3 | Killer.sh practice exams | Week 5-6 |
| 4 | Review weak areas | Final week |

## Related

- [Exam Walkthrough](../16-interview-prep/exam-walkthrough.md)
- [CKA Practice Tests](../16-interview-prep/cka-practice.md)
- [Debugging Commands](../16-interview-prep/debugging-commands.md)
- [Learning Path](./learning-path.md)
