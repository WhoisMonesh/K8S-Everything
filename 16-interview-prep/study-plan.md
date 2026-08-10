# Certification Study Plan

> **Category:** Interview Preparation / Certification

A time-boxed plan for CKA -> CKAD -> CKS (9 weeks), mapped to the docs in this repo.

## Prerequisites

| Before you start | You should be able to |
|------------------|-----------------------|
| Run a local cluster | `minikube start` or `kind create cluster` |
| Write YAML confidently | Use `kubectl explain` + `--dry-run=client -o yaml` |
| Comfortable with kubectl | See [kubectl cheatsheet](../cheat-sheets/kubectl.md) |

## Weeks 1-3: CKA (Cluster Administrator)
**Goal:** install, operate, troubleshoot a cluster end-to-end.

| Week | Focus | Docs |
|------|-------|------|
| 1 | Control plane + install | [architecture](../02-architecture/architecture.md), [upgrades](../08-cluster-operations/upgrades.md), kubelet, [etcd](../02-architecture/etcd.md) |
| 2 | Workloads + storage | [deployments](../03-workloads/deployments.md), [statefulsets](../03-workloads/statefulsets.md), [storage](../05-storage/storage.md) |
| 3 | Networking + troubleshooting | [services](../04-networking/services.md), [cni](../04-networking/cni-kube-proxy.md), [troubleshooting](../14-troubleshooting/) |

> **Hands-on:** every day, run `kubectl get/describe/logs/exec` on 3 Pods you didn't write. Use [troubleshooting-patterns.md](../14-troubleshooting/troubleshooting-patterns.md) as the checklist.

## Weeks 4-6: CKAD (Application Developer)
**Goal:** design, configure, and expose apps.

| Week | Focus | Docs |
|------|-------|------|
| 4 | App design + config | [deployments](../03-workloads/deployments.md), [configmaps](../01-core-concepts/configmaps.md), [secrets](../01-core-concepts/secrets.md) |
| 5 | Services + probes | [services](../04-networking/services.md), [deployments - probes](../03-workloads/deployments.md) |
| 6 | Observability + rollouts | [prometheus](../13-observability/prometheus.md), `kubectl rollout`, [debug](../14-troubleshooting/troubleshooting-patterns.md) |

## Weeks 7-9: CKS (Security Specialist) - CKA required first
**Goal:** harden a cluster + secure the supply chain.

| Week | Focus | Docs |
|------|-------|------|
| 7 | Cluster hardening | [security README](../06-security/README.md), [RBAC](../06-security/rbac.md), [PSA](../06-security/pod-security-admission.md), [upgrades](../08-cluster-operations/upgrades.md) |
| 8 | Network + image security | [network-policies](../04-networking/network-policies.md), [PKI/certificates](../06-security/certificates.md) |
| 9 | Runtime + supply chain | audit logs, Falco, cosign, SBOM |

## Daily rhythm
1. **45 min** hands-on cluster time (no docs open first).
2. **Review** the failed bits against these docs.
3. **Re-run** the same task from scratch.

## Practice resources
- **killer.sh** / `killer.sh/cks` - official mock exams (use the `--time` flag).
- [Practice tests](cka-practice.md)
- [Exam day checklist](exam-checklist.md)
